#!/usr/bin/env python3
"""(AI-assisted) Host-native CoverFinder same-folder regression and retry contract."""
from pathlib import Path
import base64
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
    # Real, valid 20x20 RGB samples (generated once; test needs no PIL).
    images = Path(tmp) / "fixtures" / "games"
    images.mkdir(parents=True)
    images.joinpath("actual-art.png").write_bytes(base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAIAAAAC64paAAAAHUlEQVR4nGPcp+vIQC5gIlvnqOZRzaOaRzVTRTMA+DQBVPBR3qkAAAAASUVORK5CYII="))
    images.joinpath("actual-art.jpg").write_bytes(base64.b64decode(
        "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAA0JCgsKCA0LCgsODg0PEyAVExIS"
        "EyccHhcgLikxMC4pLSwzOko+MzZGNywtQFdBRkxOUlNSMj5aYVpQYEpRUk//"
        "2wBDAQ4ODhMREyYVFSZPNS01T09PT09PT09PT09PT09PT09PT09PT09PT09P"
        "T09PT09PT09PT09PT09PT09PT09PT0//wAARCAAUABQDASIAAhEBAxEB/8QA"
        "FQABAQAAAAAAAAAAAAAAAAAAAAX/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QA"
        "FgEBAQEAAAAAAAAAAAAAAAAAAAQG/8QAFBEBAAAAAAAAAAAAAAAAAAAAAP/a"
        "AAwDAQACEQMRAD8AkAJ2pAAAAAAf/9k="
    ))
    out = Path(tmp) / "test_same_folder"
    cmd = [compiler, "-std=c++20", "-O1",
           "-ffunction-sections", "-fdata-sections",
           "-I"+str(repo / "gba/src"), "-I"+str(repo / "ps5/frontend"),
           str(repo / "tests/test_gbaxy_cover_sibling.cpp"),
           str(repo / "ps5/frontend/fe_covers.cpp"),
           "-Wl,--gc-sections", "-pthread", "-o", str(out)]
    subprocess.run(cmd, check=True)
    subprocess.run([str(out), str(Path(tmp) / "fixtures")], check=True)
