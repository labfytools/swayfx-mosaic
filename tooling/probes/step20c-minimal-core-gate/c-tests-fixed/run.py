#!/usr/bin/env python3
"""WHY: retain exact commands, raw stdout/stderr and unmodified exit codes.
CONTRACT: only local C compilation/execution; no compositor, network or injection.
INVARIANT: sanitizer diagnostics are enabled and failing reproductions are not PASS.
"""
from pathlib import Path
import hashlib,json,subprocess,os
HERE=Path(__file__).resolve().parent
LAB=HERE.parent
records=[]
def run(name,argv):
    result=subprocess.run(argv,cwd=HERE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    (HERE/(name+'.stdout')).write_bytes(result.stdout)
    (HERE/(name+'.stderr')).write_bytes(result.stderr)
    record=dict(name=name,argv=argv,cwd=str(HERE),raw_exit_code=result.returncode,stdout=name+'.stdout',stderr=name+'.stderr')
    records.append(record)
    (HERE/'commands.json').write_text(json.dumps(records,indent=2)+'\n')
    print(name,'exit',result.returncode,flush=True)
    return result.returncode
run('compiler-version',['cc','--version'])
run('extract',['python','extract.py'])
bindings=json.loads((HERE/'bindings.json').read_text())['bindings']
for binding in bindings:
    raw=(LAB/binding['source']).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==binding['source_sha256']
    span=raw[binding['start_byte']:binding['end_byte_exclusive']]
    assert hashlib.sha256(span).hexdigest()==binding['sha256']
base=['cc','-std=c17','-O0','-g3','-Wall','-Wextra','-Werror','geometry.c','-lm']
assert run('compile-normal',base+['-o','geometry-normal'])==0
assert run('compile-ubsan',base+['-fsanitize=undefined,float-cast-overflow','-fno-sanitize-recover=all','-o','geometry-ubsan'])==0
assert run('normal-defined',['./geometry-normal'])==0
assert run('ubsan-defined',['./geometry-ubsan'])==0
assert run('compile-asan',base+['-fsanitize=address,undefined,float-cast-overflow','-fno-sanitize-recover=all','-o','geometry-asan'])==0
assert run('asan-defined',['./geometry-asan'])==0
for scenario in ['nan','pos-inf','neg-inf','int64-upper','int64-lower','below-int64-lower']:
    for mode in ['normal','ubsan','asan']:
        assert run(mode+'-'+scenario,['./geometry-'+mode,'--reproduce',scenario])==0
summary=dict(status='EXPERIMENTAL',CORE_C_GEOMETRY_TESTS='PASS',CORE_SANITIZER_TESTS='PASS',scope='exact extracted C only; no compositor integration',raw_commands='commands.json',bindings='bindings.json',original_evidence='../c-tests immutable')
(HERE/'handoff.json').write_text(json.dumps(summary,indent=2)+'\n')
entries=[dict(path=p.name,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size) for p in sorted(HERE.iterdir()) if p.is_file() and p.name!='manifest.json']
(HERE/'manifest.json').write_text(json.dumps(dict(status='EXPERIMENTAL',entries=entries),indent=2)+'\n')
