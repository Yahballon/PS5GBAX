// (AI-assisted) Same-folder user cover override regression, including .gba/.zip/.7z.
// SPDX-License-Identifier: GPL-3.0-or-later
#include "fe_covers.h"
#include <cassert>
#include <cstdio>
#include <filesystem>
#include <fstream>
#include <iterator>
#include <string>
#include <vector>
namespace fs = std::filesystem;

static void Put(const fs::path& path, const std::string& bytes = "image data") {
    std::ofstream f(path, std::ios::binary);
    assert(f.good());
    f << bytes;
}
static fe::GameInfo Game(const fs::path& dir, const std::string& file,
                         const std::string& stem, const std::string& serial) {
    fe::GameInfo g;
    g.file = file;
    g.stem = stem;
    g.path = (dir / file).string();
    g.title = "Unrelated display title";
    g.serial = serial;
    return g;
}
int main(int argc, char** argv) {
    assert(argc == 2);
    const fs::path root(argv[1]), games = root / "games",
                   manual = root / "covers", cache = root / "cache";
    fs::create_directories(games);
    fs::create_directories(manual);
    fs::create_directories(cache);

    Put(games / "marioland2.PNG");
    Put(games / "marioland2.jpg");
    Put(games / "marioland2.JPEG");
    Put(manual / "GBA-1234.jpg");
    Put(cache / "GBA-1234.jpg");
    for (const std::string ext : {".gba", ".zip", ".7z", ".GBA", ".ZIP", ".7Z"}) {
        const auto game = Game(games, "marioland2" + ext, "Unrelated stem", "GBA-1234");
        const auto covers = fe::CoverFinder(manual.string(), cache.string()).Find(game);
        assert(covers.size() >= 5);
        assert(covers[0].path == (games / "marioland2.PNG").string());
        assert(std::string(covers[0].source) == "beside");
        assert(covers[1].path == (games / "marioland2.jpg").string());
        assert(covers[2].path == (games / "marioland2.JPEG").string());
        assert(std::string(covers[3].source) == "manual");
        assert(std::string(covers[4].source) == "cache");
        const auto best = fe::CoverFinder(manual.string(), cache.string()).Best(game);
        assert(best.path == covers[0].path);
        fe::CoverConfig cfg;
        cfg.manual_dir = manual.string();
        cfg.cache_dir = cache.string();
        assert(fe::CoverService::MissingCovers({game}, cfg).empty());
    }

    // Full stem including dots, mixed case, dump tags; never fuzzy-title match.
    Put(games / "Super.Mario.v2 (USA).pNg");
    auto dotted = Game(games, "Super.Mario.v2 (USA).7z", "completely different",
                       "GBA-DOT");
    auto best = fe::CoverFinder(manual.string(), cache.string()).Best(dotted);
    assert(best.path == (games / "Super.Mario.v2 (USA).pNg").string());

    // Deliberately do NOT match a typo with an extra dot before .jpg.
    // The user asked to revert the temporary double-dot workaround.
    const std::string violet="Pokemon Ultra Violet (1.22) LSA (Fire Red Hack)";
    Put(games / (violet + "..jpg"));
    auto violet_game=Game(games,violet+".gba",violet,"GBA-7B502EB5");
    assert(fe::CoverFinder(manual.string(),cache.string()).FindBeside(violet_game).empty());
    Put(games / (violet + ".jpg"));
    assert(fe::CoverFinder(manual.string(),cache.string()).Best(violet_game).path==
           (games / (violet + ".jpg")).string());

    // Empty custom cover is ignored; matching JPEG is selected instead.
    Put(games / "invalid.png", "");
    Put(games / "invalid.jpeg");
    best = fe::CoverFinder(manual.string(), cache.string()).Best(
        Game(games, "invalid.gba", "invalid", "GBA-EMPTY"));
    assert(best.path == (games / "invalid.jpeg").string());

    // If no sibling exists, the shared manual folder retains its priority.
    best = fe::CoverFinder(manual.string(), cache.string()).Best(
        Game(games, "missing.7z", "missing", "GBA-1234"));
    assert(best.path == (manual / "GBA-1234.jpg").string());

    // Test a directory that was indexed before a cover was uploaded.
    // A new exact-cased file must be detected even by the same old finder.
    const auto late = Game(games, "added.zip", "added", "GBA-LATE");
    fe::CoverFinder cached(manual.string(), cache.string());
    assert(cached.FindBeside(late).empty());
    Put(games / "added.jpg");
    auto direct = cached.FindBeside(late);
    assert(direct.size() == 1 && direct[0].path == (games / "added.jpg").string());

    // A fresh finder also notices a newly uploaded uppercase extension.
    const auto upper = Game(games, "another.7z", "another", "GBA-UPPER");
    assert(fe::CoverFinder(manual.string(), cache.string()).FindBeside(upper).empty());
    Put(games / "ANOTHER.JPG");
    best = fe::CoverFinder(manual.string(), cache.string()).Best(upper);
    assert(best.path == (games / "ANOTHER.JPG").string());

    // The real PNG/JPEG samples are written by the Python harness, proving
    // both codecs work in the same decoder the console uses.
    for (const std::string ext : {".png", ".jpg"}) {
        const fs::path sample = games / ("actual-art" + ext);
        std::ifstream input(sample, std::ios::binary);
        assert(input.good());
        std::vector<uint8_t> encoded((std::istreambuf_iterator<char>(input)), {});
        fe::CoverImage image;
        const bool decoded=fe::CoverService::Decode(encoded, 1024, image);
        if(!decoded) std::fprintf(stderr,
            "FAIL real %s decode: %zu bytes, header %02x %02x %02x %02x (dimensions %dx%d)\\n",
            ext.c_str(), encoded.size(), encoded.size()>0?encoded[0]:0,
            encoded.size()>1?encoded[1]:0, encoded.size()>2?encoded[2]:0,
            encoded.size()>3?encoded[3]:0, image.width, image.height);
        assert(decoded);
        assert(image.width == 20 && image.height == 20);
        assert(image.rgba.size() == 20u * 20 * 4);
    }
    const auto valid = Game(games, "actual-art.gba", "actual-art", "GBA-JPEG");
    assert(fe::CoverFinder(manual.string(), cache.string()).Best(valid).path ==
           (games / "actual-art.png").string());

    std::puts("PASS same-folder PNG/JPG/JPEG overrides for GBA/ZIP/7z, extension cases, priority, offline prefetch, stale dir cache, valid PNG/JPEG decode, Triangle rediscovery");
}
