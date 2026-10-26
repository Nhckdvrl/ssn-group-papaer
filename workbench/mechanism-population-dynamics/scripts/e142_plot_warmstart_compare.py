#!/usr/bin/env python3
"""Plot E142 shared-random-gate cohort against fixed/free/warm references."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POP = "Dolma_held_positions"
METRICS = (
    ("native_mean_teacher_SSE_per_position", "Mean native Y error vs teacher", "#4C78A8", "o"),
    ("native_mean_bias_SSE_per_position", "Cohort mean bias²", "#F58518", "s"),
    ("native_cohort_variance_per_position", "Native Y cohort variance", "#54A24B", "^"),
    ("cohort_variance_per_position", "Σ component variances", "#B279A2", "o"),
    ("FP64_sum_cohort_variance_per_position", "FP64 sum variance", "#E45756", "s"),
    ("component_cross_covariance_per_position", "Component cross-covariance", "#72B7B2", "^"),
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def metric(record: dict, key: str) -> dict:
    item = record["summary"]["global"][key]
    if "point" not in item or len(item.get("ci95", [])) != 2:
        raise ValueError(f"Missing stored point/CI for {key}")
    return item


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--e142", type=Path, default=ROOT / "results/e142/readout.json")
    parser.add_argument("--e139", type=Path, default=ROOT / "results/e139/readout.json")
    parser.add_argument("--e140", type=Path, default=ROOT / "results/e140/readout.json")
    parser.add_argument("--audit", type=Path, default=ROOT / "results/e142/independent_audit.json")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results/e142/figures")
    parser.add_argument("--table", type=Path, default=ROOT / "results/e142/readout_table.json")
    args = parser.parse_args()
    s142, s139, s140, audit = [json.loads(p.read_text()) for p in (args.e142, args.e139, args.e140, args.audit)]
    for name, obj in (("E142", s142), ("E139", s139), ("E140", s140)):
        if obj.get("status") != "complete" or obj.get("errors"):
            raise ValueError(f"{name} readout is not complete")
    if audit.get("status") != "complete" or audit.get("readout_sha256") != sha(args.e142):
        raise ValueError("E142 independent audit does not bind to the current E142 readout")
    if s142["old_reference"]["R_F"]["sha256"] != sha(args.e139) or s142["old_reference"]["T"]["sha256"] != sha(args.e140):
        raise ValueError("E142 old-cohort references differ from E139/E140 summaries")

    groups = {
        "R_free": ("R — free gate (E139)", s139["components"]["free_final_Dolma_held_positions"]),
        "S_shared_random": ("S — shared random gate (E142)", s142["components"]["final_Dolma_held_positions"]),
        "T_warmstart": ("T — native warmstart, trainable (E140)", s140["components"]["final_Dolma_held_positions"]),
        "F_fixed": ("F — native gate fixed (E139)", s139["components"]["fixed_final_Dolma_held_positions"]),
    }
    table = {
        "experiment": "E142",
        "source_sha256": {"E142": sha(args.e142), "E142_audit": sha(args.audit), "E139": sha(args.e139), "E140": sha(args.e140)},
        "population": {"name": "Dolma held positions", "positions": 262144, "sequences": 512, "file_clusters": 32},
        "interval_scope": "Input-file cluster bootstrap conditional on each fixed three-student cohort; not initialization-seed CI.",
        "final_groups": {},
        "initial_reference_snapshot": {},
        "paired_shared_minus_old_groups": s142["components"],
        "limits": "E139/E140 are prior cohort summaries; E142 is a shared-random-gate cohort. Protocols differ in more than one mechanism. No equivalence or knowledge-fraction claim.",
    }

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    fig, axes = plt.subplots(1, 2, figsize=(13.5, 6.2), squeeze=False)
    ax_native, ax_component = axes[0]
    ordered = list(groups.items())
    x = np.arange(len(ordered), dtype=float)
    for j, (field, label, color, marker) in enumerate(METRICS[:3]):
        for i, (key, (_, record)) in enumerate(ordered):
            v = metric(record, field); point = float(v["point"]); lo, hi = map(float, v["ci95"])
            ax_native.errorbar(i+(j-1)*0.16, point, yerr=[[point-lo],[hi-point]], color=color, marker=marker, linestyle="none", capsize=2.7, markersize=5, label=label if i==0 else None)
            table["final_groups"].setdefault(key,{})[field]=v
    ax_native.set_xticks(x,[name for _,(name,_) in ordered],rotation=12,ha="right",fontsize=8)
    ax_native.set_ylabel("Squared native Y output units / position")
    ax_native.set_title("Native Y teacher error = cohort bias² + variance")
    ax_native.grid(axis="y",alpha=0.2);ax_native.legend(frameon=False,fontsize=7)

    for j,(field,label,color,marker) in enumerate(METRICS[3:]):
        for i,(key,(_,record)) in enumerate(ordered):
            v=metric(record,field);point=float(v["point"]);lo,hi=map(float,v["ci95"])
            ax_component.errorbar(i+(j-1)*0.16,point,yerr=[[point-lo],[hi-point]],color=color,marker=marker,linestyle="none",capsize=2.7,markersize=5,label=label if i==0 else None)
            table["final_groups"].setdefault(key,{})[field]=v
    ax_component.set_xticks(x,[name for _,(name,_) in ordered],rotation=12,ha="right",fontsize=8)
    ax_component.set_ylabel("Squared actual-component units / position")
    ax_component.set_title("Component variance, FP64 sum variance and cross-covariance")
    ax_component.axhline(0,color="#555555",linestyle="--",linewidth=0.8);ax_component.grid(axis="y",alpha=0.2);ax_component.legend(frameon=False,fontsize=7)

    # Initial comparisons are a table only; E140's initial raw readout is registered as an E139 fixed-initial reuse.
    initial_records = {
        "R_free_initial": s139["components"]["free_initial_Dolma_held_positions"],
        "F_fixed_initial": s139["components"]["fixed_initial_Dolma_held_positions"],
        "T_warmstart_initial_reused_fixed": s140["components"]["initial_reuse"]["populations"][POP],
        "S_shared_random_initial": s142["components"]["initial_Dolma_held_positions"],
    }
    for key,record in initial_records.items():
        table["initial_reference_snapshot"][key]={field:metric(record,field) for field,_,_,_ in METRICS[:3]}
        table["initial_reference_snapshot"][key].update({field:metric(record,field) for field,_,_,_ in METRICS[3:]})
    table["initial_reference_note"]="Initial group readings are tabulated separately. E140 warmstart initial statistics reuse the exact E139 fixed initial snapshot; R/F/T old model weights and raw cohorts remain referenced, not duplicated."
    table["paired_contrasts"]={k:s142["components"][k] for k in ('paired_shared_minus_F_Dolma_held_positions','paired_shared_minus_R_Dolma_held_positions','paired_shared_minus_T_Dolma_held_positions')}

    fig.suptitle("E142 — Shared-random-gate cohort among prior free/fixed/warm references",fontsize=14,y=0.98)
    fig.text(0.5,0.02,"Dolma only; same 262,144 held positions and squared-output/position units. All CIs are input-file cluster uncertainty conditional on each fixed cohort, not seed CI. "
             "E140 initial reuse is listed in the table, not plotted as a new measurement. Protocols differ; no same-function or knowledge-fraction claim.",
             ha="center",fontsize=8,wrap=True)
    fig.subplots_adjust(left=0.07,right=0.99,bottom=0.17,top=0.88,wspace=0.34)
    args.output_dir.mkdir(parents=True,exist_ok=True)
    outputs=[]
    for fmt,name in (("png","shared_random_vs_RTF.png"),("pdf","shared_random_vs_RTF.pdf")):
        path=args.output_dir/name;tmp=path.with_name(path.stem+".partial"+path.suffix)
        fig.savefig(tmp,format=fmt,dpi=300 if fmt=="png" else None,bbox_inches="tight");os.replace(tmp,path);outputs.append(str(path))
    plt.close(fig)
    table["readout_audit_sha256"]=audit["readout_sha256"]
    args.table.parent.mkdir(parents=True,exist_ok=True);tmp=args.table.with_suffix(args.table.suffix+".partial")
    tmp.write_text(json.dumps(table,indent=2,sort_keys=True)+"\n");os.replace(tmp,args.table)
    print(json.dumps({"status":"complete","outputs":outputs,"table":str(args.table)},indent=2))


if __name__=="__main__":main()
