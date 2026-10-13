#!/usr/bin/env python3
"""Synthetic negative branches and real historical replay; never launch clients."""
import argparse
from dataclasses import replace
import json
from pathlib import Path
import tempfile
import threading
import unittest
import sys
import re
from PIL import Image
import model as m
from model import *
from predicates import geometry,protocol,dismissal,terminal,root_clip,Defect,popup_pixels,COLORS,point,pair,mapped
from ledger import initial_for_offline_test,reserve,valid,LIMITS
from authorization import authorize,THIS_TICKET,MARKER
from replay import replay_native,replay_nested,color_geometry,HISTORICAL,NESTED
from support import save

HERE=Path(__file__).resolve().parent
RECEIPTS=[]
FIXTURE_SNAPSHOT=None
BASELINE_CHECKED=False
BOOTSTRAP=False
ACTIVE=None
TRACKED={str(p.resolve()) for p in HERE.glob('*.py')}
LINES={}
CONTRACTS={}
FAILED={}

def trace(frame,event,arg):
    if ACTIVE and event=='line' and frame.f_code.co_filename in TRACKED:
        key=frame.f_code.co_filename+':'+str(frame.f_lineno)
        LINES.setdefault(ACTIVE,set()).add(key)
    if ACTIVE and event=='exception' and arg[0] in (AssertionError,Invalid,Defect):
        FAILED.setdefault(ACTIVE,set()).add(frame.f_code.co_filename+':'+str(frame.f_lineno))
    if ACTIVE and event=='return' and frame.f_code.co_name=='require':
        contract=frame.f_locals.get('contract');value=frame.f_locals.get('value')
        CONTRACTS.setdefault(ACTIVE,set()).add((contract,bool(value)))
    # CONTRACT: a rejected aggregation gate is an observed false predicate,
    # not a raised exception and not a new graphical/scientific measurement.
    if ACTIVE and event=='return' and frame.f_code.co_name=='need' and frame.f_code.co_filename==str(HERE/'write_results.py'):
        ok=bool(frame.f_locals.get('ok'));name=frame.f_locals.get('name')
        CONTRACTS.setdefault(ACTIVE,set()).add(('aggregate/'+str(name),ok))
        if not ok and frame.f_back:
            FAILED.setdefault(ACTIVE,set()).add(frame.f_back.f_code.co_filename+':'+str(frame.f_back.f_lineno))
    return trace

