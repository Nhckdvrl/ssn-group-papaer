#!/usr/bin/env python3
"""Plot already-saved E141 support XOR/both partition and paired input intervals."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GROUPS = ("free", "fixed", "warm")
PAIRS = ("seed0_seed1", "seed0_seed2", "seed1_seed2")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def point_ci(record: dict) -> tuple[float, float, float]:
    return float(record["point"]), float(record["ci95"][0]), float(record["ci95"][1])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", type=Path, default=ROOT / "results/e141/support_partition.json")
    parser.add_argument("--audit", type=Path, default=ROOT / "results/e141/independent_audit.json")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results/e141/figures")
    parser.add_argument("--table", type=Path, default=ROOT / "results/e141/readout_table.json")
    args = parser.parse_args()
    summary = json.loads(args.summary.read_text())
    audit = json.loads(args.audit.read_text())
    if summary.get("experiment") != "E141" or summary.get("status") != "complete" or summary.get("errors"):
        raise ValueError("E141 support partition summary must be complete/error-free")
    if audit.get("experiment") != "E141" or audit.get("status") != "complete":
        raise ValueError("E141 independent audit must be complete")
    if audit.get("source_summary_sha256") != sha(args.summary):
        raise ValueError("Independent audit is not bound to this summary")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    group_names = {"free": "Free router", "fixed": "Fixed router", "warm": "Trainable warmstart"}
    group_colors = {"free": "#4C78A8", "fixed": "#F58518", "warm": "#54A24B"}
    table = {
        "experiment": "E141",
        "source_summary_sha256": sha(args.summary),
        "source_independent_audit_sha256": sha(args.audit),
        "scope": "Actual BF16 component outputs, three fixed finite cohorts, original 262,144 Dolma held positions/512 sequences/32 files; CIs resample input files, not seeds.",
        "groups": {},
        "paired_contrasts": summary["contrasts"],
        "auxiliary_common_on_cosine_scope": "Pooled cosine only on each pair's actual both-on positions; support counts differ by group/pair and are reported alongside it; descriptive, not pure-content evidence.",
    }
    for group in GROUPS:
        record = summary["groups"][group]
        g = record["summary"]["global"]
        pairs = {}
        for pair in PAIRS:
            pairs[pair] = {}
            for field in ("xor_count_per_position", "both_on_count_per_position", "left_on_count_per_position", "right_on_count_per_position", "neither_on_count_per_position", "both_f_pooled_cosine"):
                value = g[f"{pair}/{field}"]
                pairs[pair][field] = {"point": value["point"], "ci95": value["ci95"], "defined_draws": value.get("defined_draws")}
        table["groups"][group] = {
            "raw_sha256": record["raw_sha256"], "metadata_sha256": record["metadata_sha256"],
            "xor": {"point": g["cohort_xor_per_position"]["point"], "ci95": g["cohort_xor_per_position"]["ci95"]},
            "both": {"point": g["cohort_both_per_position"]["point"], "ci95": g["cohort_both_per_position"]["ci95"]},
            "total": {"point": g["cohort_total_per_position"]["point"], "ci95": g["cohort_total_per_position"]["ci95"]},
            "pairs": pairs,
            "all_64_experts_retained": True,
        }

    fig, axes = plt.subplots(1, 3, figsize=(16.2, 5.8), squeeze=False)
    ax_stack, ax_ci, ax_fcos = axes[0]
    x = np.arange(3, dtype=float)
    xor_values, both_values, total_values, total_ci = [], [], [], []
    for group in GROUPS:
        g = summary["groups"][group]["summary"]["global"]
        xor = g["cohort_xor_per_position"]
        both = g["cohort_both_per_position"]
        total = g["cohort_total_per_position"]
        xor_values.append(float(xor["point"]))
        both_values.append(float(both["point"]))
        total_values.append(float(total["point"]))
        total_ci.append(total["ci95"])
    ax_stack.bar(x, xor_values, color="#B279A2", label="Support XOR")
    ax_stack.bar(x, both_values, bottom=xor_values, color="#72B7B2", label="Both-on component difference")
    for i, group in enumerate(GROUPS):
        lo, hi = map(float, total_ci[i])
        point = total_values[i]
        ax_stack.errorbar(i + 0.12, point, yerr=[[point - lo], [hi - point]], color="#222222", marker="D", linestyle="none", capsize=3, linewidth=1.2, markersize=5)
    ax_stack.set_xticks(x, [group_names[g] for g in GROUPS], rotation=10, ha="right")
    ax_stack.set_ylabel("Component difference SSE / position\n(squared expert-output units)")
    ax_stack.set_title("Actual component difference: XOR + both = total\nblack diamond: total with 95% file CI", fontsize=9)
    ax_stack.grid(axis="y", alpha=0.2)
    ax_stack.legend(frameon=False, fontsize=8, loc="upper left")

    # Show each component and total with its already-stored input-cluster CI.
    metric_specs = [
        ("cohort_xor_per_position", "XOR", "o", -0.18),
        ("cohort_both_per_position", "Both", "s", 0.0),
        ("cohort_total_per_position", "Total", "^", 0.18),
    ]
    for group_index, group in enumerate(GROUPS):
        g = summary["groups"][group]["summary"]["global"]
        for field, label, marker, shift in metric_specs:
            point, lo, hi = point_ci(g[field])
            ax_ci.errorbar(group_index + shift, point, yerr=[[point-lo],[hi-point]], color=group_colors[group], marker=marker,
                           linestyle="none", capsize=2.5, markersize=5, linewidth=1.1, label=f"{group_names[group]} · {label}" if group_index==0 else None)
    ax_ci.set_xticks(range(3), [group_names[g] for g in GROUPS], rotation=10, ha="right")
    ax_ci.set_ylabel("Component difference SSE / position\n(squared expert-output units)")
    ax_ci.set_title("Stored file-bootstrap intervals for XOR, both and total", fontsize=9)
    ax_ci.grid(axis="y", alpha=0.2)
    ax_ci.legend(frameon=False, fontsize=7, loc="best", ncol=1)

    # Auxiliary cosine is never pooled across support conditions; show the observed count in each x tick.
    offsets = {"free": -0.23, "fixed": 0.0, "warm": 0.23}
    markers = {"free": "o", "fixed": "s", "warm": "^"}
    fcos_counts = {}
    for group in GROUPS:
        g = summary["groups"][group]["summary"]["global"]
        fcos_counts[group] = []
        for i, pair in enumerate(PAIRS):
            cos = g[f"{pair}/both_f_pooled_cosine"]
            count = float(g[f"{pair}/both_on_count_per_position"]["point"])
            fcos_counts[group].append(count)
            point, lo, hi = point_ci(cos)
            ax_fcos.errorbar(i + offsets[group], point, yerr=[[point-lo],[hi-point]], color=group_colors[group], marker=markers[group],
                             linestyle="none", capsize=2.3, markersize=4.5, linewidth=1.0,
                             label=group_names[group] if i==0 else None)
    table["auxiliary_common_on_cosine_scope"] += " Per-pair both-on counts per position are listed in groups.*.pairs.*.both_on_count_per_position."
    ax_fcos.set_xticks(range(3), ["0–1", "0–2", "1–2"])
    ax_fcos.set_ylabel("Pooled cosine of actual both-on f vectors\n(unitless; file-bootstrap CI)")
    ax_fcos.set_title("Auxiliary common-on vector alignment\nper-pair support counts in table", fontsize=9)
    ax_fcos.grid(axis="y", alpha=0.2)
    ax_fcos.legend(frameon=False, fontsize=8)

    fig.suptitle("E141 — Support XOR, both-on difference and total", fontsize=14, y=0.98)
    fig.text(0.5, 0.015,
             "Groups use the same 262,144 held positions; actual support counts differ by group/pair. XOR+both is a descriptive partition, not a causal mask intervention. "
             "Cosine is auxiliary and only on common-on positions. All CIs resample files, not seeds; no pure-content or knowledge-fraction interpretation.",
             ha="center", fontsize=7.5, wrap=True)
    fig.subplots_adjust(left=0.07, right=0.99, bottom=0.16, top=0.86, wspace=0.38)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    outputs=[]
    for fmt,name in (("png","support_partition.png"),("pdf","support_partition.pdf")):
        path=args.output_dir/name;tmp=path.with_name(path.stem+".partial"+path.suffix)
        fig.savefig(tmp,format=fmt,dpi=300 if fmt=="png" else None,bbox_inches="tight");os.replace(tmp,path);outputs.append(str(path))
    plt.close(fig)
    args.table.parent.mkdir(parents=True,exist_ok=True);tmp=args.table.with_suffix(args.table.suffix+".partial")
    tmp.write_text(json.dumps(table,indent=2,sort_keys=True)+"\n");os.replace(tmp,args.table)
    print(json.dumps({"status":"complete","outputs":outputs,"table":str(args.table)},indent=2))


if __name__=="__main__":
    main()
