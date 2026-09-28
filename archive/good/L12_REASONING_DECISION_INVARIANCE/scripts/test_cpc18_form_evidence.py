#!/usr/bin/env python3
"""Construct-validity tests for E20 prompts and selective-sensitivity metrics."""

import pandas as pd

from cpc18_form_evidence_common import load_problems, make_prompt
from summarize_cpc18_form_evidence import unit_metrics
from summarize_cpc18_form_evidence_control import effects


def check_prompt(problem, evidence):
    raw_ab = make_prompt(problem, evidence, "raw", "ab")
    summary_ab = make_prompt(problem, evidence, "summary", "ab")
    summary_ba = make_prompt(problem, evidence, "summary", "ba")
    assert raw_ab.count("\n") >= 22
    for payoff, count in evidence["option_a_frequencies"]:
        phrase = f"{int(payoff) if float(payoff).is_integer() else payoff} points occurred {count}/20 times"
        assert phrase in summary_ab
        assert phrase in summary_ba
    assert "generating probabilities are not shown" in raw_ab
    assert "generating probabilities are not shown" in summary_ab


def test_metrics():
    rows = []
    # Both forms always follow the evidence direction: zero form sensitivity,
    # unit evidence sensitivity, and therefore unit selective sensitivity.
    for evidence in ("A", "B"):
        for form in ("raw", "summary"):
            for order in ("ab", "ba"):
                for sample in range(4):
                    rows.append({
                        "problem": "test", "source_split": "test",
                        "evidence_choice": evidence, "form": form,
                        "order": order, "sample_index": sample,
                        "underlying_choice": evidence, "valid": True,
                    })
    metrics = unit_metrics(pd.DataFrame(rows)).iloc[0]
    assert metrics.form_sensitivity == 0
    assert metrics.evidence_sensitivity == 1
    assert metrics.selective_sensitivity == 1
    assert metrics.selective_sensitivity_lower == 1
    assert metrics.selective_sensitivity_upper == 1

    control_rows = []
    for prompt in ("A", "B"):
        for trajectory in ("A", "B"):
            control_rows.append({
                "problem": "test", "form": "raw", "order": "ab",
                "a_sample_index": 0, "b_sample_index": 0,
                "prompt_evidence": prompt, "trajectory_evidence": trajectory,
                "p_a_choice": 1.0 if trajectory == "A" else 0.0,
            })
    control = effects(pd.DataFrame(control_rows)).iloc[0]
    assert control.delta_p == 0
    assert control.delta_r == 1
    assert control.delta_control == 1


def main():
    problem = load_problems(1)[0]
    for evidence in problem["evidence"]:
        check_prompt(problem, evidence)
    test_metrics()
    print("E20 prompt equivalence and metric controls passed")


if __name__ == "__main__":
    main()
