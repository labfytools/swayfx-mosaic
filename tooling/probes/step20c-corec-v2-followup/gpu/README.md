# GPU-G3 — private GLES admission follow-up

EXPERIMENTAL_SOURCE_ONLY. This kit derives a new diagnostic from the published
[G2 sources](../../step20c-corec-v2/gpu/README.md). It carries no G2 binary or
runtime qualification. B4 is INCONCLUSIVE until an independent reviewer accepts
the exact final bytes and receipts. Compositor build, staging and native GPU
run are NOT_RUN. STEP20C remains NEXT; production multi-output is
NOT_YET_SUPPORTED and PRODUCTION_AUTHORIZED is FALSE.

## Normative basis and bounded contract

[EGL 1.5](https://registry.khronos.org/EGL/specs/eglspec.1.5.pdf),
§3.7.1.1, printed pp52–53 (PDF pages58–59), permits a later backwards compatible
context. Its footnote18 identifies CLIENT_VERSION as the major-version alias.
However §3.7.4, printed p63 (PDF page69), describes the context query as the
supported client version. Thus EGL2/GL3.2 remains an observed divergence; this
kit does **not** relabel the queried EGL value as merely a creation request or
assert universal conformance. The independent reviewer must assess the limited
diagnostic admission separately from that divergence.

[OpenGL ES 3.2, May 5 2022](https://registry.khronos.org/OpenGL/specs/es/3.2/es_spec_3.2.pdf),
§20.2, printed pp441–442 (PDF pages458–459), specifies the VERSION string and
matching MAJOR_VERSION/MINOR_VERSION queries. The code first validates current
EGL context/display and ES API, then bounded GL_VERSION attesting ES3.0–3.2,
then these ES3 queries and GLSL string without errors. ES2, ES4, unqualified
ES3 minors, forged framing and contradictory integer results are refused.
Installed headers define EGL_CONTEXT_CLIENT_VERSION and MAJOR_VERSION as
0x3098; GLES3 MAJOR_VERSION/MINOR_VERSION are 0x821b/0x821c. Their hashes are
recorded in the offline receipt; headers alone prove no native capability.

`g2_gl.h` keeps the exact `g2_read` symbol used by the unchanged G2 hooks.
`g2_native.h` adds observable lifecycle flags and G3 metadata. Queries consume
the GL error queue in separate pre/version/capability/state/attachment/read/
restore windows. Error consumption cannot be restored. State is null when
unobserved; attempted restoration requires a clean error window and exact
state/context/display/API equality. Bindings restored are READ/DRAW FBO, RBO,
PBO and PACK alignment/row/skip. READ_BUFFER is observed on the target and is
never modified; returning the original FBO restores its original selection.
Other queried state is unchanged. Only complete, single-sample native RBO
color attachments with supported byte channels/dimensions are read. Texture
attachment dimensions remain NOT_PROVEN and are refused. Black RGBA with
alpha zero is valid. Functional blur shaders, sampler and rendering policy
are unchanged. GLSL string is evidence about the implementation; the linked
program's mediump/ESSL100 requirements remain tied to frozen shader sources,
actual program/type/location, precision capability and uniform bits.

DMA-BUF FDs are borrowed and fstat identities are recorded without closing,
seeking or decoding. AMD modifier020000001046bb04 accepts image stride3584
offset0 and auxiliary stride1024 offset2293760. Only the image plane requires
width×4; auxiliary allocation bounds/decoding remain NOT_PROVEN. Unknown
modifiers are refused. `halfpixel` records native bits and capability; there
is no fitted tolerance or mandatory CPU-float32 equality for mediump.

## Source reconstruction and offline commands

Start with the [CORE assembler](../../step20c-corec-v2/README.md) from a fresh
Git extraction and its verified 85-file SceneFX tree. Use a NEW LAB created by
mkdtemp under `/var/tmp/swayfx-mosaic-step20c-native-closure-*`, UID owner,
mode0700. All generated files and every temp/cache directory stay there.
Run commands with an allowlisted environment, for example:

```sh
env -i PATH=/usr/bin:/bin LANG=C.UTF-8 \
  TMPDIR="$LAB/scratch" TMP="$LAB/scratch" TEMP="$LAB/scratch" \
  XDG_CACHE_HOME="$LAB/cache" XDG_DATA_HOME="$LAB/data" \
  PYTHONPYCACHEPREFIX="$LAB/pycache" CCACHE_DIR="$LAB/ccache" \
  python "$KIT/reproduce.py" --lab "$LAB" --core "$CORE/scene" \
  --destination "$LAB/replay-g3-scene"
```

Create the listed environment directories first, mode0700. `$KIT` is this
directory, `$CORE` the verified assembler destination. `reproduce.py` verifies
every CORE byte and mode against the versioned provenance. It applies the
relative parent kit's `gpu/g2-native.patch` with fixed SHA256
77d7445ceaf643fd5cc708d31c3f2c77feaeb80f8130c419c55e5514ecc8a75d, then applies the G3 delta and verifies both diagnostic headers against
the supplied full new headers. The hook source SHA remains
c2886ef259fc91431dfe97841387082420ab80a0fe2f07e7dcdb71fc95731181.
`g3-admission.patch` is the review delta between the parent and new headers;
full new headers are the assembly authority and are explicitly frozen.

With the same allowlisted environment, run:

```sh
python "$KIT/test-targeted.py" --lab "$LAB" --scene "$LAB/replay-g3-scene"
python "$KIT/freeze.py" --lab "$LAB" --output "$LAB/g3-source-freeze-v2.json"
```

This performs C17 FakeGL execution of the exact header, controlled wrong
native variants, exact arm-consumer C extraction, actual native helper C,
Python parser/scenario negative tests, source syntax checking, Wayland header
generation and client syntax compilation. The client is not executed. It
does not require compile_commands from any historical LAB. C processes set
RLIMIT_CORE=0 and PR_SET_DUMPABLE=0. Generated tests, logs and receipts remain
under `LAB/g3-offline`; the relative source manifest is
`LAB/g3-source-freeze.json`. The freezer never grants its own review.

## Prospective native wiring — requires parent admission

Define `G3_ROOT` at compile time as the reviewed new LAB's exact
`gpu-work/acquisition` path. There is deliberately no default absolute LAB.
That definition is part of the new binary's reviewed identity. The C hook
requires MOSAIC_G3_DIR to equal both the macro and realpath, mode0700. Python
ROOT comes from MOSAIC_G3_DIR supplied **before import** and verifies the new
LAB prefix. No runtime directory is created by this kit.

The parent must bind `scenario.run(session,binding)` to a **GPU-G3** Session
whose sockets, binary/maps, watchdog, capture limits and durable ledger have
been independently reviewed. `binding` requires `G3_ledger_reserved=True`,
gate_file, binary, client, client_sha256, nonce and source_manifest_sha256.
The Session binary category is `gpu` and its actual executable must be the
new reviewed G3 binary. Environment variables MOSAIC_G3_DIR/NONCE belong in
the Session's explicit compositor allowlist. The caller owns finally/cleanup.
The parent must provide a gate mode0600 containing source_review=ACCEPTED,
gl_observability=PASS, runtime_authorized=true, diagnostic=GPU-G3,
acquisition_root, and exact binary_sha256. This kit never produces that gate.

Epochs A/B/A-return are single use, strictly ordered, capped at three. All
ten physical readbacks per epoch are full800×600 RGBA (the prospective ROI is
the complete field, without a post-hoc mask), total57,600,000 bytes, cap256MiB.
There are two H2 baselines then three H1/H2 pairs: eight output captures.
Every arm/raw/metadata publication is exclusive, nofollow and bounded.
Rejected/incomplete A forbids B and return. Input commands are G3-A/G3-B/
G3-A-return; client content is the unchanged alternating 8-pixel RGB pattern.
Whole H1/H2 comparisons report zero-tolerance differences and row counts.
Synchronous reads may perturb timing; GPU completion, presented-buffer
identity, object lifetime, complete damage, atomic generation and whole-field
causality remain NOT_PROVEN. A future build/run requires B4 and C gates;
offline success does not consume or authorize a GPU-G3 run. The freezer's
default output name is `g3-source-freeze.json`; it creates a new mode-0600 file
exclusively, refuses any existing destination, and syncs the file and LAB
directory. Use a new explicit direct-child name for every later freeze; a prior
freeze is immutable evidence.
