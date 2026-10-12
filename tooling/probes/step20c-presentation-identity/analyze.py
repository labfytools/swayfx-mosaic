"""Correlate native headless output events without inventing frame identity."""
import hashlib
import json
from pathlib import Path
import re
import sys

from PIL import Image

if len(sys.argv) != 2:
    raise SystemExit('usage: analyze.py LAB')
lab = Path(sys.argv[1]).resolve()
results = lab / 'presentation-results'
results.mkdir(exist_ok=True)


def fields(line):
    return {k: v for k, v in re.findall(r'([a-z_]+)=([^ ]+)', line)}


def save(name, value):
    (results / name).write_text(json.dumps(value, indent=2) + '\n')


events, commits, presents, scenes, inputs, pixels, damage, matrix, transitions = [], [], [], [], [], [], [], [], []
repaint_results = []
for run in sorted((lab / 'runs').glob('*')):
    status_path = run / 'exit-status.json'
    if not status_path.exists():
        continue
    run_id = run.name
    status = json.loads(status_path.read_text())
    output_by_seq = {}
    active_commit = None
    for line in (run / 'compositor.log').read_text().splitlines():
        match = re.search(r'\b(PI_OUTPUT_COMMIT|PI_OUTPUT_PRESENT|PI_SCENE|PI_OWNER|PI_POPUP|TEMPORAL_DAMAGE|SPIKE_DAMAGE|TEMPORAL_OUTPUT_COMMIT)\b(.*)', line)
        if not match:
            continue
        kind = match.group(1)
        data = {'run': run_id, 'kind': kind, **fields(match.group(2))}
        events.append(data)
        if kind == 'PI_OUTPUT_COMMIT':
            key = (data['output'], int(data['commit_seq']))
            if key in output_by_seq:
                raise RuntimeError(f'duplicate native commit sequence in {run_id}: {key}')
            data['commit_seq'] = key[1]
            data['present_count'] = 0
            data['scene'] = None
            data['owners'] = []
            data['popups'] = []
            commits.append(data)
            output_by_seq[key] = data
            active_commit = data
        elif kind == 'PI_OUTPUT_PRESENT':
            data['commit_seq'] = int(data['commit_seq'])
            data['matched'] = (data['output'], data['commit_seq']) in output_by_seq
            if data['matched']:
                output_by_seq[(data['output'], data['commit_seq'])]['present_count'] += 1
            presents.append(data)
            active_commit = None
        elif kind in ('PI_SCENE', 'PI_OWNER', 'PI_POPUP'):
            # CONTRACT: these synchronous callback lines belong to the
            # immediately preceding commit callback, never to a later frame.
            if active_commit is not None and data['output'] == active_commit['output']:
                if kind == 'PI_SCENE':
                    active_commit['scene'] = data
                    scenes.append({'run': run_id, 'output': data['output'],
                                   'commit_seq': active_commit['commit_seq'], **data})
                elif kind == 'PI_OWNER':
                    active_commit['owners'].append(data)
                else:
                    active_commit['popups'].append(data)
        else:
            if kind in ('TEMPORAL_DAMAGE', 'SPIKE_DAMAGE'):
                damage.append(data)
            if kind == 'TEMPORAL_OUTPUT_COMMIT':
                repaint_results.append(data)
            active_commit = None
    runner_events = [json.loads(line) for line in (run / 'events.jsonl').read_text().splitlines()]
    starts = [e for e in runner_events if e['kind'] == 'transition_start']
    for index, start in enumerate(starts):
        begin = start['monotonic_ns']
        end = starts[index + 1]['monotonic_ns'] if index + 1 < len(starts) else None
        own_commits = [c for c in commits if c['run'] == run_id and
                       c['output'] == 'HEADLESS-1' and int(c['ns']) >= begin and
                       (end is None or int(c['ns']) < end)]
        own_presents = [p for p in presents if p['run'] == run_id and
                        p['output'] == 'HEADLESS-1' and int(p['ns']) >= begin and
                        (end is None or int(p['ns']) < end)]
        transitions.append({'run': run_id, 'series': start['series'],
                            'index': start['index'], 'requested_scroll': start['target'],
                            'start_ns': begin, 'next_command_ns': end,
                            'commit_count_in_interval': len(own_commits),
                            'present_count_in_interval': len(own_presents),
                            'observed_commit_scrolls': [c['scene'].get('scroll')
                                if c['scene'] else None for c in own_commits],
                            'command_to_frame_identity': 'UNPROVEN'})
    for event in runner_events:
        if event['kind'] in ('pointer_request', 'camera_observed', 'ipc', 'client_request'):
            inputs.append({'run': run_id, **event})
        if event['kind'] != 'capture':
            continue
        path = run / event['path']
        image = Image.open(path).convert('RGB')
        counts = {name: image.get_flattened_data().count(rgb)
                  for name, rgb in {'A_yellow': (224, 192, 32),
                                    'B_green': (32, 208, 160)}.items()}
        before, after = event['before_ns'], event['after_ns']
        nearby = [p['commit_seq'] for p in presents if p['run'] == run_id and
                  p['output'] == event['output'] and before <= int(p['ns']) <= after]
        pixels.append({'run': run_id, 'output': event['output'], 'tag': event['tag'],
                       'path': event['path'], 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                       'before_ns': before, 'after_ns': after, 'size': list(image.size),
                       'roi': [400, 90, 800, 310] if event['output'] == 'HEADLESS-1'
                       else [0, 90, 200, 310], 'exact_color_pixels': counts,
                       'present_events_during_capture': nearby,
                       'commit_seq_of_captured_buffer': None})
    client = (run / 'client.log').read_text() if (run / 'client.log').exists() else ''
    compositor_text = (run / 'compositor.log').read_text()
    protocol_error = bool(re.search(r'protocol error|invalid serial',
                                    compositor_text + client, re.I))
    grabs = re.findall(r'POPUP_[AB] GRAB_REQUEST origin=wl_pointer.button '
                       r'target=\w+ serial=(\d+) used=(\d+)', client)
    button_serials = set(re.findall(r'POINTER_BUTTON target=\w+ serial=(\d+) '
                                    r'button=272 state=1', client))
    valid_grabs = len(grabs) >= 2 and all(
        serial == used and serial in button_serials for serial, used in grabs)
    for line in client.splitlines():
        if any(token in line for token in ('GRAB_REQUEST', 'POINTER_ENTER', 'POINTER_BUTTON',
                                           'POPUP_DONE', 'MAP', 'DESTROY')):
            inputs.append({'run': run_id, 'kind': 'client_line', 'line': line})
    own_commits = [c for c in commits if c['run'] == run_id]
    own_presents = [p for p in presents if p['run'] == run_id]
    matrix.append({'run': run_id, 'runner': 'FAIL' if status['failure'] else 'PASS',
                   'accepted_commits': len(own_commits), 'present_events': len(own_presents),
                   'matched_present_events': sum(p['matched'] for p in own_presents),
                   'commits_without_present': sum(c['present_count'] == 0 for c in own_commits),
                   'scene_snapshots': sum(c['scene'] is not None for c in own_commits),
                   'valid_button_serials': 'PASS' if valid_grabs else 'INCONCLUSIVE',
                   'protocol_error': protocol_error,
                   'capture_count': sum(p['run'] == run_id for p in pixels),
                   'failure': status['failure']})

