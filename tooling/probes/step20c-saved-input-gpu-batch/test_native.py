import unittest
from pathlib import Path
from native_replay import replay,validate_claims
from input_validators import InvalidEvidence
LAB=Path('/home/fy59/swayfx-mosaic-targeted-7gge6h8b')
class NativeTests(unittest.TestCase):
    def test_real_all_821(self):
        reports=[replay(p.read_text()) for p in (LAB/'runs').glob('*/run/compositor.log')]
        self.assertEqual(tuple(sum(r[k] for r in reports) for k in ('total_commits','paired','missing')),(821,789,32))
    def test_real_57(self):
        p=Path('/home/fy59/swayfx-mosaic-overnight-mcolx0gq/matrix/F-mosaic/run/compositor.log')
        r=replay(p.read_text());self.assertEqual(tuple(r[k] for k in ('total_commits','paired','missing')),(57,55,2))
    def test_wrong_output_fake_present(self):
        text='PI_OUTPUT_COMMIT output=H1 commit_seq=1 ns=10\nPI_OUTPUT_PRESENT output=H2 commit_seq=1 ns=20 presented=1'
        r=replay(text);self.assertEqual(r['missing'],1);self.assertEqual(len(r['unmatched_presents']),1)
        with self.assertRaises(InvalidEvidence):replay(text.replace('H2','H1').replace('ns=20','ns=9'))
        with self.assertRaises(InvalidEvidence):replay(text.replace('presented=1',''))
    def test_no_invented_generation_or_gpu_or_buffer(self):
        for claim in ('atomic_generation','source_buffer_is_output','gpu_completion','all_frames_damage'):
            with self.assertRaises(InvalidEvidence):validate_claims({claim:True})
    def test_unknown_missing_not_guessed_from_teardown(self):
        t='PI_OUTPUT_COMMIT output=H1 commit_seq=1 ns=10\noutput destroyed ns=11'
        self.assertEqual(replay(t)['rows'][0]['missing_cause']['kind'],'UNKNOWN')
        with self.assertRaises(InvalidEvidence):replay(t,{('H1',1):{'kind':'OUTPUT_DESTROY'}})
if __name__=='__main__':unittest.main()
