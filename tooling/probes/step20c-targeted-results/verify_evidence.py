"""Read-only integrity checks for retained targeted evidence.

WHY: published compact records must resolve to actual retained bytes.
CONTRACT: this verifies integrity, never scientific readiness or a runtime gate.
INVARIANT: no launch, ledger mutation, receipt rewrite or inferred buffer identity.
"""
import hashlib
import json
from pathlib import Path


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def verify(directory):
    directory = Path(directory)
    repo = directory.parents[2]
    results = json.loads((directory / "RESULTS.json").read_text())
    artifacts = json.loads((directory / "ARTIFACTS.json").read_text())
    bindings = list(results["provenance"])
    bindings += [{"path": str(repo / x["path"]), "sha256": x["sha256"]}
                 for x in results["frozen_source_bindings"]]
    for run in artifacts["runs"]:
        bindings += [{"path": str(Path(run["prefix"]) / name), "sha256": digest}
                     for name, digest in run["files"].items()]
    failures = []
    for binding in bindings:
        try:
            if sha(binding["path"]) != binding["sha256"]:
                failures.append(binding["path"])
        except OSError:
            failures.append(binding["path"])
    if failures:
        raise ValueError("Missing or changed retained files: " + ", ".join(failures))
    return {"status": "INTEGRITY_PASS", "bindings": len(bindings),
            "scientific_readiness": "NOT_ASSERTED"}


if __name__ == "__main__":
    print(json.dumps(verify(Path(__file__).resolve().parent), sort_keys=True))
