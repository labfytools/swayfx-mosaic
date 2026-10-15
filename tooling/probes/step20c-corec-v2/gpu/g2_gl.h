/* G2 new source-only intrusive diagnostic. No production API. */
#ifndef G2_GL_H
#define G2_GL_H
#include <EGL/egl.h>
#include <GLES3/gl3.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#define G2_CAP (256u * 1024u * 1024u)
#define G2_ERRORS 16
struct g2_errors { GLenum values[G2_ERRORS]; unsigned count; bool exhausted; };
struct g2_state {
 GLint read_fbo, draw_fbo, rbo, pack, pbo, row, skip_rows, skip_pixels;
 GLint viewport[4], scissor[4], program, active, texture;
 GLboolean scissor_on;
};
struct g2_sample {
 EGLContext context; EGLint client_version; EGLenum api;
 char version[160]; struct g2_state before, after;
 struct g2_errors pre, query, read, restore;
 GLint object_type, object, level, width, height, format, channels[4];
 GLint read_buffer, samples; GLenum status; size_t bytes; unsigned char *pixels;
 bool success; const char *reason;
};
static struct g2_errors g2_drain(void) {
 struct g2_errors e = {0};
 for (unsigned i=0;i<G2_ERRORS;i++) {
  GLenum v=glGetError(); if (v==GL_NO_ERROR) return e;
  e.values[e.count++]=v;
 }
 /* No unbounded probing: sixteen errors means attribution rejected. */
 e.exhausted=true; return e;
}
static bool g2_clean(struct g2_errors e) { return !e.count && !e.exhausted; }
static bool g2_size(int w,int h,size_t used,size_t *n) {
 if(w<=0 || h<=0 || used>G2_CAP || (size_t)w>SIZE_MAX/4/(size_t)h) return false;
 *n=(size_t)w*(size_t)h*4; return *n<=G2_CAP-used;
}
static void g2_state_get(struct g2_state *s) {
 memset(s,0,sizeof(*s));
 glGetIntegerv(GL_READ_FRAMEBUFFER_BINDING,&s->read_fbo);
 glGetIntegerv(GL_DRAW_FRAMEBUFFER_BINDING,&s->draw_fbo);
 glGetIntegerv(GL_RENDERBUFFER_BINDING,&s->rbo);
 glGetIntegerv(GL_PACK_ALIGNMENT,&s->pack);
 glGetIntegerv(GL_PIXEL_PACK_BUFFER_BINDING,&s->pbo);
 glGetIntegerv(GL_PACK_ROW_LENGTH,&s->row);
 glGetIntegerv(GL_PACK_SKIP_ROWS,&s->skip_rows);
 glGetIntegerv(GL_PACK_SKIP_PIXELS,&s->skip_pixels);
 glGetIntegerv(GL_VIEWPORT,s->viewport); glGetIntegerv(GL_SCISSOR_BOX,s->scissor);
 s->scissor_on=glIsEnabled(GL_SCISSOR_TEST);
 glGetIntegerv(GL_CURRENT_PROGRAM,&s->program);
 glGetIntegerv(GL_ACTIVE_TEXTURE,&s->active);
 glGetIntegerv(GL_TEXTURE_BINDING_2D,&s->texture);
}
static void g2_state_restore(const struct g2_state *s) {
 glBindFramebuffer(GL_READ_FRAMEBUFFER,(GLuint)s->read_fbo);
 glBindFramebuffer(GL_DRAW_FRAMEBUFFER,(GLuint)s->draw_fbo);
 glBindRenderbuffer(GL_RENDERBUFFER,(GLuint)s->rbo);
 glBindBuffer(GL_PIXEL_PACK_BUFFER,(GLuint)s->pbo);
 glPixelStorei(GL_PACK_ALIGNMENT,s->pack);
 glPixelStorei(GL_PACK_ROW_LENGTH,s->row);
 glPixelStorei(GL_PACK_SKIP_ROWS,s->skip_rows);
 glPixelStorei(GL_PACK_SKIP_PIXELS,s->skip_pixels);
}
/* Called with the actual current native target. ES2 is explicitly unsupported:
 * no ES3-only enum is ever queried before both EGL and GL attest ES3.
 * Only native RBO color attachments are accepted. Texture attachments retain
 * type/name/level, but safe dimensions on this pinned API are NOT_PROVEN.
 * Error queue consumption and synchronous readback cannot be restored. */
