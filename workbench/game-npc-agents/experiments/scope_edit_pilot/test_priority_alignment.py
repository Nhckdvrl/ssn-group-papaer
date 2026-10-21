import unittest,tempfile,json
from pathlib import Path
from alignment_audit import lint,annotation,score
from priority_pilot import prepare
import scope_probe as p

class PriorityAlignmentTests(unittest.TestCase):
    def test_lint_is_not_a_keyword_verdict(self):
        self.assertIn('commitment',lint("But if you insist, I'll do it."))
        self.assertNotIn('commitment',lint('I will not do it.'))
        self.assertIn('reported_speech',lint('The patron said "I will perform".'))
        self.assertIn('permission_ambiguous',lint('You may proceed.'))
        self.assertNotIn('permission_ambiguous',lint('You may not proceed.'))
        self.assertNotIn('commitment',lint('Healer, attend to him.'))
    def test_unknown_not_counted_as_proven_effective(self):
        t=dict(task_id='x',story_id='s',case_id='c',variant='base',mode='situated',scope='preserve',allowed_actions=['A','B'],expected_actions=['B'])
        raw='{"action_id":"B","utterance":"You may proceed."}'
        a=annotation(t,raw,'unclear','Proceed has no explicit complement.')
        z=score([t],[dict(task_id='x',raw=raw)],[a])['summary']['situated']
        self.assertEqual((z['action_matches'],z['effective_lower'],z['effective_upper']),(1,0,1))
        with self.assertRaises(AssertionError):score([t],[dict(task_id='x',raw=raw+' ')],[a])
    def test_compilation_no_test_or_oracle_information(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d);prepare(out);tasks=p.read_jsonl(out/'qwen_stage1_tasks.jsonl')
            self.assertEqual(len(tasks),108)
            teachers=[t for t in tasks if t['task_id'].startswith('compile/')]
            for t in teachers:
                other=next(x for x in teachers if x['story_id']==t['story_id'] and x['mode']!=t['mode'])
                self.assertEqual(t['messages'][1],other['messages'][1])
                self.assertNotIn('CURRENT SCENE',str(t['messages']))
                self.assertNotIn('expected_actions',str(t['messages']))
                for s in p.read_json(out/'fixtures_v2.json')['stories']:
                    self.assertNotIn(s['author_edit'],str(t['messages']))
                    for c in s['cases']:self.assertNotIn(c['scenario'],str(t['messages']))

if __name__=='__main__':unittest.main()
