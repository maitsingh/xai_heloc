"""Validate the reported paired experiment against its retained per-application results."""
import json,unittest
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1]
class ExternalScoreTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.d=json.loads((R/'results/external_score/experiment.json').read_text())
  cls.old=json.loads((R/'results/reference/audit_results.json').read_text())
 def test_pairing_keeps_changed_outcomes(self):
  expected={c['case_id'] for c in self.old['cases'] if c['model']=='without_score'}
  self.assertEqual(expected,{p['case_id'] for p in self.d['pairs']})
  for variant in ['with_score','without_score']:self.assertEqual(expected,{r['case_id'] for r in self.d['records'] if r['model']==variant})
  self.assertEqual(sum(p['outcome_changed'] for p in self.d['pairs']),self.d['summary']['outcomes_changed'])
 def test_all_shapley_explanations_reconstruct_predictions(self):
  for r in self.d['records']:
   self.assertAlmostEqual(r['score'],r['shapley']['diagnostics']['base']+sum(r['shapley']['values']),places=10)
   self.assertEqual(len(r['shapley']['values']),len(r['features']))
 def test_original_scores_and_contributions_preserved(self):
  for c in self.old['cases']:
   if c['model']!='without_score':continue
   r=next(r for r in self.d['records'] if r['case_id']==c['case_id'] and r['model']=='without_score')
   self.assertAlmostEqual(c['score'],r['score'],places=10)
   np.testing.assert_allclose(c['explanations']['Exact interventional Shapley'][0]['values'],r['shapley']['values'],atol=1e-10)
 def test_external_summary_uses_positive_contributions_and_correct_denominator(self):
  records=[r for r in self.d['records'] if r['model']=='with_score']
  n=sum(any(v['id']=='ExternalRiskEstimate' for v in r['shapley']['individual']) for r in records)
  self.assertEqual(n,self.d['summary']['external_in_top_adverse'])
  self.assertEqual(len(records),self.d['summary']['paired_applications'])
  for r in records:
   self.assertEqual(5,len(r['surrogate']))
   self.assertTrue(all('heldout_r2' in run for run in r['surrogate']))
if __name__=='__main__':unittest.main()
