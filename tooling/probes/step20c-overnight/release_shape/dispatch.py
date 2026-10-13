"""Prepare, freeze, check, or explicitly preflight G; RUN needs review acceptance."""
import argparse
import json
import os
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
OVERNIGHT=HERE.parent
sys.path[:0]=[str(HERE),str(OVERNIGHT)]
from adapter import generate_g
import gate

def prepare():
    w=gate.WORK
    os.chmod(w,0o700);os.chmod(w/'results',0o700)
    if (w/'run').exists() or (w/'consumed.json').exists() or (w/'freeze.json').exists():
        raise RuntimeError('G workspace already consumed/frozen; no replacement or retry')
    for name in ('nested-client','pointer-daemon','static-reference'):
        p=w/name
        if not p.is_symlink() or p.resolve()!=(gate.LAB/'horizontal/clients'/name).resolve():
            raise RuntimeError('C2 client symlink must reference exact compiled fixture: '+name)
    # Bind complete reused C2 runner source and its accepted input before writing the generated G copy.
    c2=gate.LAB/'horizontal/C2/runner.py'
    from horizontal_adapter import generate
    if c2.read_text()!=generate('C2'):
        raise RuntimeError('frozen C2 fixture source mismatch')
    runner=generate_g()
    fd=os.open(w/'runner.py',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'w') as stream:
        stream.write(runner);stream.flush();os.fsync(stream.fileno())
    dfd=os.open(w,os.O_RDONLY|os.O_DIRECTORY)
    try:os.fsync(dfd)
    finally:os.close(dfd)
    print('G_SMOKE_RUNNER_PREPARED runtime NOT RUN')

def freeze():
    w=gate.WORK
    if (w/'freeze.json').exists(): raise RuntimeError('freeze already exists; no replacement')
    tests=json.loads((w/'results/prepare-tests.json').read_text())
    if tests.get('status')!='PASS': raise RuntimeError('offline fixture tests not PASS')
    files=gate.expected_files()
    # Verify all entries still exist and bind the current persistent budget without making it a post-run immutable input.
    budget_sha=gate.sha(gate.LAB/'budget.json')
    data={'status':'READY_FOR_REVIEW','scope':'OVERNIGHT_G_SMOKE_FINAL_BYTES',
          'files':files,'budget_before_run_sha256':budget_sha,
          'binary':{'path':str(gate.BINARY),'sha256':gate.BINARY_SHA,'build_id':gate.BUILD_ID},
          'source_bindings':gate.TRACE_SOURCES,
          'plan':gate.PLANS,'graphics':'NOT TESTED','neutrality':'NOT PROVEN',
          'generic_author_generator_negatives':'NOT_PROVEN: mechanism and execution receipt not retained',
          'runtime':'NOT RUN'}
    gate.exclusive(w/'freeze.json',data)
    # The persisted freeze is read back and checked before report.
    gate._frozen_files()
    print('G_SMOKE_FREEZE_READY_FOR_INDEPENDENT_REVIEW')

def missing_review_preflight():
    before=(gate.LAB/'budget.json').read_bytes()
    token=gate.WORK/'consumed.json';run=gate.WORK/'run'
    try:gate.preflight(require_review=True)
    except Exception as exc:
        refusal={'status':'REFUSED','reason':str(exc),'review_missing':not (gate.GROOT/'reviews/release-smoke-review.json').exists(),
                 'budget_unchanged':(gate.LAB/'budget.json').read_bytes()==before,
                 'consumed_token_created':token.exists(),'runtime_created':run.exists()}
        if not refusal['review_missing'] or not refusal['budget_unchanged'] or refusal['consumed_token_created'] or refusal['runtime_created']:
            raise RuntimeError('missing-review refusal side-effect invariant failed') from exc
        out=gate.WORK/'results/missing-review-preflight.json'
        fd=os.open(out,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
        with os.fdopen(fd,'w') as stream:json.dump(refusal,stream,indent=2);stream.write('\n');stream.flush();os.fsync(stream.fileno())
        print(json.dumps(refusal,indent=2));return 2
    print(json.dumps({'status':'PASS','scope':'reviewed G bytes only','binary':str(gate.BINARY),
                      'binary_sha256':gate.BINARY_SHA,'build_id':gate.BUILD_ID,
                      'runtime':'NOT RUN','token_created':False},indent=2))
    return 0

def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=('prepare','tests','freeze','preflight','run'));a=p.parse_args()
    if a.action=='prepare':prepare()
    elif a.action=='tests':
        import subprocess
        return subprocess.run([sys.executable,str(HERE/'tests.py'),'--output',str(gate.WORK/'results/prepare-tests.json')],check=False).returncode
    elif a.action=='freeze':freeze()
    elif a.action=='preflight':return missing_review_preflight()
    else:
        gate.preflight(require_review=True)
        runner=gate.WORK/'runner.py'
        if runner.read_text()!=generate_g():raise RuntimeError('G runner differs from freeze generator')
        sys.path[:0]=[str(HERE),str(OVERNIGHT),str(gate.BASE)]
        exec(compile(runner.read_text(),str(runner),'exec'),{'__name__':'__main__','__file__':str(runner)})
    return 0
if __name__=='__main__':raise SystemExit(main())
