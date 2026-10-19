#!/usr/bin/env python3
"""GBAXY must use GBA artwork (not NES/SNES) and preserve region fallbacks."""
from pathlib import Path
r=Path(__file__).resolve().parents[1]
h=(r/"gba/src/cover_urls.h").read_text()
worker=(r/"ps5/frontend/fe_covers.cpp").read_text()
assert 'https://thumbnails.libretro.com/Nintendo%20-%20Game%20Boy%20Advance/Named_Boxarts/' in h
assert 'https://raw.githubusercontent.com/libretro-thumbnails/Nintendo_-_Game_Boy_Advance/master/Named_Boxarts/' in h
assert 'const std::string url=std::string(host)+CoverEncode(filename)' in h
assert 'if(tried>=3)break' in h
assert 'if(tried<3) add(stem+".png")' in h
assert 'game.region' in h and 'matches.emplace_back' in h
assert 'gba::CoverEncode' in worker and 'snes::CoverEncode' not in worker
assert '"Game Boy Advance"' in worker and '"Nintendo SNES"' not in worker
print("PASS GBAXY direct Libretro GBA covers, GitHub mirror, No-Intro variants and GBA placeholder")
