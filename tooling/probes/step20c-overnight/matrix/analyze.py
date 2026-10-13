"""Offline per-case bounded evidence summary; never invent missing native identity."""
import argparse,json
from pathlib import Path
from gate import LAB
from protocols import RUNS
p=argparse.ArgumentParser();p.add_argument('run_id',choices=RUNS);a=p.parse_args();w=LAB/'matrix'/a.run_id/'run'
raw=json.loads((w/'outcome.json').read_text());spec=RUNS[a.run_id]
print(json.dumps(dict(case=spec['id'],runtime=raw,status=raw['status'],source_observability_ceilings=spec.get('ceilings',[]),
    complete_damage='NOT PROVEN',atomic_generation='NOT PROVEN',production='NOT YET SUPPORTED',historical_acceptance_transferred=False),indent=2))
