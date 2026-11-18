#!/usr/bin/env python3
"""E192 readouts 1-5 (card: division/experiments/E192-frozen-router-intervention.md), run on whatever save points exist.
Inputs (node-local, gathered by e192_collect.sh): ANA/arms/<arm>/{run_info.json, train_log.jsonl, routers_cXXXX.npz,
nll_cXXXX.npz, dump_cXXXX/}; ROOT/dclm/eval_dclm.u16 + pool_P1.u16 (token classes); ROOT/ckpt/iter_* (official router
weights read from the bf16 DCP tensors on CPU); ROOT/official/i<iter>/ (e192_eval.py anchors, if present).
Definitions follow E191 (e191_decomp.py; its top / agree / chance / hung / rowcos / lincka are copied verbatim below
because e191_decomp.py is a script with module-level execution): effective router W diag(g), x^ = h / g, top-6 overlap
|S_a & S_b| / 6 and top-1 agreement; main view = FLORES eng + UD (12,000 tokens), mid band = MoE layers 2-7 (index 1..6);
CIs = sentence-cluster bootstrap (routing) or 2048-window bootstrap (NLL), 1000 draws, paired where the card says paired.
Writes OUT/{tables.md, summary.json, fig_nll.png, fig_diff.png, fig_routing.png, fig_decomp.png, fig_geometry.png}.
usage: nice -n 19 NT=8 python e192_analyze.py --ana /tmp/xiang_e192/analysis --out /tmp/xiang_e192/analysis/out"""
import argparse, glob, json, os, re, sys, time
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--ana", default="/tmp/xiang_e192/analysis"); ap.add_argument("--root", default="/tmp/xiang_e192")
ap.add_argument("--out", default="/tmp/xiang_e192/analysis/out"); ap.add_argument("--boot", type=int, default=1000)
ap.add_argument("--max-c", type=int, default=10 ** 9, help="ignore save points after this continuation iter (stage-1 analysis: 540)")
a = ap.parse_args()
os.environ.setdefault("OMP_NUM_THREADS", os.environ.get("NT", "8"))
import torch  # noqa: E402
torch.set_num_threads(int(os.environ.get("NT", 8)))
from scipy.optimize import linear_sum_assignment  # noqa: E402
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.makedirs(a.out, exist_ok=True)
t0 = time.time()
log = lambda *x: print(f"[{time.time() - t0:.0f}s]", *x, flush=True)
L, E, K, DM = 8, 64, 6, 1024
MID = list(range(1, 7))
SEQ, GB = 2048, 1024

# ------------------------------------------------------------------ copied from e191_decomp.py
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


def hung(S):
    r, c = linear_sum_assignment(-S)
    p = np.empty(E, np.int64); p[c] = r          # expert j of b -> p[j] of a
    return p


def rowcos(Wm):
    Wc = Wm - Wm.mean(0, keepdims=True)
    return Wc / np.linalg.norm(Wc, axis=1, keepdims=True)


def lincka(A, B):
    A = A - A.mean(0, keepdim=True); B = B - B.mean(0, keepdim=True)
    return float((A.T @ B).pow(2).sum() / ((A.T @ A).pow(2).sum().sqrt() * (B.T @ B).pow(2).sum().sqrt()))
# ------------------------------------------------------------------


ARMDEF = {"A1": (1080, "free", "on", 1), "A2": (1080, "free", "on", 2), "B1": (1080, "frozen", "on", 1),
          "B2": (1080, "frozen", "on", 2), "C1": (1080, "reset", "on", 1), "C2": (1080, "reset", "on", 2),
          "D": (540, "frozen", "on", 1), "E": (540, "free", "on", 1), "F": (1080, "only", "on", 1), "G": (1080, "frozen", "off", 1)}
# replication arms (card section 追加臂, POST-HOC 11-18)
ARMDEF.update({"B2r": (1080, "frozen", "on", 2), "G2": (1080, "frozen", "off", 2), "A3": (1080, "free", "on", 3), "B3": (1080, "frozen", "on", 3),
               "A4": (1080, "free", "on", 4), "B4": (1080, "frozen", "on", 4), "A5": (1080, "free", "on", 5), "B5": (1080, "frozen", "on", 5)})
REPL = ["B2r", "G2", "A3", "B3", "A4", "B4", "A5", "B5"]
# round 3 (card "B2r 的结果与第三轮", 11-18): per-layer router treatments + p6 test on the official data
ARMDEF.update({"CL1_1": (1080, "reset", "on", 1), "CL1_2": (1080, "reset", "on", 2), "CD_1": (1080, "reset", "on", 1), "CD_2": (1080, "reset", "on", 2),
               "DL1free": (540, "frozen", "on", 1), "DL1only": (540, "frozen", "on", 1), "D2": (540, "frozen", "on", 2), "E2": (540, "free", "on", 2),
               "P6GS03": (1080, "free", "on", 1)})
ROUND3 = ["CL1_1", "CL1_2", "CD_1", "CD_2", "DL1free", "DL1only", "D2", "E2", "P6GS03"]
RESET_L = {"CL1_1": [1], "CL1_2": [1], "CD_1": list(range(2, 9)), "CD_2": list(range(2, 9))}       # MoE layer numbers
FROZEN_L = {"DL1free": list(range(2, 9)), "DL1only": [1], "D2": list(range(1, 9))}
HIDE = set(REPL) | set(ROUND3)
PAIRS = [("B1", "A1"), ("B2", "A2"), ("C1", "A1"), ("C2", "A2"), ("D", "E"), ("G", "B1"), ("F", "A1"),
         ("B3", "A3"), ("B4", "A4"), ("B5", "A5"), ("B2r", "A2"), ("G2", "A2"), ("G2", "B2r"), ("B2r", "B2"),
         ("CL1_1", "A1"), ("CL1_2", "A2"), ("CD_1", "A1"), ("CD_2", "A2"), ("DL1free", "E"), ("DL1only", "E"), ("D2", "E2"), ("P6GS03", "A1")]
FLOOR = ("A1", "A2")


def points(arm):
    """save points with complete dump (meta.json) AND nll AND routers"""
    d = f"{a.ana}/arms/{arm}"; out = []
    for m in sorted(glob.glob(f"{d}/dump_c*/meta.json")):
        c = int(re.search(r"dump_c(\d+)", m).group(1))
        if os.path.exists(f"{d}/nll_c{c:04d}.npz") and os.path.exists(f"{d}/routers_c{c:04d}.npz"):
            if c <= a.max_c:
                out.append(c)
    return out


ARMS = [x for x in ARMDEF if os.path.isdir(f"{a.ana}/arms/{x}")]
PTS = {x: points(x) for x in ARMS}
DONE = {x: any(os.path.exists(f"{a.ana}/arms/{x}/DONE_{n:04d}") for n in (108, 540, 1080) if n <= a.max_c) for x in ARMS}
INTERIM = not all(DONE.get(x, False) for x in ARMS)          # any present arm still running -> interim label
log("arms", PTS, "interim" if INTERIM else "final")
S = {"arms": ARMS, "points": PTS, "done": DONE, "interim": INTERIM, "pending": []}

# ------------------------------------------------------------------ token-set meta (same for every dump)
ref_dump = f"{a.ana}/arms/{ARMS[0]}/dump_c{PTS[ARMS[0]][0]:04d}"
M0 = np.load(f"{ref_dump}/toksub_meta.npz"); meta0 = json.load(open(f"{ref_dump}/meta.json"))
src_ud = meta0["src_ud"]
VIEW = np.where((M0["src"] == 0) | (M0["src"] == src_ud))[0]
clus = np.unique(M0["src"][VIEW].astype(np.int64) * 100000 + M0["sid"][VIEW], return_inverse=True)[1]; NC = int(clus.max()) + 1
rngb = np.random.default_rng(1920)
BOOTC = np.stack([np.bincount(rngb.integers(0, NC, NC), minlength=NC) for _ in range(a.boot)]).astype(np.float64)
CCNT = np.bincount(clus, minlength=NC).astype(np.float64)
NV = VIEW.size
for x in ARMS:                                   # all dumps must be on the same token rows
    for c in PTS[x][:1] + PTS[x][-1:]:
        m = np.load(f"{a.ana}/arms/{x}/dump_c{c:04d}/toksub_meta.npz")
        assert (m["inp"] == M0["inp"]).all() and (m["pos"] == M0["pos"]).all(), (x, c)


def ci_tok(v):
    s = np.bincount(clus, v, NC); B = (BOOTC @ s) / (BOOTC @ CCNT)
    return [float(v.mean()), float(np.quantile(B, .025)), float(np.quantile(B, .975))]


_cache = {}


def pt(arm, c):
    """routers + gains of a save point (official: arm='OFF', c=iter)"""
    k = (arm, c)
    if k not in _cache:
        if arm == "OFF":
            _cache[k] = official_router(c)
        else:
            r = np.load(f"{a.ana}/arms/{arm}/dump_c{c:04d}/router.npz")
            _cache[k] = (torch.tensor(r["gate"]), torch.tensor(r["post_attention_layernorm"]))
    return _cache[k]


_hc = {}


def xhat(arm, c, l):
    """router input / own gain on the main view, float32 [NV, d]"""
    k = (arm, c, l)
    if k not in _hc:
        if len(_hc) > 160:
            _hc.clear()
        if arm == "OFF":
            h = np.load(f"{a.root}/official/i{c}/dump/toksub.npy", mmap_mode="r")[l][VIEW]
        else:
            h = np.load(f"{a.ana}/arms/{arm}/dump_c{c:04d}/toksub.npy", mmap_mode="r")[l][VIEW]
        _hc[k] = torch.tensor(np.asarray(h, dtype=np.float32)) / pt(arm, c)[1][l]
    return _hc[k]


def weff(arm, c, l):
    W, g = pt(arm, c)
    return W[l] * g[l]


