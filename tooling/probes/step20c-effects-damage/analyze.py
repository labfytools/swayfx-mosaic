#!/usr/bin/env python3
"""Measure fixed output-local PNG regions and hash every retained raw proof."""

import argparse
import hashlib
import json
import re
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw

ROIS = {
    "left": {"interior": (300, 100, 700, 500),
             "boundary": (720, 50, 800, 550)},
    "right": {"boundary": (0, 50, 80, 550),
              "reference": (250, 250, 550, 500)},
}
PHASES = ("FX1-shadow", "FX2-blur", "FX3-optimized-candidate",
          "FX4-combined", "T4-hidden-1", "T5-return-1", "T4-hidden-2",
          "T5-return-2", "T4-hidden-3", "T5-return-3",
          "T7-standard-return", "T6-disabled", "T6-restored", "T6-closed")


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def native_events(log):
    commits = [{"output": m[0], "commit_seq": int(m[1]), "ns": int(m[2])}
               for m in re.findall(r"PI_OUTPUT_COMMIT output=(\S+) commit_seq=(\d+) ns=(\d+)", log)]
    presents = [{"output": m[0], "commit_seq": int(m[1]), "ns": int(m[2]),
                 "presented": bool(int(m[3]))}
                for m in re.findall(r"PI_OUTPUT_PRESENT output=(\S+) commit_seq=(\d+) ns=(\d+).*?presented=(\d+)", log)]
    identities = {(p["output"], p["commit_seq"]) for p in presents}
    return {"instrumented": bool(commits), "commits": commits, "presentations": presents,
            "unpresented": [c for c in commits if (c["output"], c["commit_seq"]) not in identities]}


def difference(first, second, box=None):
    if box:
        first, second = first.crop(box), second.crop(box)
    delta = ImageChops.difference(first, second)
    bbox = delta.getbbox()
    channels = list(delta.getdata())
    pixels = sum(channel != (0, 0, 0) for channel in channels)
    return {"pixels": pixels, "bbox": bbox,
            "mean_rgb_distance": round(sum(sum(channel) for channel in channels) /
                                       (3 * delta.width * delta.height), 4)}


def analyze_run(run):
    result = {"run": run.name, "captures": [], "comparisons": [],
              "damage": {"events": 0, "outputs": {}}, "failure": None}
    status = run / "exit-status.json"
    if status.exists():
        result["exit_status"] = json.loads(status.read_text())
    events = []
    event_file = run / "events.jsonl"
    if event_file.exists():
        events = [json.loads(line) for line in event_file.read_text().splitlines()]
    captures = {(item["output"], item["tag"]): item for item in events
                if item.get("kind") == "capture"}
    damage_events = []
    log = run / "compositor.log"
    if log.exists():
        log_text = log.read_text(errors="replace")
        result["native_events"] = native_events(log_text)
        result["renderer"] = {key: re.findall(pattern, log_text)[:1]
                              for key, pattern in {
                                  "gles": r"Using (OpenGL ES[^\n]+)",
                                  "gpu": r"GL renderer: ([^\n]+)",
                                  "wlroots": r"wlroots version ([^\n]+)",
                                  "scenefx": r"scenefx version ([^\n]+)",
                              }.items()}
        damage = re.compile(r"TEMPORAL_DAMAGE ordinal=\d+ ns=(\d+) output=(\S+) extent=(-?\d+),(-?\d+)\.\.(-?\d+),(-?\d+)")
        for match in damage.finditer(log.read_text(errors="replace")):
            damage_events.append((int(match.group(1)), match.group(2),
                                  tuple(int(match.group(i)) for i in range(3, 7))))
            result["damage"]["events"] += 1
            output = match.group(2)
            result["damage"]["outputs"][output] = result["damage"]["outputs"].get(output, 0) + 1
    for side in ROIS:
        baseline = run / f"{side}-FX0-off.png"
        if not baseline.exists():
            continue
        with Image.open(baseline) as img:
            base = img.convert("RGB")
        previous = None
        ordered = [(item["after_ns"], run / item["path"], item)
                   for item in captures.values() if item["output"] ==
                   ("HEADLESS-1" if side == "left" else "HEADLESS-2")]
        for _, path, capture in sorted(ordered):
            with Image.open(path) as img:
                image = img.convert("RGB")
            if image.size != (800, 600):
                result["failure"] = f"unexpected dimensions: {path.name} {image.size}"
            result["captures"].append({"file": path.name, "side": side,
                "phase": path.stem[len(side)+1:], "dimensions": image.size,
                "sha256": sha(path), "before_ns": capture["before_ns"],
                "after_ns": capture["after_ns"]})
            if previous is not None:
                older, old_image = previous
                output = capture["output"]
                interval = [box for ns, name, box in damage_events
                            if name == output and older["after_ns"] < ns <= capture["after_ns"]]
                mask = Image.new("1", image.size, 0)
                painter = ImageDraw.Draw(mask)
                for box in interval:
                    painter.rectangle((box[0], box[1], box[2]-1, box[3]-1), fill=1)
                changed = ImageChops.difference(old_image, image).convert("RGB")
                outside = sum(px != (0, 0, 0) and not cover
                              for px, cover in zip(changed.getdata(), mask.getdata()))
                result.setdefault("transitions", []).append({"side": side,
                    "from": older["tag"], "to": capture["tag"],
                    "changed_pixels": difference(old_image, image)["pixels"],
                    "damage_events": len(interval) if damage_events else None,
                    "changed_outside_damage": outside if damage_events else None})
            previous = capture, image
            if path != baseline:
                result["comparisons"].append({"side": side,
                    "phase": path.stem[len(side)+1:],
                    "baseline": baseline.name,
                    "whole": difference(base, image),
                    "rois": {name: difference(base, image, box)
                             for name, box in ROIS[side].items()}})
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("lab", type=Path)
    parser.add_argument("runs", nargs="+", type=Path)
    parser.add_argument("--include-all-raw-runs", action="store_true",
                        help="manifest all retained runs, including excluded fixture variants")
    args = parser.parse_args()
    lab = args.lab.resolve()
    out = lab / "effects-damage-results"
    out.mkdir(mode=0o700, exist_ok=True)
    results = [analyze_run(run.resolve()) for run in args.runs]
    (out / "pixel-analysis.json").write_text(json.dumps(results, indent=2) + "\n")
    raw_runs = list((lab / "runs").iterdir()) if args.include_all_raw_runs else args.runs
    proofs = [path for run in raw_runs for path in run.resolve().rglob("*") if path.is_file()]
    proofs += [lab / "fx-checker.png"]
    proofs += [path for path in (lab / "effects-damage-run-generated.py",
                                 lab / "effects-build-log.txt",
                                 lab / "effects-source-sha256.txt",
                                 out / "metadata.json",
                                 out / "pixel-analysis.json") if path.exists()]
    proofs += [path for path in (lab / "effects-preparation-logs").rglob("*") if path.is_file()]
    manifest = out / "raw-evidence-sha256.txt"
    manifest.write_text("".join(f"{sha(path)}  {path.relative_to(lab)}\n"
                                for path in sorted(set(proofs))))
    print(json.dumps({"runs": len(results), "captures": sum(len(r["captures"]) for r in results),
                      "raw_proofs": len(proofs), "manifest_sha256": sha(manifest),
                      "results": str(out)}, indent=2))


if __name__ == "__main__":
    main()
