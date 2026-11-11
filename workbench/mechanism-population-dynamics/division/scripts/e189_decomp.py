"""E189 readouts 1-5 (card: division/experiments/E189-training-axis-routing-decomposition.md).
OLMoE-1B-7B-0924 training axis, 9 checkpoints k, 16 layers, 22,000 toksub rows (router inputs).
  xhat_s = h_s / g_s (g = post_attention_layernorm gain);  T_t(x) = top8(W_t diag(g_t) x)   [primary: gain -> router]
  TS[t, s] = T_t(xhat_s) for every (t, s) pair; F = main (release).
  O = TS[t,t] vs TS[F,F]; H = TS[F,t] vs TS[F,F]; R = TS[t,F] vs TS[F,F]; H' = TS[t,t] vs TS[t,F]; R' = TS[t,t] vs TS[F,t]
  secondary (gain -> hidden state): raw h_s fed to W_t.
  grid G[t,s] = TS[t,s] vs TS[F,F]; adjacent pairs (k_i -> k_{i+1}) and endpoint 5.1T variants of the decomposition.
  geometry floor: one shared random router (N_A / N_B / N_G from W_F diag(g_F), 8 draws each, e187_decomp.py rules)
  applied to xhat_s, agreement vs xhat_F (and vs the adjacent checkpoint, and vs 5.1T).
  subspace drift (readout 4), layer-0 9x9 prev/inp information grid (readout 5, e185_lib.mi_marg).
Writes /tmp/xiang_e186/e189/{decomp.json, pertok.npz} (node-local)."""
import json, os, sys, time
import numpy as np
import torch
from scipy.optimize import linear_sum_assignment

torch.set_num_threads(int(os.environ.get("NT", 8)))
BASE = "/tmp/xiang_e186"
OUT = f"{BASE}/e189"
sys.path.insert(0, f"{BASE}/bundle/code")
from e185_lib import Plan, mi_marg  # noqa: E402

KEYS = ["olmoe0924_s5k", "olmoe0924_s20k", "olmoe0924_s80k", "olmoe0924_s140k", "olmoe0924_s200k",
        "olmoe0924_s260k", "olmoe0924_s320k", "olmoe0924_s1220k", "olmoe0924_main"]
TOK = [20e9, 83e9, 335e9, 587e9, 838e9, 1.09e12, 1.34e12, 5.1e12, None]
NK, F, F2 = len(KEYS), len(KEYS) - 1, len(KEYS) - 2
L, E, K, D = 16, 64, 8, 8
MID = list(range(2, 12))
LAYERS = [int(x) for x in os.environ.get("LAYERS", ",".join(map(str, range(L)))).split(",")]
t0 = time.time()
log = lambda *a: print(f"[{time.time() - t0:.0f}s]", *a, flush=True)

P = np.load(f"{OUT}/prep.npz")
N = P["src"].size
clus = P["clus"]; NC = int(clus.max()) + 1
eng = (P["src"] == 0) | (P["src"] == 20)
RT = [np.load(f"{BASE}/hidden/{k}/router.npz") for k in KEYS]
W = torch.tensor(np.stack([r["gate"] for r in RT]))                          # [NK, L, E, d]
G = torch.tensor(np.stack([r["post_attention_layernorm"] for r in RT]))      # [NK, L, d]
TS_MM = [np.load(f"{BASE}/hidden/{k}/toksub.npy", mmap_mode="r") for k in KEYS]
res = {"keys": KEYS, "tokens": TOK, "N": int(N), "min_abs_gain": float(G.abs().min()), "layers": {}}
log("min |g|", res["min_abs_gain"])

rng_b = np.random.default_rng(1890)
BOOT = np.stack([np.bincount(rng_b.integers(0, NC, NC), minlength=NC) for _ in range(1000)]).astype(np.float64)
CCNT = np.bincount(clus, minlength=NC).astype(np.float64)