def official_router(it):
    d = f"{a.root}/ckpt/iter_{it:07d}"
    from e192_train import read_dcp
    names = [f"decoder.layers.{l + 1}.mlp.router.weight" for l in range(L)] + [f"decoder.layers.{l + 1}.pre_mlp_layernorm.weight" for l in range(L)]
    sd = read_dcp(d, names)
    return (torch.stack([sd[f"decoder.layers.{l + 1}.mlp.router.weight"].float() for l in range(L)]),
            torch.stack([sd[f"decoder.layers.{l + 1}.pre_mlp_layernorm.weight"].float() for l in range(L)]))


def has_official_dump(it):
    return os.path.exists(f"{a.root}/official/i{it}/dump/meta.json")


def cmp_routers(ra, rb, xin, hungarian=True):
    """agreement of two routers (arm, c) on the same input x^ = xin (arm, c); mid-band per-token mean + CI, per layer,
    identity matching and Hungarian matching of rb's experts onto ra's (row cosine of effective routers)."""
    t1m, t6m, t1h, t6h, per, ch, r6m = 0, 0, 0, 0, [], [], 0
    for l in range(L):
        x = xhat(*xin, l)
        A = top(x, weff(*ra, l)); B = top(x, weff(*rb, l))
        a1, a6 = agree(A, B); ch.append(chance(A, B)[1])
        if hungarian:
            p = hung(rowcos(weff(*ra, l).numpy().astype(np.float64)) @ rowcos(weff(*rb, l).numpy().astype(np.float64)).T)
            h1, h6 = agree(A, torch.tensor(p)[B])
        else:
            h1, h6 = a1, a6
        # POST-HOC (11-17): routing-based matching = Hungarian on the top-6 co-assignment counts of the two routers
        MA_ = torch.zeros(A.shape[0], E, dtype=torch.float64).scatter_(1, A, 1.0); MB_ = torch.zeros(B.shape[0], E, dtype=torch.float64).scatter_(1, B, 1.0)
        pr = hung((MA_.T @ MB_).numpy()); r1, r6 = agree(A, torch.tensor(pr)[B])
        per.append([float(a1.mean()), float(a6.mean()), float(h1.mean()), float(h6.mean())])
        if l in MID:
            r6m = (r6m if l != MID[0] else 0) + r6 / len(MID)
            t1m = t1m + a1 / len(MID); t6m = t6m + a6 / len(MID); t1h = t1h + h1 / len(MID); t6h = t6h + h6 / len(MID)
    return {"top6": ci_tok(t6m), "top1": ci_tok(t1m), "top6_hung": ci_tok(t6h), "top1_hung": ci_tok(t1h),
            "top6_routhung_posthoc": ci_tok(r6m), "chance_top6_mid": float(np.mean([ch[l] for l in MID])), "per_layer": per}


# ================================================================== §0 sanity
S["sanity"] = {}
if "C1" in ARMS or "C2" in ARMS:
    S["sanity"]["C_c0000_vs_S"] = {x: cmp_routers((x, 0), ("A1", 0), ("A1", 0)) for x in ("C1", "C2") if x in ARMS and 0 in PTS[x]}
S["sanity"]["B_router_maxabs_vs_S"] = {}
for x in ("B1", "B2", "D", "G"):
    if x not in ARMS:
        continue
    ref = ("A1", 0) if x != "D" else ("E", 0)
    if ref[0] not in ARMS:
        continue
    S["sanity"]["B_router_maxabs_vs_S"][x] = {c: float((pt(x, c)[0] - pt(*ref)[0]).abs().max()) for c in PTS[x]}


def trainlog(arm):
    r = [json.loads(l) for l in open(f"{a.ana}/arms/{arm}/train_log.jsonl")]
    tr = {x["it"]: x for x in r if "eval" not in x and x["it"] <= a.max_c}            # keep the last record per iter
    ev = [x for x in r if "eval" in x and x["it"] <= a.max_c]
    return [tr[k] for k in sorted(tr)], ev


TL = {x: trainlog(x) for x in ARMS}
S["train"] = {}
for x, y in [("B1", "A1"), ("B2", "A2"), ("C1", "A1"), ("D", "E")]:
    if x in ARMS and y in ARMS:
        lx = np.array([r["lm"] for r in TL[x][0]]); ly = np.array([r["lm"] for r in TL[y][0]]); n = min(len(lx), len(ly))
        d = lx[:n] - ly[:n]
        S["train"][f"{x}-{y}"] = {"n_iter": int(n), "iter1": [float(lx[0]), float(ly[0])], "diff_first5": d[:5].round(5).tolist(),
                                  "corr_of_iter_to_iter_changes": float(np.corrcoef(np.diff(lx[:n]), np.diff(ly[:n]))[0, 1]) if n > 3 else None,
                                  "mean_diff_last10": float(d[-10:].mean())}
# POST-HOC (11-18, after seeing B2's c324 point): training stability per 54-iter block from the per-iter log
S["stability"] = {}
for x in ARMS:
    tr = TL[x][0]; blocks = {}
    for b0 in range(0, len(tr), 54):
        blk = tr[b0:b0 + 54]
        if blk:
            blocks[f"{blk[0]['it']}-{blk[-1]['it']}"] = {"lm_mean": float(np.mean([r["lm"] for r in blk])), "gn_median": float(np.median([r["gn"] for r in blk])),
                                                        "gn_max": float(max(r["gn"] for r in blk)), "z_max": float(max(r["z"] for r in blk)),
                                                        "maxload_max": float(max(max(r["maxload_l"]) for r in blk)),
                                                        "n_jump_gt_0.1": int(sum(1 for i in range(1, len(blk)) if blk[i]["lm"] - blk[i - 1]["lm"] > .1))}
    S["stability"][x] = blocks
for x in ARMS:
    tr = TL[x][0]
    S["train"][x] = {"n_iter": len(tr), "router_unchanged_all": all(r["router_unchanged"] for r in tr),
                     "max_jump_first54": float(np.diff([r["lm"] for r in tr[:54]]).max()) if len(tr) > 2 else None,
                     "tok_s_median": float(np.median([r["tok_s"] for r in tr])) if tr else None}
log("sanity done")

# ================================================================== §1 held-out NLL
nllc = {}


def nll(arm, c, k):
    key = (arm, c, k)
    if key not in nllc:
        if arm == "OFF":
            z = np.load(f"{a.root}/official/i{c}/nll.npz")
        else:
            z = np.load(f"{a.ana}/arms/{arm}/nll_c{c:04d}.npz")
        nllc[key] = z[k].astype(np.float64)
    return nllc[key]


WB = {}


def boot_idx(nw):
    if nw not in WB:
        WB[nw] = np.random.default_rng(1921).integers(0, nw, (a.boot, nw))
    return WB[nw]


def wci(v):
    """v [n_windows, SEQ] per-token values -> mean + 95% window-bootstrap CI"""
    m = v.mean(1); bi = boot_idx(len(m)); b = m[bi].mean(1)
    return [float(m.mean()), float(np.quantile(b, .025)), float(np.quantile(b, .975))]


S["nll"] = {"curves": {}, "pairs": {}, "floor": {}, "official": {}}
for x in ARMS:
    st = ARMDEF[x][0]
    S["nll"]["curves"][x] = {str(c): {"official_iter": st + c, **{k: wci(nll(x, c, k)) for k in ("dclm", "wikitext")}} for c in PTS[x]}
for it in (540, 1080, 1620, 2160):
    if os.path.exists(f"{a.root}/official/i{it}/nll.npz"):
        S["nll"]["official"][str(it)] = {k: wci(nll("OFF", it, k)) for k in ("dclm", "wikitext")}
if "1620" not in S["nll"]["official"]:
    S["pending"].append("official iter 1620 / 2160 NLL + dump (e192_eval.py, GPU ~1 min each): A-vs-official floor, 2a/2d on official inputs")
for p, q in PAIRS + [FLOOR]:
    if p in ARMS and q in ARMS:
        cs = sorted(set(PTS[p]) & set(PTS[q]))
        tgt = S["nll"]["floor"] if (p, q) == FLOOR else S["nll"]["pairs"]
        tgt[f"{p}-{q}"] = {str(c): {k: wci(nll(p, c, k) - nll(q, c, k)) for k in ("dclm", "wikitext")} for c in cs}
# C - A gap: interval decrements and their ratio (geometric projection to c1080 is descriptive only)
S["nll"]["C_gap_rate"] = {}
for name in ("C1-A1", "C2-A2"):
    d = S["nll"]["pairs"].get(name, {})
    cs = sorted(int(c) for c in d)
    if len(cs) >= 3:
        g = np.array([d[str(c)]["dclm"][0] for c in cs]); dec = -np.diff(g); r = dec[1:] / np.where(dec[:-1] == 0, np.nan, dec[:-1])
        rl = float(np.nanmean(r[-3:])) if len(r) else None
        S["nll"]["C_gap_rate"][name] = {"c": cs, "gap": g.tolist(), "decrement_per_54": dec.tolist(), "ratio": r.tolist(), "ratio_last3_mean": rl,
                                         "geometric_projection_c1080": float(g[-1] * rl ** ((1080 - cs[-1]) / 54) if rl and 0 < rl < 1 else np.nan),
                                         "geometric_limit": float(g[-1] - dec[-1] * rl / (1 - rl)) if rl and 0 < rl < 1 else None}
# A vs official at equal tokens (c=0 is trivially the same weights; c=540 vs official 1620)
for x in ARMS:
    if x in ARMS:
        st = ARMDEF[x][0]
        for c in PTS[x]:
            if c > 0 and os.path.exists(f"{a.root}/official/i{st + c}/nll.npz"):
                S["nll"].setdefault("vs_official", {})[f"{x}@{st + c}"] = {k: wci(nll(x, c, k) - nll("OFF", st + c, k)) for k in ("dclm", "wikitext")}
log("nll done")

