#!/usr/bin/env python3
"""Offline transfer and strict preflight around the unchanged historical gate.

WHY: offline acceptance does not authenticate missing runtime installation data.
CONTRACT: historical bytes remain read-only; only new transfer records are made.
INVARIANT: checks create no socket, process, runtime directory or budget debit.
"""
import ast
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
OLD_FIXTURE = REPO / 'tooling/probes/step20c-static-nested-geometry-replay'
OLD_LAB = Path('/home/fy59/swayfx-mosaic-receipt-integrity-cof0umuk')
TICKET = 'SWAYFX_MOSAIC_STEP20C_RECEIPT_FREEZE_AND_STATIC_NESTED_RUNTIME_V1'
REGISTRY = Path('/home/fy59/swayfx-mosaic-static-nested-runtime-v1.owner')
REGISTRATION = REGISTRY.with_suffix('.registration.json')
AMENDMENT = REGISTRY.with_suffix('.registration-amendment.json')
SPENT = REGISTRY.with_suffix('.launch-consumed.json')
BINARY = Path('/home/fy59/swayfx-mosaic-static-runtime-hm5kbdkt/stage-static/usr/bin/swayfx-mosaic')
BINARY_SHA = 'f82557c1a9978a5e9665b9b4291b74880253725359e3df1c5b8d554921f7603b'
BUILD_ID = '942db64269640778ee433e5970ba1100bc60f94c'
WLROOTS = Path('/usr/lib/libwlroots-0.20.so')
WLROOTS_SHA = '7edca9a7d65855addda68e29ba5db94d57c803eb5fa7d0f86db3136b90ca9837'
SEALS = {'source-sha256.txt': (76, 'dbd96db3f19f6eb60fc8be13c62b1e71944a759b481d008a7825b3720cf525ce'),
         'evidence-sha256.txt': (199, 'f00ca54e39bff031a5bda585ea52cfebe9239e71b4c7ee7dc5c41a930e1598b3')}
REPORT_SHA = '311af1fe694d1bde88884afa21ef16a4fe908d6cfa47b6cbed515d1a21fedc9e'
REVIEW_SHA = '4d8401978e69a6c54f2f6144ba06deff4952671bc8e1ae3008376ab6ffe01e09'
sys.path.insert(0, str(OLD_FIXTURE))
from authorization import authorize, MARKER
from ledger import LIMITS, valid
from support import environment, sha, verify
from write_results import REQUIRED, aggregate
from receipt_integrity import make_bindings


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    return json.loads(Path(path).read_text())


def exclusive(path, data, mode=0o600):
    """File and parent fsync precede use; existing ownership is never overwritten."""
    path = Path(path)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, mode)
    with os.fdopen(fd, 'w') as out:
        out.write(data if isinstance(data, str) else json.dumps(data, indent=2) + '\n')
        out.flush()
        os.fsync(out.fileno())
    fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def regular(path, mode=None):
    path = Path(path)
    info = path.lstat()
    need(stat.S_ISREG(info.st_mode) and info.st_uid == os.getuid(), 'unsafe-owned-file: ' + str(path))
    if mode is not None:
        need(stat.S_IMODE(info.st_mode) == mode, 'file-mode: ' + str(path))


def accepted():
    """Revalidate real file-backed bindings with the actual accepted aggregate."""
    manifests = {}
    for name, (count, digest) in SEALS.items():
        p = OLD_LAB / 'results' / name
        need(sha(p) == digest, 'historical-manifest-identity')
        observed = verify(p)
        need(observed['entries'] == count, 'historical-manifest-count')
        manifests[name] = observed
    need(sha(OLD_LAB / 'independent-review.md') == REPORT_SHA, 'historical-report-identity')
    need(sha(OLD_LAB / 'results/independent-review.json') == REVIEW_SHA, 'historical-review-identity')
    evidence = {n: read(OLD_LAB / 'results' / (n + '.json')) for n in REQUIRED}
    evidence['independent-review'] = read(OLD_LAB / 'results/independent-review.json')
    bindings = make_bindings(evidence, {n: OLD_LAB / 'results' / (n + '.json') for n in REQUIRED})
    need(bindings == read(OLD_LAB / 'results/review-bindings.json'), 'accepted-bindings')
    for name, digest in bindings['source_delta'].items():
        need(sha(OLD_FIXTURE / name) == sha(OLD_LAB / 'proposed-fixture' / name) == digest, 'accepted-source: ' + name)
    gates = aggregate(evidence, sha, bindings)
    need(gates['status'] == 'READY_FOR_NEW_RUNTIME' and not gates['blockers'] and
         len(gates['markers']) == 5 and set(gates['markers'].values()) == {'PASS'}, 'accepted-aggregate')
    ready = read(OLD_LAB / 'results/offline-gate.json')
    need(ready['status'] == 'READY_FOR_NEW_RUNTIME' and ready['marker'] == MARKER and
         ready['review_bindings'] == bindings and not ready['blockers'] and ready['markers'] == gates['markers'], 'historical-READY')
    return dict(manifests=manifests, bindings=bindings, aggregate=gates,
                report_sha256=REPORT_SHA, review_sha256=REVIEW_SHA, historical_lab=str(OLD_LAB))


