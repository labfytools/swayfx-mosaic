"""Bounded headless FX0–FX4 and camera-state source fixture."""
import argparse
import fcntl
import json
from pathlib import Path
import subprocess
import sys

from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument('lab', type=Path)
ap.add_argument('mode', choices=('control', 'private_standard', 'private_mosaic'))
ap.add_argument('--camera-pairs', type=int, choices=range(4), default=3)
ap.add_argument('--reference-resize', action='store_true',
                help='replay the retained late-resize reference variant')
args = ap.parse_args()
lab = args.lab.resolve()
repo = Path(__file__).resolve().parents[3]
# WHY: reproduction and trace controls must not multiply camera repetitions.
# CONTRACT: one active runner per lab; camera pairs are counted across runs.
# INVARIANT: at most three new hide/return pairs in a fresh lab campaign.
campaign_lock = (lab / 'effects-campaign.lock').open('a')
fcntl.flock(campaign_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
prior_pairs = sum(len(list(run.glob('left-T4-hidden-*.png')))
                  for run in (lab / 'runs').glob('private_mosaic-effects-*'))
budget_file = lab / 'effects-camera-budget.json'
if budget_file.exists():
    consumed = json.loads(budget_file.read_text())['consumed']
    if type(consumed) is not int or consumed < 0:
        ap.error('invalid persisted camera budget')
    prior_pairs = max(prior_pairs, consumed)
if args.mode == 'private_mosaic' and args.camera_pairs and prior_pairs + args.camera_pairs > 3:
    ap.error(f'campaign camera budget exceeded: {prior_pairs} already recorded; use --camera-pairs 0')
if args.mode == 'private_mosaic' and args.camera_pairs:
    # Reserve before launch: failed attempts also consume the finite budget.
    temporary_budget = budget_file.with_suffix('.tmp')
    temporary_budget.write_text(json.dumps({'consumed': prior_pairs + args.camera_pairs}) + '\n')
    temporary_budget.replace(budget_file)
pattern = Image.new('RGB', (64, 64))
for y in range(64):
    for x in range(64):
        pattern.putpixel((x, y), (245, 245, 245) if (x // 8) % 2 == 0
                         else (15, 25, 45))
pattern.save(lab / 'fx-checker.png')

source = (repo / 'tooling/probes/step20c-applied-state-input/run.py').read_text()
old = "choices=('cycles', 'buffer_cycles', 'identity', 'outside', 'hidden_click', 'toggle')"
assert source.count(old) == 1
adapted = source.replace(old, old[:-1] + ", 'effects')")
anchor = "    if args.kind == 'cycles':\n"
assert adapted.count(anchor) == 1
scenario = '''    if args.kind == 'effects':
        # CONTRACT: ordinary IPC creates effects; snapshots follow settled
        # states. No compositor scheduler or rendering implementation changes.
        spawn(['swaybg', '-i', str(lab / 'fx-checker.png'), '-m', 'tile'],
              'swaybg.log')
        time.sleep(.3)
        command('[app_id="wev"] floating enable')
        if EFFECT_REFERENCE_RESIZE:
            command('[app_id="wev"] resize set width 300 height 250')
        command('[app_id="wev"] move position 250 250')
        command('gaps inner 24')
        if args.mode != 'private_mosaic':
            command('[app_id="org.mosaic.NestedGrabProbe"] focus')
            command('move right')
            command('move right')
        command('shadows disable')
        command('blur disable')
        command('shadow_blur_radius 16')
        command('shadow_offset 30 0')
        command('shadow_color #000000A0')
        command('blur_radius 5')
        command('blur_passes 3')
        if args.mode == 'private_mosaic': scroll(400)
        record('effect_owner', owner=owner()['rect'], mode=args.mode)
        time.sleep(.2)
        snapshot('FX0-off')
        command('shadows enable')
        time.sleep(.2)
        snapshot('FX1-shadow')
        command('shadows disable')
        command('blur enable')
        time.sleep(.2)
        snapshot('FX2-blur')
        command('blur_xray enable')
        time.sleep(.2)
        snapshot('FX3-optimized-candidate')
        command('shadows enable')
        time.sleep(.2)
        snapshot('FX4-combined')
        if args.mode == 'private_mosaic':
            for pair in range(1, EFFECT_CAMERA_PAIRS + 1):
                scroll(1280)
                time.sleep(.15)
                snapshot(f'T4-hidden-{pair}')
                scroll(400)
                time.sleep(.15)
                snapshot(f'T5-return-{pair}')
            command('layout splith')
            time.sleep(.2)
            snapshot('T7-standard-return')
        command('blur disable')
        command('shadows disable')
        time.sleep(.2)
        snapshot('T6-disabled')
        command('blur enable')
        command('shadows enable')
        time.sleep(.2)
        snapshot('T6-restored')
        client.stdin.write('close_owner\\n')
        client.stdin.flush()
        client.wait(timeout=8)
        record('owner_closed', exit_code=client.returncode)
        time.sleep(.2)
        snapshot('T6-closed')
    elif args.kind == 'cycles':
'''
adapted = adapted.replace(anchor, scenario).replace('EFFECT_CAMERA_PAIRS', str(args.camera_pairs))
adapted = adapted.replace('EFFECT_REFERENCE_RESIZE', str(args.reference_resize))
generated = lab / 'effects-damage-run-generated.py'
generated.write_text(adapted)
raise SystemExit(subprocess.call([sys.executable, str(generated), str(lab),
    args.mode, 'effects', '--asi-mode', '0', '--max-seconds', '120',
    '--max-captures', '40', '--max-bytes', '35000000']))
