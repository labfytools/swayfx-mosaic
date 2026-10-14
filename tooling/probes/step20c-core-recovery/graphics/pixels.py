"""Exact binary RGB masks with explicit output origin, clip and occlusion.

Screenshots prove color/visible geometry only, never native-buffer identity.
"""
from PIL import Image,ImageChops,ImageDraw
from model import *
COLORS=dict(TOPLEVEL=(35,68,204),POPUP_A=(224,192,32),POPUP_B=(32,208,160))


def color_geometry(im,target,rect,output,clip,occluders=()):
    require(im.size==(output.rectangle.width,output.rectangle.height),'replay-output-size')
    visible=intersect(rect,clip) if clip else rect
    expected=Image.new('L',im.size,0);draw=ImageDraw.Draw(expected)
    box=to_png(visible,output)
    if box.width and box.height:draw.rectangle((box.x,box.y,box.end[0]-1,box.end[1]-1),fill=255)
    for occ in occluders:
        ob=to_png(occ,output)
        if ob.width and ob.height:draw.rectangle((ob.x,ob.y,ob.end[0]-1,ob.end[1]-1),fill=0)
    actual=Image.new('L',im.size);actual.putdata([255 if px==COLORS[target] else 0 for px in im.get_flattened_data()])
    require(ImageChops.difference(expected,actual).getbbox() is None,'replay-paint-'+target)
    return dict(count=sum(actual.histogram()[1:]),bbox=actual.getbbox())
