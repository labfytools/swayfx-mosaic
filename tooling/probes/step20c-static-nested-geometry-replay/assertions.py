#!/usr/bin/env python3
"""Exhaustive AST inventory, explicit history/proposal classification and receipts.

A reached line is not proof of every conjunct. Runtime-only entries are labelled
NOT TESTED, and no synthetic 'register valid' test is credited to their fact.
"""
import argparse
import ast
import hashlib
import json
from pathlib import Path
from model import require
from support import save,sha

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
HISTORY=HERE.parent/'step20c-static-nested-grab'
HISTORICAL_FILES=('run.py','predicates.py','ipc_predicates.py','geometry_audit.py')
RESOURCE_NAMES={'reserve','spawn','wait','ipc','cmd','capture','inject','click','find','snapshot','delivery','correlate_pointer','close_client','owner_state','open_chain','stop_owned','watchdog','terminal','terminal_exchange','aggregate','correlate_historical','verify','save','command','initial','initial_for_offline_test','authorize','durable','flock','Popen','run','killpg','poll','is_socket','wait','unlink','rmtree','close','write','flush','fsync','count','read_text','write_text'}


def inventory(path):
    text=path.read_text();tree=ast.parse(text);parents={child:parent for parent in ast.walk(tree) for child in ast.iter_child_nodes(parent)}
    records=[]
    for node in ast.walk(tree):
        kind=None
        if isinstance(node,ast.Assert):kind='assert'
        elif isinstance(node,ast.Raise):kind='raise/exit failure'
        elif isinstance(node,(ast.If,ast.While)):kind='branch condition'
        elif isinstance(node,ast.Try):kind='exception/closure path'
        elif isinstance(node,ast.Compare):kind='comparison/identity condition'
        elif isinstance(node,ast.Subscript) and isinstance(node.slice,ast.UnaryOp) and isinstance(node.slice.op,ast.USub):kind='latest/index selection'
        elif isinstance(node,ast.BinOp) and isinstance(node.op,(ast.Add,ast.Sub,ast.Mult,ast.Div,ast.FloorDiv)):kind='coordinate arithmetic'
        elif isinstance(node,ast.Call):
            name=node.func.id if isinstance(node.func,ast.Name) else node.func.attr if isinstance(node.func,ast.Attribute) else ''
            if name in {'require','need'}:kind='checked invariant'
            elif name in RESOURCE_NAMES or name.startswith(('validate_','measure_','scene_')) or name in {'content','popup','same','intersect','to_png','from_png','verify_paint','pointer_local','fresh_chain','fresh_standard','constraints','local_clip_to_global','applied_model','output_model','viewport_model','verify_owner_occlusion','geometry','protocol','mapped','pair','dismissal','root_clip','popup_pixels','paint','point','equal','reference','configured','color_geometry'}:kind='validation/conversion/resource call'
        if kind:
            parent=node;function='<module>'
            while parent in parents:
                parent=parents[parent]
                if isinstance(parent,(ast.FunctionDef,ast.AsyncFunctionDef)):
                    function=parent.name;break
            expression=ast.get_source_segment(text,node) or ast.unparse(node)
            # Expressions in branch/try containers can contain whole suites.
            if isinstance(node,(ast.If,ast.While)):expression=ast.get_source_segment(text,node.test) or ast.unparse(node.test)
            if isinstance(node,ast.Try):expression='try / '+','.join(ast.unparse(h.type) if h.type else 'bare' for h in node.handlers)+' / finally='+str(bool(node.finalbody))
            canonical=ast.dump(node.test if isinstance(node,(ast.Assert,ast.If,ast.While)) else node,include_attributes=False)
            key=f'{path.relative_to(REPO)}:{node.lineno}:{node.col_offset}:{node.end_lineno}:{node.end_col_offset}:{kind}'
            contract=None
            if isinstance(node,ast.Call) and kind=='checked invariant' and len(node.args)>1 and isinstance(node.args[1],ast.Constant):contract=node.args[1].value
            records.append(dict(id=key,source=str(path.relative_to(REPO)),line=node.lineno,column=node.col_offset,function=function,kind=kind,invariant=expression,canonical_hash=hashlib.sha256(canonical.encode()).hexdigest(),contract=contract))
    return sorted(records,key=lambda r:(r['line'],r['column'],r['kind']))


