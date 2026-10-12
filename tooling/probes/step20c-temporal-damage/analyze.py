"""Analyze sampled temporal PNGs and XDG/IPC evidence; never infer all frames."""
import hashlib
import json
from pathlib import Path
import re
import sys

from PIL import Image, ImageChops, ImageDraw

if len(sys.argv) != 2:
    raise SystemExit('usage: analyze.py LAB')
lab = Path(sys.argv[1]).resolve()
colors = {'A_yellow': (224, 192, 32), 'B_green': (32, 208, 160)}
results = []


def image_metrics(path, reference=None, roi=None):
    image = Image.open(path).convert('RGB')
    data = image.get_flattened_data()
    result = {'path': path.name, 'size': list(image.size),
              'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
              'exact_color_pixels': {name: data.count(rgb) for name, rgb in colors.items()}}
    if reference is not None and reference.exists():
        other = Image.open(reference).convert('RGB')
        if other.size == image.size:
            box = roi or (0, 0, image.width, image.height)
            diff = ImageChops.difference(image.crop(box), other.crop(box))
            changed = diff.convert('L').point(lambda v: 255 if v else 0)
            coords = changed.getbbox()
            result['comparison'] = {'reference': reference.name, 'roi_local': list(box),
                                    'changed_pixels': sum(v != 0 for v in changed.get_flattened_data()),
                                    'difference_bbox_local': None if coords is None else
                                    [coords[0] + box[0], coords[1] + box[1],
                                     coords[2] + box[0], coords[3] + box[1]]}
    return result


