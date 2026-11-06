#!/usr/bin/env python3
"""E173 run 2 (11-06): recipe axis as init pair ÷ the recipe's own exact-rerun pair, at 8e8 (DIRECTION §14 pre-registration).
Inputs (no recomputation): results/e173/summary.json (init pairs, 15-pair ruler, held CE) and results/e173/rerun_ceiling.json
(rerun pairs; T_D via analyze_routing.py E167_NPERM=0, route fingerprint via analyze_functional.py route, deep = L6-11).
  16 experts : G16_I0–G16_I1 ÷ G16_I0–G16_I0R
  64 experts : init = 15-pair mean and I0D0–I1D0; rerun = I4D0–I4D0R and I0D0–BASE_I0 -> ratio reported as min–max over the 4 combos
               (route: I0D0–I1D0 ÷ I0D0–BASE_I0, the only 64e rerun pair with an 8e8 functional capture)
  256 experts: G256_I0–G256_I1 ÷ G256_I0–G256_I0R (appears once G256_I0R's captures land; "待 G256_I0R" until then)
  64 experts top-2 (control, 11-06 21:40 run 3): G64K2_I0–G64K2_I1 ÷ G64K2_I0–G64K2_I0R; the row is left out of the table
               and json until the G64K2 init pair or rerun pair has an 8e8 capture.
Writes results/e173/recipe_ratio.json and replaces the section "## 配方轴（init ÷ 重跑）" at the end of results/e173/table.md.
Usage: e173_recipe_ratio.py   (also called at the end of e173_compare.py, which rewrites table.md)
"""
import json
from pathlib import Path

WB = Path(__file__).resolve().parents[1]
OUT = WB / "results/e173"
E, Z = "800000000", "0"
HEAD = "## 配方轴（init ÷ 重跑）"
S = json.loads((OUT / "summary.json").read_text())
RC = json.loads((OUT / "rerun_ceiling.json").read_text())
rec, rule = S["recipes"], S["ruler_15pairs"][E]


def init_vals(name):
    r = rec.get(name)
    if not r or E not in r["routing"]:
        return None
    t = r["routing"][E]
    return {"L11": t["L11"], "deep": t["deep"], "route": r["route_fp"]["deep_matched"] if r["route_fp"] else None}


def rerun_vals(pair, t=E):
    v = RC.get(pair, {}).get(t)
    return None if v is None else {"L11": v["L11"], "deep": v["deep"], "route": v["route_deep"]}


def held(name, run):
    r = rec.get(name)
    h = r["health"].get(run) if r else None
    return h["held_ce_3000"] if h else None


# hand-written after the 16e rerun landed (11-06 20:55); 16 vs 64 only — superseded once the 256e rerun pair exists
VERDICT_16_64 = ("16 专家的比值 L11 .13 / 深层 .10（指纹 .69），远低于 64 专家的 .44–.53 / .40–.41（指纹 .83），而 16 专家的重跑上限 .45 / .34 与 64 专家的 .44–.50 / .40 "
                 "同一量级——16 专家处跨 init T_D 低不是读数量纲造成的，\"初始化拿走约一半\"在 16 专家上不成立，按 §14 属于\"比值随专家数变\"那一支。"
                 "是否单调、专家数是否是真正的轴，要等 256 专家点（**待 G256_I0R**，约 11-07 04:20 训完）；只有两点时不下结论。")
rows = {}
OPTIONAL = {"64k2"}  # rows skipped entirely while their captures are missing
RERUN_RUN = {16: "G16_I0R", 256: "G256_I0R", "64k2": "G64K2_I0R"}
for ne, iname, rpair, rname, runs in [(16, "g16", "G16_I0-G16_I0R", "g16r", ("G16_I0", "G16_I1", "G16_I0R")),
                                      (256, "g256", "G256_I0-G256_I0R", "g256r", ("G256_I0", "G256_I1", "G256_I0R")),
                                      ("64k2", "g64k2", "G64K2_I0-G64K2_I0R", "g64k2r", ("G64K2_I0", "G64K2_I1", "G64K2_I0R"))]:
    i, r = init_vals(iname), rerun_vals(rpair)
    if ne in OPTIONAL and not (i or r):
        continue
    ratio = None if not (i and r) else {k: (i[k] / r[k] if i[k] is not None and r[k] is not None else None) for k in ("L11", "deep", "route")}
    rows[ne] = {"init": i, "rerun": r, "rerun_step0": rerun_vals(rpair, Z), "ratio_lo": ratio, "ratio_hi": ratio,
                "held_3000": {runs[0]: held(iname, runs[0]), runs[1]: held(iname, runs[1]), runs[2]: held(rname, runs[2])}}
