from pathlib import Path
import subprocess,zipfile
r=Path(__file__).resolve().parents[2];out=r/'gba/build-tests';out.mkdir(exist_ok=True)
(out/'start.s').write_text('.syntax unified\n.arm\n.section .header,"ax"\n.global _start\n_start: b startup\n.space 188\nstartup: ldr sp,=0x03007f00\nbl gba_main\nb .\n')
(out/'test.c').write_text('''// (AI-assisted) Original homebrew test: red screen, square-wave audio, button and SRAM probe.
typedef unsigned short u16;typedef unsigned char u8;
void gba_main(void){volatile u16* io=(u16*)0x04000000;io[0]=0x403;volatile u16* v=(u16*)0x06000000;for(int i=0;i<240*160;i++)v[i]=31;
io[0x84/2]=0x80;io[0x80/2]=0x2277;io[0x82/2]=2;io[0x68/2]=0xf080;io[0x6c/2]=0x8000|1750;
volatile u8* save=(u8*)0x0e000000;for(;;){save[0]=(u8)(~io[0x130/2]&1);}}
''')
(out/'link.ld').write_text('ENTRY(_start)\nSECTIONS { . = 0x08000000; .text : { *(.header) *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment) } }')
for file in ['start.s','test.c']:
 subprocess.run(['clang-18','--target=arm-none-eabi','-mcpu=arm7tdmi','-marm','-O2','-ffreestanding','-fno-builtin','-c',str(out/file),'-o',str(out/(file+'.o'))],check=True)
subprocess.run(['ld.lld-18','-T',str(out/'link.ld'),str(out/'start.s.o'),str(out/'test.c.o'),'-o',str(out/'test.elf')],check=True)
subprocess.run(['llvm-objcopy-18','-O','binary',str(out/'test.elf'),str(out/'test.gba')],check=True)
b=bytearray((out/'test.gba').read_bytes());b[0xA0:0xAC]=b'PS5GBA TEST ';b[0xB2]=0x96;b[0xBD]=(-(sum(b[0xA0:0xBD])+0x19))&255;b.extend(b'\0'*(32768-len(b)));(out/'test.gba').write_bytes(b)
with zipfile.ZipFile(out/'test.zip','w',zipfile.ZIP_DEFLATED) as z:z.writestr('original-test.gba',b)
(out/'session-test.cpp').write_text('''// (AI-assisted) Real mGBA integration with original homebrew; no commercial game or BIOS.
#include "core_session.h"
#include "controller_bindings.h"
#include <cassert>
#include <fstream>
#include <algorithm>
#include <cstdio>
int main(int argc,char**argv){assert(argc==3);std::ifstream f(argv[1],std::ios::binary);std::vector<uint8_t> rom((std::istreambuf_iterator<char>(f)),{});gba::Session s(argv[2]);s.SetOption("mgba_skip_bios","ON");assert(s.Load("test.gba",rom));assert(s.fps>59.72&&s.fps<59.74);bool heard=false;for(int i=0;i<30;++i){s.Run();heard|=std::any_of(s.audio.begin(),s.audio.end(),[](auto v){return v!=0;});}assert(s.width==240&&s.height==160);assert((s.pixels[20000]&255)>240);assert(heard);gba::ControllerBindings c;c.Load({});c.Update(0,0);s.buttons[0]=c.Update(0x4000,1).joypad;assert(s.buttons[0]==256);s.Run();s.Run();auto* mem=(uint8_t*)retro_get_memory_data(RETRO_MEMORY_SAVE_RAM);assert(mem[0]==1);assert(s.SaveState());s.buttons[0]=0;s.Run();assert(mem[0]==0);assert(s.LoadState());assert(mem[0]==1);assert(s.SaveBattery());assert(s.Unload());assert(s.Load("test.gba",rom));mem=(uint8_t*)retro_get_memory_data(RETRO_MEMORY_SAVE_RAM);assert(mem[0]==1);assert(s.Unload());assert(!s.Load("bad.gba",std::vector<uint8_t>(256)));assert(c.Update(0x100,2).fast_forward);assert(c.Update(0x40100000,3).menu);printf("PASS real mGBA 240x160 video, nonzero audio, %.8f FPS, GBA inputs, battery save and state roundtrip\\n",s.fps);}
''')
(out/'saves').mkdir(exist_ok=True);(out/'states').mkdir(exist_ok=True)
subprocess.run(['clang++-18','-std=c++20','-O1','-I'+str(r/'gba/src'),'-I'+str(r/'gba/include'),'-I'+str(r/'ps5/frontend'),str(out/'session-test.cpp'),str(r/'gba/src/core_session.cpp'),str(r/'gba/src/controller_bindings.cpp'),str(r/'gba/build-core-host/mgba_libretro.so'),'-Wl,-rpath,'+str(r/'gba/build-core-host'),'-o',str(out/'session-test')],check=True)
subprocess.run([str(out/'session-test'),str(out/'test.gba'),str(out/'saves')],check=True,stdout=open(out/'core-test.log','w'),stderr=subprocess.STDOUT)


