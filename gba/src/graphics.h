// (AI-assisted) Pure GBA viewport calculations shared with the native runtime and tests.
#pragma once
#include <algorithm>
#include <cmath>
namespace gba {struct Viewport {float x,y,width,height;};
inline Viewport GameViewport(float w,float h,bool stretch,bool integer){float width=std::min(w,h*1.5f),height=width/1.5f;if(stretch){width=w;height=h;}else if(integer){float scale=std::max(1.f,std::floor(std::min(w/240.f,h/160.f)));width=240*scale;height=160*scale;}return {(w-width)/2,(h-height)/2,width,height};}}
