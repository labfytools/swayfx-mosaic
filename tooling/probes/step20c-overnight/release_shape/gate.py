"""Fail-closed, one-shot gate for the private G release-shape smoke."""
import fcntl
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
OVERNIGHT = REPO / 'tooling/probes/step20c-overnight'
BASE = REPO / 'tooling/probes/step20c-static-e2-completion'
LAB = Path('/home/fy59/swayfx-mosaic-overnight-mcolx0gq')
GROOT = LAB / 'release-shape'
WORK = GROOT / 'smoke'
CASE = 'G-smoke'
BINARY = GROOT / 'stage-static/usr/bin/swayfx-mosaic'
BINARY_SHA = '8063478b2d5948da3eb8b1a329978882dc1d045cf36932cc2145a78af20ba76a'
BUILD_ID = '83896fdb36f3fd21522becec0e8c5219e15f4b8e'
WLROOTS = Path('/usr/lib/libwlroots-0.20.so').resolve()
WLROOTS_SHA = '7edca9a7d65855addda68e29ba5db94d57c803eb5fa7d0f86db3136b90ca9837'
PATCH_SHA = '6e8a5b50149732ac70ecd79ab8db9258956f59036aba1bf17a477866bc44a5c1'
REVIEW = LAB / 'reviews/release-patch-review.json'
REVIEW_SHA = '29e7ea8b9124fae59a231ff6abcab3981e1ac9c697da51c05c334e888970897a'
BUILD_JSON = GROOT / 'results/phase-g-build.json'
PLANS = dict(chain=2, grab=4, click=8, capture=17, camera=2, transition=1, move=10)
# Contract: the move budget counts pointer relocations, including the eight
# click injections; the event trace therefore has only two standalone `move`
# actions plus eight `left`/`right` click actions.

# The three Mosaic source files whose G runtime traces bind the smoke.
TRACE_SOURCES = {
    str(GROOT / 'mosaic-source/sway/desktop/output.c'): 'f703fab0828ee886ce690acfa727a1f70d0dad5f9ec1f5c153db646c73d10485',
    str(GROOT / 'mosaic-source/sway/desktop/transaction.c'): '1bb30b3f171f680f8b2e6ed28aa7aad0a6854d8d77360ac8b8e314918c0982f2',
    str(GROOT / 'mosaic-source/sway/desktop/xdg_shell.c'): '123313e80fbf5d55a8e9bf2edca5a0f15a7601643a5af2904da6ba9b3914d29f',
}

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def read(path):
    return json.loads(Path(path).read_text())

def require(ok, message):
    if not ok:
        raise ValueError(message)

def validate_binary_identity(path, digest):
    require(Path(path).resolve() == BINARY.resolve() and digest == BINARY_SHA and sha(path) == BINARY_SHA, 'only exact G ELF accepted')

def validate_budget_room(state):
    sys.path.insert(0, str(OVERNIGHT))
    import ledger
    ledger._validate(state)
    require(CASE not in state['runs'] and state['used']['run'] < ledger.LIMITS['run'], 'run quota/unique id')
    require(state['campaign_used']['G'] < ledger.CAMPAIGNS['G'], 'G campaign quota')
    require(state['used']['capture'] + PLANS['capture'] <= ledger.LIMITS['capture'], 'global PNG quota')
    require(all(state['used'][k] == ledger.LIMITS[k] for k in ('scene_build','mosaic_build','stage')), 'G smoke must not extend exhausted build/stage budget')

def validate_wlroots(path, digest):
    require(Path(path).resolve()==WLROOTS and digest==WLROOTS_SHA and sha(path)==WLROOTS_SHA, 'wlroots exact bytes')

def validate_file_map(files):
    require(isinstance(files,dict) and bool(files), 'frozen file map missing')
    for path,digest in files.items():
        require(Path(path).is_file() and sha(path)==digest, 'frozen input changed: '+path)

def validate_one_shot(work):
    work=Path(work)
    require(not (work/'run').exists() and not (work/'consumed.json').exists(), 'G smoke is one-shot; no retry')