def copy_exact(source, destination):
    source, destination = Path(source), Path(destination)
    need(source.is_file() and not source.is_symlink(), 'copy-source-regular')
    with source.open('rb') as src, destination.open('xb') as dst:
        shutil.copyfileobj(src, dst)
        dst.flush()
        os.fsync(dst.fileno())
    destination.chmod(stat.S_IMODE(source.stat().st_mode))
    need(sha(source) == sha(destination), 'copy-identity')
    return dict(source=str(source), destination=str(destination), sha256=sha(source))


def run_command(lab, label, argv):
    result = subprocess.run(list(map(str, argv)), env=environment(), capture_output=True, text=True, timeout=30)
    exclusive(lab / 'raw' / (label + '.json'), dict(argv=list(map(str, argv)), exit_code=result.returncode,
                                                stdout=result.stdout, stderr=result.stderr))
    need(result.returncode == 0, 'preparation-command: ' + label)
    return result.stdout


def prepare():
    proof = accepted()
    need(not REGISTRY.exists() and not REGISTRATION.exists() and not AMENDMENT.exists() and not SPENT.exists(), 'ticket-already-registered')
    need(not BINARY.is_symlink() and sha(BINARY) == BINARY_SHA and
         stat.S_IMODE(BINARY.stat().st_mode) == 0o755 and sha(WLROOTS) == WLROOTS_SHA, 'binary-and-wlroots-before-copy')
    lab = Path(tempfile.mkdtemp(prefix='swayfx-mosaic-static-nested-runtime-', dir='/home/fy59'))
    lab.chmod(0o700)
    exclusive(REGISTRY, str(lab) + '\n')
    print('LAB=' + str(lab), flush=True)
    for name in ('results', 'raw', 'fixture', 'accepted-offline', 'handoff-source'):
        (lab / name).mkdir()
    exclusive(lab / 'campaign-owner', str(REGISTRY) + '\n')
    transfers = []
    # CONTRACT: copied receipts keep historical paths and scope byte-for-byte.
    for n in REQUIRED:
        transfers.append(copy_exact(OLD_LAB / 'results' / (n + '.json'), lab / 'accepted-offline' / (n + '.json')))
    for n in ('offline-gate.json', 'runner-readiness.json', 'review-bindings.json', *SEALS):
        transfers.append(copy_exact(OLD_LAB / 'results' / n, lab / 'accepted-offline' / n))
    transfers.append(copy_exact(OLD_LAB / 'independent-review.md', lab / 'accepted-offline/independent-review.md'))
    transfers.append(copy_exact(OLD_LAB / 'results/independent-review.json', lab / 'accepted-offline/independent-review.json'))
    for name in proof['bindings']['source_delta']:
        transfers.append(copy_exact(OLD_FIXTURE / name, lab / 'fixture' / name))
    for p in sorted(HERE.iterdir()):
        if p.is_file():
            transfers.append(copy_exact(p, lab / 'handoff-source' / p.name))
    copy_exact(REPO / 'docs/design/STEP20C_STATIC_NESTED_RUNTIME_HANDOFF_AND_VALID_GRAB.md', lab / 'protocol-before-run.md')
    binary_copy = copy_exact(BINARY, lab / 'swayfx-mosaic')
    elf = run_command(lab, 'binary-ELF', ['readelf', '-hW', '-nW', '-dW', lab / 'swayfx-mosaic'])
    need('ELF64' in elf and 'Advanced Micro Devices X86-64' in elf and BUILD_ID in elf and
         all(s not in elf for s in ('libscenefx', '(RPATH)', '(RUNPATH)')), 'ELF-contract')
    symbols = run_command(lab, 'binary-symbols', ['nm', lab / 'swayfx-mosaic'])
    need(all(' T ' + n in symbols for n in ('wlr_scene_tree_set_clip', 'wlr_scene_tree_get_clip')), 'clip-symbols')
    loader = run_command(lab, 'binary-relocations', ['ldd', '-r', lab / 'swayfx-mosaic'])
    need(all(s not in loader for s in ('undefined symbol', 'not found', 'libscenefx')) and
         str(WLROOTS.resolve()) in loader, 'resolved-relocations')
    exclusive(lab / 'results/binary-identity.json', dict(status='PASS', sha256=BINARY_SHA, build_id=BUILD_ID,
              wlroots_sha256=WLROOTS_SHA, copy=binary_copy, mode='0755', ELF='ELF64 x86-64', SceneFX_dynamic=False))
    from prepare_clients import prepare as prepare_clients
    prepare_clients(lab)
    clients = read(lab / 'results/client-provenance.json')
    for name in ('nested-client', 'pointer-daemon', 'static-reference'):
        installation = copy_exact(lab / 'client-build' / name, lab / name)
        regular(lab / name, 0o755)
        clients.setdefault('runtime_installation', []).append(installation)
    # This is a new runtime build receipt, not one of the historical REQUIREDs.
    (lab / 'results/client-provenance.json').write_text(json.dumps(clients, indent=2) + '\n')
    tree = ast.parse((lab / 'fixture/run.py').read_text())
    configs = [ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign)
               and any(isinstance(t, ast.Name) and t.id == 'config' for t in n.targets)]
    need(len(configs) == 1, 'runner-config-constant')
    exclusive(lab / 'headless-config-template', configs[0])
    exclusive(lab / 'results/accepted-offline-provenance.json', proof)
    # Freeze exact runtime inputs, including installed clients and binary, but
    # never budgets/logs/future captures or circular manifest-bound records.
    immutable = [p for root in ('fixture', 'handoff-source', 'accepted-offline', 'client-build')
                 for p in (lab / root).iterdir() if p.is_file()]
    immutable += [lab / n for n in ('swayfx-mosaic', 'nested-client', 'pointer-daemon', 'static-reference',
                                  'campaign-owner', 'headless-config-template', 'protocol-before-run.md')]
    immutable += [lab / 'results' / n for n in ('accepted-offline-provenance.json', 'binary-identity.json', 'client-provenance.json')]
    immutable += [OLD_FIXTURE / n for n in proof['bindings']['source_delta']]
    immutable += [p for p in HERE.iterdir() if p.is_file()]
    immutable += [REGISTRY, BINARY, WLROOTS.resolve()]
    need(len(immutable) == len(set(immutable)), 'unique-freeze-paths')
    for p in immutable:
        need(not p.is_symlink(), 'freeze-no-symlink')
    manifest = lab / 'results/fixture-freeze-sha256.txt'
    exclusive(manifest, ''.join(sha(p) + '  ' + str(p) + '\n' for p in sorted(immutable)))
    fixture = verify(manifest)
    registration = dict(ticket=TICKET, lab=str(lab), uid=os.getuid(), owner_registry=str(REGISTRY),
                        binary=str(BINARY), binary_sha256=BINARY_SHA, wlroots_sha256=WLROOTS_SHA,
                        fixture_sha256=fixture['sha256'], non_reusable=True)
    exclusive(REGISTRATION, registration)
    copy_exact(REGISTRATION, lab / 'results/registration.json')
    auth = dict(scope='one-new-static-nested-headless-run', explicit_user_authorization=True,
                ticket=TICKET, registered_lab=str(lab), owner_registry=str(REGISTRY), binary=str(BINARY),
                binary_sha256=BINARY_SHA, wlroots_sha256=WLROOTS_SHA, fixture_sha256=fixture['sha256'], uid=os.getuid(),
                authorization_basis='User transmitted the exact current ticket; one private launch only.')
    exclusive(lab / 'results/authorization.json', auth)
    exclusive(lab / 'results/budget.json', dict(limits=LIMITS, used=dict.fromkeys(LIMITS, 0), events=[]))
    transfer = dict(status='PREPARED_FOR_INDEPENDENT_REVIEW', ticket=TICKET, destination_lab=str(lab),
                    fixture=fixture, transfers=transfers, provenance_sha256=sha(lab / 'results/accepted-offline-provenance.json'),
                    registration_sha256=sha(REGISTRATION), authorization_sha256=sha(lab / 'results/authorization.json'),
                    historical_review_scope='FINAL_OFFLINE_RECEIPT_INTEGRITY; does not sign this transfer or dispatch')
    exclusive(lab / 'results/runtime-handoff.json', transfer)
    # WHY: this derived gate satisfies the runner with verified transfer data,
    # while the original historical gate and ACCEPTED review are left intact.
    exclusive(lab / 'results/offline-gate.json', dict(status='READY_FOR_NEW_RUNTIME', marker=MARKER,
        fixture_sha256=fixture['sha256'], markers=proof['aggregate']['markers'], blockers=[],
        scope='DERIVED_TRANSFER_OF_ACCEPTED_OFFLINE_EVIDENCE', historical_gate_sha256=sha(OLD_LAB / 'results/offline-gate.json'),
        runtime_handoff_sha256=sha(lab / 'results/runtime-handoff.json')))
    copy_exact(OLD_LAB / 'results/independent-review.json', lab / 'results/independent-review.json')
    exclusive(lab / 'results/preparation.json', dict(status='PASS', lab=str(lab), fixture=fixture, run_reserved=False))
    return lab