# ================================================================== §2 routing
S["routing"] = {"vsS": {}, "C": {}, "A1vsA2": {}, "A_vs_off1620": {}, "B_gain": {}, "load": {}}
# every arm's router at every point vs its start router (S for 1080 arms, iter-540 router for D/E), on the arm's own input
for x in ARMS:
    s0 = ("A1", 0) if ARMDEF[x][0] == 1080 else ("E", 0)
    if s0[0] not in ARMS:
        continue
    S["routing"]["vsS"][x] = {str(c): cmp_routers((x, c), s0, (x, c)) for c in PTS[x]}
    # how far the router weights and the router inputs moved from the start point (mid band)
    dr = {}
    for c in PTS[x]:
        rw, re_, ci_, co_, cf_, hS = [], [], [], [], [], 0
        for l in MID:
            W1, W0 = pt(x, c)[0][l], pt(*s0)[0][l]
            rw.append(float(torch.nn.functional.cosine_similarity(W1, W0, dim=1).mean()))
            re_.append(float(torch.nn.functional.cosine_similarity(weff(x, c, l), weff(*s0, l), dim=1).mean()))
            Wc = weff(*s0, l).double(); Wc = Wc - Wc.mean(0, keepdim=True)
            _, Sv, Vh = torch.linalg.svd(Wc, full_matrices=False); r = int((Sv > 1e-6 * Sv[0]).sum()); V = Vh[:r].T.float()
            xa, x0 = xhat(x, c, l), xhat(*s0, l); ia, i0 = xa @ V @ V.T, x0 @ V @ V.T
            cs_ = torch.nn.functional.cosine_similarity
            cf_.append(float(cs_(xa, x0, dim=1).mean())); ci_.append(float(cs_(ia, i0, dim=1).mean())); co_.append(float(cs_(xa - ia, x0 - i0, dim=1).mean()))
            hS = hS + agree(top(xa, weff(*s0, l)), top(x0, weff(*s0, l)))[1] / len(MID)
        dr[str(c)] = {"W_rowcos": float(np.mean(rw)), "Weff_rowcos": float(np.mean(re_)), "xhat_cos": float(np.mean(cf_)),
                      "xhat_cos_in": float(np.mean(ci_)), "xhat_cos_out": float(np.mean(co_)), "H_startrouter_top6": ci_tok(hS)}
    S["routing"].setdefault("drift_from_start", {})[x] = dr
# 2b: C's relearned router vs S router and vs A's router (same iter, same seed) and vs A's latest router, on C's own input
for x, y in (("C1", "A1"), ("C2", "A2")):
    if x in ARMS and y in ARMS:
        cs = sorted(set(PTS[x]) & set(PTS[y])); yl = PTS[y][-1]
        S["routing"]["C"][x] = {"vsS_onS_input": {str(c): cmp_routers((x, c), ("A1", 0), ("A1", 0)) for c in PTS[x]},
                                "vsA_same_iter": {str(c): cmp_routers((x, c), (y, c), (x, c)) for c in cs},
                                "vsA_latest": {str(c): cmp_routers((x, c), (y, yl), (x, c)) for c in PTS[x]}, "A_latest": yl}
if "C1" in ARMS and "C2" in ARMS:
    cs = sorted(set(PTS["C1"]) & set(PTS["C2"]))
    S["routing"]["C"]["C1vsC2"] = {str(c): cmp_routers(("C1", c), ("C2", c), ("C1", c)) for c in cs}
# 2a: A1 vs A2 router on the same input (both inputs), and A vs official 1620 router (router weights from DCP)
if "A1" in ARMS and "A2" in ARMS:
    cs = sorted(set(PTS["A1"]) & set(PTS["A2"]))
    S["routing"]["A1vsA2"] = {str(c): {"onA1": cmp_routers(("A1", c), ("A2", c), ("A1", c)),
                                        "onA2": cmp_routers(("A1", c), ("A2", c), ("A2", c))} for c in cs}
off_ok = os.path.exists(f"{a.root}/ckpt/iter_0001620/_fetched.json")
if off_ok:
    for x in ("A1", "A2", "B1", "B2", "C1", "C2"):
        if x in ARMS:
            S["routing"]["A_vs_off1620"][x] = {str(c): cmp_routers((x, c), ("OFF", 1620), (x, c)) for c in PTS[x]}
    S["routing"]["S_vs_off1620_onS"] = cmp_routers(("A1", 0), ("OFF", 1620), ("A1", 0))
# 2c: frozen arms: effective router W diag(g) drift (g trains) — routing change vs S on own input + gain change
for x in ("B1", "B2", "D", "G"):
    if x in ARMS:
        s0 = ("A1", 0) if x != "D" else ("E", 0)
        if s0[0] not in ARMS:
            continue
        g0 = pt(*s0)[1]
        S["routing"]["B_gain"][x] = {str(c): {"rel_gain_change_mid": float(np.mean([float((pt(x, c)[1][l] - g0[l]).norm() / g0[l].norm()) for l in MID])),
                                              "eff_router_rowcos_mid": float(np.mean([float(torch.nn.functional.cosine_similarity(weff(x, c, l), weff(*s0, l), dim=1).mean()) for l in MID])),
                                              "routing_vs_S_on_own_input": S["routing"]["vsS"][x][str(c)]["top6"]} for c in PTS[x]}
# load / top-6 probability sum / margin, per arm per point (main view, mid band)
for x in ARMS:
    S["routing"]["load"][x] = {}
    for c in PTS[x]:
        mx, ent, ps = [], [], []
        for l in MID:
            z = xhat(x, c, l) @ weff(x, c, l).T; p = torch.softmax(z, -1); tk = p.topk(K, -1)
            f = torch.bincount(tk.indices.reshape(-1), minlength=E).double(); f = f / f.sum()
            mx.append(float(f.max() * E)); ent.append(float(-(f.clamp_min(1e-12) * f.clamp_min(1e-12).log2()).sum())); ps.append(float(tk.values.sum(-1).mean()))
        S["routing"]["load"][x][str(c)] = {"maxload_xE": float(np.mean(mx)), "load_entropy_bits": float(np.mean(ent)), "top6_psum": float(np.mean(ps))}
log("routing done")

# 2d: O/H/R per arm vs its own latest point (e191 definitions), mid band, top-1 / top-6 with CI
S["decomp"] = {}
for x in ARMS:
    cs = PTS[x]; Fp = cs[-1]
    if len(cs) < 2:
        continue
    rec = {}
    for c in cs:
        comp = {k: [0, 0] for k in ("O", "H", "R")}
        for l in MID:
            Xt, XF = xhat(x, c, l), xhat(x, Fp, l); Wt, WF = weff(x, c, l), weff(x, Fp, l)
            TFF = top(XF, WF)
            for k, A in (("O", top(Xt, Wt)), ("H", top(Xt, WF)), ("R", top(XF, Wt))):
                t1, t6 = agree(A, TFF); comp[k][0] = comp[k][0] + t1 / len(MID); comp[k][1] = comp[k][1] + t6 / len(MID)
        rec[str(c)] = {k: {"top1": ci_tok(v[0]), "top6": ci_tok(v[1])} for k, v in comp.items()}
    S["decomp"][x] = {"endpoint": Fp, "toF": rec}
for x in ARMS:                                    # vs official endpoint, only once the official dump exists
    for it in (1620, 2160):
        if has_official_dump(it):
            rec = {}
            for c in PTS[x]:
                comp = {k: [0, 0] for k in ("O", "H", "R")}
                for l in MID:
                    Xt, XF = xhat(x, c, l), xhat("OFF", it, l); Wt, WF = weff(x, c, l), weff("OFF", it, l)
                    TFF = top(XF, WF)
                    for k, A in (("O", top(Xt, Wt)), ("H", top(Xt, WF)), ("R", top(XF, Wt))):
                        t1, t6 = agree(A, TFF); comp[k][0] = comp[k][0] + t1 / len(MID); comp[k][1] = comp[k][1] + t6 / len(MID)
                rec[str(c)] = {k: {"top1": ci_tok(v[0]), "top6": ci_tok(v[1])} for k, v in comp.items()}
            S["decomp"].setdefault("vs_official", {})[f"{x}->off{it}"] = rec
log("decomp done")

# ================================================================== §3 geometry B vs A (same seed, same point)
S["geometry"] = {}
CKA_SUB = torch.tensor(np.sort(np.random.default_rng(1922).choice(NV, min(4000, NV), replace=False)))
for x, y in (("B1", "A1"), ("B2", "A2"), ("C1", "A1"), ("C2", "A2"), ("D", "E"), ("A2", "A1")):
    if x not in ARMS or y not in ARMS:
        continue
    rec = {}
    for c in sorted(set(PTS[x]) & set(PTS[y])):
        ci_, co_, ki, ko, cf = [], [], [], [], []
        for l in MID:
            Wc = weff(y, c, l).double(); Wc = Wc - Wc.mean(0, keepdim=True)
            _, Sv, Vh = torch.linalg.svd(Wc, full_matrices=False); r = int((Sv > 1e-6 * Sv[0]).sum()); V = Vh[:r].T.float()
            xa, xb = xhat(y, c, l), xhat(x, c, l)
            ia, ib = xa @ V @ V.T, xb @ V @ V.T; oa, ob = xa - ia, xb - ib
            cs_ = torch.nn.functional.cosine_similarity
            cf.append(float(cs_(xa, xb, dim=1).mean())); ci_.append(float(cs_(ia, ib, dim=1).mean())); co_.append(float(cs_(oa, ob, dim=1).mean()))
            ki.append(lincka(ia[CKA_SUB].double(), ib[CKA_SUB].double())); ko.append(lincka(oa[CKA_SUB].double(), ob[CKA_SUB].double()))
        rec[str(c)] = {"cos_full": float(np.mean(cf)), "cos_in": float(np.mean(ci_)), "cos_out": float(np.mean(co_)),
                       "cka_in": float(np.mean(ki)), "cka_out": float(np.mean(ko))}
    S["geometry"][f"{x}~{y}"] = rec
log("geometry done")

