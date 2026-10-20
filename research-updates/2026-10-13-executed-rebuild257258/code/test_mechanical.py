import unittest,tempfile
from pathlib import Path
import numpy as np
from build_counts import build,normalized_runs
from finite_model import Model,better,validate
class Tests(unittest.TestCase):
 def test_counts_boundaries_and_ch(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);(p/'text').write_text('áb!ch a');build(p/'text',p/'counts.npz');m=Model(p/'counts.npz');k=tuple(range(27));s=m.score(k,[[26],[0]])
   self.assertEqual(s['emitted_characters'],3);self.assertEqual(s['mapped_source_units'],2)
   expected=m.logs[0][0,2]+m.logs[1][2,7]+m.logs[0][0,0]
   self.assertAlmostEqual(s['log_sum'],expected);self.assertEqual(normalized_runs('áb!ch a'),['ab','ch','a'])
   self.assertAlmostEqual(float(np.exp(m.logs[3][17575,0])),1/26)
   self.assertEqual(int(m.counts[1].sum()),2)
 def test_ties_dummy(self):
  k=tuple(range(27));v=list(k);v[25],v[26]=v[26],v[25];v=tuple(v)
  self.assertEqual(len(set([k,k,v])),2);self.assertEqual(k[:7],v[:7]);self.assertEqual(better(0,k,0,v),tuple('abcdefghijklmnopqrstuvwxyz')+('ch',)<tuple('abcdefghijklmnopqrstuvwxy')+('ch','z'))
 def test_limits(self):
  with self.assertRaises(ValueError):validate({'classes':[{'id':str(i)} for i in range(27)],'variants':[{}]*65,'common_identity_stable_occurrences':200})
if __name__=='__main__':unittest.main()
