import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from adaptation_protocol import actor_messages,motivation_messages,decode_state,decode_motivation


class AdaptationProtocolTests(unittest.TestCase):
    def test_generated_state_and_motivation_replace_only_target_slots(self):
        state=dict(profile='GENERATED_STATE',hidden_tracker='own memory',short_description='GENERATED_DESCRIPTION')
        m='## Current Profile\nGOLD_PROFILE\n\n## Hidden Tracker\nGOLD_TRACKER\n\n## Current Short Description\nGOLD_DESCRIPTION\n\n## Next Scene Scenario\nNEW_SITUATION'
        e=dict(role='Ada',motivation_input=[dict(role='system',content='instructions'),dict(role='user',content=m)],
               update_input=[dict(role='system',content='update'),dict(role='user',content='PAST_EXPERIENCE')])
        out=motivation_messages(e,state)
        text=json.dumps(out)
        self.assertNotIn('GOLD_',text);self.assertIn('NEW_SITUATION',text)
        self.assertIn('GOLD_PROFILE',e['motivation_input'][1]['content'])
        q=dict(messages=[dict(role='system',content='## Your Character State\n'+json.dumps({'Ada':dict(profile='GOLD_PROFILE',hidden_tracker='GOLD_TRACKER',motivation='GOLD_MOTIVATION')})+'\n\n## Other Characters\nOTHER_UNCHANGED'),dict(role='user',content='LIVE_CUE')])
        out=actor_messages(e,q,state,'GENERATED_MOTIVATION')
        text=json.dumps(out)
        self.assertNotIn('GOLD_',text);self.assertIn('OTHER_UNCHANGED',text);self.assertIn('LIVE_CUE',text)
        self.assertIn('GENERATED_MOTIVATION',text)

    def test_incomplete_state_cannot_silently_become_valid_or_use_reference(self):
        old=dict(profile='old',hidden_tracker='memory')
        self.assertIsNone(decode_state('{"profile_updated":true,"updated_profile":"new"}',old))
        self.assertIsNone(decode_motivation('{"motivation":null}'))
        valid=json.dumps(dict(profile_updated=False,updated_profile=None,hidden_tracker='new event',short_description='current'))
        self.assertEqual(decode_state(valid,old)['profile'],'old')
        self.assertEqual(decode_state('```json\n'+valid+'\n```',old)['hidden_tracker'],'new event')

    def test_complete_judge_content_and_strict_json_are_distinct(self):
        from score_adaptation_quality import parse_score,DIMENSIONS
        text=json.dumps({k:4 for k in DIMENSIONS})
        self.assertTrue(parse_score(text)['strict_json'])
        self.assertFalse(parse_score('```json\n'+text+'\n```')['strict_json'])
        self.assertFalse(parse_score(text+'\nAdditional commentary')['strict_json'])
        self.assertIsNone(parse_score(text[:-1]))

    def test_invalid_judge_dimension_is_not_silently_repaired(self):
        from score_adaptation_quality import parse_score,DIMENSIONS
        for bad in [True,'4',0,6,None]:
            value={k:4 for k in DIMENSIONS};value[DIMENSIONS[0]]=bad
            self.assertIsNone(parse_score(json.dumps(value)))


if __name__=='__main__':unittest.main()