def preflight(lab, authorization, review=True):
    """Pure checks; review=False is only for offline tests and review preparation.

    CONTRACT: dispatch always uses review=True. The original authorize() is
    mandatory and runs before any ticket-owned action can be consumed.
    """
    lab = Path(lab).resolve()
    need(not sys.flags.optimize, 'assertions-required')
    auth = authorize(lab, authorization)
    need(auth['ticket'] == TICKET and auth['registered_lab'] == str(lab), 'current-ticket-and-lab')
    need(lab.stat().st_uid == os.getuid() and stat.S_IMODE(lab.stat().st_mode) == 0o700, 'lab-local-owner-mode')
    regular(REGISTRY, 0o600)
    regular(REGISTRATION, 0o600)
    regular(lab / 'campaign-owner', 0o600)
    need(Path(auth['owner_registry']) == REGISTRY and REGISTRY.read_text().strip() == str(lab) and
         (lab / 'campaign-owner').read_text().strip() == str(REGISTRY), 'exclusive-owner-identity')
    need(not SPENT.exists() and not (lab / 'run').exists() and not (lab / 'run.lock').exists(), 'fresh-unconsumed-run')
    need(not any(stat.S_ISSOCK(p.lstat().st_mode) for p in lab.rglob('*')), 'no-preexisting-sockets')
    need(auth['binary'] == str(BINARY) and auth['binary_sha256'] == BINARY_SHA and
         auth['wlroots_sha256'] == WLROOTS_SHA and auth['uid'] == os.getuid(), 'authorized-identities')
    need(sha(BINARY) == sha(lab / 'swayfx-mosaic') == BINARY_SHA and sha(WLROOTS) == WLROOTS_SHA, 'actual-binary-wlroots')
    regular(lab / 'swayfx-mosaic', 0o755)
    fixture = verify(lab / 'results/fixture-freeze-sha256.txt')
    registration = read(REGISTRATION)
    expected = dict(ticket=TICKET, lab=str(lab), uid=os.getuid(), owner_registry=str(REGISTRY), binary=str(BINARY),
                    binary_sha256=BINARY_SHA, wlroots_sha256=WLROOTS_SHA, fixture_sha256=fixture['sha256'], non_reusable=True)
    need(registration == read(lab / 'results/registration.json'), 'original-registration-copy')
    if AMENDMENT.exists():
        # WHY: a rejected preparation candidate is never silently accepted as
        # final. CONTRACT: preserve original registration and append exactly one
        # pre-runtime amendment; ownership and all budget counters are retained.
        regular(AMENDMENT, 0o600)
        amendment = read(AMENDMENT)
        original_identity = {k: v for k, v in registration.items() if k != 'fixture_sha256'}
        need(original_identity == {k: v for k, v in expected.items() if k != 'fixture_sha256'}, 'amendment-identity-unchanged')
        need(amendment == dict(registration=expected, previous_registration_sha256=sha(REGISTRATION),
             superseded_fixture_sha256=registration['fixture_sha256'], reason='pre-runtime test exception-class correction',
             runtime_reserved=False, budget_reset=False), 'append-only-registration-amendment')
        need(read(lab / 'results/registration-amendment.json') == amendment, 'amendment-copy')
    else:
        need(registration == expected, 'durable-registration-bindings')
    need(auth['fixture_sha256'] == fixture['sha256'], 'authorization-fixture-binding')
    proof = accepted()
    need(read(lab / 'results/accepted-offline-provenance.json') == proof, 'accepted-offline-provenance')
    handoff = read(lab / 'results/runtime-handoff.json')
    need(handoff['ticket'] == TICKET and handoff['destination_lab'] == str(lab) and handoff['fixture'] == fixture and
         handoff['registration_sha256'] == sha(REGISTRATION) and handoff['authorization_sha256'] == sha(authorization) and
         handoff['provenance_sha256'] == sha(lab / 'results/accepted-offline-provenance.json'), 'handoff-bindings')
    if AMENDMENT.exists():
        need(handoff['registration_amendment_sha256'] == sha(AMENDMENT) and
             auth['registration_amendment_sha256'] == sha(AMENDMENT), 'explicit-amendment-binding')
    for item in handoff['transfers']:
        need(sha(item['source']) == sha(item['destination']) == item['sha256'], 'exact-transfer: ' + item['source'])
    gate = read(lab / 'results/offline-gate.json')
    need(gate == dict(status='READY_FOR_NEW_RUNTIME', marker=MARKER, fixture_sha256=fixture['sha256'],
                     markers=proof['aggregate']['markers'], blockers=[], scope='DERIVED_TRANSFER_OF_ACCEPTED_OFFLINE_EVIDENCE',
                     historical_gate_sha256=sha(OLD_LAB / 'results/offline-gate.json'),
                     runtime_handoff_sha256=sha(lab / 'results/runtime-handoff.json')), 'derived-gate-bindings')
    need(sha(lab / 'results/independent-review.json') == REVIEW_SHA, 'historical-review-copy')
    need(read(lab / 'results/binary-identity.json')['status'] == 'PASS', 'binary-receipt')
    clients = read(lab / 'results/client-provenance.json')
    for item in clients['runtime_installation']:
        name = Path(item['destination']).name
        need(name in ('nested-client', 'pointer-daemon', 'static-reference') and
             item['destination'] == str(lab / name) and item['source'] == str(lab / 'client-build' / name), 'client-installation-path')
        regular(lab / name, 0o755)
        need(sha(item['source']) == sha(item['destination']) == item['sha256'], 'client-installation-bytes')
    need({Path(i['destination']).name for i in clients['runtime_installation']} ==
         {'nested-client', 'pointer-daemon', 'static-reference'}, 'all-runtime-clients')
    budget = valid(read(lab / 'results/budget.json'))
    need(not any(budget['used'].values()) and not budget['events'], 'unused-ledger-required')
    if review:
        checks = read(lab / 'results/preflight-tests.json')
        need(checks['status'] == 'PASS' and checks['tests'] >= 13 and checks['source_sha256'] == sha(HERE / 'tests_offline.py'), 'negative-preflight-tests')
        reviewed = read(lab / 'results/handoff-review.json')
        need(reviewed['status'] == 'ACCEPTED' and reviewed['independent'] is True and reviewed['read_only'] is True and
             reviewed['scope'] == 'STATIC_NESTED_RUNTIME_HANDOFF' and reviewed['fixture_sha256'] == fixture['sha256'] and
             reviewed['runtime_handoff_sha256'] == sha(lab / 'results/runtime-handoff.json') and
             reviewed['authorization_sha256'] == sha(authorization) and reviewed['registration_sha256'] == sha(REGISTRATION), 'independent-handoff-acceptance')
        need(reviewed['source_sha256'] == {p.name: sha(p) for p in HERE.iterdir() if p.is_file()}, 'reviewed-handoff-sources')
        if AMENDMENT.exists():
            need(reviewed['registration_amendment_sha256'] == sha(AMENDMENT), 'reviewed-registration-amendment')
        need(sha(reviewed['report_file']) == reviewed['report_sha256'] and not reviewed['blockers'], 'handoff-review-report')
    return dict(status='PASS', marker='STATIC_NESTED_RUNTIME_PREFLIGHT=PASS', fixture=fixture,
                authorization='PASS', handoff='PASS' if review else 'PENDING_INDEPENDENT_REVIEW', run_reserved=False,
                budget=budget, ticket=TICKET, lab=str(lab))


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('action', choices=('prepare', 'preflight'))
    p.add_argument('lab', nargs='?', type=Path)
    a = p.parse_args()
    if a.action == 'prepare':
        prepare()
    else:
        result = preflight(a.lab, a.lab / 'results/authorization.json')
        exclusive(a.lab / 'results/preflight.json', result)
        print(result['marker'])
