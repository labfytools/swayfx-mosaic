#!/usr/bin/env python3
"""Portable source-only freeze, external to immutable source; never admits runs."""
import argparse
from pathlib import Path
from gate import canonical_lab,source_files,source_modes,durable,TICKET
from plans import RUNS,LIMITS

def freeze(lab,author,output=None):
 lab=canonical_lab(lab);work=lab/'followup-work';work.mkdir(mode=0o700,exist_ok=True)
 result=dict(schema='native-closure-source-v1',ticket=TICKET,author=author,files=source_files(),modes=source_modes(),plans=RUNS,limits=LIMITS,runtime='NOT_RUN',independent_review='NOT_PROVEN')
 destination=Path(output) if output else work/'source-manifest.json'
 if destination.resolve()!=destination or destination.parent!=work:raise ValueError('freeze output must be canonical followup-work path')
 durable(destination,result,exclusive=True);return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--lab',required=True);p.add_argument('--author',required=True);p.add_argument('--output');a=p.parse_args();freeze(a.lab,a.author,a.output)
