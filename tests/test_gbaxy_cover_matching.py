#!/usr/bin/env python3
"""(AI-assisted) Host-native GBA cover naming and Triangle manual-retry regression."""
from pathlib import Path
import shutil
import subprocess
import tempfile

repo=Path(__file__).resolve().parents[1]
source=(repo/"ps5/frontend/fe_app.cpp").read_text()
assert "in.triangle&&!m_prev.triangle" in source, "Triangle must retry selected cover"
assert "m_covers->Refresh(m_selected)" in source
assert 'hint(icon::Triangle, nullptr, "Retry cover")' in source
compiler=shutil.which("clang++-18") or shutil.which("clang++") or shutil.which("g++")
if not compiler: raise SystemExit("no host C++ compiler")
with tempfile.TemporaryDirectory(prefix="gbaxy-cover-") as temp:
    exe=Path(temp)/"cover-matching"
    subprocess.run([compiler,"-std=c++20","-O1","-I"+str(repo/"gba/src"),
                    "-I"+str(repo/"ps5/frontend"),
                    str(repo/"tests/test_gbaxy_cover_matching.cpp"),"-o",str(exe)],
                   check=True)
    subprocess.run([str(exe)],check=True)
print("PASS Triangle manual retry shortcut and matching contract")
