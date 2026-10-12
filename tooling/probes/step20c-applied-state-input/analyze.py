"""Parse private applied scene, buffer lifetime and input traces without invented frame IDs."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import statistics

ap = argparse.ArgumentParser()
ap.add_argument('lab', type=Path)
ap.add_argument('run', type=Path)
args = ap.parse_args()
run = args.run.resolve()
lab = args.lab.resolve()
if lab not in run.parents or not (run / 'compositor.log').is_file():
    ap.error('run must be inside the prepared lab')
out = lab / 'results-asi' / run.name
out.mkdir(parents=True, exist_ok=True)
kinds = ('ASI_MUTATION', 'BI_STAGE', 'ASI_HIT', 'ASI_WARP',
         'ASI_BUTTON_REQUEST', 'ASI_DELIVERY', 'ASI_LOCKED', 'ASI_RELEASE',
         'PI_OUTPUT_COMMIT', 'PI_OUTPUT_PRESENT', 'BI_BUFFER', 'BI_READ',
         'BI_COMMIT', 'BI_EVENT_BUFFER', 'BI_PRESENT_READ', 'BI_PRESENT_HOLD')
records = {k: [] for k in kinds}
for number, line in enumerate((run / 'compositor.log').read_text(errors='replace').splitlines(), 1):
    for kind in kinds:
        marker = kind + ' '
        if marker not in line:
            continue
        payload = line.split(marker, 1)[1]
        fields = dict(re.findall(r'(\w+)=([^ ]+)', payload))
        records[kind].append({'line': number, 'kind': kind, **fields})
        break

mode = json.loads((run / 'asi-mode.json').read_text()) if (run / 'asi-mode.json').exists() else {'mode': 'pointer_control', 'readback_dir': None}
read_dir = Path(mode['readback_dir']) if mode['readback_dir'] else None
raw = {}
if read_dir:
    for f in sorted(read_dir.glob('buffer-*.xrgb')):
        raw[f.name] = {'bytes': f.stat().st_size,
                       'sha256': hashlib.sha256(f.read_bytes()).hexdigest()}

commits = {(x['output'], x['commit_seq']): x for x in records['PI_OUTPUT_COMMIT']}
presents = {(x['output'], x['commit_seq']): x for x in records['PI_OUTPUT_PRESENT']}
selected = records['BI_COMMIT']
releases = records['ASI_RELEASE']
release_count = Counter(x['id'] for x in releases)
selected_ids = {x['id'] for x in selected}
release_ids = set(release_count)
selected_pairs = {(x['output'], x['commit_seq']) for x in selected if x['accepted'] == '1'}
matched = selected_pairs & set(presents)
client = (run / 'client.log').read_text(errors='replace') if (run / 'client.log').exists() else ''
client_events = [line for line in client.splitlines() if any(
    key in line for key in ('POPUP_A MAP', 'POPUP_B MAP', 'POPUP_DONE',
                            'POINTER_BUTTON target=', 'GRAB_REQUEST'))]
summary = {
    'mode': mode['mode'], 'native_commits': len(commits),
    'native_presents': len(presents), 'selected_commits': len(selected_pairs),
    'selected_presents': len(matched), 'selected_buffers': len(records['BI_BUFFER']),
    'raw_snapshots': len([x for x in raw if '-present' not in x]),
    'present_snapshots': len([x for x in raw if '-present' in x]),
    'lock_count': len(records['ASI_LOCKED']), 'release_count': len(releases),
    'double_release_ids': sorted(k for k,v in release_count.items() if v != 1),
    'unreleased_ids': sorted(selected_ids - release_ids),
    'cross_output_release_count': sum(1 for x in releases if x.get('reason') == 'superseded'),
    'release_reasons': dict(Counter(x.get('reason') for x in releases)),
    'mutation_events': len(records['ASI_MUTATION']),
    'scene_stages': len(records['BI_STAGE']),
    'hit_tests': len(records['ASI_HIT']),
    'seat_notifications': len(records['ASI_DELIVERY']),
    'client_popup_maps': {'A': client.count('POPUP_A MAP'), 'B': client.count('POPUP_B MAP')},
    'client_B_buttons': len(re.findall(r'POINTER_BUTTON target=POPUP_B[^\n]*state=1', client)),
    'client_popup_done': {'A': client.count('POPUP_A POPUP_DONE'),
                          'B': client.count('POPUP_B POPUP_DONE')},
}

correlation = []
pixel_analysis = []
for item in selected:
    key = (item['output'], item['commit_seq'])
    earlier = [stage for stage in records['BI_STAGE']
               if stage.get('phase') == 'POST_BUILD' and
               stage['output'] == item['output'] and
               int(stage['ns']) <= int(item['ns'])]
    stage = earlier[-1] if earlier else None
    correlation.append({'id': item['id'], 'output': item['output'],
                        'commit_seq': item['commit_seq'],
                        'accepted': item['accepted'],
                        'native_commit': key in commits,
                        'headless_present': key in presents,
                        'applied_stage': stage})
    if read_dir:
        f = read_dir / ('buffer-' + item['id'] + '.xrgb')
        if f.is_file() and f.stat().st_size == 800 * 600 * 4:
            from PIL import Image
            data = f.read_bytes()
            image = Image.frombytes('RGB', (800, 600), data, 'raw', 'BGRX', 0, -1)
            colors = {color: count for count, color in image.getcolors(480000)}
            second = read_dir / ('buffer-' + item['id'] + '-present.xrgb')
            pixel_analysis.append({'id': item['id'], 'commit_seq': item['commit_seq'],
                'epoch': stage.get('epoch') if stage else None,
                'scroll': stage.get('scroll') if stage else None,
                'tile_scene': stage.get('tile_scene') if stage else None,
                'clip': stage.get('clip') if stage else None,
                'A_yellow': colors.get((224, 192, 32), 0),
                'B_green': colors.get((32, 208, 160), 0),
                'raw_sha256': hashlib.sha256(data).hexdigest(),
                'present_read_equal': second.read_bytes() == data if second.is_file() else None})
post_to_commit = []
stages = records['BI_STAGE']
for i, stage in enumerate(stages):
    if stage.get('phase') != 'POST_BUILD' or stage['output'] != 'HEADLESS-1':
        continue
    later = next((x for x in stages[i + 1:] if x['output'] == stage['output']
                  and x['phase'] in ('PRE_BUILD', 'COMMIT_ACCEPTED')), None)
    if later and later['phase'] == 'COMMIT_ACCEPTED':
        post_to_commit.append(int(later['ns']) - int(stage['ns']))
timing = {'post_build_to_commit_median_ns':
          statistics.median(post_to_commit) if post_to_commit else None,
          'sample_count': len(post_to_commit)}

for name, obj in (('correlation', correlation), ('pixel-analysis', pixel_analysis),
                  ('timing', timing), ('scene-states', {'build': records['BI_STAGE'],
                  'hits': records['ASI_HIT'], 'mutations': records['ASI_MUTATION']}),
                  ('records', records), ('raw-buffers', raw),
                  ('client-events', client_events), ('summary', summary)):
    (out / (name + '.json')).write_text(json.dumps(obj, indent=2) + '\n')
print(json.dumps(summary, indent=2))