def validate_capture_batch(work, captures):
    from PIL import Image
    require(len(captures)==17 and len({row.get('file') for row in captures})==17, 'incomplete/duplicate G capture batch')
    expected={'H2-reference-1.png','H2-reference-2.png','E1-top.png','E1-A.png','E1-mosaic-H1.png','E1-mosaic-H2.png','E1-dismissed-H2.png','E2-top.png','E2-A.png','E2-mosaic-H1.png','E2-mosaic-H2.png','standard-H1.png','standard-H2.png','standard-A-H1.png','standard-A-H2.png','final-H2.png','final-H1.png'}
    require({row.get('file') for row in captures}==expected, 'G capture frame set incomplete')
    for row in captures:
        path=Path(work)/'run'/row['file']
        require(path.is_file() and sha(path)==row['sha256'] and row.get('exit')==0, 'G capture bytes changed')
        with Image.open(path) as image: require(image.size==(800,600), 'G capture frame dimensions')

def validate_window_results(work):
    names=('grab-serials.json','xdg-protocol-order.json','popup-root-geometry.json','popup-nested-geometry.json','applied-clips.json','mosaic-pixels.json','standard-return.json','standard-popup-input.json','final-restoration.json','cleanup.json','terminal-exit.json')
    missing=[name for name in names if not (Path(work)/'results'/name).is_file()]
    require(not missing, 'G window/lifecycle evidence incomplete: '+','.join(missing))

def durable(path, data):
    path = Path(path)
    tmp = path.with_name('.' + path.name + '.tmp-' + str(os.getpid()))
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    try:
        with os.fdopen(fd, 'w') as stream:
            json.dump(data, stream, indent=2); stream.write('\n'); stream.flush(); os.fsync(stream.fileno())
        os.replace(tmp, path)
        dfd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try: os.fsync(dfd)
        finally: os.close(dfd)
    finally:
        if tmp.exists(): tmp.unlink()

def exclusive(path, data):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'w') as stream:
        json.dump(data, stream, indent=2); stream.write('\n'); stream.flush(); os.fsync(stream.fileno())
    dfd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    try: os.fsync(dfd)
    finally: os.close(dfd)

def source_bindings(auth):
    rows = auth['trace_sources']
    require(rows == TRACE_SOURCES, 'G source binding set changed')
    require(all(sha(path) == digest for path, digest in rows.items()), 'G source hash changed')
    return {Path(path).name: digest for path, digest in rows.items()}

def _check_build_identity():
    build = read(BUILD_JSON)
    require(build['status'] == 'BUILDABLE', 'G build receipt status')
    require(build['source']['accepted_review'] == 'ACCEPTED', 'G accepted patch review')
    require(build['source']['patch_sha256'] == PATCH_SHA, 'G patch identity')
    require(build['source']['review_json_sha256'] == REVIEW_SHA, 'G review receipt binding')
    require(build['source']['release_manifest_sha256'] == sha(GROOT/'release-manifest.json'), 'G release manifest receipt binding')
    manifest=read(GROOT/'release-manifest.json')
    require(manifest['patch_sha256']==PATCH_SHA and manifest['result_source_hashes'], 'G release manifest identity')
    for rel,digest in manifest['result_source_hashes'].items(): require(sha(GROOT/rel)==digest, 'G release source changed: '+rel)
    require(build['elf']['sha256'] == BINARY_SHA and build['elf']['build_id'] == BUILD_ID, 'G ELF receipt identity')
    require(Path(build['elf']['path']).resolve() == BINARY.resolve(), 'G stage path identity')
    require(build['headless_runtime'] == 'NOT RUN' and build['graphics'] == 'NOT TESTED', 'no inherited G runtime result')
    validate_binary_identity(BINARY, BINARY_SHA)
    readelf = subprocess.run(['readelf', '-n', str(BINARY)], capture_output=True, text=True, timeout=5)
    require(readelf.returncode == 0 and BUILD_ID in readelf.stdout, 'G ELF build ID bytes')
    validate_wlroots(WLROOTS, WLROOTS_SHA)
    review = read(REVIEW)
    require(sha(REVIEW) == REVIEW_SHA and review['status'] == 'ACCEPTED' and review['independent'] is True, 'accepted exact G patch review')
    require(review['patch_sha256'] == PATCH_SHA, 'reviewed G patch digest')
    require(sha(review['report_file']) == review['report_sha256'] == '52e0db6963c44d6e17eab92404c9a882ca03a0bbae9d59ff15c43bdfb0aab0b8', 'accepted patch review report bytes')
    plan=read(LAB/'reviews/release-plan-review.json')
    require(plan.get('status')=='ACCEPTED_PLAN_ONLY' and plan.get('plan_sha256')=='b64201aa3f6a51c385ca8f6934ad20c07ea3853b5a08766e2ae174f5da229547', 'accepted plan binding')
    return build

