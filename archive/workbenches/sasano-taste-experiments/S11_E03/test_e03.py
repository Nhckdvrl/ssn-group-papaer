import collections
import unittest
from decimal import Decimal

import e03

e01 = e03.e01


class IntervalDiagnosticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = e03.make_rows()

    def test_deterministic_frozen_items_and_holdout(self):
        e03.check(self.rows)
        self.assertEqual(self.rows, e01.read_jsonl(e03.HERE / "items.jsonl"))
        self.assertTrue({int(Decimal(x["coarse"]) * 10) for x in self.rows}.isdisjoint(e03.used_numbers()))

    def test_same_interval_threshold_label_across_representations(self):
        groups = collections.defaultdict(dict)
        for x in self.rows:
            groups[(x["base_id"], x["variant"])][x["representation"]] = x
            self.assertEqual(x["expected"], "A" if e01.certifies(
                x["displayed"], x["threshold"], x["direction"]) else "B")
        for group in groups.values():
            rounded = group["rounded_report"]
            direct = group["explicit_interval"]
            self.assertEqual((rounded["interval"], rounded["threshold"], rounded["expected"]),
                             (direct["interval"], direct["threshold"], direct["expected"]))
            self.assertIn("[" + direct["interval"][0] + " m, " + direct["interval"][1] + " m)",
                          direct["prompt"])

    def test_exact_parser(self):
        self.assertEqual(e01.parse_answer("A"), "A")
        self.assertEqual(e01.parse_answer("B"), "B")
        self.assertIsNone(e01.parse_answer("A because"))
        self.assertIsNone(e01.parse_answer("B = Yes"))


if __name__ == "__main__":
    unittest.main()
