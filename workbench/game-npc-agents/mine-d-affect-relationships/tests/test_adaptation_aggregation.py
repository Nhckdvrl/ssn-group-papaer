import copy
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from summarize_adaptation_study import aggregate_primary,DIMENSIONS


class AdaptationAggregationTests(unittest.TestCase):
    def row(self,book,role,question,value):
        return dict(book_name=book,episode_id=role,question_id=question,valid=True,
                    result=dict(scores={d:value for d in DIMENSIONS}))

    def test_more_queries_do_not_turn_one_role_into_more_independent_people(self):
        rows=[self.row('A','person1','q1',1),self.row('A','person2','q2',5),self.row('B','person3','q3',5)]
        _,_,original=aggregate_primary(rows,['A','B'],3)
        rows += [self.row('A','person1','extra'+str(i),1) for i in range(40)]
        _,bybook,repeated=aggregate_primary(rows,['A','B'],len(rows))
        self.assertEqual(original,repeated)
        self.assertTrue(all(v==4 for v in repeated.values()))
        self.assertTrue(all(v==3 for v in bybook['A'].values()))

    def test_missing_judgment_does_not_produce_a_survivor_only_primary_mean(self):
        rows=[self.row('A','a','1',2),self.row('B','b','2',5)]
        rows[0]['valid']=False;rows[0]['result']=None
        good,bybook,metrics=aggregate_primary(rows,['A','B'],2)
        self.assertEqual(len(good),1)
        self.assertIsNone(metrics)
        self.assertTrue(all(v is None for v in bybook['A'].values()))


if __name__=='__main__':unittest.main()
