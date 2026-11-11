"""E187 读数 2/3/5 (weights): expert correspondences and weight drift between Qwen3-30B-A3B layers.
Inputs: ~/mechpop_cache/e187/w_<key>/ (from e187_weights.py).  For every layer pair (l, l+lag), lag in 1, 11, 12, 13, 24:
  - expert matching  pi_router : Hungarian on signed cosine of row-centred router rows (card primary)
                     pi_absraw : Hungarian on |cos| of raw router rows (E185x)
                     pi_expert : Hungarian on signed cosine of the concatenated expert sketch (gate/up/down)
  - matched cosines: router rows raw / effective (W diag g); expert gate/up/down sketch under pi_router and pi_expert;
    floor = random (unmatched) expert pairs (median, 99th pct)
  - attention q/k/v/o flattened cosine, q_norm/k_norm/post_ln/in_ln gain cosine; relative change ||B-A||/||A||
  - Base vs Instruct same-layer comparison (identity expert map) when both dumps exist.
Writes ~/mechpop_cache/e187/match_<key>.npz and results/e187/wdrift_<key>.json (+ base_vs_instruct.json)."""
import json, os, sys
import numpy as np
from scipy.optimize import linear_sum_assignment

C = os.path.expanduser("~/mechpop_cache/e187")
RES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results", "e187")
os.makedirs(RES, exist_ok=True)
L, E = 48, 128
LAGS = (1, 11, 12, 13, 24)
SEG = {"gate": slice(0, 65536), "up": slice(65536, 131072), "down": slice(131072, 196352)}   # reduced sketch (card deviation 22:50)
rng = np.random.default_rng(187)


def unit(X):
    return X / np.linalg.norm(X, axis=-1, keepdims=True)


def cos(a, b):
    a = a.ravel().astype(np.float64); b = b.ravel().astype(np.float64)
    return float(a @ b / np.linalg.norm(a) / np.linalg.norm(b))


def rel(a, b):
    a = a.ravel().astype(np.float64); b = b.ravel().astype(np.float64)
    return float(np.linalg.norm(b - a) / np.linalg.norm(a))


def hung(S):
    """S[i, j] similarity expert i of l vs expert j of m -> perm with perm[j] = matched expert of l."""
    r, c = linear_sum_assignment(-S)
    p = np.empty(E, np.int64); p[c] = r
    return p


def load(key):
    d = f"{C}/w_{key}"
    sm = dict(np.load(f"{d}/small.npz")); at = dict(np.load(f"{d}/attn.npz"))
    sk = [np.load(f"{d}/sketchS_L{l:02d}.npy", mmap_mode="r") for l in range(L)]
    return sm, at, sk


