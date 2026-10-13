#!/usr/bin/env python3
"""Read-only integrity checks; no remapping, rewriting, or budget refund."""
import argparse
from pathlib import Path
from support import sha


def verify_inventory(manifest):
    rows=Path(manifest).read_text().splitlines();assert rows
    seen=set()
    for row in rows:
        digest,p=row.split('  ',1);assert p not in seen;seen.add(p)
        assert sha(p)==digest,('manifest mismatch',p)
    return {'entries':len(rows),'sha256':sha(manifest)}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('lab',type=Path);a=p.parse_args()
    for name in ['fixture-freeze','source','evidence']:
        print(name,verify_inventory(a.lab/'results'/(name+'-sha256.txt')),'PASS')
