#!/usr/bin/env python3
"""E174: collect td_null_*, token_null_*, coarse_null.json into summary.json + summary.md (tables)."""
import json
from pathlib import Path

import numpy as np

WB = Path(__file__).resolve().parents[1]
R = WB / "results/e174"
md, S = [], {}


def f(x, d=3):
    return f"{x:.{d}f}".replace("0.", ".", 1) if x >= 0 else "−" + f"{-x:.{d}f}".replace("0.", ".", 1)


# ---------------- T_D
md.append("## 同词形分区 T_D（深层 L6–11 均值；括号 = 零假设 2.5–97.5 分位；± = 超出量的 20 块 jackknife SE）\n")
for tok in (3200000000, 800000000):
    p = R / f"td_null_{tok}.json"
    if not p.exists():
        continue
    d = json.loads(p.read_text())
    S[f"td_{tok}"] = {"pool_info": d["pool_info"]}
    md.append(f"\n**{tok/1e9:g}B token**；池信息：{json.dumps(d['pool_info'], ensure_ascii=False)}\n")
    for agg in ("deep", "L11", "shallow"):
        md.append(f"\n{agg}：\n\n| 配对 | 池 | 真实 | 零假设均值 [区间] | 超出 ± SE | 超出/真实 | 仅可动对：超出/真实 |\n|---|---|---|---|---|---|---|")
        rows = {}
        for g in ("rerun", "order", "init"):
            rs = [r for r in d["results"] if r["group"] == g]
            for pool in ("U", "F", "T"):
                X = [r["pools"][f"{pool}_all"][agg] for r in rs]
                Xm = [r["pools"][f"{pool}_movable"][agg] for r in rs]
                real = np.mean([x["real"] for x in X]); nm = np.mean([x["null_mean"] for x in X])
                lo = np.mean([x["null_lo"] for x in X]); hi = np.mean([x["null_hi"] for x in X])
                exc = np.mean([x["excess"] for x in X]); se = np.mean([x["excess_jk_se"] for x in X])
                fr = np.mean([x["excess_frac"] for x in X]); frm = np.mean([x["excess_frac"] for x in Xm])
                rng = "" if len(X) == 1 else f"（逐对 {f(min(x['excess_frac'] for x in X),2)}–{f(max(x['excess_frac'] for x in X),2)}）"
                n_above = sum(x["real"] > x["null_hi"] for x in X)
                rows[(g, pool)] = dict(real=real, null=nm, lo=lo, hi=hi, excess=exc, se=se, frac=fr, frac_movable=frm,
                                       n_pairs=len(X), n_real_above_null97_5=int(n_above))
                if pool == "T" and agg != "deep":
                    continue
                md.append(f"| {g}（{len(X)} 对） | {pool} | {f(real)} | {f(nm)} [{f(lo)}, {f(hi)}] | {f(exc)} ± {f(se)} | {f(fr,2)}{rng} | {f(frm,2)} |")
        for pool in ("U", "F"):
            ri = rows[("init", pool)]; rr = rows[("rerun", pool)]; ro = rows[("order", pool)]
            rows[("ratio", pool)] = {"init_over_rerun_real": ri["real"] / rr["real"], "init_over_rerun_excess": ri["excess"] / rr["excess"],
                                     "order_over_rerun_real": ro["real"] / rr["real"], "order_over_rerun_excess": ro["excess"] / rr["excess"]}
            md.append(f"\n{agg} 池 {pool}：初始化÷重跑 真实 {f(ri['real']/rr['real'],2)} → 超出 {f(ri['excess']/rr['excess'],2)}；顺序÷重跑 真实 {f(ro['real']/rr['real'],2)} → 超出 {f(ro['excess']/rr['excess'],2)}")
        S[f"td_{tok}"][agg] = {f"{k[0]}|{k[1]}": v for k, v in rows.items()}

# ---------------- per-token
md.append("\n\n## 逐 token 因果角色（matched；深层 L6–11 均值；零假设 32 次；± = 16 窗口块 jackknife SE）\n")
for tok in ("3200000000", "3999793152"):
    p = R / f"token_null_{tok}.json"
    if not p.exists():
        continue
    d = json.loads(p.read_text())
    S[f"token_{tok}"] = {"pool_info": d["pool_info"], "pairs": {}}
    md.append(f"\n**{tok}**；池信息：{json.dumps(d['pool_info'])}\n\n| 配对 | 真实 | U 零假设 [区间] | U 超出/真实 | F 零假设 | F 超出/真实 | LU 零假设 | LU 超出/真实 | LU 超出 ± SE |\n|---|---|---|---|---|---|---|---|---|")
    for r in d["results"]:
        L = [x for x in r["layers"] if x["layer"] >= 6]
        real = np.mean([x["real"] for x in L])
        e = {k: {"null": np.mean([x["pools"][k]["null_mean"] for x in L]), "lo": np.mean([x["pools"][k]["null_lo"] for x in L]),
                 "hi": np.mean([x["pools"][k]["null_hi"] for x in L]), "excess": np.mean([x["pools"][k]["excess"] for x in L]),
                 "se": np.mean([x["pools"][k]["excess_jk_se"] for x in L])} for k in ("U", "F", "LU")}
        S[f"token_{tok}"]["pairs"][f"{r['A']}:{r['B']}"] = {"real": real, **e}
        md.append(f"| {r['A']}:{r['B']} | {f(real)} | {f(e['U']['null'])} [{f(e['U']['lo'])}, {f(e['U']['hi'])}] | {f(e['U']['excess']/real,2)} | {f(e['F']['null'])} | {f(e['F']['excess']/real,2)} | {f(e['LU']['null'])} | {f(e['LU']['excess']/real,2)} | {f(e['LU']['excess'])} ± {f(e['LU']['se'])} |")

# ---------------- coarse
p = R / "coarse_null.json"
if p.exists():
    d = json.loads(p.read_text())
    S["coarse"] = {}
    md.append("\n\n## 词类级 route 指纹（P(专家|UPOS)，Hungarian 留出相关；深层 L6–11 均值；N1 8 次的最小–最大）\n\n| 配对 | 真实 A–B | 真实 A–N1(B) [范围] | N1(A)–N1(B) | (真实 − A–N1(B)) / 真实 | 锚点 top-8 复算一致 |\n|---|---|---|---|---|---|")
    for r in d["results"]:
        L = r["layers"]
        real = np.mean([x["real"] for x in L]); nb = np.mean([x["nullB_mean"] for x in L])
        lo = np.mean([x["nullB_lo"] for x in L]); hi = np.mean([x["nullB_hi"] for x in L]); nab = np.mean([x["nullAB_mean"] for x in L])
        S["coarse"][f"{r['A']}:{r['B']}"] = {"real": real, "nullB": nb, "nullB_lo": lo, "nullB_hi": hi, "nullAB": nab}
        cf = R / "coarse_alignment_check.json"
        C = json.loads(cf.read_text()) if cf.exists() else {}
        chk = min([v for k in (r["A"], r["B"]) for v in C.get(k, {}).values()] or [float("nan")])
        md.append(f"| {r['A']}:{r['B']} | {f(real)} | {f(nb)} [{f(lo)}, {f(hi)}] | {f(nab)} | {f((real-nb)/real,2)} | {chk:.4f} |")

(R / "summary.json").write_text(json.dumps(S, indent=1, default=float))
(R / "summary.md").write_text("\n".join(md) + "\n")
print("\n".join(md))