# 64 experts: two init numerators x two rerun denominators
b = init_vals("base")
nums = {"15 对均值": {"L11": rule["L11"][1], "deep": rule["deep"][1]}, "I0D0–I1D0": b}
dens = {p: rerun_vals(p) for p in ("I4D0-I4D0R", "I0D0-BASE_I0")}
comb = {k: [nums[n][k] / dens[d][k] for n in nums for d in dens] for k in ("L11", "deep")}
r64 = b["route"] / dens["I0D0-BASE_I0"]["route"]
rows[64] = {"init": {"L11": [rule["L11"][1], b["L11"]], "deep": [rule["deep"][1], b["deep"]], "route": b["route"]},
            "rerun": {"L11": [dens[d]["L11"] for d in dens], "deep": [dens[d]["deep"] for d in dens], "route": dens["I0D0-BASE_I0"]["route"]},
            "rerun_step0": {"I4D0-I4D0R": rerun_vals("I4D0-I4D0R", Z), "I0D0-BASE_I0": rerun_vals("I0D0-BASE_I0", Z)},
            "ratio_lo": {"L11": min(comb["L11"]), "deep": min(comb["deep"]), "route": r64},
            "ratio_hi": {"L11": max(comb["L11"]), "deep": max(comb["deep"]), "route": r64}}
ORDER = [16, 64, 256, "64k2"]
(OUT / "recipe_ratio.json").write_text(json.dumps({str(k): rows[k] for k in ORDER if k in rows}, indent=1))

f3 = lambda x: "—" if x is None else f"{x:.3f}"
f2 = lambda x: "—" if x is None else f"{x:.2f}"
rng = lambda lo, hi: f2(lo) if lo is None or abs(lo - hi) < 5e-3 else f"{lo:.2f}–{hi:.2f}"
span = lambda xs: f"{min(xs):.3f}–{max(xs):.3f}" if max(xs) - min(xs) >= 5e-4 else f"{xs[0]:.3f}"
L = [HEAD, "",
     "比值 = 只换初始化对 ÷ 同配方精确重跑对，8 亿 token；T_D 用 analyze_routing.py（E167_NPERM=0），指纹 = route 深层匹配相关（analyze_functional.py route）。"
     "64 专家分子取 15 对均值与 I0D0–I1D0，分母取 I4D0–I4D0R（A100 / A100）与 I0D0–BASE_I0（RTX / A100），比值报四种组合的范围；指纹分母只有 I0D0–BASE_I0。",
     "", "| 专家数 top-k | init L11 / 深层 / 指纹 | 重跑 L11 / 深层 / 指纹 | 重跑 step-0 L11 / 深层 | **比值 L11 / 深层 / 指纹** |", "|---|---|---|---|---|"]
for ne, lab in [(16, "16 top-2"), (64, "64 top-8"), (256, "256 top-32"), ("64k2", "64 top-2（对照）")]:
    if ne not in rows:
        continue
    r = rows[ne]
    if ne == 64:
        i, d = r["init"], r["rerun"]
        ic = f"{span(i['L11'])} / {span(i['deep'])} / {f3(i['route'])}"
        dc = f"{span(d['L11'])} / {span(d['deep'])} / {f3(d['route'])}"
        s0 = [v for v in r["rerun_step0"].values() if v]
        zc = f"{span([v['L11'] for v in s0])} / {span([v['deep'] for v in s0])}"
    else:
        i, d, z = r["init"], r["rerun"], r["rerun_step0"]
        ic = "—" if not i else f"{f3(i['L11'])} / {f3(i['deep'])} / {f3(i['route'])}"
        dc = f"待 {RERUN_RUN[ne]}" if not d else f"{f3(d['L11'])} / {f3(d['deep'])} / {f3(d['route'])}"
        zc = "—" if not z else f"{f3(z['L11'])} / {f3(z['deep'])}"
    lo, hi = r["ratio_lo"], r["ratio_hi"]
    rc = f"待 {RERUN_RUN[ne]}" if not lo else " / ".join(rng(lo[x], hi[x]) for x in ("L11", "deep", "route"))
    L.append(f"| {lab} | {ic} | {dc} | {zc} | **{rc}** |")
h16 = rows[16]["held_3000"]
L += ["", "留出 CE @3000 步：" + "，".join(f"{k} {f3(v)}" for k, v in h16.items())
      + ("" if not rows[256]["rerun"] else "；" + "，".join(f"{k} {f3(v)}" for k, v in rows[256]["held_3000"].items()))
      + ("" if "64k2" not in rows else "；64 top-2 对照（active 参数为基线 1/4，CE 不与基线比）"
         + "，".join(f"{k} {f3(v)}" for k, v in rows["64k2"]["held_3000"].items())) + "。"]
L += ["", "**对 §14 预登记的判读：** " + (
    "（256 专家点已到，判读待主会话按三点重写。）" if rows[256]["rerun"] else
    VERDICT_16_64)]
txt = (OUT / "table.md").read_text()
txt = txt.split("\n" + HEAD)[0].rstrip("\n") + "\n\n" + "\n".join(L) + "\n"
(OUT / "table.md").write_text(txt)
print("\n".join(L))
