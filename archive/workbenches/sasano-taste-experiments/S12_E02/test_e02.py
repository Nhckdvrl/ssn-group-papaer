import collections
import unittest

import e02


class HeldOutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = e02.make()

    def test_full_invariants(self):
        e02.check(self.rows)

    def test_original_and_clean_share_world_and_role(self):
        by_key = collections.defaultdict(dict)
        for x in self.rows:
            by_key[(x["base_id"], x["role"], x["readout"])][x["wording"]] = x
        for pair in by_key.values():
            a, b = pair["original"], pair["scope_clean"]
            for key in ("relation", "world_a", "world_b", "frame", "role", "polarity", "expected"):
                self.assertEqual(a[key], b[key])
            self.assertNotEqual(a["prompt"], b["prompt"])

    def test_expected_labels_and_parser(self):
        for x in self.rows:
            self.assertEqual(x["expected"], "A" if ((x["role"] == "definition") == (x["polarity"] == 0)) else "B")
        self.assertEqual(e02.e01.parse_answer("A = Yes"), "A")
        self.assertIsNone(e02.e01.parse_answer("A = No"))


if __name__ == "__main__":
    unittest.main()
