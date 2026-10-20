"""Validate measured decompositions, partitions and executable reconstructions."""
from pathlib import Path
import sys,json,hashlib,unittest
import numpy as np,joblib
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'src'))
from audit import Predictor
from score_reconstruction import Combined
class ScoreReconstructionTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.d=json.loads((R/'results/score_reconstruction/experiment.json').read_text())
  cls.m=joblib.load(R/'results/score_reconstruction/models.joblib')
 def test_split_and_reference_integrity(self):
  splits=json.loads((R/'results/reference/split.json').read_text())
  self.assertTrue(set(self.d['background_record_ids'])<=set(splits['train']))
  self.assertTrue(set(c['case_id'] for c in self.d['cases'])<=set(splits['test']))
  self.assertEqual(len(set(self.d['background_record_ids'])),24)
 def test_all_decompositions_reconstruct_their_own_system(self):
  for c in self.d['cases']:
   original=c['original_shapley'];self.assertAlmostEqual(original['diagnostics']['base']+sum(original['values']),c['original_probability'],places=9)
   for a in c['approximations'].values():
    self.assertAlmostEqual(a['diagnostics']['base']+sum(a['values']),a['probability'],places=9)
    self.assertTrue(np.isfinite(a['values']).all())
 def test_executable_models_reproduce_saved_record_predictions(self):
  m=self.m;predict=Predictor(m['original_model'],m['original_encoding'])
  for c in self.d['cases']:
   x=np.array([[c['inputs'][f] for f in self.d['features']]])
   true=predict(np.column_stack([x,[c['observed_external_score']]]))[0]
   self.assertAlmostEqual(true,c['original_probability'],places=10)
   for k,proxy in m['approximations'].items():
    combined=Combined(proxy,m['encoding'],predict,m['score_clipping_bounds'])
    self.assertAlmostEqual(combined(x)[0],c['approximations'][k]['probability'],places=10)
 def test_agreement_bands_require_original_and_pair_agreement(self):
  for b in self.d['bands']:
   t=b['probability_band'];rows=[c for c in self.d['cases'] if c['comparison']['probability_difference']<=t and c['comparison']['maximum_original_probability_error']<=t]
   self.assertEqual(len(rows),b['both_close_to_original'])
   self.assertEqual(sum(bool(c['comparison']['grouped']['turnover']) for c in rows),b['different_concept_sets_when_both_close_to_original'])
 def test_protocol_fingerprint_matches_delivered_design(self):
  self.assertEqual(self.d['protocol_sha256'],hashlib.sha256((R/'docs/EXTERNAL_SCORE_RECONSTRUCTION.md').read_bytes()).hexdigest())
if __name__=='__main__':unittest.main()
