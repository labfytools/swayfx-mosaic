"""OFFLINE_ONLY: compile/exercise the actual SHM path guard, never Wayland."""
import os,subprocess,tempfile,unittest
from pathlib import Path

class TmpdirGuard(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.work=Path(tempfile.mkdtemp(prefix='g3-path-',dir=os.environ['TMPDIR']))
  source=(Path(__file__).parent/'clients-g2.c').read_text()
  begin=source.index('/* BEGIN G3_SHM_PATH_HELPER');end=source.index('/* END G3_SHM_PATH_HELPER */',begin)
  helper=source[begin:end]
  cls.executable=cls.work/'guard'
  harness=cls.work/'guard.c'
  harness.write_text('''#define _GNU_SOURCE
#include <errno.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/resource.h>
#include <sys/prctl.h>
#include <unistd.h>
'''+helper+'''
int main(int argc,char **argv) {
 struct rlimit limit={0,0};
 if(setrlimit(RLIMIT_CORE,&limit)||prctl(PR_SET_DUMPABLE,0,0,0,0))return 3;
 if(argc==3 && !strcmp(argv[1],"directory"))return g3_private_directory(argv[2])?2:0;
 char path[512];size_t cap=argc==2?(size_t)strtoul(argv[1],NULL,10):sizeof(path);
 if(cap>sizeof(path))return 3;
 if(g3_shm_path(path,cap))return 2;
 puts(path);return 0;
}
''')
  cls.compile_argv=['cc','-std=c17','-O2','-Wall','-Wextra','-Werror',str(harness),'-o',str(cls.executable)]
  subprocess.run(cls.compile_argv,check=True,capture_output=True)
 def call(self,env=None,*args):
  e=dict(os.environ,SMX_LAB=os.environ['SMX_LAB'],TMPDIR=os.environ['SMX_LAB']+'/scratch')
  for k,v in (env or {}).items():
   if v is None:e.pop(k,None)
   else:e[k]=v
  return subprocess.run([str(self.executable),*args],env=e,capture_output=True,text=True)
 def refuse(self,env=None,*args):
  p=self.call(env,*args);self.assertEqual(p.returncode,2,p.stdout+p.stderr)
  self.assertIn('G3_SHM_PATH_REJECT reason=',p.stderr);return p
 def test_new_LAB_exact_template(self):
  p=self.call();self.assertEqual(p.returncode,0,p.stderr)
  self.assertEqual(p.stdout,os.environ['SMX_LAB']+'/scratch/g2-shm-XXXXXX\n')
 def test_missing_old_outside_prefix_and_noncanonical(self):
  for env in ({'SMX_LAB':None},{'TMPDIR':None},
              {'SMX_LAB':'/var/tmp/swayfx-mosaic-corec-v2-i516p6po','TMPDIR':'/var/tmp/swayfx-mosaic-corec-v2-i516p6po/scratch'},
              {'SMX_LAB':'/tmp/swayfx-mosaic-step20c-native-closure-test'},
              {'SMX_LAB':os.environ['SMX_LAB']+'/../child'},
              {'TMPDIR':str(self.work)},
              {'TMPDIR':os.environ['SMX_LAB']+'/scratch/'},
              {'SMX_LAB':'/var/tmp/swayfx-mosaic-step20c-native-closure-'}):
   self.refuse(env)
 def test_overflow_environment_and_output(self):
  for env in ({'SMX_LAB':'/var/tmp/swayfx-mosaic-step20c-native-closure-'+'x'*512},{'TMPDIR':'x'*512}):
   self.assertIn('environment_path_overflow',self.refuse(env).stderr)
  self.assertIn('SHM_template_overflow',self.refuse(None,'16').stderr)
 def test_real_directory_mode_symlink_and_owner(self):
  directory=Path(tempfile.mkdtemp(dir=self.work));directory.chmod(0o700)
  self.assertEqual(self.call(None,'directory',str(directory)).returncode,0)
  directory.chmod(0o755);self.refuse(None,'directory',str(directory));directory.chmod(0o700)
  alias=self.work/'alias';alias.symlink_to(directory);self.refuse(None,'directory',str(alias))
  self.refuse(None,'directory',str(directory)+'/../'+directory.name)
  if os.stat('/root').st_uid!=os.getuid():self.refuse(None,'directory','/root')
  else:self.skipTest('no accessible foreign-owned 0700 directory')

if __name__=='__main__':unittest.main(verbosity=2)
