"""Scientific figure: source exclusion, learned readout, and rule sensitivity."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
base = ROOT / "results/e90"
c = json.loads((base / "qwen3_confirmation/analysis.json").read_text())
s = json.loads((base / "qwen3_single_adapter_confirmation/analysis.json").read_text())
h = json.loads((base / "qwen3_heterogeneity/rule_sensitivity.json").read_text())
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.4))
vals = [c["metrics"][k]["accuracy"] for k in
        ["conflict_native", "conflict_late", "conflict_both", "conflict_adapter"]]
vals += [s["metrics"][k]["accuracy"] for k in ["native", "adapter"]]
x = np.arange(len(vals), dtype=float)
x[4:] += .5
means = np.array([v["mean"] * 100 for v in vals])
limits = np.array([v["ci95"] for v in vals]).T * 100
axes[0].bar(x, means, width=.72,
            color=["#8e99a4", "#4c82ae", "#5c9a80", "#d58450", "#8e99a4", "#d58450"])
axes[0].errorbar(x, means, yerr=[means-limits[0], limits[1]-means],
                 fmt="none", capsize=3, ecolor="#333333", linewidth=1)
for xi, m in zip(x, means):
    axes[0].text(xi, m+6, f"{m:.1f}", ha="center", fontsize=9)
axes[0].set_xticks(x, ["Native", "Query\nisolated", "Both\nisolated", "Query\nmodule", "Native", "Query\nmodule"])
axes[0].axvline(3.8, color="#bbbbbb", linestyle=":")
axes[0].set_ylim(0, 105)
axes[0].set_ylabel("Accuracy (%)")
axes[0].set_title("A  Source exclusion does not reproduce learned readout\n48 new contexts; same frozen query module", loc="left", fontsize=10)
axes[0].text(.28, -.23, "Mixed sources", transform=axes[0].transAxes, ha="center")
axes[0].text(.85, -.23, "Single source", transform=axes[0].transAxes, ha="center")
keys = ["native", "late", "adapter"]
for offset, readout, label, color in [(-.18, "signed_rule_effect", "Mean direction", "#4c82ae"),
                                      (.18, "absolute_rule_effect", "Mean magnitude", "#d58450")]:
    v = [h["conditions"][k][readout] for k in keys]
    m = np.array([r["mean"] for r in v])
    ci = np.array([r["ci95"] for r in v]).T
    axes[1].bar(np.arange(3)+offset, m, width=.34, color=color, label=label)
    axes[1].errorbar(np.arange(3)+offset, m, yerr=[m-ci[0], ci[1]-m],
                     fmt="none", ecolor="#333333", capsize=3, linewidth=1)
axes[1].axhline(0, color="#333333", linewidth=.8)
axes[1].set_ylim(-.7, 1.45)
axes[1].set_xticks(np.arange(3), ["Native", "Query isolated\n(target-source only)", "Query module"])
axes[1].set_ylabel("Foreign-rule effect on target-rule contrast (nats)")
axes[1].set_title("B  Cancellation is different from independence\n32 further contexts; frozen sensitivity readout", loc="left", fontsize=10)
axes[1].legend(frameon=False, loc="upper right")
fig.subplots_adjust(left=.065, right=.99, top=.83, bottom=.25, wspace=.32)
dest = ROOT / "results/figs"
dest.mkdir(parents=True, exist_ok=True)
fig.savefig(dest / "e90_source_exclusion_and_rule_sensitivity.png", dpi=180)
fig.savefig(dest / "e90_source_exclusion_and_rule_sensitivity.pdf")
