#!/usr/bin/env python3
"""Construct and audit the preregistered E10 controlled-decision set."""

import json
import math
import random
from collections import Counter
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "configs/breadth.json").read_text())


def stratum(value, boundaries):
    for name, (lower, upper) in boundaries.items():
        if lower <= value < upper:
            return name
    return None


def candidates():
    probabilities = CONFIG["probabilities_percent"]
    for scale, bounds in CONFIG["payoff_scales"].items():
        amounts = range(bounds["low"], bounds["high"] + 1, bounds["step"])
        for amount_a in amounts:
            for amount_b in amounts:
                if amount_a <= amount_b:
                    continue
                for probability_a in probabilities:
                    for probability_b in probabilities:
                        if probability_a >= probability_b:
                            continue
                        probability_gap = probability_b - probability_a
                        probability_stratum = stratum(
                            probability_gap, CONFIG["probability_gap_strata"]
                        )
                        if probability_stratum is None:
                            continue
                        ev_a = Fraction(amount_a * probability_a, 100)
                        ev_b = Fraction(amount_b * probability_b, 100)
                        if ev_a == ev_b:
                            continue
                        relative_gap = float(abs(ev_a - ev_b) / ((ev_a + ev_b) / 2))
                        ev_stratum = stratum(
                            relative_gap, CONFIG["relative_ev_gap_strata"]
                        )
                        if ev_stratum is None:
                            continue
                        divisor = math.gcd(amount_a, amount_b)
                        yield {
                            "amount_a": amount_a,
                            "prob_a": probability_a / 100,
                            "amount_b": amount_b,
                            "prob_b": probability_b / 100,
                            "ev_a": float(ev_a),
                            "ev_b": float(ev_b),
                            "gain_optimal": "A" if ev_a > ev_b else "B",
                            "loss_optimal": "B" if ev_a > ev_b else "A",
                            "relative_ev_gap": relative_gap,
                            "ev_gap_stratum": ev_stratum,
                            "probability_gap": probability_gap / 100,
                            "probability_gap_stratum": probability_stratum,
                            "payoff_scale": scale,
                            "_affine_signature": (
                                probability_a,
                                probability_b,
                                amount_a // divisor,
                                amount_b // divisor,
                            ),
                        }


def select_units():
    rng = random.Random(CONFIG["seed"])
    pool = list(candidates())
    rng.shuffle(pool)
    chosen = []
    used_signatures = set()
    used_amount_probability_pairs = set()
    strata = [
        (scale, ev_gap, probability_gap)
        for scale in CONFIG["payoff_scales"]
        for ev_gap in CONFIG["relative_ev_gap_strata"]
        for probability_gap in CONFIG["probability_gap_strata"]
    ]
    for cell in strata:
        for winner in ("A", "B"):
            matches = [
                row for row in pool
                if (
                    row["payoff_scale"],
                    row["ev_gap_stratum"],
                    row["probability_gap_stratum"],
                ) == cell
                and row["gain_optimal"] == winner
                and row["_affine_signature"] not in used_signatures
                and (
                    row["amount_a"], row["prob_a"],
                    row["amount_b"], row["prob_b"],
                ) not in used_amount_probability_pairs
            ]
            if not matches:
                raise RuntimeError(f"No eligible candidate for {cell}, winner={winner}")
            row = matches[0]
            used_signatures.add(row["_affine_signature"])
            used_amount_probability_pairs.add((
                row["amount_a"], row["prob_a"], row["amount_b"], row["prob_b"]
            ))
            chosen.append(row)
    rng.shuffle(chosen)
    for index, row in enumerate(chosen, start=1):
        row["id"] = f"c{index:02d}"
        row.pop("_affine_signature")
    return chosen


def audit(rows):
    expected_n = (
        len(CONFIG["payoff_scales"])
        * len(CONFIG["relative_ev_gap_strata"])
        * len(CONFIG["probability_gap_strata"])
        * CONFIG["units_per_cell"]
    )
    ids = [row["id"] for row in rows]
    exact = [
        (row["amount_a"], row["prob_a"], row["amount_b"], row["prob_b"])
        for row in rows
    ]
    signatures = []
    for row in rows:
        divisor = math.gcd(row["amount_a"], row["amount_b"])
        signatures.append((
            round(row["prob_a"] * 100),
            round(row["prob_b"] * 100),
            row["amount_a"] // divisor,
            row["amount_b"] // divisor,
        ))
    checks = {
        "expected_unit_count": len(rows) == expected_n,
        "unique_ids": len(ids) == len(set(ids)),
        "unique_exact_units": len(exact) == len(set(exact)),
        "no_affine_equivalents": len(signatures) == len(set(signatures)),
        "all_probability_payoff_tradeoffs": all(
            row["amount_a"] > row["amount_b"] and row["prob_a"] < row["prob_b"]
            for row in rows
        ),
        "no_ev_ties": all(row["ev_a"] != row["ev_b"] for row in rows),
        "opposite_gain_loss_gold": all(
            row["gain_optimal"] != row["loss_optimal"] for row in rows
        ),
    }
    if not all(checks.values()):
        raise RuntimeError(f"Decision-set audit failed: {checks}")
    return {
        "design": "L12-E10 controlled decision breadth v1",
        "seed": CONFIG["seed"],
        "n_units": len(rows),
        "checks": checks,
        "counts": {
            field: dict(sorted(Counter(row[field] for row in rows).items()))
            for field in [
                "payoff_scale",
                "ev_gap_stratum",
                "probability_gap_stratum",
                "gain_optimal",
            ]
        },
        "relative_ev_gap_range": [
            min(row["relative_ev_gap"] for row in rows),
            max(row["relative_ev_gap"] for row in rows),
        ],
    }


def main():
    rows = select_units()
    report = audit(rows)
    output = ROOT / CONFIG["output"]
    audit_output = ROOT / CONFIG["audit_output"]
    with output.open("w") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
    audit_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
