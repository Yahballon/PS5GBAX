#!/usr/bin/env python3
"""(AI-assisted) Regress issue #1 with the real scanner/cache compiled for the host."""
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[2]
with tempfile.TemporaryDirectory(prefix="ps5gba-rom-test-") as temporary:
    tmp = Path(temporary)
    source = tmp / "issue1.cpp"
    source.write_text(r'''
#include "games.h"
#include "library_cache.h"
#include "fe_nfs.h"
#include <cassert>
#include <filesystem>
#include <fstream>
#include <string>
#include <vector>
namespace fe::nfs {
bool IsUrl(const char* path) { return std::string(path).rfind("nfs://",0)==0; }
bool ServerReachable(const std::string&) { return false; }
void SetListProgress(std::function<void(const std::string&,bool)>) {}
void SetFastListing(bool) {}
bool List(const std::string&,std::vector<Entry>&,std::string&) { return false; }
}
int main(int argc,char** argv) {
  assert(argc==2);
  namespace fs=std::filesystem;
  fs::path root=fs::path(argv[1])/"PS5GBA";
  fs::create_directories(root/"games");
  fs::create_directories(root/"roms"/"nested");
  fs::create_directories(root/"cache");
  std::ofstream(root/"games"/"one.gba") << "test";
  std::ofstream(root/"roms"/"two.GBA") << "test";
  std::ofstream(root/"roms"/"nested"/"three.gBa") << "test";
  std::ofstream(root/"roms"/"wrong.sfc") << "test";
  auto found=gba::Scan({(root/"games").string(),(root/"roms").string()});
  assert(found.size()==3);
  auto cache=(root/"cache"/"library.bin").string();
  assert(gba::WriteLibrary(cache,found));
  std::vector<gba::Game> loaded;
  assert(gba::ReadLibrary(cache,{(root/"games").string(),(root/"roms").string()},loaded));
  assert(loaded.size()==3);
  for(const auto& g:loaded) assert(g.path.find(".sfc")==std::string::npos);
  assert(!gba::ReadLibrary(cache,{(root/"games").string()},loaded));
  assert(!gba::ReadLibrary(cache,{(root/"roms").string()},loaded));
  std::vector<gba::Game> old{{(root/"games"/"bad.sfc").string(),"bad",4}};
  assert(gba::WriteLibrary(cache,old));
  assert(!gba::ReadLibrary(cache,{(root/"games").string()},loaded));
}
''')
    output = tmp / "issue1"
    subprocess.run([
        "g++", "-std=c++20", "-O1", "-ffunction-sections", "-fdata-sections",
        "-I" + str(root / "gba/src"),
        "-I" + str(root / "gba/include"),
        "-I" + str(root / "ps5/frontend"),
        str(source), str(root / "gba/src/games.cpp"),
        str(root / "gba/src/library_cache.cpp"),
        "-Wl,--gc-sections", "-lz", "-pthread", "-o", str(output)
    ], check=True)
    subprocess.run([str(output), str(tmp)], check=True)
print("PASS (AI-assisted): internal games/roms, nested and mixed-case .gba, persistent cache and legacy SNES rejection")
