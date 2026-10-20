import json,unittest
from pathlib import Path
import numpy as np
from src.reference_experiment import neighborhood
R=Path(__file__).resolve().parents[1]

class ReferenceOutputTests(unittest.TestCase):
    def test_every_reference_explanation_reconstructs_unchanged_prediction(self):
        d=json.loads((R/'results/reference_sensitivity/experiment.json').read_text())
        self.assertEqual(len(d['records']),240)
        for r in d['records']:
            self.assertAlmostEqual(r['diagnostics']['base']+sum(r['values']),r['score'],places=10)
    def test_evaluation_neighborhood_does_not_force_the_fitting_anchor(self):
        train=np.arange(800,dtype=float).reshape(100,8);x=train[50]
        z,_,_=neighborhood(x,train,10000,include_anchor=False)
        self.assertFalse(np.array_equal(z[0],x))
        fit,_,_=neighborhood(x,train,0)
        self.assertTrue(np.array_equal(fit[0],x))
    def test_record_cluster_counts_and_reference_cardinality(self):
        d=json.loads((R/'results/reference_sensitivity/experiment.json').read_text())
        for row in d['summary']:
            self.assertEqual(row['turnover']['records'],40)
            self.assertEqual(row['turnover']['scenarios'],120)
        for m in d['reference_manifests']:self.assertEqual(len(m['values']),24)

if __name__=='__main__':unittest.main()
