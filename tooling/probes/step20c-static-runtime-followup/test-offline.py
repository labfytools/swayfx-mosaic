"""Exercise scoring against edge differences, actual paint and button events."""
from PIL import Image
from pixels import analyze, compare, interior, button_pair
x=Image.new('RGB',(800,600),(48,48,56));y=x.copy()
assert compare(x,y)['equal'];y.putpixel((799,599),(48,48,57))
r=compare(x,y);assert not r['equal'] and r['changed']==1 and r['pixels'][0]['x']==799
assert analyze(x)['count']==0
paint=Image.new('RGB',(800,600),(0,0,0))
for xx in range(482,800):
 for yy in range(25,598):paint.putpixel((xx,yy),(35,68,204))
assert analyze(paint)=={'count':182214,'bbox':(482,25,800,598)}
assert interior(paint)==(641,311)
assert len(button_pair(['BUTTON ns=1 serial=3 button=273 state=1','BUTTON ns=2 serial=4 button=273 state=0']))==2
for lines in [[],['ENTER ns=1 x=0 y=0'],['BUTTON ns=1 serial=3 button=273 state=1']]:
 try:button_pair(lines)
 except AssertionError:pass
 else:raise AssertionError('missing delivery accepted')
print('PASS exact RGB edge rejection, painted interior and real press/release scoring')
