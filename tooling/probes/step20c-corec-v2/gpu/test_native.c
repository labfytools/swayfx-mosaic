#include <GLES3/gl3.h> /* private G2 state observability */
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <pixman.h>
#include <time.h>
#include <unistd.h>
#include <wlr/render/allocator.h>
#include <wlr/render/drm_syncobj.h>
#include <wlr/util/transform.h>
#include <wlr/util/log.h>
#include <wlr/util/region.h>

#include "render/egl.h"
#include "render/fx_renderer/fx_renderer.h"
#include "render/fx_renderer/shaders.h"
#include "render/pass.h"
#include "render/tracy.h"
#include "scenefx/render/fx_renderer/fx_offscreen_buffers.h"
#include "scenefx/render/fx_renderer/fx_renderer.h"
#include "scenefx/types/fx/blur_data.h"
#include "util/matrix.h"

#include "g2_native.h"


#include <sys/resource.h>
#include <sys/prctl.h>
int main(void) {
 struct rlimit r={0,0};assert(!setrlimit(RLIMIT_CORE,&r));assert(!prctl(PR_SET_DUMPABLE,0));
 struct fx_gles_render_pass passes[9]={0};
 struct wlr_output h1={.name="HEADLESS-1",.scale=1,.transform=WL_OUTPUT_TRANSFORM_NORMAL};
 struct wlr_output h2={.name="HEADLESS-2",.scale=1,.transform=WL_OUTPUT_TRANSFORM_NORMAL};
 for(unsigned i=0;i<9;i++) {
  g2_track_output(&passes[i],i%2?&h2:&h1);
  assert(g2_intended_output(&passes[i])==(i%2==0));
  g2_forget_output(&passes[i]);assert(!g2_intended_output(&passes[i]));
 }
 assert(!g2.stopped);
 g2_track_output(&passes[0],&h1);assert(g2_intended_output(&passes[0]));
 g2_track_output(&passes[0],&h2);assert(!g2_intended_output(&passes[0]));
 g2_forget_output(&passes[0]);g2_track_output(&passes[0],&h1);assert(g2_intended_output(&passes[0]));g2_forget_output(&passes[0]);
 for(unsigned i=0;i<9;i++)g2_track_output(&passes[i],i%2?&h2:&h1);
 assert(g2.stopped && !g2_intended_output(&passes[8]));
 for(unsigned i=0;i<9;i++) {g2_forget_output(&passes[i]);}
 g2.stopped=false;
 puts("PASS nine sequential passes/output forget, pointer reuse H1/H2 and nine-simultaneous fail-closed overflow");
 struct g2_sample s={.width=800,.height=600,.bytes=800*600*4};s.pixels=calloc(1,s.bytes);assert(s.pixels);
 for(int y=0;y<600;y++)for(int x=0;x<800;x++) {
  const unsigned char a[2][3]={{245,245,245},{15,25,45}};
  memcpy(s.pixels+((size_t)y*800+(size_t)x)*4,a[(x/8)%2],3);
 }
 assert(g2_expected_source(&s,1));assert(g2_expected_source(&s,3));assert(!g2_expected_source(&s,2));
 s.pixels[4]^=1;assert(!g2_expected_source(&s,1));s.pixels[4]^=1;
 for(int y=0;y<600;y++)for(int x=0;x<800;x++) {
  const unsigned char b[2][3]={{32,192,224},{176,32,64}};
  memcpy(s.pixels+((size_t)y*800+(size_t)x)*4,b[(x/8)%2],3);
 }
 assert(g2_expected_source(&s,2));assert(!g2_expected_source(&s,3));free(s.pixels);
 assert(g2_crc((const unsigned char *)"123456789",9)==UINT32_C(0xcbf43926));
 FILE *f=tmpfile();assert(f && g2_owned(fileno(f),0600));assert(g2_write(fileno(f),"frame",5));assert(!fseek(f,0,SEEK_SET));char b[6]={0};assert(fread(b,1,5,f)==5 && !strcmp(b,"frame"));assert(!fclose(f));
 assert(!setenv("MOSAIC_G2_DIR","/tmp",1));assert(!setenv("MOSAIC_G2_NONCE","aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",1));
 assert(!g2_open() && g2.stopped && g2.dir==-1);
 puts("PASS exact native source epoch RGB admission A/B/A-return and negative substitution");
 puts("PASS exact native CRC framing/writer/owned FD cleanup and wrong realpath refusal");
 return 0;
}
