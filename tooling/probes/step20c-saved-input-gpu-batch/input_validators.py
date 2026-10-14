"""EXPERIMENTAL input correlation: sampled applied states, never atomic epochs."""
import re

INPUT_ASSERTIONS = ('actual-wire-recipient-serial', 'applied-owner-time-compatible',
                    'global-local-clip-compatible', 'standard-clip-removed', 'normal-close-error-zero')

class InvalidEvidence(ValueError):
    pass

def require(value, message):
    if not value:
        raise InvalidEvidence(message)

def contains(rect, point):
    return rect[0] <= point[0] < rect[0]+rect[2] and rect[1] <= point[1] < rect[1]+rect[3]

def fields(raw):
    return dict(re.findall(r'(\w+)=([^\s]+)', raw))

def applied_states(trace, owner, output, workspace, offset, viewport):
    """WHY: pending IPC rectangles are not applied scene origins.
    CONTRACT: PI_OWNER paired with its preceding same-output PI_SCENE only.
    INVARIANT: retain raw timestamps and identity; never use a final-row shortcut.
    """
    scenes = {}; result = []
    for raw in trace.splitlines():
        f = fields(raw)
        if 'PI_SCENE ' in raw:
            scenes[f['output']] = (f, raw)
        elif 'PI_OWNER ' in raw and f.get('id') == str(owner):
            sc = scenes.get(f.get('output'))
            if not sc or f.get('scene_valid') != '1':
                continue
            scene, scene_raw = sc
            xy = list(map(int, f['scene'].split(',')))
            size = list(map(int, f['applied_size'].split(',')))
            require(int(scene['ns']) < int(f['ns']), 'scene/owner order')
            result.append(dict(ns=int(f['ns']), owner=int(f['id']), output=f['output'],
                workspace=int(scene['workspace']), applied=True, alive=True,
                origin=[xy[i]+offset[i] for i in (0,1)], size=size,
                clip=viewport if scene['clip_valid']=='1' else None,
                layout=int(scene['layout']), raw=raw, scene_raw=scene_raw))
    return result

def wire_delivery(tail, target='TOPLEVEL'):
    """Read actual enter surface and press/release wire; callbacks alone cannot PASS."""
    enters = re.findall(r'wl_pointer#\d+\.enter\((\d+), wl_surface#(\d+), ([\d.-]+), ([\d.-]+)\)', tail)
    require(enters, 'actual recipient enter absent')
    surface = int(enters[0][1])
    callbacks = re.findall(r'POINTER_ENTER target=(\w+) wl=(\d+) serial=(\d+)', tail)
    require(callbacks and all(t==target and int(w)==surface and any(int(e[0])==int(serial) and int(e[1])==int(w) for e in enters) for t,w,serial in callbacks), 'false recipient')
    positions = re.findall(r'wl_pointer#\d+\.(?:enter\(\d+, wl_surface#\d+|motion\(\d+), ([\d.-]+), ([\d.-]+)\)', tail)
    require(positions, 'actual coordinates absent')
    buttons = re.findall(r'wl_pointer#\d+\.button\((\d+), (\d+), (\d+), ([01])\)', tail)
    cb = re.findall(r'POINTER_BUTTON target=(\w+) serial=(\d+) button=(\d+) state=([01])', tail)
    require(len(buttons)==2 and [v[3] for v in buttons]==['1','0'], 'press/release wire pair')
    require(len(cb)==2 and all(t==target and (s,b,st)==(w[0],w[2],w[3]) for (t,s,b,st),w in zip(cb,buttons)), 'serial/recipient mismatch')
    require(buttons[0][2]==buttons[1][2] and buttons[0][0]!=buttons[1][0], 'button/serial pair')
    # Position is the final wire position preceding press, not a PI_OWNER row.
    press = tail.index('.button('+buttons[0][0]+',')
    before = tail[:press]
    require('TOPLEVEL DESTROY' not in before and '.destroy()' not in before, 'delivery to destroyed surface')
    coords = re.findall(r'wl_pointer#\d+\.(?:enter\(\d+, wl_surface#\d+|motion\(\d+), ([\d.-]+), ([\d.-]+)\)', before)
    require(coords, 'no position before press')
    return dict(surface=surface, local=list(map(float,coords[-1])), buttons=[dict(serial=int(s),time_ms=int(t),button=int(b),state=int(st)) for s,t,b,st in buttons], raw=tail)

def correlate(receipt):
    require('states' in receipt and receipt.get('delivery'), 'empty PASS receipt')
    if not receipt['states']:
        return dict(status='INCONCLUSIVE',compatible_states=[],atomic_generation='NOT_PROVEN',meaning='no actual applied owner observation')
    d=receipt['delivery']; require(wire_delivery(d['raw'])==d, 'delivery differs from actual wire')
    require(d['surface']==receipt['surface'], 'wrong recipient surface')
    require(not receipt.get('other_buttons'), 'wrong client delivery')
    begin,end=receipt['interval']; require(begin<=end, 'interval ordering')
    states=receipt['states']; require(all(s.get('applied') is True for s in states), 'pending as applied')
    # WHY: sampling can straddle delivery; one observation before injection and
    # all observations through post-delivery are candidates, not atomic states.
    prior=[s['ns'] for s in states if s['ns']<=begin]
    lower=max(prior) if prior else begin
    candidates=[s for s in states if lower<=s['ns']<=end]
    if not candidates:
        return dict(status='INCONCLUSIVE',compatible_states=[],atomic_generation='NOT_PROVEN',meaning='no temporally comparable applied observation')
    matches=[]
    for s in candidates:
        if s['owner']!=receipt['owner'] or s['output']!=receipt['output'] or s['workspace']!=receipt['workspace'] or not s.get('alive'):
            continue
        p=receipt['point']; local=[p[i]-s['origin'][i] for i in (0,1)]
        if local!=d['local'] or not contains([*s['origin'],*s['size']],p): continue
        if s['clip'] is not None and not contains(s['clip'],p): continue
        matches.append(s)
    require(matches, 'no actual compatible owner/output/coordinates/clip')
    signatures={(tuple(s['origin']),tuple(s['size']),s['layout'],tuple(s['clip']) if s['clip'] else None) for s in matches}
    return dict(status='PARTIALLY_FEASIBLE' if len(signatures)==1 else 'INCONCLUSIVE',
                compatible_states=matches, interval=[begin,end], atomic_generation='NOT_PROVEN',
                meaning='sampled event-time compatibility; no common native input/scene epoch')

def standard_return(states, owner, output, workspace):
    comparable=[s for s in states if s['owner']==owner and s['output']==output and s['workspace']==workspace]
    require(comparable and all(s['applied'] and s['layout']==1 and s['clip'] is None for s in comparable), 'standard applied clip not removed')
    return 'PARTIALLY_FEASIBLE'
