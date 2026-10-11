"""Display preregistered transfer contrasts and balanced response fingerprints."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("directories", nargs="+")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    fig, axes = plt.subplots(len(args.directories), 2, figsize=(11.5, 3.8 * len(args.directories)), squeeze=False)
    keys = ["flip_minus_base", "criterion_patch_minus_base", "name_patch_minus_base",
            "explicit_flip_minus_explicit", "explicit_criterion_patch_minus_explicit"]
    labels = ["Native criterion swap", "Same-name criterion K/V", "Other-name K/V",
              "Explicit native swap", "Explicit criterion K/V"]
    colors = ["#708090", "#0072b2", "#009e73", "#999999", "#e69f00"]
    for row, directory in enumerate(args.directories):
        d = Path(directory)
        summary = json.loads((d / "analysis.json").read_text())
        ax, bx = axes[row]
        values = [summary["contrasts"][k]["donor_directed_transfer"] for k in keys]
        means = np.array([v["mean"] for v in values])
        bounds = np.array([v["ci95"] for v in values]).T
        ax.barh(np.arange(5), means, color=colors)
        ax.errorbar(means, np.arange(5), xerr=np.maximum(0, np.array([means - bounds[0], bounds[1] - means])),
                    fmt="none", ecolor="black", capsize=3)
        ax.set_yticks(np.arange(5), labels)
        ax.invert_yaxis()
        ax.axvline(0, color="black", lw=.7)
        ax.set_xlabel("Donor-standard directed shift (nats; paired 95% CI)")
        ax.set_title(f"{summary['run']['args']['stage'].capitalize()}: {len(json.loads((d / 'contexts.jsonl').read_text().splitlines()[0])['queries'])} queries × {summary['run']['args']['n']} contexts")
        rows = [json.loads(line) for line in (d / "behavior.jsonl").read_text().splitlines()]
        cells = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        for key, name, color in [("base", "Recipient native", "#708090"),
                                 ("flip", "Donor native", "#cc79a7"),
                                 ("criterion_patch", "Same-name criterion K/V", "#0072b2")]:
            points = []
            for g, dg in cells:
                per_context = [np.mean([score[key]["z"] for q, score in zip(r["queries"], r["scores"])
                                        if q["recipient_gold"] == g and q["donor_gold"] == dg]) for r in rows]
                points.append(np.mean(per_context))
            bx.plot(np.arange(4), points, "o-", label=name, color=color)
        bx.axhline(0, color="black", lw=.7)
        bx.set_xticks(np.arange(4), ["+ / +", "+ / −", "− / +", "− / −"])
        bx.set_xlabel("Correct sign under recipient / donor standard")
        bx.set_ylabel("logit(positive) − logit(negative)")
        bx.set_title("Response fingerprint across new reviews")
        bx.legend(frameon=False, fontsize=8)
    fig.suptitle("Before-input source-field interchange; recipient demonstrations retained", y=1.01)
    fig.tight_layout()
    dest = Path(args.out)
    dest.parent.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(dest.with_suffix("." + ext), dpi=180, bbox_inches="tight")
    print(dest)


if __name__ == "__main__":
    main()
