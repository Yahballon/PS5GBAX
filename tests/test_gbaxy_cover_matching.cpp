// (AI-assisted) Regression: scene and GoodTools ROM names resolve to real GBA Libretro covers.
// SPDX-License-Identifier: GPL-3.0-or-later
#include "cover_urls.h"
#include <cassert>
#include <cstdio>
#include <string>
#include <vector>

static void Check(const std::string& stem, const std::string& filename) {
    fe::GameInfo game;
    game.stem = stem;
    game.title = stem;
    const auto urls = gba::CoverUrls(game);
    const auto expected = std::string("https://thumbnails.libretro.com/Nintendo%20-%20Game%20Boy%20Advance/Named_Boxarts/") + gba::CoverEncode(filename);
    if(urls.empty() || urls.front()!=expected) {
        std::fprintf(stderr, "FAIL: %s\nexpected: %s\ngot: %s\n",
            stem.c_str(),expected.c_str(),urls.empty()?"<empty>":urls.front().c_str());
        std::abort();
    }
}
int main() {
    Check("1636 - Pokemon Fire Red (U)(Squirrels)",
          "Pokemon - FireRed Version (USA).png");
    Check("1636 - Pokemon Fire Red (U)(Squirrels).gba",
          "Pokemon - FireRed Version (USA).png");
    Check("Pokemon - FireRed Version (USA)",
          "Pokemon - FireRed Version (USA).png");
    Check("Pokemon - Leaf Green (U) [!]",
          "Pokemon - LeafGreen Version (USA).png");
    Check("Pokemon - Ruby (U)",
          "Pokemon - Ruby Version (USA).png");
    Check("Super Mario Advance 2 - Super Mario World (USA, Australia)",
          "Super Mario Advance 2 - Super Mario World (USA, Australia).png");
    Check("007 - NightFire (USA, Europe) (En,Fr,De)",
          "007 - NightFire (USA, Europe) (En,Fr,De).png");
    std::puts("PASS GoodTools catalog prefixes, Pokemon aliases, dump region tags, ordinary/007 names");
}
