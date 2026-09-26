import collections
import unittest

import e01


class InstrumentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.main, cls.controls = e01.generate()

    def test_full_invariants(self):
        e01.check(self.main, self.controls)

    def test_pair_only_role_sentence_changes(self):
        by_pair = collections.defaultdict(dict)
        for row in self.main:
            by_pair[row["pair_id"]][row["role"]] = row
        for pair in by_pair.values():
            definition, fact = pair["definition"], pair["fact"]
            self.assertEqual(definition["relation"], fact["relation"])
            self.assertEqual(definition["world_a"], fact["world_a"])
            self.assertEqual(definition["world_b"], fact["world_b"])
            self.assertEqual(definition["prompt"].count(definition["relation"]), 1)
            self.assertEqual(fact["prompt"].count(fact["relation"]), 1)
            self.assertEqual(definition["prompt"].replace(e01.FRAMES[definition["frame"]][0], "ROLE"),
                             fact["prompt"].replace(e01.FRAMES[fact["frame"]][1], "ROLE"))

    def test_ground_truth_crossed_and_polarity_balanced(self):
        for readout in ("positive", "exception"):
            for role in ("definition", "fact"):
                for frame in range(3):
                    rows = [r for r in self.main if (r["readout"], r["role"], r["frame"]) == (readout, role, frame)]
                    self.assertEqual(len(rows), 40)
                    self.assertEqual(collections.Counter(r["expected"] for r in rows), {"A": 20, "B": 20})
                    for r in rows:
                        expected_yes = (role == "definition") == (r["polarity"] == 0)
                        self.assertEqual(r["expected"], "A" if expected_yes else "B")

    def test_world_b_exception_really_violates_property(self):
        for r in self.main:
            self.assertIn(r["relation"], r["prompt"])
            if r["readout"] == "exception":
                relation_color = r["relation"].split("color ")[1].split(" and")[0]
                b_color = r["world_b"].split("color ")[1].split(" and")[0]
                self.assertNotEqual(relation_color, b_color)
            else:
                relation_color = r["relation"].split("color ")[1].split(" and")[0]
                self.assertIn("color " + relation_color + " and", r["world_b"])

    def test_parser_is_exact(self):
        for raw, parsed in ((" A\n", "A"), ("B", "B"), ("A because", None),
                            ("AB", None), ("yes", None), ("", None)):
            self.assertEqual(e01.parse_answer(raw), parsed)


if __name__ == "__main__":
    unittest.main()
