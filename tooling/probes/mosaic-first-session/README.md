# First physical session: passive preparation

EXPERIMENTAL / PHYSICAL_NOT_RUN. These tools create private evidence only.
They do not execute a compositor, use IPC, start/stop/reload a service, select a
session, deploy files, or change default-id. Production STEP20C remains NEXT.
The installed guard is trusted audited Python source, imported without `main`;
this is not a sandbox for arbitrary Python supplied as a guard.

From this directory, pass the actual installed paths as local arguments:

```sh
PYTHONDONTWRITEBYTECODE=1 MOSAIC_INSTALLED_GUARD="$GUARD" \
  python -B -m unittest -v test_prepare.py
python -B prepare.py --guard "$GUARD" --source-kit "$SOURCE_KIT" \
  --repo "$REPOSITORY" --protect "$HOME/.zprofile"
```

`GUARD`, `SOURCE_KIT` and `REPOSITORY` must be set explicitly to audited local
inputs. Missing UWSM, a changed binary/provider/manifest, unsafe files or a
non-Stable preference cause refusal. No launch command is exposed by the CLI.
Repeated preparation creates a new mode0700 directory under `/var/tmp`.

The private LAB contains mode0400 snapshots of every installed manifest file,
the manifest itself, original binary, library provider, canonical default-id,
source fixtures and optional protected files. Symlink text and owner, canonical
file owner, mode, size and SHA256 are recorded; the existing selection symlink
is validated by the original guard. Before/after receipts compare those values.
Only optional `--protect` files beyond the installed manifest are covered;
this is not a snapshot of all personal configuration or filesystem metadata.
Timestamps and inode identity are not a concurrent filesystem snapshot claim.
No file is installed from this archival copy; the desktop entry still uses the
original helper and binary. Provenance and diff against local `origin/main`
remain private. Untracked source is preserved through separately copied source
fixtures; `git diff` alone does not include untracked files.

`MANUAL.txt` contains the exact explicit UWSM launch and independent TTY recovery
commands for later separate approval. It is text, not an executable script.
Recovery requires Stable and other WM instances inactive before stopping only
the exact Mosaic instance, then all WM instances inactive before explicit Stable
start. No Kitty, IPC socket, preference rewrite or global process kill is needed.
Physical VT/PAM, DRM, eDP-1, seat0, input and actual recovery remain NOT TESTED.

Tests use actual installed context/file validation with synthetic arguments.
The repaired launch tests call the actual `launch` with filesystem observations,
context, chdir and exec intercepted; they never execute a compositor. They do
not call `arm`, `stable`, `main` or IPC. Scratch files
live in fresh private temporary directories. A valid simulated context proves
only the guard predicate, never actual logind or hardware admission.


The audited installed guard has a confirmed quoted-Conflicts decoding defect.
`repair.py --guard "$GUARD" --lab "$LAB"` stages only its exact SHA256 preimage
repair plus the corresponding manifest hash in a fresh exclusive subdirectory
of an existing owned mode0700 LAB. It retains rollback originals, exact private
diff, old/new hashes and original deployment modes. Candidates are mode0400;
there is no installation function. Changed preimages, missing manifest anchors
and repeated staging into the same subdirectory are refused. The manifest
changes only the session.py hash. Binary/provider identities remain unchanged.
One final conversational approval must explicitly cover installing both
session.py and manifest.json and the subsequent bounded physical trial.
Verify the approved hashes and loaded isolation after deployment and before
starting that approved trial. In the completed local preparation,
APPROVAL-AND-TRIAL.txt supersedes the earlier sealed manuals, including
MANUAL-final.txt, and includes the exact two-file deployment/rollback plan.
Until deployment, the private module's unmocked
verify_files authenticates the installed original, not the staged candidate.
The exact installed guard and its local inputs are required to reproduce these
tests; the repository alone is not a self-contained physical session kit.
