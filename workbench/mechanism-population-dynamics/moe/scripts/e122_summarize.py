"""Summarize the prespecified E122 layer measurements; no new slices or tests."""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1] / "results/e122"
rows = [json.loads((ROOT / f"layer{l}.json").read_text()) for l in range(16)]
summary = []
for row in rows:
    causal = row["causal"]["swap9"]
    summary.append({"layer": row["layer"],
                    "routing_split_rho": row["routing_split_spearman"],
                    "output_split_rho": row["function_split_spearman"],
                    "routing_output_partial_rho_crosshalves": [r["partial_spearman"] for r in row["cross_half"]],
                    "route_to_kl": causal["route_distance"]["kl"],
                    "route_to_dnll": causal["route_distance"]["dnll"],
                    "output_l2_to_kl": causal["output_l2"]["kl"],
                    "output_l2_to_dnll": causal["output_l2"]["dnll"]})
out = {"model": "OLMoE-1B-7B-0924", "primary_layer": 9, "control_layer": 2,
       "scope": "one model; expert-pair association and held-POS substitution are distinct estimands",
       "layers": summary, "sum_layer_wall_seconds": sum(r["elapsed_seconds"] for r in rows)}
(ROOT / "summary.json").write_text(json.dumps(out, indent=2))
fig, axes = plt.subplots(1, 2, figsize=(9, 6), sharey=True, constrained_layout=True)
y = np.arange(16)
rf = np.array([r["routing_output_partial_rho_crosshalves"] for r in summary])
axes[0].plot(rf[:, 0], y, "o", color="#28619e", label="R half A / F half B", markersize=4)
axes[0].plot(rf[:, 1], y, "x", color="#77a8c9", label="R half B / F half A", markersize=4)
axes[0].set(xlabel="Partial rank correlation across expert pairs", title="Routing vs. same-input expert output", ylabel="MoE layer (zero based)")
axes[0].legend(fontsize=8, loc="lower right")
val = np.array([r["route_to_dnll"]["partial_spearman"] for r in summary])
ci = np.array([r["route_to_dnll"]["ci_word_bootstrap"] for r in summary])
axes[1].hlines(y, ci[:, 0], ci[:, 1], color="#a6b4ba", linewidth=1.4)
axes[1].plot(val, y, "o", color="#b24f3f", markersize=4)
axes[1].set(xlabel="Partial rank correlation; 95% word bootstrap CI", title="Routing distance vs. held-out NLL change")
axes[1].axvspan(-.2, .2, color="#e8edf0", alpha=.4)
axes[1].axvline(-.2, ls="--", color="#86939c", lw=.7)
axes[1].axvline(.2, ls="--", color="#86939c", lw=.7)
for ax in axes:
    ax.set_yticks(y)
    ax.axvline(0, color="#69747a", lw=.8)
    ax.axhspan(8.6, 9.4, color="#e7d8a8", alpha=.45)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="x", alpha=.15)
axes[0].invert_yaxis()
fig.suptitle("E122: output geometry association does not establish a routing proxy for prediction loss", fontsize=11)
fig.savefig(ROOT / "routing_function_bridge.png", dpi=180)
fig.savefig(ROOT / "routing_function_bridge.pdf")
print(json.dumps({"layers": len(rows), "RF_range": [float(rf.min()), float(rf.max())],
                  "route_NLL_range": [float(val.min()), float(val.max())],
                  "route_NLL_CI_upper_max": float(ci[:, 1].max()),
                  "layer_wall_seconds": out["sum_layer_wall_seconds"]}))
