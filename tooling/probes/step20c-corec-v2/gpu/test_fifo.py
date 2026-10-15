"""Compile the exact production g2_begin body into the reviewed stub harness."""
import ctypes,json,os,resource,subprocess,tempfile
from pathlib import Path
ROOT=Path('/var/tmp/swayfx-mosaic-corec-v2-i516p6po');KIT=Path(__file__).resolve().parent
WORK=ROOT/'gpu-fifo-fix/work';WORK.mkdir(parents=True,exist_ok=True)
resource.setrlimit(resource.RLIMIT_CORE,(0,0));assert ctypes.CDLL(None).prctl(4,0,0,0,0)==0
header=(ROOT/'sources/scene-gpu/render/fx_renderer/g2_native.h').read_text()
marker='static void g2_begin(struct fx_gles_render_pass *pass,struct fx_framebuffer *source,struct fx_render_blur_pass_options *options) {'
start=header.index(marker);brace=header.index('{',start);depth=0;end=None
for i in range(brace,len(header)):
 if header[i]=='{':depth+=1
 elif header[i]=='}':
  depth-=1
  if depth==0:end=i+1;break
assert end is not None
body=header[start:end]
fixture=(ROOT/'ownreview-gpu-oom-build/fifo-exact-g2-begin.c').read_text()
fstart=fixture.index(marker);fbrace=fixture.index('{',fstart);depth=0;fend=None
for i in range(fbrace,len(fixture)):
 if fixture[i]=='{':depth+=1
 elif fixture[i]=='}':
  depth-=1
  if depth==0:fend=i+1;break
assert fend is not None
fixture=fixture[:fstart]+body+fixture[fend:]
fixture=fixture.replace('static void g2_fail(const char *s){(void)s;}','static void g2_fail(const char *s){(void)s;g2.stopped=true;}')
source=WORK/'fifo-exact-g2-begin-corrected.c';source.write_text(fixture)
binary=WORK/'fifo-exact-g2-begin-corrected'
cmd=['cc','-std=c17','-Wall','-Wextra','-Werror','-Wno-unused-parameter','-Wno-unused-function',str(source),'-o',str(binary)]
p=subprocess.run(cmd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);print(p.stdout,end='');assert p.returncode==0
with tempfile.TemporaryDirectory(prefix='fifo-g2-begin-',dir=WORK) as d:
 os.chmod(d,0o700);fifo=Path(d)/'epoch-1.arm';os.mkfifo(fifo,0o600)
 r=subprocess.run([str(binary),d],timeout=3,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 print(r.stdout,end='');assert r.returncode==0, r.returncode
 assert fifo.exists() and not (Path(d)/'epoch-1.consumed').exists()
 print('PASS exact extracted production g2_begin rejects writerless FIFO promptly before read/consume')
