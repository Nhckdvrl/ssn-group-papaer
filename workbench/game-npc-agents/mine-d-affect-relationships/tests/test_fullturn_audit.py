import importlib.util
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from audit_fullturn_study import DIMENSIONS,readable_original_scores,complete_book_values
from score_adaptation_quality import parse_score


class FullturnAudit(unittest.TestCase):
    def test_numeric_sensitivity_preserves_values_without_changing_strict_parser(self):
        values=dict(zip(DIMENSIONS,[1,2,3,4,5]))
        valid=json.dumps(dict(values,reason='ok'))
        broken=valid.replace('"ok"','"a "quoted" reason"')
        self.assertIsNone(parse_score(broken))
        self.assertEqual(readable_original_scores(broken)['scores'],values)
        self.assertEqual(readable_original_scores(valid)['scores'],values)
        self.assertEqual(readable_original_scores(broken)['mode'],'complete_numeric_prefix_before_malformed_reason')

    def test_ambiguous_or_incomplete_numeric_fields_are_not_invented(self):
        text=json.dumps({**{d:1 for d in DIMENSIONS},'reason':'ok'}).replace('"ok"','"a "quoted" reason"')
        self.assertIsNone(readable_original_scores(text.replace('"experience_interpretation": 1,','')))
        self.assertIsNone(readable_original_scores(text.replace('"experience_interpretation": 1,','"experience_interpretation": 6,')))
        self.assertIsNone(readable_original_scores(text.replace('"experience_interpretation": 1,','"experience_interpretation": 1, "experience_interpretation": 5,')))

    def test_more_questions_do_not_give_a_role_more_weight(self):
        def row(book,role,value):return dict(book_name=book,episode_id=role,result=dict(scores={d:value for d in DIMENSIONS}))
        data=[row('one','a',1),row('one','a',5),row('one','b',4),row('two','c',2)]
        self.assertEqual(complete_book_values(data,['one','two']),[3.5,2])


if __name__=='__main__':unittest.main()
