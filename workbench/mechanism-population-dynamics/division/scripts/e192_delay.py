"""E192 POST-HOC readout (11-18, written after seeing round-3 NLL): horizontal delay.

For a perturbed arm X and its same-seed control R (free router), the delay at save
point c is c - t, where t solves R(t) = X(c) on R's held-out DCLM NLL curve (linear
interpolation between save points, 54 iters apart). A constant delay means X follows
R's loss curve shifted in time; the NLL difference then shrinks only because the curve
flattens. Reads results/e192/summary.json, writes results/e192/delay.md. CPU, seconds.
"""
import json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "results", "e192")
S = json.load(open(os.path.join(RES, "summary.json")))
CUR = S["nll"]["curves"]


def curve(a):
    return {int(c): v["dclm"][0] for c, v in CUR[a].items()} if a in CUR else None


def delays(x, r):
    its = sorted(r)
    v = np.array([r[i] for i in its])
    out = {}
    for c in sorted(x):
        if c == 0 or c not in r:
            continue
        y = x[c]
        if y > v[0] or y < v[-1]:      # outside the control's range: not invertible
            out[c] = (None, y - r[c])
            continue
        # control curves are not strictly monotone at every point (event bumps); use the
        # running minimum so the inverse is defined
        vm = np.minimum.accumulate(v)
        t = float(np.interp(-y, -vm, its))
        out[c] = (c - t, y - r[c])
    return out


# (arm, control, label, first save point used for the summary)
PAIRS = [
    ("C1", "A1", "重置全部路由器，种子 1", 216), ("C2", "A2", "重置全部路由器，种子 2", 216),
    ("CD_1", "A1", "只重置第 2–8 层，种子 1", 216), ("CD_2", "A2", "只重置第 2–8 层，种子 2", 216),
    ("CL1_1", "A1", "只重置第 1 个 MoE 层，种子 1", 162), ("CL1_2", "A2", "只重置第 1 个 MoE 层，种子 2", 162),
    ("B2", "A2", "冻结，iter 318–368 出事件", 486), ("A5", "A1", "自由，iter 371–393 出事件（对照用 A1，数据顺序不同）", 486),
    ("B1", "A1", "冻结，无事件", 162), ("B2r", "A2", "冻结，无事件", 162), ("G2", "A2", "冻结 aux 关，无事件", 162),
    ("B3", "A3", "冻结，无事件", 162), ("B4", "A4", "冻结，无事件", 162),
    ("A2", "A1", "自由 vs 自由（数据顺序）", 162), ("A3", "A1", "自由 vs 自由（数据顺序）", 162), ("A4", "A1", "自由 vs 自由（数据顺序）", 162),
    ("F", "A1", "只训路由器", 162),
]

L = ["# E192 延迟读数（POST-HOC，11-18；`scripts/e192_delay.py`；只用 summary.json 里的 DCLM 留出 NLL）", "",
     "延迟 = c − t，t 是同种子自由臂的留出 NLL 曲线上与该臂在 c 处的 NLL 相等的 iter（保存点之间线性插值，54 iter 一档）。"
     "每 iter 2.1M token。`—` = 该点 NLL 超出对照曲线的范围（事件中或重学瞬态）。", "",
     "## 汇总（从'起算点'到该臂最后一个保存点）", "",
     "| 臂 − 对照 | 处理 | 起算点 | 点数 | 延迟均值（iter） | 最小 … 最大 | 前半 / 后半均值 | 首点 NLL 差 → 末点 NLL 差 |", "|---|---|---|---|---|---|---|---|"]
detail = []
for a, r, lab, c0 in PAIRS:
    x, y = curve(a), curve(r)
    if x is None or y is None:
        continue
    d = delays(x, y)
    pts = [(c, dv, g) for c, (dv, g) in d.items() if c >= c0 and dv is not None]
    if not pts:
        continue
    dv = np.array([p[1] for p in pts])
    h = len(dv) // 2
    L.append(f"| {a} − {r} | {lab} | {c0} | {len(dv)} | {dv.mean():+.0f} | {dv.min():+.0f} … {dv.max():+.0f} | "
             f"{dv[:h].mean():+.0f} / {dv[h:].mean():+.0f} | {pts[0][2]:+.4f} → {pts[-1][2]:+.4f} |" if h else
             f"| {a} − {r} | {lab} | {c0} | {len(dv)} | {dv.mean():+.0f} | {dv.min():+.0f} … {dv.max():+.0f} | — | {pts[0][2]:+.4f} → {pts[-1][2]:+.4f} |")
    detail.append(f"- **{a} − {r}**（c : 延迟 : NLL 差）：" + "，".join(
        f"{c}:{'—' if v is None else format(v, '+.0f')}:{g:+.4f}" for c, (v, g) in d.items()))
L += ["", "## 逐点", ""] + detail + [""]
open(os.path.join(RES, "delay.md"), "w").write("\n".join(L))
print("\n".join(L[:len(PAIRS) + 12]))
