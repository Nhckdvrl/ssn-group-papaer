#!/usr/bin/env python3
"""E176: published single-model MoE expert-analysis readouts (OLMoE §5.1-5.3, ST-MoE §7, Shazeer/BASE/OpenMoE
top-token tables, Antoine expert POS-KL, DBES S_spec/R_eff/S_iso) recomputed on our 9 runs, at three levels:
  model level  : one number per run
  class level  : an expert-id-free profile per run (correlated across runs in e176_summarize.py)
  expert level : per-expert vectors after Hungarian matching (cross-fit: match on one half of the documents,
                 read out on the other half, both directions averaged)
Uses only S{l} (top-8 expert ids of the 29,551 anchors, word-final token) from the E167 routing cache.

Usage: e176_readouts.py [NPROC]  -> results/e176/runs.json, results/e176/pairs.json
"""
import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
import collections
import itertools
import json
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from scipy.optimize import linear_sum_assignment
from scipy.stats import spearmanr

WB = Path(__file__).resolve().parents[1]
CAP = Path.home() / "mechpop_cache/e167_analysis/routing"
OUT = WB / "results/e176"
K, E, NL = 8, 64, 12
T = 3200000000
SAT_T = [0, 25000000, 50000000, 100000000, 200000000, 400000000, 800000000, 1600000000]
T_SAT = 50000000      # the "~1% of pretraining" checkpoint (1.6% of 3.2B)
T_WARM = 400000000    # inside warmup (warmup ends at 5.24e8 tokens)
INITS = [f"I{i}D0" for i in range(6)]
RUNS = INITS + ["I0D1", "I1D1", "I4D0R"]
GENRES = ["answers", "email", "newsgroup", "reviews", "weblog"]

P = np.load(CAP / "pairs.npz")
aw = P["anchor_word"]
upos = P["anchor_upos"]
form = P["anchor_type"].astype(str)
n = len(aw)
ann = json.load(open(WB / "results/e167/ud_annotations.json"))
genre = np.array([GENRES.index(ann[int(w)]["genre"]) for w in aw])
doc = np.array([ann[int(w)]["doc_id"] for w in aw])
cnt = collections.Counter(upos)
PROF = sorted(u for u in cnt if cnt[u] >= 200)
ucls = np.array([PROF.index(u) if u in PROF else -1 for u in upos])
UALL = sorted(cnt)
uall = np.array([UALL.index(u) for u in upos])
FORMS = sorted(set(form))
fidx = np.array([FORMS.index(f) for f in form]) if len(FORMS) < 5000 else None
nf = np.bincount(fidx, minlength=len(FORMS))
# cross-fit halves by document (seed 176)
udoc = sorted(set(doc))
rng = np.random.default_rng(176)
half_of_doc = dict(zip(udoc, rng.permutation(len(udoc)) % 2))
half = np.array([half_of_doc[d] for d in doc])
HALVES = [np.where(half == 0)[0], np.where(half == 1)[0]]


def load(run, t):
    Z = np.load(CAP / f"{run}__ckpt_{t}.npz")
    return [Z[f"S{l}"].astype(np.int64) for l in range(NL)]


def mh(S):
    X = np.zeros((len(S), E), np.float32)
    np.put_along_axis(X, S, 1.0, 1)
    return X


# ---------------- per-expert / per-class quantities on a token subset ----------------
def coact(S):
    X = mh(S)
    M = X.T @ X
    d = np.diag(M).copy()
    C = M / np.maximum(d[:, None], 1)
    np.fill_diagonal(C, np.nan)
    return C


def genre_spec(S, g):
    """spec(E,D) = slots of D's tokens on E / N_D (sums to 8 over E); returns (E,5) spec, (E,) overall"""
    sp = np.zeros((E, len(GENRES)))
    for D in range(len(GENRES)):
        m = g == D
        sp[:, D] = np.bincount(S[m].ravel(), minlength=E) / max(m.sum(), 1)
    allr = np.bincount(S.ravel(), minlength=E) / len(S)
    return sp, allr


