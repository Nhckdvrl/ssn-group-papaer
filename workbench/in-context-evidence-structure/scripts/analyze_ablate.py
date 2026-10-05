"""E10 analysis: effect of run-head ablation on surface/latent signatures."""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze_common import boot_ci, fmt  # noqa

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / "results/ablate_pilot"


def load(data, path):
    meta = {}
    for l in open(ROOT / "data" / data / "rows.jsonl"):
        r = json.loads(l); meta[r["uid"]] = (r["cond"], r["base_id"], r["query_label_B"])
    recs = []
    for l in open(path):
        s = json.loads(l); c, b, qb = meta[s["uid"]]; lo1 = s["lp"][1] - s["lp"][0]
        recs.append((c, b, lo1 if qb == 1 else -lo1))
    return pd.DataFrame(recs, columns=["cond", "base", "lo"])


for setting in ("none", "run16", "ctrl16"):
    p = R / f"switch_{setting}.jsonl"
    if not p.exists():
        continue
    df = load("switch_pilot_T16", p)
    print(f"\n##### {setting}")
    for fm in ("const", "irr5", "rule5"):
        D = df[df.cond.str.startswith(fm + ":")].copy(); D["pat"] = D.cond.str.split(":").str[1]
        pv = D.pivot_table(index="base", columns="pat", values="lo")
        cl = pv.suffix_4 - pv.disp_4; nz = pv.noise_2__suffix_3 - pv.suffix_3; rc = pv.single_16 - pv.single_1
        print(f"  {fm:6s} allA {pv.allA.mean():+6.2f}  suffix4-disp4 {fmt(*boot_ci(cl))}  noise2 {fmt(*boot_ci(nz))}  "
              f"last-first {rc.mean():+.2f}")
    pa = R / f"align_{setting}.jsonl"
    if pa.exists():
        A = load("long_pilot", pa)
        A["kind"] = A.cond.str.split(":").str[1].str.split("_").str[0]
        A["order"] = A.cond.str.split("_").str[1]; A["p"] = A.cond.str.split("_").str[2]
        A["b"] = A.base.str.split("_aligned").str[0].str.split("_anti").str[0]
        pv = A.pivot_table(index=["b", "kind", "order"], columns="p", values="lo")
        eff = (pv["B"] - pv["allA"]).rename("e").reset_index()
        for k in ("aligned", "anti"):
            w = eff[eff.kind == k].pivot_table(index="b", columns="order", values="e")
            d = (w.suffix4 - w.disp4).dropna()
            print(f"  align {k:8s} suffix4-disp4 {fmt(*boot_ci(d))}")
