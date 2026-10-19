#include "fe_gbaxy_cover_aspect.h"
#include <cassert>
#include <cmath>
#include <iostream>
static bool near(float a,float b){return std::fabs(a-b)<0.005f;}
int main(){
 auto portrait=fe::GBAXYCaseSize(fe::GBAXYImageRatio(700,920),448,435);
 assert(portrait.height>portrait.width&&near(portrait.width/portrait.height,700.f/920));
 auto square=fe::GBAXYCaseSize(1.f,448,435);
 assert(near(square.width,square.height));
 auto wide=fe::GBAXYCaseSize(1.5f,448,435);
 assert(wide.width>wide.height&&wide.width<=435);
 auto fitted=fe::GBAXYFitInside(1.f,portrait.width,portrait.height);
 assert(near(fitted.width,fitted.height));
 std::cout<<"PASS GBAXY uncropped adaptive GBA cover dimensions\n";
}
