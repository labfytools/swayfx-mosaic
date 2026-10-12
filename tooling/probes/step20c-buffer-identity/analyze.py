#!/usr/bin/env python3
"""Analyze one private fixed-geometry buffer run without assigning a frame to input."""

import hashlib
import json
import pathlib
import re
import statistics
import sys

from PIL import Image

if len(sys.argv) != 4:
    raise SystemExit("usage: analyze.py LAB RUN_DIRECTORY BUFFER_DIRECTORY")
lab, run, buffers = map(pathlib.Path, sys.argv[1:])
lines = (run / "compositor.log").read_text(errors="replace").splitlines()
out = lab / "results"
out.mkdir(exist_ok=True)


def records(kind):
    found = []
    for line in lines:
        if kind not in line:
            continue
        tail = line.split(kind, 1)[1]
        values = dict(re.findall(r"([a-z_]+)=([^ ]+)", tail))
        values["kind"] = kind
        found.append(values)
    return found


def save(name, value):
    (out / (name + ".json")).write_text(json.dumps(value, indent=2) + "\n")


observed = records("BI_BUFFER")
direct = {int(x["id"]): x for x in records("BI_DIRECT")}
reads = {int(x["id"]): x for x in records("BI_READ")}
commits = {int(x["id"]): x for x in records("BI_COMMIT")}
event_buffers = {int(x["id"]): x for x in records("BI_EVENT_BUFFER")}
locked = {int(x["id"]): x for x in records("BI_LOCKED")}
held_present = {int(x["id"]): x for x in records("BI_PRESENT_HOLD")}
released = {int(x["id"]): x for x in records("BI_RELEASE")}
second_reads = {int(x["id"]): x for x in records("BI_PRESENT_READ")}
native_commits = records("PI_OUTPUT_COMMIT")
native_presents = records("PI_OUTPUT_PRESENT")
stages = records("BI_STAGE")

# The synchronous commit callback logs its scene observation immediately
# after the native event line. Do not attach a later logical IPC state.
scene = {}
for i, line in enumerate(lines):
    if "PI_OUTPUT_COMMIT" not in line:
        continue
    v = dict(re.findall(r"([a-z_]+)=([^ ]+)", line.split("PI_OUTPUT_COMMIT", 1)[1]))
    if i + 1 < len(lines) and "PI_SCENE" in lines[i + 1]:
        z = dict(re.findall(r"([a-z_]+)=([^ ]+)", lines[i + 1].split("PI_SCENE", 1)[1]))
        if z.get("output") == v.get("output"):
            scene[(v["output"], v["commit_seq"])] = z

presents = {(v["output"], v["commit_seq"]): v for v in native_presents}
fingerprints = []
lifetimes = []
correlations = []
pixels = []
scene_states = []
for entry in observed:
    ident = int(entry["id"])
    commit = commits.get(ident, {})
    key = (commit.get("output"), commit.get("commit_seq"))
    current_scene = scene.get(key, {})
    path = buffers / f"buffer-{ident}.xrgb"
    readable = reads.get(ident, {}).get("status") == "READ" and path.is_file()
    fp = {"id": ident, "read_status": reads.get(ident, {}).get("status", "UNOBSERVED"),
          "direct_available": direct.get(ident, {}).get("available"),
          "source_format": entry.get("dmabuf_format"), "read_format": "DRM_FORMAT_XRGB8888",
          "width": 800, "height": 600, "stride": 3200,
          "state_flags": entry.get("state"), "output_transform": "normal (fixed runner)",
          "source_crop": entry.get("src"), "destination": entry.get("dst")}
    if readable:
        raw = path.read_bytes()
        if len(raw) != 800 * 600 * 4:
            raise ValueError(f"invalid snapshot length for {ident}: {len(raw)}")
        # SceneFX FX glReadPixels rows start at the bottom. DRM XRGB8888 on
        # this little-endian host stores B,G,R,X; normalize top-down RGB.
        rgb = Image.frombytes("RGB", (800, 600), raw, "raw", "BGRX", 0, -1)
        colors = dict((tuple(color), count) for count, color in rgb.getcolors(480001))
        counts = {"A_yellow": colors.get((224, 192, 32), 0),
                  "B_green": colors.get((32, 208, 160), 0)}
        fp.update(raw_sha256=hashlib.sha256(raw).hexdigest(),
                  rgb_sha256=hashlib.sha256(rgb.tobytes()).hexdigest(),
                  byte_count=len(raw), padding_bytes_per_row=0)
        pixels.append({"id": ident, "output": key[0], "commit_seq": key[1],
                       "roi_output_pixels": [0, 0, 800, 600],
                       "scroll": current_scene.get("scroll"),
                       "tile_scene": current_scene.get("tile_scene"),
                       "clip": current_scene.get("clip"), "counts": counts})
        later = buffers / f"buffer-{ident}-present.xrgb"
        if later.exists():
            later_raw = later.read_bytes()
            fp["present_read_sha256"] = hashlib.sha256(later_raw).hexdigest()
            fp["present_read_equal"] = later_raw == raw
    fingerprints.append(fp)
    lifetimes.append({"id": ident, "locked": ident in locked,
                      "present_while_locked": ident in held_present,
                      "release_reason": released.get(ident, {}).get("reason"),
                      "lock_age_ns": released.get(ident, {}).get("age_ns")})
    correlations.append({"id": ident, "output": key[0], "commit_seq": key[1],
                         "accepted": commit.get("accepted") == "1",
                         "same_buffer_in_native_callback": event_buffers.get(ident, {}).get("same") == "1",
                         "native_present": key in presents,
                         "presented": presents.get(key, {}).get("presented"),
                         "read_status": fp["read_status"]})
    scene_states.append({"id": ident, "output": key[0], "commit_seq": key[1], **current_scene})