# ================================================================== §4 token classes (DCLM held-out), §5 raw examples
from tokenizers import Tokenizer  # noqa: E402
tk = Tokenizer.from_file(f"{a.root}/tok/pythia12b/tokenizer.json")
ev = np.fromfile(f"{a.root}/dclm/eval_dclm.u16", np.uint16)
nw = (len(ev) - 1) // SEQ
Wi = np.stack([ev[j * SEQ:j * SEQ + SEQ + 1] for j in range(nw)]).astype(np.int64)       # [1024, 2049]
inp_, tgt_ = Wi[:, :-1], Wi[:, 1:]
cnt = np.bincount(np.fromfile(f"{a.root}/dclm/pool_P1.u16", np.uint16, count=100_000_000), minlength=50304).astype(np.float64)
V = tk.get_vocab_size(); toks = [tk.id_to_token(i) or "" for i in range(max(V, 50304))]
frag = np.array([(not t.startswith("Ġ")) and t.isalpha() for t in toks[:50304]])
fq_t = cnt[tgt_]; qs = np.quantile(fq_t, [.2, .4, .6, .8]); fqq = np.searchsorted(qs, fq_t, side="right")
CLS = {"pos0": np.broadcast_to(np.arange(SEQ) == 0, tgt_.shape), "doc_start(after EOD)": inp_ == 0,
       "word_fragment(no leading space, alphabetic)": frag[tgt_], "word_initial": ~frag[tgt_] & (inp_ != 0)}
for q in range(5):
    CLS[f"freq_q{q + 1}(target, P1 counts)"] = fqq == q
HCLS = {}


def hclasses(arm):
    """H(e|id) tertile masks from the DCLM-held-out routing of `arm` at its last stage-1 point (e192_hroute.py):
    entropy (bits) of the top-1 expert given the input token id, mean over mid layers; ids with >= 5 occurrences."""
    if arm in HCLS:
        return HCLS[arm]
    f = f"{a.root}/hroute/{arm}_c0540.npy"
    if not os.path.exists(f):
        HCLS[arm] = None; return None
    R = np.load(f, mmap_mode="r"); ids = inp_.ravel(); Hs = np.zeros(50304); n_id = np.bincount(ids, minlength=50304)
    for l in MID:
        t1 = np.asarray(R[l][..., 0]).ravel().astype(np.int64)
        J = np.bincount(ids * E + t1, minlength=50304 * E).reshape(50304, E).astype(np.float64)
        P = J / np.maximum(J.sum(1, keepdims=True), 1)
        Hs += -(np.where(P > 0, P * np.log2(np.where(P > 0, P, 1)), 0)).sum(1) / len(MID)
    ok = n_id[ids] >= 5; Ht = Hs[ids]; cuts = np.quantile(Ht[ok], [1 / 3, 2 / 3])
    m = {"H(e|id) low": (ok & (Ht <= cuts[0])).reshape(inp_.shape), "H(e|id) mid": (ok & (Ht > cuts[0]) & (Ht <= cuts[1])).reshape(inp_.shape),
         "H(e|id) high": (ok & (Ht > cuts[1])).reshape(inp_.shape)}
    HCLS[arm] = (m, cuts.tolist(), float(ok.mean()))
    return HCLS[arm]


HREF = {"B1-A1": "A1", "B2-A2": "A2", "C1-A1": "A1", "C2-A2": "A2", "D-E": "E", "A1-A2": "A1"}
if not all(os.path.exists(f"{a.root}/hroute/{x}_c0540.npy") for x in ("A1", "A2", "E")):
    S["pending"].append("readout 4 H(e|id) stratum: hroute files missing for some of A1/A2/E (e192_hroute.py)")


def cls_ci(dv, mask):
    """per-window mean of dv over mask tokens -> token-weighted mean + window bootstrap CI"""
    s = (dv * mask).sum(1); n = mask.sum(1).astype(np.float64); bi = boot_idx(len(s))
    b = s[bi].sum(1) / np.maximum(n[bi].sum(1), 1)
    return [float(s.sum() / max(n.sum(), 1)), float(np.quantile(b, .025)), float(np.quantile(b, .975)), int(n.sum())]


S["token_classes"] = {}; S["examples"] = {}
for p, q in [("B1", "A1"), ("B2", "A2"), ("C1", "A1"), ("C2", "A2"), ("D", "E"), FLOOR]:
    if p in ARMS and q in ARMS:
        cs = sorted(set(PTS[p]) & set(PTS[q]))
        c = cs[-1]; dv = nll(p, c, "dclm") - nll(q, c, "dclm")
        S["token_classes"][f"{p}-{q}"] = {"c": c, **{k: cls_ci(dv, m) for k, m in CLS.items()}}
        hc = hclasses(HREF[f"{p}-{q}"])
        if hc is not None:
            S["token_classes"][f"{p}-{q}"].update({k: cls_ci(dv, m) for k, m in hc[0].items()})
            S["token_classes"][f"{p}-{q}"]["H_ref"] = {"arm": HREF[f"{p}-{q}"], "tertile_cuts_bits": hc[1], "coverage": hc[2]}
# raw examples: B - A averaged over the seed pairs at the latest common point
pairsB = [(p, q) for p, q in (("B1", "A1"), ("B2", "A2")) if p in ARMS and q in ARMS]
if pairsB:
    c = min(sorted(set(PTS[p]) & set(PTS[q]))[-1] for p, q in pairsB)
    dv = np.mean([nll(p, c, "dclm") - nll(q, c, "dclm") for p, q in pairsB], 0)
    flat = dv.ravel(); order = np.argsort(flat)

    def ex(i):
        w, j = divmod(int(i), SEQ)
        ctx = tk.decode(inp_[w, max(0, j - 15):j + 1].tolist()); t = tk.decode([int(tgt_[w, j])])
        return {"w": w, "pos": j, "diff": float(flat[i]), "ctx": ctx[-120:], "target": t}
    S["examples"] = {"c": c, "pairs": pairsB, "B_worse_than_A": [ex(i) for i in order[::-1][:20]], "B_better_than_A": [ex(i) for i in order[:20]]}
log("token classes done")

# ================================================================== §R replication / stability (POST-HOC, card 追加臂)
GN_T, JUMP_T = 5.0, 0.1                       # thresholds fixed in the card section 追加臂
S["events"] = {}
for x in ARMS:
    tr = TL[x][0]
    if not tr:
        continue
    hit = [i for i, r in enumerate(tr) if r["gn"] > GN_T or (i > 0 and r["lm"] - tr[i - 1]["lm"] > JUMP_T)]
    if ARMDEF[x][1] == "reset":                 # reset arms: the relearning transient is not a stability event by design
        hit = [i for i in hit if tr[i]["it"] > 54]
    ev, cur = [], []
    for i in hit:
        if cur and i - cur[-1] > 10:
            ev.append(cur); cur = []
        cur.append(i)
    if cur:
        ev.append(cur)
    out = []
    for e in ev:
        seg = tr[e[0]:e[-1] + 1]; pre = tr[max(0, e[0] - 20):e[0]]
        ml = np.array([r["maxload_l"] for r in seg])
        base = np.array([r["maxload_l"] for r in pre]).mean(0) if pre else np.ones(ml.shape[1])
        first_iter_layers = [int(j) + 1 for j in np.where(ml[0] > 3)[0]]
        out.append({"start_it": seg[0]["it"], "end_it": seg[-1]["it"], "n_flagged_iters": len(e), "peak_gn": float(max(r["gn"] for r in seg)),
                    "peak_lm": float(max(r["lm"] for r in seg)), "lm_before": float(np.mean([r["lm"] for r in pre])) if pre else None,
                    "peak_z": float(max(r["z"] for r in seg)), "peak_maxload_per_layer": ml.max(0).round(2).tolist(),
                    "pre_maxload_per_layer": base.round(2).tolist(), "layers_over_3x_at_first_flagged_iter": first_iter_layers})
    S["events"][x] = out
# per-iter detail of every frozen-arm event (and the paired A on the same iters)
S["event_iters"] = {}
for x, evs in S["events"].items():
    for k, e in enumerate(evs):
        y = {"B1": "A1", "B2": "A2", "B2r": "A2", "G": "A1", "G2": "A2", "B3": "A3", "B4": "A4", "B5": "A5", "D": "E"}.get(x)
        lo, hi = e["start_it"] - 18, e["end_it"] + 14
        rows = []
        tx = {r["it"]: r for r in TL[x][0]}; ty = {r["it"]: r for r in TL[y][0]} if y in TL else {}
        for it in range(lo, hi + 1):
            if it in tx:
                r = tx[it]; q = ty.get(it)
                rows.append({"it": it, "lm": r["lm"], "gn": r["gn"], "aux": r["aux"], "z": r["z"], "top6_psum_l": r["top6_psum_l"],
                             "maxload_l": r["maxload_l"], "loadent_l": r.get("loadent_l"), "lse2_l": r.get("lse2_l"),
                             "pair": y, "pair_lm": q["lm"] if q else None, "pair_gn": q["gn"] if q else None,
                             "pair_maxload": max(q["maxload_l"]) if q else None})
        S["event_iters"][f"{x}#{k + 1}"] = rows
# per-layer state at the save points around B2's event (dumps): load entropy, max load, top-6 mass, gain change vs S
S["b2_layers"] = {}
for x in ("B2", "A2", "B2r"):
    if x not in ARMS:
        continue
    for c in (270, 324, 378, 540):
        if c not in PTS[x]:
            continue
        rows = []
        for l in range(L):
            z = xhat(x, c, l) @ weff(x, c, l).T; p = torch.softmax(z, -1); tk = p.topk(K, -1)
            f = torch.bincount(tk.indices.reshape(-1), minlength=E).double(); f = f / f.sum()
            g0 = pt("A1", 0)[1][l]
            rows.append({"layer": l + 1, "load_entropy_bits": float(-(f.clamp_min(1e-12) * f.clamp_min(1e-12).log2()).sum()),
                         "maxload_xE": float(f.max() * E), "top6_psum": float(tk.values.sum(-1).mean()),
                         "lse2": float(torch.logsumexp(z, -1).pow(2).mean()), "rel_gain_change_vs_S": float((pt(x, c)[1][l] - g0).norm() / g0.norm())})
        S["b2_layers"][f"{x}@c{c}"] = rows
