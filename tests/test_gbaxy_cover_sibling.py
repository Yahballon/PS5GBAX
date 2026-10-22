#!/usr/bin/env python3
"""(AI-assisted) Host-native CoverFinder same-folder regression and retry contract."""
from pathlib import Path
import shutil
import subprocess
import tempfile

repo = Path(__file__).resolve().parents[1]
worker = (repo / "ps5/frontend/fe_covers.cpp").read_text()
assert 'std::strcmp(updated.source,"beside")==0' in worker
assert 'finder=CoverFinder(m_cfg.manual_dir,m_cfg.cache_dir)' in worker
assert 'if(!m_cfg.allow_download || !m_download)' in worker
assert 'const std::string ext = LowerAscii(file.substr(dot))' in worker
compiler = shutil.which("clang++-18") or shutil.which("clang++") or shutil.which("g++")
if compiler is None:
    raise SystemExit("C++ compiler missing")
with tempfile.TemporaryDirectory(prefix="gbaxy-same-folder-") as tmp:
    out = Path(tmp) / "test_same_folder"
    cmd = [compiler, "-std=c++20", "-O1",
           "-ffunction-sections", "-fdata-sections",
           "-I"+str(repo / "gba/src"), "-I"+str(repo / "ps5/frontend"),
           str(repo / "tests/test_gbaxy_cover_sibling.cpp"),
           str(repo / "ps5/frontend/fe_covers.cpp"),
           "-Wl,--gc-sections", "-pthread", "-o", str(out)]
    subprocess.run(cmd, check=True)
    subprocess.run([str(out), str(Path(tmp) / "fixtures")], check=True)
