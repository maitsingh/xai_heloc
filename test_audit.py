import unittest
import numpy as np
from src.audit import exact_shapley, Encoding, reason_list, compare
class AuditChecks(unittest.TestCase):
 def test_shapley_known_additive_model(self):
  phi,m=exact_shapley(np.array([3.,4.]),np.array([[0.,0.],[2.,2.]]),lambda a:2*a[:,0]+3*a[:,1])
  np.testing.assert_allclose(phi,[4,9],atol=1e-10);self.assertLess(abs(m['residual']),1e-10)
 def test_special_states_distinct(self):
  e=Encoding().fit(np.array([[2.],[6.]]));z=e.transform(np.array([[-7.],[-8.],[-9.],[4.]]))
  self.assertEqual(len(np.unique(z,axis=0)),4);np.testing.assert_array_equal(z[:,0],[4,4,4,4])
 def test_group_signed_cancellation(self):
  rs=reason_list([.3,-.4,.1],['MSinceOldestTradeOpen','AverageMInFile','NumInqLast6M'],True)
  self.assertEqual([r['id'] for r in rs],['Recent inquiries'])
 def test_empty_list_is_unresolved(self):self.assertIsNone(compare([],[])['retention'])
 def test_distinct_overlap_denominators(self):
  c=compare([{'id':i} for i in ['a','b','c','d']],[{'id':i} for i in ['a','b','e','f']])
  self.assertEqual(c['retention'],.5);self.assertAlmostEqual(c['jaccard'],1/3)
if __name__=='__main__':unittest.main()
