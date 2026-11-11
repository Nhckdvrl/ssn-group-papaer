"""E187 读数 1 + 4 (toksub part) + geometry floor: cross-application decomposition of the routing divergence between
Qwen3-30B-A3B layers l and m = l+lag on the E179 token-level router inputs (20 languages x 1000 tokens, all 48 layers).
  h_l = g_l * xhat_l  (g = post-attention RMSNorm gain).  T_l(x) = top8(W_l x).
  O  = T_l(h_l)            vs pi T_m(h_m)             observed
  H  = T_l(h_l)            vs T_l(g_l * xhat_m)        same (effective) router, hidden-state drift only   [primary]
  R  = T_l(g_l * xhat_m)   vs pi T_m(h_m)             same input xhat_m, router drift only               [primary]
  R' = T_l(h_l)            vs pi T_m(g_m * xhat_l)     same input xhat_l, router drift only               [primary]
  H2/R2/R'2: gain assigned to the hidden state (raw h fed to the other layer's W)                       [secondary]
  geometry floor: one shared random router on xhat_l and xhat_m (N_A = Weff Q Haar, N_B = N1 + load-matched bias
  fitted on xhat_l, N_G = iid Gaussian rows with Weff's row norms); 8 draws each.
Floors: token-shuffle expectation, random expert permutation (200). CIs: sentence-cluster bootstrap (1000).
Expert map pi from e187_wdrift.py (router-row matching; alternatives absraw / expert reported too).
Writes results/e187/decomp.json and ~/mechpop_cache/e187/agree_<l>_<m>.npz (per-token agreement for copy pairs)."""
import json, os, sys, time
import numpy as np
import torch

torch.set_num_threads(int(os.environ.get("NT", 20)))
C = os.path.expanduser("~/mechpop_cache/e187")
RES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results", "e187")
L, E, K, N = 48, 128, 8, 20000
LAGS = [int(x) for x in os.environ.get("LAGS", "12,24,1,11,13").split(",")]
t0 = time.time()
sm = np.load(f"{C}/w_instruct/small.npz")
W = torch.tensor(sm["gate"], dtype=torch.float32)            # [L, E, d]
g = torch.tensor(sm["post_ln"], dtype=torch.float32)         # [L, d]
gw = np.load("/home/xiang/mechpop_cache/e179/qwen3/gateW.npy")
assert np.abs(gw - sm["gate"]).max() < 1e-6, "router weights differ from E179 gateW"
print("min |g|", float(g.abs().min()), flush=True)
from scipy.optimize import linear_sum_assignment
_G = sm["gate"].astype(np.float64)
_Gc = _G - _G.mean(1, keepdims=True); _Gc /= np.linalg.norm(_Gc, axis=2, keepdims=True)
_Gr = _G / np.linalg.norm(_G, axis=2, keepdims=True)
_ME = dict(np.load(f"{C}/match_instruct.npz")) if os.path.exists(f"{C}/match_instruct.npz") else {}


def _hung(S):
    r, c = linear_sum_assignment(-S)
    p = np.empty(E, np.int64); p[c] = r
    return p


class _Match(dict):
    """router-row matchings computed here (identical rule to e187_wdrift.py); expert-sketch matching read from file."""
    def __missing__(self, k):
        l, m, kind = k.split("_")
        l, m = int(l), int(m)
        if kind == "router":
            v = _hung(_Gc[l] @ _Gc[m].T)
        elif kind == "absraw":
            v = _hung(np.abs(_Gr[l] @ _Gr[m].T))
        else:
            v = _ME[k]
        self[k] = v
        return v


match = _Match()
ids = np.load("/home/xiang/mechpop_cache/atlas_e185/toksub_ids_qwen3.npz")
clus = ids["lang"] * 10000 + ids["sid"]
_, clus = np.unique(clus, return_inverse=True)
NC = clus.max() + 1
TS = np.load("/home/xiang/mechpop_cache/e179/qwen3/toksub.npy", mmap_mode="r")
Hs = {}


def h(l):
    if l not in Hs:
        Hs[l] = torch.tensor(np.asarray(TS[l], dtype=np.float32))
    return Hs[l]


def top(x, Wm, b=None):
    z = x @ Wm.T
    if b is not None:
        z = z + b
    return z.topk(K, -1).indices


