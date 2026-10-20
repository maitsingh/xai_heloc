import json,unittest
from pathlib import Path
from copy import deepcopy
from src.evidence_review import review
R=Path(__file__).resolve().parents[1]

class EvidenceReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs=json.loads((R/'results/notice_audit/inputs.json').read_text())
        cls.truth={r['id']:r for r in json.loads((R/'results/notice_audit/truth.json').read_text())}
    def test_borrower_partitions_do_not_overlap(self):
        p=json.loads((R/'results/notice_audit/partition.json').read_text())
        self.assertEqual(sum(v=='evaluation' for v in p.values()),20)
        for s in self.inputs:self.assertEqual(self.truth[s['id']]['partition'],p[str(s['case_id'])])
    def test_matching_historical_artifact_is_not_flagged_for_being_old(self):
        s=next(s for s in self.inputs if self.truth[s['id']]['scenario']=='historical')
        self.assertEqual(review(s['bundle'])['disposition'],'No discrepancy detected')
    def test_missing_evidence_is_not_a_confirmed_defect(self):
        self.assertEqual(review({'notice':{}})['disposition'],'Insufficient evidence')
    def test_checker_cannot_see_truth_and_same_input_has_same_review(self):
        for s in self.inputs[:20]:
            self.assertNotIn('family',s['bundle']);self.assertNotIn('scenario',s['bundle'])
            self.assertEqual(review(s['bundle']),review(deepcopy(s['bundle'])))
    def test_termination_rule_distinguished_from_diagnostic_score(self):
        s=next(s for s in self.inputs if self.truth[s['id']]['scenario']=='omitted_policy')
        self.assertIn('decision_coverage',{f['code'] for f in review(s['bundle'])['findings']})

if __name__=='__main__':unittest.main()
