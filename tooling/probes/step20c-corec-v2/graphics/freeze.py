#!/usr/bin/env python3
"""Freeze source-only bytes. No ledger initialization/admission/reservation."""
import argparse
from pathlib import Path
from gate import canonical_lab,sha,durable,TICKET
from plans import RUNS,LIMITS

def freeze(lab):
 lab=canonical_lab(lab);root=Path(__file__).resolve().parent
 files={str(p.relative_to(root)):sha(p) for p in sorted(root.rglob("*")) if p.is_file()}
 if any(name.endswith((".pyc",".png",".so",".o")) or "__pycache__" in name for name in files):raise ValueError("generated artifact in source kit")
 result=dict(schema="graphics-v2-source-freeze",ticket=TICKET,source_root=str(root),files=files,plans=RUNS,limits=LIMITS,preflight="PENDING_INDEPENDENT_REVIEW",runtime="NOT_RUN",real_reservations=0)
 durable(lab/"graphics-next-work/graphics-source-freeze.json",result);return result
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--lab",required=True);a=p.parse_args();freeze(a.lab)
