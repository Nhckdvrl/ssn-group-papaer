import unittest
from e01r_instruments import case_metrics,intervention,tag_metrics

class E01RInstrumentTests(unittest.TestCase):
    def test_balanced_codebook_contains_both_rules(self):
        for family,actions in [('case',('lower','upper')),('tag',('amber','violet'))]:
            for template in ('A','B'):
                for mapping in ('identity','swapped'):
                    texts=[intervention(family,template,mapping,a)['text'] for a in actions]
                    self.assertIn('Rule 1',texts[0]); self.assertIn('Rule 2',texts[0])
                    self.assertEqual(texts[0].replace('Rule 1 now','Rule X now').replace('Rule 2 now','Rule X now'),
                                     texts[1].replace('Rule 1 now','Rule X now').replace('Rule 2 now','Rule X now'))
    def test_mapping_swap_changes_label_not_semantics(self):
        self.assertEqual(intervention('case','A','identity','lower')['selected_label'],'1')
        self.assertEqual(intervention('case','A','swapped','lower')['selected_label'],'2')
    def test_case_metrics(self):
        self.assertTrue(case_metrics('all lower letters.',True)['lower_strict'])
        self.assertTrue(case_metrics('ALL UPPER LETTERS.',True)['upper_strict'])
        self.assertFalse(case_metrics('Mixed Case.',True)['lower_strict'])
        self.assertFalse(case_metrics('all lower letters',False)['lower_strict'])
    def test_tag_requires_leading_tag_and_reasoning(self):
        self.assertTrue(tag_metrics('[amber] enough reasoning follows here')['amber_success'])
        self.assertFalse(tag_metrics('reasoning [amber] arrives late')['amber_success'])
        self.assertFalse(tag_metrics('[violet] short')['violet_success'])

if __name__=='__main__': unittest.main()
