#!/usr/bin/env python3
"""E192 p6 diagnostic (POST-HOC, 11-18; CPU only): where does "our continuation is ~.05 nat better than the official
checkpoint at the same token count" sit?  From saved per-token held-out NLL arrays only:
 (a) by document structure: target = EOD; target is document token 1 / 2-8 / 9-64 / >64 after the last EOD in the window;
     no EOD earlier in the window (document began before the window);
 (b) by window position; (c) by target-token frequency quintile (P1 counts, first 1e8 tokens);
 (d) over save points: A(c) - linear interpolation of official 1080 -> 1620 (rough), overall and per class (a).
Streams: our held-out stream (gs10, 1024 windows; arms' nll_cXXXX.npz and official/i*/nll.npz) and the third-shard stream
(gs05; p6/*_nll.npz).  Writes ROOT/p6/p6_diag.json and p6_diag.md (included into tables.md by e192_analyze.py).
usage: nice -n 19 python e192_p6diag.py --ana /tmp/xiang_e192/analysis --root /tmp/xiang_e192"""
import argparse, json, os
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--ana", default="/tmp/xiang_e192/analysis"); ap.add_argument("--root", default="/tmp/xiang_e192")
a = ap.parse_args()
SEQ, EOD = 2048, 0
R = a.root


def windows(f):
    x = np.fromfile(f, np.uint16); n = (len(x) - 1) // SEQ
    return np.stack([x[j * SEQ:j * SEQ + SEQ + 1] for j in range(n)]).astype(np.int64)


cnt = np.bincount(np.fromfile(f"{R}/dclm/pool_P1.u16", np.uint16, count=100_000_000), minlength=50304).astype(np.float64)


def classes(W):
    inp, tgt = W[:, :-1], W[:, 1:]
    pos = np.broadcast_to(np.arange(SEQ), inp.shape)
    last = np.where(inp == EOD, pos, -1); last = np.maximum.accumulate(last, axis=1)   # last EOD position in input <= j
    t = pos - last                                    # 0: input is EOD -> target is doc token 1
    seen = last >= 0
    C = {"target = EOD": tgt == EOD,
         "doc token 1 (input = EOD)": seen & (t == 0) & (tgt != EOD),
         "doc tokens 2-8": seen & (t >= 1) & (t <= 7) & (tgt != EOD),
         "doc tokens 9-64": seen & (t >= 8) & (t <= 63) & (tgt != EOD),
         "doc tokens > 64": seen & (t >= 64) & (tgt != EOD),
         "no EOD earlier in window": ~seen & (tgt != EOD)}
    P = {"window pos 0": pos == 0, "pos 1-15": (pos >= 1) & (pos < 16), "pos 16-127": (pos >= 16) & (pos < 128),
         "pos 128-511": (pos >= 128) & (pos < 512), "pos 512-2047": pos >= 512}
    fq = cnt[tgt]; qs = np.quantile(fq, [.2, .4, .6, .8]); q = np.searchsorted(qs, fq, side="right")
    Q = {f"freq q{i + 1}": q == i for i in range(5)}
    return C, P, Q


rng = np.random.default_rng(1923)


def ci(dv, m):
    s = (dv * m).sum(1); n = m.sum(1).astype(np.float64); bi = rng.integers(0, len(s), (1000, len(s)))
    b = s[bi].sum(1) / np.maximum(n[bi].sum(1), 1)
    tot = float(s.sum() / max(n.sum(), 1))
    return {"mean": tot, "lo": float(np.quantile(b, .025)), "hi": float(np.quantile(b, .975)), "n": int(n.sum()),
            "share_of_total_gap": float(s.sum() / dv.size)}


def load(path, key):
    return np.load(path)[key].astype(np.float64)


out = {"streams": {}}
W10 = windows(f"{R}/dclm/eval_dclm.u16"); C10 = classes(W10)
W05 = windows(f"{R}/dclm/eval_dclm3.u16") if os.path.exists(f"{R}/dclm/eval_dclm3.u16") else None
A = f"{a.ana}/arms"
comps = {"gs10: A1@1620 − off1620": (load(f"{A}/A1/nll_c0540.npz", "dclm"), load(f"{R}/official/i1620/nll.npz", "dclm"), C10),
         "gs10: A2@1620 − off1620": (load(f"{A}/A2/nll_c0540.npz", "dclm"), load(f"{R}/official/i1620/nll.npz", "dclm"), C10),
         "gs10: A1@2160 − off2160": (load(f"{A}/A1/nll_c1080.npz", "dclm"), load(f"{R}/official/i2160/nll.npz", "dclm"), C10),
         "gs10: E@1080 − off1080": (load(f"{A}/E/nll_c0540.npz", "dclm"), load(f"{R}/official/i1080/nll.npz", "dclm"), C10),
         "gs10: off1620 − off1080 (official's own progress, for scale)": (load(f"{R}/official/i1620/nll.npz", "dclm"), load(f"{R}/official/i1080/nll.npz", "dclm"), C10)}
