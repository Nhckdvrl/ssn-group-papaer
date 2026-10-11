"""E40: fit a saturating evidence-aggregation model to all 17 scores per base (full prompt + 16 deletions).

  ld_v = A * tanh(z_v) + B,   z_v = prior(query) + sum_{t in S_v} w(features_t) * sigma_t
sigma_t = +1 / -1 for the pole shown by demo t (mapped to the query's vocabulary poles).  w is linear in one-hot
feature groups.  Model variants add feature groups one at a time; fit on split-0 bases, report held-out R^2 on
(a) all scores and (b) deletion effects (ld_full - ld_del).  usage: fit_kernel.py TAG [TAG...]"""
import json, sys
from pathlib import Path
import numpy as np, torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze_kernel import demos, DBINS  # noqa

ROOT = Path(__file__).resolve().parents[1]
GROUPS = {
    "dist": lambda m, t: [f"d{int(np.digitize(abs(m['xs'][t] - m['qx']), DBINS[1:-1]))}"],
    "dist_x_cls": lambda m, t: [f"d{int(np.digitize(abs(m['xs'][t] - m['qx']), DBINS[1:-1]))}c{int(m['cls'][t] == m['qc'])}"],
    "vrel": lambda m, t: [f"v:{'same' if m['ann'][t] == 0 else m['v']}->{'same' if m['qa'] == 0 else m['v']}"],
    "pos": lambda m, t: [f"p{t // 2}"],
    "same_ann": lambda m, t: [f"a{int(m['ann'][t] == m['qa'])}"],
    "ann_x_vrel": lambda m, t: [f"a{int(m['ann'][t] == m['qa'])}:{'same' if m['ann'][t] == 0 else m['v']}->{'same' if m['qa'] == 0 else m['v']}"],
    "flip_x_tau": lambda m, t: [f"f{m['flip'][t]}:{m['tau']}"],
}
MODELS = {
    "M0 dist+vrel": ["dist", "vrel"],
    "M1 +class": ["dist_x_cls", "vrel"],
    "M2 +pos": ["dist_x_cls", "vrel", "pos"],
    "M3 +ann": ["dist_x_cls", "vrel", "same_ann"],
    "M4 +ann x vrel": ["dist_x_cls", "ann_x_vrel"],
    "M5 +flip x tau": ["dist_x_cls", "vrel", "flip_x_tau"],
    "M6 all": ["dist_x_cls", "ann_x_vrel", "pos", "flip_x_tau"],
}


def build(tag, meta, groups):
    z = np.load(ROOT / f"results/kernel/{tag}.npz")
    ld = dict(zip(z["uid"], z["ld"]))
    vocab = {}
    feats_rows, sig_rows, y, split, prior_rows, base_ix, var_ix = [], [], [], [], [], [], []
    bases = sorted(meta)
    for bi, b in enumerate(bases):
        m = meta[b]
        i = (int(b.split("_")[1]) - 940000) // 7919
        F = []
        for t in range(16):
            names = [n for g in groups for n in GROUPS[g](m, t)]
            F.append([vocab.setdefault(n, len(vocab)) for n in names])
        pr = [f"q{m['qx'] // 10}", f"qv:{'same' if m['qa'] == 0 else m['v']}", f"s{m['s']}"]
        for var in range(-1, 16):
            keep = [t for t in range(16) if t != var]
            feats_rows.append([F[t] for t in keep]); sig_rows.append([2 * m["ys"][t] - 1 for t in keep])
            y.append(ld[f"{b}|{var}"]); split.append((i // 4) % 2); prior_rows.append(pr); base_ix.append(bi); var_ix.append(var)
    pv = {}
    P = [[pv.setdefault(n, len(pv)) for n in pr] for pr in prior_rows]
    return vocab, pv, feats_rows, sig_rows, np.array(y, np.float32), np.array(split), P, np.array(base_ix), np.array(var_ix)


def fit(tag, meta, groups, steps=1500):
    vocab, pv, F, S, y, split, P, bix, vix = build(tag, meta, groups)
    n, k = len(y), len(vocab)
    # dense design: X[v, f] = sum over demos t in variant v with feature f of sigma_t (each demo contributes to all its features)
    X = np.zeros((n, k), np.float32)
    for v in range(n):
        for fl, s in zip(F[v], S[v]):
            for f in fl:
                X[v, f] += s
    Q = np.zeros((n, len(pv)), np.float32)
    for v in range(n):
        Q[v, P[v]] = 1
    X, Q, Y = map(torch.tensor, (X, Q, y))
    tr = torch.tensor(split == 0)
    w = torch.zeros(k, requires_grad=True); q = torch.zeros(len(pv), requires_grad=True)
    lA = torch.tensor(np.log(float(np.abs(y).max())), requires_grad=True); B = torch.zeros(1, requires_grad=True)
    opt = torch.optim.Adam([w, q, lA, B], lr=0.03)
    for _ in range(steps):
        pred = lA.exp() * torch.tanh(X @ w + Q @ q) + B
        loss = ((pred - Y)[tr] ** 2).mean() + 1e-4 * (w ** 2).sum()
        opt.zero_grad(); loss.backward(); opt.step()
    with torch.no_grad():
        pred = (lA.exp() * torch.tanh(X @ w + Q @ q) + B).numpy()
    te = split == 1
    r2 = lambda a, b: 1 - ((a - b) ** 2).sum() / ((a - a.mean()) ** 2).sum()
    # deletion effects on held-out bases
    full = {b: (y[i], pred[i]) for i, (b, v) in enumerate(zip(bix, vix)) if v == -1}
    dy = np.array([full[b][0] - y[i] for i, (b, v) in enumerate(zip(bix, vix)) if v >= 0 and te[i]])
    dp = np.array([full[b][1] - pred[i] for i, (b, v) in enumerate(zip(bix, vix)) if v >= 0 and te[i]])
    inv = {i: n_ for n_, i in vocab.items()}
    return {"r2_scores": float(r2(y[te], pred[te])), "r2_deletions": float(r2(dy, dp)), "A": float(lA.exp()),
            "w": {inv[i]: round(float(w[i]), 3) for i in range(k)}}


def main():
    meta = demos()
    out = {}
    for tag in sys.argv[1:]:
        out[tag] = {}
        for name, groups in MODELS.items():
            out[tag][name] = fit(tag, meta, groups)
            print(tag, name, f"R2 scores {out[tag][name]['r2_scores']:.3f}  R2 deletions {out[tag][name]['r2_deletions']:.3f}", flush=True)
    f = ROOT / "results/kernel/fit.json"
    old = json.loads(f.read_text()) if f.exists() else {}
    f.write_text(json.dumps(old | out, indent=1))


if __name__ == "__main__":
    main()
