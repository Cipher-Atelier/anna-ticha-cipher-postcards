import copy,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from finite_model import validate
from run_experiment import ROOT,packet,require_class_order,learn_development,evaluate_held,code_hashes,file_hash
class PhaseTests(unittest.TestCase):
 def test_held_class_order(self):
  p=packet([list(range(27))*4]);ids=[c['id'] for c in p['classes']]
  require_class_order(p,ids)
  for classes in [p['classes'][::-1],p['classes'][:-1]]:
   q=copy.deepcopy(p);q['classes']=classes
   with self.assertRaises(ValueError):require_class_order(q,ids)
 def test_numeric_claim_and_variants(self):
  p=packet([list(range(27))*6]);validate(p)
  cases=[]
  q=copy.deepcopy(p);q['variants'][0]['runs']=[[p['classes'][0]['id']]];cases.append(q)
  q=copy.deepcopy(p);q['variants'][0]['id']='';cases.append(q)
  q=copy.deepcopy(p);q['variants']*=2;cases.append(q)
  q=copy.deepcopy(p);q['variants'][0]['runs'][0][0]='UNKNOWN';cases.append(q)
  for q in cases:
   with self.assertRaises(ValueError):validate(q)
 def test_phase_no_held_dependency_and_no_refit(self):
  with tempfile.TemporaryDirectory() as tmp:
   d=Path(tmp);dev=packet([list(range(27))*6]);held=packet([list(range(27))*4]);(d/'dev').write_text(json.dumps(dev));(d/'held').write_text(json.dumps(held));key=tuple(range(27))
   with patch('run_experiment.optimize',return_value=(key,[key,key[::-1]],[{'seed':0,'key':key,'worst_score':0}],0)) as opt:
    learn_development(d/'dev',d/'freeze');opt.assert_called_once()
   with patch('run_experiment.optimize',side_effect=AssertionError('refit')),patch('run_experiment.build',side_effect=AssertionError('rebuild')):
    result=evaluate_held(d/'freeze',d/'held',d/'out');self.assertEqual(result['optimizer_calls'],0)
   with self.assertRaises(FileExistsError):
    with patch('run_experiment.optimize',return_value=(key,[key],[],0)):learn_development(d/'dev',d/'freeze')
   f=json.loads((d/'freeze').read_text());f['counts_sha256']='bad';(d/'bad').write_text(json.dumps(f))
   with self.assertRaisesRegex(ValueError,'counts hash'):evaluate_held(d/'bad',d/'held',d/'out2')
if __name__=='__main__':unittest.main()
