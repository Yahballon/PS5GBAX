// (AI-assisted) Regression tests for general fuzzy GBA artwork matching.
// SPDX-License-Identifier: GPL-3.0-or-later
#include "cover_urls.h"
#include <cassert>
#include <cstdio>
#include <string>

static void Check(const char* rom, const char* expected) {
    fe::GameInfo g;
    g.stem=rom;
    g.title=rom;
    const auto urls=gba::CoverUrls(g);
    const std::string path=gba::CoverEncode(expected);
    if(urls.empty() || urls.front().find(path)==std::string::npos) {
        std::fprintf(stderr,"FAIL: %s\\nexpected artwork: %s\\nfirst URL: %s\\n",
             rom,expected,urls.empty()?"<none>":urls.front().c_str());
        std::abort();
    }
}
int main() {
    Check("1636 - Pokemon Fire Red (U)(Squirrels)",
          "Pokemon - FireRed Version (USA).png"); // existing exact/alias logic
    Check("Metriod Fusion (USA)", "Metroid Fusion (USA)"); // transposed letters
    Check("Sonic Adavance 2 (USA)", "Sonic Advance 2 (USA)"); // typo + sequel
    Check("Super Mario Advance 2 - Super Mario Wrld (USA, Australia)",
          "Super Mario Advance 2 - Super Mario World (USA, Australia).png");
    Check("Advance Wars 2 - Black Hole Risng (USA)",
          "Advance Wars 2 - Black Hole Rising (USA)");
    Check("Legend of Zelda, The - The Minsh Cap (USA)",
          "Legend of Zelda, The - The Minish Cap (USA)");
    Check("Fnal Fantasy VI Advance (USA)","Final Fantasy VI Advance (USA).png");
    Check("Super Mario Advance 2 (USA, Australia)",
          "Super Mario Advance 2 - Super Mario World (USA, Australia).png"); // partial prefix

    // A typo cannot silently switch a game's numbered sequel.
    assert(gba::CoverFuzzyScore("sonicadvance9","sonicadvance3")==-1);
    assert(gba::CoverFuzzyScore("advancewars2","advancewars")==-1);
    // Short generic prefixes are too ambiguous for automatic selection.
    assert(gba::CoverFuzzyScore("sonicadvance","sonicadvance2")==-1);

    // Identical region alternatives aren't independent games, but two
    // similarly named different games must not be guessed.
    const gba::CoverEntry duplicate_regions[]={
        {"metroidfusion","Metroid Fusion (USA).png"},
        {"metroidfusion","Metroid Fusion (Europe).png"}
    };
    assert(gba::CoverBestFuzzyKey("metriodfusion",duplicate_regions,2).key=="metroidfusion");
    const gba::CoverEntry ambiguous[]={
        {"sonicadvanze2","A (USA).png"},
        {"sonicadvancz2","B (USA).png"}
    };
    assert(gba::CoverBestFuzzyKey("sonicadvanzz2",ambiguous,2).key.empty());
    std::puts("PASS: fuzzy GBA artwork aliases, misspellings, shortened titles, sequel safety, ambiguous-name rejection");
}
