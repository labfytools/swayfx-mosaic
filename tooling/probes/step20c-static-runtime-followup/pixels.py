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
    events=[re.search(r'BUTTON ns=(\d+) serial=(\d+) button=(\d+) state=(\d+)',x) for x in lines]
    events=[tuple(map(int,x.groups())) for x in events if x]
    assert len(events)==2 and [x[2:] for x in events]==[(273,1),(273,0)],events
    assert all(x[1]>0 for x in events)
    return [{'ns':x[0],'serial':x[1],'button':x[2],'state':x[3]} for x in events]