summary = {"observed_buffers": len(observed), "read_buffers": sum(x["read_status"] == "READ" for x in fingerprints),
           "direct_available": sum(x["direct_available"] == "1" for x in fingerprints),
           "native_commits": len(native_commits), "native_presents": len(native_presents),
           "accepted_sampled": sum(x["accepted"] for x in correlations),
           "same_native_state_buffer": sum(x["same_buffer_in_native_callback"] for x in correlations),
           "sampled_with_present": sum(x["native_present"] for x in correlations),
           "sampled_released": sum(x["release_reason"] is not None for x in lifetimes),
           "released_on_present": sum(x["release_reason"] == "present" for x in lifetimes),
           "superseded_before_present": sum(x["release_reason"] == "superseded" for x in lifetimes),
           "present_while_locked": sum(x["present_while_locked"] for x in lifetimes),
           "second_reads": len(second_reads),
           "second_reads_equal": sum(x.get("present_read_equal") is True for x in fingerprints),
           "runner_failure": json.loads((run / "exit-status.json").read_text()).get("failure")}

build_ns, post_build_to_commit_ns, present_delay_ns = [], [], []
per_output = {}
for stage in stages:
    name, phase = stage.get("output"), stage.get("phase")
    now = int(stage["ns"])
    if phase == "PRE_BUILD":
        per_output[name] = {"pre": now}
    elif phase == "POST_BUILD" and "pre" in per_output.get(name, {}):
        per_output[name]["post"] = now
        build_ns.append(now - per_output[name]["pre"])
    elif phase == "COMMIT_ACCEPTED" and "post" in per_output.get(name, {}):
        post_build_to_commit_ns.append(now - per_output[name]["post"])
for c in native_commits:
    p = presents.get((c["output"], c["commit_seq"]))
    if p:
        present_delay_ns.append(int(p["ns"]) - int(c["ns"]))
summary["timing_median_ns"] = {
    "build": int(statistics.median(build_ns)) if build_ns else None,
    "post_build_to_commit": int(statistics.median(post_build_to_commit_ns)) if post_build_to_commit_ns else None,
    "commit_to_present": int(statistics.median(present_delay_ns)) if present_delay_ns else None,
}
save("commits", native_commits)
save("presentations", native_presents)
save("buffer-lifetime", lifetimes)
save("buffer-fingerprints", fingerprints)
save("scene-states", {"stages": stages, "sampled_commits": scene_states})
save("correlation", correlations)
save("pixel-analysis", pixels)
save("matrix", {"fixed_geometry": "HEADLESS-1 (-800,0), HEADLESS-2 (0,0); 800x600; scale=1; normal",
                "run": run.name, "sampled_snapshots": len(fingerprints),
                "pointer_to_commit_identity": "UNOBSERVED", "physical_presentation": "NOT TESTED"})
save("summary", summary)
print(json.dumps(summary, indent=2))
