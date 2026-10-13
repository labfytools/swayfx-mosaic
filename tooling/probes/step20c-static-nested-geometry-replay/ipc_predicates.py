"""Pure validators for replay and live observations, never desktop IPC.

WHY: stored border thickness and container IPC geometry are not rendered pixels.
CONTRACT: callers supply measured identities; validate ancestors and applied scene.
INVARIANT: no width-zero predicate, hard-coded runtime IDs, or native buffer y.
"""
import re

OUTPUTS = {'HEADLESS-1': (-800, 0, 800, 600, 1.0, 'normal'),
           'HEADLESS-2': (0, 0, 800, 600, 1.0, 'normal')}
ZERO = dict(x=0, y=0, width=0, height=0)
FULL = dict(x=0, y=0, width=800, height=600)


def nodes(node):
    yield node
    for child in node.get('nodes', []) + node.get('floating_nodes', []):
        yield from nodes(child)


def workspace(tree, name):
    rows = [n for n in nodes(tree) if n.get('type') == 'workspace' and n.get('name') == name]
    assert len(rows) == 1, 'workspace identity'
    return rows[0]


def ancestry(tree, con_id, path=()):
    if tree.get('id') == con_id:
        return path + (tree,)
    for child in tree.get('nodes', []) + tree.get('floating_nodes', []):
        found = ancestry(child, con_id, path + (tree,))
        if found:
            return found
    return ()


def validate_outputs(outputs):
    actual = {o['name']: (*[o['rect'][k] for k in ('x', 'y', 'width', 'height')],
                          o['scale'], o['transform']) for o in outputs if o['active']}
    assert actual == OUTPUTS, ('output geometry', actual)
    assert len([o for o in outputs if o['active']]) == 2, 'duplicate output'
    return actual


def validate_reference(snapshot, con_id, pid, workspace_name='2', output_name='HEADLESS-2'):
    """B_NONE may retain width 2; require actual empty decoration/full content.

    IPC visibility means view_is_visible, not proof of SHM coverage. RGB is
    independently required by the runner. Width is returned only as metadata.
    """
    validate_outputs(snapshot['outputs'])
    path = ancestry(snapshot['tree'], con_id)
    assert path, 'reference surface absent'
    ref = path[-1]
    ws = next((n for n in path if n.get('type') == 'workspace'), None)
    out = next((n for n in path if n.get('type') == 'output'), None)
    assert ref.get('type') == 'con' and ref.get('shell') == 'xdg_shell', 'reference view absent'
    assert ref.get('app_id') == 'org.mosaic.StaticReference', 'reference App ID'
    assert ref.get('pid') == pid and pid > 0 and ref['id'] == con_id, 'reference PID/ID'
    assert ws and ws['name'] == workspace_name and ws.get('output') == output_name, 'reference workspace'
    assert out and out['name'] == output_name and out['rect'] == FULL, 'reference output'
    assert ref.get('visible') is True, 'reference visibility'
    assert ref.get('border') == 'none', 'reference border mode'
    assert ref.get('rect') == FULL and ref.get('window_rect') == FULL, 'reference full content'
    assert ref.get('deco_rect') == ZERO, 'effective reference decoration'
    return {'status': 'PASS', 'con_id': con_id, 'pid': pid, 'workspace': ws['id'],
            'output': output_name, 'stored_border_width': ref.get('current_border_width'),
            'reference': ref}


def scene_from_log(text, output):
    rows = [s for s in text.splitlines() if 'PI_SCENE output=' + output + ' ' in s
            and 'workspace=none' not in s]
    assert rows, 'applied scene trace absent'
    line = rows[-1]
    m = re.search(r'workspace=(\d+) layout=(\d+) scroll=(-?[\d.]+) tile_scene=(-?\d+),(-?\d+) clip_valid=(\d+) clip=(-?\d+),(-?\d+),(\d+),(\d+)', line)
    assert m, 'scene trace format'
    v = list(map(float, m.groups()))
    origin = OUTPUTS[output][:2]
    return {'workspace': int(v[0]), 'layout_enum': int(v[1]), 'scroll': v[2],
            'tile_local': v[3:5], 'clip_valid': bool(v[5]), 'clip_local': v[6:10],
            'global_clip': [origin[0] + v[3] + v[6], origin[1] + v[4] + v[7], v[8], v[9]],
            'raw': line}


def measure_owner(text, owner):
    rows = [x for x in text.splitlines() if 'PI_OWNER output=HEADLESS-1 ' in x
            and f' id={owner["id"]} ' in x]
    assert rows, 'applied owner trace absent'
    line = rows[-1]
    m = re.search(r'scene_valid=1 scene=(-?\d+),(-?\d+) applied_size=(\d+),(\d+)', line)
    assert m, 'owner trace format'
    x, y, w, h = map(int, m.groups())
    win = owner['window_rect']
    return {'id': owner['id'], 'scene': [x, y, w, h], 'window_rect': win,
            'horizontal_content': [x + win['x'], win['width']], 'raw': line, 'IPC': owner}


def client_commit(text):
    rows = [s for s in text.splitlines() if s.startswith('COMMIT ')]
    assert rows, 'no real client commit'
    m = re.fullmatch(r'COMMIT ns=(\d+) serial=(\d+) size=(\d+)x(\d+) color=([0-9a-f]{8})', rows[-1])
    assert m, 'client commit format'
    ns, serial, w, h = map(int, m.groups()[:4])
    assert ns > 0 and 0 < serial <= 0xffffffff and 0 < w <= 4096 and 0 < h <= 4096
    return {'ns': ns, 'serial': serial, 'width': w, 'height': h, 'color': m[5], 'raw': rows[-1]}


def validate_camera(before_scroll, after_scroll, delta, scene):
    assert type(delta) is int and -2147483647 <= delta <= 2147483647
    assert after_scroll == before_scroll + delta and scene['scroll'] == after_scroll, 'camera correction applied'
