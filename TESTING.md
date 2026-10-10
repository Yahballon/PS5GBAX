# Verification

(AI-assisted) Historical verification supplied with the project reports that the following host checks passed; these have not been rerun for this source checkout: real mGBA ARM execution, 240×160 color framebuffer, nonzero audio, 59.72750092 FPS, controller A/menu/fast forward, SRAM persistence across reload, save-state restoration including cartridge memory, raw/ZIP loading, recursive ROM scan, graphics/controller INI persistence, continuous 32768→48000 Hz stereo resampling, GLSL compilation, actual Vulkan ORIGINAL/SMOOTH/ENHANCED output, reusable texture uploads, and 1080p/4K aspect/integer/stretch calculations. Fresh release validation must be recorded separately using RELEASING.md.

Vulkan previews use CPU llvmpipe, not the PS5 GPU. Measured host frames with readback/export were around 20–40 ms at 720p and 145–190 ms at 4K, so they verify rendering correctness rather than console speed. PS5 GPU performance has not been measured. No automatic effect downgrade is claimed.

Console checklist: launch PPSA99209; test local/USB/NFS `.gba` and ZIP games; confirm button mapping and touchpad return; restart and check battery/state/settings persistence; compare presets at 1080p and 4K; check game sound and timing during long sessions; check resolution/VSync fallback logs; repeat library/game transitions and fast-forward; inspect `/data/PS5GBA/logs/boot.log`. Test Flash/EEPROM and RTC cartridges, optional BIOS, and NFS-offline startup on hardware. SRAM was exercised directly by original homebrew; other save devices rely on mGBA's existing implementations and still need console coverage.

## Fresh build validation — 2026-10-10

(AI-assisted) Compiled in Ubuntu with Clang/LLVM 18 using the prepared PS5
dependencies. Native link, ELF memory parameters, signed-container integrity
and the PPSA99209 filesystem helper passed. The host regression suite passed
for the GBA core, library/settings, resampling and Vulkan rendering through 4K.
ZIP CRC, required files, title ID and all 16 build-manifest file hashes passed.
Package: `dist/PS5GBA-v2-by-YAHBALLON.zip`; SHA-256 is recorded in
`VERIFICATION.json` and the adjacent checksum file. PS5 hardware testing remains
pending; host rendering results do not establish console GPU performance.