def class_top1_dist(s1, cl, ncl):
    """P(e|c) from top-1 ids: (ncl, E)"""
    m = cl >= 0
    M = np.bincount(cl[m] * E + s1[m], minlength=ncl * E).reshape(ncl, E).astype(float)
    return M / np.maximum(M.sum(1, keepdims=True), 1)


def entropy(p):
    q = p[p > 0]
    return float(-(q * np.log(q)).sum())


def form_counts(s1, fi):
    return np.bincount(fi * E + s1, minlength=len(FORMS) * E).reshape(len(FORMS), E)


def top10(Fc):
    """per expert: set of the 10 forms with most top-1 assignments (ties -> lower form index)"""
    out = []
    for e in range(E):
        c = Fc[:, e]
        o = np.lexsort((np.arange(len(c)), -c))[:10]
        out.append(set(int(i) for i in o if c[i] > 0))
    return out


def jacc(a, b):
    return len(a & b) / len(a | b) if (a | b) else np.nan


def expert_pos_kl(S, ua):
    M = np.zeros((len(UALL), E))
    for slot in range(K):
        M += np.bincount(ua * E + S[:, slot], minlength=len(UALL) * E).reshape(len(UALL), E)
    pc = M.sum(1) / M.sum()
    pce = M / np.maximum(M.sum(0, keepdims=True), 1)
    kl = np.array([np.sum(np.where(pce[:, e] > 0, pce[:, e] * np.log(np.maximum(pce[:, e], 1e-300) / pc), 0)) for e in range(E)])
    return kl


def dbes(Sl, g):
    """S_spec, R_eff per genre, S_iso and per-genre-pair 1-cos; Sl = list over layers of (n,8) ids"""
    Pm = []
    for D in range(len(GENRES)):
        m = g == D
        M = np.stack([np.bincount(S[m].ravel(), minlength=E) for S in Sl]).astype(float)   # L x E
        Pm.append(M / M.sum(1, keepdims=True))
    U = np.full(E, 1 / E)
    sspec = [float(np.mean([np.sum(p[p > 0] * np.log(p[p > 0] / U[p > 0])) for p in Pr])) for Pr in Pm]
    reff = []
    for Pr in Pm:
        s = np.linalg.svd(Pr, compute_uv=False)
        q = s / s.sum()
        reff.append(float(np.exp(-(q[q > 0] * np.log(q[q > 0])).sum()) / min(Pr.shape)))
    pairs = {}
    for a, b in itertools.combinations(range(len(GENRES)), 2):
        va, vb = Pm[a].ravel(), Pm[b].ravel()
        pairs[f"{GENRES[a]}|{GENRES[b]}"] = float(1 - va @ vb / np.linalg.norm(va) / np.linalg.norm(vb))
    return {"S_spec": float(np.mean(sspec)), "S_spec_genre": dict(zip(GENRES, sspec)), "R_eff": float(np.mean(reff)),
            "R_eff_genre": dict(zip(GENRES, reff)), "S_iso": float(np.mean(list(pairs.values()))), "iso_pair": pairs}


