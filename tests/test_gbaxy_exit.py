#!/usr/bin/env python3
"""Prevent any regression to SIGSYS when closing a PS5 GBAXY native title."""
from pathlib import Path
import json

r=Path(__file__).resolve().parents[1]
ui=(r/'ps5/frontend/fe_ps5.cpp').read_text()
main=(r/'gba/src/main_shelf.cpp').read_text()
crt=(r/'ps5/proto/native/tooling/native/app_crt.cpp').read_text()
version=(r/'gba/src/gbaxy_build_version.h').read_text()
app=json.loads((r/'app.json').read_text())
param=json.loads((r/'gba/sce_sys/param.json').read_text())

assert 'if (app.ExitRequested())' in ui
assert 'gbaxy_exit_to_shell("CoverFlow exit confirmed")' in ui
assert '::exit(0)' not in ui
assert 'extern "C" int sceSystemServiceLoadExec(' in main
assert 'sceSystemServiceLoadExec("exit",nullptr)' in main
assert 'gbaxy_exit_to_shell("frontend completed")' in main
assert 'extern "C" [[noreturn]] void catchReturnFromMain(int status)' in main
assert 'gbaxy_exit_to_shell("CRT main return")' in main
assert 'for(;;)sceKernelUsleep(100000)' in main
assert '__attribute__((weak)) void catchReturnFromMain' in crt
assert 'catchReturnFromMain(status);' in crt and 'exit(status);' in crt
assert app['version']=='2.3.0' and app['releaseTag']=='v2.3.0'
assert param['titleId']=='PPSA99209' and param['contentVersion']=='02.003.000'
assert 'kVersion[] = "2.3.0"' in version
print("PASS: PS5 shell exit, CRT main-return interception, no libc exit, title/version preserved")
