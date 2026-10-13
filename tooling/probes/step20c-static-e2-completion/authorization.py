"""Fail closed before any lock, ledger debit or subprocess."""
import json
from pathlib import Path
from model import require

def authorize(lab,authorization):
    require(authorization is not None,'explicit-authorization-required')
    from handoff import preflight
    preflight(lab,authorization,review=True,consumed=True)
    return json.loads(Path(authorization).read_text())
