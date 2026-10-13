"""Exact whole-image comparisons and measured interior click selection.

CONTRACT: no mask or tolerance may turn a whole-output difference into PASS.
INVARIANT: coordinates of every differing pixel are retained on failure.
"""
from PIL import Image, ImageChops
import re
COLORS = {(35,68,204),(32,208,160)}
def analyze(im):
    mask=Image.new('L',im.size)
    values=[255 if c in COLORS else 0 for c in im.get_flattened_data()]
    mask.putdata(values)
    return {'count':sum(v!=0 for v in values),'bbox':mask.getbbox()}
def compare(a,b):
    assert a.size==b.size
    points=[{'x':i%a.width,'y':i//a.width,'before':x,'after':y}
            for i,(x,y) in enumerate(zip(a.get_flattened_data(),b.get_flattened_data())) if x!=y]
    return {'equal':not points,'changed':len(points),'bbox':ImageChops.difference(a,b).getbbox(),'pixels':points}
def interior(im):
    box=analyze(im)['bbox'];assert box
    x1,y1,x2,y2=box;assert x2-x1>40 and y2-y1>40
    x,y=(x1+x2)//2,(y1+y2)//2
    assert all(im.getpixel((xx,yy)) in COLORS for xx in range(x-20,x+21) for yy in range(y-20,y+21))
    return x,y

def button_pair(lines):
    # CONTRACT: malformed or extra client button lines must never be filtered out.
    events=[]
    for line in lines:
        m=re.fullmatch(r'BUTTON ns=(\d+) serial=(\d+) button=(\d+) state=(\d+)',line)
        assert m, ('malformed button',line)
        events.append(tuple(map(int,m.groups())))
    assert len(events)==2 and [x[2:] for x in events]==[(273,1),(273,0)],events
    assert all(x[0]>0 and 0<x[1]<=0xffffffff for x in events), 'timestamp/serial bounds'
    assert events[0][0]<events[1][0] and events[0][1]!=events[1][1], 'press/release order'
    return [{'ns':x[0],'serial':x[1],'button':x[2],'state':x[3]} for x in events]


def painted_geometry(im, measured, commit):
    """Paint supplies y; applied scene and actual COMMIT supply horizontal continuation.

    WHY: window_rect.y deliberately excludes an enabled server titlebar.
    CONTRACT: require solid target paint to the viewport boundary, no guessed y.
    """
    value = analyze(im);box = value['bbox'];assert box, 'no permitted target pixels'
    x1,y1,x2,y2 = box;x,w = measured['horizontal_content']
    assert x1-800 == x and x2 == 800, 'paint/scene horizontal correlation'
    assert value['count'] == (x2-x1)*(y2-y1), 'nonrectangular target paint'
    assert y2-y1 == commit['height'] and commit['width'] == w, 'painted configured dimensions'
    assert 20 <= y1+20 < y2-20 <= 600
    return value


def click_points(left, right, measured):
    """Select from captured target pixels; H2 must be inside continuation/reference."""
    px,py = interior(left);x,w = measured['horizontal_content']
    hx = min(100,int(x+w)-30)
    assert 20 <= hx < 780 and 20 <= py < 580, 'H2 point margin'
    assert x+20 <= hx < x+w-20, 'inside continued content'
    assert all(right.getpixel((xx,yy)) == (48,48,56)
               for xx in range(hx-20,hx+21) for yy in range(py-20,py+21)), 'H2 accessible reference interior'
    return {'permitted': (px-800,py), 'forbidden': (hx,py),
            'paint_bbox': analyze(left)['bbox'], 'horizontal_content': [x,w]}


def delivery(events, recipient):
    """No fabricated recipient: only a real pair in its named client log counts."""
    assert set(events) == {'target','reference','filler'}, 'client log set'
    pair=button_pair(events[recipient])
    assert all(not rows for name,rows in events.items() if name != recipient), 'wrong recipient delivery'
    return pair
