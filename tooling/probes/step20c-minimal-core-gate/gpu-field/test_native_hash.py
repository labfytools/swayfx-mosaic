"""Compile exact private SHA helper bytes for a CPU-only hash unit check.
No compositor, GL context, client or diagnostic source-pair build is launched.
"""
import hashlib,json,subprocess,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
header=(HERE/'scene/render/fx_renderer/gpu_field_private.h').read_text()
start=header.index('static uint32_t gf_rot');end=header.index('static void gf_log')
code=header[start:end]
with tempfile.TemporaryDirectory(prefix='g1-cpu-hash-') as tmp:
    p=Path(tmp);source=p/'sha.c';binary=p/'sha'
    source.write_text('#include <stdint.h>\n#include <stddef.h>\n#include <stdio.h>\n'+code+'\nint main(void){unsigned char data[10000];size_t n=fread(data,1,sizeof(data),stdin);char h[65];gf_sha(data,n,h);puts(h);return 0;}\n')
    c=subprocess.run(['cc','-std=c17','-Wall','-Wextra','-Werror',str(source),'-o',str(binary)],capture_output=True,text=True)
    if c.returncode:raise RuntimeError(c.stderr)
    lengths=[0,3,55,56,63,64,65,127,128,10000]
    for n in lengths:
        data=bytes((i*37)%256 for i in range(n))
        r=subprocess.run([str(binary)],input=data,capture_output=True)
        assert r.returncode==0 and r.stdout.decode().strip()==hashlib.sha256(data).hexdigest(),n
print(json.dumps(dict(status='PASS_CPU_ONLY',cases=len(lengths),exact_helper_sha256=hashlib.sha256(code.encode()).hexdigest(),graphical_launches=0,source_pair_builds=0)))
