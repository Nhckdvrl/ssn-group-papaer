import collections
import unittest

import e03


class E03Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.main, cls.controls = e03.generate()

    def test_complete_invariants(self):
        e03.check(self.main, self.controls)

    def test_triple_pairing_and_exact_relation(self):
        triples = collections.defaultdict(dict)
        for x in self.main:
            triples[x["pair_id"]][x["role"]] = x
        for triple in triples.values():
            self.assertEqual(set(triple), set(e03.ROLES))
            self.assertEqual(len({x["relation"] for x in triple.values()}), 1)
            self.assertEqual(len({x["world_a"] for x in triple.values()}), 1)
            self.assertEqual(len({x["world_b"] for x in triple.values()}), 1)
            self.assertEqual(len({x["expected"] for x in triple.values()}), 2)
            for x in triple.values():
                self.assertEqual(x["prompt"].count('"'+x["relation"]+'"'), 1)

    def test_new_vocabulary_and_labels(self):
        self.assertFalse(set(e03.NONCES) & set(e03.e01.NONCES))
        self.assertFalse(set(e03.COLORS) & set(e03.e01.COLORS))
        self.assertFalse(set(e03.SHAPES) & set(e03.e01.SHAPES))
        self.assertFalse(set(e03.NAMES) & set(e03.e01.NAMES))
        for x in self.main:
            self.assertEqual(x["expected"], "A" if ((x["role"] == "definition") == (x["polarity"] == 0)) else "B")

    def test_parser(self):
        for raw, parsed in (("A", "A"), (" B\n", "B"), ("A = Yes", "A"),
                            ("B = No.", "B"), ("A = No", None), ("B because", None)):
            self.assertEqual(e03.e01.parse_answer(raw), parsed)


if __name__ == "__main__":
    unittest.main()
