# GBAXY v2.3.0 by YAHBALLON

(AI-assisted) Feature and stability release for PS5 Game Boy Advance homebrew (PPSA99209).

## Improvements

- **7z ROMs (Issue #2):** load single-GBA LZMA/LZMA2 archives from local storage, USB or NFS, with memory bounds and archive validation; existing `.gba` and `.zip` support remains.
- **Smarter cover search:** the Libretro GBA artwork index supports scene-dump prefixes (e.g. `1636 -`), No-Intro/GoodTools region labels, Pokemon aliases, and conservative fuzzy name matching that rejects ambiguous sequels.
- **Local ROM-folder cover override:** `My Game.gba`, `My Game.zip` or `My Game.7z` uses `My Game.png`, `My Game.jpg` or `My Game.jpeg` in the same folder. Image filenames are matched case-insensitively; PNG takes priority. Local covers override manual covers, cached thumbnails and automatic download. **Exact basename matching remains required** (the temporary double-dot filename workaround has been removed).
- **Triangle: Retry cover** updates the selected artwork, checks the same ROM folder first (also when offline), and can discover an image uploaded while GBAXY is already open.
- **Settings and stability:** avoid dangling settings-row references on first save and synchronize the GPU when returning from a game to the shelf. The console exit fix from v2.2.1 remains.
- **Diagnostics:** clearer cover decoding and local-file errors in `/data/PS5GBA/logs/boot.log`.

## Installation

Download `PPSA99209.zip` from the release assets, extract the `PPSA99209` directory and copy it to `/data/homebrew/`. Preserve `/data/PS5GBA/` to keep ROMs, save games, screenshots, settings and cache. The automatically generated GitHub source ZIP is not an installable application.

## Verification

The user reports that the tested homebrew and local cover detection now work on PS5. CI performs native PS5 compilation, source checks, archive tests and ZIP integrity checks before publishing. The specific published v2.3.0 package still requires on-console regression testing after version bump.

---
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
