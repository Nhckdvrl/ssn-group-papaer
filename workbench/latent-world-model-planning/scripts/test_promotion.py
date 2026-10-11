"""Instrument controls, not scientific experiment results."""
import unittest
import numpy as np
from promotion import Calibration, promote


class PromotionControl(unittest.TestCase):
    def test_certified_elites_across_penalty_scales_and_ties(self):
        rng = np.random.default_rng(23)
        for scale in (0, 0.01, 1, 100):
            for _ in range(30):
                cheap = rng.integers(0, 50, 300).astype(float)
                refined = cheap + scale * rng.exponential(size=300)
                bought = []
                def query(ids):
                    bought.extend(ids.tolist())
                    return refined[ids]
                out = promote(cheap, query, k=30, mode="LOWER-BOUND")
                np.testing.assert_array_equal(out["elite"], np.argsort(refined, kind="stable")[:30])
                self.assertEqual(len(set(bought)), len(bought))
                self.assertGreaterEqual(len(bought), 30)

    def test_fixed_budget_and_no_unpurchased_outcomes(self):
        rng = np.random.default_rng(77)
        cheap = rng.random(300)
        refined = cheap + rng.random(300)
        calibration = Calibration.fit([cheap], [refined])
        for mode in ("RANDOM-M", "TOP-M", "TOP-M-SCREEN", "ELITE-BAND"):
            seen = []
            def query(ids):
                seen.extend(ids.tolist())
                return refined[ids]
            out = promote(cheap, query, k=30, mode=mode, budget=60, calibration=calibration)
            self.assertEqual(len(seen), 60)
            # Alter every outcome that this selector did not purchase.
            mutated = refined.copy()
            mutated[np.setdiff1d(np.arange(300), out["queried"])] = -1000
            again = promote(cheap, lambda ids: mutated[ids], k=30, mode=mode, budget=60, calibration=calibration)
            np.testing.assert_array_equal(out["elite"], again["elite"])
            np.testing.assert_array_equal(out["queried"], again["queried"])

    def test_invalid_lower_bound_cannot_claim_certificate(self):
        with self.assertRaises(ValueError):
            promote(np.arange(50.), lambda ids: -np.ones(len(ids)), k=5, mode="LOWER-BOUND")


if __name__ == "__main__":
    unittest.main()
