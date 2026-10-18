# Preparing a PS5GBA release

(AI-assisted) Release preparation is separate from publishing a GitHub release.

1. Review `git status --short` and include the required source, assets and
   license files. Keep generated builds, local configuration and user data out
   of Git. Run `python3 gba/tools/check_release.py` to check source hygiene.
2. Follow `BUILDING.md` on Linux with the prepared PS5 dependencies, then run
   `python3 gba/tools/test.py`. Record fresh results in `VERIFICATION.json`;
   previous reported results are historical, not verification of a new build.
3. Run the console checklist in `TESTING.md`. Keep the release marked as
   requiring console validation until that build has actually been tested.
4. Inspect `gba/build-shelf/PS5GBA-v2.1-by-YAHBALLON.zip`.
   It must contain `PPSA99209/eboot.bin`, `sce_sys/param.json`, the icon,
   `sce_module/libc.prx`, `lapy.elf`, `lapy-manifest.json`, `build-manifest.json`
   and the `licenses/` directory. Check the title ID and ZIP integrity.
5. Compute the ZIP's SHA-256 and record its exact filename and digest with the
   release. Include the corresponding source and all dependency notices; verify
   that externally built components' source and license obligations are met.
6. Review `RELEASE_NOTES.md`, tag the reviewed commit, and upload the application
   ZIP as a GitHub release asset. GitHub's automatic source ZIP is source only
   and cannot be installed as the application.

CI source and ROM regression checks run on GitHub-hosted Ubuntu 24.04. Native compilation also runs on GitHub-hosted Ubuntu and bootstraps the public PS5 Vulkan, Payload SDK, PacBrew, libnfs and title-bound Lapy dependencies. A push to `main` builds and publishes the signed ZIP as `v2.1.0` only after validation; tags `v*` and manual `workflow_dispatch` are supported. The workflow refuses to overwrite an existing release. The initial graphics toolchain build may take significant runner time; if dependencies fail, the job fails without publishing a fake package. A successful CI build still requires on-console verification.

Generated application ZIPs are kept in ignored build/dist folders and are not included in Git source archives. Do not describe a
release as verified merely because an earlier package passed checks.
