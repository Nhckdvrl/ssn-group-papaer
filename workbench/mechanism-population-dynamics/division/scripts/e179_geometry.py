#!/usr/bin/env python3
"""E179 direct geometry readouts on the router-input hidden states (card: experiments/E179-...md).

Per MoE layer, two levels (sentence means: 19,940 rows; token subsample: 20,000 rows):
  G1   full-dim 20-way multinomial logistic regression, 5-fold CV grouped by sentence id (fold = perm(sid) % 5),
       features z-scored with train-fold stats, L2 1e-3, full-batch L-BFGS <= 300 iters; test accuracy + NLL
  G2   centroid dispersion: mean pairwise centroid distance / mean within-language distance to centroid (raw space)
       supplementary: in T's readout subspace V (row space of the row-centred gate), and after global z-scoring
  G3   PCA on all rows (pooled, centred); principal = first k PC coordinates, residual = the rest;
       k = k50 (smallest k with >= 50% variance) and k = 16; G1-type probe + G2-type dispersion in each subspace
  ctrl label-permuted G1 (token level) at the first and last layer
Usage: e179_geometry.py CAPTURE_DIR  -> CAPTURE_DIR/geometry.json
"""
import json, os, sys, time
import numpy as np
import torch

CAP = sys.argv[1]
dev = torch.device("cuda")
meta = json.load(open(os.path.join(CAP, "meta.json")))
L, NS, NL = meta["L"], meta["n_sent"], len(meta["langs"])
SENT = np.load(os.path.join(CAP, "sentmean.npy"), mmap_mode="r")
TOKS = np.load(os.path.join(CAP, "toksub.npy"), mmap_mode="r")
tm = np.load(os.path.join(CAP, "toksub_meta.npz"))
GW = np.load(os.path.join(CAP, "gateW.npy"))
NU = SENT.shape[1]
perm = np.random.default_rng(179).permutation(NS)
LV = {"sent": (np.arange(NU) // NS, perm[np.arange(NU) % NS] % 5),
      "tok": (tm["lang"].astype(np.int64), perm[tm["sid"]] % 5)}
t0 = time.time()


def probe(X, y, fold, iters=300, lam=1e-3):
    accs, nlls = [], []
    for f in range(5):
        tr, te = fold != f, fold == f
        mu, sd = X[tr].mean(0), X[tr].std(0).clamp_min(1e-6)
        Xtr, Xte = (X[tr] - mu) / sd, (X[te] - mu) / sd
        W = torch.zeros(X.shape[1], NL, device=dev, requires_grad=True)
        b = torch.zeros(NL, device=dev, requires_grad=True)
        opt = torch.optim.LBFGS([W, b], lr=1, max_iter=iters, history_size=20, line_search_fn="strong_wolfe",
                                tolerance_grad=1e-6, tolerance_change=1e-9)
        ytr = y[tr]

        def closure():
            opt.zero_grad()
            loss = torch.nn.functional.cross_entropy(Xtr @ W + b, ytr) + 0.5 * lam * (W * W).sum()
            loss.backward()
            return loss
        opt.step(closure)
        with torch.no_grad():
            lo = Xte @ W + b
            accs.append(float((lo.argmax(1) == y[te]).float().mean()))
            nlls.append(float(torch.nn.functional.cross_entropy(lo, y[te])))
    return float(np.mean(accs)), float(np.mean(nlls))


def disp(X, y):
    C = torch.stack([X[y == i].mean(0) for i in range(NL)])
    iu, ju = torch.triu_indices(NL, NL, 1)
    between = (C[iu] - C[ju]).norm(dim=1).mean()
    within = torch.stack([(X[y == i] - C[i]).norm(dim=1).mean() for i in range(NL)]).mean()
    return float(between / within)


out = {lv: {} for lv in LV}
for l in range(L):
    W = torch.tensor(GW[l], device=dev, dtype=torch.float64)
    _, S, Vh = torch.linalg.svd(W - W.mean(0, keepdim=True), full_matrices=False)
    V = Vh[S > 1e-6 * S[0]].T.float()
    for lv, (yl, fl) in LV.items():
        X = torch.tensor(np.asarray((SENT if lv == "sent" else TOKS)[l], dtype=np.float32), device=dev)
        y = torch.tensor(yl, device=dev)
        fold = torch.tensor(fl, device=dev)
        r = {}
        r["G1_acc"], r["G1_nll"] = probe(X, y, fold)
        r["G2"] = disp(X, y)
        r["G2_readout"] = disp(X @ V, y)
        r["G2_std"] = disp((X - X.mean(0)) / X.std(0).clamp_min(1e-6), y)
        Xc = X - X.mean(0)
        ev, P = torch.linalg.eigh((Xc.T.double() @ Xc.double()) / Xc.shape[0])
        ev, P = ev.flip(0).clamp_min(0), P.flip(1).float()
        cum = (ev.cumsum(0) / ev.sum()).cpu().numpy()
        k50 = int(np.searchsorted(cum, 0.5) + 1)
        r["k50"] = k50
        r["var16"] = float(cum[15])
        r["rank"] = int((ev > 1e-6 * ev[0]).sum())  # numerically null directions (n < d in smoke runs) are dropped
        Z = Xc @ P[:, :r["rank"]]
        for kname, k in (("k50", k50), ("k16", 16)):
            for sname, Zs in (("prin", Z[:, :k]), ("res", Z[:, k:])):
                acc, nll = probe(Zs, y, fold)
                r[f"G3_{kname}_{sname}_acc"], r[f"G3_{kname}_{sname}_nll"] = acc, nll
                r[f"G3_{kname}_{sname}_disp"] = disp(Zs, y)
        if lv == "tok" and l in (0, L - 1):
            yp = y[torch.randperm(len(y), generator=torch.Generator().manual_seed(l)).to(dev)]
            r["G1_acc_permuted"] = probe(X, yp, fold)[0]
        out[lv][l] = r
        del X, Z, Xc
    print(f"[{time.time() - t0:6.0f}s] layer {l}: " + " | ".join(
        f"{lv} G1 {out[lv][l]['G1_acc']:.3f} G2 {out[lv][l]['G2']:.3f} k50 {out[lv][l]['k50']} "
        f"prin {out[lv][l]['G3_k50_prin_acc']:.3f}/{out[lv][l]['G3_k50_prin_disp']:.3f} "
        f"res {out[lv][l]['G3_k50_res_acc']:.3f}/{out[lv][l]['G3_k50_res_disp']:.3f}" for lv in LV), flush=True)
json.dump(out, open(os.path.join(CAP, "geometry.json"), "w"), indent=1)
print("done", time.time() - t0)