static struct g2_sample g2_read(GLuint fbo,int width,int height,size_t used) {
 struct g2_sample s={.reason="NOT_PROVEN"}; bool saved=false, changed=false;
 s.context=eglGetCurrentContext(); s.api=eglQueryAPI();
 if(s.context==EGL_NO_CONTEXT || s.api!=EGL_OPENGL_ES_API) {s.reason="UNKNOWN_CONTEXT"; return s;}
 if(!eglQueryContext(eglGetCurrentDisplay(),s.context,EGL_CONTEXT_CLIENT_VERSION,&s.client_version)) {
  s.reason="EGL_QUERY_FAILED"; return s;
 }
 s.pre=g2_drain(); if(!g2_clean(s.pre)) {s.reason="PREEXISTING_GL_ERRORS"; return s;}
 const char *v=(const char *)glGetString(GL_VERSION);
 if(v) snprintf(s.version,sizeof(s.version),"%s",v);
 s.query=g2_drain(); if(!g2_clean(s.query)) {s.reason="VERSION_QUERY_ERROR"; return s;}
 if(s.client_version<3 || !v || strncmp(v,"OpenGL ES 3.",12)!=0) {
  s.reason="GLES_STATE_NOT_SUPPORTED"; return s;
 }
 if(!g2_size(width,height,used,&s.bytes)) {s.reason="RAW_BUDGET_OR_OVERFLOW"; return s;}
 g2_state_get(&s.before); s.query=g2_drain();
 if(!g2_clean(s.query)) {s.reason="STATE_QUERY_ERROR"; return s;}
 saved=true; changed=true;
 glBindFramebuffer(GL_READ_FRAMEBUFFER,fbo);
 glGetFramebufferAttachmentParameteriv(GL_READ_FRAMEBUFFER,GL_COLOR_ATTACHMENT0,
  GL_FRAMEBUFFER_ATTACHMENT_OBJECT_TYPE,&s.object_type);
 glGetFramebufferAttachmentParameteriv(GL_READ_FRAMEBUFFER,GL_COLOR_ATTACHMENT0,
  GL_FRAMEBUFFER_ATTACHMENT_OBJECT_NAME,&s.object);
 if(s.object_type==GL_RENDERBUFFER && s.object>0) {
  glBindRenderbuffer(GL_RENDERBUFFER,(GLuint)s.object);
  glGetRenderbufferParameteriv(GL_RENDERBUFFER,GL_RENDERBUFFER_WIDTH,&s.width);
  glGetRenderbufferParameteriv(GL_RENDERBUFFER,GL_RENDERBUFFER_HEIGHT,&s.height);
  glGetRenderbufferParameteriv(GL_RENDERBUFFER,GL_RENDERBUFFER_INTERNAL_FORMAT,&s.format);
  glGetRenderbufferParameteriv(GL_RENDERBUFFER,GL_RENDERBUFFER_SAMPLES,&s.samples);
  const GLenum c[4]={GL_RENDERBUFFER_RED_SIZE,GL_RENDERBUFFER_GREEN_SIZE,GL_RENDERBUFFER_BLUE_SIZE,GL_RENDERBUFFER_ALPHA_SIZE};
  for(int i=0;i<4;i++) glGetRenderbufferParameteriv(GL_RENDERBUFFER,c[i],&s.channels[i]);
 } else if(s.object_type==GL_TEXTURE) {
  glGetFramebufferAttachmentParameteriv(GL_READ_FRAMEBUFFER,GL_COLOR_ATTACHMENT0,
   GL_FRAMEBUFFER_ATTACHMENT_TEXTURE_LEVEL,&s.level);
 }
 glGetIntegerv(GL_READ_BUFFER,&s.read_buffer);
 s.status=glCheckFramebufferStatus(GL_READ_FRAMEBUFFER);
 s.query=g2_drain();
 if(!g2_clean(s.query)) {s.reason="ATTACHMENT_QUERY_ERROR"; goto done;}
 if(s.object_type!=GL_RENDERBUFFER) {s.reason="TEXTURE_ATTACHMENT_DIMENSIONS_NOT_PROVEN"; goto done;}
 if(s.read_buffer!=GL_COLOR_ATTACHMENT0 || s.samples!=0 || s.status!=GL_FRAMEBUFFER_COMPLETE || s.width!=width || s.height!=height ||
  s.channels[0]!=8 || s.channels[1]!=8 || s.channels[2]!=8 || (s.channels[3]!=0 && s.channels[3]!=8)) {
  s.reason="ATTACHMENT_UNSUPPORTED"; goto done;
 }
 glBindBuffer(GL_PIXEL_PACK_BUFFER,0); glPixelStorei(GL_PACK_ALIGNMENT,1);
 glPixelStorei(GL_PACK_ROW_LENGTH,0); glPixelStorei(GL_PACK_SKIP_ROWS,0); glPixelStorei(GL_PACK_SKIP_PIXELS,0);
 s.query=g2_drain(); if(!g2_clean(s.query)) {s.reason="PACK_QUERY_ERROR"; goto done;}
 s.pixels=malloc(s.bytes); if(!s.pixels) {s.reason="ALLOCATION_FAILED"; goto done;}
 /* glReadPixels returns void. NO alpha sentinel or file hash success gate. */
 glReadPixels(0,0,width,height,GL_RGBA,GL_UNSIGNED_BYTE,s.pixels);
 s.read=g2_drain();
 if(!g2_clean(s.read)) {s.reason="READ_GL_ERROR"; goto done;}
 s.success=true; s.reason="READ_SUCCESS";
 done:
 if(saved && changed) {
  g2_state_restore(&s.before); g2_state_get(&s.after); s.restore=g2_drain();
  if(!g2_clean(s.restore) || memcmp(&s.before,&s.after,sizeof(s.before)) || eglGetCurrentContext()!=s.context) {
   s.success=false; s.reason="RESTORE_FAILED";
  }
 }
 return s;
}
#endif
