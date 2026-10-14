"""New bounded synthetic delta tests; no native runtime qualification."""
import ast
import inspect
import unittest
from types import SimpleNamespace
from engine import Session
from fx import effects_verdict, effects_campaign

class OwnerDelta(unittest.TestCase):
    def state(self,layout='mosaic',floating=False,group_fullscreen=0,owner_fullscreen=0,initial='mosaic'):
        owner=dict(id=3,type='con',pid=42,rect=dict(x=120,y=30,width=200,height=100),window_rect=dict(x=2,y=3,width=196,height=97),deco_rect=dict(height=5),fullscreen_mode=owner_fullscreen)
        group=dict(id=2,type='con',nodes=[owner],fullscreen_mode=group_fullscreen)
        ws=dict(id=1,type='workspace',name='1',layout=layout,nodes=[] if floating else [group],floating_nodes=[group] if floating else [])
        if layout=='mosaic':ws['mosaic']=dict(rows=[dict(scroll_x=70)])
        s=Session.__new__(Session);s.spec=dict(mode=initial);s.proc={'owner':SimpleNamespace(pid=42)}
        s.snapshot=lambda tag:dict(tree=ws);s.save=lambda *args:None
        # No Session initialization, IPC, processes, captures or ledger writes.
        return s.owner('owner')
    def check(self,state,x):
        self.assertEqual(state['origin'],[x,33]);self.assertEqual(state['scene'],[x-2,25,200,105])
        self.assertTrue(state['geometry_status'].startswith('IPC_PENDING_CANDIDATE'))
        self.assertIn('fresh pointer-local corroboration',state['evidence'])
    def test_standard_return_missing_mosaic_key(self):self.check(self.state(layout='splith'),122)
    def test_current_mosaic_overrides_initial_standard(self):self.check(self.state(initial='standard'),52)
    def test_current_mosaic_tiled_camera(self):self.check(self.state(),52)
    def test_floating_group_exempt(self):self.check(self.state(floating=True),122)
    def test_current_fullscreen_group_exempt(self):self.check(self.state(group_fullscreen=1),122)
    def test_current_fullscreen_owner_exempt(self):self.check(self.state(owner_fullscreen=1),122)

class FXDelta(unittest.TestCase):
    def test_shadow_exact_false_nonpass_after_all_closes(self):
        closed=[];closes={}
        for name in ('glass','background','filler0'):
            closed.append(name);closes[name]=dict(status='PASS')
        self.assertEqual(closed,['glass','background','filler0'])
        spill=dict(exact=False,pixels=1,max_delta=1)
        self.assertEqual(effects_verdict(closes,dict(ABA_byte_exact=True),dict(exact=True),True,dict(spill=spill)),'INCONCLUSIVE')
        self.assertEqual(spill,dict(exact=False,pixels=1,max_delta=1))
    def test_exact_shadow_preserves_bounded_verdict(self):
        self.assertEqual(effects_verdict({n:dict(status='PASS') for n in ('glass','background','filler0')},dict(ABA_byte_exact=True),dict(exact=True),True,dict(spill=dict(exact=True))),'PARTIALLY_FEASIBLE')
    def test_real_campaign_verdict_after_close_and_final_capture(self):
        tree=ast.parse(inspect.getsource(effects_campaign))
        calls=[n for n in ast.walk(tree) if isinstance(n,ast.Call)]
        verdict=next(n.lineno for n in calls if isinstance(n.func,ast.Name) and n.func.id=='effects_verdict')
        close=next(n.lineno for n in calls if isinstance(n.func,ast.Attribute) and n.func.attr=='record' and n.args and isinstance(n.args[0],ast.Constant) and n.args[0].value=='fx-normal-close')
        final=next(n.lineno for n in calls if isinstance(n.func,ast.Attribute) and n.func.attr=='pair_capture' and n.args[0].value=='final')
        self.assertGreater(verdict,close);self.assertGreater(verdict,final)

if __name__=='__main__':unittest.main(verbosity=2)