class Case(unittest.TestCase):
    def setUp(self):
        global ACTIVE
        ACTIVE=self.id();self.p=Provenance(9,6,'applied-1','synthetic applied trace')
        self.a=Applied(Rect(Space.GLOBAL,-320,0,640,600,self.p),Rect(Space.CONTENT,2,0,636,573,self.p),Rect(Space.CONFIGURE,0,0,636,573,self.p),Native(Rect(Space.NATIVE,0,0,420,320,self.p),12,1680,1,20),2,25,25,21)
        self.r=content(self.a);self.o=Output('H1',Rect(Space.GLOBAL,-800,0,800,600,self.p),1.0,'normal');self.clip=Rect(Space.VIEWPORT,-800,0,800,600,self.p)
    def tearDown(self):
        global ACTIVE
        ACTIVE=None
    def reject(self,contract,fn):
        with self.assertRaisesRegex(Invalid,'^'+re.escape(contract)+'$'):fn()
    def test_positive_geometry(self):
        self.assertEqual(self.r.values(),[-318,25,636,573]);self.assertEqual(to_png(intersect(self.r,self.clip),self.o).values(),[482,25,318,573])
        self.assertEqual(from_png(Rect(Space.PNG,482,25,318,573,self.p),self.o).values(),[-318,25,318,573])
        verify_paint(self.r,self.o,[482,25,800,598],182214,self.clip)
    def test_negative_native_height(self):self.reject('paint-origin-intersection',lambda:verify_paint(replace(self.r,height=320),self.o,[482,25,800,598],182214,self.clip))
    def test_negative_scene_window_y(self):self.reject('paint-origin-intersection',lambda:verify_paint(replace(self.r,y=0),self.o,[482,25,800,598],182214,self.clip))
    def test_negative_titlebar(self):self.reject('titlebar-content-offset',lambda:content(replace(self.a,titlebar=0)))
    def test_negative_output_origin(self):self.reject('paint-origin-intersection',lambda:verify_paint(self.r,replace(self.o,rectangle=replace(self.o.rectangle,x=0)),[482,25,800,598],182214,self.clip))
    def test_negative_png_space(self):self.reject('global-to-png-spaces',lambda:to_png(replace(self.r,space=Space.PNG),self.o))
    def test_negative_png_bounds(self):self.reject('png-bounds',lambda:from_png(Rect(Space.PNG,-1,25,318,573,self.p),self.o))
    def test_negative_assignment(self):self.reject('configure-assignment',lambda:content(replace(self.a,configured=replace(self.a.configured,width=420))))
    def test_negative_workspace(self):self.reject('workspace-identity',lambda:content(replace(self.a,window=replace(self.a.window,provenance=replace(self.p,workspace=7)))))
    def test_negative_owner(self):self.reject('owner-identity',lambda:content(replace(self.a,window=replace(self.a.window,provenance=replace(self.p,owner=10)))))
    def test_negative_old_camera(self):self.reject('applied-generation',lambda:intersect(self.r,replace(self.clip,provenance=replace(self.p,generation='old-camera'))))
    def test_negative_local_global_clip(self):self.reject('global-intersection',lambda:intersect(self.r,replace(self.clip,space=Space.CONTENT)))
    def test_negative_buffer_identity(self):self.reject('native-buffer-identity',lambda:content(replace(self.a,native=replace(self.a.native,buffer_id=0))))
    def test_negative_pending(self):self.reject('pending-not-applied',lambda:content(replace(self.a,scene=replace(self.a.scene,provenance=replace(self.p,state='pending')))))
    def test_negative_scale(self):self.reject('unmeasured-output-scale',lambda:to_png(self.r,replace(self.o,scale=2.0)))
    def test_negative_transform(self):self.reject('unmeasured-output-transform',lambda:to_png(self.r,replace(self.o,transform='90')))
    def test_positive_popup(self):
        A=popup(self.r,Rect(Space.POPUP,100,80,350,170,self.p),9,9,22,True)
        B=popup(A,Rect(Space.POPUP,100,60,300,130,self.p),12,12,23,True)
        self.assertEqual(A.values(),[-218,105,350,170]);self.assertEqual(B.values(),[-118,165,300,130]);self.assertEqual(crossing(B,0),'EXERCISED')
        self.assertEqual(crossing(replace(B,x=1),0),'NOT EXERCISED')
        pointer_local((-100,175),B,(18,10));constraints(0,[100,80,350,170],[100,80,350,170])
        self.assertEqual(local_clip_to_global(Rect(Space.CONTENT,-482,-25,800,600,self.p),(-318,25),self.p).values(),[-800,0,800,600])
    def test_negative_parent(self):self.reject('xdg-parent',lambda:popup(self.r,Rect(Space.POPUP,100,80,350,170,self.p),11,9,22,True))
    def test_negative_ack(self):self.reject('popup-ack',lambda:popup(self.r,Rect(Space.POPUP,100,80,350,170,self.p),9,9,0,True))
    def test_negative_map(self):self.reject('popup-map',lambda:popup(self.r,Rect(Space.POPUP,100,80,350,170,self.p),9,9,22,False))
    def test_negative_constraints(self):self.reject('zero-flags-no-adjustment',lambda:constraints(0,[100,80,350,170],[99,80,350,170]))
    def test_negative_pointer(self):self.reject('pointer-local-correlation',lambda:pointer_local((-308,35),self.r,(0,0)))
    def test_negative_occlusion(self):
        im=Image.new('RGB',(800,600));r=Rect(Space.GLOBAL,-800,0,1,1,self.p)
        self.reject('replay-paint-POPUP_A',lambda:color_geometry(im,'POPUP_A',r,self.o,None))
    def test_negative_standard_stale_origin(self):self.reject('fresh-standard-generation',lambda:fresh_standard(self.r,self.r))
    def test_positive_standard_fresh(self):self.assertEqual(fresh_standard(self.r,replace(self.r,x=-398,provenance=replace(self.p,generation='standard-2'))).x,-398)
    def test_negative_E2_identity(self):self.reject('fresh-E2-identity',lambda:fresh_chain(dict(owner=9,pid=10,serials=[1,2]),dict(owner=9,pid=11,serials=[3,4])))
    def test_negative_E2_serials(self):self.reject('fresh-E2-serials',lambda:fresh_chain(dict(owner=9,pid=10,serials=[1,2]),dict(owner=10,pid=11,serials=[2,3])))
    def test_positive_E2(self):fresh_chain(dict(owner=9,pid=10,serials=[1,2]),dict(owner=10,pid=11,serials=[3,4]))
    def test_positive_terminal(self):
        for ipc in (0,1):self.assertTrue(terminal(True,ipc,0,"Handling command 'exit'\nShutting down sway",False,False,stdout='actual reply',stderr='actual stderr')['scientific_cleanup_pass'])
    def test_negative_terminal_incomplete(self):self.assertFalse(terminal(False,1,0,"Handling command 'exit'\nShutting down sway",False,False)['scientific_cleanup_pass'])
    def test_negative_terminal_unhandled(self):self.assertFalse(terminal(True,1,0,'Shutting down sway',False,False)['scientific_cleanup_pass'])
    def test_negative_terminal_compositor(self):self.assertFalse(terminal(True,1,1,"Handling command 'exit'\nShutting down sway",False,False)['scientific_cleanup_pass'])
    def test_negative_terminal_protocol(self):self.assertFalse(terminal(True,1,0,"Handling command 'exit'\nShutting down sway",True,False)['scientific_cleanup_pass'])
    def test_negative_terminal_rescue(self):self.assertFalse(terminal(True,1,0,"Handling command 'exit'\nShutting down sway",False,True)['scientific_cleanup_pass'])
    def test_negative_dismissal_hit(self):
        with self.assertRaisesRegex(Defect,'invisible popup'):dismissal('POPUP_B POPUP_DONE \nPOPUP_A POPUP_DONE \nPOPUP_B DESTROY \nPOPUP_A DESTROY ',['POINTER_BUTTON target=POPUP_B serial=22 button=273 state=1'])
    def test_negative_dismissal_incomplete(self):
        with self.assertRaises(AssertionError):dismissal('POPUP_A POPUP_DONE ',[])
    def test_positive_dismissal(self):self.assertEqual(dismissal('POPUP_B POPUP_DONE \nPOPUP_A POPUP_DONE \nPOPUP_B DESTROY \nPOPUP_A DESTROY ',[])['status'],'PASS')
    def test_positive_button(self):pair(['POINTER_BUTTON target=POPUP_B serial=22 button=273 state=1','POINTER_BUTTON target=POPUP_B serial=23 button=273 state=0'],'POPUP_B')
    def test_negative_button(self):
        with self.assertRaises(Defect):pair(['POINTER_BUTTON target=POPUP_A serial=22 button=273 state=1'],'POPUP_B')
    def test_negative_root_ambiguous(self):
        trace='PI_OWNER output=HEADLESS-1 ns=10 id=9 scene_valid=1\nPI_POPUP output=HEADLESS-1 ns=11 local_index=1 tree=0x1 enabled=1 clip_valid=1 clip=-482,-25,800,600\nPI_POPUP output=HEADLESS-1 ns=12 local_index=2 tree=0x2 enabled=1 clip_valid=1 clip=-482,-25,800,600'
        self.reject('root-chain-unique',lambda:root_clip(trace,[-318,25],True,9,1,20))
    def test_positive_root(self):
        trace='PI_OWNER output=HEADLESS-1 ns=10 id=9 scene_valid=1\nPI_POPUP output=HEADLESS-1 ns=11 local_index=1 tree=0x1 enabled=1 clip_valid=1 clip=-482,-25,800,600'
        self.assertTrue(root_clip(trace,[-318,25],True,9,1,20)['clip_valid'])
    def test_negative_future_gate(self):self.reject('explicit-future-authorization-required',lambda:authorize('/does/not/exist',None))
    def test_negative_current_ticket_gate(self):
        with tempfile.TemporaryDirectory(prefix='geometry-auth-test-') as tmp:
            f=Path(tmp)/'auth.json';f.write_text(json.dumps(dict(scope='one-new-static-nested-headless-run',explicit_user_authorization=True,ticket=THIS_TICKET)))
            self.reject('distinct-future-ticket-required',lambda:authorize(tmp,f))
    def test_real_native_replay(self):replay_native(LAB)
    def test_real_nested_replay(self):
        rows=replay_nested(LAB)
        crossing=next(r for r in rows if r['case']=='run-private_mosaic-crossing-b_cross')
        self.assertEqual(crossing['B'][:2],[662,165])
        standard=next(r for r in rows if r['case']=='run-private_mosaic-toggle-b_cross')
        sample=next(c for c in standard['input_correlation']['callbacks'] if c['target']=='POPUP_B')
        self.assertEqual(sample['origin'],[622,165]);self.assertEqual(sample['global_point'],[900,190]);self.assertEqual(sample['local'],[278,25])
    def test_positive_protocol(self):protocol(self.protocol_text())
    def protocol_text(self):
        text=(NESTED/'run-private_mosaic-crossing-b_cross/client.log').read_text();return text[:text.index('POPUP_B POPUP_DONE ')]
    def test_negative_protocol_serial(self):
        with self.assertRaises(AssertionError):protocol(self.protocol_text().replace('serial=55 used=55','serial=0 used=0'))
    def test_negative_protocol_missing_serial(self):
        with self.assertRaises(AssertionError):protocol(self.protocol_text().replace('POPUP_A GRAB_REQUEST','MISSING GRAB_REQUEST'))
    def test_negative_protocol_parent(self):
        with self.assertRaises(AssertionError):protocol(self.protocol_text().replace('parent=POPUP_A parent_xdg=12','parent=TOPLEVEL parent_xdg=9'))
    def test_negative_protocol_ACK(self):
        with self.assertRaises(AssertionError):protocol(self.protocol_text().replace('xdg_surface#12.ack_configure(56)','xdg_surface#12.ack_configure(0)'))
    def test_negative_protocol_map(self):
        with self.assertRaises(AssertionError):protocol(self.protocol_text().replace('POPUP_B MAP ','POPUP_B NOTMAP '))
    def test_negative_protocol_reused_objects(self):
        with self.assertRaises(AssertionError):protocol(self.protocol_text().replace('POPUP_B CREATE wl=13','POPUP_B CREATE wl=11'))
    def test_positive_ledger_exhaustion(self):
        with tempfile.TemporaryDirectory(prefix='geometry-ledger-test-') as tmp:
            p=Path(tmp)/'budget.json';initial_for_offline_test(p);reserve(p,'run');before=p.read_bytes()
            self.reject('ledger-exhausted',lambda:reserve(p,'run'));self.assertEqual(p.read_bytes(),before)
            with self.assertRaises(FileExistsError):initial_for_offline_test(p)
    def test_negative_ledger_corruption(self):
        with tempfile.TemporaryDirectory(prefix='geometry-ledger-test-') as tmp:
            p=Path(tmp)/'budget.json';initial_for_offline_test(p);s=json.loads(p.read_text());s['used']['run']=True;p.write_text(json.dumps(s))
            self.reject('ledger-counts',lambda:reserve(p,'run'))
            s['used']['run']=1;p.write_text(json.dumps(s));self.reject('ledger-events',lambda:reserve(p,'run'))
    def test_positive_ledger_concurrency(self):
        with tempfile.TemporaryDirectory(prefix='geometry-ledger-test-') as tmp:
            p=Path(tmp)/'budget.json';initial_for_offline_test(p);wins=[];fails=[]
            def debit():
                try:reserve(p,'run');wins.append(1)
                except Invalid:fails.append(1)
            ts=[threading.Thread(target=debit) for _ in range(8)]
            for t in ts:t.start()
            for t in ts:t.join()
            self.assertEqual((len(wins),len(fails)),(1,7));valid(json.loads(p.read_text()))
    def test_negative_ledger_partial_bundle(self):
        with tempfile.TemporaryDirectory(prefix='geometry-ledger-test-') as tmp:
            p=Path(tmp)/'budget.json';initial_for_offline_test(p);reserve(p,'run');before=p.read_bytes()
            self.reject('ledger-exhausted',lambda:reserve(p,'click','run'));self.assertEqual(before,p.read_bytes())
    def test_negative_ledger_unknown(self):
        with tempfile.TemporaryDirectory(prefix='geometry-ledger-test-') as tmp:
            p=Path(tmp)/'budget.json';initial_for_offline_test(p);self.reject('ledger-debit-kinds',lambda:reserve(p,'reset'))
    def test_negative_ledger_missing(self):self.reject('existing-ledger-required',lambda:reserve('/tmp/absent-geometry-ledger-never-created','run'))

    def test_positive_empty_intersection(self):
        r=replace(self.r,x=1000);verify_paint(r,self.o,None,0,self.clip)
        self.assertEqual(to_png(r,self.o).width,0)
    def popup_images(self,mosaic):
        from PIL import ImageDraw
        g={'A':[-20,10,40,40],'B':[-10,20,30,20],'provenance':dict(owner=9,workspace=6,generation='applied-1',evidence='synthetic mask',state='applied')}
        ims=[]
        for ox in (-800,0):
            im=Image.new('RGB',(800,600),(48,48,56));draw=ImageDraw.Draw(im)
            for key,name in [('A','POPUP_A'),('B','POPUP_B')]:
                x,y,w,h=g[key];left=max(x,ox);right=min(x+w,ox+800)
                if left<right and (not mosaic or ox==-800):draw.rectangle((left-ox,y,right-ox-1,y+h-1),fill=COLORS[name])
            ims.append(im)
        return g,*ims,Image.new('RGB',(800,600),(48,48,56))
    def test_positive_popup_pixels(self):
        for mosaic in (True,False):
            g,left,right,base=self.popup_images(mosaic);popup_pixels(left,right,g,mosaic,base)
    def test_negative_popup_pixels_forbidden(self):
        g,left,right,base=self.popup_images(True);right.putpixel((1,21),COLORS['POPUP_B'])
        self.reject('replay-paint-POPUP_B',lambda:popup_pixels(left,right,g,True,base))
    def test_negative_popup_pixels_occlusion(self):
        g,left,right,base=self.popup_images(True);left.putpixel((795,21),COLORS['POPUP_A'])
        self.reject('replay-paint-POPUP_A',lambda:popup_pixels(left,right,g,True,base))
    def test_negative_popup_pixels_reference(self):
        g,left,right,base=self.popup_images(True);right.putpixel((300,300),(1,2,3))
        with self.assertRaises(Defect):popup_pixels(left,right,g,True,base)
    def test_negative_popup_pixels_provenance(self):
        g,left,right,base=self.popup_images(True);g.pop('provenance');self.reject('popup-paint-provenance',lambda:popup_pixels(left,right,g,True,base))
    def test_negative_popup_pixels_standard_absent(self):
        g,left,right,base=self.popup_images(True)
        self.reject('replay-paint-POPUP_A',lambda:popup_pixels(left,right,g,False,base))
    def test_negative_output_image_dimensions(self):
        self.reject('replay-output-size',lambda:color_geometry(Image.new('RGB',(799,600)),'TOPLEVEL',self.r,self.o,None))
    def historical_applied_inputs(self):
        from observations import applied_model
        cal=json.loads((HISTORICAL/'results/camera-calibration.json').read_text())[-1]
        measured={**cal['after_owner'],'workspace':cal['scene']['workspace']};return measured,measured['IPC'],(HISTORICAL/'run/E1.log').read_text()
    def test_negative_native_natural_geometry(self):
        from observations import applied_model
        measured,owner,text=self.historical_applied_inputs();changed={**owner,'geometry':{**owner['geometry'],'x':1}}
        measured['IPC']=changed;self.reject('native-natural-geometry',lambda:applied_model(measured,changed,text,'test'))
    def test_positive_applied_adapter(self):
        from observations import applied_model,output_model,viewport_model
        measured,owner,text=self.historical_applied_inputs();a=applied_model(measured,owner,text,'historical-adapter');self.assertEqual(a.configure_ack,21)
        snap=json.loads((HISTORICAL/'results/E1-applied-snapshot.json').read_text());output_model(snap,'HEADLESS-1',a.scene.provenance)
        viewport_model({'workspace':6,'clip_valid':True,'global_clip':[-800,0,800,600]},a.scene.provenance)
    def test_negative_applied_adapter_owner(self):
        from observations import applied_model
        measured,owner,text=self.historical_applied_inputs();self.reject('measured-owner-identity',lambda:applied_model({**measured,'id':10},owner,text,'test'))
    def test_negative_applied_adapter_workspace(self):
        from observations import applied_model
        measured,owner,text=self.historical_applied_inputs();measured.pop('workspace');self.reject('measured-workspace-required',lambda:applied_model(measured,owner,text,'test'))
    def test_negative_native_trace_missing(self):
        from observations import applied_model
        measured,owner,text=self.historical_applied_inputs();self.reject('native-shm-trace-required',lambda:applied_model(measured,owner,text.replace('create_buffer(','not_create_buffer['),'test'))
    def test_negative_native_trace_after_map(self):
        from observations import applied_model
        measured,owner,text=self.historical_applied_inputs();self.reject('toplevel-buffer-before-map',lambda:applied_model(measured,owner,'TOPLEVEL MAP early\n'+text,'test'))
    def test_negative_native_attach(self):
        from observations import applied_model
        measured,owner,text=self.historical_applied_inputs();self.reject('native-toplevel-attach',lambda:applied_model(measured,owner,text.replace('wl_surface#3.attach(wl_buffer#12','wl_surface#3.attach(wl_buffer#999'),'test'))
    def test_negative_toplevel_configure_missing(self):
        from observations import applied_model
        measured,owner,text=self.historical_applied_inputs();self.reject('toplevel-configure-required',lambda:applied_model(measured,owner,text.replace('TOPLEVEL ROLE_CONFIGURE w=636 h=573','TOPLEVEL ROLE_CONFIGURE w=0 h=0'),'test'))
    def test_negative_assigned_ACK_trace(self):
        from observations import applied_model
        measured,owner,text=self.historical_applied_inputs();self.reject('assigned-ack-trace',lambda:applied_model(measured,owner,text.replace('xdg_surface#9.ack_configure(21)','xdg_surface#9.ack_configure(999)'),'test'))
    def test_negative_output_unique(self):
        from observations import output_model
        self.reject('unique-active-output',lambda:output_model({'outputs':[]},'HEADLESS-1',self.p))
    def test_negative_viewport_workspace(self):
        from observations import viewport_model
        self.reject('viewport-workspace',lambda:viewport_model({'workspace':7,'clip_valid':True,'global_clip':[-800,0,800,600]},self.p))
    def test_negative_viewport_valid(self):
        from observations import viewport_model
        self.reject('viewport-applied-valid',lambda:viewport_model({'workspace':6,'clip_valid':False,'global_clip':[-800,0,800,600]},self.p))
    def test_positive_client_preparation(self):
        from prepare_clients import prepare
        with tempfile.TemporaryDirectory(prefix='geometry-client-compile-test-') as tmp:
            lab=Path(tmp);(lab/'raw').mkdir();(lab/'results').mkdir();prepare(lab)
    def test_negative_client_source_identity(self):
        import prepare_clients as pc
        from unittest.mock import patch
        import shutil
        with tempfile.TemporaryDirectory(prefix='geometry-client-identity-test-') as tmp:
            root=Path(tmp);(root/'raw').mkdir();(root/'results').mkdir();fake=root/'probes'
            for dirname in ('step20c-nested-grab','step20c-valid-grab','step20c-saved-target-timeout-input','step20c-static-nested-grab'):(fake/dirname).mkdir(parents=True)
            for rel in ('step20c-nested-grab/nested-client.c','step20c-valid-grab/pointer-daemon.c','step20c-saved-target-timeout-input/static-reference.c','step20c-saved-target-timeout-input/saved-client.c','step20c-static-nested-grab/placement.patch'):
                shutil.copyfile(pc.PROBES/rel,fake/rel)
            nested=fake/'step20c-nested-grab/nested-client.c';nested.write_text(nested.read_text()+'\n/* corrupted fixture identity */\n')
            with patch.object(pc,'PROBES',fake):self.reject('frozen-nested-source',lambda:pc.prepare(root))
    def test_negative_client_placement_identity(self):
        import prepare_clients as pc
        from unittest.mock import patch
        import shutil
        with tempfile.TemporaryDirectory(prefix='geometry-client-identity-test-') as tmp:
            root=Path(tmp);(root/'raw').mkdir();(root/'results').mkdir();fake=root/'probes'
            for dirname in ('step20c-nested-grab','step20c-valid-grab','step20c-saved-target-timeout-input','step20c-static-nested-grab'):(fake/dirname).mkdir(parents=True)
            for rel in ('step20c-nested-grab/nested-client.c','step20c-valid-grab/pointer-daemon.c','step20c-saved-target-timeout-input/static-reference.c','step20c-saved-target-timeout-input/saved-client.c'):
                shutil.copyfile(pc.PROBES/rel,fake/rel)
            (fake/'step20c-static-nested-grab/placement.patch').write_text('corrupt recorded patch')
            with patch.object(pc,'PROBES',fake):self.reject('byte-identical-placement',lambda:pc.prepare(root))
    def altered_client_contract(self,field,contract):
        import prepare_clients as pc
        from unittest.mock import patch
        import shutil
        with tempfile.TemporaryDirectory(prefix='geometry-client-contract-test-') as tmp:
            root=Path(tmp);(root/'raw').mkdir();(root/'results').mkdir();here=root/'fixture';here.mkdir();shutil.copyfile(pc.HERE/'placement.patch',here/'placement.patch')
            data=json.loads((pc.HERE/'client-contract.json').read_text())
            if field=='adapted':data['adapted_nested_sha256']='corrupt hash'
            else:data['protocols'][field]='corrupt hash'
            (here/'client-contract.json').write_text(json.dumps(data))
            with patch.object(pc,'HERE',here):self.reject(contract,lambda:pc.prepare(root))
    def test_negative_client_adapted_identity(self):self.altered_client_contract('adapted','byte-identical-adapted-client')
    def test_negative_client_xdg_header(self):self.altered_client_contract('xdg-shell-client.h','byte-identical-protocol-xdg-shell-client.h')
    def test_negative_client_xdg_code(self):self.altered_client_contract('xdg-shell-protocol.c','byte-identical-protocol-xdg-shell-protocol.c')
    def test_negative_client_pointer_header(self):self.altered_client_contract('virtual-pointer-client.h','byte-identical-protocol-virtual-pointer-client.h')
    def test_negative_client_pointer_code(self):self.altered_client_contract('virtual-pointer-protocol.c','byte-identical-protocol-virtual-pointer-protocol.c')
    def test_positive_owner_occlusion(self):
        from observations import verify_owner_occlusion
        left=Image.new('RGB',(800,600));right=Image.new('RGB',(800,600));r=Rect(Space.GLOBAL,-800,0,1,1,self.p);left.putpixel((0,0),COLORS['TOPLEVEL'])
        g={'A':[1000,0,1,1],'B':[1000,0,1,1]};verify_owner_occlusion(left,right,r,g,True)
        left.putpixel((0,0),(0,0,0));self.reject('replay-paint-TOPLEVEL',lambda:verify_owner_occlusion(left,right,r,g,True))
    def test_positive_inventory_checker(self):
        self.make_register_check()
    def make_register_check(self,corrupt=None,contract=None,proof=None):
        from assertions import HERE,REPO,HISTORY,HISTORICAL_FILES,inventory,classify,check
        from support import sha
        with tempfile.TemporaryDirectory(prefix='geometry-register-test-') as tmp:
            lab=Path(tmp);(lab/'results').mkdir()
            paths=[HISTORY/n for n in HISTORICAL_FILES]+[HERE/'model.py']
            records=[classify(r) for p in paths for r in inventory(p)]
            for r in records:r.update(positive_executed_test_ids=[],negative_executed_test_ids=[],test_status='NOT TESTED runtime dependency')
            register={'source_inventory':{str(p.relative_to(REPO)):sha(p) for p in paths},'records':records}
            if corrupt:corrupt(register)
            (lab/'results/assertion-register.json').write_text(json.dumps(register));(lab/'results/test-receipts.json').write_text(json.dumps({'tests':proof or []}))
            if contract:self.reject(contract,lambda:check(lab))
            else:self.assertEqual(check(lab)['historical_asserts'],145)
    def test_negative_inventory_counterfeit_receipt(self):
        self.make_register_check(lambda r:r['records'][0].update(positive_executed_test_ids=['already-passed-other-test']),'register-predicate-receipt-correlation',[{'id':'already-passed-other-test','status':'PASS','executed_lines':[]}])
    def test_negative_inventory_missing(self):self.make_register_check(lambda r:r['records'].pop(),'register-exhaustive-unique')
    def test_negative_inventory_duplicate(self):self.make_register_check(lambda r:r['records'].append(r['records'][0]),'register-exhaustive-unique')
    def test_negative_inventory_stale_source(self):self.make_register_check(lambda r:r['source_inventory'].update({next(iter(r['source_inventory'])):'wrong'}),'register-source-freshness')
    def test_negative_inventory_unclassified(self):self.make_register_check(lambda r:r['records'][0].update(domain=''),'register-classified')
    def test_negative_inventory_stale_AST(self):self.make_register_check(lambda r:r['records'][0].update(canonical_hash='wrong'),'register-ast-freshness')
    def test_negative_inventory_untested_claim(self):self.make_register_check(lambda r:r['records'][0].update(positive_executed_test_ids=['never executed']),'register-executed-receipts')
    def test_positive_authorization_pure(self):
        with tempfile.TemporaryDirectory(prefix='geometry-auth-test-') as tmp:
            root=Path(tmp);(root/'results').mkdir()
            auth=dict(scope='one-new-static-nested-headless-run',explicit_user_authorization=True,ticket='synthetic-future-unit-test',registered_lab=str(root),owner_registry='test-only-owner',binary='test-only-binary',binary_sha256='test-only-hash',wlroots_sha256='test-only-hash')
            f=root/'auth.json';f.write_text(json.dumps(auth));(root/'results/offline-gate.json').write_text(json.dumps(dict(marker=MARKER)));(root/'results/independent-review.json').write_text(json.dumps(dict(status='ACCEPTED',independent=True)))
            self.assertEqual(authorize(root,f),auth)
            (root/'run').mkdir();self.reject('fresh-run-required',lambda:authorize(root,f));(root/'run').rmdir()
            (root/'results/independent-review.json').write_text(json.dumps(dict(status='NOT TESTED',independent=True)))
            self.reject('completed-offline-review-required',lambda:authorize(root,f))
            (root/'results/independent-review.json').write_text(json.dumps(dict(status='ACCEPTED',independent=True)));auth.pop('binary');f.write_text(json.dumps(auth));self.reject('future-input-provenance',lambda:authorize(root,f))
            auth['registered_lab']='wrong';f.write_text(json.dumps(auth));self.reject('registered-fresh-lab-required',lambda:authorize(root,f))
    def test_negative_offline_lab_authorization(self):
        with tempfile.TemporaryDirectory(prefix='geometry-auth-test-') as tmp:
            root=Path(tmp);f=root/'auth.json';f.write_text(json.dumps(dict(scope='one-new-static-nested-headless-run',explicit_user_authorization=True,ticket='synthetic-future-unit-test',registered_lab=str(HISTORICAL.resolve()))))
            self.reject('historical-or-offline-lab-forbidden',lambda:authorize(HISTORICAL,f))
    def test_negative_ledger_sequences(self):
        with tempfile.TemporaryDirectory(prefix='geometry-ledger-test-') as tmp:
            p=Path(tmp)/'budget.json';initial_for_offline_test(p);reserve(p,'click');state=json.loads(p.read_text());state['events'][0]['seq']=5
            self.reject('ledger-sequences',lambda:valid(state));state['events'][0]['seq']=0;state['events'][0]['kind']='run'
            self.reject('ledger-accounting',lambda:valid(state));state['limits']['run']=2;self.reject('ledger-schema',lambda:valid(state))
    def test_negative_ledger_test_scope(self):
        with tempfile.TemporaryDirectory(prefix='geometry-other-test-') as tmp:self.reject('test-ledger-only',lambda:initial_for_offline_test(Path(tmp)/'budget.json'))
    def test_positive_negative_geometry_shared_protocol(self):
        g=geometry(self.protocol_text(),[-318,25],self.p)
        self.assertEqual(g['A'],[-118,105,300,170]);self.assertEqual(g['B'],[102,165,300,130]);self.assertEqual(g['crossing']['B'],'NOT EXERCISED')
        self.reject('popup-owner-provenance-required',lambda:geometry(self.protocol_text(),[-318,25]))
    def test_negative_popup_native_attach(self):
        text=self.protocol_text();text=re.sub(r'wl_surface#11.attach\(wl_buffer#\d+', 'wl_surface#11.attach(null',text)
        self.reject('popup-native-attach',lambda:protocol(text))
    def test_negative_popup_native_size(self):
        text=self.protocol_text();text=text.replace(', 0, 300, 170, 1200, 1)',', 0, 299, 170, 1196, 1)')
        self.reject('popup-native-configured-size',lambda:protocol(text))
    def test_negative_debug_parent(self):
        self.reject('debug-parent-request',lambda:protocol(self.protocol_text().replace('xdg_surface#12.get_popup','xdg_surface#999.get_popup')))
    def test_negative_debug_button(self):
        self.reject('debug-real-button-serial',lambda:protocol(self.protocol_text().replace('wl_pointer#8.button(55,','wl_pointer#8.button(999,')))
    def test_negative_debug_popup_configure(self):
        self.reject('debug-popup-configure',lambda:protocol(self.protocol_text().replace('xdg_popup#14.configure(200,','xdg_popup#14.configure(999,')))
    def test_negative_debug_xdg_configure(self):
        self.reject('debug-xdg-configure',lambda:protocol(self.protocol_text().replace('xdg_surface#12.configure(56)','xdg_surface#12.configure(999)')))
    def test_negative_root_missing(self):self.reject('bounded-root-owner-observations',lambda:root_clip('',[-318,25],True,9,1,20))
    def test_negative_root_format(self):self.reject('root-trace-format',lambda:root_clip('PI_OWNER output=HEADLESS-1 ns=10 id=9 x\nPI_POPUP output=HEADLESS-1 ns=11 bad',[-318,25],True,9,1,20))
    def test_negative_root_state(self):
        text='PI_OWNER output=HEADLESS-1 ns=10 id=9 x\nPI_POPUP output=HEADLESS-1 ns=11 local_index=1 tree=0x1 enabled=1 clip_valid=0 clip=0,0,0,0'
        with self.assertRaises(Defect):root_clip(text,[-318,25],True,9,1,20)
        self.assertFalse(root_clip(text,[-318,25],False,9,1,20)['clip_valid'])
    def test_negative_root_clip_origin(self):self.reject('root-applied-global-clip',lambda:root_clip('PI_OWNER output=HEADLESS-1 ns=10 id=9 x\nPI_POPUP output=HEADLESS-1 ns=11 local_index=1 tree=0x1 enabled=1 clip_valid=1 clip=0,0,800,600',[-318,25],True,9,1,20))
    def test_negative_root_unstable(self):
        text='PI_OWNER output=HEADLESS-1 ns=10 id=9 x\nPI_POPUP output=HEADLESS-1 ns=11 local_index=1 tree=0x1 enabled=1 clip_valid=0 clip=0,0,0,0\nPI_POPUP output=HEADLESS-1 ns=12 local_index=1 tree=0x1 enabled=1 clip_valid=1 clip=-482,-25,800,600'
        self.reject('root-window-state-consistent',lambda:root_clip(text,[-318,25],True,9,1,20))
    def test_negative_root_enabled(self):self.reject('root-enabled-index',lambda:root_clip('PI_OWNER output=HEADLESS-1 ns=10 id=9 x\nPI_POPUP output=HEADLESS-1 ns=11 local_index=1 tree=0x1 enabled=0 clip_valid=1 clip=-482,-25,800,600',[-318,25],True,9,1,20))

    def correlation_fixture(self,name='run-private_mosaic-crossing-b_cross'):
        from replay import correlate_historical
        d=NESTED/name;tree=json.loads((d/'tree-open.json').read_text())
        from ipc_predicates import nodes
        owner=next(n for n in nodes(tree) if n.get('app_id')=='org.mosaic.NestedGrabProbe')
        comp=(d/'compositor.log').read_text()
        c=re.findall(r'PROBE_POPUP_CLIP owner=(\S+) local=(-?\d+),(-?\d+) (\d+)x(\d+)',comp)[0]
        origin=(-int(c[1]),-int(c[2]));text=(d/'client.log').read_text()
        rects={'TOPLEVEL':Rect(Space.GLOBAL,*origin,owner['window_rect']['width'],owner['window_rect']['height'],self.p)}
        for target,parent in [('POPUP_A','TOPLEVEL'),('POPUP_B','POPUP_A')]:
            x,y,w,h=map(int,re.findall(target+r' ROLE_CONFIGURE x=(-?\d+) y=(-?\d+) w=(\d+) h=(\d+)',text)[-1]);r=rects[parent]
            rects[target]=Rect(Space.GLOBAL,r.x+x,r.y+y,w,h,self.p)
        return correlate_historical,text,(d/'pointer.log').read_text(),rects

    def test_positive_historical_wire_correlation(self):
        fn,text,inject,rects=self.correlation_fixture();r=fn(text,inject,rects)
        self.assertEqual(r['status'],'PASS');self.assertEqual(r['buttons'][4]['msec'],1008)
        self.assertEqual(r['callbacks'][-1]['local'],[38,25])

    def test_negative_historical_all_coordinates(self):
        fn,text,inject,rects=self.correlation_fixture()
        self.reject('historical-coordinate-wire-local',lambda:fn(re.sub(r'(POINTER_(?:ENTER|MOTION)[^\n]* x=)[\d.-]+',r'\g<1>99999.00',text),inject,rects))

    def test_negative_historical_both_wire_callback_coordinates(self):
        fn,text,inject,rects=self.correlation_fixture()
        bad=text.replace('x=38.00 y=25.00','x=99999.00 y=25.00').replace('38.00000000, 25.00000000','99999.00000000, 25.00000000')
        self.reject('pointer-local-correlation',lambda:fn(bad,inject,rects))

    def test_negative_historical_debug_motion_coordinate(self):
        fn,text,inject,rects=self.correlation_fixture('run-private_mosaic-close_b-visible')
        self.reject('historical-coordinate-wire-local',lambda:fn(text.replace('motion(1003, 38.00000000','motion(1003, 99999.00000000'),inject,rects))

    def test_negative_historical_recipient(self):
        fn,text,inject,rects=self.correlation_fixture()
        self.reject('historical-enter-surface-identity',lambda:fn(text.replace('POINTER_ENTER target=POPUP_B','POINTER_ENTER target=POPUP_A'),inject,rects))

    def test_negative_historical_additional_invisible_button(self):
        fn,text,inject,rects=self.correlation_fixture()
        bad=text.replace('POPUP_B POPUP_DONE ','POINTER_BUTTON target=POPUP_B serial=999 button=273 state=1\nPOPUP_B POPUP_DONE ')
        self.reject('historical-button-wire-present',lambda:fn(bad,inject,rects))

    def test_negative_historical_button_order(self):
        fn,text,inject,rects=self.correlation_fixture()
        self.reject('historical-button-wire-identity',lambda:fn(text.replace('serial=65 button=273 state=1','serial=65 button=273 state=0'),inject,rects))

    def test_positive_historical_map_retarget(self):
        fn,text,inject,rects=self.correlation_fixture('run-private_mosaic-close_b-visible');r=fn(text,inject,rects)
        enters=[c for c in r['callbacks'] if c['target']=='POPUP_A']
        self.assertEqual(enters[0]['global_point'],[340,150]);self.assertEqual(enters[0]['local'],[48,45])
        self.assertEqual(r['buttons'][-1]['phase'],'after-B-close')

    def exchange(self,ipc=1,measures=True,timeout=False,invocation=False):
        import subprocess
        from types import SimpleNamespace
        from predicates import terminal_exchange
        def execute(*a,**k):
            if invocation:raise OSError('synthetic invocation failure')
            return SimpleNamespace(returncode=ipc,stdout='actual stdout',stderr='actual stderr')
        def wait(**k):
            if timeout:raise subprocess.TimeoutExpired('synthetic-compositor',3)
            return 0
        recorded=[]
        data=terminal_exchange(execute,wait,['synthetic'],{},measures,
            lambda:"Handling command 'exit'\nShutting down sway",lambda:False,lambda:False,
            lambda out,err:recorded.append((out,err)))
        return data,recorded

    def test_positive_terminal_exchange_transport(self):
        data,recorded=self.exchange();self.assertTrue(data['scientific_cleanup_pass'])
        self.assertEqual(data['ipc_exit'],1);self.assertTrue(data['transport_incident'])
        self.assertEqual(recorded,[('actual stdout','actual stderr')])

    def test_negative_terminal_exchange_wait_timeout(self):
        data,recorded=self.exchange(ipc=7,timeout=True)
        self.assertEqual(data['ipc_exit'],7);self.assertEqual(data['stdout'],'actual stdout')
        self.assertEqual(data['stderr'],'actual stderr');self.assertIn('compositor_error',data)
        self.assertFalse(data['scientific_cleanup_pass']);self.assertEqual(len(recorded),1)

    def test_negative_terminal_exchange_incomplete(self):
        self.assertFalse(self.exchange(measures=False)[0]['scientific_cleanup_pass'])

    def test_negative_terminal_exchange_invocation(self):
        data,recorded=self.exchange(invocation=True);self.assertIsNone(data['ipc_exit'])
        self.assertIn('ipc_error',data);self.assertFalse(data['scientific_cleanup_pass']);self.assertEqual(recorded,[])

    def test_receipt_fail_closed_empty(self):
        from write_results import aggregate
        result=aggregate({},lambda path:None,{})
        self.assertEqual(result['status'],'INCONCLUSIVE')
        self.assertTrue(result['blockers'])

    def test_receipt_fail_closed_status_only(self):
        from write_results import aggregate,REQUIRED
        result=aggregate({n:{'status':'PASS'} for n in REQUIRED},lambda path:None,{})
        self.assertEqual(result['status'],'INCONCLUSIVE')
        self.assertEqual(set(result['markers'].values()),{'INCONCLUSIVE'})

    def aggregate_fixture(self):
        from write_results import REQUIRED,aggregate
        from support import sha
        from receipt_integrity import make_bindings
        # WHY: bootstrap with genuine current preflight receipts, collected
        # before aggregation tests, not forced statuses or obsolete hashes.
        root=LAB/'preflight'/'results'
        global FIXTURE_SNAPSHOT
        import pickle,copy
        if FIXTURE_SNAPSHOT is None:
            evidence={n:json.loads((root/(n+'.json')).read_text()) for n in REQUIRED}
            FIXTURE_SNAPSHOT=(pickle.dumps(evidence),make_bindings(evidence))
        # Separate object graphs for every mutation. The serialization is an
        # in-memory copy of our own JSON, never untrusted external pickle input.
        evidence=pickle.loads(FIXTURE_SNAPSHOT[0])
        bindings=copy.deepcopy(FIXTURE_SNAPSHOT[1])
        # CONTRACT: synthetic acceptance exists in this independent memory
        # snapshot only. It is never persisted as the real review.
        evidence['independent-review']=dict(status='ACCEPTED',independent=True,scope='SYNTHETIC_IN_MEMORY_ONLY',**__import__('copy').deepcopy(bindings))
        def safe_hash(path):
            try:return sha(path)
            except (OSError,ValueError):return None
        return aggregate,evidence,safe_hash,bindings

    def test_positive_aggregate_complete_bound(self):
        fn,e,h,b=self.aggregate_fixture();result=fn(e,h,b)
        self.assertEqual(result['status'],'READY_FOR_NEW_RUNTIME')
        self.assertEqual(set(result['markers'].values()),{'PASS'})

    def test_negative_aggregate_review_stale(self):
        fn,e,h,b=self.aggregate_fixture();e['independent-review']['source_delta']={}
        self.assertEqual(fn(e,h,b)['status'],'INCONCLUSIVE')

    def test_negative_aggregate_review_unaccepted(self):
        fn,e,h,b=self.aggregate_fixture();e['independent-review']['status']='CORRECTION_REQUIRED'
        self.assertEqual(fn(e,h,b)['status'],'INCONCLUSIVE')

    def test_negative_aggregate_stale_sources(self):
        fn,e,h,b=self.aggregate_fixture()
        result=fn(e,lambda path:'stale',b);self.assertEqual(result['status'],'INCONCLUSIVE')
        for name in ('source-audit','client-provenance','test-receipts','assertion-register','historical-evidence','historical-replay'):
            self.assertTrue(any(x.startswith(name+':') for x in result['blockers']))

    def test_negative_aggregate_missing_case(self):
        fn,e,h,b=self.aggregate_fixture();e['historical-replay']['cases'].pop()
        self.assertEqual(fn(e,h,b)['status'],'INCONCLUSIVE')

    def test_negative_aggregate_missing_C17(self):
        fn,e,h,b=self.aggregate_fixture();e['client-provenance']['commands']=[]
        self.assertEqual(fn(e,h,b)['status'],'INCONCLUSIVE')

    def test_negative_aggregate_incomplete_coverage(self):
        fn,e,h,b=self.aggregate_fixture();e['assertion-coverage']['entries']=0
        self.assertEqual(fn(e,h,b)['status'],'INCONCLUSIVE')


