"""Export E146 geometry/prediction comparisons; all random partitions shown."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

WB = Path(__file__).resolve().parents[1]


def main():
    d = json.loads((WB / "results/e146/summary.json").read_text())
    plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False, "pdf.fonttype": 42})
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.9), dpi=150)
    labels = ["Train-selected", "Random 0", "Random 1", "Random 2"]
    colors = ["#2166AC", "#777777", "#777777", "#777777"]
    for x, (name, row) in enumerate(d["partitions"].items()):
        axes[0].plot(x-.15, row["cal_cut"], marker="x", color=colors[x], label="Train cut" if x == 0 else None)
        axes[0].plot(x, row["held_cut"], marker="s", markerfacecolor="white", color=colors[x], label="Held cut" if x == 0 else None)
        for ax, key, offset in ((axes[0], "delta_sum64_teacher_sse", .15), (axes[1], "delta_mu_to_variant_kl", 0), (axes[2], "delta_nll", 0)):
            r = row[key]
            lo, hi = r["crossed_file_source_ci95"]
            ax.vlines(x+offset, lo, hi, color=colors[x])
            ax.plot(x+offset, r["point"], marker="o", color=colors[x], label="Observed risk" if x == 0 and offset else None)
    for ax in axes:
        ax.axhline(0, color="#999999", linewidth=.7)
        ax.set_xticks(range(4), labels, rotation=18)
        ax.grid(axis="y", alpha=.15)
        ax.set_xlim(-.5, 3.5)
    axes[0].set_title("A  Covariance cuts and observed squared risk")
    axes[0].set_ylabel("Risk increase / position (layer units)")
    axes[0].legend(frameon=False, fontsize=7)
    axes[1].set_title("B  Actual KL from the common reference")
    axes[1].set_ylabel("Grouped minus intact KL (nats / token)")
    axes[2].set_title("C  Actual label NLL")
    axes[2].set_ylabel("Grouped minus intact NLL (nats / token)")
    fig.tight_layout(rect=(0, .12, 1, 1), w_pad=2)
    fig.text(.5, .015, "One train-selected partition and all three fixed random partitions; 8 groups of 8 experts.\n"
             "Four source-map units, each with three cyclic shifts. Crossed input-file/source intervals, conditional on these three students.",
             ha="center", fontsize=8, color="#666666")
    out = WB / "results/e146/figures"
    out.mkdir(parents=True, exist_ok=True)
    for suffix in ("png", "pdf"):
        fig.savefig(out / ("grouped_recombination."+suffix), bbox_inches="tight")
    print(str(out / "grouped_recombination.png"))


if __name__ == "__main__":
    main()
