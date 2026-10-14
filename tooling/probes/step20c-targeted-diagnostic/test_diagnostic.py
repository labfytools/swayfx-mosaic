"""Offline only: real A/G wire and IPC, synthetic native identity mutations."""
import copy,json,re,unittest,tempfile
from unittest.mock import patch
from diagnostic import *

TRACE='''SD_CREATE ns=101 node=0x1 source_node=0x2 source=0x3 tree=0x4 parent=0x5 locks_before=1 locks_after=2 dest=636,573 src=0,0,636,573 transform=0
SD_TREE ns=102 owner=10 tree=0x4 parent=0x5 content=0x6 saved_enabled=1 content_enabled=0
OPT_BUFFER_DRAW ns=103 output=HEADLESS-1 node=0x1 buffer=0x3 surface=(nil) global=-318,25 dest=636x573 source=636x573 draw=482,30,770,570
SD_SAMPLE ns=104 node=0x1 source=0x3 live_source=0x3 output=HEADLESS-1 global=-318,25 dest=636,573 src=0,0,636,573 transform=0 enabled=1 node_enabled=1 viewport=-800,0,800,600 timeline=(nil) point=0 direct=0
SD_ANCESTOR ns=105 sample_ns=104 node=0x1 output=HEADLESS-1 tree=0x5 global=-800,0 enabled=1 clip_valid=1 clip=30,30,740,540
Transaction 0xaa timed out (1 waiting)
SD_REMOVE ns=199 owner=10 tree=0x4 content=0x6
SD_NODE_DESTROY ns=200 node=0x1 source=0x3
SD_RELEASE ns=201 node=0x1 source=0x3 locks=0 gpu_complete=NOT_PROVEN
SD_BUFFER_DESTROY ns=202 node=0x1 source=0x3 gpu_complete=NOT_PROVEN
'''

