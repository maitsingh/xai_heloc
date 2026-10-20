"""Meaningful replay/abstention checks for missing and contradictory evidence."""
import copy
import json
from pathlib import Path
import sys
import unittest
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from decision_reconstruction import assess, digest, decide
R=Path(__file__).resolve().parents[1]

class ReconstructionTests(unittest.TestCase):
    def setUp(self):
        self.inputs={'a':.4,'b':.2}; self.policy={'decline_at_or_above':.5}
        self.p={'inputs':self.inputs,'policy':self.policy,'model_sha256':'original',
                'explanation':{'base':.2,'values':[.2,.2]},
                'event':{'prediction':.6,'decision':'Declined','inputs_sha256':digest(self.inputs),'policy_sha256':digest(self.policy),'model_sha256':'original'}}
        self.calls=0
    def predict(self,a):
        self.calls+=1
        return np.array([sum(a[0])])
    def evaluate(self,p):return assess(p,self.predict,'original',['a','b'])
    def test_original_replays_actual_predictor(self):
        r=self.evaluate(self.p)
        self.assertTrue(r['original_decision_reconstructed']);self.assertEqual(self.calls,1)
    def test_missing_policy_preserves_prediction_only(self):
        self.p.pop('policy');r=self.evaluate(self.p)
        self.assertTrue(r['prediction_reproduced']);self.assertFalse(r['original_decision_reconstructed'])
        self.assertEqual(r['inconsistencies'],[])
    def test_new_policy_does_not_establish_old_decision_even_if_same_outcome(self):
        self.p['policy']={'decline_at_or_above':.55};r=self.evaluate(self.p)
        self.assertEqual(decide(.6,self.p['policy']),'Declined')
        self.assertFalse(r['original_decision_reconstructed']);self.assertIn('policy',r['inconsistencies'])
    def test_changed_input_is_not_silently_replayed(self):
        self.p['inputs']['a']=.8;r=self.evaluate(self.p)
        self.assertEqual(self.calls,0);self.assertFalse(r['prediction_reproduced'])
    def test_different_model_identity_is_not_silently_replayed(self):
        self.p['model_sha256']='other';r=self.evaluate(self.p)
        self.assertEqual(self.calls,0);self.assertFalse(r['prediction_reproduced'])
    def test_arithmetic_failure_does_not_erase_valid_decision_replay(self):
        self.p['explanation']['values'][0]+=.1;r=self.evaluate(self.p)
        self.assertFalse(r['explanation_sum_matches']);self.assertTrue(r['original_decision_reconstructed'])
    def test_matching_explanation_does_not_authenticate_prediction(self):
        self.p.pop('inputs');self.p.pop('model_sha256');self.p.pop('policy');r=self.evaluate(self.p)
        self.assertTrue(r['explanation_sum_matches']);self.assertFalse(r['prediction_reproduced'])
    def test_measured_case_coverage_and_expected_manipulations(self):
        d=json.loads((R/'results/decision_reconstruction/experiment.json').read_text())
        self.assertEqual(d['package_count'],280);self.assertEqual(len(d['cases']),40)
        self.assertEqual(d['changed_outcomes_under_later_policy'],20)
        for c in d['cases']:
            self.assertTrue(c['packages']['original']['assessment']['original_decision_reconstructed'])
            self.assertFalse(c['packages']['chart_only']['assessment']['original_decision_reconstructed'])
            self.assertFalse(c['packages']['new_policy']['assessment']['original_decision_reconstructed'])
        self.assertEqual({r['records'] for r in d['summary']},{40})

if __name__=='__main__':unittest.main()