def ci_many(V):
    """V: [n_vec, N] per-token values -> [n_vec, 2] 95% cluster-bootstrap CI of the mean."""
    S = np.stack([np.bincount(clus, v, NC) for v in V], 1)                   # [NC, n_vec]
    B = (BOOT @ S) / (BOOT @ CCNT)[:, None]
    return np.quantile(B, [.025, .975], axis=0).T


def top(x, Wm, b=None):
    z = x @ Wm.T
    if b is not None:
        z = z + b
    return z.topk(K, -1).indices


def agree(A, B):
    t1 = (A[:, 0] == B[:, 0]).float()
    MA = torch.zeros(A.shape[0], E).scatter_(1, A, 1.0)
    return t1.numpy(), (MA.gather(1, B).sum(1) / K).numpy()


def chance(A, B):
    n = A.shape[0]
    pa = torch.bincount(A[:, 0], minlength=E).double() / n; pb = torch.bincount(B[:, 0], minlength=E).double() / n
    fa = torch.bincount(A.reshape(-1), minlength=E).double() / n; fb = torch.bincount(B.reshape(-1), minlength=E).double() / n
    return float((pa * pb).sum()), float((fa * fb).sum() / K)


def perm_floor(A, B, n=200, seed=0):
    J1 = torch.zeros(E, E, dtype=torch.float64).index_put_((A[:, 0], B[:, 0]), torch.ones(A.shape[0], dtype=torch.float64), accumulate=True)
    MA = torch.zeros(A.shape[0], E, dtype=torch.float64).scatter_(1, A, 1.0); MB = torch.zeros(A.shape[0], E, dtype=torch.float64).scatter_(1, B, 1.0)
    J8 = MA.T @ MB
    gen = torch.Generator().manual_seed(seed)
    a1, a8 = [], []
    for _ in range(n):
        p = torch.randperm(E, generator=gen)
        a1.append(float(J1[p, torch.arange(E)].sum() / A.shape[0])); a8.append(float(J8[p, torch.arange(E)].sum() / A.shape[0] / K))
    return [float(np.mean(a1)), float(np.quantile(a1, .99)), float(np.mean(a8)), float(np.quantile(a8, .99))]


def hung(S):
    r, c = linear_sum_assignment(-S)
    p = np.empty(E, np.int64); p[c] = r          # expert j of b -> p[j] of a
    return p


def rowcos(Wm):
    Wc = Wm - Wm.mean(0, keepdims=True)
    return Wc / np.linalg.norm(Wc, axis=1, keepdims=True)


genQ = torch.Generator().manual_seed(189)
QA = []
for _ in range(D):
    Q_, R_ = torch.linalg.qr(torch.randn(2048, 2048, generator=genQ, dtype=torch.float64))
    QA.append((Q_ * torch.sign(torch.diagonal(R_))).float())
log("haar ready")


def fit_bias(Z, target, iters=200, lr=0.5):
    b = torch.zeros(E, dtype=Z.dtype); scale = Z.std(); tgt = target / target.sum()
    for _ in range(iters):
        f = torch.bincount(Z.add(b).topk(K, -1).indices.reshape(-1), minlength=E).to(Z.dtype)
        b = b + lr * scale * (tgt - f / f.sum()) / (tgt + 1e-3)
    return b