if W05 is not None and os.path.exists(f"{R}/p6/A1_c0540_nll.npz"):
    C05 = classes(W05)
    comps["gs05: A1@1620 − off1620"] = (load(f"{R}/p6/A1_c0540_nll.npz", "dclm_gs05"), load(f"{R}/p6/off1620_nll.npz", "dclm_gs05"), C05)
    comps["gs05: A2@1620 − off1620"] = (load(f"{R}/p6/A2_c0540_nll.npz", "dclm_gs05"), load(f"{R}/p6/off1620_nll.npz", "dclm_gs05"), C05)
for name, (x, y, (C, P, Q)) in comps.items():
    dv = x - y
    out["streams"][name] = {"total": float(dv.mean()), "by_doc": {k: ci(dv, m) for k, m in C.items()},
                            "by_pos": {k: ci(dv, m) for k, m in P.items()}, "by_freq": {k: ci(dv, m) for k, m in Q.items()}}
# (d) over save points: A(c) - linear interpolation official 1080 -> 1620, per doc class
o0, o1 = load(f"{R}/official/i1080/nll.npz", "dclm"), load(f"{R}/official/i1620/nll.npz", "dclm")
C, P, Q = C10
out["curve"] = {}
for arm in ("A1", "A2", "B1", "P6GS03"):
    rows = {}
    for c in range(0, 541, 54):
        f = f"{A}/{arm}/nll_c{c:04d}.npz"
        if not os.path.exists(f):
            continue
        dv = load(f, "dclm") - (o0 + (o1 - o0) * c / 540)
        rows[str(c)] = {"total": float(dv.mean()), **{k: float((dv * m).sum() / max(m.sum(), 1)) for k, m in C.items()}}
    out["curve"][arm] = rows
# round 3 p6 test: continuation on the official data (gs03) at c54 / c108 vs the official interpolation, both streams
out["gs03_test"] = {}
if os.path.exists(f"{R}/p6/off1080_nll.npz"):
    q0, q1 = load(f"{R}/p6/off1080_nll.npz", "dclm_gs05"), load(f"{R}/p6/off1620_nll.npz", "dclm_gs05")
    for c in (54, 108):
        f = f"{R}/p6/P6GS03_c{c:04d}_nll.npz"
        if os.path.exists(f):
            z = np.load(f)
            out["gs03_test"][f"c{c}"] = {"gs10_minus_interp": float((z["dclm_gs10"].astype(np.float64) - (o0 + (o1 - o0) * c / 540)).mean()),
                                         "gs05_minus_interp": float((z["dclm_gs05"].astype(np.float64) - (q0 + (q1 - q0) * c / 540)).mean())}
            fa = f"{A}/A1/nll_c{c:04d}.npz"
            if os.path.exists(fa):
                out["gs03_test"][f"c{c}"]["gs10_minus_A1"] = float((z["dclm_gs10"].astype(np.float64) - load(fa, "dclm")).mean())
json.dump(out, open(f"{R}/p6/p6_diag.json", "w"), indent=1, ensure_ascii=False)

T = ["### R6′ (p6) 诊断：续训比官方低的那 .05 nat 落在哪些 token 上（POST-HOC，11-18；只用已保存的逐 token NLL；"
     "\"占总差\" = 该类贡献 / 全部 token 的平均差）\n"]
for grp, lab in (("by_doc", "文档结构"), ("by_pos", "窗口位置"), ("by_freq", "目标 token 频率五分位")):
    names = list(next(iter(out["streams"].values()))[grp])
    T.append(f"**{lab}**（均值 [95% CI]；括号内 = token 数 / 占总差）\n")
    T.append("| 对比 | 总差 | " + " | ".join(names) + " |\n|" + "---|" * (len(names) + 2))
    for name, v in out["streams"].items():
        T.append(f"| {name} | {v['total']:+.4f} | " + " | ".join(
            f"{v[grp][k]['mean']:+.4f} [{v[grp][k]['lo']:+.4f}, {v[grp][k]['hi']:+.4f}] ({v[grp][k]['n']} / {v[grp][k]['share_of_total_gap']:+.4f})" for k in names) + " |")
    T.append("")
T.append("**差距何时出现**：A(c) − 官方 1080→1620 线性插值（粗；官方损失曲线是凹的，插值偏高，所以中间点的差被高估、两端准确）\n")
names = ["total"] + list(C)
T.append("| 臂 | c | " + " | ".join(names) + " |\n|" + "---|" * (len(names) + 2))
for arm, rows in out["curve"].items():
    for c, r in rows.items():
        T.append(f"| {arm} | {c} | " + " | ".join(f"{r[k]:+.4f}" for k in names) + " |")
if out["gs03_test"]:
    T.append("\n**p6 检验（第三轮）：用官方训练数据（gs03）从 S 续训**——相对官方 1080→1620 线性插值的差（gs10 / gs05），及与 A1 同点之差（gs10）\n")
    for k, v in out["gs03_test"].items():
        T.append(f"- {k}: " + "，".join(f"{kk} {vv:+.4f}" for kk, vv in v.items()))
open(f"{R}/p6/p6_diag.md", "w").write("\n".join(T) + "\n")
print("\n".join(T))
