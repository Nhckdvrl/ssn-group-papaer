"""Scoring must not turn partial or out-of-range judge text into valid evidence."""
import json,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from summarize_results import parse_arcane_local,first_valid
from summarize_state_quality import parse_puf

class ArcaneTransportTest(unittest.TestCase):
 def row(self,text,kind='per_response',finish='stop'):
  return dict(response=text,kind=kind,mode='arc',novel='book',character_slug='role',probe_id='probe',finish_reason=finish,task_id='id',actor_model='actor')
 def test_native_json_and_fence(self):
  for s in ['{"scores":{"apf":1,"rpf":100,"rae":50}}','```json\n{"scores":{"apf":1,"rpf":100,"rae":50}}\n```']:
   r=parse_arcane_local(self.row(s));self.assertTrue(r['parse_ok']);self.assertTrue(r['native_json'])
 def test_complete_scores_with_truncated_commentary_are_flagged(self):
  r=parse_arcane_local(self.row('```json\n{"scores":{"ptf_alignment":50,"ptf_direction":60,"ptf_shape":70},"average":60}\n```\nRationale incomplete...','trajectory','length'))
  self.assertTrue(r['parse_ok']);self.assertFalse(r['native_json']);self.assertEqual(r['finish_reason'],'length')
 def test_never_infer_partial_scores(self):
  self.assertFalse(parse_arcane_local(self.row('{"scores":{"apf":90,"rpf":80,"rae":'))['parse_ok'])
 def test_missing_bool_float_and_out_of_range_are_invalid(self):
  for v in [None,True,50.5,0,101]:
   scores=dict(apf=50,rpf=50,rae=v)
   if v is None:del scores['rae']
   self.assertFalse(parse_arcane_local(self.row(json.dumps(dict(scores=scores))))['parse_ok'])
 def test_first_valid_does_not_reselect_by_score(self):
  rows=[dict(judge_id='x',parse_ok=False,scores=None),dict(judge_id='x',parse_ok=True,scores=10),dict(judge_id='x',parse_ok=True,scores=90)]
  self.assertEqual(first_valid(rows,'judge_id')[0]['scores'],10)

class PUFTransportTest(unittest.TestCase):
 def test_native_arithmetic_and_own_score_ignored(self):
  p=parse_puf(json.dumps(dict(merits=[dict(points=8)],demerits=[dict(points=-3)],score=99)))
  self.assertEqual(p['score'],55)
 def test_missing_structure_does_not_default_to_fifty(self):
  self.assertFalse(parse_puf('{}')['parse_ok'])
  self.assertFalse(parse_puf('{"merits":[],"demerits":')['parse_ok'])
 def test_range_diagnostic_does_not_silently_change_native_arithmetic(self):
  p=parse_puf('{"merits":[{"points":18}],"demerits":[]}')
  self.assertEqual(p['score'],68);self.assertFalse(p['all_points_within_prompt_range'])
if __name__=='__main__':unittest.main()
