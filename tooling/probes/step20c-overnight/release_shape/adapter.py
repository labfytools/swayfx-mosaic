"""Bounded G smoke derivation from the frozen accepted C2 fixture."""
from pathlib import Path
import ast
import hashlib
import sys

REPO = Path(__file__).resolve().parents[4]
OVERNIGHT = REPO / 'tooling/probes/step20c-overnight'
BASE = REPO / 'tooling/probes/step20c-static-e2-completion'
sys.path.insert(0, str(OVERNIGHT))
from horizontal_adapter import generate, replace_one

IMPORT = 'from horizontal_gate import begin_run, debit, binding_sources, finish_run'
G_IMPORT = 'from gate import begin_run, debit, binding_sources, finish_run'

def generate_g():
    text = generate('C2')
    text = replace_one(text, IMPORT, G_IMPORT)
    ast.parse(text, filename='G-smoke/runner.py')
    return text

if __name__ == '__main__':
    runner = generate_g()
    print('G_RUNNER_SHA256', hashlib.sha256(runner.encode()).hexdigest())
