"""Pure E2 input/lifecycle predicates shared with offline negative tests."""
import re
from model import require
from predicates import COLORS, paint, equal, pair, point


def opening_pair(lines,target,serial):
    actual=[]
    for line in lines:
        m=re.fullmatch(r'POINTER_BUTTON target=(\w+) serial=(\d+) button=(\d+) state=(\d+)',line)
        require(m is not None,'opening-button-format');actual.append([m[1],*map(int,m.groups()[1:])])
    require(len(actual)==2 and all(e[0]==target for e in actual) and
            [e[2:] for e in actual]==[[272,1],[272,0]] and actual[0][1]==serial and
            0<actual[0][1]<actual[1][1]<=0xffffffff,'real-left-opening-pair')
    return actual


def explicit_child_close(before,after,ids,request_ns,done_ns):
    """Client destroy must follow a recorded explicit request; no popup_done."""
    require(type(request_ns) is int and request_ns<done_ns,'explicit-close-request-order')
    require(after.startswith(before),'append-only-client-protocol')
    tail=after[len(before):]
    require('POPUP_DONE ' not in after,'close-must-not-be-dismissal')
    b=ids['POPUP_B'];a=ids['POPUP_A']
    destroy=f'POPUP_B DESTROY role={b[2]} xdg={b[1]} wl={b[0]}'
    require(tail.count(destroy)==1 and tail.count('COMMAND close_b DONE')==1 and
            tail.index(destroy)<tail.index('COMMAND close_b DONE'),'explicit-child-destroy-DONE')
    for obj,stem in [(b[2],'xdg_popup'),(b[1],'xdg_surface'),(b[0],'wl_surface')]:
        require(tail.count(f'{stem}#{obj}.destroy()')==1,'child-protocol-destroy')
    require(after.count(f'POPUP_A MAP wl={a[0]} xdg={a[1]}')==1 and
            'POPUP_A DESTROY ' not in after and 'TOPLEVEL DESTROY' not in after,'same-A-remains-mapped')
    return dict(status='PASS',request_ns=request_ns,done_ns=done_ns,B=b,A=a,
                meaning='explicit client close, no compositor popup_done')


def a_survival(image,before,after,ids,buttons,global_point,rect):
    a=ids['POPUP_A']
    require(paint(image,'POPUP_B')['count']==0 and paint(image,'POPUP_A')['count']>0,'child-zero-residual-A-painted')
    require(before.startswith('') and after.startswith(before),'A-input-protocol-appended')
    require('POPUP_A DESTROY ' not in after and 'POPUP_A POPUP_DONE ' not in after and
            after.count(f'POPUP_A MAP wl={a[0]} xdg={a[1]}')==1,'same-A-live-after-input')
    require(rect[0]<=global_point[0]<rect[0]+rect[2] and rect[1]<=global_point[1]<rect[1]+rect[3], 'A-recomputed-point-bounds')
    return dict(status='PASS',pair=pair(buttons,'POPUP_A'),ids=a,point=global_point)


def normal_owner_close(before,after,ids,code):
    require(code==0 and after.startswith(before),'normal-client-exit')
    tail=after[len(before):]
    require(tail.count('COMMAND close_owner')==1 and tail.count('TOPLEVEL DESTROY')==1 and
            'POPUP_DONE ' not in tail,'normal-owner-close-command')
    a=ids['POPUP_A'];top=ids['TOPLEVEL']
    require(tail.count(f'POPUP_A DESTROY role={a[2]} xdg={a[1]} wl={a[0]}')==1 and
            tail.index('COMMAND close_owner')<tail.index('POPUP_A DESTROY ')<tail.index('TOPLEVEL DESTROY'),
            'normal-owner-child-first-destruction')
    for obj,stem in [(a[2],'xdg_popup'),(a[1],'xdg_surface'),(a[0],'wl_surface'),
                     (top[2],'xdg_toplevel'),(top[1],'xdg_surface'),(top[0],'wl_surface')]:
        require(tail.count(f'{stem}#{obj}.destroy()')==1,'owner-protocol-destroy')
    return dict(status='PASS',client_exit=code,ids=ids)


def final_restoration(baseline,final):
    cmp=equal(baseline,final)
    require(cmp['equal'] and all(paint(final,n)['count']==0 for n in ('POPUP_A','POPUP_B')),'whole-H2-final-exact')
    return dict(status='PASS',comparison=cmp)
