"""Real historical INPUT-01 replay and adversarial applied-state tests."""
import copy,json,re,unittest,hashlib
from pathlib import Path
from input_validators import *
HIST=Path('/home/fy59/swayfx-mosaic-targeted-7gge6h8b/runs/input-A/run')

def historical_receipt():
    events=[json.loads(s) for s in (HIST/'events.jsonl').read_text().splitlines()]
    clicks=[e for e in events if e['kind']=='click-observation']
    c=clicks[-1]; tail=c['tails']['owner']; d=wire_delivery(tail)
    state=json.loads((HIST/'owner-geometry.json').read_text());o=state['owner'];w=state['workspace']
    states=applied_states((HIST/'compositor.log').read_text(),o['id'],w['output'],w['id'],
        [o['window_rect']['x'],o['deco_rect']['height']+o['window_rect']['y']],[-800,0,800,600])
    return dict(owner=o['id'],workspace=w['id'],output=w['output'],surface=d['surface'],delivery=d,
        point=c['point'],interval=[c['start_ns'],c['ns']],states=states,other_buttons={},
        source_hashes={str(HIST/name):hashlib.sha256((HIST/name).read_bytes()).hexdigest() for name in ('events.jsonl','owner.log','compositor.log','owner-geometry.json')})

class InputTests(unittest.TestCase):
    def test_real_mutation(self):
        r=historical_receipt();v=correlate(r)
        self.assertEqual(r['point'],[-314,30]);self.assertEqual(r['delivery']['local'],[324,5])
        self.assertEqual([b['serial'] for b in r['delivery']['buttons']],[45,46])
        self.assertEqual(v['compatible_states'][0]['origin'],[-638,25]);self.assertEqual(v['atomic_generation'],'NOT_PROVEN')
    def test_negative_owner_output_serial_recipient_local_pending_destroyed_clip(self):
        base=historical_receipt()
        for field,value in [('owner',999),('output','HEADLESS-2'),('surface',99),('workspace',999)]:
            r=copy.deepcopy(base);r[field]=value
            with self.assertRaises(InvalidEvidence):correlate(r)
        for key,value in [('applied',False),('alive',False),('origin',[100,100]),('clip',[0,0,800,600])]:
            r=copy.deepcopy(base)
            for s in r['states']:s[key]=value
            with self.assertRaises(InvalidEvidence):correlate(r)
        r=copy.deepcopy(base);r['delivery']['local']=[4,900]
        with self.assertRaises(InvalidEvidence):correlate(r)
        r=copy.deepcopy(base);r['other_buttons']={'filler':['BUTTON']}
        with self.assertRaises(InvalidEvidence):correlate(r)
        with self.assertRaises(InvalidEvidence):wire_delivery(base['delivery']['raw'].replace('serial=45','serial=99'))
        with self.assertRaises(InvalidEvidence):wire_delivery(base['delivery']['raw'].replace('wl=3','wl=99'))
    def test_status_pass_empty(self):
        with self.assertRaises(InvalidEvidence):correlate({'status':'PASS'})
    def test_multiple_plausible_applied_states(self):
        r=historical_receipt();match=correlate(r)['compatible_states'][0];alternate=copy.deepcopy(match);alternate['layout']=1;alternate['clip']=None;r['states'].append(alternate)
        self.assertEqual(correlate(r)['status'],'INCONCLUSIVE')
    def test_shifted_interval_and_destroyed_recipient(self):
        r=historical_receipt();r['interval']=[0,1]
        self.assertEqual(correlate(r)['status'],'INCONCLUSIVE')
        r=historical_receipt()
        with self.assertRaises(InvalidEvidence):wire_delivery('TOPLEVEL DESTROY\n'+r['delivery']['raw'])
    def test_no_applied_state_is_inconclusive(self):
        r=historical_receipt();r['states']=[]
        self.assertEqual(correlate(r)['status'],'INCONCLUSIVE')
    def test_standard_clip_removal(self):
        r=historical_receipt();state=copy.deepcopy(r['states'][-1]);state['layout']=1;state['clip']=None
        self.assertEqual(standard_return([state],r['owner'],r['output'],r['workspace']),'PARTIALLY_FEASIBLE')
        state['clip']=[-800,0,800,600]
        with self.assertRaises(InvalidEvidence):standard_return([state],r['owner'],r['output'],r['workspace'])
    def test_wrong_focus_is_not_owner_identity(self):
        r=historical_receipt();r['owner']=8
        with self.assertRaises(InvalidEvidence):correlate(r)
if __name__=='__main__':unittest.main()
