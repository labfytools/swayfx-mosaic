"""Exhaustive assertion inventory for the derived E2 runtime, offline only.

PASS means classified source inventory, not executed runtime assertion coverage.
Independent review must inspect these final bytes before dispatch.
"""
import ast
import hashlib
from pathlib import Path
from model import require
from support import sha
HERE=Path(__file__).resolve().parent
RUNTIME=('run.py','model.py','observations.py','ipc_predicates.py','predicates.py','pixels.py','transition.py','lifecycle.py','authorization.py','ledger.py','support.py','handoff.py','launch.py','gate.py')
DOMAINS={'run.py':'runtime orchestration and raw outcomes','model.py':'typed coordinate and provenance contract',
 'observations.py':'native SHM vs applied destination geometry','ipc_predicates.py':'IPC identity and applied trace adapters',
 'predicates.py':'RGB/input/XDG protocol/unique-root/terminal observations','pixels.py':'exact RGB geometry',
 'transition.py':'current applied temporal transition','lifecycle.py':'explicit close and input lifecycle',
 'authorization.py':'reviewed dispatch before runtime','ledger.py':'nonrefundable action accounting',
 'support.py':'private environment/source integrity','handoff.py':'exclusive prospective source/review binding',
 'launch.py':'exclusive single dispatch','gate.py':'semantic offline receipts'}

def audit():
    records=[]
    for name in RUNTIME:
        source=HERE/name;tree=ast.parse(source.read_text())
        for n in ast.walk(tree):
            if isinstance(n,ast.Assert) or (isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='require'):
                records.append(dict(file=name,line=n.lineno,domain=DOMAINS[name],
                    predicate=ast.unparse(n),ast_sha256=hashlib.sha256(ast.dump(n,include_attributes=False).encode()).hexdigest(),
                    runtime_execution='NOT TESTED',review='PENDING_INDEPENDENT_REVIEW'))
    run=(HERE/'run.py').read_text();tree=ast.parse(run)
    require('E1' not in run,'E1-runtime-entirely-removed')
    calls=[n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name)]
    require(sum(n.func.id=='open_chain' for n in calls)==1,'single-runtime-chain')
    require(sum(n.func.id=='click' for n in calls)==4,'four-complete-click-sites')
    require(sum(n.func.id=='validate_applied_standard_transition' for n in calls)==2,'transition-through-B-input')
    require(all(name in run for name in ('opening_pair','explicit_child_close','a_survival','normal_owner_close','final_restoration')),'E2-full-path-shared-predicates')
    require("global baseline" in run and "if name=='E2':" in run,'reference-relocated-to-E2')
    require('applied_model(owners' not in run,'old-configure-not-reparsed-as-current')
    require(bool(records),'nonempty-source-audit')
    return dict(status='PASS',scope='EXHAUSTIVE_STATIC_ASSERTION_INVENTORY; runtime NOT TESTED',
        sources={n:sha(HERE/n) for n in RUNTIME},records=records,
        reviewed_hazards=['native SHM420x320 vs configured/applied content; no painted-height=320 predicate',
            'IPC y is not content origin; scene+titlebar+window offset is explicit',
            'current PI_SCENE and actual clip/owner trees; pending and IPC reply insufficient',
            'old Mosaic geometry reused directly, not reparsed using later standard configure',
            'root traces have no owner ID; only bounded unique-root XDG/IPC correlation',
            'right input pairs and left opening serials are different predicates',
            'actual terminal IPC code and each owned process code stay separate'])

if __name__=='__main__':
    import json,sys
    with Path(sys.argv[1]).open('x') as out:json.dump(audit(),out,indent=2);out.write('\n')