# B2 vs B2r: identical config rerun — per-iter train-loss difference
if "B2" in ARMS and "B2r" in ARMS:
    t2 = {r["it"]: r["lm"] for r in TL["B2"][0]}; tr_ = {r["it"]: r["lm"] for r in TL["B2r"][0]}
    its = sorted(set(t2) & set(tr_)); d = np.array([tr_[i] - t2[i] for i in its])
    pre = [k for k, i in enumerate(its) if i < 318]
    S["b2_vs_b2r"] = {"n_common_iters": len(its), "iter1": [t2.get(1), tr_.get(1)],
                      "mean_abs_diff_before_318": float(np.abs(d[pre]).mean()) if pre else None,
                      "max_abs_diff_before_318": float(np.abs(d[pre]).max()) if pre else None,
                      "B2r_events": S["events"].get("B2r", []), "diff_by_block": {f"{its[k]}-{its[min(k + 53, len(its) - 1)]}": float(d[k:k + 54].mean()) for k in range(0, len(its), 54)}}
# floor over all A seeds: range of pairwise A differences at each c (DCLM)
As = [x for x in ("A1", "A2", "A3", "A4", "A5") if x in ARMS]
S["nll"]["floor_allA"] = {}
for c in sorted(set.intersection(*[set(PTS[x]) for x in As])) if len(As) >= 2 else []:
    ds = [float((nll(p, c, "dclm") - nll(q, c, "dclm")).mean()) for i, p in enumerate(As) for q in As[i + 1:]]
    S["nll"]["floor_allA"][str(c)] = {"n_pairs": len(ds), "min": min(ds), "max": max(ds), "max_abs": max(abs(v) for v in ds), "arms": As}
# p6: third-shard held-out stream
S["p6"] = {}
p6d = f"{a.root}/p6"
if os.path.isdir(p6d):
    Z = {os.path.basename(f)[:-8]: np.load(f) for f in glob.glob(f"{p6d}/*_nll.npz")}
    for k, z in Z.items():
        S["p6"][k] = {s_: wci(z[s_].astype(np.float64)) for s_ in z.files}
    for x, o in (("A1_c0540", "off1620"), ("A2_c0540", "off1620"), ("E_c0540", "off1080")):
        if x in Z and o in Z:
            S["p6"][f"{x} − {o}"] = {s_: wci(Z[x][s_].astype(np.float64) - Z[o][s_].astype(np.float64)) for s_ in Z[x].files}
if not S["p6"]:
    S["pending"].append("p6 third-shard evals (e192_p6.py; queued on fvcrc20 GPU 3 after F)")
log("replication / stability done")

# ---- R7 (moved from the 11-18 hand computation): F's router displacement vs A1's, routing agreement, logit scale
S["r7"] = {}
if "F" in ARMS and "A1" in ARMS and 540 in PTS["F"] and 540 in PTS["A1"]:
    WS_, WA_, WF_ = pt("A1", 0)[0], pt("A1", 540)[0], pt("F", 540)[0]
    S["r7"]["F_dW_cos_vs_A1"] = [float(torch.nn.functional.cosine_similarity((WF_[l] - WS_[l]).ravel(), (WA_[l] - WS_[l]).ravel(), dim=0)) for l in range(L)]
    S["r7"]["F_dW_norm_ratio"] = [float((WF_[l] - WS_[l]).norm() / (WA_[l] - WS_[l]).norm()) for l in range(L)]
    S["r7"]["agree_on_A1_input"] = {"F_vs_A1": cmp_routers(("F", 540), ("A1", 540), ("A1", 540), False)["top6"],
                                    "S_vs_A1": cmp_routers(("A1", 0), ("A1", 540), ("A1", 540), False)["top6"],
                                    "F_vs_S": cmp_routers(("F", 540), ("A1", 0), ("A1", 540), False)["top6"]}
S["r7"]["lse2"] = {}
for x in ("A1", "B1", "F", "G", "G2", "B2r"):
    for c in (0, 540, 1080):
        if x in ARMS and c in PTS[x]:
            v = [float(torch.logsumexp(xhat(x, c, l) @ weff(x, c, l).T, -1).pow(2).mean()) for l in range(L)]
            S["r7"]["lse2"][f"{x}@c{c}"] = {"per_layer": v, "mid": float(np.mean([v[l] for l in MID]))}

# ---- round 3: per-layer relearned / frozen router readouts
S["round3"] = {}
for x, y, z in (("CL1_1", "A1", "CL1_2"), ("CL1_2", "A2", "CL1_1"), ("CD_1", "A1", "CD_2"), ("CD_2", "A2", "CD_1")):
    if x not in ARMS or y not in ARMS:
        continue
    rec = {}
    for c in PTS[x]:
        r = {"vsS_onS": [v[1] for v in cmp_routers((x, c), ("A1", 0), ("A1", 0), False)["per_layer"]]}
        if c in PTS[y]:
            r["vsA_same_iter"] = [v[1] for v in cmp_routers((x, c), (y, c), (x, c), False)["per_layer"]]
            r["A_vsS"] = [v[1] for v in cmp_routers((y, c), ("A1", 0), (y, c), False)["per_layer"]]
        if z in ARMS and c in PTS[z]:
            r["vs_other_seed"] = [v[1] for v in cmp_routers((x, c), (z, c), (x, c), False)["per_layer"]]
        rec[str(c)] = r
    S["round3"][x] = {"reset_layers": RESET_L[x], "pair": y, "points": rec}
for x, y in (("DL1free", "E"), ("DL1only", "E"), ("D2", "E2")):
    if x not in ARMS or y not in ARMS:
        continue
    rec = {}
    for c in sorted(set(PTS[x]) & set(PTS[y])):
        rec[str(c)] = {"vsE_same_iter": [v[1] for v in cmp_routers((x, c), (y, c), (x, c), False)["per_layer"]],
                       "vs_start": [v[1] for v in cmp_routers((x, c), ("E", 0), (x, c), False)["per_layer"]],
                       "maxabs_W_vs_start": [float((pt(x, c)[0][l] - pt("E", 0)[0][l]).abs().max()) for l in range(L)]}
    S["round3"][x] = {"frozen_layers": FROZEN_L[x], "pair": y, "points": rec}
log("round 3 done")

json.dump(S, open(f"{a.out}/summary.json", "w"), indent=1, ensure_ascii=False)

# ================================================================== figures
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
COL = {"A1": "#1f77b4", "A2": "#6baed6", "B1": "#d62728", "B2": "#fc9272", "C1": "#2ca02c", "C2": "#a1d99b", "D": "#9467bd",
       "E": "#bcbddc", "F": "#8c564b", "G": "#e377c2"}
tokB = lambda x, c: (ARMDEF[x][0] + c) * GB * SEQ / 1e9

fig, ax = plt.subplots(1, 2, figsize=(11, 4))
for i, k in enumerate(("dclm", "wikitext")):
    for x in ARMS:
        cs = PTS[x]; ax[i].plot([tokB(x, c) for c in cs], [S["nll"]["curves"][x][str(c)][k][0] for c in cs], "o-", ms=3, color=COL.get(x, "gray"), label=x)
    for it, v in S["nll"]["official"].items():
        ax[i].plot(int(it) * GB * SEQ / 1e9, v[k][0], "k*", ms=9)
    ax[i].set_xlabel("training tokens (B)"); ax[i].set_ylabel(f"held-out NLL ({k})"); ax[i].set_title(k)
ax[0].legend(fontsize=7, ncol=2)
fig.suptitle("E192 held-out NLL per arm (stars: official checkpoints)" + ("  [INTERIM]" if INTERIM else ""))
fig.tight_layout(); fig.savefig(f"{a.out}/fig_nll.png", dpi=130); plt.close(fig)

fig, axs = plt.subplots(2, 2, figsize=(11, 8))
allp = dict(S["nll"]["pairs"]); allp.update({f"floor {kk}": vv for kk, vv in S["nll"]["floor"].items()})
for row, keep in enumerate((lambda n: True, lambda n: not n.startswith("C"))):   # bottom row: without the reset arms
    for i, k in enumerate(("dclm", "wikitext")):
        ax_ = axs[row, i]
        for name, d in allp.items():
            cs = sorted(int(c) for c in d)
            if not cs or not keep(name):
                continue
            m = np.array([d[str(c)][k] for c in cs]); xs = [c * GB * SEQ / 1e9 for c in cs]
            col = "k" if name.startswith("floor") else COL.get(name.split("-")[0], "gray")
            ax_.plot(xs, m[:, 0], marker="o", ms=3, color=col, label=name, ls="--" if name.startswith("floor") else "-")
            ax_.fill_between(xs, m[:, 1], m[:, 2], color=col, alpha=.15)
        ax_.axhline(0, color="gray", lw=.5); ax_.set_xlabel("continued-training tokens (B)")
        ax_.set_ylabel(f"paired NLL difference ({k})" + ("" if row == 0 else ", reset arms hidden"))
axs[0, 0].legend(fontsize=7); axs[1, 0].legend(fontsize=7)
fig.suptitle("E192 paired differences with 95% window-bootstrap CI" + ("  [INTERIM]" if INTERIM else ""))
fig.tight_layout(); fig.savefig(f"{a.out}/fig_diff.png", dpi=130); plt.close(fig)

fig, ax = plt.subplots(1, 3, figsize=(15, 4))
for x in ARMS:
    d = S["routing"]["vsS"].get(x, {})
    cs = sorted(int(c) for c in d)
    ax[0].plot([c * GB * SEQ / 1e9 for c in cs], [d[str(c)]["top6"][0] for c in cs], "o-", ms=3, color=COL.get(x, "gray"), label=x)
ax[0].set_title("router vs start router (own input), top-6, mid"); ax[0].legend(fontsize=7)
for x in ("C1", "C2"):
    if x in S["routing"]["C"]:
        for key, ls in (("vsS_onS_input", "-"), ("vsA_same_iter", "--"), ("vsA_latest", ":")):
            d = S["routing"]["C"][x][key]; cs = sorted(int(c) for c in d)
            ax[1].plot([c * GB * SEQ / 1e9 for c in cs], [d[str(c)]["top6"][0] for c in cs], ls, marker="o", ms=3, color=COL.get(x, "gray"), label=f"{x} {key}")
            ax[1].plot([c * GB * SEQ / 1e9 for c in cs], [d[str(c)]["top6_hung"][0] for c in cs], ls, marker="x", ms=3, color=COL.get(x, "gray"), alpha=.5)
