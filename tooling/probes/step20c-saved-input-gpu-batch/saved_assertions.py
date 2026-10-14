"""Complete source-position inventory for common/saved important predicates."""
import ast
from pathlib import Path
from plans import HERE,HIST
# Test names describe deterministic predicate validation. Runtime dependencies
# explicitly stay NOT RUN until the separately reviewed one-shot campaign.
CONTRACTS={
'ledger.py':('accounting/exact-byte authorization','durable budget + freeze/review/preflight SHA','test_ledger.AccountingTests.test_all_caps','test_ledger.AccountingTests.test_old_ticket','launch review; token; identity'),
'runtime.py':('owned runtime / cleanup','private socket, /proc identity, mapped libraries, owned EXIT log','test_saved.SavedTests.test_historical_held','test_saved.SavedTests.test_dead_client','actual runtime NOT RUN; inherited sealed engine'),
'saved.py':('held → natural timeout → final H2','IPC requests/snapshots, real client wire, full RGB, compositor timeout, EXIT error','test_saved.SavedTests.test_geometry_replay','test_saved.SavedTests.test_teardown_not_natural','actual runtime NOT RUN; C3 native evidence never transferred'),
'saved_validators.py':('saved instance / geometry / retirement','ordered SD_CREATE/TREE/SAMPLE/ANCESTOR/DRAW/REMOVE/DESTROY/source signal/wire/PNG','test_saved.SavedTests.test_historical_reuse','test_saved.SavedTests.test_post_destroy','C3 exact; no native generation; release ambiguity NOT PROVEN'),
'saved_replay.py':('historical read-only association','exact historical IPC command receipt, initial/pending snapshot, wire, log, PNG','saved_replay.replay','test_saved.SavedTests.test_false_ack','read-only historical evidence'),
}
def inventory():
    rows=[]
    for filename,contract in CONTRACTS.items():
        path=HERE/filename;source=path.read_text();tree=ast.parse(source)
        for n in ast.walk(tree):
            if isinstance(n,ast.Call) and ((isinstance(n.func,ast.Name) and n.func.id=='need') or (isinstance(n.func,ast.Attribute) and n.func.attr=='need')):
                rows.append(dict(file=str(path),line=n.lineno,step=contract[0],predicate=ast.get_source_segment(source,n),evidence=contract[1],positive=contract[2],negative=contract[3],runtime_dependency=contract[4]))
    # Pure imported predicates carry their own source position and old frozen
    # tests; new negative replay validates their real wire/geometry assumptions.
    imported=HERE.parent/'step20c-targeted-diagnostic/diagnostic.py'
    source=imported.read_text();tree=ast.parse(source)
    for f in tree.body:
        if isinstance(f,ast.FunctionDef) and f.name in ('pending_geometry','saved_identity'):
            for n in ast.walk(f):
                if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='need':rows.append(dict(file=str(imported),line=n.lineno,step='imported '+f.name,predicate=ast.get_source_segment(source,n),evidence='real IPC/wire or interval-filtered SD native trace',positive='test_saved.SavedTests.test_geometry_replay' if f.name=='pending_geometry' else 'test_saved.SavedTests.test_historical_reuse',negative='test_saved.SavedTests.test_geometry_null' if f.name=='pending_geometry' else 'test_saved.SavedTests.test_wrong_origin',runtime_dependency='source closure exact SHA; addresses filtered by observed instance'))
    return sorted(rows,key=lambda r:(r['file'],r['line']))
if __name__=='__main__':
    import json
    print(json.dumps(inventory(),indent=2))