for name, value in [('commits.json', commits), ('presentations.json', presents),
                    ('camera-states.json', scenes), ('damage-analysis.json', damage),
                    ('input-analysis.json', inputs), ('pixel-analysis.json', pixels),
                    ('matrix.json', matrix), ('transitions.json', transitions)]:
    save(name, value)
(results / 'events.jsonl').write_text(''.join(json.dumps(e) + '\n' for e in events))
summary = {'accepted_commits': len(commits), 'present_events': len(presents),
           'matched_present_events': sum(p['matched'] for p in presents),
           'unmatched_present_events': sum(not p['matched'] for p in presents),
           'commits_without_present': sum(c['present_count'] == 0 for c in commits),
           'headless_presented_true': sum(p['presented'] == '1' for p in presents),
           'presented_false': sum(p['presented'] == '0' for p in presents),
           'repaint_commit_calls_rejected': sum(r['accepted'] == '0' for r in repaint_results),
           'scene_snapshots': len(scenes), 'capture_count': len(pixels),
           'captures_with_present_during_capture': sum(bool(p['present_events_during_capture'])
                                                       for p in pixels),
           'runs': len(matrix), 'runner_failures': sum(x['runner'] == 'FAIL' for x in matrix),
           'invalid_or_unproven_grabs': sum(x['valid_button_serials'] != 'PASS' for x in matrix),
           'protocol_error_runs': sum(x['protocol_error'] for x in matrix),
           'buffer_content_identity': 'UNPROVEN'}
save('summary.json', summary)
print(json.dumps(summary))
