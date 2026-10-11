#!/usr/bin/env python3
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/pilot_seed29"
CONFIG = json.loads((ROOT / "configs/pilot.json").read_text())
RNG = np.random.default_rng(29)
MIN_VALID_RATE = 0.8


def ev_consistent_rate(frame):
    expected = {
        p["id"]: {
            "A": p["loss_a"] * p["prob_a"],
            "B": p["loss_b"] * p["prob_b"],
        }
        for p in CONFIG["prospects"]
    }
    valid = frame.dropna(subset=["underlying_choice"])
    correct = []
    for row in valid.itertuples():
        values = expected[row.prospect]
        target = max(values, key=values.get) if row.frame == "gain" else min(values, key=values.get)
        correct.append(row.underlying_choice == target)
    return float(np.mean(correct)) if correct else float("nan")


def metrics(frame):
    valid = frame.dropna(subset=["underlying_choice"])
    rates = valid.assign(a=(valid.underlying_choice == "A").astype(float)).groupby(["prospect", "frame", "order"]).a.mean()
    frame_scores, order_scores = [], []
    for prospect in sorted(frame.prospect.unique()):
        frame_scores.append(np.mean([
            1 - abs(
                rates.get((prospect, "gain", order), np.nan)
                - (1 - rates.get((prospect, "loss", order), np.nan))
            )
            for order in ["ab", "ba"]
        ]))
        for framing in ["gain", "loss"]:
            order_scores.append(1 - abs(rates.get((prospect, framing, "ab"), np.nan) - rates.get((prospect, framing, "ba"), np.nan)))
    return float(np.nanmean(frame_scores)), float(np.nanmean(order_scores))


def bootstrap_components(frame, rng, draws=5000):
    prospects = sorted(frame.prospect.unique())
    rates = np.full((draws, len(prospects), 2, 2), np.nan)
    for pi, prospect in enumerate(prospects):
        for fi, framing in enumerate(["gain", "loss"]):
            for oi, order in enumerate(["ab", "ba"]):
                cell = frame[(frame.prospect == prospect) & (frame.frame == framing) & (frame.order == order)]
                choices = cell.underlying_choice.dropna()
                n = len(choices)
                if n:
                    p = float((choices == "A").mean())
                    rates[:, pi, fi, oi] = rng.binomial(n, p, draws) / n
    frame_scores = (
        1 - np.abs(rates[:, :, 0, :] - (1 - rates[:, :, 1, :]))
    ).mean(axis=-1)
    order_scores = (1 - np.abs(rates[:, :, :, 0] - rates[:, :, :, 1])).mean(axis=-1)
    return prospects, frame_scores, order_scores


def bootstrap(frame, draws=5000):
    rng = np.random.default_rng(29)
    prospects, frame_scores, _ = bootstrap_components(frame, rng, draws)
    sampled = rng.integers(0, len(prospects), size=(draws, len(prospects)))
    values = np.take_along_axis(frame_scores, sampled, axis=1).mean(axis=1)
    return [float(np.nanquantile(values, 0.025)), float(np.nanquantile(values, 0.975))]


def bootstrap_difference(left, right, draws=5000):
    rng = np.random.default_rng(2901)
    prospects_left, frame_left, order_left = bootstrap_components(left, rng, draws)
    prospects_right, frame_right, order_right = bootstrap_components(right, rng, draws)
    if prospects_left != prospects_right:
        raise ValueError("branch contrast requires the same prospect set")
    sampled = rng.integers(0, len(prospects_left), size=(draws, len(prospects_left)))
    frame_diff = (
        np.take_along_axis(frame_left, sampled, axis=1).mean(axis=1)
        - np.take_along_axis(frame_right, sampled, axis=1).mean(axis=1)
    )
    order_diff = (
        np.take_along_axis(order_left, sampled, axis=1).mean(axis=1)
        - np.take_along_axis(order_right, sampled, axis=1).mean(axis=1)
    )
    return {
        "frame_consistency_ci95": [float(np.nanquantile(frame_diff, 0.025)), float(np.nanquantile(frame_diff, 0.975))],
        "order_consistency_ci95": [float(np.nanquantile(order_diff, 0.025)), float(np.nanquantile(order_diff, 0.975))],
    }


def main():
    summaries = {}
    canonical = [OUT / branch / "raw.jsonl" for branch in ["base", "instruct_sft", "think_sft", "think_sft_no_think"]]
    for path in [path for path in canonical if path.exists() and path.stat().st_size > 0]:
        frame = pd.read_json(path, lines=True)
        if "underlying_choice" not in frame:
            continue
        branch = path.parent.name
        frame_consistency, order_consistency = metrics(frame)
        generated_behavior_compatible = bool(frame.protocol.iloc[0] != "common_raw")
        summaries[branch] = {
            "n": int(len(frame)), "valid_n": int(frame.underlying_choice.notna().sum()),
            "invalid_rate": float(frame.underlying_choice.isna().mean()),
            "behavior_identifiable": bool(
                generated_behavior_compatible and frame.underlying_choice.notna().mean() >= MIN_VALID_RATE
            ),
            "frame_consistency": frame_consistency, "frame_consistency_ci95": bootstrap(frame),
            "order_consistency": order_consistency,
            "ev_consistent_choice_rate": ev_consistent_rate(frame),
            "shown_a_rate_among_valid": float((frame.dropna(subset=["shown_choice"]).shown_choice == "A").mean()),
            "mean_forced_p_shown_a": float(frame.forced_p_shown_a.mean()),
            "raw": str(path),
        }
    if {"instruct_sft", "think_sft"}.issubset(summaries):
        instruct_frame = pd.read_json(OUT / "instruct_sft/raw.jsonl", lines=True)
        think_frame = pd.read_json(OUT / "think_sft/raw.jsonl", lines=True)
        summaries["contrasts"] = {
            "think_minus_instruct": summaries["think_sft"]["frame_consistency"] - summaries["instruct_sft"]["frame_consistency"],
            "think_minus_instruct_order_consistency": summaries["think_sft"]["order_consistency"] - summaries["instruct_sft"]["order_consistency"],
            **bootstrap_difference(think_frame, instruct_frame),
            "shared_base_generated_behavior_identifiable": bool(
                "base" in summaries and all(
                summaries[name]["behavior_identifiable"] for name in ["base", "instruct_sft", "think_sft"]
                )
            ),
        }
        if summaries["contrasts"]["shared_base_generated_behavior_identifiable"]:
            summaries["contrasts"]["difference_in_change"] = (
                summaries["think_sft"]["frame_consistency"] - summaries["base"]["frame_consistency"]
            ) - (summaries["instruct_sft"]["frame_consistency"] - summaries["base"]["frame_consistency"])
    if "think_sft" in summaries and "think_sft_no_think" in summaries:
        summaries["deliberation_intervention"] = {
            "normal_minus_no_think_frame_consistency": summaries["think_sft"]["frame_consistency"] - summaries["think_sft_no_think"]["frame_consistency"],
            "normal_minus_no_think_order_consistency": summaries["think_sft"]["order_consistency"] - summaries["think_sft_no_think"]["order_consistency"],
            "normal_minus_no_think_ev_consistent_rate": summaries["think_sft"]["ev_consistent_choice_rate"] - summaries["think_sft_no_think"]["ev_consistent_choice_rate"],
        }
    (OUT / "summary.json").write_text(json.dumps(summaries, indent=2) + "\n")
    print(json.dumps(summaries, indent=2))


if __name__ == "__main__":
    main()
