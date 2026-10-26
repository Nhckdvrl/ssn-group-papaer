#!/usr/bin/env python3
"""Plot E140 trainable warmstart against the fixed/free E139 cohort summaries."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POPS = ("Dolma_held_positions", "POS_held_targets")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def get(summary, key):
    v = summary["summary"]["global"][key]
    if "point" not in v or len(v.get("ci95", [])) != 2:
        raise ValueError(f"Missing point/CI for {key}")
    return v


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--e140-readout", type=Path, default=ROOT / "results/e140/readout.json")
    parser.add_argument("--e139-readout", type=Path, default=ROOT / "results/e139/readout.json")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results/e140/figures")
    parser.add_argument("--table", type=Path, default=ROOT / "results/e140/readout_table.json")
    args = parser.parse_args()
    warm = json.loads(args.e140_readout.read_text())
    prior = json.loads(args.e139_readout.read_text())
    if warm.get("experiment") != "E140" or warm.get("status") != "complete" or warm.get("errors"):
        raise ValueError("E140 readout must be complete and error-free")
    if prior.get("experiment") != "E139" or prior.get("status") != "complete" or prior.get("errors"):
        raise ValueError("E139 fixed/free comparator readout must be complete")
    ref = warm.get("old_E139_reference", {})
    if ref.get("sha256") != sha(args.e139_readout):
        raise ValueError("E140 is not bound to this E139 prior summary")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    table = {"experiment": "E140", "source_sha256": {"E140": sha(args.e140_readout), "E139": sha(args.e139_readout)},
             "scope": "E139 fixed/free cohort and E140 warmstart; intervals are input clusters conditional on each fixed cohort, not seed CI.",
             "final": {}, "initial_reference_snapshot": {}}
    protocols = ("free", "fixed", "warmstart")
    groups = {"free": "Free router (E139)", "fixed": "Fixed router (E139)", "warmstart": "Trainable native-router warmstart (E140)"}
    colors = {"teacher_error": "#4C78A8", "bias": "#F58518", "variance": "#54A24B"}
    native_fields = (
        ("native_mean_teacher_SSE_per_position", "Mean native Y error vs teacher", "teacher_error"),
        ("native_mean_bias_SSE_per_position", "Cohort mean bias²", "bias"),
        ("native_cohort_variance_per_position", "Within-cohort variance", "variance"),
    )
    comp_fields = (
        ("cohort_variance_per_position", "Σₑ Var(component)"),
        ("FP64_sum_cohort_variance_per_position", "Var(FP64 component sum)"),
        ("component_cross_covariance_per_position", "Cross-covariance"),
    )
    table["final"] = {}
    table["initial_reference_snapshot"] = {}
    fig, axes = plt.subplots(2, 2, figsize=(15.2, 9.0), squeeze=False)
    for col, pop in enumerate(POPS):
        source_names = {"free": f"free_final_{pop}", "fixed": f"fixed_final_{pop}"}
        records = {
            "free": prior["components"][source_names["free"]],
            "fixed": prior["components"][source_names["fixed"]],
            "warmstart": warm["components"][f"final_{pop}"],
        }
        x = np.arange(3, dtype=float)
        table["final"][pop] = {}
        for protocol, rec in records.items():
            table["final"][pop][protocol] = {key: get(rec, key) for key, _, _ in native_fields}
            table["final"][pop][protocol].update({key: get(rec, key) for key, _ in comp_fields})
        ax_y, ax_c = axes[0, col], axes[1, col]
        for j, (key, label, color_key) in enumerate(native_fields):
            for i, protocol in enumerate(protocols):
                value = get(records[protocol], key)
                point = float(value["point"]); lo, hi = map(float, value["ci95"])
                ax_y.errorbar(i+(j-1)*0.16, point, yerr=[[point-lo],[hi-point]], color=colors[color_key], marker=("o","s","^")[j], linestyle="none", capsize=2.5, markersize=5, label=label if i==0 else None)
        ax_y.set_title(f"{pop}: native Y teacher error = bias² + cohort variance", fontsize=9)
        ax_y.set_xticks(x, [groups[p] for p in protocols], rotation=10, ha="right", fontsize=7)
        ax_y.set_ylabel("Squared native output units / position")
        ax_y.grid(axis="y", alpha=0.2);ax_y.legend(frameon=False,fontsize=7,loc="best")

        for j,(key,label) in enumerate(comp_fields):
            for i,protocol in enumerate(protocols):
                value=get(records[protocol],key);point=float(value['point']);lo,hi=map(float,value['ci95'])
                ax_c.errorbar(i+(j-1)*0.16,point,yerr=[[point-lo],[hi-point]],color=("#4C78A8","#F58518","#54A24B")[j],marker=("o","s","^")[j],linestyle="none",capsize=2.5,markersize=5,label=label if i==0 else None)
        ax_c.set_title(f"{pop}: actual component variance identity",fontsize=9)
        ax_c.set_xticks(x,[groups[p] for p in protocols],rotation=10,ha="right",fontsize=7)
        ax_c.set_ylabel("Component variance / cross-covariance\n(squared output units / position)")
        ax_c.axhline(0,color="#555555",linestyle="--",linewidth=0.8);ax_c.grid(axis="y",alpha=0.2);ax_c.legend(frameon=False,fontsize=7,loc="best")

        # Initial cohort snapshots are tabulated, not plotted as a fourth/selected point.
        for protocol, rec in (
            ("free_E139", prior["components"][f"free_initial_{pop}"]),
            ("fixed_E139", prior["components"][f"fixed_initial_{pop}"]),
            ("warmstart_initial_reused_fixed", warm["components"]["initial_reuse"]["populations"][pop]),
        ):
            table["initial_reference_snapshot"].setdefault(pop,{})[protocol]={key:get(rec,key) for key,_,_ in native_fields}
            table["initial_reference_snapshot"][pop][protocol].update({key:get(rec,key) for key,_ in comp_fields})

    table["initial_reference_snapshot_note"] = "E140 warmstart initial snapshot reuses the E139 fixed-group initial stats because full initial tensors are identical; retained as a table reference, not added as a favorable main-plot point."
    table["comparison_scope"] = "E139 free/fixed are complete-protocol references; E140 begins from the matched fixed initial state but trains the gate. This does not isolate a single causal mechanism."
    fig.suptitle("E140 — Trainable native-router warmstart against E139 cohorts",fontsize=14,y=0.98)
    fig.text(0.5,0.018,"Final readouts only; E140 fixed-gate and free-router protocols change together with auxiliary/clip/decay coupling. Initial references are tabulated separately. File/word intervals are input-cluster uncertainty, not seed CI. No same-function or knowledge-fraction claim.",ha="center",fontsize=7.5,wrap=True)
    fig.subplots_adjust(left=0.07,right=0.99,bottom=0.13,top=0.90,hspace=0.44,wspace=0.32)
    args.output_dir.mkdir(parents=True,exist_ok=True)
    out=[]
    for fmt,name in (("png","warmstart_vs_free_fixed.png"),("pdf","warmstart_vs_free_fixed.pdf")):
        path=args.output_dir/name;tmp=path.with_name(path.stem+".partial"+path.suffix)
        fig.savefig(tmp,format=fmt,dpi=300 if fmt=="png" else None,bbox_inches="tight");os.replace(tmp,path);out.append(str(path))
    plt.close(fig)
    args.table.parent.mkdir(parents=True,exist_ok=True);tmp=args.table.with_suffix(args.table.suffix+".partial")
    tmp.write_text(json.dumps(table,indent=2,sort_keys=True)+"\n");os.replace(tmp,args.table)
    print(json.dumps({"status":"complete","outputs":out,"table":str(args.table)},indent=2))


if __name__=="__main__":
    main()
