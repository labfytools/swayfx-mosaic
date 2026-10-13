#!/usr/bin/env python3
"""One explicit reviewed C run; no retries, no inherited live desktop socket."""
import argparse
from pathlib import Path
import sys
from horizontal_adapter import BASE,generate
from horizontal_gate import preflight,sha
p=argparse.ArgumentParser();p.add_argument('lab',type=Path);p.add_argument('case',choices=['C0','C1','C2']);a=p.parse_args()
lab=a.lab.resolve();preflight(lab,a.case)
runner=lab/'horizontal'/a.case/'runner.py'
if runner.read_text()!=generate(a.case):raise ValueError('generated reviewed runner changed')
# Preserve overnight gate first, with only the identified validator dependency directory next.
sys.path.insert(1,str(BASE))
exec(compile(runner.read_text(),str(runner),'exec'),{'__name__':'__main__','__file__':str(runner)})
