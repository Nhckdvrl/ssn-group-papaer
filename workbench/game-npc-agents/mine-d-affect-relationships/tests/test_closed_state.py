import json,sys,unittest
from pathlib import Path
from types import SimpleNamespace
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from run_closed_updates import substitute,decode_state
from score_role_likelihood import character_regions

class ClosedStateTests(unittest.TestCase):
 def test_replacing_state_preserves_scene_and_current_motivation(self):
  s='## Scene Interactions\nA hit B\n\n## Current Profile (State At Scene Start)\nold P\n\n## Hidden Tracker (State At Scene Start)\nold H\n\n## Current Motivation (State At Scene Start)\nprotect B'
  v=substitute(s,dict(profile='new P',hidden_tracker='new H'))
  self.assertEqual(v.split('## Current Profile')[0],s.split('## Current Profile')[0]);self.assertEqual(v.split('## Current Motivation')[1],s.split('## Current Motivation')[1]);self.assertIn('new H',v);self.assertNotIn('old H',v)
 def test_no_profile_edit_still_commits_new_tracker(self):
  before=dict(profile='stable identity',hidden_tracker='old belief');native=SimpleNamespace(extract_json_fragment=json.loads,dict_to_markdown_text=str)
  r=decode_state(json.dumps(dict(profile_updated=False,updated_profile=None,hidden_tracker='new evidence',short_description='same person, now informed')),before,native)
  self.assertEqual(r['profile'],'stable identity');self.assertEqual(r['hidden_tracker'],'new evidence');self.assertEqual(before['hidden_tracker'],'old belief')
 def test_missing_flag_cannot_become_valid_no_update(self):
  native=SimpleNamespace(extract_json_fragment=json.loads,dict_to_markdown_text=str)
  self.assertIsNone(decode_state('{"hidden_tracker":"x","short_description":"y"}',dict(profile='z'),native))
 def test_visible_actions_are_distinct_from_private_thought(self):
  text='[I distrust her.] (I close the door.) No.';inside,valid=character_regions(text);self.assertTrue(valid);self.assertTrue(inside[2]);self.assertFalse(inside[text.index('close')]);self.assertFalse(character_regions('[unclosed')[1])
if __name__=='__main__':unittest.main()
