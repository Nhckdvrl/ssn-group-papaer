"""E187 读数 2/3 without the expert sketch (11-10 04:50, NFS at ~70 kB/s made the expert sketch unreadable tonight):
router rows (centred / raw / effective W*g, matched by the card rule), attention q/k/v/o flattened cosine and
relative change, RMSNorm / q_norm / k_norm gains, for copy pairs and lag 1/11/13 references, Instruct and Base, plus
the three-block lineage (star decomposition) and Base-vs-Instruct same-layer weights.  Expert gate/up/down drift is
left to e187_wdrift.py once the sketches exist.  Writes results/e187/wdrift_lite.json and appends to tables.md."""
import json, os
import numpy as np
from scipy.optimize import linear_sum_assignment

C = os.path.expanduser("~/mechpop_cache/e187")
RES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results", "e187")
L, E = 48, 128
BP = {"B1↔B2": (12, range(6, 18)), "B2↔B3": (12, range(18, 30)), "B1↔B3": (24, range(6, 18))}


def unit(X):
    return X / np.linalg.norm(X, axis=-1, keepdims=True)


def cos(a, b):
    a = a.ravel().astype(np.float64); b = b.ravel().astype(np.float64)
    return float(a @ b / np.linalg.norm(a) / np.linalg.norm(b))


def rel(a, b):
    a = a.ravel().astype(np.float64); b = b.ravel().astype(np.float64)
    return float(np.linalg.norm(b - a) / np.linalg.norm(a))


M = {}
for key in ("instruct", "base"):
    sm = dict(np.load(f"{C}/w_{key}/small.npz")); at = dict(np.load(f"{C}/w_{key}/attn.npz"))
    G = sm["gate"].astype(np.float64); g = sm["post_ln"].astype(np.float64)
    Gc = unit(G - G.mean(1, keepdims=True)); Gr = unit(G); Ge = G * g[:, None, :]; Gec = unit(Ge - Ge.mean(1, keepdims=True))
    rows = []
    for lag in (12, 24, 1, 11, 13):
        for l in range(L - lag):
            m = l + lag
            if lag in (1, 11, 13) and not (6 <= l and m <= 41):
                continue
            S = Gc[l] @ Gc[m].T
            r, c = linear_sum_assignment(-S); p = np.empty(E, np.int64); p[c] = r
            j = np.arange(E)
            ri = np.random.default_rng(l * 100 + m).integers(0, E, (4000, 2))
            rec = dict(l=l, m=m, lag=lag, router_cos_centred=float(S[p, j].mean()),
                       router_floor_p99=float(np.quantile(S[ri[:, 0], ri[:, 1]], .99)),
                       router_cos_raw=float((Gr[l][p] * Gr[m]).sum(1).mean()),
                       router_cos_eff=float((Gec[l][p] * Gec[m]).sum(1).mean()),
                       router_rel=float(np.linalg.norm(Ge[m] - Ge[l][p]) / np.linalg.norm(Ge[l][p])),
                       match_identity=float((p == j).mean()))
            for q in "qkvo":
                rec[f"attn_{q}_cos"] = cos(at[q][l], at[q][m]); rec[f"attn_{q}_rel"] = rel(at[q][l], at[q][m])
            for n in ("post_ln", "in_ln", "q_norm", "k_norm"):
                rec[f"{n}_cos"] = cos(sm[n][l], sm[n][m])
            rows.append(rec)
    M[key] = dict(rows=rows, sm=sm, at=at)
    print(key, "done", flush=True)

out, summ = [], {}
f3 = lambda x: f"{x:.3f}"
cols = [("router_cos_centred", "路由器行 cos（中心化，配对）"), ("router_cos_eff", "有效路由器 W·g"), ("router_floor_p99", "未配对行 p99"),
        ("match_identity", "配对 = 同编号的比例"), ("attn_q_cos", "q"), ("attn_k_cos", "k"), ("attn_v_cos", "v"), ("attn_o_cos", "o"),
        ("post_ln_cos", "post-ln 增益"), ("router_rel", "相对变化 路由器"), ("attn_q_rel", "相对变化 q"), ("attn_o_rel", "相对变化 o")]