def classify(r):
    text=r['invariant'];fn=r['function'];src=r['source']
    if fn=='correlate_historical' or any(w in (fn+' '+text).lower() for w in ('serial','protocol','ack','xdg','mapped','configure','parent','grab','dismiss','button','pair')):
        domain='XDG lifecycle/input';support=['wlroots types/xdg_shell/wlr_xdg_popup.c retained source-audit.json:configure/unconstrain','xdg-shell.xml ACK/map/parent/grab protocol','actual WAYLAND_DEBUG/client.log']
    elif any(w in (fn+' '+text).lower() for w in ('terminal','exit','cleanup','rescue','reap','kill','poll','process','socket','watchdog','wait','expire','time','code')):
        domain='terminal/owned resources';support=['actual stdout/stderr/process exit; no causal packet claim','sway/commands/exit.c and sway/main.c shutdown']
    elif any(w in (fn+' '+text).lower() for w in ('owner','workspace','focus','camera','scroll','reference','output','scene','clip','geometry','content','paint','png','buffer','height','width','origin','rect','point','pixel','bounds')):
        domain='typed geometry/assignment';support=['source-audit.json: output.c destination, transaction.c applied arrangement, ipc-json.c window_rect','SceneFX wlr_scene.c inherited clipping/render/hit; wlroots scene surface native input','actual IPC/applied traces and independent RGB']
    elif any(w in (fn+' '+text).lower() for w in ('ledger','budget','reserve','limit','debit','auth','gate','freeze','hash','manifest','sha','identity','inventory')):
        domain='authorization/provenance/budget';support=['offline gate explicit authorization and durable maxima','source hashes / exact files / typed identity provenance']
    else:
        domain='operational pure guard';support=['Python/C fixture operational contract; synthetic error branch permissible','offline gate scope']
    history='step20c-static-nested-grab/' in src
    decision='retain'
    rationale='Retain checked fact/operation; measurements remain independently required.'
    # Frozen invalid assumptions and obsolete one-ticket authorization are replaced.
    if history and ('topbox[3]-topbox[1]==320' in text or 'origin[1]==after' in text):
        decision='correct';rationale='Historical failure reproduced: native SHM height differs from rendered destination; titlebar-dependent IPC y excludes actual content offset. Replaced by model.content/verify_paint.'
    elif history and ('rows[-1]' in text and fn=='root_clip'):
        decision='replace';rationale='Latest arbitrary root is ambiguous. Proposed bounded time/owner/unique tree correlation fails closed.'
    elif history and ('configured_A' in text and '==[100,80' in text):
        decision='replace';rationale='Requested placement is source-backed prediction; actual configure/ACK/map is measured and crossing can be NOT EXERCISED.'
    elif history and ('OWNER' in text or 'STATIC_NESTED_GRAB_FIXTURE_PREFLIGHT' in text or fn=='<module>' and 'reserve(lab' in text):
        decision='replace';rationale='Historical authorization/ledger cannot authorize new run; future gate precedes all creation/debit.'
    elif history and fn=='validate_preflight' and ('commit[' in text or 'SavedBufferProbe' in text):
        decision='remove';rationale='Saved-buffer probe validator is not the native420x320 nested client contract. Applied/native/configure are correlated independently by shared model.'
    elif history and src.endswith('geometry_audit.py'):
        decision='retain historical only';rationale='Frozen diagnostic facts retained; new independent replay reads actual inputs without executing the failed runner.'
    stage={'open_chain':'E1/E2 mapped Mosaic','owner_state':'owner/camera observation','correlate_pointer':'visible pointer correlation','close_client':'ordered client close','root_clip':'bounded root clip','terminal':'terminal cleanup','protocol':'XDG valid-grab chain','popup_pixels':'rendered popup mask','geometry':'actual configured popup geometry','replay_native':'historical E1','replay_nested':'historical popup/standard/dismissal','authorize':'pre-runtime refusal','reserve':'durable reservation','content':'native/configure/applied/rendered conversion'}.get(fn,fn)
    # CONTRACT: aggregate and terminal_exchange receipts prove offline decisions
    # only; their successful mocks never become new runtime observations.
    if fn in {'aggregate','need'}:
        domain='authorization/provenance/budget'
        support=['mandatory offline evidence freshness/completeness and independent bound acceptance']
    r.update(history='frozen historical' if history else 'corrected proposed offline fixture',stage=stage,domain=domain,source_protocol_evidence_support=support,replay_possible=not (src.endswith('run.py') or fn in {'spawn','watchdog'}),decision=decision,rationale=rationale)
    return r


