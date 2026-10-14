"""Pure accounting tests; no laboratory token is consumed."""
import copy,unittest
from ledger import validate
from plans import RUNS,SCOPE,CAPS
class AccountingTests(unittest.TestCase):
    def state(self):return dict(scope=SCOPE,runs={},events=[])
    def add(self,s,rid,kind,count):
        s['runs'][rid]=dict(planned=RUNS[rid]['limits'],reserved=dict.fromkeys(RUNS[rid]['limits'],0))
        s['runs'][rid]['reserved'][kind]=count
        for i in range(count):s['events'].append(dict(id=rid,kind=kind,ns=1,sequence=len(s['events'])))
    def test_fixed_eight(self):self.assertEqual(len(RUNS),8);self.assertEqual(sum(CAPS.values()),96);validate(self.state())
    def test_all_caps(self):
        s=self.state()
        for rid in RUNS:self.add(s,rid,'capture',RUNS[rid]['limits']['capture'])
        validate(s);self.assertEqual(len(s['events']),90)
    def test_local_exceeded(self):
        s=self.state();self.add(s,'saved-A','capture',11)
        with self.assertRaises(ValueError):validate(s)
    def test_old_ticket(self):
        s=self.state();s['scope']='STEP20C_TARGETED_FINAL_BYTES_V1'
        with self.assertRaises(ValueError):validate(s)
    def test_reconcile(self):
        s=self.state();self.add(s,'saved-A','capture',1);s['runs']['saved-A']['reserved']['capture']=0
        with self.assertRaises(ValueError):validate(s)
if __name__=='__main__':unittest.main()
