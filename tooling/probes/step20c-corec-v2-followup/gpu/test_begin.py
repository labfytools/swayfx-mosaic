"""Compile the exact native arm consumer against bounded filesystem fixtures."""
import ctypes
import os
from pathlib import Path
import resource
import subprocess
import tempfile

resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
assert ctypes.CDLL(None).prctl(4, 0, 0, 0, 0) == 0
KIT = Path(__file__).resolve().parent
header = (KIT/'g2_native.h').read_text()
marker = 'static void g2_begin(struct fx_gles_render_pass *pass,struct fx_framebuffer *source,struct fx_render_blur_pass_options *options) {'
start = header.index(marker)
end = header.index('\n}\n',start)+3
body = header[start:end]
prefix = r'''
#define _GNU_SOURCE
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <inttypes.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/resource.h>
#include <sys/prctl.h>
#include <errno.h>
struct fx_gles_render_pass {void *fx_offscreen_buffers;};
struct fx_framebuffer {int unused;};
struct bd {int num_passes;};
struct fx_render_blur_pass_options {struct bd *blur_data;float blur_strength;struct {struct {void *clip;}base;}tex_options;};
static struct {bool stopped,active;unsigned epoch,point;size_t used;int dir;FILE *meta;const void *pass;uintptr_t pass_sequence;char nonce[65];}g2;
static bool g2_intended_output(void *p){(void)p;return true;}
static bool g2_open(void){return true;}
static void g2_fail(const char *s){(void)s;g2.stopped=true;}
static bool blur_data_should_parameters_blur_effects(void *p){(void)p;return false;}
static void g2_sample_native(void *p,void *b,unsigned x,void *r){(void)p;(void)b;(void)x;(void)r;}
'''
suffix = r'''
int main(int argc,char **argv) {
 (void)argc;struct rlimit r={0,0};assert(!setrlimit(RLIMIT_CORE,&r));assert(!prctl(PR_SET_DUMPABLE,0));
 g2.dir=open(argv[1],O_RDONLY|O_DIRECTORY|O_NOFOLLOW);assert(g2.dir>=0);memset(g2.nonce,'a',64);
 struct fx_gles_render_pass pass={0};struct bd bd={.num_passes=3};
 struct fx_render_blur_pass_options options={.blur_data=&bd,.blur_strength=1};
 g2_begin(&pass,NULL,&options);
 if(!strcmp(argv[2],"accept")){assert(g2.active&&!g2.stopped&&g2.epoch==1);assert(!fclose(g2.meta));}
 else assert(g2.stopped&&!g2.active&&g2.epoch==0);
 assert(!close(g2.dir));return 0;
}
'''
with tempfile.TemporaryDirectory(prefix='g3-begin-',dir=os.environ['TMPDIR']) as name:
    work=Path(name);work.chmod(0o700)
    source=work/'begin.c';source.write_text(prefix+body+suffix)
    binary=work/'begin'
    subprocess.run(['cc','-std=c17','-Wall','-Wextra','-Werror',str(source),'-o',str(binary)],check=True)
    for case in ('fifo','symlink','wrong-mode','hardlink','oversize','consumed','accept'):
        d=work/case;d.mkdir(mode=0o700);arm=d/'epoch-1.arm'
        if case=='fifo':os.mkfifo(arm,0o600)
        elif case=='symlink':arm.symlink_to('/dev/null')
        else:
            arm.write_bytes(b'a'*64+b' 1\n');arm.chmod(0o600)
            if case=='wrong-mode':arm.chmod(0o644)
            if case=='hardlink':os.link(arm,d/'alias')
            if case=='oversize':arm.write_bytes(b'a'*1000)
            if case=='consumed':(d/'epoch-1.consumed').write_bytes(b'old')
        subprocess.run([str(binary),str(d),case],check=True,timeout=3)
        if case=='accept':assert not arm.exists() and (d/'epoch-1.consumed').exists()
        else:assert arm.exists() or arm.is_symlink()
        print('PASS exact native g2_begin',case)
