#!/usr/bin/env python3
"""Plot the E20-E22 selective-sensitivity result as one causal story."""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
CONTROLLED = ROOT / "results/cpc18_form_evidence_seed157"
EXTERNAL = ROOT / "results/cpc18_form_evidence_llama_seed179"
STATE = ROOT / "results/cpc18_selective_state_seed173"
OUTPUT = ROOT / "results/selective_sensitivity_story"


def read(path):
    return json.loads(path.read_text())


def interval_error(item):
    mean = item["mean"]
    low, high = item["base_decision_bootstrap_ci95"]
    return [[mean - low], [high - mean]]


def main():
    behavior = read(CONTROLLED / "behavior_summary.json")
    control = read(CONTROLLED / "control_summary.json")
    external_behavior = read(EXTERNAL / "behavior_summary.json")
    external_control = read(EXTERNAL / "control_summary.json")
    state = read(STATE / "summary.json")

    axes = [
        ("OLMo siblings", behavior, "olmo_instruct_sft", "olmo_think_sft", "#277da1"),
        ("Qwen same weights", behavior, "qwen_non_thinking", "qwen_thinking", "#43aa8b"),
        ("Llama ecosystem", external_behavior, "llama_instruct", "deepseek_r1", "#f3722c"),
    ]
    fig, panels = plt.subplots(1, 3, figsize=(13.2, 3.8), constrained_layout=True)

    ax = panels[0]
    for label, summary, standard, reasoning, color in axes:
        start = (
            summary[standard]["form_sensitivity"]["mean"],
            summary[standard]["evidence_sensitivity"]["mean"],
        )
        end = (
            summary[reasoning]["form_sensitivity"]["mean"],
            summary[reasoning]["evidence_sensitivity"]["mean"],
        )
        ax.annotate("", xy=end, xytext=start, arrowprops={"arrowstyle": "->", "lw": 2.2, "color": color})
        ax.scatter(*start, s=42, facecolor="white", edgecolor=color, linewidth=1.8, zorder=3)
        ax.scatter(*end, s=52, color=color, edgecolor="white", linewidth=.7, zorder=3, label=label)
    ax.set(xlabel="Sensitivity to form", ylabel="Sensitivity to evidence", xlim=(-.03, .43), ylim=(-.04, 1.04))
    ax.set_title("A  Reasoning reallocates sensitivity", loc="left", fontweight="bold")
    ax.legend(frameon=False, fontsize=8, loc="lower left")
    ax.text(.98, .03, "open: standard\nfilled: reasoning", transform=ax.transAxes, ha="right", va="bottom", fontsize=7, color="#555555")

    ax = panels[1]
    pairs = [
        ("OLMo", control["reasoning_minus_standard"]["olmo_sft"], "#277da1"),
        ("Qwen", control["reasoning_minus_standard"]["qwen_mode"], "#43aa8b"),
        ("Llama", external_control["reasoning_minus_standard"]["llama_external"], "#f3722c"),
    ]
    x = np.arange(len(pairs))
    width = .34
    for offset, form in ((-width / 2, "raw"), (width / 2, "summary")):
        values = [item[1]["forms"][form]["delta_control_difference"] for item in pairs]
        means = [item["mean"] for item in values]
        errors = np.array([interval_error(item) for item in values]).squeeze().T
        ax.bar(x + offset, means, width, color=[item[2] for item in pairs], alpha=.95 if form == "raw" else .5, label=form.capitalize())
        ax.errorbar(x + offset, means, yerr=errors, fmt="none", ecolor="#222222", elinewidth=1, capsize=2)
    ax.axhline(0, color="#777777", linewidth=.8)
    ax.set_xticks(x, [item[0] for item in pairs])
    ax.set_ylabel(r"Reasoning $-$ standard change in $\Delta_R-\Delta_P$")
    ax.set_title("B  Evidence-bearing trajectories gain control", loc="left", fontweight="bold")
    ax.legend(frameon=False, fontsize=8)

    ax = panels[2]
    layers = state["layer_profile"]
    colors = {"donor_evidence_effect": "#43aa8b", "donor_form_sensitivity": "#f94144"}
    labels = {"donor_evidence_effect": "Evidence direction", "donor_form_sensitivity": "Form"}
    for key in ("donor_evidence_effect", "donor_form_sensitivity"):
        means = np.array([row[key]["mean"] for row in layers])
        lows = np.array([row[key]["base_decision_bootstrap_ci95"][0] for row in layers])
        highs = np.array([row[key]["base_decision_bootstrap_ci95"][1] for row in layers])
        xs = np.array([row["layer"] for row in layers])
        ax.plot(xs, means, marker="o", color=colors[key], label=labels[key])
        ax.fill_between(xs, lows, highs, color=colors[key], alpha=.16)
    ax.axhline(0, color="#777777", linewidth=.8)
    ax.set(xlabel="Decoder layer", ylabel="Donor-directed choice effect", xticks=[0, 8, 16, 24, 31])
    ax.set_title("C  A selective causal state emerges late", loc="left", fontweight="bold")
    ax.legend(frameon=False, fontsize=8, loc="upper left")

    for ax in panels:
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", color="#dddddd", linewidth=.6, alpha=.7)
        ax.set_axisbelow(True)

    OUTPUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT / "selective_sensitivity_story.pdf", bbox_inches="tight")
    fig.savefig(OUTPUT / "selective_sensitivity_story.png", dpi=220, bbox_inches="tight")


if __name__ == "__main__":
    main()