def _frozen_files():
    freeze = read(WORK / 'freeze.json')
    require(freeze.get('status') == 'READY_FOR_REVIEW' and isinstance(freeze.get('files'), dict), 'G smoke freeze missing')
    files = freeze['files']
    require(files == expected_files(), 'G freeze file set changed')
    validate_file_map(files)
    return freeze

def expected_files():
    """Complete inputs: C2 closure plus G sources/build/patch and fixture code."""
    c2 = read(LAB / 'horizontal/freeze.json')
    rows = dict(c2['files'])
    # Reused runtime modules and their sealed generator/input closure.
    for path in [HERE/'adapter.py', HERE/'gate.py', HERE/'dispatch.py', HERE/'tests.py',
                 HERE/'README.md', HERE/'__init__.py',
                 OVERNIGHT/'horizontal_adapter.py', OVERNIGHT/'horizontal_gate.py',
                 OVERNIGHT/'ledger.py', BASE/'run.py', BASE/'client-contract.json',
                 *(BASE/n for n in ('model.py','observations.py','ipc_predicates.py','pixels.py','predicates.py','lifecycle.py','transition.py','support.py')),
                 WORK/'runner.py', WORK/'results/prepare-tests.json']:
        rows[str(path)] = sha(path)
    # Bind every source input of the G SceneFX and Mosaic trees.
    for root in (GROOT/'scene-source', GROOT/'mosaic-source'):
        for path in root.rglob('*'):
            if path.is_file() and '.git' not in path.parts:
                rows[str(path)] = sha(path)
    fixed = [
        REVIEW, LAB/'reviews/release-patch-review.md',
        GROOT/'release-removal.patch', GROOT/'release-manifest.json',
        LAB/'parent/release-plan.json', LAB/'reviews/release-plan-review.json',
        LAB/'reviews/release-plan-review.md', BUILD_JSON, GROOT/'REPORT-BUILD.md',
        GROOT/'results/static-stage-manifest.json', GROOT/'results/binary-elf.json',
        GROOT/'raw/phase-g-commands.json',
        GROOT/'scene-build/meson-info/intro-buildoptions.json',
        GROOT/'mosaic-build/meson-info/intro-buildoptions.json',
        GROOT/'mosaic-build/meson-info/intro-targets.json',
        LAB/'horizontal/identity.json', LAB/'horizontal/compile.json',
        LAB/'horizontal/protocol-scanner.json', LAB/'horizontal/offline-tests-repair-v1.json',
        LAB/'horizontal/C2/runner.py',
        Path('/usr/lib/libwlroots-0.20.so').resolve(), BINARY,
    ]
    # The offline completion-predicate test consumes this immutable, completed
    # C2 evidence. Freeze the actual events and the records that validate them.
    c2work=LAB/'horizontal/C2'
    c2_evidence=[c2work/'actions.json',c2work/'run/events.jsonl',
        c2work/'results/captures.json',c2work/'results/clicks.json',c2work/'results/runtime.json']
    c2_evidence.extend(c2work/'results'/name for name in (
        'grab-serials.json','xdg-protocol-order.json','popup-root-geometry.json',
        'popup-nested-geometry.json','applied-clips.json','mosaic-pixels.json',
        'standard-return.json','standard-popup-input.json','final-restoration.json',
        'cleanup.json','terminal-exit.json'))
    c2_evidence.extend(c2work/'run'/name for name in (
        'H2-reference-1.png','H2-reference-2.png','E1-top.png','E1-A.png',
        'E1-mosaic-H1.png','E1-mosaic-H2.png','E1-dismissed-H2.png','E2-top.png',
        'E2-A.png','E2-mosaic-H1.png','E2-mosaic-H2.png','standard-H1.png',
        'standard-H2.png','standard-A-H1.png','standard-A-H2.png','final-H2.png','final-H1.png'))
    fixed.extend(c2_evidence)
    fixed.extend(path for info in (GROOT/'scene-build/meson-info',GROOT/'mosaic-build/meson-info') for path in info.iterdir() if path.is_file())
    for path in fixed:
        require(path.is_file(), 'required G freeze input missing: ' + str(path))
        rows[str(path)] = sha(path)
    # Complete DESTDIR identity, including the four separate future notices.
    for path in (GROOT/'stage-static').rglob('*'):
        if path.is_file(): rows[str(path)] = sha(path)
    # Exact C17 fixture binaries and generated protocol sources are also present through C2 closure.
    return dict(sorted(rows.items()))

