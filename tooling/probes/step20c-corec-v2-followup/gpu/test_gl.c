#define _GNU_SOURCE
#include "g2_gl.h"
#include <assert.h>
#include <limits.h>
#include <sys/resource.h>
#include <sys/prctl.h>
static struct g2_state state;
static int mode, read_calls, unsupported, pending, query_count;
static bool read_done;
static const char *version="OpenGL ES 3.2 FakeGL";
static void reset(int m) {
 memset(&state,0,sizeof(state));state.read_fbo=11;state.draw_fbo=12;state.rbo=13;
 state.pack=8;state.pbo=15;state.row=32;state.skip_rows=2;state.skip_pixels=3;
 state.viewport[2]=2;state.viewport[3]=3;state.scissor[2]=2;state.scissor[3]=3;
 state.program=21;state.active=GL_TEXTURE0;state.texture=22;
 mode=m;read_calls=unsupported=pending=query_count=0;read_done=false;
 version=(m==6||m==14)?"OpenGL ES 2.0 FakeGL":m==20?"OpenGL ES 3.20 FakeGL":m==21?"OpenGL ES 3.3 FakeGL":m==22?"OpenGL 3.2":m==23?"OpenGL ES 4.0":"OpenGL ES 3.2 FakeGL";
}
EGLContext EGLAPIENTRY eglGetCurrentContext(void) {return mode==5?EGL_NO_CONTEXT:(EGLContext)(uintptr_t)(mode==17&&read_done?7:5);}
EGLDisplay EGLAPIENTRY eglGetCurrentDisplay(void) {return mode==24?EGL_NO_DISPLAY:(EGLDisplay)(uintptr_t)6;}
EGLenum EGLAPIENTRY eglQueryAPI(void) {return mode==12?EGL_OPENGL_API:EGL_OPENGL_ES_API;}
EGLBoolean EGLAPIENTRY eglQueryContext(EGLDisplay d,EGLContext c,EGLint a,EGLint *v) {(void)d;(void)c;(void)a;*v=(mode==6||mode==18)?2:3;return mode==13?EGL_FALSE:EGL_TRUE;}
GLenum GL_APIENTRY glGetError(void) {
 if(mode==1 && query_count==0) {query_count++;return GL_INVALID_OPERATION;}
 if(mode==8)return GL_INVALID_OPERATION;
 if(pending){GLenum e=(GLenum)pending;pending=0;return e;}return GL_NO_ERROR;
}
const GLubyte *GL_APIENTRY glGetString(GLenum e) {if(mode==25)pending=GL_INVALID_ENUM;return (const GLubyte *)(e==GL_SHADING_LANGUAGE_VERSION?"OpenGL ES GLSL ES 3.20 FakeGL":version);}
void GL_APIENTRY glGetIntegerv(GLenum e,GLint *v) {
 if(mode==6)unsupported++;
 if(mode==2 && e==GL_READ_FRAMEBUFFER_BINDING)pending=GL_INVALID_ENUM;
 switch(e) {
 case GL_MAJOR_VERSION:*v=mode==19?2:3;if(mode==26)pending=GL_INVALID_ENUM;break;
 case GL_MINOR_VERSION:*v=mode==27?1:2;break;
 #define FIELD(e,f) case e:*v=state.f;break
 case GL_READ_BUFFER:*v=mode==16?GL_NONE:GL_COLOR_ATTACHMENT0;break;
 FIELD(GL_READ_FRAMEBUFFER_BINDING,read_fbo);FIELD(GL_DRAW_FRAMEBUFFER_BINDING,draw_fbo);
 FIELD(GL_RENDERBUFFER_BINDING,rbo);FIELD(GL_PACK_ALIGNMENT,pack);FIELD(GL_PIXEL_PACK_BUFFER_BINDING,pbo);
 FIELD(GL_PACK_ROW_LENGTH,row);FIELD(GL_PACK_SKIP_ROWS,skip_rows);FIELD(GL_PACK_SKIP_PIXELS,skip_pixels);
 FIELD(GL_CURRENT_PROGRAM,program);FIELD(GL_ACTIVE_TEXTURE,active);FIELD(GL_TEXTURE_BINDING_2D,texture);
 case GL_VIEWPORT:memcpy(v,state.viewport,sizeof(state.viewport));break;
 case GL_SCISSOR_BOX:memcpy(v,state.scissor,sizeof(state.scissor));break;
 default:unsupported++;pending=GL_INVALID_ENUM;break;
 }
}
GLboolean GL_APIENTRY glIsEnabled(GLenum e) {(void)e;return state.scissor_on;}
void GL_APIENTRY glBindFramebuffer(GLenum e,GLuint v) {if(e==GL_READ_FRAMEBUFFER)state.read_fbo=(GLint)v;else state.draw_fbo=(GLint)v;}
void GL_APIENTRY glBindRenderbuffer(GLenum e,GLuint v) {(void)e;state.rbo=(GLint)v;}
void GL_APIENTRY glBindBuffer(GLenum e,GLuint v) {(void)e;if(mode==11&&read_done&&v==15)pending=GL_INVALID_OPERATION;if(!(mode==4&&read_done))state.pbo=(GLint)v;}
void GL_APIENTRY glPixelStorei(GLenum e,GLint v) {
 if(mode==9&&e==GL_PACK_ALIGNMENT&&v==1)pending=GL_INVALID_OPERATION;
 switch(e) {case GL_PACK_ALIGNMENT:state.pack=v;break;case GL_PACK_ROW_LENGTH:state.row=v;break;
 case GL_PACK_SKIP_ROWS:state.skip_rows=v;break;case GL_PACK_SKIP_PIXELS:state.skip_pixels=v;break;default:unsupported++;}
}
void GL_APIENTRY glGetFramebufferAttachmentParameteriv(GLenum t,GLenum a,GLenum e,GLint *v) {
 (void)t;(void)a;if(mode==10)pending=GL_INVALID_ENUM;*v=e==GL_FRAMEBUFFER_ATTACHMENT_OBJECT_TYPE?(mode==7?GL_TEXTURE:GL_RENDERBUFFER):e==GL_FRAMEBUFFER_ATTACHMENT_OBJECT_NAME?44:0;
}
void GL_APIENTRY glGetRenderbufferParameteriv(GLenum t,GLenum e,GLint *v) {
 (void)t;*v=e==GL_RENDERBUFFER_WIDTH?2:e==GL_RENDERBUFFER_HEIGHT?3:e==GL_RENDERBUFFER_INTERNAL_FORMAT?GL_RGBA8:e==GL_RENDERBUFFER_SAMPLES?(mode==15?4:0):8;
}
GLenum GL_APIENTRY glCheckFramebufferStatus(GLenum e) {(void)e;return mode==28?GL_FRAMEBUFFER_INCOMPLETE_ATTACHMENT:GL_FRAMEBUFFER_COMPLETE;}
void GL_APIENTRY glReadPixels(GLint x,GLint y,GLsizei w,GLsizei h,GLenum f,GLenum t,void *p) {
 (void)x;(void)y;assert(f==GL_RGBA&&t==GL_UNSIGNED_BYTE);assert(state.pbo==0&&state.pack==1&&state.row==0);
 read_calls++;read_done=true;if(mode==3)pending=GL_INVALID_OPERATION;else memset(p,0,(size_t)w*(size_t)h*4);
}
int main(void) {
 struct rlimit r={0,0};assert(!setrlimit(RLIMIT_CORE,&r));assert(!prctl(PR_SET_DUMPABLE,0));
 const char *reasons[]={"READ_SUCCESS","PREEXISTING_GL_ERRORS","STATE_QUERY_ERROR","READ_GL_ERROR","RESTORE_FAILED","UNKNOWN_CONTEXT","GLES_STATE_NOT_SUPPORTED","TEXTURE_ATTACHMENT_DIMENSIONS_NOT_PROVEN","PREEXISTING_GL_ERRORS","PACK_QUERY_ERROR","ATTACHMENT_QUERY_ERROR","RESTORE_FAILED","UNKNOWN_CONTEXT","EGL_QUERY_FAILED","GLES_STATE_NOT_SUPPORTED","ATTACHMENT_UNSUPPORTED","ATTACHMENT_UNSUPPORTED","RESTORE_FAILED","READ_SUCCESS","VERSION_INCONSISTENT","GLES_STATE_NOT_SUPPORTED","GLES_STATE_NOT_SUPPORTED","GLES_STATE_NOT_SUPPORTED","GLES_STATE_NOT_SUPPORTED","UNKNOWN_CONTEXT","VERSION_QUERY_ERROR","CAPABILITY_QUERY_ERROR","VERSION_INCONSISTENT","ATTACHMENT_UNSUPPORTED"};
 for(int i=0;i<29;i++) {
  reset(i);struct g2_state before=state;struct g2_sample s=g2_read(99,2,3,0);
  assert(s.success==(i==0||i==18));assert(!strcmp(s.reason,reasons[i]));assert(!unsupported);
  if(i==0||i==3||i==7)assert(!memcmp(&state,&before,sizeof(state)));
  if(i==0||i==18){assert(s.version_queried&&s.state_saved&&s.bound&&s.read_attempted&&s.restore_attempted);assert(read_calls==1&&s.bytes==24);for(size_t n=0;n<s.bytes;n++)assert(s.pixels[n]==0);}
  if(i==1||i==2||i==5||i==6||i==7||i==8||i==9||i==10||i==12||i==13||i==14||i==15||i==16)assert(!read_calls);
  if(i==8)assert(s.pre.exhausted&&s.pre.count==G2_ERRORS);
  if(!s.state_saved)assert(!s.bound&&!s.read_attempted&&!s.restore_attempted);
  if(i>=19)assert(!read_calls);
  printf("PASS exact g2_read mode=%d reason=%s\n",i,s.reason);free(s.pixels);
 }
 GLint minor=0;char too_long[170];memset(too_long,'x',sizeof(too_long));memcpy(too_long,"OpenGL ES 3.2 ",14);too_long[169]=0;
 assert(!g2_version(NULL,&minor));assert(!g2_version(too_long,&minor));assert(!g2_version("OpenGL ES 3.2\nforged",&minor));
 assert(g2_version("OpenGL ES 3.0",&minor)&&minor==0);assert(g2_version("OpenGL ES 3.1 vendor",&minor)&&minor==1);
 size_t n=0;assert(!g2_size(INT_MAX,INT_MAX,0,&n));assert(!g2_size(2,3,G2_CAP-23,&n));assert(!g2_size(-1,3,0,&n));
 assert(g2_size(2,3,G2_CAP-24,&n)&&n==24);
 reset(0);struct g2_sample s=g2_read(99,INT_MAX,INT_MAX,0);assert(!s.success&&!read_calls);free(s.pixels);
 puts("PASS size/overflow/exact-cap; black RGBA alpha zero is valid, no sentinel gate");return 0;
}
