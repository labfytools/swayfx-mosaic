# STEP20C mutation coverage fixture — EXPERIMENTAL

The [protocol and findings](../../../docs/design/STEP20C_MUTATION_COVERAGE_PROBE.md)
apply only to a disposable private headless laboratory. This fixture reuses
the frozen applied-state, SceneFX clip, XDG client and pointer fixtures.
It adds one private client patch for a fixed-size recolor and a toplevel
input-region toggle. The runner is generated from the preceding trace-only
runner inside `/tmp`; this repository contains no duplicate compositor or
runner source. Neither private patch is a production dependency.

## Rebuild and targeted replay

```sh
prep=$(sh tooling/probes/step20c-mutation-coverage/prepare.sh)
printf '%s\n' "$prep"
LAB=$(printf '%s\n' "$prep" | sed -n 's/^LAB=//p')
PYTHONDONTWRITEBYTECODE=1 python tooling/probes/step20c-applied-state-input/run.py \
  "$LAB" private_mosaic cycles --cycles 1 --asi-mode 0 \
  --max-seconds 120 --max-captures 40
for mode in control private_standard; do
  PYTHONDONTWRITEBYTECODE=1 python tooling/probes/step20c-applied-state-input/run.py \
    "$LAB" "$mode" cycles --cycles 1 --asi-mode 0 \
    --max-seconds 120 --max-captures 40
done
for mode in control private_standard private_mosaic; do
  for scenario in content input_region; do
    PYTHONDONTWRITEBYTECODE=1 python tooling/probes/step20c-mutation-coverage/run.py \
      "$LAB" "$mode" "$scenario"
  done
done
PYTHONDONTWRITEBYTECODE=1 python tooling/probes/step20c-mutation-coverage/run.py \
  "$LAB" private_mosaic hold_exit
cc -std=c17 -Wall -Wextra -Werror -pedantic \
  tooling/probes/step20c-mutation-coverage/lifetime-model.c \
  -o "$LAB/lifetime-model"
"$LAB/lifetime-model"
PYTHONDONTWRITEBYTECODE=1 python tooling/probes/step20c-mutation-coverage/analyze.py "$LAB"
sha256sum --quiet -c "$LAB/mutation-results/source-sha256.txt"
sha256sum --quiet -c "$LAB/mutation-results/artifact-sha256.txt"
```

Run each case once in a newly prepared lab; the analyzer rejects missing or
ambiguous runs. It writes structured `inventory.json`, `scenario-matrix.json`,
`lifetime.json` and SHA-256 manifests under `LAB/mutation-results/`. Raw
client/compositor logs, exact exit statuses, IPC states and targeted captures
remain under `LAB/runs/`. Only the compositor receives the private SceneFX
library path. Every run has its own mode-0700 runtime and explicit IPC socket;
the previous runner removes it and terminates its process groups.

`hold_exit` is the only B case that takes one extra output-buffer lock and
read. It intentionally retains that lock after a real headless `present`,
then lets normal private compositor shutdown destroy the output. This tests
the actual output-destroy callback once. `lifetime-model.c` is a **synthetic**
C17 state-machine check of the direct rejected-commit unlock and idempotent
destroy release; it does **not** test a wlroots/backend rejected commit.
The latter remains **NOT TESTED**. Normal T1–T5 runs are trace-only.

The fixed output geometry is HEADLESS-1 `(-800,0)` and HEADLESS-2 `(0,0)`,
both 800×600, scale 1, normal transform. The standard controls receive no
Mosaic camera. `grim` captures establish sampled visible pixels, never the
identity of a committed output buffer. Native `(output, commit_seq)` and
headless `present` are correlated separately from actual client input.

## Pinned source-audit input

`prepare.sh` clones wlroots from
`https://gitlab.freedesktop.org/wlroots/wlroots.git` into the **new** lab,
checks out 0.20.2 commit `d783533489e1f75d6886c2ab5c5960090ef268f8`,
and archives it to `LAB/wlroots/`. It verifies SHA-256
`b8c83f292006bc44d349891b1d460245db9dae891e986e6dc2006572f99a7f97`
for `types/scene/surface.c` and
`e73655cc589321f18a824ed4b153c9b1973f9c41a0f8d52b1d380e28a42671cc`
for `types/scene/subsurface_tree.c`. The analyzer hashes these lab-owned files.
The earlier `/tmp/mosaic-wlroots-0202-source/` is not a replay input.
The full wlroots checkout, build products and manifests remain outside Git.