ax[1].axhline(K / E, color="gray", lw=.5); ax[1].set_title("reset router relearning (o identity, x Hungarian)"); ax[1].legend(fontsize=6)
for x, d in S["routing"]["B_gain"].items():
    cs = sorted(int(c) for c in d)
    ax[2].plot([c * GB * SEQ / 1e9 for c in cs], [d[str(c)]["rel_gain_change_mid"] for c in cs], "o-", ms=3, color=COL.get(x, "gray"), label=f"{x} |dg|/|g|")
ax[2].set_title("frozen arms: pre-MLP gain change"); ax[2].legend(fontsize=7)
for i in range(3):
    ax[i].set_xlabel("continued-training tokens (B)")
fig.tight_layout(); fig.savefig(f"{a.out}/fig_routing.png", dpi=130); plt.close(fig)

fig, ax = plt.subplots(1, 3, figsize=(15, 4), sharey=True)
for i, k in enumerate(("O", "H", "R")):
    for x, d in S["decomp"].items():
        if x == "vs_official":
            continue
        cs = sorted(int(c) for c in d["toF"])
        ax[i].plot([c * GB * SEQ / 1e9 for c in cs], [d["toF"][str(c)][k]["top6"][0] for c in cs], "o-", ms=3, color=COL.get(x, "gray"), label=x)
    ax[i].set_title(f"{k} vs own latest point (top-6, mid)"); ax[i].set_xlabel("continued-training tokens (B)")
ax[0].legend(fontsize=7)
fig.tight_layout(); fig.savefig(f"{a.out}/fig_decomp.png", dpi=130); plt.close(fig)

fig, ax = plt.subplots(1, 2, figsize=(10, 4))
for name, d in S["geometry"].items():
    cs = sorted(int(c) for c in d); xs = [c * GB * SEQ / 1e9 for c in cs]
    col = COL.get(name.split("~")[0], "gray")
    ax[0].plot(xs, [d[str(c)]["cos_in"] for c in cs], "o-", ms=3, color=col, label=f"{name} in")
    ax[0].plot(xs, [d[str(c)]["cos_out"] for c in cs], "o--", ms=3, color=col, label=f"{name} out")
    ax[1].plot(xs, [d[str(c)]["cka_in"] for c in cs], "o-", ms=3, color=col, label=f"{name} in")
    ax[1].plot(xs, [d[str(c)]["cka_out"] for c in cs], "o--", ms=3, color=col, label=f"{name} out")
ax[0].set_title("per-token cosine of router inputs, in / out of readout subspace"); ax[1].set_title("linear CKA in / out")
ax[0].legend(fontsize=6)
fig.tight_layout(); fig.savefig(f"{a.out}/fig_geometry.png", dpi=130); plt.close(fig)

# ================================================================== tables.md
f3 = lambda v: f"{v[0]:.4f} [{v[1]:.4f}, {v[2]:.4f}]"
f3s = lambda v: f"{v[0]:+.4f} [{v[1]:+.4f}, {v[2]:+.4f}]"
f2 = lambda v: f"{v[0]:.3f} [{v[1]:.3f}, {v[2]:.3f}]"
T = []
T.append(f"# E192 读数表{'（中间点，未完成）' if INTERIM else ''}\n")
T.append(f"由 `division/scripts/e192_analyze.py` 生成（{time.strftime('%Y-%m-%d %H:%M')}）。卡：`division/experiments/E192-frozen-router-intervention.md`。"
         "不写判决表；CI = 95%，NLL 按 2048 窗口自助（配对差在窗口内先做差），路由按句聚类自助，1000 次。路由口径同 E191：有效路由器 W·diag(g)，"
         "x̂ = h/g，主视图 FLORES eng + UD（12,000 token），mid = MoE 第 2–7 层，top-6 重合 = |S∩S'|/6。c = 续训 iter（A/B/C 起点 1080，D/E 起点 540）。\n")
T.append("保存点：" + "；".join(f"{x} {PTS[x]}{' DONE' if DONE[x] else ''}" for x in ARMS) + "\n")
if S["pending"]:
    T.append("**尚未计算（缺输入）**：" + "；".join(S["pending"]) + "\n")
T.append("## §0 阳性对照 / 健全性\n")
for x, v in S["sanity"].get("C_c0000_vs_S", {}).items():
    T.append(f"- (p5) {x} 续训第 0 点（重置后）路由器 vs S 路由器（S 输入，mid）：top-6 恒等 {f2(v['top6'])}，匈牙利 {f2(v['top6_hung'])}，"
             f"top-1 {f2(v['top1'])}；负载乘积期望 {v['chance_top6_mid']:.3f}，均匀 6/64 = {K / E:.3f}")
for x, v in S["sanity"]["B_router_maxabs_vs_S"].items():
    T.append(f"- (p4) {x} 各保存点 router.weight 与起点的最大绝对差：" + ", ".join(f"c{c} {d:.1e}" for c, d in v.items())
             + f"；逐 iter 哈希不变：{S['train'][x]['router_unchanged_all']}")
for k, v in S["train"].items():
    if "-" in k:
        T.append(f"- 训练 loss {k}：iter 1 = {v['iter1'][0]:.4f} / {v['iter1'][1]:.4f}，前 5 iter 差 {v['diff_first5']}，"
                 f"逐 iter 变化的相关 {v['corr_of_iter_to_iter_changes']:.3f}，最近 10 iter 平均差 {v['mean_diff_last10']:+.4f}（n = {v['n_iter']}）")
T.append("- (p3) 前 54 iter 相邻最大跳变：" + "，".join(f"{x} {S['train'][x]['max_jump_first54']:.3f}" for x in ARMS if S['train'][x]['max_jump_first54'] is not None)
         + "；吞吐中位数（k token/s）：" + "，".join(f"{x} {S['train'][x]['tok_s_median'] / 1e3:.1f}" for x in ARMS if S['train'][x]['tok_s_median']))
T.append("\n### 训练稳定性（POST-HOC，11-18 看到 B2 c324 后加；逐 54 iter 块，第一个 micro batch 的最大负载 × E 取 8 层最大）\n")
T.append("| 臂 | iter 块 | 训练 loss 均值 | 梯度范数中位数 | 梯度范数最大 | z-loss 最大 | 最大负载 × E 最大 | 相邻跳变 > .1 次数 |\n|---|---|---|---|---|---|---|---|")
_m = lambda d: {k: v for k, v in d.items() if k not in HIDE}
for x, bl in _m(S["stability"]).items():
    for k, v in bl.items():
        T.append(f"| {x} | {k} | {v['lm_mean']:.4f} | {v['gn_median']:.3f} | {v['gn_max']:.2f} | {v['z_max']:.4f} | {v['maxload_max']:.2f} | {v['n_jump_gt_0.1']} |")
T.append("\n## §1 留出 NLL（读数 1）\n")
T.append("| 臂 | c | 官方 iter | DCLM 留出 | wikitext-103 test |\n|---|---|---|---|---|")
for x in [y for y in ARMS if y not in HIDE]:
    for c in PTS[x]:
        v = S["nll"]["curves"][x][str(c)]
        T.append(f"| {x} | {c} | {v['official_iter']} | {f3(v['dclm'])} | {f3(v['wikitext'])} |")
for it, v in S["nll"]["official"].items():
    T.append(f"| 官方 | — | {it} | {f3(v['dclm'])} | {f3(v['wikitext'])} |")
T.append("\n配对差（同数据种子，同一批窗口）与地板 |A1 − A2|：\n")
T.append("（阶段：c ≤ 540 = 阶段 1（池 P1）；c > 540 = 阶段 2（池 P2，只 A/B/C）；复制臂另见 §R）\n")
T.append("| 对比 | 阶段 | c | DCLM 差 | wikitext 差 |\n|---|---|---|---|---|")
for name, d in list(S["nll"]["pairs"].items()) + [(f"地板 {k}", v) for k, v in S["nll"]["floor"].items()]:
    if any(x in HIDE for x in name.replace("地板 ", "").split("-")):
        continue
    for c, v in d.items():
        T.append(f"| {name} | {1 if int(c) <= 540 else 2} | {c} | {f3s(v['dclm'])} | {f3s(v['wikitext'])} |")
for name, v in {k: v for k, v in S["nll"].get("vs_official", {}).items() if k.split("@")[0] not in HIDE}.items():
    T.append(f"| {name} − 官方 | — | {f3s(v['dclm'])} | {f3s(v['wikitext'])} |")
T.append("\n## §2 路由（读数 2）\n")
T.append("### 2·1 各臂路由器 vs 起点路由器（各自当前输入；1080 臂对 S，D/E 对 iter 540 路由器）\n")
T.append("| 臂 | c | top-6 恒等 | top-6 匈牙利 | top-1 恒等 | 偶遇 |\n|---|---|---|---|---|---|")
for x, d in _m(S["routing"]["vsS"]).items():
    for c, v in d.items():
        T.append(f"| {x} | {c} | {f2(v['top6'])} | {f2(v['top6_hung'])} | {f2(v['top1'])} | {v['chance_top6_mid']:.3f} |")
T.append("\n### 2b 重置路由器的重学（C）\n")
T.append("| 臂 | 对比 | c | top-6 恒等 | top-6 匈牙利（权重行余弦） | top-6 匈牙利（路由共现，POST-HOC） | top-1 恒等 | 偶遇 |\n|---|---|---|---|---|---|---|---|")
for x, dd in S["routing"]["C"].items():
    if x == "C1vsC2":
        for c, v in dd.items():
            T.append(f"| C1 vs C2 | 同 iter（C1 输入） | {c} | {f2(v['top6'])} | {f2(v['top6_hung'])} | {f2(v['top6_routhung_posthoc'])} | {f2(v['top1'])} | {v['chance_top6_mid']:.3f} |")
        continue
    for key, lab in (("vsS_onS_input", "vs S 路由器（S 输入）"), ("vsA_same_iter", "vs 同种子 A 同 iter（C 输入）"), ("vsA_latest", f"vs A 最新点 c{dd['A_latest']}（C 输入）")):
        for c, v in dd[key].items():
            T.append(f"| {x} | {lab} | {c} | {f2(v['top6'])} | {f2(v['top6_hung'])} | {f2(v['top6_routhung_posthoc'])} | {f2(v['top1'])} | {v['chance_top6_mid']:.3f} |")
