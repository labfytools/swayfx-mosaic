"""Actual immutable G1 bytes and adversarial in-memory copies; never rewrites G1."""
import copy
import unittest
import validate as v
import replay
from test_fixture import obj


class ModifierReplay(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows,cls.raw=replay.load()
        cls.samples=replay.sample_protocol(cls.rows,cls.raw)

    def test_nine_real_samples_and_global_rejection(self):
        result=replay.audit()
        self.assertEqual(result['sample_protocol'],'PASS')
        self.assertEqual(result['epoch_validator'],{'status':'REJECTED','reason':'effective halfpixel'})
        self.assertEqual(result['GL_ERROR_QUEUE'],'UNOBSERVED')
        self.assertEqual(result['read_success'],'NOT_PROVEN')
        self.assertEqual(result['GPU_DCC_RUNTIME'],'NOT_RUN')

    def test_dcc_and_linear_metadata_only(self):
        self.assertEqual(v.validate_object(self.samples[1]['object'])['auxiliary_extent'],'NOT_PROVEN')
        self.assertEqual(v.validate_object(obj(1))['layout'],'LINEAR_PACKED')
        # Linear is only a synthetic regression control, never an acquired GPU control.

    def test_bad_planes_and_modifier(self):
        o=self.samples[1]['object']
        mutations=[('drm_format',0),('modifier','020000001046fb04'),
                   ('modifier','020000001046bb05'),('modifier','ffffffffffffffff'),
                   ('modifier','q'*16),('planes',[[3196,0],[1024,2293760]]),
                   ('planes',[[3584,0],[0,2293760]]),('planes',[[3584,0],[1024,0]]),
                   ('planes',[[3584,0],[1024,1]]),('planes',[[3584,0],[1024,2**32-1]]),
                   ('planes',[[3584,2**32-1],[1024,2293760]]),
                   ('planes',[[3584,0],[3584,0]]),('planes',[[3584,0]]),
                   ('planes',[[3584,0],[True,2293760]]),('planes',[[3584,0],[1024,-1]])]
        for key,value in mutations:
            with self.subTest(key=key,value=value),self.assertRaises(v.Rejected):
                bad=copy.deepcopy(o);bad[key]=value;v.validate_object(bad)
        for key in o:
            bad=copy.deepcopy(o);del bad[key]
            with self.subTest(missing=key),self.assertRaises((v.Rejected,KeyError)):
                v.validate_object(bad)

    def test_real_sample_mutations(self):
        mutations=[lambda s:s[4].update(valid=False),lambda s:s[4].update(sentinel_alpha_written=False),
                   lambda s:s[4].update(offset=1),lambda s:s[4].update(sha256='0'*64),
                   lambda s:s[4].update(context_after='other'),lambda s:s[4]['after'].__setitem__(3,99),
                   lambda s:s[4].update(target_read_buffer=0),lambda s:s[4].update(roi=[0,0,800,600]),
                   lambda s:s[4]['attachment'].__setitem__(1,999),lambda s:s[4].update(fbo_status=0)]
        for mutate in mutations:
            rows=copy.deepcopy(self.rows);samples=[r for r in rows if r['kind']=='sample'];mutate(samples)
            with self.subTest(mutation=mutate),self.assertRaises(v.Rejected):replay.sample_protocol(rows,self.raw)
        for raw in (self.raw[:-1],bytes([self.raw[0]^1])+self.raw[1:]):
            with self.assertRaises(v.Rejected):replay.sample_protocol(self.rows,raw)

    def test_eleven_writes_two_copies_and_mutations(self):
        self.assertEqual(v.validate_g1_envelope(self.rows,self.samples,self.rows[0]['context'])['writes'],11)
        def run(mutate):
            rows=copy.deepcopy(self.rows);mutate(rows)
            samples=[r for r in rows if r['kind']=='sample']
            with self.assertRaises((v.Rejected,KeyError,IndexError)):
                v.validate_g1_envelope(rows,samples,rows[0]['context'])
        run(lambda r:r.remove(next(x for x in r if x['kind']=='copy')))
        run(lambda r:r.remove(next(x for x in r if x['kind']=='write' and x['sequence']==11)))
        for key,value in [('read_fbo',999),('texture',0),('context','wrong'),('sampler',[0]*4),('color_mask',[0]*4)]:
            run(lambda r,key=key,value=value:next(x for x in r if x['kind']=='write').update({key:value}))
        run(lambda r:next(x for x in r if x['kind']=='copy')['src'].update(fbo=999))
        run(lambda r:next(x for x in r if x['kind']=='write')['uniforms'].append({'name':'tex','type':35678,'value':[0]}))


if __name__=='__main__':unittest.main(verbosity=2)