# Each generated method has its own executed ID and exact expected contract.
# These are separate negative cases, not a broad 'register valid' receipt.
def install_negative(name,contract,fn):
    def test(self):self.reject(contract,lambda:fn(self))
    test.__name__='test_negative_'+name
    setattr(Case,test.__name__,test)

for name,contract,fn in [
    ('tag','tag-required',lambda s:Rect('SceneGlobal',0,0,1,1,s.p)),
    ('integer','integer-geometry',lambda s:Rect(Space.GLOBAL,0.5,0,1,1,s.p)),
    ('size','nonnegative-size',lambda s:Rect(Space.GLOBAL,0,0,-1,1,s.p)),
    ('evidence','evidence-required',lambda s:Rect(Space.GLOBAL,0,0,1,1,replace(s.p,evidence=''))),
    ('assignment_spaces','assignment-spaces',lambda s:content(replace(s.a,window=replace(s.a.window,space=Space.GLOBAL)))),
    ('native_space','native-space',lambda s:content(replace(s.a,native=replace(s.a.native,rectangle=replace(s.a.native.rectangle,space=Space.GLOBAL))))),
    ('commit_serial','commit-serial',lambda s:content(replace(s.a,native=replace(s.a.native,commit_serial=0)))),
    ('assigned_ACK','assigned-configure-ack',lambda s:content(replace(s.a,configure_ack=0))),
    ('destination','assigned-destination',lambda s:content(replace(s.a,scene=replace(s.a.scene,width=641)))),
    ('png_from_space','png-to-global-spaces',lambda s:from_png(s.r,s.o)),
    ('png_from_transform','unmeasured-png-transform',lambda s:from_png(Rect(Space.PNG,0,0,1,1,s.p),replace(s.o,scale=2))),
    ('paint_area','paint-area',lambda s:verify_paint(s.r,s.o,[482,25,800,598],1,s.clip)),
    ('popup_spaces','popup-spaces',lambda s:popup(s.r,Rect(Space.GLOBAL,100,80,350,170,s.p),9,9,22,True)),
    ('crossing_space','crossing-space',lambda s:crossing(replace(s.r,space=Space.PNG),0)),
    ('local_clip_space','clip-local-space',lambda s:local_clip_to_global(s.clip,(-318,25),s.p)),
    ('pointer_bounds','pointer-global-bounds',lambda s:pointer_local((1000,1000),s.r,(0,0))),
    ('standard_owner','standard-owner',lambda s:fresh_standard(s.r,replace(s.r,provenance=replace(s.p,owner=10)))),
    ('positioner_flags','positioner-flags',lambda s:constraints(64,[0,0,1,1],[0,0,1,1])),
    ('terminal_codes','actual-terminal-codes',lambda s:terminal(True,None,0,"Handling command 'exit'\nShutting down sway",False,False)),
]:install_negative(name,contract,fn)