T.append("\n### 2a 跨数据顺序的重现：A1 vs A2；各臂 vs 官方 iter 1620 路由器（权重取自官方 checkpoint，输入 = 各臂自身）\n")
T.append("| 对比 | c | top-6 恒等 | top-6 匈牙利 | top-1 |\n|---|---|---|---|---|")
for c, v in S["routing"]["A1vsA2"].items():
    T.append(f"| A1 vs A2（A1 输入） | {c} | {f2(v['onA1']['top6'])} | {f2(v['onA1']['top6_hung'])} | {f2(v['onA1']['top1'])} |")
    T.append(f"| A1 vs A2（A2 输入） | {c} | {f2(v['onA2']['top6'])} | {f2(v['onA2']['top6_hung'])} | {f2(v['onA2']['top1'])} |")
if "S_vs_off1620_onS" in S["routing"]:
    v = S["routing"]["S_vs_off1620_onS"]
    T.append(f"| S vs 官方 1620（S 输入） | — | {f2(v['top6'])} | {f2(v['top6_hung'])} | {f2(v['top1'])} |")
for x, d in S["routing"]["A_vs_off1620"].items():
    for c, v in d.items():
        T.append(f"| {x} vs 官方 1620 | {c} | {f2(v['top6'])} | {f2(v['top6_hung'])} | {f2(v['top1'])} |")
T.append("\n### 2c 冻结臂：有效路由器 W·diag(g) 的漂移（W 不变，g 在训）\n")
T.append("| 臂 | c | ‖Δg‖/‖g‖（mid） | 有效路由器行余弦 vs 起点 | 路由 vs 起点 top-6（自身输入） |\n|---|---|---|---|---|")
for x, d in S["routing"]["B_gain"].items():
    for c, v in d.items():
        T.append(f"| {x} | {c} | {v['rel_gain_change_mid']:.4f} | {v['eff_router_rowcos_mid']:.4f} | {f2(v['routing_vs_S_on_own_input'])} |")
T.append("\n### 2d O / H / R（对各臂自身最新点；e191 定义；mid，top-6，括号内 top-1）\n")
T.append("| 臂 | 终点 c | c | O | H | R |\n|---|---|---|---|---|---|")
for x, d in _m(S["decomp"]).items():
    if x == "vs_official":
        continue
    for c, v in d["toF"].items():
        T.append(f"| {x} | {d['endpoint']} | {c} | " + " | ".join(f"{f2(v[k]['top6'])} ({v[k]['top1'][0]:.3f})" for k in ("O", "H", "R")) + " |")
for name, d in S["decomp"].get("vs_official", {}).items():
    for c, v in d.items():
        T.append(f"| {name} | — | {c} | " + " | ".join(f"{f2(v[k]['top6'])} ({v[k]['top1'][0]:.3f})" for k in ("O", "H", "R")) + " |")
T.append("\n### 负载与 top-6 概率和（主视图，mid）\n")
T.append("| 臂 | c | 最大负载 × E | 负载熵（bit，均匀 6） | top-6 概率和 |\n|---|---|---|---|---|")
for x, d in _m(S["routing"]["load"]).items():
    for c, v in d.items():
        T.append(f"| {x} | {c} | {v['maxload_xE']:.3f} | {v['load_entropy_bits']:.3f} | {v['top6_psum']:.4f} |")
T.append("\n### 2e 从起点出发各自走了多远：路由器权重 vs 路由器输入（mid；1080 臂以 S 为起点，D/E 以官方 540）\n")
T.append("H_起点路由器 = 起点路由器作用于当前输入 vs 作用于起点输入的 top-6 重合（只由输入漂移造成的路由变化）。\n")
T.append("| 臂 | c | W 行余弦 | 有效路由器行余弦 | x̂ 逐 token 余弦 | x̂ 子空间内 | x̂ 子空间外 | H_起点路由器 top-6 | 路由器 vs 起点 top-6（当前输入） |\n|---|---|---|---|---|---|---|---|---|")
for x, d in _m(S["routing"].get("drift_from_start", {})).items():
    for c, v in d.items():
        T.append(f"| {x} | {c} | {v['W_rowcos']:.4f} | {v['Weff_rowcos']:.4f} | {v['xhat_cos']:.4f} | {v['xhat_cos_in']:.4f} | {v['xhat_cos_out']:.4f} | {f2(v['H_startrouter_top6'])} | {f2(S['routing']['vsS'][x][c]['top6'])} |")
cl = S["routing"]["C"]
if "C1" in cl and "A1vsA2" in S["routing"] and S["routing"]["A1vsA2"]:
    cL = max(int(c) for c in cl["C1"]["vsS_onS_input"])
    T.append(f"\n### 2b′ 逐层（c{cL}，top-6 恒等）：C 的重学路由器与它的自然上限\n")
    rows = []
    def pl(d, key="top6"):
        return [v[1] for v in d["per_layer"]]
    cols = []
    for x, y in (("C1", "A1"), ("C2", "A2")):
        if x in cl:
            cols.append((f"{x} vs S（S 输入）", pl(cl[x]["vsS_onS_input"][str(cL)])))
            if str(cL) in cl[x]["vsA_same_iter"]:
                cols.append((f"{x} vs {y} 同 iter", pl(cl[x]["vsA_same_iter"][str(cL)])))
    if "C1vsC2" in cl and str(cL) in cl["C1vsC2"]:
        cols.append(("C1 vs C2", pl(cl["C1vsC2"][str(cL)])))
    if str(cL) in S["routing"]["A1vsA2"]:
        cols.append(("上限：A1 vs A2 同 iter", pl(S["routing"]["A1vsA2"][str(cL)]["onA1"])))
    for x in ("A1", "A2"):
        if x in S["routing"]["vsS"] and str(cL) in S["routing"]["vsS"][x]:
            cols.append((f"上限：{x} vs S", pl(S["routing"]["vsS"][x][str(cL)])))
    T.append("| MoE 层 | " + " | ".join(n for n, _ in cols) + " |\n|" + "---|" * (len(cols) + 1))
    for l in range(L):
        T.append(f"| {l + 1}{'（mid）' if l in MID else ''} | " + " | ".join(f"{v[l]:.3f}" for _, v in cols) + " |")
if S["nll"].get("C_gap_rate"):
    T.append("\n### C − A 差距的收敛速度（DCLM，每 54 iter 的减少量与相邻比值；几何外推只是描述）\n")
    for name, v in S["nll"]["C_gap_rate"].items():
        T.append(f"- {name}：差距 " + " → ".join(f"{g:.4f}" for g in v["gap"]) + "；每段减少 " + ", ".join(f"{d:.4f}" for d in v["decrement_per_54"])
                 + f"；相邻比值 " + ", ".join(f"{r:.2f}" for r in v["ratio"]) + f"；最近 3 个比值均值 {v['ratio_last3_mean']:.3f}"
                 + (f"，按此几何外推 c1080 约 {v['geometric_projection_c1080']:.4f}、极限约 {v['geometric_limit']:.4f}" if v.get("geometric_limit") is not None else ""))
T.append("\n## §3 几何（读数 3）：同一 token 上路由器输入 x̂ 的相似度（读出子空间 = 参照臂有效路由器的中心化行空间）\n")
T.append("| 对 | c | cos 全空间 | cos 子空间内 | cos 子空间外 | CKA 内 | CKA 外 |\n|---|---|---|---|---|---|---|")
for name, d in S["geometry"].items():
    for c, v in d.items():
        T.append(f"| {name} | {c} | {v['cos_full']:.4f} | {v['cos_in']:.4f} | {v['cos_out']:.4f} | {v['cka_in']:.4f} | {v['cka_out']:.4f} |")
T.append("\n## §4 token 类（读数 4；DCLM 留出流，最新共同点；逐 token NLL 差，窗口自助 CI）\n")
names = list(CLS) + [k for k in ("H(e|id) low", "H(e|id) mid", "H(e|id) high") if any(k in v for v in S["token_classes"].values())]
T.append("| 对比 | c | " + " | ".join(names) + " |\n|" + "---|" * (len(names) + 2))
for k, v in S["token_classes"].items():
    T.append(f"| {k} | {v['c']} | " + " | ".join((f"{v[n][0]:+.4f} [{v[n][1]:+.4f}, {v[n][2]:+.4f}] (n={v[n][3]})" if n in v else "—") for n in names) + " |")
for k, v in S["token_classes"].items():
    if "H_ref" in v:
        T.append(f"- {k}：H(e∣id) 由 {v['H_ref']['arm']} 的 c0540 在 DCLM 留出流上算（top-1 专家给定输入 id 的熵，mid 均值，出现 ≥ 5 次的 id，覆盖 {v['H_ref']['coverage']:.3f}），三分位切点 {v['H_ref']['tertile_cuts_bits'][0]:.2f} / {v['H_ref']['tertile_cuts_bits'][1]:.2f} bit")
T.append("")
if S["examples"]:
    T.append(f"## §5 原始样例（读数 5；B − A，两对种子平均，c{S['examples']['c']}；DCLM 留出流）\n")
    for key, lab in (("B_worse_than_A", "B 比 A 差最多"), ("B_better_than_A", "B 比 A 好最多")):
        T.append(f"**{lab}**\n\n| 差 | 上下文 … ⟦目标⟧ |\n|---|---|")
        for e in S["examples"][key]:
            T.append(f"| {e['diff']:+.2f} | `{e['ctx'].replace('|', '¦').replace(chr(10), '⏎')}` ⟦{e['target'].replace('|', '¦').replace(chr(10), '⏎')}⟧ |")
        T.append("")