# ---------------- per run ----------------
def per_run(args):
    run, t, with_sat = args
    S = load(run, t)
    r = {"run": run, "t": t}
    if with_sat:
        sat8, sat1, sat_upos = {}, {}, {}
        for tt in SAT_T:
            St = load(run, tt)
            sat8[tt] = [float((mh(St[l]) * mh(S[l])).sum(1).mean() / K) for l in range(NL)]
            sat1[tt] = [float(np.mean(St[l][:, 0] == S[l][:, 0])) for l in range(NL)]
            if tt in (0, T_SAT):
                prof = []
                for l in range(NL):
                    ov = (mh(St[l]) * mh(S[l])).sum(1) / K
                    prof.append([float(ov[ucls == c].mean()) for c in range(len(PROF))])
                sat_upos[tt] = prof
        r["sat_k8"], r["sat_k1"], r["sat_upos"] = sat8, sat1, sat_upos
    # #2 co-activation
    strong, maxco = [], []
    for l in range(NL):
        C = coact(S[l])
        off = C[~np.isnan(C)]
        strong.append(float(np.mean(off >= 0.5)))
        maxco.append(float(np.nanmax(C, 1).mean()))
    r["coact_strong_frac"], r["coact_maxmean"] = strong, maxco
    r["coact_max"] = [float(np.nanmax(coact(S[l]))) for l in range(NL)]
    # #3 domain specialisation
    liftmax, liftmax_any, dev = [], [], []
    for l in range(NL):
        sp, allr = genre_spec(S[l], genre)
        lift = np.where(allr[:, None] > 0, sp / np.maximum(allr[:, None], 1e-12), np.nan)
        liftmax.append(float(np.nanmean(np.nanmax(lift, 1))))
        liftmax_any.append(float(np.nanmax(lift)))
        dev.append([float(0.5 * np.abs(sp[:, D] - allr).sum()) for D in range(len(GENRES))])
    r["genre_liftmax_mean"], r["genre_lift_max"], r["genre_dev"] = liftmax, liftmax_any, dev
    r["genre_n"] = dict(zip(GENRES, np.bincount(genre, minlength=5).tolist()))
    # #6 class routing entropy (top-1) and #8-style class profile
    H1, H8 = [], []
    for l in range(NL):
        Pc = class_top1_dist(S[l][:, 0], ucls, len(PROF))
        H1.append([entropy(p) for p in Pc])
        h8 = []
        for c in range(len(PROF)):
            b = np.bincount(S[l][ucls == c].ravel(), minlength=E).astype(float)
            h8.append(entropy(b / b.sum()))
        H8.append(h8)
    w = np.array([cnt[u] for u in PROF], float)
    r["ent_k1"], r["ent_k8"] = H1, H8
    r["ent_k1_wmean_norm"] = [float(np.dot(h, w) / w.sum() / np.log(E)) for h in H1]
    r["ent_k8_wmean_norm"] = [float(np.dot(h, w) / w.sum() / np.log(E)) for h in H8]
    # #7 word-form purity, per-form profile, top-10 table stability within run
    pur, pur_form = [], []
    for l in range(NL):
        Fc = form_counts(S[l][:, 0], fidx)
        pf = Fc.max(1) / np.maximum(nf, 1)
        pur.append(float(pf.mean()))
        pur_form.append(pf.tolist())
    r["purity"], r["purity_form"] = pur, pur_form
    if with_sat:
        Sw = load(run, T_WARM)
        r["top10_warm_jacc"] = [float(np.nanmean([jacc(a, b) for a, b in zip(top10(form_counts(Sw[l][:, 0], fidx)), top10(form_counts(S[l][:, 0], fidx)))]))
                                for l in range(NL)]
    # #13 DBES
    r["dbes"] = dbes(S, genre)
    print(f"{run}@{t} done", flush=True)
    return r


# ---------------- per pair (expert level, cross-fit) ----------------
def match(XA, XB):
    O = XA.T @ XB
    ra, cb = linear_sum_assignment(-O)
    pi = np.empty(E, int)
    pi[ra] = cb
    return pi    # A expert a <-> B expert pi[a]


def pearson(a, b):
    a, b = np.asarray(a, float).ravel(), np.asarray(b, float).ravel()
    m = np.isfinite(a) & np.isfinite(b)
    if m.sum() < 3 or a[m].std() == 0 or b[m].std() == 0:
        return np.nan
    return float(np.corrcoef(a[m], b[m])[0, 1])


