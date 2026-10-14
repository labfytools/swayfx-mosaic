import unittest
from pathlib import Path
from PIL import Image
from gpu_replay import replay,homologous,diff
from native_replay import validate_claims
LAB=Path('/home/fy59/swayfx-mosaic-targeted-7gge6h8b/runs')
class GPUReplayTests(unittest.TestCase):
    def test_real_whole_differences(self):
        for name,pixels in [('pristine',37252),('A',34323),('G',34323)]:
            r=replay(LAB/f'FX-{name}/run');d=r['whole_H1_A_return']
            self.assertEqual(d['pixels'],pixels);self.assertEqual(max(v['max_abs'] for v in d['perchannel']),6)
            self.assertEqual(r['CACHE_A_RETURN_CAUSALITY'],'INCONCLUSIVE')
            self.assertTrue(r['source_SHM']['ABA_byte_exact'])
    def test_sixteen_homologous(self):
        self.assertEqual(len(homologous(LAB/'FX-A/run',LAB/'FX-G/run')),16)
    def test_masked_whole_and_source_buffer_output_falseproof(self):
        im=Image.new('RGB',(2,2))
        with self.assertRaises(ValueError):diff(im,im,mask=[])
        with self.assertRaises(ValueError):validate_claims({'source_buffer_is_output':True})
if __name__=='__main__':unittest.main()