class DiagnosticTests(unittest.TestCase):
    def real(self,rid='saved-A'):
        run=plans.DEFAULT_LAB/'runs'/rid/'run'
        before=(run/'owner.log').read_text().split('COMMAND hold_next_configure DONE')[0]
        full=(run/'owner.log').read_text();cut=full.index('COMMAND hold_next_configure DONE');after=full[cut:]
        prior=int(re.findall(r'ACK ns=\d+ serial=(\d+)',before)[-1]);events=[json.loads(l) for l in (run/'events.jsonl').read_text().splitlines()]
        request=next(e['ns'] for e in events if e['kind']=='ipc-request' and e['args']==['gaps inner current set 30'])
        a=gate.read(run/'owner-owner-snapshot.json');b=gate.read(run/'saved-requested-pending-snapshot.json')
        return [a,b,10,6,before,after,prior,request]
    def test_real_A_G(self):
        for rid in ('saved-A','saved-G'):
            p=pending_geometry(*self.real(rid));self.assertEqual(p['held']['serial'],39);self.assertEqual(p['held']['requested_size'],[636,513])
    def test_fictitious_gaps(self):
        args=self.real();workspace(args[1]['tree'],'1')['gaps']={'inner':30}
        with self.assertRaises(ValueError):pending_geometry(*args)
    def test_wrong_workspace(self):
        args=self.real();args[3]=999
        with self.assertRaises(ValueError):pending_geometry(*args)
    def test_wrong_owner(self):
        args=self.real();args[2]=9
        with self.assertRaises(ValueError):pending_geometry(*args)
    def test_wrong_requested_size(self):
        args=self.real();args[5]=args[5].replace('636x513','636x514')
        with self.assertRaises(ValueError):pending_geometry(*args)
    def test_unreceived_serial(self):
        args=self.real();args[5]=args[5].replace('.configure(39)','.configure(40)')
        with self.assertRaises(ValueError):pending_geometry(*args)
    def test_ack_rejected(self):
        args=self.real();args[5]+='\nxdg_surface#3.ack_configure(39)\n'
        with self.assertRaises(ValueError):pending_geometry(*args)
    def test_stale_command(self):
        args=self.real();args[7]=10**18
        with self.assertRaises(ValueError):pending_geometry(*args)
    def test_native_positive(self):
        self.assertEqual(saved_identity(TRACE,10,100,True)['gpu_completion'],'NOT PROVEN')
    def test_native_mutations(self):
        mutations=[TRACE.replace('source_node=0x2','source_node=0x1'),TRACE.replace('SD_SAMPLE ns=104 node=0x1','SD_SAMPLE ns=104 node=0x9'),TRACE.replace('live_source=0x3 output=HEADLESS-1','live_source=0x3 output=HEADLESS-2'),TRACE.replace('SD_SAMPLE ns=104 node=0x1 source=0x3','SD_SAMPLE ns=104 node=0x1 source=0x9'),TRACE.replace('OPT_BUFFER_DRAW ns=103','OPT_BUFFER_DRAW ns=203'),TRACE.replace('gpu_complete=NOT_PROVEN','gpu_complete=PROVEN'),TRACE.replace('SD_NODE_DESTROY','OTHER'),TRACE.replace('SD_CREATE','OTHER'),TRACE.replace('global=-318,25 dest=636,573','global=10,25 dest=636,573'),TRACE.replace('sample_ns=104','sample_ns=105'),TRACE.replace('SD_BUFFER_DESTROY ns=202','SD_BUFFER_DESTROY ns=103')]
        for text in mutations:
            with self.subTest(text=text),self.assertRaises(ValueError):saved_identity(text,10,100,True)
    def test_creation_window_and_reuse_negatives(self):
        mutations=[TRACE.replace('SD_CREATE ns=101','SD_CREATE ns=90'),
                   TRACE.replace('SD_CREATE ns=101','SD_CREATE ns=102'),
                   TRACE.replace('SD_TREE ns=102','SD_TREE ns=104'),
                   TRACE.replace('OPT_BUFFER_DRAW ns=103','OPT_BUFFER_DRAW ns=102'),
                   TRACE.replace('owner=10','owner=11'),
                   TRACE.replace('SD_CREATE ns=101', 'SD_CREATE ns=101',1)+'SD_CREATE ns=300 node=0x1 source_node=0x9 source=0x8 tree=0x7 parent=0x5\n',
                   TRACE+'SD_TREE ns=301 owner=11 tree=0x4 parent=0x5 content=0x6 saved_enabled=1 content_enabled=0\n']
        for text in mutations:
            with self.subTest(text=text),self.assertRaises(ValueError):saved_identity(text,10,100)
    def test_removal_positive_synchronous_before_runner_observation(self):
        identity=saved_identity(TRACE,10,100)
        proof=saved_removal(TRACE,identity,210)
        self.assertEqual(proof['nodes'][0]['ns'],'200')
        self.assertEqual(proof['gpu_completion'],'NOT PROVEN')
    def test_removal_exact_window_negatives(self):
        identity=saved_identity(TRACE,10,100)
        mutations=[TRACE.replace('SD_NODE_DESTROY ns=200','SD_NODE_DESTROY ns=90'),
                   TRACE.replace('SD_NODE_DESTROY ns=200 node=0x1','SD_NODE_DESTROY ns=200 node=0x9'),
                   TRACE.replace('SD_REMOVE ns=199 owner=10','SD_REMOVE ns=199 owner=11'),
                   TRACE.replace('SD_REMOVE ns=199 owner=10 tree=0x4','SD_REMOVE ns=199 owner=10 tree=0x9'),
                   TRACE.replace('content=0x6\nSD_NODE_DESTROY','content=0x9\nSD_NODE_DESTROY'),
                   TRACE.replace('Transaction 0xaa timed out (1 waiting)\n',''),
                   TRACE.replace('Transaction 0xaa timed out (1 waiting)\n','')+'Transaction 0xaa timed out (1 waiting)\n',
                   TRACE.replace('SD_NODE_DESTROY ns=200','SD_NODE_DESTROY ns=220'),
                   TRACE.replace('SD_REMOVE ns=199','SD_REMOVE ns=220'),
                   TRACE.replace('SD_NODE_DESTROY ns=200 node=0x1 source=0x3','SD_NODE_DESTROY ns=200 node=0x1 source=0x9')]
        for text in mutations:
            with self.subTest(text=text),self.assertRaises(ValueError):saved_removal(text,identity,210)
        # A destruction emitted only by normal explicit close is too late.
        with self.assertRaises(ValueError):saved_removal(TRACE,identity,199)
    def test_removal_not_global_count(self):
        identity=saved_identity(TRACE,10,100)
        text=TRACE.replace('SD_NODE_DESTROY ns=200 node=0x1','SD_NODE_DESTROY ns=200 node=0x9')
        text+='SD_NODE_DESTROY ns=201 node=0x8 source=0x3\n'
        with self.assertRaises(ValueError):saved_removal(text,identity,210)
    def test_absent_release_is_still_not_gpu_proof(self):
        text='\n'.join(l for l in TRACE.splitlines() if 'SD_RELEASE' not in l and 'SD_BUFFER_DESTROY' not in l)
        identity=saved_identity(text,10,100,True)
        self.assertEqual(identity['gpu_completion'],'NOT PROVEN')
        self.assertEqual(saved_removal(text,identity,210)['gpu_completion'],'NOT PROVEN')
    def test_false_gpu_release_remains_rejected(self):
        with self.assertRaises(ValueError):saved_identity(TRACE.replace('gpu_complete=NOT_PROVEN','gpu_complete=PROVEN'),10,100,True)
    def budget(self):
        state=copy.deepcopy(gate.read(plans.DEFAULT_LAB/'budget.json'))
        # Model a fixed fourteen-token final state offline, without touching lab.
        for rid,spec in plans.RUNS.items():
            if rid not in state['runs']:
                state['runs'][rid]=dict(campaign=spec['campaign'],planned=spec['limits'],reserved=dict.fromkeys(spec['limits'],0),consumed_ns=1,freeze_sha256='offline')
                state['used']['run']+=1;state['campaign_runs'][spec['campaign']]+=1
        return state
    def test_budget_known_extension(self):
        plans.RUNS[SPEC['id']]=SPEC
        try:self.assertEqual(gate.validate(self.budget())['used']['run'],14)
        finally:del plans.RUNS[SPEC['id']]
    def test_budget_unknown_and_caps(self):
        plans.RUNS[SPEC['id']]=SPEC
        try:
            state=self.budget()
            for mutate in (lambda s:s['runs'].__setitem__('retry',copy.deepcopy(s['runs'][SPEC['id']])),lambda s:s['runs'][SPEC['id']]['planned'].__setitem__('capture',17),lambda s:s['used'].__setitem__('capture',175),lambda s:s['campaign_used'].__setitem__('saved',31),lambda s:s['campaign_runs'].__setitem__('saved',4)):
                s=copy.deepcopy(state);mutate(s)
                with self.assertRaises(ValueError):gate.validate(s)
        finally:del plans.RUNS[SPEC['id']]
    def test_registration_before_after_verify(self):
        with tempfile.TemporaryDirectory(prefix='saved-diag-offline-') as folder:
            path=Path(folder);(path/'diagnostic-registration.json').write_text(json.dumps(dict(scope=SCOPE,spec=SPEC)))
            with patch.object(gate,'verify') as verify:
                with registration(path):self.assertEqual(plans.RUNS[SPEC['id']],SPEC)
                self.assertNotIn(SPEC['id'],plans.RUNS);self.assertEqual(verify.call_count,2)
    def test_registration_duplicate_rejected(self):
        with tempfile.TemporaryDirectory(prefix='saved-diag-offline-') as folder:
            path=Path(folder);(path/'diagnostic-registration.json').write_text(json.dumps(dict(scope=SCOPE,spec=SPEC)))
            with registration(path,False):
                with self.assertRaises(ValueError):
                    with registration(path,False):pass
    def test_missing_persisted_registration_rejected(self):
        with tempfile.TemporaryDirectory(prefix='saved-diag-offline-') as folder:
            with self.assertRaises(FileNotFoundError):
                with registration(Path(folder),False):pass
    def test_retry_build_token_rejected(self):
        with tempfile.TemporaryDirectory(prefix='saved-diag-offline-') as folder:
            token=Path(folder)/'build.token.json';gate.durable(token,dict(kind='build'),True)
            with self.assertRaises(FileExistsError):gate.durable(token,dict(kind='build'),True)
    def test_no_extra_buffer_ref_or_synchronization(self):
        patch=(HERE/'saved-passive.patch').read_text();added='\n'.join(l[1:] for l in patch.splitlines() if l.startswith('+') and not l.startswith('+++'))
        for token in ('wlr_buffer_lock(', 'wlr_buffer_unlock(', 'wlr_scene_buffer_set_buffer(', 'ack_configure(', 'wait_timeline(', 'read_pixels('):self.assertNotIn(token,added)

if __name__=='__main__':unittest.main(verbosity=2)
