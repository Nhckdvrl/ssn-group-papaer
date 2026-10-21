"""No-network v1.1 protocol tests. Run: python3 -m unittest -v test_v11_probe.py"""
import json
import unittest
from pathlib import Path
import v11_probe as v11

ROOT = Path(__file__).parent

class V11Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixtures = v11.v1.read_json(str(ROOT / "fixtures.json"))
        cls.overrides = v11.load_extra(str(ROOT / "v11_annotations.json"))
        cls.tasks = v11.make_tasks(cls.fixtures,cls.overrides)

    def test_count_and_modes(self):
        self.assertEqual(len(self.tasks),60)
        self.assertEqual({t["mode"] for t in self.tasks},{"original","explicit","situated"})
        self.assertEqual(len({t["story_id"] for t in self.tasks}),4)

    def test_no_oracle_gold_in_prompts(self):
        for t in self.tasks:
            x = json.dumps(t["messages"])
            self.assertNotIn("expected_actions",x)
            self.assertNotIn("situated_scope",x)
            self.assertNotIn("editor_rationale",x)

    def test_abstract_rule_not_leaked_to_situated(self):
        for s in self.fixtures["stories"]:
            subset = [t for t in self.tasks if t["story_id"]==s["story_id"] and t["mode"]=="situated"]
            self.assertTrue(subset)
            for t in subset:
                self.assertNotIn(s["author_edit"],t["messages"][1]["content"])

    def test_messages_and_actions_are_separated(self):
        for t in self.tasks:
            self.assertIn("AVAILABLE PHYSICAL/NARRATIVE ACTIONS",t["messages"][1]["content"])
            self.assertIn("utterance",t["messages"][0]["content"])
            self.assertNotIn('"thought"',t["messages"][0]["content"])

    def test_situated_underspecified_is_not_strict_accuracy(self):
        oracle = [{"task_id":t["task_id"],"action_id":t["expected_actions"][0]} for t in self.tasks]
        result = v11.evaluate(self.tasks,oracle)
        self.assertEqual(len(result["paired_comparisons"]),40)
        self.assertTrue(any(x["n_author_intent_only"]>0 for x in result["metrics"] if x["mode"]=="situated"))
        self.assertTrue(any(x["n_scored"]>0 for x in result["metrics"] if x["mode"]=="explicit"))

    def test_pressure_has_same_expected_action(self):
        indexed = {(t["story_id"],t["case_id"],t["mode"],t["variant"]):t for t in self.tasks}
        for t in self.tasks:
            if t["variant"]=="pressure":
                normal = indexed[(t["story_id"],t["case_id"],t["mode"],"base")]
                self.assertEqual(t["expected_actions"],normal["expected_actions"])
                self.assertEqual(t["scope"],"preserve")

    def test_duplicate_responses_rejected(self):
        q = self.tasks[0]
        with self.assertRaisesRegex(ValueError,"Duplicate"):
            v11.evaluate(self.tasks,[{"task_id":q["task_id"],"action_id":"A"}]*2)

if __name__=="__main__":
    unittest.main()
