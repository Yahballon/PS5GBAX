# Building PS5GBA

(AI-assisted) Use WSL Ubuntu/Linux, Clang/LLVM 18, Python 3, CMake, Ninja, make and zlib development headers. Source layout: `gba/src/` is the adapter/runtime; `gba/third_party/mgba/` is the pinned upstream core; `ps5/frontend/` is the reused native UI/renderer; `ps5/proto/native/tooling/` contains the native app writer.

Use the same prepared dependency set as PS5SNES: the PS5 Payload SDK under `PS5_Vulkan/.deps/native/ps5-payload-sdk`, the native Vulkan driver/support archives and runtime, `filesystem-helper`/Lapy with pacbrew curl/OpenSSL/zlib libraries, and `libnfs-install`. These external SDK dependencies are not bundled into the source ZIP. No source files from PS5SNES are required to build this project.

```sh
PS5GBA_DEPS=/path/to/prepared/ps5-build bash gba/tools/build.sh
```

Override `PS5_PAYLOAD_SDK`, `LIBNFS_PREFIX`, or `LIBZ_PREFIX` if your dependencies use other locations. The core uses upstream CMake to generate the GBA-only source list and version header, then compiles the selected C files for `x86_64-sie-ps5`; the frontend follows the original PS5SNES native link/sign/package workflow. No Qt, SDL, GB core, JIT or OpenGL renderer is linked.

The compiled SPIR-V is included in the source. After shader edits, regenerate it with a host glslang compiler:

```sh
GLSLANG_VALIDATOR=/path/to/glslangValidator bash ps5/frontend/build_shaders.sh
```

Build output: `gba/build-shelf/PS5GBA-v2.1-by-YAHBALLON.zip`. Upload this generated application ZIP as a release asset; no prebuilt application is included in this source checkout. See [RELEASING.md](RELEASING.md) for the release checklist. The package includes the application-specific elevation helper, `eboot.bin`, metadata/icon, `sce_module/libc.prx` and license notices.

Host tests (Clang/LLVM 18, Mesa Vulkan/llvmpipe and zlib required):

```sh
python3 gba/tools/test.py
```

Core revision: 26b7884bc25a5933960f3cdcd98bac1ae14d42e2 (mGBA 0.10.5). Frontend: GPL-3.0-or-later; mGBA: MPL-2.0. Console test status is recorded separately from build success.