def agree_vec(A, B, perm=None):
    """per-token top-1 agreement and top-8 overlap; B's expert ids mapped through perm (expert of m -> of l)."""
    if perm is not None:
        B = perm[B]
    t1 = (A[:, 0] == B[:, 0]).float()
    MA = torch.zeros(A.shape[0], E).scatter_(1, A, 1.0)
    ov = MA.gather(1, B).sum(1) / K
    return t1.numpy(), ov.numpy()


def chance(A, B, perm):
    B = perm[B]
    pa = torch.bincount(A[:, 0], minlength=E).double() / N; pb = torch.bincount(B[:, 0], minlength=E).double() / N
    fa = torch.bincount(A.reshape(-1), minlength=E).double() / N; fb = torch.bincount(B.reshape(-1), minlength=E).double() / N
    return float((pa * pb).sum()), float((fa * fb).sum() / K)


def perm_floor(A, B, n=200, seed=0):
    """agreement under random expert permutations: via joint tables."""
    J1 = torch.zeros(E, E, dtype=torch.float64).index_put_((A[:, 0], B[:, 0]), torch.ones(N, dtype=torch.float64), accumulate=True)
    MA = torch.zeros(N, E, dtype=torch.float64).scatter_(1, A, 1.0); MB = torch.zeros(N, E, dtype=torch.float64).scatter_(1, B, 1.0)
    J8 = MA.T @ MB
    gen = torch.Generator().manual_seed(seed)
    a1, a8 = [], []
    for _ in range(n):
        p = torch.randperm(E, generator=gen)            # expert j of m -> p[j] of l
        a1.append(float(J1[p, torch.arange(E)].sum() / N)); a8.append(float(J8[p, torch.arange(E)].sum() / N / K))
    return float(np.mean(a1)), float(np.quantile(a1, .99)), float(np.mean(a8)), float(np.quantile(a8, .99))


rng_b = np.random.default_rng(1870)
BOOT = [np.bincount(rng_b.integers(0, NC, NC), minlength=NC) for _ in range(1000)]


def ci(v):
    s = np.bincount(clus, v, NC); c = np.bincount(clus, None, NC)
    bs = [float((w * s).sum() / (w * c).sum()) for w in BOOT]
    return [float(np.quantile(bs, .025)), float(np.quantile(bs, .975))]


# ---------------------------------------------------------------- shared random routers (geometry floor)
D = 8
genQ = torch.Generator().manual_seed(187)
QA = []
for _ in range(D):
    A_ = torch.randn(2048, 2048, generator=genQ, dtype=torch.float64)
    Q_, R_ = torch.linalg.qr(A_)
    QA.append((Q_ * torch.sign(torch.diagonal(R_))).float())
print("haar ready", round(time.time() - t0), flush=True)


def fit_bias(Z, target, iters=200, lr=0.5):
    b = torch.zeros(E, dtype=Z.dtype); scale = Z.std(); tgt = target / target.sum()
    for _ in range(iters):
        f = torch.bincount(Z.add(b).topk(K, -1).indices.reshape(-1), minlength=E).to(Z.dtype)
        f = f / f.sum()
        b = b + lr * scale * (tgt - f) / (tgt + 1e-3)
    return b


def random_routers(l):
    """24 shared random routers built from layer l's effective router (act on xhat)."""
    Weff = (W[l] * g[l]).double()
    out = []
    for j in range(D):
        out.append(("N_A", (Weff.float() @ QA[j]), None))
    Wc = Weff - Weff.mean(0, keepdim=True)
    U, S, Vh = torch.linalg.svd(Wc, full_matrices=False)
    r = int((S > 1e-6 * S[0]).sum()); V = Vh[:r].T
    xl = (h(l) / g[l]).double()
    target = torch.bincount(top(xl, Weff).reshape(-1), minlength=E).double()
    gen = torch.Generator().manual_seed(18700 + l)
    for j in range(D):
        A_ = torch.randn(r, r, generator=gen, dtype=torch.float64)
        Q_, R_ = torch.linalg.qr(A_); Q_ = Q_ * torch.sign(torch.diagonal(R_))
        Wn = (U[:, :r] * S[:r]) @ Q_ @ V.T
        bn = fit_bias(xl @ Wn.T, target)
        out.append(("N_B", Wn.float(), bn.float()))
    rn = Weff.norm(dim=1, keepdim=True)
    for j in range(D):
        Gm = torch.randn(E, 2048, generator=gen, dtype=torch.float64)
        out.append(("N_G", (Gm / Gm.norm(dim=1, keepdim=True) * rn).float(), None))
    return out


