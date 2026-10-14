"""Deterministic positive historical replay and hostile evidence mutations."""
import copy,json,re,sys,unittest
from pathlib import Path
from PIL import Image
from plans import OLD_LAB
from saved_validators import *
from runtime import engine
workspace=engine.workspace
from ledger import validate,source_bindings
class SavedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.folder=OLD_LAB/'runs/saved-diagnostic-A/run';cls.text=(cls.folder/'compositor.log').read_text();cls.wire=(cls.folder/'owner.log').read_text()
        cls.instances=lifetime_instances(cls.text);cls.target=[v for v in cls.instances if v['activation'] and v['activation']['owner']=='10'][-1];cls.request=int(cls.target['create']['ns'])-1
        cls.prior=30;cls.cut=cls.wire.index('COMMAND hold_next_configure');cls.before=cls.wire[:cls.cut];cls.after=cls.wire[cls.cut:]
    def reject(self,fn,*args):
        with self.assertRaises((ValueError,RuntimeError)):fn(*args)
    def test_historical_reuse(self):
        self.assertEqual(len(self.instances),16);self.assertLess(len({v['create']['node'] for v in self.instances}),len(self.instances));self.assertEqual(len(saved_identity(self.text,10,self.request)['nodes']),1)
    def test_historical_held(self):self.assertEqual(held_configure(self.before,self.after,self.prior)['requested_size'],[636,513])
    def test_false_ack(self):self.reject(held_configure,self.before,self.after+'\nACK ns=999 serial=39\n',self.prior)
    def test_false_wire(self):self.reject(held_configure,self.before,re.sub(r'xdg_surface#\d+\.configure\(39\)','removed',self.after),self.prior)
    def test_overlapping_pointer(self):
        c=self.target['create']['raw'];self.reject(lifetime_instances,self.text.replace(c,c+'\n'+c))
    def test_post_destroy(self):
        sample=self.target['samples'][0];dead=self.target['destroy'];bad=re.sub(r'ns=\d+',f"ns={int(dead['ns'])+1}",sample['raw'],count=1)
        self.reject(lifetime_instances,self.text+'\n'+bad)
    def test_wrong_source(self):
        r=self.target['samples'][0];self.reject(lifetime_instances,self.text.replace(r['raw'],r['raw'].replace('source='+r['source'],'source=0xbad',1)))
    def test_wrong_owner(self):self.reject(saved_identity,self.text,999,self.request)
    def test_wrong_output(self):
        r=self.target['samples'][0];self.reject(saved_identity,self.text.replace(r['raw'],r['raw'].replace('output=HEADLESS-1','output=HEADLESS-2')),10,self.request)
    def test_null_fields(self):
        c=self.target['create'];self.reject(lifetime_instances,self.text.replace(c['raw'],c['raw'].replace('source='+c['source'],'source=(nil)',1)))
    def test_wrong_origin(self):
        r=self.target['samples'][0];self.reject(saved_identity,self.text.replace(r['raw'],r['raw'].replace('global='+r['global'],'global=-100,0')),10,self.request)
    def test_teardown_not_natural(self):
        identity=saved_identity(self.text,10,self.request,True);self.reject(natural_retirement,self.text,identity,2**62,2**63,True,self.before,self.after,self.prior)
    def test_post_destroy_draw(self):
        d=self.target['destroy'];raw=f"OPT_BUFFER_DRAW ns={int(d['ns'])+1} node={d['node']} buffer={d['source']} output=HEADLESS-1"
        self.reject(lifetime_instances,self.text+'\n'+raw)
    def test_synthetic_natural_contract(self):
        # Deliberately synthetic timeout/removal receipt, never historical proof.
        identity=saved_identity(self.text,10,self.request,True);tree=identity['tree'];dead=self.target['destroy']
        removal=f"SD_REMOVE ns={int(dead['ns'])-1} owner=10 tree={tree['tree']} content={tree['content']}"
        text=self.text.replace(dead['raw'],'Transaction 0xabc timed out (1 waiting)\n'+removal+'\n'+dead['raw'])
        result=natural_retirement(text,identity,2**62,2**63,True,self.before,self.after,self.prior)
        self.assertEqual(result['gpu_completion'],'NOT PROVEN')
    def test_false_timeout(self):self.reject(timeout_line,'status=PASS',-1,True,1,5_000_000_001,6_000_000_001)
    def test_dead_client(self):self.reject(timeout_line,'Transaction 0x1 timed out (1 waiting)',-1,False,1,5_000_000_001,6_000_000_001)
    def test_empty_pass(self):self.reject(lifetime_instances,'status=PASS')
    def test_gpu_invented(self):self.reject(lifetime_instances,self.text.replace('gpu_complete=NOT_PROVEN','gpu_complete=PASS'))
    def test_masked_rgb(self):
        a=Image.new('RGB',(2,2),(48,48,56));b=a.copy();b.putpixel((1,1),(48,48,57));self.assertTrue(rgb_exact(a,a));self.reject(rgb_exact,a,b)
    def test_geometry_replay(self):
        initial=json.loads((self.folder/'initial-applied.json').read_text())['state']['snapshot'];pending=json.loads((self.folder/'saved-requested-pending-snapshot.json').read_text());ws=workspace(initial['tree'],'1')
        p=pending_geometry(initial,pending,10,ws['id'],self.before,self.after,30,1);self.assertEqual(p['held']['serial'],39)
    def test_geometry_null(self):
        initial=json.loads((self.folder/'initial-applied.json').read_text())['state']['snapshot'];pending=json.loads((self.folder/'saved-requested-pending-snapshot.json').read_text());ws=workspace(initial['tree'],'1');workspace(pending['tree'],'1')['rect']['x']=None
        with self.assertRaises((ValueError,RuntimeError,TypeError)):pending_geometry(initial,pending,10,ws['id'],self.before,self.after,30,1)
if __name__=='__main__':unittest.main()