def build(lab):
    paths=[HISTORY/n for n in HISTORICAL_FILES]+[p for p in sorted(HERE.glob('*.py')) if p.name!='tests_offline.py']
    allrecords=[classify(r) for p in paths for r in inventory(p)]
    tests=json.loads((lab/'results/test-receipts.json').read_text())['tests']
    receipts={r['id']:r for r in tests if r['status']=='PASS'}
    by_hash={}
    for r in allrecords:
        if r['history'].startswith('corrected'):by_hash.setdefault(r['canonical_hash'],[]).append(r)
    for r in allrecords:
        corresponding=[r]+(by_hash.get(r['canonical_hash'],[]) if r['history']=='frozen historical' else [])
        positive=[];negative=[]
        for tid,test in receipts.items():
            lines=set(test.get('executed_lines',[]))
            executed=any(str(REPO/c['source'])+':'+str(c['line']) in lines for c in corresponding)
            contracts=test.get('contracts',[])
            failed_contract=r.get('contract') and any(c['contract']==r['contract'] and not c['pass'] for c in contracts)
            if executed and test['mode']=='positive' and not (r['domain']=='authorization/provenance/budget' and r['function'] in {'aggregate','need'} and 'inventory_' in tid):positive.append(tid)
            if failed_contract:negative.append(tid)
            elif executed and any(str(REPO/c['source'])+':'+str(c['line']) in test.get('failed_lines',[]) for c in corresponding):negative.append(tid)
        # Exact known historical semantic defects have explicit replacement tests.
        if r['decision']=='correct':
            suffix='negative_native_height' if '320' in r['invariant'] else 'negative_scene_window_y'
            negative += [tid for tid in receipts if tid.endswith(suffix)]
            positive += [tid for tid in receipts if tid.endswith('real_native_replay')]
        r['positive_executed_test_ids']=sorted(set(positive));r['negative_executed_test_ids']=sorted(set(negative))
        r['coverage_meaning']='executed line / exact require-contract failure or recorded false aggregation gate; conjunct completeness not implied'
        r['future_runtime_required']=r['source'].endswith('/run.py') or r['domain'] in {'XDG lifecycle/input','terminal/owned resources'}
        r['test_status']='RETIRED historical contract with explicit rationale' if r['decision']=='remove' else 'PASS executed positive/negative branch' if positive and negative else 'PARTIAL positive replay' if positive else 'NOT TESTED runtime dependency' if r['future_runtime_required'] else 'NOT TESTED pure branch'
        if not positive or not negative:
            r['untested_reason']='Live applied/input/cleanup fact requires future authorized execution; historical or synthetic receipt only proves listed observations.' if r['future_runtime_required'] else 'Branch inventoried; no claim of executed negative/positive coverage. Independent review must decide whether this pure branch is necessary for readiness.'
    files={str(p.relative_to(REPO)):sha(p) for p in paths}
    scientific_core={'model.py','ledger.py','authorization.py','observations.py','pixels.py'}
    unsupported=[r['id'] for r in allrecords if Path(r['source']).name in scientific_core and r['kind']=='checked invariant' and not (r['positive_executed_test_ids'] and r['negative_executed_test_ids'])]
    save(lab,'offline-core-coverage',dict(status='PASS' if not unsupported else 'FAIL NOT PROVEN',unproved=unsupported))
    save(lab,'assertion-register',dict(status='CLASSIFIED; execution status is per-entry',source_inventory=files,artifact_inventory={str(p):sha(p) for p in HERE.iterdir() if p.suffix in ('.patch','.json')},records=allrecords,counts={kind:sum(r['kind']==kind for r in allrecords) for kind in sorted({r['kind'] for r in allrecords})},historical_asserts=sum(r['kind']=='assert' and r['history']=='frozen historical' for r in allrecords)))
    return check(lab)