# WHY: exercise the production aggregator independently for each mandatory gate.
from write_results import REQUIRED
for gate in REQUIRED:
    for mutation in ('missing','failed'):
        def test(self,gate=gate,mutation=mutation):
            fn,e,h,b=self.aggregate_fixture()
            if mutation=='missing':e.pop(gate)
            else:e[gate]['status']='FAIL'
            result=fn(e,h,b)
            self.assertEqual(result['status'],'INCONCLUSIVE')
            self.assertTrue(any(x.startswith(gate+':') for x in result['blockers']))
        setattr(Case,'test_negative_aggregate_'+gate.replace('-','_')+'_'+mutation,test)


for gate in REQUIRED:
    def test(self,gate=gate):
        import copy
        fn,e,h,b=self.aggregate_fixture()
        original=copy.deepcopy(b)
        original['evidence_sha256']={n:'reviewed-proof-'+n for n in REQUIRED}
        e['independent-review']=dict(status='ACCEPTED',independent=True,**copy.deepcopy(original))
        current=copy.deepcopy(original);current['evidence_sha256'][gate]='changed-proof'
        result=fn(e,h,current)
        self.assertEqual(result['status'],'INCONCLUSIVE')
        self.assertTrue(any(x.startswith('independent-review:') for x in result['blockers']))
    setattr(Case,'test_negative_aggregate_'+gate.replace('-','_')+'_stale_review_binding',test)


