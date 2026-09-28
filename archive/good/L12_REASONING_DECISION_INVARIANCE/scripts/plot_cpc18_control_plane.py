#!/usr/bin/env python3
"""Plot the E17 prompt-versus-trajectory causal control plane."""

import json

import matplotlib.pyplot as plt

from cpc18_common import CONFIG, ROOT


LABELS = {
    "olmo_instruct_sft": "OLMo Instruct-SFT",
    "olmo_think_sft": "OLMo Think-SFT",
    "qwen_non_thinking": "Qwen non-thinking",
    "qwen_thinking": "Qwen thinking",
    "llama_instruct": "Llama Instruct",
    "deepseek_r1": "DeepSeek-R1-Distill",
}
COLORS = {"olmo_sft": "#0072B2", "qwen_mode": "#009E73", "llama_external": "#D55E00"}


def main():
    result_dir = ROOT / CONFIG["result_dir"]
    summary = json.loads((result_dir / "control_summary.json").read_text())
    fig, axis = plt.subplots(figsize=(7.2, 5.4))
    axis.axhline(0, color="#999999", linewidth=0.8)
    axis.axvline(0, color="#999999", linewidth=0.8)
    for pair in sorted(summary["reasoning_minus_standard"]):
        specs = [spec for spec in CONFIG["regimes"] if spec["pair"] == pair]
        standard = next(spec["name"] for spec in specs if spec["role"] == "standard")
        reasoning = next(spec["name"] for spec in specs if spec["role"] == "reasoning")
        points = []
        for name, marker in [(standard, "o"), (reasoning, "s")]:
            x = summary[name]["delta_p"]
            y = summary[name]["delta_r"]
            xv, yv = x["mean_probability_effect"], y["mean_probability_effect"]
            points.append((xv, yv))
            axis.errorbar(
                xv, yv,
                xerr=[[xv - x["base_decision_bootstrap_ci95"][0]],
                      [x["base_decision_bootstrap_ci95"][1] - xv]],
                yerr=[[yv - y["base_decision_bootstrap_ci95"][0]],
                      [y["base_decision_bootstrap_ci95"][1] - yv]],
                fmt=marker, markersize=7, capsize=2.5,
                color=COLORS[pair], markeredgecolor="white", markeredgewidth=0.7,
            )
            axis.annotate(
                LABELS[name], (xv, yv), xytext=(5, 5),
                textcoords="offset points", fontsize=8,
            )
        axis.annotate(
            "", xy=points[1], xytext=points[0],
            arrowprops={"arrowstyle": "->", "color": COLORS[pair], "linewidth": 1.4},
        )
    axis.set_xlabel(r"Prompt control $\Delta_P$")
    axis.set_ylabel(r"Trajectory control $\Delta_R$")
    axis.set_title("CPC18 description/history causal control")
    axis.spines[["top", "right"]].set_visible(False)
    axis.grid(color="#dddddd", linewidth=0.6, alpha=0.7)
    fig.tight_layout()
    fig.savefig(result_dir / "control_plane.pdf")
    fig.savefig(result_dir / "control_plane.png", dpi=180)


if __name__ == "__main__":
    main()