def random_routers(Weff, xfit, seed):
    """24 shared random routers from an effective router (act on xhat): N_A, N_B (bias fit on xfit), N_G."""
    Weff = Weff.double(); out = []
    for j in range(D):
        out.append(("N_A", (Weff.float() @ QA[j]), None))
    Wc = Weff - Weff.mean(0, keepdim=True)
    U, S, Vh = torch.linalg.svd(Wc, full_matrices=False)
    r = int((S > 1e-6 * S[0]).sum()); V = Vh[:r].T
    target = torch.bincount(top(xfit.double(), Weff).reshape(-1), minlength=E).double()
    gen = torch.Generator().manual_seed(seed)
    for j in range(D):
        Q_, R_ = torch.linalg.qr(torch.randn(r, r, generator=gen, dtype=torch.float64)); Q_ = Q_ * torch.sign(torch.diagonal(R_))
        Wn = (U[:, :r] * S[:r]) @ Q_ @ V.T
        out.append(("N_B", Wn.float(), fit_bias(xfit.double() @ Wn.T, target).float()))
    rn = Weff.norm(dim=1, keepdim=True)
    for j in range(D):
        Gm = torch.randn(E, 2048, generator=gen, dtype=torch.float64)
        out.append(("N_G", (Gm / Gm.norm(dim=1, keepdim=True) * rn).float(), None))
    return out


def lincka(A, B):
    A = A - A.mean(0, keepdim=True); B = B - B.mean(0, keepdim=True)
    return float((A.T @ B).pow(2).sum() / ((A.T @ A).pow(2).sum().sqrt() * (B.T @ B).pow(2).sum().sqrt()))


def drift(a, b):
    """mean relative drift ||a-b||/||b|| and mean cosine over tokens."""
    return float(((a - b).norm(dim=1) / b.norm(dim=1).clamp_min(1e-12)).mean()), \
        float(torch.nn.functional.cosine_similarity(a, b, dim=1).mean())


# id-mean decomposition support (ids with >= 5 occurrences in the 22k rows)
inp = P["inp"]
uid, uinv, ucnt = np.unique(inp, return_inverse=True, return_counts=True)
idok = ucnt[uinv] >= 5
res["idmean_coverage"] = float(idok.mean())
idx_ok = torch.tensor(np.where(idok)[0]); inv_ok = torch.tensor(np.unique(uinv[idok], return_inverse=True)[1])
n_ok_ids = int(inv_ok.max()) + 1


def idmean_split(x):
    xs = x[idx_ok]
    M = torch.zeros(n_ok_ids, x.shape[1]).index_add_(0, inv_ok, xs)
    M = M / torch.bincount(inv_ok, minlength=n_ok_ids).float()[:, None]
    mu = M[inv_ok]
    return mu, xs - mu


CKA_SUB = torch.tensor(np.sort(np.random.default_rng(1891).choice(N, 4000, replace=False)))
COMPS = ["O", "H", "R", "Hp", "Rp"]
PT = np.zeros((NK, 5, 2, N), np.float32)        # mid-band per-token mean (top-1, top-8) vs F
PTn = np.zeros((NK, 5, 2, N), np.float32)
nmid = 0
store_pc = {}