def integrity_negative(self, label, mutate, group, category):
    import copy
    from receipt_integrity import make_bindings
    fn,e,h,b=self.aggregate_fixture()
    global BASELINE_CHECKED
    if not BOOTSTRAP and not BASELINE_CHECKED:
        self.assertEqual(fn(e,h,b)['status'],'READY_FOR_NEW_RUNTIME','mutation baseline must be complete')
        BASELINE_CHECKED=True
    mutate(e)
    # Rebind the synthetic memory-only review to the mutation so the semantic
    # checker itself must reject it; stale-review rejection alone is inadequate.
    if group!='independent-review':
        import hashlib
        from receipt_integrity import encoded
        b=copy.deepcopy(b)
        b['evidence_content'][group]=hashlib.sha256(encoded(e[group]).encode()).hexdigest()
        b['evidence_sha256'][group]=b['evidence_content'][group]
        e['independent-review']=dict(status='ACCEPTED',independent=True,scope='SYNTHETIC_IN_MEMORY_ONLY',**copy.deepcopy(b))
    r=fn(e,h,b)
    self.assertEqual(r['status'],'INCONCLUSIVE',label)
    self.assertTrue(any(x.startswith(group+':') for x in r['blockers']),(label,r['blockers']))
    for marker,dependencies in r['marker_scope'].items():
        if group in dependencies:self.assertEqual(r['markers'][marker],'INCONCLUSIVE',label)
    MUTATIONS.append(dict(label=label,category=category,gate=group,status=r['status'],blockers=r['blockers'],markers=r['markers']))


