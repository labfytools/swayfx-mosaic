#!/usr/bin/env python3
import argparse, json, pathlib
from assemble import verify, HERE
ap = argparse.ArgumentParser()
ap.add_argument("destination", type=pathlib.Path)
args = ap.parse_args()
print(json.dumps(verify(args.destination, json.loads((HERE / "provenance.json").read_text())), indent=2))