for run in sorted((lab / 'runs').glob('*')):
    if not (run / 'exit-status.json').exists():
        continue
    name = run.name
    mode = next((m for m in ('control', 'private_standard', 'private_mosaic')
                 if name.startswith(m + '-')), 'unknown')
    kind = name[len(mode) + 1:].split('-')[0]
    status = json.loads((run / 'exit-status.json').read_text())
    events = [json.loads(line) for line in (run / 'events.jsonl').read_text().splitlines()]
    client = (run / 'client.log').read_text() if (run / 'client.log').exists() else ''
    compositor = (run / 'compositor.log').read_text()
    pointer = (run / 'pointer.log').read_text() if (run / 'pointer.log').exists() else ''
    damage = re.findall(r'SPIKE_DAMAGE output=(\S+) extent=(-?\d+),(-?\d+)\.\.(-?\d+),(-?\d+)',
                        compositor)
    timed_damage = [dict(ordinal=int(n), ns=int(ns), output=output,
                         extent=[int(x1), int(y1), int(x2), int(y2)])
        for n, ns, output, x1, y1, x2, y2 in re.findall(
            r'TEMPORAL_DAMAGE ordinal=(\d+) ns=(\d+) output=(\S+) extent=(-?\d+),(-?\d+)\.\.(-?\d+),(-?\d+)',
            compositor)]
    timed_commits = [dict(ordinal=int(n), ns=int(ns), output=output, accepted=bool(int(ok)))
        for n, ns, output, ok in re.findall(
            r'TEMPORAL_OUTPUT_COMMIT ordinal=(\d+) ns=(\d+) output=(\S+) accepted=(\d+)',
            compositor)]
    (run / 'damage.log').write_text('\n'.join(line for line in compositor.splitlines()
                                         if 'SPIKE_DAMAGE' in line) + '\n')
    grabs = re.findall(r'(POPUP_[AB]) GRAB_REQUEST origin=wl_pointer.button target=(\w+) serial=(\d+) used=(\d+)', client)
    button_serials = set(re.findall(r'POINTER_BUTTON target=\w+ serial=(\d+) button=272 state=1', client))
    grab_valid = bool(grabs) and all(serial == used and serial in button_serials
                                      for _, _, serial, used in grabs)
    captures = {}
    for event in events:
        if event['kind'] != 'capture':
            continue
        path = run / event['path']
        tag = event['tag']
        side = 'left' if event['output'] == 'HEADLESS-1' else 'right'
        cycle_prefix = tag.split('-S')[0]
        reference = run / f'{side}-{cycle_prefix}-S0-reference.png'
        # This fixed ROI covers the measured b_cross A/B footprint on the
        # left output; it was declared before looking at captured anomalies.
        roi = (400, 90, 800, 310) if side == 'left' else (0, 90, 200, 310)
        metrics = image_metrics(path, reference if path != reference else None, roi)
        metrics.update(output=event['output'], tag=tag, before_ns=event['before_ns'],
                       after_ns=event['after_ns'])
        captures[path.name] = metrics
    damage_intervals = []
    previous = {}
    for event in events:
        if event['kind'] != 'capture':
            continue
        output = event['output']
        earlier = previous.get(output)
        previous[output] = event
        if earlier is None:
            continue
        first = Image.open(run / earlier['path']).convert('RGB')
        second = Image.open(run / event['path']).convert('RGB')
        image_diff = ImageChops.difference(first, second)
        changed = image_diff.convert('L').point(lambda v: 255 if v else 0)
        box = changed.getbbox()
        records = [d for d in timed_damage if d['output'] == output and
                   earlier['after_ns'] <= d['ns'] <= event['after_ns']]
        commits = [c for c in timed_commits if c['output'] == output and
                   earlier['after_ns'] <= c['ns'] <= event['after_ns']]
        overlap = None if box is None else any(
            not (box[2] <= d['extent'][0] or d['extent'][2] <= box[0] or
                 box[3] <= d['extent'][1] or d['extent'][3] <= box[1])
            for d in records)
        uncovered = None
        if timed_damage:
            # CONTRACT: union only the output-local extents falling between
            # these sampled captures. This is an interval comparison, not an
            # association with every presented frame.
            mask = Image.new('L', first.size, 0)
            draw = ImageDraw.Draw(mask)
            for d in records:
                x1, y1, x2, y2 = d['extent']
                if x2 > x1 and y2 > y1:
                    draw.rectangle((x1, y1, x2 - 1, y2 - 1), fill=255)
            uncovered = sum(v != 0 for v in ImageChops.subtract(changed, mask).get_flattened_data())
        damage_intervals.append({'output': output, 'from': earlier['path'],
            'to': event['path'], 'from_after_ns': earlier['after_ns'],
            'to_after_ns': event['after_ns'], 'changed_pixels':
            sum(v != 0 for v in changed.get_flattened_data()),
            'change_bbox_local': None if box is None else list(box),
            'damage_ordinals': [d['ordinal'] for d in records],
            'commit_ordinals': [c['ordinal'] for c in commits],
            'damage_bbox_overlaps_change': overlap,
            'changed_pixels_outside_logged_damage_extents': uncovered})
    (run / 'damage-analysis.json').write_text(json.dumps({
        'status': 'PARTIAL' if timed_damage else 'NOT TESTED',
        'reason': 'Sampled grim captures have no presented-frame identity; '
                  'damage extents and accepted commits cannot establish every presentation.',
        'timed_damage': timed_damage, 'timed_commits': timed_commits,
        'sample_intervals': damage_intervals}, indent=2) + '\n')
    assertions = {}
    assertions['run_completed'] = 'FAIL' if status['failure'] else 'PASS'
    assertions['private_runtime_removed'] = ('PASS' if any(e['kind'] == 'cleanup' and
        e.get('runtime_removed') for e in events) else 'FAIL')
    assertions['protocol_log'] = ('FAIL' if re.search(r'protocol error|invalid serial',
        compositor + client, re.I) else 'PASS')
    assertions['valid_button_serials'] = 'PASS' if grab_valid else 'INCONCLUSIVE'
    assertions['two_level_chain'] = ('PASS' if 'POPUP_A CREATE' in client and
        'POPUP_B CREATE' in client and 'parent=TOPLEVEL' in client and
        'parent=POPUP_A' in client else 'INCONCLUSIVE')
    completed_cycles = sum(e['kind'] == 'cycle_end' for e in events)
    if kind == 'cycles':
        assertions['cycles_complete'] = 'PASS' if completed_cycles and not status['failure'] else 'FAIL'
        a_right_presses = len(re.findall(
            r'POINTER_BUTTON target=POPUP_A[^\n]*button=273 state=1', client))
        assertions['A_interactive_after_B_close'] = ('PASS' if completed_cycles and
            a_right_presses >= completed_cycles and all(
                f'left-cycle-{i:03d}-S6-A-interaction.png' in captures
                for i in range(1, completed_cycles + 1)) else 'INCONCLUSIVE')
        assertions['object_lifecycle'] = ('PASS' if all(
            client.count(p + ' CREATE') == completed_cycles and
            client.count(p + ' DESTROY') == completed_cycles
            for p in ('POPUP_A', 'POPUP_B')) else 'FAIL')
        visual = []
        uncovered = []
        restored = []
        for i in range(1, completed_cycles + 1):
            prefix = f'cycle-{i:03d}'
            def equal_roi(before, after):
                first, second = (run / f'left-{prefix}-{before}.png',
                                 run / f'left-{prefix}-{after}.png')
                if not first.exists() or not second.exists():
                    return None
                box = (400, 90, 800, 310)
                left = Image.open(first).convert('RGB').crop(box)
                right = Image.open(second).convert('RGB').crop(box)
                return ImageChops.difference(left, right).getbbox() is None
            def pixels(side, tag, color):
                item = captures.get(f'{side}-{prefix}-{tag}.png')
                return None if item is None else item['exact_color_pixels'][color]
            vals = [pixels('left', 'S3-visible', 'A_yellow'),
                    pixels('left', 'S3-visible', 'B_green'),
                    pixels('left', 'S6-close-B-stable', 'B_green'),
                    pixels('left', 'S6-close-B-stable', 'A_yellow'),
                    pixels('left', 'S7-close-A-stable', 'A_yellow'),
                    pixels('left', 'S7-close-A-stable', 'B_green')]
            if None in vals:
                visual.append('INCONCLUSIVE')
            elif vals[0] > 0 and vals[1] > 0 and vals[2] == 0 and vals[3] > 0 and vals[4] == vals[5] == 0:
                visual.append('PASS')
            else:
                visual.append('FAIL')
            if mode == 'private_mosaic':
                hidden = [pixels('left', 'S4-hidden-stable', c) for c in colors]
                returned = [pixels('left', 'S5-return-stable', c) for c in colors]
                visual.append('INCONCLUSIVE' if None in hidden + returned else
                    'PASS' if hidden == [0, 0] and returned[0] > 0 and returned[1] > 0 else 'FAIL')
                restored.append(equal_roi('S3-visible', 'S5-return-stable'))
            uncovered.extend((equal_roi('S1-A', 'S6-close-B-stable'),
                              equal_roi('S0-reference', 'S7-close-A-stable')))
        assertions['sampled_visual_lifecycle'] = ('FAIL' if 'FAIL' in visual else
            'INCONCLUSIVE' if 'INCONCLUSIVE' in visual or not visual else 'PASS')
        assertions['uncovered_region_equality'] = ('INCONCLUSIVE' if None in uncovered or
            not uncovered else 'PASS' if all(uncovered) else 'FAIL')
        assertions['camera_return_region_equality'] = ('NOT TESTED' if mode != 'private_mosaic'
            else 'INCONCLUSIVE' if None in restored or not restored else
            'PASS' if all(restored) else 'FAIL')
    else:
        assertions['cycles_complete'] = 'NOT TESTED'
        assertions['A_interactive_after_B_close'] = 'NOT TESTED'
        assertions['sampled_visual_lifecycle'] = 'NOT TESTED'
        assertions['object_lifecycle'] = 'NOT TESTED'
        assertions['uncovered_region_equality'] = 'NOT TESTED'
        assertions['camera_return_region_equality'] = 'NOT TESTED'
    if kind == 'camera':
        camera_events = [e for e in events if e['kind'] == 'camera_observed']
        assertions['camera_ipc_identity'] = ('PASS' if len(camera_events) >= 1 and
            len({e['owner_id'] for e in camera_events}) == 1 and
            all(e['target'] in (400, 1280) for e in camera_events) else 'INCONCLUSIVE')
        sampled = []
        for path, item in captures.items():
            match = re.match(r'left-camera-(?:stable|fast|burst)-(\d+)', path)
            if not match:
                continue
            expected_hidden = int(match.group(1)) % 2 == 0
            counts = item['exact_color_pixels']
            sampled.append(all(v == 0 for v in counts.values()) if expected_hidden else
                           all(v > 0 for v in counts.values()))
        assertions['sampled_camera_pixels'] = ('INCONCLUSIVE' if not sampled else
            'PASS' if all(sampled) else 'FAIL')
        assertions['popup_survives_camera'] = ('PASS' if client.count('POPUP_A CREATE') == 1
            and client.count('POPUP_B CREATE') == 1 and 'POPUP_DONE' not in client else 'FAIL')
    else:
        assertions['camera_ipc_identity'] = 'NOT TESTED'
        assertions['sampled_camera_pixels'] = 'NOT TESTED'
        assertions['popup_survives_camera'] = 'NOT TESTED'
    if kind == 'outside':
        done = re.findall(r'(POPUP_[AB]) POPUP_DONE', client)
        destroyed = re.findall(r'(POPUP_[AB]) DESTROY', client)
        left = captures.get('left-outside-dismissed.png', {}).get('exact_color_pixels')
        right = captures.get('right-outside-dismissed.png', {}).get('exact_color_pixels')
        assertions['outside_dismissal'] = ('INCONCLUSIVE' if left is None or right is None
            else 'PASS' if done == destroyed == ['POPUP_B', 'POPUP_A'] and
            all(v == 0 for v in list(left.values()) + list(right.values()))
            else 'FAIL')
    else:
        assertions['outside_dismissal'] = 'NOT TESTED'
    if kind == 'hidden_click':
        targets = [e for e in events if e['kind'] == 'hidden_click_target']
        done = re.findall(r'(POPUP_[AB]) POPUP_DONE', client)
        returned = captures.get('left-hidden-click-returned.png', {}).get('exact_color_pixels')
        assertions['hidden_click_no_popup_hit'] = ('INCONCLUSIVE' if not targets or
            returned is None else 'PASS' if
            targets[-1]['popup_buttons_before'] == targets[-1]['popup_buttons_after'] and
            done == ['POPUP_B', 'POPUP_A'] and all(v == 0 for v in returned.values())
            else 'FAIL')
    else:
        assertions['hidden_click_no_popup_hit'] = 'NOT TESTED'
    if kind == 'toggle':
        right = captures.get('right-toggle-standard-stable.png', {}).get('exact_color_pixels')
        assertions['standard_return'] = ('INCONCLUSIVE' if right is None else
            'PASS' if right['B_green'] > 0 and 'POPUP_DONE' not in client and
            len(re.findall(r'POINTER_BUTTON target=POPUP_B[^\n]*state=1', client)) >= 2
            else 'FAIL')
    else:
        assertions['standard_return'] = 'NOT TESTED'
    assertions['damage_frame_association'] = 'PARTIAL' if timed_damage else 'NOT TESTED'
    if status['failure'] or 'FAIL' in assertions.values():
        verdict = 'FAIL'
    elif 'INCONCLUSIVE' in assertions.values():
        verdict = 'INCONCLUSIVE'
    else:
        verdict = 'PARTIAL'  # sampled captures and damage extents lack frame identity
    result = {'run': name, 'mode': mode, 'kind': kind, 'verdict': verdict,
              'assertions': assertions, 'completed_cycles': completed_cycles,
              'capture_count': len(captures), 'damage_record_count': len(damage),
              'timed_damage_record_count': len(timed_damage),
              'timed_commit_record_count': len(timed_commits),
              'sample_interval_count': len(damage_intervals),
              'changed_intervals_without_overlapping_damage_extent': sum(
                  item['changed_pixels'] > 0 and item['damage_bbox_overlaps_change'] is False
                  for item in damage_intervals) if timed_damage else None,
              'changed_pixels_outside_logged_damage_extents': sum(
                  item['changed_pixels_outside_logged_damage_extents'] or 0
                  for item in damage_intervals) if timed_damage else None,
              'damage_by_output': {output: sum(d[0] == output for d in damage)
                                   for output in ('HEADLESS-1', 'HEADLESS-2')},
              'grab_requests': grabs, 'popup_create_count': {p: client.count(p + ' CREATE')
                                                             for p in ('POPUP_A', 'POPUP_B')},
              'popup_destroy_count': {p: client.count(p + ' DESTROY')
                                      for p in ('POPUP_A', 'POPUP_B')},
              'capture_metrics': captures, 'exit_status': status,
              'pointer_ack_count': pointer.count('INJECT_DONE')}
    (run / 'analysis.json').write_text(json.dumps(result, indent=2) + '\n')
    results.append({k: v for k, v in result.items() if k != 'capture_metrics'})
    print(name, verdict, 'cycles', completed_cycles, 'captures', len(captures),
          'damage', len(damage), flush=True)