MUTATIONS=[]
def original_R02(self, name):
    def mutate(e):
        if name=='A':e['historical-replay']['cases'][0]['input_correlation']={'status':'PASS'}
        elif name=='B':
            for k in ('content','PNG_bbox','count','visible_intersection'):e['rendered'][k]=None
        else:e['popup-root']['cases']=[{} for _ in range(9)]
    integrity_negative(self,'R02-'+name,mutate,{'A':'historical-replay','B':'rendered','C':'popup-root'}[name],'original')

for letter in 'ABC':
    def test(self,letter=letter):original_R02(self,letter)
    setattr(Case,'test_integrity_R02_'+letter,test)


def essential_paths(evidence):
    """Required fields, including scenario-specific nested original facts.

    All root/nested observations are inspected in all nine cases. Empty
    failed_lines/contracts and scenario nulls are legitimate and not mutated
    into the same value; deleting their schema key still must be rejected.
    """
    for gate in REQUIRED:
        for key in evidence[gate]:yield gate,[key]
    for gate in ('historical-replay','popup-root','popup-nested'):
        for index,row in enumerate(evidence[gate]['cases']):
            def walk(value,path):
                if isinstance(value,dict):
                    for k,v in value.items():
                        yield path+[k]
                        # File inventories are complete mappings, not samples.
                        yield from walk(v,path+[k])
                elif isinstance(value,list) and value and isinstance(value[0],dict):
                    for i,v in enumerate(value):yield from walk(v,path+[i])
            for path in walk(row,['cases',index]):yield gate,path


