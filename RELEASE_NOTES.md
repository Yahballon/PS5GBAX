# GBAXY v2.2.1 by YAHBALLON

## Fix: PS5 SIGSYS crash when closing GBAXY

- Replace the C library `exit(0)` in the native CoverFlow close path with the PS5 system-service request `sceSystemServiceLoadExec("exit", nullptr)` **after resource shutdown**.
- Override `catchReturnFromMain` in the native CRT so an ordinary return from `main()` cannot fall through to the forbidden libc exit syscall.
- When the system service declines a shutdown, log the return code to `/data/PS5GBA/logs/boot.log` and wait for the shell instead of crashing.
- Keep `PPSA99209`, existing game ROMs, saves, settings, cache, GBA core and Porpoise UI unchanged.

**Validation:** CI compilation and tests do not prove the fix on real PS5 hardware. Verify pressing ○ then × closes without the CE-10 / SIGSYS error.

---
# PS5GBA v2.1 by YAHBALLON

(AI-assisted) Native PS5 Game Boy Advance emulator using mGBA 0.10.5.
App ID: **PPSA99209**.

- Fix Issue #1: correct cached `.gba` extension filtering (including `.GBA`), recognize internal `games/` and `roms/` folders, and fix old SNES-format text in the empty library screen.
- Automatic Libretro GBA box-art matching, disk caching and R2 cover refresh.
- Default graphics: 4K output, 4K ENHANCED, Stretch, Integer Scaling on,
  and VSync off. Existing explicit settings and saves are preserved.
- Routine mGBA DEBUG/INFO traces are suppressed; warnings and errors remain.
- Local, USB and NFS game loading, battery saves, save states and configurable
  controller shortcuts. See the README for controls and supported paths.

## Installation

Download the application ZIP attached to the release, extract it and copy the
complete `PPSA99209` folder to `/data/homebrew/`. Preserve `/data/PS5GBA/` when
updating. GitHub's automatic source archives are not installable applications.
No games or proprietary BIOS images are included.

## Validation status

Earlier native builds and host tests were reported as passing. These historical
results have not been rerun for this source checkout. Smooth gameplay was
reported with the selected graphics configuration; the v2.1 release build still
requires a PS5 console retest. General firmware compatibility and sustained
GPU performance across games have not been established. See `TESTING.md` and
`RELEASING.md` before publishing.

## Fresh build validation — 2026-10-10

(AI-assisted) Compiled in Ubuntu with Clang/LLVM 18 using the prepared PS5
dependencies. Native link, ELF memory parameters, signed-container integrity
and the PPSA99209 filesystem helper passed. The host regression suite passed
for the GBA core, library/settings, resampling and Vulkan rendering through 4K.
ZIP CRC, required files, title ID and all 16 build-manifest file hashes passed.
Package: `dist/PS5GBA-v2-by-YAHBALLON.zip`; SHA-256 is recorded in
`VERIFICATION.json` and the adjacent checksum file. PS5 hardware testing remains
pending; host rendering results do not establish console GPU performance.
