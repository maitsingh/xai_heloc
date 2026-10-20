"""Verify the descriptive masking count against retained attribution lists."""
import json,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
class GroupingAnalysisTests(unittest.TestCase):
 def test_hidden_changes_have_changed_factors_and_unchanged_categories(self):
  data=json.loads((R/'results/reference_sensitivity/grouping_analysis.json').read_text())
  ref=json.loads((R/'results/reference_sensitivity/experiment.json').read_text())
  hidden=0;apps=set()
  for r in data['records']:
   a=next(x for x in ref['records'] if x['case_id']==r['case_id'] and x['reference']=='population' and x['seed']==r['seed'])
   b=next(x for x in ref['records'] if x['case_id']==r['case_id'] and x['reference']=='near_cutoff' and x['seed']==r['seed'])
   detailed={x['id'] for x in a['individual']}!={x['id'] for x in b['individual']}
   grouped={x['id'] for x in a['grouped']}!={x['id'] for x in b['grouped']}
   expected=detailed and not grouped
   self.assertEqual(expected,r['hidden_change'])
   if expected:hidden+=1;apps.add(r['case_id'])
  self.assertEqual(hidden,data['hidden_change_comparisons'])
  self.assertEqual(len(apps),data['applications_with_hidden_change'])
  self.assertEqual(len(data['records']),data['paired_comparisons'])
if __name__=='__main__':unittest.main()
