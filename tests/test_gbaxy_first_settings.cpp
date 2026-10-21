// (AI-assisted) Regression for the first settings edit of a newly discovered game.
// GPL-3.0-or-later
#include "fe_options.h"
#include "fe_settings.h"
#include <cassert>
#include <cstdio>
#include <string>
#include <sys/stat.h>
#include <unistd.h>

static fe::OptionsSheet::Row FindRow(const fe::OptionsSheet& sheet, const std::string& key) {
    for (const auto& row : sheet.rows()) {
        if (row.kind == fe::OptionsSheet::Kind::Option && row.def && row.def->key == key)
            return row;  // Deliberately copy: Save() rebuilds all sheet rows.
    }
    std::fprintf(stderr,"missing setting %s\n",key.c_str());
    std::abort();
}
int main(int argc, char** argv) {
    assert(argc==2);
    const std::string root=argv[1];
    assert(mkdir(root.c_str(),0777)==0);
    fe::OptionsPaths paths;
    paths.settings_dir=root+"/settings"; // Does not exist on a fresh console.
    paths.gs_ini=root+"/gs.ini";
    fe::GameInfo game;
    game.stem="Legend of Zelda, The - A Link to the Past & Four Swords (USA)";
    game.title=game.stem;
    game.serial="GBA-BB94D4C2";
    fe::OptionsSheet sheet;
    sheet.Open(paths,&game);
    const auto config=paths.settings_dir+"/"+game.stem+".ini";
    assert(access(config.c_str(),F_OK)!=0);
    assert(sheet.Step(FindRow(sheet,"GBA/Graphics"),1));
    assert(access(config.c_str(),F_OK)==0);
    assert(sheet.saved()==1);
    sheet.Open(paths,&game);
    assert(sheet.Step(FindRow(sheet,"GBA/Sharpness"),1));
    sheet.Open(paths,&game);
    assert(sheet.Step(FindRow(sheet,"GBA/Aspect"),1));
    const auto v=sheet.Value(FindRow(sheet,"GBA/Graphics"));
    assert(!v.empty());
    std::string actual;
    assert(fe::settings::ReadFile(config,actual));
    assert(actual.find("GBA/Graphics=")!=std::string::npos);
    assert(actual.find("GBA/Sharpness=")!=std::string::npos);
    assert(actual.find("GBA/Aspect=")!=std::string::npos);
    // Global sheet and control tab must still work after a fresh-game write.
    sheet.Open(paths,nullptr);
    assert(sheet.Step(FindRow(sheet,"GBA/FPS"),1));
    sheet.Open(paths,&game);
    sheet.SetTab(fe::kTabControls);
    assert(sheet.Step(FindRow(sheet,"GBA/ButtonA"),1));
    std::puts("PASS: new game first settings creation, repeated edits, global, controls");
}
