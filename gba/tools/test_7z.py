#!/usr/bin/env python3
"""(AI-assisted) Native host regression for GBAXY issue #2 7z support."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import zipfile

root = Path(__file__).resolve().parents[2]
sdk = root / "gba/third_party/mgba/src/third-party/lzma"
c_sources = [
    "7zAlloc", "7zArcIn", "7zBuf", "7zBuf2", "7zCrc", "7zCrcOpt", "7zDec",
    "CpuArch", "Delta", "LzmaDec", "Lzma2Dec", "Bra", "Bra86", "BraIA64",
    "Bcj2", "Ppmd7", "Ppmd7Dec", "7zStream"
]
archiver = shutil.which("7z") or shutil.which("7za")
if not archiver:
    raise SystemExit("7z or 7za is needed for 7z regression fixtures")
cxx = shutil.which("clang++-18") or shutil.which("clang++")
cc = shutil.which("clang-18") or shutil.which("clang")
if not cxx or not cc:
    raise SystemExit("Clang compiler unavailable")
with tempfile.TemporaryDirectory(prefix="gbaxy-7z-") as name:
    out = Path(name)
    input_dir = out / "input"
    input_dir.mkdir()
    rom = bytearray(32768)
    rom[3] = 0xEA
    rom[0xB2] = 0x96
    (input_dir / "one.gba").write_bytes(rom)
    (input_dir / "two.gba").write_bytes(rom)
    (input_dir / "note.txt").write_text("not a ROM")
    (input_dir / "too-big.gba").write_bytes(bytes(33 << 20))
    def pack(output, files, *opts):
        subprocess.run([archiver, "a", "-t7z", str(out/output), *opts,
                        *(str(input_dir/f) for f in files)],
                       check=True, stdout=subprocess.DEVNULL)
    pack("lzma.7z", ["one.gba"], "-m0=lzma")
    pack("lzma2.7z", ["one.gba"], "-m0=lzma2")
    pack("multi.7z", ["one.gba", "two.gba"])
    pack("empty.7z", ["note.txt"])
    pack("large.7z", ["too-big.gba"])
    pack("encrypted.7z", ["one.gba"], "-pGBAXYTEST", "-mhe=on")
    (out/"corrupt.7z").write_bytes(b"invalid 7z archive")
    (out/"truncated.7z").write_bytes((out/"lzma2.7z").read_bytes()[:40])
    test = out/"test.cpp"
    test.write_text(r"""
#include "sevenzip.h"
#include <cassert>
#include <cstdio>
#include <fstream>
#include <iterator>
#include <string>
#include <vector>
int main(int argc,char**argv){
  for(int i=1;i<argc;++i){
    std::ifstream f(argv[i],std::ios::binary);
    std::vector<uint8_t> packed((std::istreambuf_iterator<char>(f)),{});
    std::vector<uint8_t> rom;
    std::string error;
    bool okay=gba::Unsevenzip(packed,rom,error);
    std::string path(argv[i]);
    bool expected=path.find("lzma.7z")!=std::string::npos ||
                  path.find("lzma2.7z")!=std::string::npos;
    if(okay!=expected){
      std::fprintf(stderr,"FAIL %s: %s\n",path.c_str(),error.c_str());
      return 1;
    }
    if(okay && (rom.size()!=32768 || rom[3]!=0xEA || rom[0xB2]!=0x96))return 2;
  }
  std::puts("PASS sevenzip LZMA/LZMA2, reject multi/no-ROM, oversized, encrypted, corrupt/truncated");
}
""")
    objects = []
    for stem in c_sources:
        obj = out / (stem+".o")
        subprocess.run([cc, "-std=gnu11", "-O1", "-D_7ZIP_PPMD_SUPPPORT",
                        "-c", str(sdk/(stem+".c")), "-o", str(obj)], check=True)
        objects.append(str(obj))
    exe = out/"test"
    subprocess.run([cxx, "-std=c++20", "-O1",
                    "-I"+str(root/"gba/src"),
                    "-I"+str(root/"gba/third_party/mgba/src"),
                    str(test), str(root/"gba/src/sevenzip.cpp"),
                    *objects, "-o",str(exe)],check=True)
    subprocess.run([str(exe),*(str(out/n) for n in
                    ["lzma.7z","lzma2.7z","multi.7z","empty.7z",
                     "large.7z","encrypted.7z","corrupt.7z","truncated.7z"])],check=True)
