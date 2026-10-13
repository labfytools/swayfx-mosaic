"""Pure refusal gate. No files/locks/processes are created by validation."""
import json
from pathlib import Path
from model import require

MARKER = 'SWAYFX_MOSAIC_STATIC_NESTED_GEOMETRY_OFFLINE_GATE=READY_FOR_NEW_RUNTIME'
THIS_TICKET = 'static-nested-geometry-offline-replay'


def authorize(lab, authorization):
    require(authorization is not None, 'explicit-future-authorization-required')
    auth = json.loads(Path(authorization).read_text())
    require(auth.get('scope') == 'one-new-static-nested-headless-run' and
            auth.get('explicit_user_authorization') is True and
            auth.get('ticket') and auth['ticket'] != THIS_TICKET, 'distinct-future-ticket-required')
    lab = Path(lab).resolve()
    require(auth.get('registered_lab') == str(lab), 'registered-fresh-lab-required')
    require('static-nested-grab-m0a5e2qh' not in str(lab) and
            'static-nested-geometry-replay-a56csvoo' not in str(lab), 'historical-or-offline-lab-forbidden')
    gate = json.loads((lab/'results/offline-gate.json').read_text())
    review = json.loads((lab/'results/independent-review.json').read_text())
    require(gate.get('marker') == MARKER and review.get('status') == 'ACCEPTED' and
            review.get('independent') is True, 'completed-offline-review-required')
    require(not (lab/'run').exists(), 'fresh-run-required')
    require(all(auth.get(k) for k in ('owner_registry', 'binary', 'binary_sha256', 'wlroots_sha256')), 'future-input-provenance')
    return auth
