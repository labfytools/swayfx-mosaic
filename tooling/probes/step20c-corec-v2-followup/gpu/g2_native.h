/* PRIVATE G3 admission; G2 symbols/hooks preserved. No public API. */
#ifndef G2_NATIVE_H
#define G2_NATIVE_H
#include "g2_gl.h"
#include <fcntl.h>
#include <sys/stat.h>
#include <errno.h>
#include <inttypes.h>
#include <limits.h>
#include <wlr/render/dmabuf.h>
#include <drm_fourcc.h>
#include <wlr/types/wlr_buffer.h>
#ifndef G3_ROOT
#error "Define G3_ROOT as the reviewed new LAB acquisition path"
#endif
#define G2_ROOT G3_ROOT
static struct {
 bool stopped, active; unsigned epoch, point; size_t used;
 int dir; FILE *meta; const void *pass, *output;
 uintptr_t pass_sequence; char nonce[65];
} g2={.dir=-1};
static const char *g2_names[]={"source","down0","down1","down2","up2","up1","up0","optimized-cache","no-blur-cache","composition-presubmit"};
static void g2_fail(const char *reason) {
 g2.stopped=true;
 if(g2.meta) {fprintf(g2.meta,"{\"kind\":\"rejected\",\"reason\":\"%s\",\"point\":%u}\n",reason,g2.point); fflush(g2.meta); fsync(fileno(g2.meta)); fclose(g2.meta); g2.meta=NULL;}
 g2.active=false;
}
static uint32_t g2_crc(const unsigned char *p,size_t n) {
 uint32_t crc=~0u;
 for(size_t i=0;i<n;i++) {crc^=p[i]; for(int b=0;b<8;b++) crc=(crc>>1)^((0u-(crc&1u))&0xedb88320u);}
 return ~crc;
}
static bool g2_write(int fd,const void *ptr,size_t n) {
 const char *p=ptr; while(n) {ssize_t k=write(fd,p,n); if(k<0 && errno==EINTR) continue; if(k<=0)return false; p+=k;n-=(size_t)k;} return true;
}
static void g2_error_json(const char *name,struct g2_errors e) {
 fprintf(g2.meta,",\"%s\":{\"exhausted\":%s,\"codes\":[",name,e.exhausted?"true":"false");
 for(unsigned i=0;i<e.count;i++) {fprintf(g2.meta,"%s%u",i?",":"",e.values[i]);}
 fputs("]}",g2.meta);
}
static void g2_state_json(const char *name,const struct g2_state *s) {
 fprintf(g2.meta,",\"%s\":{\"read_draw_rbo_pack_pbo_row_skip\":[%d,%d,%d,%d,%d,%d,%d,%d],\"viewport\":[%d,%d,%d,%d],\"scissor\":[%d,%d,%d,%d],\"scissor_enabled\":%u,\"program_active_texture\":[%d,%d,%d]}",name,s->read_fbo,s->draw_fbo,s->rbo,s->pack,s->pbo,s->row,s->skip_rows,s->skip_pixels,s->viewport[0],s->viewport[1],s->viewport[2],s->viewport[3],s->scissor[0],s->scissor[1],s->scissor[2],s->scissor[3],s->scissor_on,s->program,s->active,s->texture);
}
static void g2_region(const pixman_region32_t *region) {
 int n=0; pixman_box32_t *r=region?pixman_region32_rectangles(region,&n):NULL;
 fputs(",\"fresh_rectangles\":[",g2.meta);
 if(n>256) {fputs("],\"fresh_region_overflow\":true",g2.meta);return;}
 for(int i=0;i<n;i++)fprintf(g2.meta,"%s[%d,%d,%d,%d]",i?",":"",r[i].x1,r[i].y1,r[i].x2,r[i].y2);
 fputs("]",g2.meta);
}
static bool g2_dmabuf_supported(struct fx_framebuffer *b) {
 struct wlr_dmabuf_attributes a={0};
 if(!wlr_buffer_get_dmabuf(b->buffer,&a))return false;
 bool format=a.format==DRM_FORMAT_ABGR8888 || a.format==DRM_FORMAT_XBGR8888 || a.format==DRM_FORMAT_ARGB8888 || a.format==DRM_FORMAT_XRGB8888;
 bool amd=a.modifier==UINT64_C(0x020000001046bb04);
 if(!format || (a.modifier!=0 && !amd) || a.n_planes!=(amd?2:1) || a.width!=b->buffer->width || a.height!=b->buffer->height || a.width<=0 || a.height<=0)return false;
 if((uint64_t)a.stride[0]<(uint64_t)a.width*4)return false;
 for(int i=0;i<a.n_planes;i++) {struct stat st;if(!a.stride[i] || a.fd[i]<0 || fstat(a.fd[i],&st))return false;}
 return true; /* Metadata sanity, NEVER modifier decoding/allocation proof. */
}
static void g2_native_object(struct fx_framebuffer *b) {
 fprintf(g2.meta,",\"native\":{\"fx\":\"%"PRIxPTR"\",\"wlr\":\"%"PRIxPTR"\",\"fbo_rbo_tex\":[%u,%u,%u],\"dimensions\":[%d,%d],\"image\":\"%"PRIxPTR"\"}",(uintptr_t)b,(uintptr_t)b->buffer,b->fbo,b->rbo,b->tex,b->buffer->width,b->buffer->height,(uintptr_t)b->image);
 struct wlr_dmabuf_attributes a={0};
 if(!wlr_buffer_get_dmabuf(b->buffer,&a)) {fputs(",\"dmabuf\":null",g2.meta);return;}
 /* Borrowed descriptors: NEVER finish(), close(), duplicate or seek these FDs.
  * fstat exposes descriptor identity, not a trustworthy DCC allocation length. */
 fprintf(g2.meta,",\"dmabuf\":{\"format\":%u,\"modifier\":\"%016"PRIx64"\",\"dimensions\":[%d,%d],\"borrowed\":true,\"allocation_length\":\"NOT_PROVEN\",\"planes\":[",a.format,a.modifier,a.width,a.height);
 if(a.n_planes<1 || a.n_planes>4) {fputs("]}",g2.meta);return;}
 for(int i=0;i<a.n_planes;i++) {struct stat st={0};bool ok=fstat(a.fd[i],&st)==0;
 fprintf(g2.meta,"%s{\"stride\":%u,\"offset\":%u,\"fd\":%d,\"fstat_ok\":%s,\"dev\":%ju,\"ino\":%ju}",i?",":"",a.stride[i],a.offset[i],a.fd[i],ok?"true":"false",(uintmax_t)st.st_dev,(uintmax_t)st.st_ino);}
 fputs("]}",g2.meta);
}
static bool g2_owned(int fd,mode_t mode) {struct stat s;return fstat(fd,&s)==0 && s.st_uid==geteuid() && (s.st_mode&0777)==mode;}
static bool g2_open(void) {
 if(g2.dir>=0)return true;
 const char *d=getenv("MOSAIC_G3_DIR"),*nonce=getenv("MOSAIC_G3_NONCE"); char real[PATH_MAX];
 if(!d || !nonce)return false;
 if(strlen(nonce)!=64 || !realpath(d,real) || strcmp(real,G2_ROOT) || strcmp(d,G2_ROOT)) {g2.stopped=true;return false;}
 for(unsigned i=0;i<64;i++)if(!((nonce[i]>='0'&&nonce[i]<='9')||(nonce[i]>='a'&&nonce[i]<='f'))) {g2.stopped=true;return false;}
 g2.dir=open(d,O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC);
 if(g2.dir<0 || !g2_owned(g2.dir,0700)) {if(g2.dir>=0)close(g2.dir);g2.dir=-1;g2.stopped=true;return false;}
 memcpy(g2.nonce,nonce,65);return true;
}
static void g2_begin(struct fx_gles_render_pass *pass,struct fx_framebuffer *source,struct fx_render_blur_pass_options *options);
static bool g2_expected_source(const struct g2_sample *s,unsigned epoch) {
 if(s->width!=800 || s->height!=600 || !s->pixels)return false;
 const unsigned char a[2][3]={{245,245,245},{15,25,45}};
 const unsigned char b[2][3]={{32,192,224},{176,32,64}};
 for(int y=0;y<600;y++)for(int x=0;x<800;x++) {
  const unsigned char *expected=(epoch==2?b:a)[(x/8)%2];
  if(memcmp(s->pixels+((size_t)y*800+(size_t)x)*4,expected,3))return false;
 }
 return true; /* RGB source admission only; alpha is recorded, never sentinel. */
}
static void g2_sample_native(struct fx_gles_render_pass *pass,struct fx_framebuffer *b,unsigned point,const pixman_region32_t *region) {
 if(!g2.active || g2.pass!=pass)return;
 if(point!=g2.point || point>=10) {g2_fail("STAGE_ORDER_OR_DUPLICATE");return;}
 if(region && pixman_region32_n_rects(region)>256) {g2_fail("REGION_LIMIT");return;}
 if(!g2_dmabuf_supported(b)) {g2_fail("DMABUF_METADATA_UNSUPPORTED");return;}
 struct g2_sample s=g2_read(b->fbo,b->buffer->width,b->buffer->height,g2.used);
 fprintf(g2.meta,"{\"kind\":\"sample\",\"epoch\":%u,\"pass_sequence\":%"PRIuPTR",\"point\":%u,\"stage\":\"%s\",\"context\":\"%"PRIxPTR"\",\"api\":%u,\"client_version\":%d,\"result\":\"%s\",\"bytes\":%zu,\"attachment\":[%d,%d,%d,%d,%d,%d],\"channels\":[%d,%d,%d,%d],\"status\":%u",g2.epoch,g2.pass_sequence,point,g2_names[point],(uintptr_t)s.context,s.api,s.client_version,s.reason,s.bytes,s.object_type,s.object,s.level,s.width,s.height,s.format,s.channels[0],s.channels[1],s.channels[2],s.channels[3],s.status);
 fprintf(g2.meta,",\"read_success\":%s,\"read_buffer\":%d,\"samples\":%d",s.success?"true":"false",s.read_buffer,s.samples);
 fputs(",\"gl_version_hex\":\"",g2.meta);for(size_t i=0;i<strlen(s.version);i++)fprintf(g2.meta,"%02x",(unsigned char)s.version[i]);fputc('"',g2.meta);
 g2_error_json("pre_errors",s.pre);g2_error_json("query_errors",s.query);g2_error_json("read_errors",s.read);g2_error_json("restore_errors",s.restore);
 fprintf(g2.meta,",\"version_queried\":%s,\"state_saved\":%s,\"bound\":%s,\"read_attempted\":%s,\"restore_attempted\":%s",s.version_queried?"true":"false",s.state_saved?"true":"false",s.bound?"true":"false",s.read_attempted?"true":"false",s.restore_attempted?"true":"false");
 if(s.capability_queried)fprintf(g2.meta,",\"gl_major\":%d,\"gl_minor\":%d",s.major,s.minor);else fputs(",\"gl_major\":null,\"gl_minor\":null",g2.meta);
 fputs(",\"glsl_hex\":\"",g2.meta);for(size_t i=0;i<strlen(s.glsl);i++)fprintf(g2.meta,"%02x",(unsigned char)s.glsl[i]);fputc('"',g2.meta);
 g2_error_json("version_errors",s.version_errors);g2_error_json("capability_errors",s.capability);g2_error_json("state_errors",s.state_errors);
 if(s.state_saved)g2_state_json("before",&s.before);else fputs(",\"before\":null",g2.meta);
 if(s.restore_attempted)g2_state_json("after",&s.after);else fputs(",\"after\":null",g2.meta);g2_native_object(b);g2_region(region);
 if(!s.success) {fputs("}\n",g2.meta);free(s.pixels);g2_fail(s.reason);return;}
 char name[64];snprintf(name,sizeof(name),"epoch-%u-point-%u.rgba",g2.epoch,point);
 int fd=openat(g2.dir,name,O_WRONLY|O_CREAT|O_EXCL|O_NOFOLLOW|O_CLOEXEC,0600);
 bool ok=fd>=0 && g2_write(fd,s.pixels,s.bytes) && fsync(fd)==0;
 if(fd>=0 && close(fd))ok=false;
 fprintf(g2.meta,",\"crc32\":\"%08x\",\"file\":\"%s\",\"published\":%s}\n",g2_crc(s.pixels,s.bytes),name,ok?"true":"false");
 g2.used+=s.bytes;
 if(!ok || fflush(g2.meta) || fsync(fileno(g2.meta))) {free(s.pixels);g2_fail("PUBLICATION_FAILED");return;}
 g2.point++;
 if(point==0 && !g2_expected_source(&s,g2.epoch)) {free(s.pixels);g2_fail("SOURCE_PATTERN_NOT_CURRENT_EPOCH");return;}
 free(s.pixels);
 if(point==9) {
  fprintf(g2.meta,"{\"kind\":\"end\",\"epoch\":%u,\"points\":10,\"raw_total\":%zu,\"accepted\":true}\n",g2.epoch,g2.used);
  bool final_ok=fflush(g2.meta)==0 && fsync(fileno(g2.meta))==0;
  if(fclose(g2.meta)) {final_ok=false;}
  g2.meta=NULL;g2.active=false;
  if(!final_ok)g2.stopped=true;
  if(g2.epoch==3)g2.stopped=true;
 }
}
/* Explicit intended-output mapping; bounded eight outputs, no public ABI. */
static struct {const void *pass;bool intended;} g2_outputs[8];
static void g2_forget_output(struct fx_gles_render_pass *pass) {
 for(unsigned i=0;i<8;i++)if(g2_outputs[i].pass==pass) {
  g2_outputs[i].pass=NULL;g2_outputs[i].intended=false;
 }
}
static bool g2_intended_output(struct fx_gles_render_pass *pass) {
 for(unsigned i=0;i<8;i++)if(g2_outputs[i].pass==pass)return g2_outputs[i].intended;
 return false;
}
static void g2_track_output(struct fx_gles_render_pass *pass,struct wlr_output *output) {
 /* A native pass owns its mapping only until submit. Address reuse overwrites
  * prior identity. Overflow never silently associates another output. */
 g2_forget_output(pass);
 for(unsigned i=0;i<8;i++)if(!g2_outputs[i].pass) {
  g2_outputs[i].pass=pass;
  g2_outputs[i].intended=strcmp(output->name,"HEADLESS-1")==0 && output->scale==1.0f && output->transform==WL_OUTPUT_TRANSFORM_NORMAL;
  return;
 }
 g2_fail("TOO_MANY_SIMULTANEOUS_NATIVE_PASSES");
}
static void g2_begin(struct fx_gles_render_pass *pass,struct fx_framebuffer *source,struct fx_render_blur_pass_options *options) {
 if(g2.stopped)return;
 if(g2.active) {if(g2.pass==pass)g2_fail("MULTIPLE_OPTIMIZED_CANDIDATES");return;}
 if(!g2_intended_output(pass) || !g2_open())return;
 unsigned e=g2.epoch+1;if(e>3)return;
 char arm[40],consumed[40],meta[40],expected[80],data[81]={0};
 snprintf(arm,sizeof(arm),"epoch-%u.arm",e);snprintf(consumed,sizeof(consumed),"epoch-%u.consumed",e);
 snprintf(expected,sizeof(expected),"%s %u\n",g2.nonce,e);
 /* WHY: O_NONBLOCK makes non-regular substitutions (especially a FIFO with
  * no writer) fail closed without stalling the compositor callback.
  * CONTRACT: validate identity, permissions, link count and exact bounded
  * framing size before reading or consuming the arm token. */
 int fd=openat(g2.dir,arm,O_RDONLY|O_NONBLOCK|O_NOFOLLOW|O_CLOEXEC);if(fd<0) {if(errno!=ENOENT)g2.stopped=true;return;}
 struct stat st;
 bool ok=fstat(fd,&st)==0 && S_ISREG(st.st_mode) && st.st_uid==geteuid() &&
  (st.st_mode&0777)==0600 && st.st_nlink==1 && st.st_size==(off_t)strlen(expected);
 if(!ok) {close(fd);g2.stopped=true;return;}
 ssize_t n=read(fd,data,sizeof(data)-1);
 if(n!=(ssize_t)strlen(expected) || memcmp(data,expected,(size_t)n)) {close(fd);g2.stopped=true;return;}
 /* Consume BEFORE any query, readback or publication. Existing consumed token
  * is fatal, even if a prior process died or first A was rejected. */
 struct stat linked;
 if(linkat(g2.dir,arm,g2.dir,consumed,0) || fstatat(g2.dir,consumed,&linked,AT_SYMLINK_NOFOLLOW) ||
  !S_ISREG(linked.st_mode) || linked.st_dev!=st.st_dev || linked.st_ino!=st.st_ino || linked.st_nlink!=2 ||
  unlinkat(g2.dir,arm,0) || fsync(g2.dir)) {close(fd);g2.stopped=true;return;}
 close(fd);
 g2.epoch=e;g2.point=0;g2.pass=pass;g2.pass_sequence++;g2.active=true;
 snprintf(meta,sizeof(meta),"epoch-%u.jsonl",e);fd=openat(g2.dir,meta,O_WRONLY|O_CREAT|O_EXCL|O_NOFOLLOW|O_CLOEXEC,0600);
 if(fd<0 || !(g2.meta=fdopen(fd,"w"))) {if(fd>=0)close(fd);g2.stopped=true;g2.active=false;return;}
 fprintf(g2.meta,"{\"kind\":\"begin\",\"schema\":\"G3-followup-v1\",\"epoch\":%u,\"label\":\"%s\",\"nonce\":\"%s\",\"output\":\"HEADLESS-1\",\"pass\":\"%"PRIxPTR"\",\"offscreen_output_key\":\"%"PRIxPTR"\",\"intrusive_error_queue\":true,\"error_queue_restorable\":false,\"readback_may_synchronize\":true,\"rows\":\"GL_LOW_TO_HIGH\",\"present_buffer\":\"NOT_PROVEN\",\"gpu_completion\":\"NOT_PROVEN\",\"lifetime\":\"NOT_PROVEN\"}\n",e,e==1?"A":e==2?"B":"A-return",g2.nonce,(uintptr_t)pass,(uintptr_t)pass->fx_offscreen_buffers);
 if(options->blur_data->num_passes!=3 || options->blur_strength!=1.0f || blur_data_should_parameters_blur_effects(options->blur_data)) {g2_fail("NON_PROSPECTIVE_BLUR_CONFIGURATION");return;}
 g2_sample_native(pass,source,0,options->tex_options.base.clip);
}
/* Executed while the actual blur program and source sampler remain bound. */
static void g2_uniform(struct fx_gles_render_pass *pass,struct blur_shader *shader,struct fx_texture *texture,const pixman_region32_t *region) {
 if(!g2.active || g2.pass!=pass || g2.point<1 || g2.point>6)return;
 if(region && pixman_region32_n_rects(region)>256) {g2_fail("REGION_LIMIT");return;}
 struct g2_errors pre=g2_drain();if(!g2_clean(pre)) {fputs("{\"kind\":\"uniform-errors\"",g2.meta);g2_error_json("pre_errors",pre);fputs("}\n",g2.meta);g2_fail("PRE_UNIFORM_GL_ERROR");return;}
 struct g2_state draw_state;GLboolean color_mask[4]={0};
 g2_state_get(&draw_state);glGetBooleanv(GL_COLOR_WRITEMASK,color_mask);
 GLboolean blend=glIsEnabled(GL_BLEND),stencil=glIsEnabled(GL_STENCIL_TEST);
 GLint program=0,min=0,mag=0,wraps=0,wrapt=0;GLfloat value[2]={0};GLint range[2]={0},precision=0;
 glGetIntegerv(GL_CURRENT_PROGRAM,&program);
 struct g2_errors initial=g2_drain();
 if(!g2_clean(initial)) {fputs("{\"kind\":\"uniform-errors\"",g2.meta);g2_error_json("query_errors",initial);fputs("}\n",g2.meta);g2_fail("UNIFORM_PROGRAM_QUERY_ERROR");return;}
 if(program!=(GLint)shader->program || shader->halfpixel<0 || texture->target!=GL_TEXTURE_2D) {g2_fail("UNIFORM_PROGRAM_OR_TARGET");return;}
 GLint actual=glGetUniformLocation((GLuint)program,"halfpixel");
 initial=g2_drain();
 if(!g2_clean(initial) || actual!=shader->halfpixel) {fputs("{\"kind\":\"uniform-errors\"",g2.meta);g2_error_json("query_errors",initial);fputs("}\n",g2.meta);g2_fail("UNIFORM_LOCATION");return;}
 GLint count=0;glGetProgramiv((GLuint)program,GL_ACTIVE_UNIFORMS,&count);bool typed=false;
 initial=g2_drain();
 if(!g2_clean(initial) || count<0 || count>128) {fputs("{\"kind\":\"uniform-errors\"",g2.meta);g2_error_json("query_errors",initial);fputs("}\n",g2.meta);g2_fail("UNIFORM_COUNT");return;}
 for(GLuint i=0;i<(GLuint)count;i++) {char name[128];GLsizei len=0;GLint size=0;GLenum type=0;glGetActiveUniform((GLuint)program,i,sizeof(name),&len,&size,&type,name);
  if(len==9 && !memcmp(name,"halfpixel",9) && size==1 && type==GL_FLOAT_VEC2)typed=true;
 }
 GLfloat radius=0,proj[9]={0},tex_proj[9]={0};
 glGetUniformfv((GLuint)program,shader->radius,&radius);
 glGetUniformfv((GLuint)program,shader->proj,proj);glGetUniformfv((GLuint)program,shader->tex_proj,tex_proj);
 glGetUniformfv((GLuint)program,actual,value);
 glGetShaderPrecisionFormat(GL_FRAGMENT_SHADER,GL_MEDIUM_FLOAT,range,&precision);
 glGetTexParameteriv(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,&min);glGetTexParameteriv(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,&mag);
 glGetTexParameteriv(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,&wraps);glGetTexParameteriv(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,&wrapt);
 struct g2_errors errors=g2_drain();if(!g2_clean(errors)||!typed) {fputs("{\"kind\":\"uniform-errors\"",g2.meta);g2_error_json("query_errors",errors);fputs("}\n",g2.meta);g2_fail("UNIFORM_QUERY_OR_TYPE");return;}
 uint32_t bits[2];memcpy(bits,value,sizeof(bits));
 fprintf(g2.meta,"{\"kind\":\"uniform\",\"point\":%u,\"program\":%d,\"location\":%d,\"type\":%u,\"actual_bits\":[%u,%u],\"shader_default_float\":\"mediump\",\"varying\":\"mediump\",\"precision_capability\":[%d,%d,%d],\"operation_precision\":\"NOT_PROVEN\",\"sampler\":[%d,%d,%d,%d],\"source_texture\":%u,\"native_texture_dimensions\":[%u,%u],\"gl_level_dimensions\":\"NOT_PROVEN\"",g2.point,program,actual,GL_FLOAT_VEC2,bits[0],bits[1],range[0],range[1],precision,min,mag,wraps,wrapt,texture->tex,texture->wlr_texture.width,texture->wlr_texture.height);
 fprintf(g2.meta,",\"qualifier_basis\":\"FROZEN_LINK_INPUT_SOURCE\",\"shader_source_sha256\":\"%s\"",g2.point<=3?"01664694e4201efb35ec698e89783e220ed930972b5396b86fa842814cd82d4d":"1db325237c9a6c70c2d97518e2f690d448cd006139e9f410cd16e097a1677ad1");
 uint32_t radius_bits,proj_bits[9],tex_proj_bits[9];memcpy(&radius_bits,&radius,4);memcpy(proj_bits,proj,sizeof(proj));memcpy(tex_proj_bits,tex_proj,sizeof(tex_proj));
 fprintf(g2.meta,",\"other_uniforms\":{\"radius_location\":%d,\"radius_bits\":%u,\"proj_location\":%d,\"proj_bits\":[",shader->radius,radius_bits,shader->proj);
 for(unsigned i=0;i<9;i++)fprintf(g2.meta,"%s%u",i?",":"",proj_bits[i]);
 fprintf(g2.meta,"],\"tex_proj_location\":%d,\"tex_proj_bits\":[",shader->tex_proj);
 for(unsigned i=0;i<9;i++)fprintf(g2.meta,"%s%u",i?",":"",tex_proj_bits[i]);
 fputs("]}",g2.meta);g2_state_json("draw_state",&draw_state);
 fprintf(g2.meta,",\"blend_stencil\":[%u,%u],\"color_mask\":[%u,%u,%u,%u]",blend,stencil,color_mask[0],color_mask[1],color_mask[2],color_mask[3]);
 g2_region(region);fputs("}\n",g2.meta);
}
#endif
