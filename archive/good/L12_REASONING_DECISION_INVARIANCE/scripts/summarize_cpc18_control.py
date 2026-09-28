#!/usr/bin/env python3
"""Summarize CPC18 causal control and fit pair-level mixed-effects checks."""

import json

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from cpc18_common import CONFIG, ROOT


def bootstrap(values, seed):
    values = np.asarray(values, dtype=float)
    rng = np.random.default_rng(seed)
    indexes = rng.integers(0, len(values), (CONFIG["bootstrap_samples"], len(values)))
    draws = values[indexes].mean(axis=1)
    return [float(np.quantile(draws, 0.025)), float(np.quantile(draws, 0.975))]


def effects(frame):
    keys = ["problem", "history_id", "order", "sample_index"]
    cells = frame.pivot_table(
        index=keys,
        columns=["prompt_presentation", "trajectory_presentation"],
        values="p_ev_choice",
    ).dropna()
    delta_r = (
        (cells[("explicit", "explicit")] - cells[("explicit", "history")])
        + (cells[("history", "explicit")] - cells[("history", "history")])
    ) / 2
    delta_p = (
        (cells[("explicit", "explicit")] - cells[("history", "explicit")])
        + (cells[("explicit", "history")] - cells[("history", "history")])
    ) / 2
    result = pd.DataFrame(index=cells.index)
    result["delta_r"] = delta_r.to_numpy()
    result["delta_p"] = delta_p.to_numpy()
    result["delta_control"] = (delta_r - delta_p).to_numpy()
    return result.reset_index()


def metric_summary(values, seed):
    return {
        "mean_probability_effect": float(values.mean()),
        "base_decision_bootstrap_ci95": bootstrap(values, seed),
        "positive_base_decision_fraction": float((values > 0).mean()),
    }


def mixed_effects(pair_frame):
    data = pair_frame.copy()
    data["prompt_explicit"] = (
        data.prompt_presentation == "explicit"
    ).astype(float)
    data["trajectory_explicit"] = (
        data.trajectory_presentation == "explicit"
    ).astype(float)
    data["reasoning"] = (data.role == "reasoning").astype(float)
    data["order_ba"] = (data.order == "ba").astype(float)
    formula = (
        "p_ev_choice ~ prompt_explicit * trajectory_explicit * reasoning "
        "+ order_ba"
    )
    try:
        fit = smf.mixedlm(
            formula,
            data,
            groups=data["problem"],
            re_formula="~prompt_explicit+trajectory_explicit",
        ).fit(reml=False, method="lbfgs", maxiter=300, disp=False)
        names = [
            "prompt_explicit:reasoning",
            "trajectory_explicit:reasoning",
        ]
        return {
            "converged": bool(fit.converged),
            "n_observations": int(fit.nobs),
            "n_base_decisions": int(data.problem.nunique()),
            "formula": formula,
            "random_effects": "base-decision intercept + prompt + trajectory slopes",
            "coefficients": {
                name: {
                    "estimate": float(fit.params[name]),
                    "standard_error": float(fit.bse[name]),
                    "p_value": float(fit.pvalues[name]),
                }
                for name in names
            },
            "control_reorganization_interaction": {
                "estimate": float(fit.params[names[1]] - fit.params[names[0]]),
                "interpretation": "reasoning change in Delta_R minus reasoning change in Delta_P",
            },
        }
    except Exception as error:
        return {"converged": False, "error": repr(error), "formula": formula}


def main():
    out = ROOT / CONFIG["result_dir"]
    frames = {}
    units = {}
    summary = {"design": "L12-E17 CPC18 prompt-trajectory interventional decomposition"}
    for offset, spec in enumerate(CONFIG["regimes"]):
        name = spec["name"]
        frames[name] = pd.read_json(
            out / "raw" / "control" / f"{name}.jsonl", lines=True
        )
        units[name] = effects(frames[name])
        base = units[name].groupby("problem")[[
            "delta_p", "delta_r", "delta_control"
        ]].mean()
        summary[name] = {
            "pair": spec["pair"],
            "role": spec["role"],
            "n_trace_units": int(len(units[name])),
            "n_base_decisions": int(len(base)),
        }
        for metric_index, metric in enumerate(["delta_p", "delta_r", "delta_control"]):
            summary[name][metric] = metric_summary(
                base[metric], CONFIG["seed"] + offset * 10 + metric_index
            )

    summary["reasoning_minus_standard"] = {}
    unit_rows = []
    for pair_index, pair in enumerate(sorted({s["pair"] for s in CONFIG["regimes"]})):
        members = [s for s in CONFIG["regimes"] if s["pair"] == pair]
        reasoning = next(s for s in members if s["role"] == "reasoning")["name"]
        standard = next(s for s in members if s["role"] == "standard")["name"]
        reason_base = units[reasoning].groupby("problem")[[
            "delta_p", "delta_r", "delta_control"
        ]].mean()
        standard_base = units[standard].groupby("problem")[[
            "delta_p", "delta_r", "delta_control"
        ]].mean()
        joined = reason_base.join(
            standard_base, lsuffix="_reasoning", rsuffix="_standard"
        )
        pair_summary = {
            "reasoning_regime": reasoning,
            "standard_regime": standard,
            "n_paired_base_decisions": int(len(joined)),
        }
        for metric_index, metric in enumerate(["delta_p", "delta_r", "delta_control"]):
            values = joined[f"{metric}_reasoning"] - joined[f"{metric}_standard"]
            pair_summary[f"{metric}_difference"] = metric_summary(
                values, CONFIG["seed"] + 100 + pair_index * 10 + metric_index
            )
        pair_frame = pd.concat([frames[reasoning], frames[standard]], ignore_index=True)
        pair_summary["mixed_effects_confirmation"] = mixed_effects(pair_frame)
        summary["reasoning_minus_standard"][pair] = pair_summary
        for row in joined.reset_index().to_dict(orient="records"):
            unit_rows.append({"pair": pair, **row})

    with (out / "control_unit_metrics.jsonl").open("w") as handle:
        for row in unit_rows:
            handle.write(json.dumps(row) + "\n")
    (out / "control_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