def access(e,gate,path):
    node=e[gate]
    for part in path[:-1]:node=node[part]
    return node,path[-1]


def test_deletions(self):
    # WHY: bulk mutation receipts prove returned verdicts, not line coverage.
    # Individual R02/positive tests keep tracing; suppressing tracing here
    # avoids charging repeated read/hash loops as scientific branch proof.
    sys.settrace(None)
    _,e,_,_=self.aggregate_fixture()
    for gate,path in essential_paths(e):
        def mutate(d,gate=gate,path=path):
            parent,key=access(d,gate,path);del parent[key]
        integrity_negative(self,gate+'/'+str(path),mutate,gate,'deletion')


def test_nullifications(self):
    sys.settrace(None)
    _,e,_,_=self.aggregate_fixture()
    for gate,path in essential_paths(e):
        parent,key=access(e,gate,path);original=parent[key]
        for value in (None,{},[], ''):
            if type(value) is type(original) and value==original:continue
            def mutate(d,gate=gate,path=path,value=value):
                parent,key=access(d,gate,path);parent[key]=value
            integrity_negative(self,gate+'/'+str(path)+'='+repr(value),mutate,gate,'nullification')


def test_contradictions(self):
    sys.settrace(None)
    attacks=[('rendered',['content',3],320),('rendered',['content',1],0),
        ('rendered',['PNG_bbox',0],483),('rendered',['count'],182215),
        ('rendered',['count'],True),('applied',['scroll'],161.0),
        ('applied',['globalclip',0],0),('applied',['titlebar'],0),
        ('native-shm',['stride'],1280),('native-shm',['buffer'],True),
        ('xdg-configure',['assigned_ACK'],20),('positioner',['flags'],1)]
    attacks += [('assertion-register',['records',0,'test_status'],None),
        ('assertion-register',['records',0,'domain'],'invented classification'),
        ('assertion-register',['historical_asserts'],True),
        ('test-receipts',['tests',0,'executed_lines'],[]),
        ('test-receipts',['tests',0,'id'],'__main__.Case.test_fabricated')]
    for index in range(9):
        for field,value in [('owner',999),('workspace',999),('origin',[0,0]),('A',[0,0,300,170]),('B',[0,0,300,130]),('case','unknown')]:
            attacks.append(('historical-replay',['cases',index,field],value))
        attacks += [('historical-replay',['cases',index,'protocol','grabs',1,'parent'],'TOPLEVEL'),
            ('historical-replay',['cases',index,'protocol','grabs',1,'serial'],55),
            ('historical-replay',['cases',index,'input_correlation','buttons',0,'target'],'POPUP_B'),
            ('historical-replay',['cases',index,'input_correlation','buttons',0,'serial'],999),
            ('historical-replay',['cases',index,'input_correlation','buttons',1,'state'],1),
            ('historical-replay',['cases',index,'input_correlation','callbacks',-1,'local'],[99999.0,1.0]),
            ('historical-replay',['cases',index,'input_correlation','actions',0,'motion_msec'],99999),
            ('popup-root',['cases',index,'origin'],[0,0]),
            ('popup-root',['cases',index,'clip'],[0,0,1,1]),
            ('popup-nested',['cases',index,'B'],[0,0,300,130]),
            ('popup-nested',['cases',index,'protocol','grabs',1,'ack'],999)]
    for gate,path,value in attacks:
        def mutate(d,gate=gate,path=path,value=value):
            parent,key=access(d,gate,path);parent[key]=value
        integrity_negative(self,gate+'/'+str(path),mutate,gate,'contradiction')
    for gate in ('historical-replay','popup-root','popup-nested'):
        integrity_negative(self,gate+' duplicated identity',lambda d,gate=gate:d[gate]['cases'].__setitem__(1,__import__('copy').deepcopy(d[gate]['cases'][0])),gate,'contradiction')