(lab / 'results').mkdir(exist_ok=True)
(lab / 'results/summary.json').write_text(json.dumps(results, indent=2) + '\n')
(lab / 'results/damage-analysis.json').write_text(json.dumps([
    {'run': r['run'], 'timed_damage_record_count': r['timed_damage_record_count'],
     'timed_commit_record_count': r['timed_commit_record_count'],
     'sample_interval_count': r['sample_interval_count'],
     'changed_intervals_without_overlapping_damage_extent':
        r['changed_intervals_without_overlapping_damage_extent'],
     'changed_pixels_outside_logged_damage_extents':
        r['changed_pixels_outside_logged_damage_extents']}
    for r in results], indent=2) + '\n')
(lab / 'results/pixel-analysis.json').write_text(json.dumps([
    {'run': r['run'], 'capture_count': r['capture_count'],
     'sampled_visual_lifecycle': r['assertions']['sampled_visual_lifecycle'],
     'uncovered_region_equality': r['assertions']['uncovered_region_equality'],
     'A_interactive_after_B_close': r['assertions']['A_interactive_after_B_close'],
     'camera_return_region_equality': r['assertions']['camera_return_region_equality'],
     'sampled_camera_pixels': r['assertions']['sampled_camera_pixels']}
    for r in results], indent=2) + '\n')


