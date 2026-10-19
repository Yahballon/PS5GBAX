#!/usr/bin/env python3
from pathlib import Path
import json
r=Path(__file__).resolve().parents[1]
a=(r/"gba/src/loading.cpp").read_text()
b=(r/"ps5/frontend/fe_exact_porpoise.cpp").read_text()
c=(r/"ps5/frontend/fe_options.cpp").read_text()
d=json.loads((r/"gba/sce_sys/param.json").read_text())
assert "ADVANCE CURRENT" in a and "gbaxy_build::kVersion" in a
assert all(x in a for x in ["progress.games","progress.entries","progress.directory","progress.sources_total"])
for t in ["advance-wave","pixel-mint","lava-pulse","silver-core","cosmic-violet"]:
    assert t in b and t in c,t
assert d["titleId"]=="PPSA99209" and d["localizedParameters"]["en-US"]["titleName"]=="GBAXY"
assert "GBAXYCaseSize" in b and "gba::" not in b
print("PASS: GBAXY themes, Advance Current loader, mGBA title ID and adaptive portrait covers")
