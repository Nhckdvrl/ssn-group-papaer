#!/usr/bin/env python3
"""E172 summary tables from results/e172/*.json -> results/e172/summary.json (+ printed tables).
Readout 1: content - function T_D difference per init pair (deep L6-11 mean and L11), seed-jackknife SE,
init/rerun and init/order ratios per group. Readout 2/3 summaries are copied from their own json files."""
import itertools
import json
from pathlib import Path

import numpy as np

WB = Path(__file__).resolve().parents[1]
R = WB / "results/e172"
out = {}


def jk_se(pairs, vals, seeds):
    jk = [np.mean([v for (a, b), v in zip(pairs, vals) if s not in (a, b)]) for s in seeds]
    return float(np.sqrt((len(seeds) - 1) / len(seeds) * ((np.array(jk) - np.mean(jk)) ** 2).sum()))


r1 = {}
for tok in (3200000000, 3999793152, 400000000, 0):
    f = R / f"token_class_td_{tok}.json"
    if not f.exists():
        continue
    o = json.loads(f.read_text())
    pairs = [tuple(p) for p in o["pairs"]["init"]]
    seeds = sorted({r for p in pairs for r in p})
    rec = {"n_init_pairs": len(pairs), "groupings": {}}
    for gname, G in o["groupings"].items():
        tab = {}
        for g, r in G.items():
            L = r["layers"]
            row = {"n_pairs": r["n_pairs"], "n_types": r["n_types"]}
            for lname, ls in (("deep", range(6, 12)), ("L11", [11])):
                per = np.mean([L[l]["D_init_pairs"] for l in ls], 0) if pairs else np.array([])
                row[lname] = {k: (float(np.mean([L[l][f"D_{k}"] for l in ls])) if L[ls[0]].get(f"D_{k}") is not None else None)
                              for k in ("init", "order", "rerun", "floor")}
                row[lname]["T_ctx_init"] = float(np.mean([L[l]["C_init"] for l in ls])) if pairs else None
                row[lname]["init_per_pair"] = per.tolist()
                row[lname]["init_range"] = [float(per.min()), float(per.max())] if len(per) else None
                row[lname]["init_jkse"] = jk_se(pairs, per, seeds) if len(pairs) > 2 else None
            tab[g] = row
        rec["groupings"][gname] = tab
    # content - function contrasts
    con = {}
    for gname, (ga, gb) in {"type_majority_upos": ("content", "function"), "pair_same_upos": ("content", "function"),
                            "type_freq": ("high", "low"), "class_x_freq_high": ("content|high", "function|high")}.items():
        src = "class_x_freq" if gname == "class_x_freq_high" else gname
        G = rec["groupings"].get(src, {})
        if ga not in G or gb not in G or not pairs:
            continue
        c = {}
        for lname in ("deep", "L11"):
            d = np.array(G[ga][lname]["init_per_pair"]) - np.array(G[gb][lname]["init_per_pair"])
            c[lname] = {"a": ga, "b": gb, "mean_diff_init": float(d.mean()), "pair_range": [float(d.min()), float(d.max())],
                        "n_pairs_a_gt_b": int((d > 0).sum()), "n_pairs": int(len(d)), "jkse": jk_se(pairs, d, seeds),
                        "diff_rerun": (G[ga][lname]["rerun"] - G[gb][lname]["rerun"]) if G[ga][lname]["rerun"] is not None else None,
                        "diff_order": (G[ga][lname]["order"] - G[gb][lname]["order"]) if G[ga][lname]["order"] is not None else None,
                        "ratio_init_rerun_a": (G[ga][lname]["init"] / G[ga][lname]["rerun"]) if G[ga][lname]["rerun"] else None,
                        "ratio_init_rerun_b": (G[gb][lname]["init"] / G[gb][lname]["rerun"]) if G[gb][lname]["rerun"] else None,
                        "ratio_init_order_a": G[ga][lname]["init"] / G[ga][lname]["order"] if G[ga][lname]["order"] else None,
                        "ratio_init_order_b": G[gb][lname]["init"] / G[gb][lname]["order"] if G[gb][lname]["order"] else None}
        con[gname] = c
    rec["contrasts"] = con
    r1[str(tok)] = rec
out["readout1"] = r1

for tok in (3200000000, 3999793152):
    f = R / f"antoine_{tok}.json"
    if f.exists():
        a = json.loads(f.read_text())
        out[f"readout2_{tok}"] = {k: a[k] for k in ("baseline_word_form", "stability", "init_spread", "pair_diffs", "n_per_upos", "profile_upos")}
        out[f"readout2_{tok}"]["per_model"] = {m: {"model_spec": v["model_spec"], "probe_acc": v["probe_all"]["acc"], "probe_f1": v["probe_all"]["macro_f1"],
                                                     "probe_layer_acc": v["probe_layer_acc"]} for m, v in a["models"].items()}
        fl = [m for m in a["models"] if m.endswith("@0")]
        out[f"readout2_{tok}"]["untrained_spec_upos_deep"] = {u: float(np.mean([np.mean([a["models"][m]["spec"][l][u] for l in range(6, 12)]) for m in fl]))
                                                              for u in a["profile_upos"]}
