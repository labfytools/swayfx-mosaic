# First physical Mosaic session — experimental contract

Verdict: **MOSAIC_PHYSICAL_SESSION_READY_FOR_EXPLICIT_APPROVAL**.
State: **PHYSICAL_NOT_RUN / REPAIR_NOT_INSTALLED**. This is a short,
voluntary, single-output trial, not production qualification or STEP20C closure.
STEP20A DONE; STEP20B EXPERIMENTAL; STEP20C NEXT; STEP20D–G PLANNED.
Production multi-output remains NOT_YET_SUPPORTED.

## Accepted scope

READY_FOR_APPROVAL means the retained CORE-C V2 identity, installed dedicated
session entry, staged guard correction, service isolation, offline refusals
and manual TTY procedure have been checked. It includes the explicit future
two-file deployment decision below; it does not claim deployment is complete.
It does not prove GPU, seat0, DRM, eDP-1, input,
physical VT switching or actual recovery. Those remain PHYSICAL_NOT_RUN.

Use the existing experimental session and binary. Preserve Stable, the greeter,
all personal configuration and `default-id = sway.desktop`. No compositor
execution, including `--version`, config validation or headless startup, is
authorized during this preparation. Keep copies, receipts and logs in a new
private mode0700 LAB; no private paths, personal identifiers or raw logs in Git.

## Guard repair prepared before approval

A read-only check exposed a real pre-launch refusal in the installed guard:
systemd 262 quotes and escapes an autostart unit in its `Conflicts` property;
plain whitespace splitting does not recover the unit name. The required
exclusion is present, but the old predicate reports it missing. This is an
offline preparation defect, not evidence of a physical compositor failure.

The smallest correction uses `shlex.split()` to decode the quoted word list
without executing a shell; all required exclusions must still be present.
The [source-only tool](../../tooling/probes/mosaic-first-session/README.md)
prepares it and the updated integrity manifest privately.
Before approval, do not install either file. The exact local diff must be
reviewable; the requested future write set is limited to the dedicated
`session.py` and `manifest.json` in the existing Mosaic test configuration
directory. No entry, config, unit, greeter or preference change is needed.
Do not attempt the trial with the uncorrected guard. Approval must cover these
two file replacements as well as the physical trial; retain checked originals
for rollback. The normal session keeps using the retained original CORE-C V2
binary; the new LAB's binary copy is a non-executable archive, not a deployment.

## Shortest accepted login path

After separate conversational approval, installation/check of the reviewed
guard repair and voluntary logout from Stable, use authenticated TTY2 on
seat0. Cancel any personal login compositor menu to reach a shell (the retained
menu replay uses Tab, Tab, Enter for Cancel); then `exec /usr/bin/zsh -f`.
Before starting, open and verify a second authenticated recovery shell on TTY3,
then return to TTY2. Cancel if that console cannot be reached. Keep both logins
alive. Check `default-id` still says `sway.desktop` and inspect:

```sh
/usr/bin/systemctl --user list-units 'wayland-wm@*.service' --all --plain --no-pager
```

With every WM inactive (none active, activating or deactivating), run:

```sh
/usr/bin/uwsm start -- swayfx-mosaic-test.desktop
```

Installed UWSM supports an explicit desktop entry ID; only its special `default`
and `select` paths resolve or save the preference. Keep the login alive while
the session runs. Do not use the existing `arm` helper. The current greeter
starts `uwsm start default` and has no Stable/Mosaic selector.

## Planned trial, three to five minutes

On eDP-1 only, verify French keyboard and pointer. In the recovery Kitty, run
the existing dedicated `inspect-session.py` first: it verifies the exact
process/binary/provider and socket owner before any explicit Mosaic IPC. On
success only, set standard layout with `swaymsg -s "$SWAYSOCK" layout splith`.
Start in standard `splith`,
open at least five light Kitty windows if necessary for horizontal overflow,
toggle with Super+Alt+L, focus with Super+arrows and scroll with
Super+Ctrl+Left/Right. Check basic floating, close a window and toggle back to
standard. Basic floating uses `swaymsg -s "$SWAYSOCK" floating toggle` twice
on the focused window, after that same identity check; no floating shortcut
is installed. Super+Return opens Kitty; Super+Shift+Q closes a client.
The existing Super+Shift+E binding invokes native `exit`; prefer the ordered
unit stop below for normal trial exit, as recommended by installed UWSM.
Super alone never moves windows.

## Manual independent recovery

If there is no image, Kitty or IPC socket, switch to the already verified TTY3.
Inspect UWSM units with the list command above. If Stable or another WM is
active, activating or deactivating, do not stop anything or start another WM.
If only Mosaic remains, stop only its exact instance:

```sh
/usr/bin/systemctl --user stop 'wayland-wm@swayfx\x2dmosaic\x2dtest.desktop.service'
```

