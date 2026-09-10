#!/usr/bin/env python3
"""Synthetic direction check for the E21 state-selectivity estimand."""

import pandas as pd

from summarize_cpc18_selective_state import compute_unit_metrics


def main():
    rows = []
    for target_form in ("raw", "summary"):
        for target_evidence in ("A", "B"):
            for donor_form in ("raw", "summary"):
                for donor_evidence in ("A", "B"):
                    rows.append({
                        "problem": "test",
                        "layer": 31,
                        "target_form": target_form,
                        "target_evidence": target_evidence,
                        "donor_form": donor_form,
                        "donor_evidence": donor_evidence,
                        "patched_p_a": 1.0 if donor_evidence == "A" else 0.0,
                    })
    result = compute_unit_metrics(pd.DataFrame(rows)).iloc[0]
    assert result.donor_evidence_effect == 1.0
    assert result.donor_form_sensitivity == 0.0
    assert result.state_selectivity == 1.0
    print("E21 state-selectivity direction check passed")


if __name__ == "__main__":
    main()
