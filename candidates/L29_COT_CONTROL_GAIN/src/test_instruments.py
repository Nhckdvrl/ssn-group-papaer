import unittest
from instruments import violation,choose_prefix,has_answer
from summarize_audit import max_window_mean

class Chars:
    def decode(self,ids,**kwargs): return ''.join(ids)

class InstrumentTests(unittest.TestCase):
    def test_case(self):
        self.assertFalse(violation('abc 123 + =','lowercase',''))
        self.assertTrue(violation('abc X','lowercase',''))
        self.assertFalse(violation('ABC 123','uppercase',''))
        self.assertTrue(violation('ABC x','uppercase',''))
    def test_words_and_truncation(self):
        self.assertFalse(violation('massive ','suppression','mass'))
        self.assertFalse(violation('mass','suppression','mass'))
        self.assertTrue(violation('mass,','suppression','mass'))
        self.assertTrue(violation('MASS ','suppression','mass'))
        self.assertTrue(violation('mass','suppression','mass',complete=True))
        self.assertFalse(violation('biomass ','suppression','mass'))
    def test_prefix_is_pre_violation_and_at_boundary(self):
        txt='we compute the required quantity from the equation. \n'
        n=choose_prefix(list(txt+'BAD'),Chars(),'lowercase','')
        self.assertIsNotNone(n); self.assertNotIn('BAD',txt[:n])
        self.assertIsNone(choose_prefix(list('Bad '+txt),Chars(),'lowercase',''))
    def test_suppression_prefix_precedes_imminent_natural_violation(self):
        txt='we compute the first quantity. then the forbidden value appears.'
        n=choose_prefix(list(txt),Chars(),'suppression','forbidden')
        self.assertEqual(''.join(list(txt)[:n]),'we compute the first quantity.')
        self.assertFalse(violation(txt[:n],'suppression','forbidden',complete=True))
    def test_decimal_period_is_not_boundary(self):
        txt='the value is 0.132 atm and continues.'
        self.assertIsNone(choose_prefix(list(txt),Chars(),'suppression','atm'))
    def test_answer_rejected(self):
        self.assertTrue(has_answer('work\nAnswer: B'))
        self.assertTrue(has_answer('work\nfinal answer: b'))
        self.assertIsNone(choose_prefix(list('Answer: B\n'+'x '*50),Chars(),'lowercase',''))
    def test_no_empty_mathematical_only_state(self):
        self.assertIsNone(choose_prefix(list('1 + 2 = 3\n'*10),Chars(),'lowercase',''))
    def test_support_window_handles_short_prefix(self):
        self.assertEqual(max_window_mean([1.0,3.0],16),2.0)
        self.assertEqual(max_window_mean([0.0]*16+[32.0],16),2.0)
if __name__=='__main__': unittest.main()