def check(lab):
    register=json.loads((lab/'results/assertion-register.json').read_text());records=register['records']
    actual={r['id']:r for rel in register['source_inventory'] for r in inventory(REPO/rel)}
    require(len(records)==len({r['id'] for r in records}) and set(actual)=={r['id'] for r in records},'register-exhaustive-unique')
    require(all(sha(REPO/rel)==digest for rel,digest in register['source_inventory'].items()) and all(sha(p)==digest for p,digest in register.get('artifact_inventory',{}).items()),'register-source-freshness')
    tests=json.loads((lab/'results/test-receipts.json').read_text())['tests'];passed={r['id'] for r in tests if r['status']=='PASS'}
    require(all(r['stage'] and r['domain'] and r['source_protocol_evidence_support'] and r['decision'] and r['rationale'] for r in records),'register-classified')
    require(all(r['canonical_hash']==actual[r['id']]['canonical_hash'] for r in records),'register-ast-freshness')
    require(all(set(r['positive_executed_test_ids']+r['negative_executed_test_ids'])<=passed for r in records),'register-executed-receipts')
    byhash={}
    for r in records:
        if r['history'].startswith('corrected'):byhash.setdefault(r['canonical_hash'],[]).append(r)
    proof={r['id']:r for r in tests if r['status']=='PASS'}
    def claimed(r,tid,negative):
        t=proof[tid];peers=[r]+(byhash.get(r['canonical_hash'],[]) if r['history']=='frozen historical' else [])
        lines=t.get('failed_lines' if negative else 'executed_lines',[])
        if any(str(REPO/c['source'])+':'+str(c['line']) in lines for c in peers):return True
        if negative and r.get('contract') and any(c['contract']==r['contract'] and not c['pass'] for c in t.get('contracts',[])):return True
        if r['decision']=='correct':
            if not negative:return tid.endswith('real_native_replay')
            name='negative_native_height' if '320' in r['invariant'] else 'negative_scene_window_y'
            return tid.endswith(name) and any(c['contract']=='paint-origin-intersection' and not c['pass'] for c in t.get('contracts',[]))
        return False
    require(all(claimed(r,tid,False) for r in records for tid in r['positive_executed_test_ids']) and
            all(claimed(r,tid,True) for r in records for tid in r['negative_executed_test_ids']), 'register-predicate-receipt-correlation')
    receipt_inventory=json.loads((lab/'results/test-receipts.json').read_text()).get('source_inventory',{})
    require(all(sha(p)==digest for p,digest in receipt_inventory.items()),'test-receipt-source-freshness')
    core=json.loads((lab/'results/offline-core-coverage.json').read_text()) if (lab/'results/offline-core-coverage.json').exists() else None
    if core is not None:require(core.get('status')=='PASS','offline-core-untested-rejected')
    require(sum(r['kind']=='assert' and r['history']=='frozen historical' for r in records)==145,'historical-145-assertions')
    unresolved=[r['id'] for r in records if r['test_status']=='NOT TESTED pure branch' and r['kind']=='checked invariant']
    result=dict(status='PASS AST inventory/freshness/classification; PARTIAL executed branch coverage' if unresolved else 'PASS',entries=len(records),historical_asserts=145,positive_and_negative=sum(bool(r['positive_executed_test_ids'] and r['negative_executed_test_ids']) for r in records),positive_only=sum(bool(r['positive_executed_test_ids']) and not r['negative_executed_test_ids'] for r in records),unexecuted=sum(not r['positive_executed_test_ids'] and not r['negative_executed_test_ids'] for r in records),unresolved_pure_invariants=unresolved,runtime_facts='NOT TESTED; no generic register test credited')
    save(lab,'assertion-coverage',result);return result

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('lab',type=Path);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    print(json.dumps(check(args.lab) if args.check else build(args.lab),indent=2))