def verify_review():
    freeze = _frozen_files()
    freeze_sha = sha(WORK/'freeze.json')
    review_path = GROOT/'reviews/release-smoke-review.json'
    require(review_path.is_file(), 'independent G smoke byte review missing')
    review = read(review_path)
    require(review.get('status') == 'ACCEPTED' and review.get('scope') == 'OVERNIGHT_G_SMOKE_FINAL_BYTES', 'G smoke review scope/status')
    require(review.get('independent') is True and review.get('read_only') is True and review.get('blockers') == [], 'G smoke review independence/blockers')
    require(review.get('freeze_sha256') == freeze_sha and review.get('files') == freeze['files'], 'G smoke review bindings')
    require(Path(review['report_file']).is_file() and sha(review['report_file']) == review['report_sha256'], 'G smoke report bytes')
    return review

def preflight(require_review=True):
    require(sys.flags.optimize == 0, 'assertions disabled')
    require(LAB.is_dir() and LAB.stat().st_uid == os.getuid() and stat.S_IMODE(LAB.stat().st_mode) == 0o700, 'registered owned LAB mode')
    require(WORK.is_dir() and WORK.stat().st_uid == os.getuid(), 'G smoke workspace owner')
    validate_one_shot(WORK)
    require((WORK/'results').is_dir(), 'G results directory')
    require((WORK/'results/clients').is_symlink() and (WORK/'results/clients').resolve()==(LAB/'horizontal/clients').resolve(), 'results client link changed')
    for name in ('nested-client','pointer-daemon','static-reference'):
        p=WORK/name
        require(p.is_symlink() and p.resolve()==(LAB/'horizontal/clients'/name).resolve(), 'C2 client symlink changed: '+name)
    for proc in Path('/proc').iterdir():
        if proc.name.isdigit():
            try: exe=(proc/'exe').resolve(strict=True)
            except (FileNotFoundError, PermissionError, ProcessLookupError): continue
            require(exe != BINARY.resolve(), 'G binary already running')
    build = _check_build_identity()
    sys.path.insert(0, str(OVERNIGHT)); import ledger
    validate_budget_room(read(LAB/'budget.json'))
    freeze = _frozen_files()
    # Refuse inherited A bytes and any other ELF even if it is executable.
    require(freeze['files'].get(str(BINARY)) == BINARY_SHA, 'G ELF absent from freeze')
    require(all(sha(path)==digest for path,digest in TRACE_SOURCES.items()), 'G runtime sources changed')
    from adapter import generate_g
    require((WORK/'runner.py').read_text() == generate_g(), 'generated G C2 runner changed')
    if require_review: verify_review()
    return dict(binary=str(BINARY), binary_sha256=BINARY_SHA, build_id=BUILD_ID,
        wlroots_sha256=WLROOTS_SHA, trace_sources=TRACE_SOURCES,
        pristine=dict(path=str(LAB/'stage-static/usr/bin/swayfx-mosaic'), sha256='979dcd95ab43fa1e465d6e9d262485b73d186cedacd0f957059dd24f482ce6f4'))

def begin_run():
    auth = preflight(require_review=True)
    token = WORK/'consumed.json'
    exclusive(token, dict(case=CASE, freeze_sha256=sha(WORK/'freeze.json'), consumed_at_ns=time.time_ns()))
    # The durable unique token comes before the locked global ledger reservation.
    sys.path.insert(0, str(OVERNIGHT))
    import ledger
    ledger.reserve(LAB/'budget.json', 'run', campaign='G', run_id=CASE, duration_s=150)
    exclusive(WORK/'actions.json', dict(planned=PLANS, reserved=dict.fromkeys(PLANS,0), events=[]))
    return LAB, CASE, WORK, auth