for key in ("instruct", "base"):
    rows = M[key]["rows"]
    out += [f"## 2'. 权重漂移（{key}；不含专家——专家草图因 NFS 未读完，见卡）", "", "| 对 | " + " | ".join(c[1] for c in cols) + " |",
            "|---|" + "---|" * len(cols)]
    for n, (lag, ls) in list(BP.items()) + [("lag 1", (1, None)), ("lag 11", (11, None)), ("lag 13", (13, None))]:
        rr = [r for r in rows if r["lag"] == lag and (ls is None or r["l"] in ls)]
        out.append(f"| {n} | " + " | ".join(f3(np.mean([r[c] for r in rr])) for c, _ in cols) + " |")
        summ[f"{key}_{n}"] = {c: float(np.mean([r[c] for r in rr])) for c, _ in cols}
    out += ["", f"谱系（{key}）：三块成对余弦与星形分解 a_i = √(cos_ij·cos_ik/cos_jk)，逐块内位置平均", "",
            "| 读数 | cos(B1,B2) | cos(B2,B3) | cos(B1,B3) | a1 | a2 | a3 | cos(B1,B3) 最低的位置数 |", "|---|---|---|---|---|---|---|---|"]
    for c in ("router_cos_centred", "attn_q_cos", "attn_k_cos", "attn_v_cos", "attn_o_cos"):
        v12 = np.array([r[c] for r in rows if r["lag"] == 12 and r["l"] in range(6, 18)])
        v23 = np.array([r[c] for r in rows if r["lag"] == 12 and r["l"] in range(18, 30)])
        v13 = np.array([r[c] for r in rows if r["lag"] == 24 and r["l"] in range(6, 18)])
        a1 = np.sqrt(v12 * v13 / v23); a2 = np.sqrt(v12 * v23 / v13); a3 = np.sqrt(v13 * v23 / v12)
        k = int(np.sum((v13 < v12) & (v13 < v23)))
        out.append(f"| {c} | {v12.mean():.3f} | {v23.mean():.3f} | {v13.mean():.3f} | {a1.mean():.3f} | {a2.mean():.3f} | {a3.mean():.3f} | {k}/12 |")
        summ[f"lineage_{key}_{c}"] = dict(c12=float(v12.mean()), c23=float(v23.mean()), c13=float(v13.mean()),
                                          a1=float(a1.mean()), a2=float(a2.mean()), a3=float(a3.mean()), n_c13_lowest=k)
    out.append("")
si, sb = M["instruct"]["sm"], M["base"]["sm"]; ai, ab = M["instruct"]["at"], M["base"]["at"]
bv = []
for l in range(L):
    bv.append(dict(l=l, router_cos=float((unit(si["gate"][l].astype(np.float64)) * unit(sb["gate"][l].astype(np.float64))).sum(1).mean()),
                   router_rel=rel(sb["gate"][l], si["gate"][l]), q_cos=cos(ai["q"][l], ab["q"][l]), q_rel=rel(ab["q"][l], ai["q"][l]),
                   o_cos=cos(ai["o"][l], ab["o"][l]), o_rel=rel(ab["o"][l], ai["o"][l])))
out += ["### Base vs Instruct 同层权重（后训练改了多少）", "", "| 层段 | 路由器行 cos | 相对变化 | q cos | 相对变化 | o cos | 相对变化 |", "|---|---|---|---|---|---|---|"]
for nm, ls in (("0–5", range(6)), ("6–41", range(6, 42)), ("42–47", range(42, 48))):
    rr = [r for r in bv if r["l"] in ls]
    out.append(f"| {nm} | " + " | ".join(f"{np.mean([r[k] for r in rr]):.4f}" for k in ("router_cos", "router_rel", "q_cos", "q_rel", "o_cos", "o_rel")) + " |")
json.dump({"rows": {k: v["rows"] for k, v in M.items()}, "base_vs_instruct": bv, "summary": summ},
          open(f"{RES}/wdrift_lite.json", "w"), indent=0, ensure_ascii=False)
open(f"{RES}/tables_wdrift_lite.md", "w").write("# E187 权重漂移（不含专家，`e187_wdrift_lite.py`）\n\n" + "\n".join(out) + "\n")
print("\n".join(out))
