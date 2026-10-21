"""No-network smoke tests: python3 -m unittest -v test_scope_probe.py"""
import json,unittest
from pathlib import Path
from scope_probe import validate,render,parse_reply,score

class TestScopeProbe(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads(Path(__file__).with_name("fixtures.json").read_text(encoding="utf-8"))
        cls.tasks=render(cls.data)
    def test_schema_counts_and_scope(self):
        self.assertEqual(validate(self.data),{"stories":4,"cases":16,"change":8,"preserve":8})
        self.assertEqual(len(self.tasks),32)
    def test_gold_not_in_model_messages(self):
        for t in self.tasks:
            x=json.dumps(t["messages"])
            self.assertNotIn("expected_actions",x)
            self.assertNotIn("editor_rationale",x)
    def test_before_after_have_identical_case_and_choices(self):
        pairs={}
        for t in self.tasks: pairs.setdefault((t["story_id"],t["case_id"]),{})[t["condition"]]=t
        for both in pairs.values():
            pre=both["before"]["messages"][1]["content"]
            post=both["after"]["messages"][1]["content"]
            self.assertIn("AUTHOR'S NEW CHARACTER REVISION",post)
            self.assertNotIn("AUTHOR'S NEW CHARACTER REVISION",pre)
            self.assertEqual(pre.split("Current scene:\n")[1],post.split("Current scene:\n")[1])
    def test_perfect_oracle_roundtrip(self):
        a=[{"task_id":t["task_id"],"action_id":t["expected_actions"][0],"utterance":"fake oracle"} for t in self.tasks]
        s=score(self.tasks,a)
        self.assertEqual(s["groups"]["change"]["paired_both_correct"],8)
        self.assertEqual(s["groups"]["preserve"]["paired_both_correct"],8)
        self.assertEqual(s["groups"]["change"]["action_changed"],8)
        self.assertEqual(s["groups"]["preserve"]["action_changed"],0)
    def test_wrong_target_lowers_correct_count(self):
        a=[{"task_id":t["task_id"],"action_id":t["expected_actions"][0]} for t in self.tasks]
        q=next(t for t in self.tasks if t["scope"]=="change" and t["condition"]=="after")
        next(x for x in a if x["task_id"]==q["task_id"])["action_id"]=next(x for x in q["allowed_actions"] if x not in q["expected_actions"])
        self.assertEqual(score(self.tasks,a)["groups"]["change"]["paired_both_correct"],7)
    def test_response_parser_requires_json(self):
        self.assertEqual(parse_reply('{"action_id":"B","utterance":"No."}'),("B","No."))
        self.assertEqual(parse_reply("Sure, action B."),(None,None))
    def test_cannot_double_count_response(self):
        t=self.tasks[0]
        with self.assertRaises(ValueError):score(self.tasks,[{"task_id":t["task_id"],"action_id":"A"}]*2)

if __name__=="__main__":unittest.main()
