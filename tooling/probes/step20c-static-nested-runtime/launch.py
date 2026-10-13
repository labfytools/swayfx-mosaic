#!/usr/bin/env python3
"""One durable dispatch; never rebuild, retry, refund or reset.

WHY: a new directory must not reopen this ticket's single launch entitlement.
CONTRACT: full reviewed preflight precedes consumption; runner owns its ledger.
INVARIANT: even a dispatch/runner failure leaves the exclusive spent token.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
from handoff import preflight, exclusive, REGISTRY, SPENT, TICKET, sha, environment


def launch(lab):
    lab = Path(lab).resolve()
    auth = lab / 'results/authorization.json'
    result = preflight(lab, auth)
    existing = json.loads((lab / 'results/preflight.json').read_text())
    if existing != result:
        raise ValueError('published-preflight-must-match')
    # O_EXCL consumption also arbitrates concurrent dispatches. No action can
    # execute if another dispatcher won, even before runner ledger locking.
    exclusive(SPENT, dict(ticket=TICKET, lab=str(lab), uid=os.getuid(), owner_registry=str(REGISTRY),
                          fixture_sha256=result['fixture']['sha256'], authorization_sha256=sha(auth)))
    env = environment()
    for key in ('LD_DEBUG', 'LD_DEBUG_OUTPUT'):
        env.pop(key, None)
    argv = [sys.executable, str(lab / 'fixture/run.py'), str(lab), '--future-authorization', str(auth)]
    with (lab / 'raw/runner.stdout').open('x') as out, (lab / 'raw/runner.stderr').open('x') as err:
        proc = subprocess.run(argv, env=env, stdout=out, stderr=err)
    exclusive(lab / 'results/dispatch.json', dict(argv=argv, exit_code=proc.returncode, launch_consumed=True,
                                                 runner_sha256=sha(lab / 'fixture/run.py')))
    return proc.returncode


if __name__ == '__main__':
    raise SystemExit(launch(Path(sys.argv[1])))
