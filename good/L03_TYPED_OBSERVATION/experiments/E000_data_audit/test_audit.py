"""Synthetic software fixtures only; never count these as research observations."""
import unittest

from audit import classify, extract, inventory


class GoldContractTests(unittest.TestCase):
    def test_zero_and_negative_are_values(self):
        for value in ("0", "0.0", "-42", "12.5"):
            self.assertEqual(classify(value, None), {"status": "VALUE", "value": value})

    def test_provider_combined_status_is_not_split(self):
        self.assertEqual(classify("-888888888", "(X)")["status"],
                         "NOT_APPLICABLE_OR_NOT_AVAILABLE")

    def test_distinct_nonvalue_states(self):
        cases = [("-666666666", "-", "NOT_COMPUTABLE"),
                 ("-999999999", "N", "NOT_DISPLAYABLE_INSUFFICIENT_CASES"),
                 (None, None, "NO_DATA_FOR_GEOGRAPHY")]
        for value, annotation, status in cases:
            self.assertEqual(classify(value, annotation), {"status": status, "value": None})

    def test_interval_is_not_a_scalar(self):
        for value, annotation, status in [("250000", "250,000+", "MEDIAN_LOWER_BOUND"),
                                           ("2500", "2,500-", "MEDIAN_UPPER_BOUND")]:
            gold = classify(value, annotation)
            self.assertEqual(gold["status"], status)
            self.assertIsNone(gold["value"])
            self.assertEqual(gold["bound"], value)

    def test_ambiguous_pairs_never_become_gold(self):
        for value, annotation in [("-888888888", None), ("-666666666", "N"),
                                  ("-222222222", "**"), ("-777777777", None),
                                  ("20", "*"), (None, "N"), ("null", None),
                                  ("NaN", None), ("Infinity", None),
                                  ("250001", "250,000+"), ("20", "")]:
            with self.subTest(value=value, annotation=annotation):
                with self.assertRaises(ValueError):
                    classify(value, annotation)


class ExtractionTests(unittest.TestCase):
    def setUp(self):
        self.source = {"group": "B19013", "dataset": "2023/acs/acs5", "estimates": ["B19013_001E"]}
        self.meta = {"variables": {"B19013_001E": {"label": "Estimate!!Median income", "group": "B19013"},
                                   "B19013_001EA": {"label": "Annotation"}}}
        self.header = ["NAME", "B19013_001E", "B19013_001EA", "state", "county"]

    def test_unknown_retained_with_provenance(self):
        data = [self.header, ["Fixture A", "0", None, "01", "001"],
                ["Fixture B", "-888888888", "unexpected", "01", "003"]]
        valid, rejected = extract(data, self.source, self.meta, "fixture-hash")
        self.assertEqual((len(valid), len(rejected)), (1, 1))
        self.assertEqual(valid[0]["source_sha256"], "fixture-hash")
        self.assertIn("reason", rejected[0])
        self.assertNotIn("gold", rejected[0])

    def test_bad_shape_and_duplicate_units_rejected(self):
        row = ["Fixture", "1", None, "01", "001"]
        for data in [[self.header, row, row], [self.header, row[:-1]],
                     [self.header[:-1], row[:-1]], [], {"error": "access denied"}]:
            with self.assertRaises(ValueError):
                extract(data, self.source, self.meta, "fixture-hash")

    def test_estimate_annotation_pair_required(self):
        self.assertEqual(inventory(self.meta, self.source)["paired_estimate_count"], 1)
        del self.meta["variables"]["B19013_001EA"]
        with self.assertRaises(ValueError):
            inventory(self.meta, self.source)

    def test_semantic_drift_rejected(self):
        self.source["expected_labels"] = {"B19013_001E": "A different meaning"}
        with self.assertRaises(ValueError):
            inventory(self.meta, self.source)


if __name__ == "__main__":
    unittest.main()
