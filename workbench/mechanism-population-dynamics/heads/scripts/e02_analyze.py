"""E02 analysis: abstraction ladder per seed. Writes results/e02/summary.json, summary.md, e02_population.png."""
import json
from pathlib import Path

import numpy as np

D = Path(__file__).resolve().parents[1] / "results" / "e02"
SEEDS = ["pythia-70m"] + [f"pythia-70m-seed{i}" for i in range(1, 10)]
STEPS = [0, 128, 256, 512, 1000, 2000, 3000, 4000, 6000, 8000, 16000, 32000, 64000, 100000, 130000, 143000]
POST = [s for s in STEPS if s >= 1000]


def load(seed, step):
    p = D / f"{seed}__step{step}.json"
    return json.loads(p.read_text()) if p.exists() else None


def per_ckpt(r):
    s = r["single"]
    heads = sorted({k.split("|")[0] for k in s})
    dm = {h: s[f"{h}|mean"]["dCL"] for h in heads}
    top = max(dm, key=dm.get)
    g = r.get("groups", {})
    union = g.get("union", {}).get("dCL")
    out = {
        "CL": r["clean"]["CL"], "FL": r["clean"]["FL"], "ACC": r["clean"]["ACC"],
        "prev_role": r["roles"]["prev"], "ind_role": r["roles"]["induction"],
        "max_S_prev": max(r["S_prev"].values()), "max_S_ind": max(r["S_ind"].values()),
        "top_causal_head": top, "top_causal_dCL": dm[top],
        "top_causal_type": ("prev" if top in r["roles"]["prev"] else "ind" if top in r["roles"]["induction"] else "other"),
        "top_causal_S_prev": r["S_prev"][top], "top_causal_S_ind": r["S_ind"][top],
        "union_dCL": union,
        "union_beats_random": (None if union is None else
                               float(np.mean([union > x for x in g["union"]["random_dCL"]]))),
        "prev_group_dCL": g.get("prev", {}).get("dCL"), "ind_group_dCL": g.get("induction", {}).get("dCL"),
        "concentration": (dm[top] / union if union and union > 0.5 else None),
        "n_heads_dCL_gt_1": sum(v > 1.0 for v in dm.values()),
        "neg_heads": {h: round(v, 2) for h, v in dm.items() if v < -0.5},
    }
    for role in ("prev", "induction"):
        grp = g.get(role)
        if grp and len(grp["heads"]) >= 1:
            ssum = sum(dm[h] for h in grp["heads"])
            out[f"{role}_n"] = len(grp["heads"])
            out[f"{role}_layers"] = sorted({int(h.split('.')[0]) for h in grp["heads"]})
            out[f"{role}_synergy"] = grp["dCL"] / ssum if ssum > 0.3 else None
            out[f"{role}_max_single_share"] = max(dm[h] for h in grp["heads"]) / grp["dCL"] if grp["dCL"] > 0.5 else None
    if "kcomp" in r:
        c, a = r["kcomp"]["clean"], r["kcomp"]["prev_ablated"]
        out["kcomp_ratio"] = float(np.mean([a[h] / c[h] for h in c if c[h] > 0.05])) if any(c[h] > 0.05 for h in c) else None
    if "R2" in r:
        out["R2"] = r["R2"]
    return out


def main():
    summ = {}
    for seed in SEEDS:
        rows = {}
        for st in STEPS:
            r = load(seed, st)
            if r:
                rows[st] = per_ckpt(r)
        if not rows:
            continue
        form_prev = next((st for st in STEPS if st in rows and rows[st]["max_S_prev"] >= 0.5), None)
        form_ind = next((st for st in STEPS if st in rows and rows[st]["max_S_ind"] >= 0.2), None)
        summ[seed] = {"rows": rows, "form_prev": form_prev, "form_ind": form_ind}
    (D / "summary.json").write_text(json.dumps(summ, indent=1))

    lines = ["| seed | prev-role heads (@8000 / @143000) | induction-role heads (@8000 / @143000) | top causal head (type) @1000 / 8000 / 143000 | concentration @1000 / 8000 / 143000 | K-comp ratio @8000 | CL @1000 / 8000 / 143000 | form prev / ind |",
             "|---|---|---|---|---|---|---|---|"]
    for seed, v in summ.items():
        R = v["rows"]

        def g(st, k, fmt="{}"):
            return fmt.format(R[st][k]) if st in R and R[st].get(k) is not None else "—"
        tops = " / ".join(f"{R[s]['top_causal_head']}({R[s]['top_causal_type']},{R[s]['top_causal_dCL']:.1f})" if s in R else "—"
                          for s in (1000, 8000, 143000))
        lines.append(f"| {seed} | {g(8000,'prev_role')} / {g(143000,'prev_role')} | {g(8000,'ind_role')} / {g(143000,'ind_role')} | "
                     f"{tops} | {g(1000,'concentration','{:.2f}')} / {g(8000,'concentration','{:.2f}')} / {g(143000,'concentration','{:.2f}')} | "
                     f"{g(8000,'kcomp_ratio','{:.2f}')} | {g(1000,'CL','{:.2f}')} / {g(8000,'CL','{:.2f}')} / {g(143000,'CL','{:.2f}')} | "
                     f"{v['form_prev']} / {v['form_ind']} |")
    (D / "summary.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