f = R / "f2_timeline.json"
if f.exists():
    t = json.loads(f.read_text())
    out["readout3"] = {"summary": t["summary"], "missing": t["missing"], "tokens": t["tokens"], "ref": t["ref"]}
(R / "summary.json").write_text(json.dumps(out, indent=1))

# ---- readout 3 noise: per-init-pair t80 of the absolute deep cell curve (pairs present at every t <= REF)
if f.exists():
    toks = [x for x in t["tokens"] if x <= t["ref"]]
    pairs_ref = [tuple(q) for q in t["curves"][str(t["ref"])]["pairs"]["init"]]
    def t80(ts, ys, ref):
        thr = .8 * ref
        for i in range(len(ys)):
            if all(y >= thr for y in ys[i:]):
                if i == 0:
                    return float(ts[0])
                x0, x1 = np.log10(ts[i - 1]), np.log10(ts[i]); y0, y1 = ys[i - 1], ys[i]
                return float(10 ** (x0 + (thr - y0) / (y1 - y0) * (x1 - x0)))
        return None
    per = {}
    for v in t["vars"]:
        curves = []
        for q in pairs_ref:
            ys = []
            for x in toks:
                c = t["curves"][str(x)]
                ps = [tuple(z) for z in c["pairs"]["init"]]
                ys.append(c["init"][v]["cell_deep_per_pair"][ps.index(q)])
            curves.append(ys)
        per[v] = [t80(toks, ys, ys[-1]) for ys in curves]
    lt = {v: np.log10(np.array(per[v], float)) for v in per}
    order_cons = {f"{a}<{b}": int((lt[a] < lt[b]).sum()) for a in t["vars"] for b in t["vars"] if a != b}
    out["readout3"]["per_pair_t80_init_deep"] = {v: {"median": float(np.median(per[v])), "min": float(min(per[v])), "max": float(max(per[v])),
                                                     "values": per[v]} for v in per}
    out["readout3"]["per_pair_order_consistency"] = {"n_pairs": len(pairs_ref), "counts": order_cons}
    (R / "summary.json").write_text(json.dumps(out, indent=1))
    print("\n=== readout 3: per-pair t80 (abs deep cell curve, 15 init pairs)")
    for v in sorted(per, key=lambda v: np.median(per[v])):
        print(f"{v:10s} median {np.median(per[v])/1e6:6.0f}M  range {min(per[v])/1e6:6.0f}–{max(per[v])/1e6:6.0f}M")
    for a, b in (("upos", "deprel"), ("upos", "prev_upos"), ("upos", "next_upos"), ("upos", "head_upos"), ("feats", "deprel"), ("upos", "genre"), ("upos", "sentpos"), ("deprel", "prev_upos"), ("sentpos", "deprel"), ("genre", "deprel")):
        print(f"  {a} earlier than {b}: {order_cons[a+'<'+b]}/{len(pairs_ref)} pairs")

# ---- print
for tok, rec in r1.items():
    print(f"\n=== readout 1 @ {tok} ({rec['n_init_pairs']} init pairs)")
    for gname in ("type_majority_upos", "type_freq", "class_x_freq", "pair_same_upos"):
        G = rec["groupings"].get(gname)
        if not G:
            continue
        print(f"-- {gname}")
        print("| 组 | 对数 | 词形数 | 深层 初始化（15 对范围，jkSE） | 深层 只换顺序 | 深层 重跑 | 深层 地板 | L11 初始化 | L11 只换顺序 | L11 重跑 | 初始化÷重跑（深层） |")
        for g, r in G.items():
            d, e = r["deep"], r["L11"]
            fm = lambda x: "—" if x is None else f"{x:.3f}"
            print(f"| {g} | {r['n_pairs']} | {r['n_types']} | {fm(d['init'])} ({d['init_range'][0]:.2f}–{d['init_range'][1]:.2f}, {fm(d['init_jkse'])}) | {fm(d['order'])} | {fm(d['rerun'])} | {fm(d['floor'])} | "
                  f"{fm(e['init'])} | {fm(e['order'])} | {fm(e['rerun'])} | {('—' if not d['rerun'] else f'{d[chr(105)+chr(110)+chr(105)+chr(116)]/d[chr(114)+chr(101)+chr(114)+chr(117)+chr(110)]:.2f}')} |")
    for gname, c in rec["contrasts"].items():
        for lname, x in c.items():
            print(f"contrast {gname} {lname}: {x['a']} − {x['b']} = {x['mean_diff_init']:+.3f} (pairs {x['pair_range'][0]:+.3f}…{x['pair_range'][1]:+.3f}, {x['n_pairs_a_gt_b']}/{x['n_pairs']} >0, jkSE {x['jkse']:.3f})"
                  f" | rerun {x['diff_rerun'] if x['diff_rerun'] is None else round(x['diff_rerun'], 3)} order {x['diff_order'] if x['diff_order'] is None else round(x['diff_order'], 3)}")
print("\nsaved", R / "summary.json")