def selected(mode, kind):
    found = [r for r in results if r['mode'] == mode and r['kind'] == kind]
    return max(found, key=lambda r: r['completed_cycles']) if found else None


matrix = {}
for label, assertion, kind in (
    ('repeated_open_A_B', 'two_level_chain', 'cycles'),
    ('close_B_reveals_A', 'uncovered_region_equality', 'cycles'),
    ('close_A_reveals_background', 'uncovered_region_equality', 'cycles'),
    ('outside_click', 'outside_dismissal', 'outside'),
    ('ghost_pixels_sampled', 'uncovered_region_equality', 'cycles'),
    ('A_after_B_input', 'A_interactive_after_B_close', 'cycles'),
    ('crash_or_protocol_error', 'protocol_log', 'cycles')):
    matrix[label] = {}
    for mode in ('control', 'private_standard', 'private_mosaic'):
        run = selected(mode, kind)
        matrix[label][mode] = {'status': run['assertions'][assertion] if run else 'NOT TESTED',
                               'run': run['run'] if run else None}
for label, assertion, kind in (
    ('camera_hide', 'sampled_visual_lifecycle', 'cycles'),
    ('camera_return', 'camera_return_region_equality', 'cycles'),
    ('camera_fast', 'sampled_camera_pixels', 'camera'),
    ('standard_layout_return', 'standard_return', 'toggle')):
    matrix[label] = {}
    for mode in ('control', 'private_standard', 'private_mosaic'):
        run = selected(mode, kind) if mode == 'private_mosaic' else None
        matrix[label][mode] = {'status': run['assertions'][assertion] if run else 'N/A',
                               'run': run['run'] if run else None}