for l in LAYERS:
    tl = time.time()
    H = [torch.tensor(np.asarray(TS_MM[k][l], dtype=np.float32)) for k in range(NK)]
    X = [H[k] / G[k, l] for k in range(NK)]
    Weff = [W[k, l] * G[k, l] for k in range(NK)]
    TSm = [[top(X[s], Weff[t]) for s in range(NK)] for t in range(NK)]                   # primary
    TSr = [[top(H[s], W[t, l]) for s in range(NK)] for t in range(NK)]                   # secondary (raw h)
    rec = {}
    # positive controls
    rec["pc_self"] = [float(np.mean(agree(TSm[F][F], TSm[F][F])[i])) for i in (0, 1)]
    rec["pc_gain_recovery_top8"] = float(np.mean([agree(TSm[k][k], TSr[k][k])[1].mean() for k in range(NK)]))
    S = rowcos(Weff[F].numpy().astype(np.float64)); pr = np.random.default_rng(l).permutation(E)
    rec["pc_hung_perm_recovery"] = float((hung(S @ S[pr].T) == pr).mean())
    rec["identity_rate_eff"] = []; rec["identity_rate_raw"] = []
    hperm = []
    for k in range(NK):
        p_e = hung(rowcos(Weff[k].numpy().astype(np.float64)) @ rowcos(Weff[F].numpy().astype(np.float64)).T)
        p_r = hung(rowcos(W[k, l].numpy().astype(np.float64)) @ rowcos(W[F, l].numpy().astype(np.float64)).T)
        rec["identity_rate_eff"].append(float((p_e == np.arange(E)).mean())); rec["identity_rate_raw"].append(float((p_r == np.arange(E)).mean()))
        hperm.append(torch.tensor(p_e))
    # decomposition vs endpoint e (F = release; F2 = 5.1T robustness) and adjacent pairs
    def decomp(a, b, TT, keep=None):
        defs = {"O": (TT[a][a], TT[b][b]), "H": (TT[b][a], TT[b][b]), "R": (TT[a][b], TT[b][b]),
                "Hp": (TT[a][a], TT[a][b]), "Rp": (TT[a][a], TT[b][a])}
        out, vecs = {}, {}
        for c, (A, B) in defs.items():
            t1, t8 = agree(A, B)
            out[c] = [float(t1.mean()), float(t8.mean())]
            out[c + "_chance"] = list(chance(A, B))
            vecs[c] = (t1, t8)
        return out, vecs
    rec["toF"], rec["toF_raw"], rec["to51"], rec["adj"], rec["toF_eng"] = [], [], [], [], []
    vF = []
    for t in range(NK):
        o, v = decomp(t, F, TSm); vF.append(v)
        o["perm_floor_O"] = perm_floor(TSm[t][t], TSm[F][F]) if t in (0, 2, 6, 7) else None
        q = torch.argsort(hperm[t])                    # hperm: F expert j -> t expert p[j]; q maps t labels to F labels
        o["O_hung"] = [float(x.mean()) for x in agree(TSm[F][F], q[TSm[t][t]])]
        o["R_hung"] = [float(x.mean()) for x in agree(TSm[F][F], q[TSm[t][F]])]
        rec["toF"].append(o)
        rec["toF_raw"].append(decomp(t, F, TSr)[0])
        rec["to51"].append(decomp(t, F2, TSm)[0])
        rec["toF_eng"].append({c: [float(v[c][0][eng].mean()), float(v[c][1][eng].mean())] for c in COMPS})
    for i in range(NK - 1):
        rec["adj"].append(decomp(i, i + 1, TSm)[0])
    rec["grid"] = [[[float(x.mean()) for x in agree(TSm[t][s], TSm[F][F])] for s in range(NK)] for t in range(NK)]
    # CIs (per layer) for the five components vs F
    V = np.stack([vF[t][c][i] for t in range(NK) for c in COMPS for i in (0, 1)])
    C = ci_many(V).reshape(NK, len(COMPS), 2, 2)
    rec["toF_ci"] = C.tolist()
    if l in MID:
        for t in range(NK):
            for ci_, c in enumerate(COMPS):
                PT[t, ci_, 0] += vF[t][c][0]; PT[t, ci_, 1] += vF[t][c][1]
        nmid += 1
    # geometry floor: shared random routers built from layer-l release effective router
    fl = {fam: {"toF": [], "adj": [], "to51": []} for fam in ("N_A", "N_B", "N_G")}
    for fam, Wr, br in random_routers(Weff[F], X[F], 18900 + l):
        Ts = [top(X[s], Wr, br) for s in range(NK)]
        fl[fam]["toF"].append([[float(x.mean()) for x in agree(Ts[s], Ts[F])] for s in range(NK)])
        fl[fam]["adj"].append([[float(x.mean()) for x in agree(Ts[i], Ts[i + 1])] for i in range(NK - 1)])
        fl[fam]["to51"].append([[float(x.mean()) for x in agree(Ts[s], Ts[F2])] for s in range(NK)])
        if fam == "N_A" and len(fl[fam]["toF"]) == 1:
            fl[fam]["toF_eng_draw0"] = [[float(x[eng].mean()) for x in agree(Ts[s], Ts[F])] for s in range(NK)]
    rec["geo"] = {fam: {kk: (np.array(vv).tolist()) for kk, vv in d.items()} for fam, d in fl.items()}
    # readout 4: subspace drift
    Pv = {}
    for k in range(NK):
        Wc = Weff[k].double() - Weff[k].double().mean(0, keepdim=True)
        _, Sk, Vh = torch.linalg.svd(Wc, full_matrices=False)
        Pv[k] = Vh[: int((Sk > 1e-6 * Sk[0]).sum())].T.float()
    VF = Pv[F]
    sub = []
    for t in range(NK):
        a, b = X[t], X[F]
        ai, bi = a @ VF, b @ VF
        ao, bo = a - ai @ VF.T, b - bi @ VF.T
        r = {"in": drift(ai, bi), "out": drift(ao, bo), "full": drift(a, b),
             "cka_in": lincka(ai, bi), "cka_out": lincka(ao[CKA_SUB], bo[CKA_SUB]), "cka_full": lincka(a[CKA_SUB], b[CKA_SUB]),
             "energy_in_t": float((ai.norm(dim=1) ** 2 / a.norm(dim=1) ** 2).mean()),
             "pa_cos_mean": float(torch.linalg.svdvals(Pv[t].T @ VF).mean())}
        mua, ra = idmean_split(a); mub, rb = idmean_split(b)
        r["idmean_full"] = drift(mua, mub); r["resid_full"] = drift(ra, rb)
        r["idmean_in"] = drift(mua @ VF, mub @ VF); r["resid_in"] = drift(ra @ VF, rb @ VF)
        sc = CKA_SUB[idok[CKA_SUB.numpy()]]
        pos_in_ok = torch.tensor(np.searchsorted(idx_ok.numpy(), sc.numpy()))
        r["cka_idmean_full"] = lincka(mua[pos_in_ok], mub[pos_in_ok]); r["cka_resid_full"] = lincka(ra[pos_in_ok], rb[pos_in_ok])
        r["cka_idmean_in"] = lincka(mua @ VF, mub @ VF); r["cka_resid_in"] = lincka(ra @ VF, rb @ VF)
        r["energy_idmean_full"] = float((mub.pow(2).sum() / (mub.pow(2).sum() + rb.pow(2).sum())))
        r["energy_idmean_in"] = float(((mub @ VF).pow(2).sum() / ((mub @ VF).pow(2).sum() + (rb @ VF).pow(2).sum())))
        sub.append(r)
    rec["subspace"] = sub
    # store positive control (T_F and others vs E186 stores, same tokens)
    for k, key in enumerate(KEYS):
        sd = f"{BASE}/store/{key}"
        if not os.path.exists(f"{sd}/topk.npy"):
            continue
        if key not in store_pc:
            store_pc[key] = {}
        if "rows" not in store_pc[key]:
            st = np.load(f"{sd}/tokmeta.npz"); sm = json.load(open(f"{sd}/meta.json")); sides = sm["sides"]
            cor, side, sid_, pos_, inp_, up = (st[f].astype(np.int64) for f in ("corpus", "side", "sid", "pos", "inp", "upos"))
            udc = int(np.unique(cor[up >= 0])[0]) if (up >= 0).any() else 1
            kf = lambda c, sd_, si, p: ((c * 64 + sd_) * 100000 + si) * 4096 + p
            skey = kf(cor, np.where(cor == udc, 0, side), sid_, pos_); order = np.argsort(skey); sk = skey[order]
            rows = np.full(N, -1, np.int64); langs = json.load(open(f"{BASE}/hidden/{key}/meta.json"))["langs"]
            for rr in range(N):
                a_ = int(P["src"][rr])
                if a_ == 20:
                    q = kf(udc, 0, int(P["sid"][rr]), int(P["pos"][rr]))
                elif langs[a_] in sides:
                    q = kf(1 - udc, sides.index(langs[a_]), int(P["sid"][rr]), int(P["pos"][rr]))
                else:
                    continue
                j = np.searchsorted(sk, q)
                if j < sk.size and sk[j] == q and inp_[order[j]] == inp[rr]:
                    rows[rr] = order[j]
            store_pc[key]["rows"] = rows
        rows = store_pc[key]["rows"]; okr = np.where(rows >= 0)[0]
        if okr.size == 0:
            continue
        stk = np.load(f"{sd}/topk.npy", mmap_mode="r")
        so = np.argsort(rows[okr]); srt = rows[okr][so]
        blk = torch.tensor(np.asarray(stk[l, srt, 0, :]).astype(np.int64))
        mine = TSm[k][k][torch.tensor(okr[so])]
        t1, t8 = agree(mine, blk)
        store_pc[key].setdefault("layers", {})[l] = [float(t1.mean()), float(t8.mean()), int(okr.size)]
    # readout 5: layer-0 grid of prev / inp information
    if l == 0:
        plan = Plan(np.arange(N))
        plan.add_marg("inp", inp); plan.add_marg("prev", P["prev"])
        gr = np.zeros((NK, NK, 4))
        for t in range(NK):
            for s in range(NK):
                e1 = TSm[t][s][:, 0].numpy().astype(np.int64)
                ip = mi_marg(e1, plan.marg["inp"], E); pp = mi_marg(e1, plan.marg["prev"], E)
                gr[t, s] = [pp[0] / pp[3], ip[0] / ip[3], pp[0] / ip[0], ip[3]]
        rec["l0_grid"] = {"share_prev": gr[..., 0].tolist(), "share_inp": gr[..., 1].tolist(), "ratio": gr[..., 2].tolist(),
                          "H_top1": gr[..., 3].tolist()}
        # geometry reference: N_B-type router from W_t, bias fit on xhat_t (diagonal), 1 draw
        nb = []
        for t in range(NK):
            fam, Wr, br = random_routers(Weff[t], X[t], 18950 + t)[D]       # first N_B draw
            e1 = top(X[t], Wr, br)[:, 0].numpy().astype(np.int64)
            ip = mi_marg(e1, plan.marg["inp"], E); pp = mi_marg(e1, plan.marg["prev"], E)
            nb.append([pp[0] / pp[3], ip[0] / ip[3], pp[0] / ip[0]])
        rec["l0_NB_diag"] = nb
        # same grid restricted to the English view (eng FLORES + UD) for the 5b shape check
        plan_e = Plan(np.where(eng)[0]); plan_e.add_marg("inp", inp); plan_e.add_marg("prev", P["prev"])
        ge = np.zeros((NK, NK))
        for t in range(NK):
            for s in range(NK):
                e1 = TSm[t][s][:, 0].numpy().astype(np.int64)[np.where(eng)[0]]
                ge[t, s] = mi_marg(e1, plan_e.marg["prev"], E)[0] / mi_marg(e1, plan_e.marg["inp"], E)[0]
        rec["l0_grid_eng_ratio"] = ge.tolist()
    res["layers"][l] = rec
    log("layer", l, "O/H/R top1 @20B", [round(rec["toF"][0][c][0], 3) for c in ("O", "H", "R")], "secs", round(time.time() - tl))
    json.dump(res, open(f"{OUT}/decomp.json", "w"))

res["store_pc"] = {k: v.get("layers", {}) for k, v in store_pc.items()}
res["store_pc_rows"] = {k: int((v["rows"] >= 0).sum()) for k, v in store_pc.items()}
if nmid:
    PT /= nmid
    # mid-band CIs
    res["mid_ci"] = ci_many(PT.reshape(-1, N)).reshape(NK, 5, 2, 2).tolist()
    np.savez_compressed(f"{OUT}/pertok.npz", PT=PT)
json.dump(res, open(f"{OUT}/decomp.json", "w"))
log("done")
