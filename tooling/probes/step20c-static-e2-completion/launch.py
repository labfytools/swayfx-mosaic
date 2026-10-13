#!/usr/bin/env python3
"""Exclusive consumed ticket; full reviewed preflight before dispatch.

Derived from static-nested-runtime/launch.py. No retries, refunds or builds.
"""
import sys
from pathlib import Path
import subprocess
from handoff import preflight,read,exclusive,SPENT,TICKET,sha,environment

def launch(lab):
    lab=Path(lab).resolve();auth=lab/'results/authorization.json'
    result=preflight(lab,auth)
    if read(lab/'results/preflight.json')!=result:raise ValueError('published-preflight-mismatch')
    exclusive(SPENT,dict(ticket=TICKET,lab=str(lab),token=result['token'],fixture_sha256=result['fixture']['sha256'],authorization_sha256=sha(auth)))
    argv=[sys.executable,str(lab/'fixture/run.py'),str(lab),'--future-authorization',str(auth)]
    with (lab/'raw/runner.stdout').open('x') as out,(lab/'raw/runner.stderr').open('x') as err:
        proc=subprocess.run(argv,env=environment(),stdout=out,stderr=err)
    exclusive(lab/'results/dispatch.json',dict(argv=argv,exit_code=proc.returncode,launch_consumed=True,runner_sha256=sha(lab/'fixture/run.py')))
    return proc.returncode

if __name__=='__main__':raise SystemExit(launch(Path(sys.argv[1])))
