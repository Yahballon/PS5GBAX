#!/usr/bin/env python3
"""(AI-assisted) Compile and run the full Libretro GBA artwork fuzzy matcher."""
from pathlib import Path
import shutil
import subprocess
import tempfile

root=Path(__file__).resolve().parents[1]
compiler=shutil.which("clang++-18") or shutil.which("clang++") or shutil.which("g++")
if compiler is None: raise SystemExit("Host C++ compiler missing")
with tempfile.TemporaryDirectory(prefix="gbaxy-fuzzy-") as work:
    exe=Path(work)/"test"
    subprocess.run([compiler,"-std=c++20","-O1",
       "-I"+str(root/"gba/src"),"-I"+str(root/"ps5/frontend"),
       str(root/"tests/test_gbaxy_cover_fuzzy.cpp"),"-o",str(exe)],
       check=True)
    subprocess.run([str(exe)],check=True)