def test_freshness(self):
    import copy
    fn,e,h,b=self.aggregate_fixture()
    from receipt_integrity import make_bindings
    from support import sha
    # A correct source hash replaced by the hash of its own mutated file must
    # still lose the previously signed acceptance.
    for key in ('source_delta','evidence_sha256','evidence_content'):
        current=copy.deepcopy(b);first=next(iter(current[key]));current[key][first]='0'*64
        r=fn(e,h,current);self.assertEqual(r['status'],'INCONCLUSIVE');self.assertTrue(r['blockers'])
        MUTATIONS.append(dict(label='stale '+key,category='freshness',status=r['status'],blockers=r['blockers']))
    for gate in REQUIRED:
        d=copy.deepcopy(e);d[gate]={};current=make_bindings(d)
        # Old acceptance, even with fresh current bindings, is not reusable.
        r=fn(d,h,current);self.assertEqual(r['status'],'INCONCLUSIVE')
        self.assertTrue(any(x.startswith('independent-review:') for x in r['blockers']))
    for key in ('status','independent','scope','source_delta','evidence_sha256','evidence_content'):
        for value in (None,{},[], ''):
            integrity_negative(self,'review '+key+'='+repr(value),lambda d,key=key,value=value:d['independent-review'].__setitem__(key,value),'independent-review','freshness')
    for file in (str(HERE/'placement.patch'),str(HERE/'receipt_integrity.py'),next(iter(e['historical-evidence']['inputs']))):
        r=fn(e,lambda p,file=file:None if str(p)==file else h(p),b)
        self.assertEqual(r['status'],'INCONCLUSIVE');self.assertTrue(r['blockers'])
        MUTATIONS.append(dict(label='missing '+file,category='freshness',status=r['status'],blockers=r['blockers']))


def test_omissions(self):
    fn,e,h,b=self.aggregate_fixture()
    self.assertIsNone(e['popup-root']['cases'][4]['clip'])
    self.assertIsNone(e['popup-nested']['cases'][0]['standard'])
    self.assertIsNone(e['popup-nested']['cases'][2]['dismissal'])
    self.assertIsNone(e['historical-replay']['cases'][0]['colors']['right']['POPUP_B']['bbox'])
    self.assertEqual(e['historical-replay']['cases'][0]['colors']['right']['POPUP_B']['count'],0)
    self.assertEqual(fn(e,h,b)['status'],'READY_FOR_NEW_RUNTIME')


def test_writer(self):
    import contextlib,io,copy
    from write_results import write,aggregate
    from receipt_integrity import make_bindings
    fn,e,h,b=self.aggregate_fixture()
    # CONTRACT: no synthetic acceptance is persisted, even in the writer test.
    e['independent-review']={'status':'NOT RUN','independent':False}
    with tempfile.TemporaryDirectory(prefix='mosaic-real-writer-') as tmp:
        root=Path(tmp);(root/'results').mkdir()
        for name,data in e.items():save(root,name,data)
        current=make_bindings(e,{n:root/'results'/(n+'.json') for n in REQUIRED})
        expected=aggregate(e,h,current)
        with contextlib.redirect_stdout(io.StringIO()):observed=write(root)
        self.assertEqual(observed['status'],expected['status']);self.assertEqual(observed['markers'],expected['markers'])
        e['rendered']['count']=None;save(root,'rendered',e['rendered'])
        with contextlib.redirect_stdout(io.StringIO()):observed=write(root)
        self.assertEqual(observed['status'],'INCONCLUSIVE')
        self.assertEqual(observed['markers']['STATIC_NESTED_SHM_RENDER_GEOMETRY_REPLAY'],'INCONCLUSIVE')
        self.assertTrue(any(x.startswith('rendered:') for x in observed['blockers']))
        # CONTRACT B-01: decoder exhaustion must invalidate persisted READY,
        # not merely raise before publication. The fake prior marker is an
        # adversarial receipt in this test-owned temp LAB, not signed review.
        prior={'status':'READY_FOR_NEW_RUNTIME','marker':'SWAYFX_MOSAIC_STATIC_NESTED_GEOMETRY_OFFLINE_GATE=READY_FOR_NEW_RUNTIME'}
        save(root,'runner-readiness',prior);save(root,'offline-gate',prior)
        (root/'results/rendered.json').write_text('['*100000+'0'+']'*100000)
        with contextlib.redirect_stdout(io.StringIO()):observed=write(root)
        self.assertEqual(observed['status'],'INCONCLUSIVE')
        self.assertTrue(any(x.startswith('rendered:') for x in observed['blockers']))
        for name in ('runner-readiness','offline-gate'):
            persisted=json.loads((root/'results'/(name+'.json')).read_text())
            self.assertEqual(persisted['status'],'INCONCLUSIVE')
            self.assertEqual(persisted['markers']['STATIC_NESTED_SHM_RENDER_GEOMETRY_REPLAY'],'INCONCLUSIVE')
        save(LAB,'writer-entrypoint-test',dict(status='PASS',aggregate_source=str(Path(aggregate.__code__.co_filename)),mock=False,synthetic_review_persisted=False,invalid=observed['blockers']))


Case.test_integrity_deletions=test_deletions
Case.test_integrity_nullifications=test_nullifications
Case.test_integrity_contradictions=test_contradictions
Case.test_integrity_freshness=test_freshness
Case.test_integrity_legitimate_omissions=test_omissions
Case.test_integrity_writer=test_writer


class Result(unittest.TextTestResult):
    def addSuccess(self,test):
        super().addSuccess(test);RECEIPTS.append(dict(id=test.id(),status='PASS',mode='negative' if '.test_negative_' in test.id() else 'positive',executed_lines=sorted(LINES.get(test.id(),set())),failed_lines=sorted(FAILED.get(test.id(),set())),contracts=[{'contract':c,'pass':v} for c,v in sorted(CONTRACTS.get(test.id(),set()))]));sys.settrace(trace)
    def addFailure(self,test,err):
        super().addFailure(test,err);RECEIPTS.append(dict(id=test.id(),status='FAIL',error=str(err[1])));sys.settrace(trace)
    def addError(self,test,err):
        super().addError(test,err);RECEIPTS.append(dict(id=test.id(),status='FAIL',error=str(err[1])));sys.settrace(trace)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('lab',type=Path);parser.add_argument('--preflight',action='store_true');parser.add_argument('--negative-preflight',action='store_true');args=parser.parse_args();LAB=args.lab
    sys.settrace(trace)
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(Case)
    if args.preflight:suite=unittest.TestSuite(t for t in suite if 'aggregate' not in t.id() and 'integrity' not in t.id())
    if args.negative_preflight:suite=unittest.TestSuite(t for t in suite if t._testMethodName not in ('test_positive_aggregate_complete_bound','test_integrity_legitimate_omissions'))
    BOOTSTRAP=args.negative_preflight
    result=unittest.TextTestRunner(verbosity=2,resultclass=Result).run(suite)
    sys.settrace(None)
    save(LAB,'test-receipts',dict(source_inventory={str(p):__import__('hashlib').sha256(p.read_bytes()).hexdigest() for p in HERE.iterdir() if p.suffix in ('.py','.patch','.json')},status='PASS' if result.wasSuccessful() else 'FAIL',tests=RECEIPTS))
    save(LAB,'positive',{'tests':[r for r in RECEIPTS if r.get('mode')=='positive']})
    save(LAB,'negative',{'tests':[r for r in RECEIPTS if r.get('mode')=='negative']})
    if not args.preflight:
        save(LAB,'aggregate-negative',{'status':'PASS' if result.wasSuccessful() else 'FAIL', 'mutations':MUTATIONS})
        for category in ('deletion','nullification','contradiction','freshness','original'):
            save(LAB,category+'-tests',{'status':'PASS' if result.wasSuccessful() else 'FAIL','mutations':[r for r in MUTATIONS if r['category']==category]})
    raise SystemExit(0 if result.wasSuccessful() else 1)
