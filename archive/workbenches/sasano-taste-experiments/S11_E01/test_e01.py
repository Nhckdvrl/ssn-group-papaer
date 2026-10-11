import collections
import unittest
from decimal import Decimal

import e01


class DecimalInstrumentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = e01.make_rows()

    def test_reference_example_is_derived(self):
        self.assertEqual(e01.parse_expression("2.0"), (Decimal("2.0"), Decimal("0.1")))
        self.assertEqual(e01.parse_expression("2.00"), (Decimal("2.00"), Decimal("0.01")))
        self.assertEqual(e01.interval("2.0"), (Decimal("1.95"), Decimal("2.05")))
        self.assertEqual(e01.interval("2.00"), (Decimal("1.995"), Decimal("2.005")))
        self.assertEqual(e01.interval("2.00 × 10^0"), e01.interval("2.00"))
        self.assertFalse(e01.certifies("2.0", "1.99", "greater"))
        self.assertTrue(e01.certifies("2.00", "1.99", "greater"))

    def test_all_items_and_label_balance(self):
        e01.check(self.rows)

    def test_derived_labels_and_open_gap(self):
        for x in self.rows:
            if x["cell"] == "measurement":
                self.assertEqual(x["expected"], "A" if e01.certifies(x["displayed"], x["threshold"], x["direction"]) else "B")
                self.assertNotIn(Decimal(x["threshold"]), e01.interval(x["displayed"]))
            elif x["cell"] == "value":
                same = e01.parse_expression(x["coarse"])[0] == e01.parse_expression(x["fine"])[0]
                self.assertEqual(x["expected"], "A" if same == (x["question_polarity"] == "same") else "B")
            else:
                same = e01.interval(x["fine"]) == e01.interval(x["notation"])
                self.assertEqual(x["expected"], "A" if same == (x["question_polarity"] == "same") else "B")

    def test_explicit_natural_pairs_only_change_preamble(self):
        groups = collections.defaultdict(dict)
        for x in self.rows:
            if x["layer"] in ("explicit", "natural"):
                groups[(x["base_id"], x["cell"], x["variant"])][x["layer"]] = x
        for group in groups.values():
            explicit, natural = group["explicit"], group["natural"]
            self.assertEqual(explicit["expected"], natural["expected"])
            self.assertEqual(explicit["prompt"].replace(e01.EXPLICIT, "ROLE"),
                             natural["prompt"].replace(e01.NATURAL, "ROLE"))

    def test_parser_rejects_explanations_and_conflicting_glosses(self):
        for raw, expected in ((" A\n", "A"), ("B = No.", "B"), ("A = Yes", "A"),
                              ("A = No", None), ("B because", None), ("yes", None), ("", None)):
            self.assertEqual(e01.parse_answer(raw), expected)


if __name__ == "__main__":
    unittest.main()