TOP = {}


def T_self(l):
    if l not in TOP:
        TOP[l] = top(h(l), W[l])
    return TOP[l]


res = []
pairs = [(l, l + lag) for lag in LAGS for l in range(L - lag)]
for (l, m) in pairs:
    xl, xm = h(l) / g[l], h(m) / g[m]
    A = T_self(l); B = T_self(m)
    Cp = top(xm * g[l], W[l]); Cs = top(h(m), W[l])
    Dp = top(xl * g[m], W[m]); Ds = top(h(l), W[m])
    rec = dict(l=l, m=m, lag=m - l)
    vecs = {}
    for mk in ("router", "absraw") + (("expert",) if _ME else ()):
        perm = torch.tensor(match[f"{l}_{m}_{mk}"])
        defs = {"O": (A, B, perm), "H": (A, Cp, None), "R": (Cp, B, perm), "Rp": (A, Dp, perm),
                "H2": (A, Cs, None), "R2": (Cs, B, perm), "Rp2": (A, Ds, perm)}
        if mk != "router":
            defs = {k: v for k, v in defs.items() if k in ("O", "R", "Rp")}
        for k, (X, Y, p) in defs.items():
            t1, ov = agree_vec(X, Y, p)
            suf = "" if mk == "router" else "_" + mk
            rec[f"{k}{suf}_top1"] = float(t1.mean()); rec[f"{k}{suf}_top8"] = float(ov.mean())
            if mk == "router":
                vecs[k] = (t1, ov)
        if mk == "router":
            c1, c8 = chance(A, B, perm)
            rec["chance_shuffle_top1"], rec["chance_shuffle_top8"] = c1, c8
            f = perm_floor(A, B)
            rec["perm_floor_top1_mean"], rec["perm_floor_top1_p99"], rec["perm_floor_top8_mean"], rec["perm_floor_top8_p99"] = f
    # positive control on gain recovery
    if m - l == 12 and l in (6, 12, 18):
        rec["pc_gain_recovery_top8"] = float(agree_vec(T_self(m), top(xm * g[m], W[m]))[1].mean())
    # geometry floor (shared random router), copy pairs + references (all pairs; cheap enough)
    if (m - l) in (12, 24) or (m - l in (1, 11, 13) and 6 <= l and m <= 41):
        fl = {"N_A": [], "N_B": [], "N_G": []}
        for fam, Wr, br in random_routers(l):
            t1, ov = agree_vec(top(xl, Wr, br), top(xm, Wr, br))
            fl[fam].append((float(t1.mean()), float(ov.mean())))
        for fam, v in fl.items():
            v = np.array(v)
            rec[f"geo_{fam}_top1"] = [float(v[:, 0].mean()), float(v[:, 0].min()), float(v[:, 0].max())]
            rec[f"geo_{fam}_top8"] = [float(v[:, 1].mean()), float(v[:, 1].min()), float(v[:, 1].max())]
    if (m - l) in (12, 24):
        for k in ("O", "H", "R", "Rp"):
            rec[f"{k}_top1_ci"] = ci(vecs[k][0]); rec[f"{k}_top8_ci"] = ci(vecs[k][1])
        np.savez(f"{C}/agree_{l}_{m}.npz", **{f"{k}_t1": v[0].astype(np.float32) for k, v in vecs.items()},
                 **{f"{k}_ov": v[1].astype(np.float32) for k, v in vecs.items()},
                 A1=A[:, 0].numpy().astype(np.uint8), B1=B[:, 0].numpy().astype(np.uint8))
    res.append(rec)
    print(l, m, " ".join(f"{k}={rec[k + '_top1']:.3f}" for k in ("O", "H", "R", "Rp")),
          "geoNA=%.3f" % rec["geo_N_A_top1"][0] if "geo_N_A_top1" in rec else "", round(time.time() - t0), flush=True)
json.dump(res, open(f"{RES}/decomp{os.environ.get('TAG', '')}.json", "w"), indent=0)
print("done", round(time.time() - t0))