matrix['hidden_click_no_popup_hit'] = {
    mode: {'status': selected(mode, 'hidden_click')['assertions']['hidden_click_no_popup_hit']
           if mode == 'private_mosaic' and selected(mode, 'hidden_click') else 'N/A',
           'run': selected(mode, 'hidden_click')['run'] if mode == 'private_mosaic'
           and selected(mode, 'hidden_click') else None}
    for mode in ('control', 'private_standard', 'private_mosaic')}
matrix['damage_observed'] = {
    mode: {'status': 'PARTIAL' if selected(mode, 'cycles') and
           selected(mode, 'cycles')['timed_damage_record_count'] else 'NOT TESTED',
           'run': selected(mode, 'cycles')['run'] if selected(mode, 'cycles') else None}
    for mode in ('control', 'private_standard', 'private_mosaic')}
matrix['input_render_consistency'] = {
    mode: {'status': 'PARTIAL' if selected(mode, 'cycles') else 'NOT TESTED',
           'run': selected(mode, 'cycles')['run'] if selected(mode, 'cycles') else None}
    for mode in ('control', 'private_standard', 'private_mosaic')}
for mode in ('control', 'private_standard', 'private_mosaic'):
    run = selected(mode, 'cycles')
    if run:
        matrix['crash_or_protocol_error'][mode]['status'] = ('PASS' if
            run['assertions']['protocol_log'] == run['assertions']['run_completed'] == 'PASS'
            else 'FAIL')
(lab / 'results/matrix.json').write_text(json.dumps(matrix, indent=2) + '\n')
