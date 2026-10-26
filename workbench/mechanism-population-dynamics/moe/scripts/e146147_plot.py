"""Report the preregistered intact-baseline outcomes and show the strong control."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import e146_grouped as g

c = g.c


def main():
    directory = c.WB / "results/e147"
    m = c.read(directory / "manifest.json")
    old = c.read(c.WB / "results/e144/manifest.json")
    chunks, old_chunks = [], []
    for a, b in zip(m["raw_batches"], old["raw_batches"]):
        if c.sha(a["path"]) != a["sha256"] or c.sha(b["path"]) != b["sha256"]:
            raise ValueError("Reporting raw SHA differs")
        with np.load(a["path"], allow_pickle=False) as f:
            chunks.append({k: f[k].copy() for k in ("metrics", "layer")})
        with np.load(b["path"], allow_pickle=False) as f:
            ids = [f["names"].tolist().index(f"F{s}") for s in range(3)]
            old_chunks.append({k: f[k][ids].astype(float).mean(0).mean(1) for k in ("metrics", "layer")})
    rows = c.read(c.WB / "results/e144/selected.json")["rows"]
    absolute = {"scope": "Reporting reduction of predeclared E147 intact-baseline outcomes, four matched source units.",
                "cal_cut": m["cal_gamma_cut"], "held_cut": m["held_gamma_cut"]}
    for container, j, key in (("metrics", 0, "delta_nll"), ("metrics", 1, "delta_mu_to_variant_kl"), ("layer", 1, "delta_sum64_teacher_sse")):
        values = np.concatenate([a[container] for a in chunks], axis=1).astype(float).mean(2)[..., j].reshape(4, 3, 64).mean(1)
        baseline = np.concatenate([a[container] for a in old_chunks])[:, j]
        absolute[key] = g.mc_stats(values-baseline[None, :], rows)
    c.write(directory / "absolute_effects.json", absolute)
    previous = c.read(c.WB / "results/e146/summary.json")["partitions"]
    data = {"Train Gamma": previous["cal_gamma"], "Gate only": absolute,
            **{f"Random {i}": previous[f"random{i}"] for i in range(3)}}
    plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False, "pdf.fonttype": 42})
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.9), dpi=150)
    colors = ["#2166AC", "#1B7837", "#888888", "#888888", "#888888"]
    for x, (name, row) in enumerate(data.items()):
        axes[0].plot(x-.12, row["cal_cut"], marker="x", color=colors[x], label="Train cut" if x == 0 else None)
        axes[0].plot(x, row["held_cut"], marker="s", markerfacecolor="white", color=colors[x], label="Held cut" if x == 0 else None)
        for ax, key, offset in ((axes[0], "delta_sum64_teacher_sse", .12), (axes[1], "delta_mu_to_variant_kl", 0), (axes[2], "delta_nll", 0)):
            r = row[key]
            lo, hi = r["crossed_file_source_ci95"]
            ax.vlines(x+offset, lo, hi, color=colors[x])
            ax.plot(x+offset, r["point"], marker="o", color=colors[x], label="Observed risk" if x == 0 and offset else None)
    for ax in axes:
        ax.axhline(0, color="#999999", linewidth=.7)
        ax.set_xticks(range(5), list(data), rotation=20)
        ax.grid(axis="y", alpha=.15)
        ax.set_xlim(-.5, 4.5)
    axes[0].set(title="A  Cuts and observed squared risk", ylabel="Risk increase / position (layer units)")
    axes[0].legend(frameon=False, fontsize=7)
    axes[1].set(title="B  Actual common-reference KL", ylabel="Grouped minus intact KL (nats / token)")
    axes[2].set(title="C  Actual label NLL", ylabel="Grouped minus intact NLL (nats / token)")
    fig.tight_layout(rect=(0, .13, 1, 1), w_pad=2)
    fig.text(.5, .015, "All partitions have 8 groups of 8. Same four source-map units and three cyclic shifts; crossed input-file/source intervals.\n"
             "E147 gate-only control was preregistered after E146: no extra Gamma advantage was detected at this resolution.", ha="center", fontsize=8, color="#666666")
    out = directory / "figures"
    out.mkdir(exist_ok=True)
    for suffix in ("png", "pdf"):
        fig.savefig(out / ("group_control."+suffix), bbox_inches="tight")
    print(json.dumps({k: v["point"] for k, v in absolute.items() if isinstance(v, dict)}, indent=2))


if __name__ == "__main__":
    main()
