#!/usr/bin/env python3
"""EXPERIMENTAL read-only exact-key native replay. Never synthesize presents."""
import argparse, hashlib, json, re
from pathlib import Path
from input_validators import require
NATIVE_ASSERTIONS=('native-exact-output-sequence', 'no-invented-present', 'no-output-source-buffer-alias', 'no-generation-inference')

def replay(text, causes=None):
    commits={}; presents={}; causes=causes or {}
    for raw in text.splitlines():
        if not any(mark in raw for mark in ('PI_OUTPUT_COMMIT ', 'PI_OUTPUT_PRESENT ')): continue
        f=dict(re.findall(r'(\w+)=([^\s]+)',raw))
        require(all(k in f for k in ('output','commit_seq','ns')), 'native fields absent')
        key=(f['output'],int(f['commit_seq']))
        if 'PI_OUTPUT_PRESENT ' in raw:
            require(f.get('presented') in ('0','1'), 'real presented flag required')
        dest=commits if 'PI_OUTPUT_COMMIT ' in raw else presents
        require(key not in dest, 'duplicate exact key')
        dest[key]=dict(fields=f,raw=raw)
    rows=[]
    for key,c in commits.items():
        p=presents.get(key)
        if p:
            require(int(p['fields']['ns'])>int(c['fields']['ns']), 'present precedes commit')
            require(p['fields'].get('presented') in ('0','1'), 'real presented flag required')
        reason=causes.get(key)
        if reason:
            require(reason.get('evidence') and reason.get('source_sha256') and reason.get('source_path') and reason.get('kind') in ('RUN_END','OUTPUT_DESTROY','IDLE_CALLBACK_CANCELLATION','INSTRUMENTATION_FILTER'), 'unproven missing cause')
            source=Path(reason['source_path']);raw=source.read_bytes()
            require(hashlib.sha256(raw).hexdigest()==reason['source_sha256'] and reason['evidence'] in raw.decode(errors='replace'), 'missing-cause source binding')
            marker='PI_MISSING_PRESENT_CAUSE '+f'output={key[0]} commit_seq={key[1]} kind={reason["kind"]}'
            require(marker in reason['evidence'], 'exact native cause marker required; source possibility is not occurrence proof')
        # CONTRACT: observed absence is unknown unless an exact-key cause has
        # its own source proof. A nearby teardown timestamp is insufficient.
        rows.append(dict(output=key[0],commit_seq=key[1],commit=c,present=p,
            status='PAIRED' if p else 'MISSING_PRESENT',
            missing_cause=None if p else (reason or {'kind':'UNKNOWN'})))
    return dict(total_commits=len(commits),paired=sum(r['present'] is not None for r in rows),
        missing=sum(r['present'] is None for r in rows),rows=rows,
        unmatched_presents=[dict(output=k[0],commit_seq=k[1],**v) for k,v in presents.items() if k not in commits],
        NATIVE_COMMIT_PRESENT='PARTIALLY_FEASIBLE' if commits else 'NOT_EXERCISED',
        NATIVE_ORDERING_DISCRIMINANT='NOT_EXERCISED',NATIVE_BUFFER_IDENTITY='NOT_PROVEN',
        NATIVE_BUFFER_LIFETIME='NOT_PROVEN',NATIVE_DAMAGE_COVERAGE='NOT_PROVEN',
        GPU_COMPLETION='NOT_PROVEN',ATOMIC_GENERATION='NOT_PROVEN',
        limits='Exact native event keys only; PNG, SHM, saved scene buffers and output GPU buffers are distinct. Stabilized damage envelopes do not prove every frame.')

def validate_claims(claims):
    # INVARIANT: pairage is never evidence for these stronger identities.
    require(not claims.get('source_buffer_is_output') and not claims.get('atomic_generation') and not claims.get('gpu_completion') and not claims.get('all_frames_damage'), 'invented native inference')

def main():
    p=argparse.ArgumentParser();p.add_argument('--log',type=Path,action='append',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    require(not a.output.exists(),'new replay receipt only')
    reports=[]
    for path in a.log:
        raw=path.read_bytes();reports.append(dict(path=str(path),sha256=hashlib.sha256(raw).hexdigest(),replay=replay(raw.decode(errors='replace'))))
    result=dict(status='EXPERIMENTAL',runtime='NOT_RUN',reports=reports,
        totals={k:sum(r['replay'][k] for r in reports) for k in ('total_commits','paired','missing')})
    a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result['totals']))
if __name__=='__main__':main()