Wait for completion and inspect units again. Only when every WM is inactive,
target Stable explicitly (also works after failure before any socket exists):

```sh
/usr/bin/uwsm start -- sway.desktop
```

Read the saved preference before restart; it must still be `sway.desktop`.
If it differs, cancel and investigate; this mission never arms Mosaic. The
existing manual Stable preference helper is independent of the binary/LAB but
writes the preference, so reserve it for a separately acknowledged anomalous
selection recovery. Explicit Stable start bypasses the preference entirely.
Never kill the user manager or stop a wildcard target. A failed context check,
lingering stop, unavailable recovery console or identity mismatch is grounds
to cancel. Actual VT/PAM and physical crash recovery remain NOT TESTED.

## Out of scope

Multi-output, complete clipping/damage/lifetime guarantees, GPU G4, advanced
fullscreen, greeter V3B, production installation, QuickShell integration and
personal bindings deployment are excluded. The headless UDMABUF/namespace
failure is separate evidence, not a proven failure of the physical DRM path.

## Validation and handoff

The retained binary is CORE-C V2 SHA256
`91f48aae2675331e0a2c60ec2fedf983745c521c75232c704a6516a4140801fb`,
Build ID `d5d304533f2c8db9d738365e9bd7f2c96779ef8d`. It has no SceneFX
DT_NEEDED or RPATH/RUNPATH. The exact wlroots 0.20.2 provider SHA256 is
`7edca9a7d65855addda68e29ba5db94d57c803eb5fa7d0f86db3136b90ca9837`.
Local versions: UWSM 0.27.1-1, SwayFX 0.6-1, SceneFX 0.5-1, Kitty 0.49.2-1,
systemd 262-1. These facts do not qualify a different dependency build.

The prepared guard SHA256 is
`34198274977204e365f4d7b092e9dc96bdc18d5b8027f6677ae47b1d3fe02799`;
its manifest SHA256 is
`2fdecc1a1be0bc1a009ed8854d116ce22b99c71596729e746ad8f0920e35bcc2`.
Only that guard's digest changes inside the manifest. Both installed files
remain unchanged; their existing mode0600 must be retained on future deployment.
Private receipts preserve original bytes, exact diff, old/new SHA and rollback.
An interrupted two-file deployment must be repaired or rolled back before
launch; there is no claim of an atomic transaction spanning both files.

Independently rerun targeted evidence: 24 inert tests pass against actual guard code,
including repaired launch with every effect intercepted, missing exclusions,
malformed quotes, fake seat, wrong cgroup, inherited IPC, concurrent WM,
missing UWSM and changed binary. Eighteen retained guard/selection tests and
two real UWSM/whiptail PTY replays pass in a shadow environment with all starts
intercepted. The selection test writes only its shadow preference. Thirty-two
audited input files and the selection symlink remain unchanged. `session.py
check`, ELF relocations and private copy identity pass. Current static config
inspection verifies eDP-1, bindings, no include, Xwayland/effects disabled;
native config parsing is NOT_RUN. No full grammar validation is claimed.
Both installed UWSM `start -n -- <explicit-entry>` simulations pass without
unit writes/start/reload, reporting `Units unchanged`; the active Stable PID
and activation timestamp remain unchanged. AST, local documentation links
and `git diff --check` pass. Independent bounded delta review is ACCEPTED.

Validator invocation errors are retained: the imperative PTY replay has no
unittest cases (runner exit5); its proper script entry point passes both cases.
An initial relocation command used an incorrect guessed path; the manifest's
actual binary path passes `ldd -r`. Neither failure is a native compositor run.
The parent's first final unittest invocation omitted the mandatory
`MOSAIC_INSTALLED_GUARD` input and failed setup without running tests; the
corrected explicit-input command passes all 24 tests.
The original quoted-Conflicts predicate FAIL remains documented above; only
the privately staged correction passes its corresponding offline predicate.

Independent final audit is PASS / ACCEPTED with no blocking finding.
The final local handoff is `APPROVAL-AND-TRIAL.txt`, superseding earlier sealed
manuals, and includes the precise two-file deployment/rollback plan. These
tests require the audited installed guard and local inputs; this repository
alone is not a self-contained physical session kit. Private LAB location,
exact local commands, final check receipts and publication refs belong to the
local handoff, not public logs. No physical session is authorized by READY;
actual login/input/return and all visual trial cells are NOT TESTED.

After a future failure, collect at most 80 journal entries for the exact Mosaic
unit into the private LAB, plus its bounded exit receipt; do not publish raw
logs. Main risks are untested physical DRM/input/VT recovery, temporary LAB or
dependency identity drift, and remaining experimental Mosaic rendering/input
limitations. Cancel on a black screen, failed input or identity/context refusal;
use the independent recovery console rather than weakening a guard.