T.append("\n## §R 复制臂与稳定性事件（POST-HOC，卡\"追加臂\"一节；阈值：裁剪前梯度范数 > 5 或相邻 iter 训练 loss 跳变 > .1；重置臂前 54 iter 的重学瞬态不计）\n")
T.append("### R1 各臂事件（全部臂，含阶段 1 / 阶段 2 / 复制臂）\n")
T.append("| 臂 | 事件 | 起止 iter | 标记 iter 数 | 事件前 loss | 峰值 loss | 峰值梯度范数 | 峰值 z | 首个标记 iter 上 > 3× 负载的层 | 各层峰值最大负载 × E（层 1–8） |\n|---|---|---|---|---|---|---|---|---|---|")
for x, evs in S["events"].items():
    if not evs:
        T.append(f"| {x} | 无 | — | 0 | — | — | {max(r['gn'] for r in TL[x][0]):.2f}（全程最大） | — | — | — |")
    for k, e in enumerate(evs):
        T.append(f"| {x} | #{k + 1} | {e['start_it']}–{e['end_it']} | {e['n_flagged_iters']} | {e['lm_before'] if e['lm_before'] is None else round(e['lm_before'], 3)} | {e['peak_lm']:.3f} | {e['peak_gn']:.2f} | {e['peak_z']:.4f} | {e['layers_over_3x_at_first_flagged_iter']} | {e['peak_maxload_per_layer']} |")
T.append("\n### R2 配对 B − A（DCLM 留出，c540 / 各臂最新点）与全部 A 两两差范围\n")
T.append("| 对比 | c | DCLM 差 | wikitext 差 | 该配对有无事件 |\n|---|---|---|---|---|")
for p, q in [("B1", "A1"), ("B2", "A2"), ("B3", "A3"), ("B4", "A4"), ("B5", "A5"), ("B2r", "A2"), ("G2", "A2"), ("G2", "B2r"), ("B2r", "B2"), ("G", "B1")]:
    d = S["nll"]["pairs"].get(f"{p}-{q}", {})
    cs = [c for c in d if int(c) <= 540]
    if cs:
        c = max(cs, key=int); v = d[c]
        T.append(f"| {p}−{q} | {c} | {f3s(v['dclm'])} | {f3s(v['wikitext'])} | {p}: {len(S['events'].get(p, []))} 次，{q}: {len(S['events'].get(q, []))} 次 |")
for c, v in S["nll"]["floor_allA"].items():
    if int(c) in (54, 270, 540):
        T.append(f"| 地板：{len(v['arms'])} 个 A 的 {v['n_pairs']} 个两两差 | {c} | 范围 [{v['min']:+.4f}, {v['max']:+.4f}]，最大绝对 {v['max_abs']:.4f} | — | — |")
if "b2_vs_b2r" in S:
    v = S["b2_vs_b2r"]
    T.append(f"\n### R3 B2 vs B2r（完全相同配置重跑）\n\n- 共同 iter {v['n_common_iters']}；iter 1 loss {v['iter1']}；iter < 318 的逐 iter 训练 loss 差：平均绝对 {v['mean_abs_diff_before_318']}，最大绝对 {v['max_abs_diff_before_318']}；B2r 事件：{v['B2r_events'] or '无'}")
    T.append("- 逐 54 iter 块平均差（B2r − B2）：" + "，".join(f"{k} {d:+.4f}" for k, d in v["diff_by_block"].items()))
T.append("\n### R4 事件逐 iter 明细（事件前 18 iter 到事件后 14 iter；最大负载 / top-6 概率和为第一个 micro batch，层 1–8）\n")
for key, rows in S["event_iters"].items():
    x = key.split("#")[0]
    if ARMDEF.get(x, (0, ""))[1] not in ("frozen",) and x not in ("E",):
        continue
    T.append(f"**{key}**（对照 = {rows[0]['pair'] if rows else '—'}）\n")
    T.append("| iter | loss | 梯度范数 | aux | z | 最大负载 × E（层 1–8） | top-6 概率和（层 1–8） | 对照 loss | 对照梯度范数 | 对照最大负载 |\n|---|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        T.append(f"| {r['it']} | {r['lm']:.3f} | {r['gn']:.2f} | {r['aux']:.4f} | {r['z']:.4f} | {[round(v, 1) for v in r['maxload_l']]} | {[round(v, 2) for v in r['top6_psum_l']]} | "
                 + (f"{r['pair_lm']:.3f} | {r['pair_gn']:.2f} | {r['pair_maxload']:.1f} |" if r['pair_lm'] is not None else "— | — | — |"))
    T.append("")
if S["b2_layers"]:
    T.append("### R5 B2 事件前后保存点的逐层状态（主视图；c324 落在事件中，c270 在事件前）\n")
    T.append("| 臂@点 | 层 | 负载熵（bit） | 最大负载 × E | top-6 概率和 | lse² | ‖g − g_S‖/‖g_S‖ |\n|---|---|---|---|---|---|---|")
    for k, rows in S["b2_layers"].items():
        for r in rows:
            T.append(f"| {k} | {r['layer']} | {r['load_entropy_bits']:.3f} | {r['maxload_xE']:.2f} | {r['top6_psum']:.3f} | {r['lse2']:.3f} | {r['rel_gain_change_vs_S']:.4f} |")
if S["p6"]:
    T.append("\n### R6 (p6) 第三个分片上的留出 NLL（gs10 = 我们的留出流，gs05 = 第三分片；窗口自助 CI）\n")
    T.append("| 模型 / 差 | gs10 | gs05 |\n|---|---|---|")
    for k, v in S["p6"].items():
        fm = f3s if "−" in k else f3
        T.append(f"| {k} | {fm(v['dclm_gs10'])} | {fm(v['dclm_gs05'])} |")
T.append("\n### R2b 复制臂配对差逐点（DCLM 留出）\n")
T.append("| 对比 | c | DCLM 差 | wikitext 差 |\n|---|---|---|---|")
for name, d in S["nll"]["pairs"].items():
    if any(x in REPL for x in name.split("-")):
        for c, v in d.items():
            T.append(f"| {name} | {c} | {f3s(v['dclm'])} | {f3s(v['wikitext'])} |")
T.append("\n地板（全部 A 两两差，逐点）：" + "；".join(f"c{c} [{v['min']:+.4f}, {v['max']:+.4f}]（{v['n_pairs']} 对）" for c, v in S["nll"]["floor_allA"].items()))
if S["r7"]:
    T.append("\n### R7 F / G 的补充读数（主视图 mid，top-6 恒等）\n")
    if "F_dW_cos_vs_A1" in S["r7"]:
        T.append("- cos(W_F − W_S, W_A1 − W_S)（层 1–8）：" + " / ".join(f"{v:.3f}" for v in S["r7"]["F_dW_cos_vs_A1"])
                 + "；‖W_F − W_S‖ / ‖W_A1 − W_S‖：" + " / ".join(f"{v:.2f}" for v in S["r7"]["F_dW_norm_ratio"]))
        g_ = S["r7"]["agree_on_A1_input"]
        T.append(f"- A1@c540 输入上：F vs A1@c540 {f2(g_['F_vs_A1'])}；S vs A1@c540 {f2(g_['S_vs_A1'])}；F vs S {f2(g_['F_vs_S'])}")
    T.append("- 路由器 logits 尺度 mean lse²：" + "；".join(f"{k} mid {v['mid']:.3f}（层 1–8：{' / '.join(f'{u:.2f}' for u in v['per_layer'])}）" for k, v in S["r7"]["lse2"].items()))

# ------------------------------------------------------------------ §T round 3
T3 = [x for x in ROUND3 if x in ARMS]
if T3:
    T.append("\n## §T 第三轮（POST-HOC，卡\"B2r 的结果与第三轮\"一节；按层的路由器处理与 p6 官方数据续训）\n")
    T.append("### T1 留出 NLL 配对差（DCLM，逐点；与 C − A、D − E 并列）\n")
    T.append("| 对比 | c | DCLM 差 | wikitext 差 |\n|---|---|---|---|")
    for name in ("C1-A1", "CL1_1-A1", "CD_1-A1", "C2-A2", "CL1_2-A2", "CD_2-A2", "D-E", "DL1free-E", "DL1only-E", "D2-E2", "P6GS03-A1"):
        for c, v in S["nll"]["pairs"].get(name, {}).items():
            if int(c) <= 540:
                T.append(f"| {name} | {c} | {f3s(v['dclm'])} | {f3s(v['wikitext'])} |")
    T.append("\n### T2 逐层路由器（top-6 恒等，各臂最新点；重置层 / 冻结层加 *）\n")
    for x, d in S["round3"].items():
        c = max(d["points"], key=int); r = d["points"][c]; mark = set(d.get("reset_layers", d.get("frozen_layers", [])))
        T.append(f"**{x}**（c{c}，对照 {d['pair']}）\n")
        T.append("| 量 | " + " | ".join(f"{l}{'*' if l in mark else ''}" for l in range(1, L + 1)) + " |\n|" + "---|" * (L + 1))
        for k, v in r.items():
            T.append(f"| {k} | " + " | ".join(f"{u:.3f}" if isinstance(u, float) and u < 10 else f"{u:.1e}" for u in v) + " |")
        T.append("")
    T.append("### T3 第三轮各臂的留出 NLL、负载（主视图 mid）\n")
    T.append("| 臂 | c | DCLM | wikitext | 最大负载 × E | 负载熵 | top-6 概率和 |\n|---|---|---|---|---|---|---|")
    for x in T3:
        for c in PTS[x]:
            v = S["nll"]["curves"][x][str(c)]; ld = S["routing"]["load"][x][str(c)]
            T.append(f"| {x} | {c} | {f3(v['dclm'])} | {f3(v['wikitext'])} | {ld['maxload_xE']:.3f} | {ld['load_entropy_bits']:.3f} | {ld['top6_psum']:.4f} |")
if os.path.exists(f"{a.root}/p6/p6_diag.md"):                 # e192_p6diag.py output (POST-HOC, 11-18)
    T.append("\n" + open(f"{a.root}/p6/p6_diag.md").read())
open(f"{a.out}/tables.md", "w").write("\n".join(T) + "\n")
log("wrote", a.out)
