#!/usr/bin/env python3
"""(AI-assisted) Run the first-game settings creation regression on a host."""
from pathlib import Path
import shutil
import subprocess
import tempfile

repo=Path(__file__).resolve().parents[1]
compiler=shutil.which("clang++-18") or shutil.which("clang++") or shutil.which("g++")
if not compiler: raise SystemExit("C++ compiler missing")
with tempfile.TemporaryDirectory(prefix="gbaxy-settings-") as wd:
    binary=Path(wd)/"test-first-game-settings"
    args=[compiler,"-std=c++20","-O1","-g","-fno-omit-frame-pointer",
          "-I"+str(repo/"ps5/frontend"),
          "-I"+str(repo/"3rdparty/vulkan/include"),
          str(repo/"tests/test_gbaxy_first_settings.cpp"),
          str(repo/"ps5/frontend/fe_options.cpp"),
          str(repo/"ps5/frontend/fe_settings.cpp"),
          "-o",str(binary)]
    subprocess.run(args,check=True)
    subprocess.run([str(binary),str(Path(wd)/"fresh")],check=True)
