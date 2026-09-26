import collections
import unittest

import e02

e01 = e02.e01


class HeldOutReplicationTests(unittest.TestCase):
    def test_items_are_valid_and_disjoint(self):
        items = e02.rows()
        e02.check(items)
        self.assertEqual(items, e01.read_jsonl(e02.HERE / "items.jsonl"))

    def test_pairing_and_exact_parser(self):
        items = e02.rows()
        pairs = collections.defaultdict(dict)
        for item in items:
            pairs[item["base_id"]][item["variant"]] = item
            self.assertEqual(item["expected"], "A" if e01.certifies(
                item["displayed"], item["threshold"], item["direction"]) else "B")
        self.assertEqual(len(pairs), 60)
        self.assertTrue(all(x["coarse"]["expected"] == "B" and x["fine"]["expected"] == "A"
                            for x in pairs.values()))
        self.assertIsNone(e01.parse_answer("A because"))


if __name__ == "__main__":
    unittest.main()