def analyse(key):
    sm, at, sk = load(key)
    G = sm["gate"].astype(np.float64)                       # [L, E, d]
    g = sm["post_ln"].astype(np.float64)                    # [L, d]
    Gc = unit(G - G.mean(1, keepdims=True)); Gr = unit(G)
    Geff = G * g[:, None, :]; Gec = unit(Geff - Geff.mean(1, keepdims=True))
    SK = {}
    for l in range(L):                                   # raw float32 sketches + per-segment norms, all in RAM
        X = np.asarray(sk[l], dtype=np.float32)
        SK[l] = {"X": X, **{"n_" + s: np.linalg.norm(X[:, sl].astype(np.float64), axis=1) for s, sl in SEG.items()},
                 "n_all": np.linalg.norm(X.astype(np.float64), axis=1)}

    def gram(l, m, s):
        sl = SEG.get(s, slice(None))
        M = (SK[l]["X"][:, sl] @ SK[m]["X"][:, sl].T).astype(np.float64)
        return M / np.outer(SK[l]["n_" + s], SK[m]["n_" + s])

    match, rows = {}, []
    for lag in LAGS:
        for l in range(L - lag):
            m = l + lag
            Sr = Gc[l] @ Gc[m].T
            pr = hung(Sr)
            pa = hung(np.abs(Gr[l] @ Gr[m].T))
            Se = gram(l, m, "all")
            pe = hung(Se)
            match[f"{l}_{m}_router"] = pr; match[f"{l}_{m}_absraw"] = pa; match[f"{l}_{m}_expert"] = pe
            j = np.arange(E)
            rec = dict(l=l, m=m, lag=lag,
                       router_cos_centred=float(Sr[pr, j].mean()),
                       router_cos_raw=float((Gr[l][pr] * Gr[m]).sum(1).mean()),
                       router_cos_eff=float((Gec[l][pr] * Gec[m]).sum(1).mean()),
                       router_cos_centred_under_expert_match=float(Sr[pe, j].mean()),
                       router_rel=float(np.linalg.norm(Geff[m] - Geff[l][pr]) / np.linalg.norm(Geff[l][pr])),
                       match_router_vs_expert=float((pr == pe).mean()),
                       match_router_vs_absraw=float((pr == pa).mean()))
            ri = rng.integers(0, E, (2000, 2))
            for s in ("gate", "up", "down", "all"):
                M = Se if s == "all" else gram(l, m, s)
                rec[f"exp_{s}_cos_routermatch"] = float(M[pr, j].mean())
                rec[f"exp_{s}_cos_expertmatch"] = float(M[pe, j].mean())
                fl = M[ri[:, 0], ri[:, 1]]
                rec[f"exp_{s}_floor_med"] = float(np.median(fl)); rec[f"exp_{s}_floor_p99"] = float(np.quantile(fl, .99))
            rec["exp_all_rel_routermatch"] = float(np.mean([rel(np.asarray(sk[l][pr[e]], np.float32),
                                                                np.asarray(sk[m][e], np.float32)) for e in range(0, E, 8)]))
            for p in "qkvo":
                rec[f"attn_{p}_cos"] = cos(at[p][l], at[p][m]); rec[f"attn_{p}_rel"] = rel(at[p][l], at[p][m])
            for n in ("q_norm", "k_norm", "post_ln", "in_ln"):
                rec[f"{n}_cos"] = cos(sm[n][l], sm[n][m]); rec[f"{n}_meanratio"] = float(sm[n][m].mean() / sm[n][l].mean())
            rows.append(rec)
            if lag == 12:
                print(key, l, m, {k: round(v, 3) for k, v in rec.items() if isinstance(v, float) and
                                  k in ("router_cos_centred", "exp_all_cos_routermatch", "exp_all_cos_expertmatch",
                                        "attn_q_cos", "match_router_vs_expert")}, flush=True)
    np.savez(f"{C}/match_{key}.npz", **match)
    # sketch-error check: second neuron subset of gate (rows 640:768) vs first (rows 0:128), lag-12 pairs (8,20),(20,32),(8,9)
    alt = np.load(f"{C}/w_{key}/sketchS_alt_gate640.npz")
    chk = {}
    for (l, m) in ((8, 20), (20, 32), (8, 32), (8, 9)):
        pr = match[f"{l}_{m}_router"]
        M1 = gram(l, m, "gate")
        a2, b2 = unit(alt[f"L{l}"].astype(np.float64)), unit(alt[f"L{m}"].astype(np.float64))
        chk[f"{l}_{m}"] = dict(rows0_32=float(M1[pr, np.arange(E)].mean()), rows640_672=float((a2[pr] * b2).sum(1).mean()))
    json.dump({"key": key, "rows": rows, "sketch_check": chk}, open(f"{RES}/wdrift_{key}.json", "w"), indent=0)
    return sm, at, SK


out = {}
for key in sys.argv[1:]:
    out[key] = analyse(key)
if "instruct" in out and "base" in out:
    (si, ai, ki), (sb, ab, kb) = out["instruct"], out["base"]
    rows = []
    for l in range(L):
        rec = dict(l=l, router_cos=float((unit(si["gate"][l].astype(np.float64)) * unit(sb["gate"][l].astype(np.float64))).sum(1).mean()),
                   router_rel=rel(sb["gate"][l], si["gate"][l]), post_ln_cos=cos(si["post_ln"][l], sb["post_ln"][l]))
        for p in "qkvo":
            rec[f"attn_{p}_cos"] = cos(ai[p][l], ab[p][l]); rec[f"attn_{p}_rel"] = rel(ab[p][l], ai[p][l])
        X, Y = ki[l]["X"], kb[l]["X"]
        rec["exp_all_cos"] = float((unit(X.astype(np.float64)) * unit(Y.astype(np.float64))).sum(1).mean())
        rec["exp_all_rel"] = float(np.linalg.norm(X - Y) / np.linalg.norm(Y))
        rows.append(rec)
    json.dump(rows, open(f"{RES}/base_vs_instruct.json", "w"), indent=0)
    print("base vs instruct", [round(r["exp_all_cos"], 4) for r in rows[::6]])
