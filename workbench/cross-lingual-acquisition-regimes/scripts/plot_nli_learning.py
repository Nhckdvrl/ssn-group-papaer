"""Plot all adaptation seeds without selecting checkpoints or outcomes."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
report = json.loads((ROOT / "results/nli_analysis_seeds_17_29_43.json").read_text())
conditions = {"baseline": ("FWB", "#276b46"), "monoweb": ("MWB", "#b03a48"),
              "onlyparallel": ("MWB+P", "#3467a1")}
steps = [0, 64, 256, 1024]
examples = np.array(steps) * 32
fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
for axis, split, title in zip(axes, ["en_test", "de_test"], ["English task learning", "German transfer"]):
    for condition, (label, color) in conditions.items():
        values = np.array([[next(row["accuracy"] for row in report["table"]
                                if row["condition"] == condition and row["seed"] == seed
                                and row["updates"] == step and row["split"] == split)
                            for step in steps] for seed in report["seeds"]]) * 100
        for seed_values in values:
            axis.plot(examples, seed_values, color=color, alpha=.2, linewidth=1)
        axis.plot(examples, values.mean(0), "o-", color=color, label=label, linewidth=2)
    axis.axhline(100/3, color="gray", linestyle=":", linewidth=1)
    axis.set_xticks(examples, ["0", "2,048", "8,192", "32,768"])
    axis.tick_params(axis="x", labelsize=9, labelrotation=30)
    axis.set_xlabel("English training examples")
    axis.set_title(title)
    axis.grid(axis="y", alpha=.2)
    axis.legend(frameon=False)
axes[0].set_ylabel("XNLI accuracy (%)")
fig.suptitle("MONOWEB 34K: fixed recipe, all three adaptation seeds")
fig.tight_layout()
fig.savefig(ROOT / "results/nli_learning_curves.png", dpi=180)
