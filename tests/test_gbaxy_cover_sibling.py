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
        "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAAUABQDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwDmqKKK4z78KKKKACiiigAooooA/9k="))
    out = Path(tmp) / "test_same_folder"
    cmd = [compiler, "-std=c++20", "-O1",
           "-ffunction-sections", "-fdata-sections",
           "-I"+str(repo / "gba/src"), "-I"+str(repo / "ps5/frontend"),
           str(repo / "tests/test_gbaxy_cover_sibling.cpp"),
           str(repo / "ps5/frontend/fe_covers.cpp"),
           "-Wl,--gc-sections", "-pthread", "-o", str(out)]
    subprocess.run(cmd, check=True)
    subprocess.run([str(out), str(Path(tmp) / "fixtures")], check=True)
