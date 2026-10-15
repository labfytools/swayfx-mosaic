"""Wrong native variants must fail the unchanged exact-body FakeGL tests."""
import ctypes
import os
from pathlib import Path
import resource
import shutil
import subprocess
import tempfile

resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
assert ctypes.CDLL(None).prctl(4, 0, 0, 0, 0) == 0
KIT=Path(__file__).resolve().parent
header=(KIT/'g2_gl.h').read_text()
variants={
    'major-contradiction':('s.major!=3 || s.minor!=parsed_minor','s.minor!=parsed_minor'),
    'minor-contradiction':('s.major!=3 || s.minor!=parsed_minor','s.major!=3'),
    'false-read-lifecycle':('s.read_attempted=true;','s.read_attempted=false;'),
    'missing-pack-restore':('glPixelStorei(GL_PACK_ALIGNMENT,s->pack);','/* deliberately broken restore */'),
}
with tempfile.TemporaryDirectory(prefix='g3-mutants-',dir=os.environ['TMPDIR']) as name:
    work=Path(name)
    shutil.copyfile(KIT/'test_gl.c',work/'test_gl.c')
    for label,(old,new) in variants.items():
        assert header.count(old)==1
        (work/'g2_gl.h').write_text(header.replace(old,new))
        binary=work/label
        subprocess.run(['cc','-std=c17','-Wall','-Wextra','-Werror','-I'+str(work),str(work/'test_gl.c'),'-o',str(binary)],check=True)
        result=subprocess.run([str(binary)],capture_output=True,text=True,timeout=5)
        assert result.returncode != 0, label
        print(f'PASS wrong native variant rejected {label}: raw_exit={result.returncode}')
