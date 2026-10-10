# PS5GBA v2 by YAHBALLON

(AI-assisted) Native PS5 Game Boy Advance emulator using mGBA 0.10.5.
App ID: **PPSA99209**.

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
reported with the selected graphics configuration; the v2 release build still
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