def debit(lab, case, work, *kinds):
    require(Path(lab).resolve()==LAB and case==CASE and Path(work).resolve()==WORK, 'G action binding')
    require(kinds and all(k in PLANS for k in kinds), 'unknown G action')
    lockpath=WORK/'actions.lock'
    with lockpath.open('a+') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        state=read(WORK/'actions.json')
        require(state.get('planned')==PLANS and set(state.get('reserved',{}))==set(PLANS), 'G action ledger schema')
        require(len(state.get('events',[]))==sum(state['reserved'].values()), 'G action ledger count mismatch')
        require(dict(Counter(e.get('kind') for e in state['events']))=={k:v for k,v in state['reserved'].items() if v}, 'G action event/count mismatch')
        for i,event in enumerate(state['events']):
            require(event.get('sequence')==i and event.get('kind') in PLANS and type(event.get('ns')) is int, 'G action event schema')
        require(all(state['reserved'][k]+kinds.count(k)<=PLANS[k] for k in kinds), 'G local action quota')
        for kind in kinds:
            if kind=='capture':
                sys.path.insert(0,str(OVERNIGHT));import ledger
                ledger.reserve(LAB/'budget.json','capture',run_id=CASE)
            state['reserved'][kind]+=1
            state['events'].append(dict(sequence=len(state['events']),kind=kind,ns=time.monotonic_ns()))
        durable(WORK/'actions.json',state)

def binding_sources(auth):
    require(auth['binary']==str(BINARY) and auth['binary_sha256']==BINARY_SHA, 'G binary source binding')
    return source_bindings(auth)

def finish_predicate(state, events, captures, clicks, runtime, capture_ok, window_ok):
    """Evaluate the real completion gate over recorded action and runtime evidence."""
    counts=dict(Counter(e.get('kind') for e in state.get('events',[])))
    ledger_ok=(state.get('planned')==PLANS and set(state.get('reserved',{}))==set(PLANS)
        and counts=={k:v for k,v in state.get('reserved',{}).items() if v}
        and all(type(v) is int and 0<=v<=PLANS.get(k,-1) for k,v in state.get('reserved',{}).items()))
    event_capture_ok=sum(e.get('kind')=='capture' for e in events)==PLANS['capture']
    injections=[e for e in events if e.get('kind')=='injection']
    click_actions=[e for e in injections if e.get('action') in ('left','right')]
    standalone_moves=[e for e in injections if e.get('action')=='move']
    injection_ok=(len(injections)==PLANS['click']+2
        and len(click_actions)==PLANS['click']
        and len(standalone_moves)==2
        and len(click_actions)+len(standalone_moves)==len(injections))
    grabs=sum(e.get('grab') is True for e in injections)
    complete=(ledger_ok and state.get('reserved')==PLANS and capture_ok and window_ok
        and event_capture_ok and injection_ok and grabs==PLANS['grab']
        and len(clicks)==PLANS['click'] and runtime.get('status')=='PASS')
    return dict(complete=complete, action_ledger_valid=ledger_ok,
        event_capture_count_valid=event_capture_ok, injections=len(injections),
        click_injections=len(click_actions), standalone_move_injections=len(standalone_moves),
        pointer_counts_valid=injection_ok, grabs=grabs)

def finish_run(lab, case, work):
    verify_review()
    require(Path(lab).resolve()==LAB and case==CASE and Path(work).resolve()==WORK, 'G finish binding')
    state=read(WORK/'actions.json')
    events_path=WORK/'run/events.jsonl'
    events=[json.loads(line) for line in events_path.read_text().splitlines()] if events_path.is_file() else []
    captures=read(WORK/'results/captures.json') if (WORK/'results/captures.json').is_file() else []
    clicks=read(WORK/'results/clicks.json') if (WORK/'results/clicks.json').is_file() else []
    runtime=read(WORK/'results/runtime.json') if (WORK/'results/runtime.json').is_file() else {'status':'INCONCLUSIVE','failure':'runtime result missing'}
    try: validate_capture_batch(WORK,captures);capture_ok=True
    except Exception: capture_ok=False
    try: validate_window_results(WORK);window_ok=True
    except Exception: window_ok=False
    predicate=finish_predicate(state,events,captures,clicks,runtime,capture_ok,window_ok)
    observed=dict(status='PASS' if predicate['complete'] else 'INCONCLUSIVE', runtime=runtime,
        planned=PLANS, reserved=state.get('reserved'), action_ledger_valid=predicate['action_ledger_valid'],
        captures=len(captures), capture_bytes_valid=capture_ok, event_capture_count_valid=predicate['event_capture_count_valid'],
        clicks=len(clicks), injections=predicate['injections'], click_injections=predicate['click_injections'],
        standalone_move_injections=predicate['standalone_move_injections'], grabs=predicate['grabs'],
        pointer_counts_valid=predicate['pointer_counts_valid'],
        window_evidence_complete=window_ok,
        measurement_event=any(e.get('kind')=='measurements-completed' and e.get('status')=='PASS' for e in events))
    durable(WORK/'finish.json',observed)
    return observed