def per_pair(args):
    (ra, ta, ta_sat), (rb, tb, tb_sat), kind = args
    SA, SB = load(ra, ta), load(rb, tb)
    SAs = load(ra, ta_sat) if ta_sat is not None else None
    SBs = load(rb, tb_sat) if tb_sat is not None else None
    out = collections.defaultdict(list)
    for l in range(NL):
        vals = collections.defaultdict(list)
        for h in (0, 1):
            fit, ev = HALVES[h], HALVES[1 - h]
            pi = match(mh(SA[l][fit]), mh(SB[l][fit]))
            A, B = SA[l][ev], SB[l][ev]
            overlap = float((mh(A) * mh(B)[:, pi]).sum(1).mean() / K)
            vals["matched_overlap"].append(overlap)
            # #1 per-expert saturation (share of T-slots on e that were on e at the early ckpt)
            if SAs is not None:
                XA, XB = mh(A), mh(B)
                sa = (XA * mh(SAs[l][ev])).sum(0) / np.maximum(XA.sum(0), 1)
                sb = (XB * mh(SBs[l][ev])).sum(0) / np.maximum(XB.sum(0), 1)
                vals["sat_expert"].append(pearson(sa, sb[pi]))
            # #2 co-activation matrix
            CA, CB = coact(A), coact(B)[np.ix_(pi, pi)]
            m = ~np.isnan(CA)
            vals["coact"].append(float(spearmanr(CA[m], CB[m])[0]))
            # #3 genre lift profile
            spA, aA = genre_spec(A, genre[ev]); spB, aB = genre_spec(B, genre[ev])
            vals["genre_lift"].append(pearson(spA / aA[:, None] - 1, (spB / aB[:, None] - 1)[pi]))
            # #6 P(e|c) per class
            PA = class_top1_dist(A[:, 0], ucls[ev], len(PROF)); PB = class_top1_dist(B[:, 0], ucls[ev], len(PROF))[:, pi]
            vals["class_dist"].append(float(np.nanmean([pearson(PA[c], PB[c]) for c in range(len(PROF))])))
            # #7 top-10 form tables
            tA, tB = top10(form_counts(A[:, 0], fidx[ev])), top10(form_counts(B[:, 0], fidx[ev]))
            vals["top10_jacc"].append(float(np.nanmean([jacc(tA[a], tB[pi[a]]) for a in range(E)])))
            # #8 expert POS KL
            vals["pos_kl"].append(pearson(expert_pos_kl(A, uall[ev]), expert_pos_kl(B, uall[ev])[pi]))
        for k, v in vals.items():
            out[k].append(float(np.nanmean(v)))
    print(f"pair {ra}@{ta}:{rb}@{tb} ({kind}) done", flush=True)
    return {"a": f"{ra}@{ta}", "b": f"{rb}@{tb}", "kind": kind, **out}


def main():
    nproc = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    OUT.mkdir(parents=True, exist_ok=True)
    jobs = [(r, T, True) for r in RUNS] + [(r, 0, False) for r in INITS]
    pj = []
    for a, b in itertools.combinations(INITS, 2):
        pj.append(((a, T, T_SAT), (b, T, T_SAT), "init"))
        pj.append(((a, 0, None), (b, 0, None), "floor"))
        pj.append(((a, T, 0), (b, T, 0), "sat_floor"))   # per-expert sat(0->T): floor for #1 expert level
    for a, b in (("I0D0", "I0D1"), ("I1D0", "I1D1")):
        pj.append(((a, T, T_SAT), (b, T, T_SAT), "order"))
    pj.append((("I4D0", T, T_SAT), ("I4D0R", T, T_SAT), "rerun"))
    with Pool(nproc) as pool:
        runs = pool.map(per_run, jobs, chunksize=1)
        (OUT / "runs.json").write_text(json.dumps({"T": T, "T_SAT": T_SAT, "T_WARM": T_WARM, "SAT_T": SAT_T, "PROF": PROF,
                                                   "n_per_prof": {u: cnt[u] for u in PROF}, "GENRES": GENRES, "FORMS": FORMS,
                                                   "n_forms": nf.tolist(), "half_sizes": [len(h) for h in HALVES],
                                                   "runs": {f"{r['run']}@{r['t']}": r for r in runs}}))
        pairs = pool.map(per_pair, pj, chunksize=1)
    (OUT / "pairs.json").write_text(json.dumps(pairs))


if __name__ == "__main__":
    main()
