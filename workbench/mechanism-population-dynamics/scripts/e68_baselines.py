"""E68: identifying a model's initialization without head roles -- weight and SeedPrints baselines (protocol:
experiments/E68-*.md). Same leave-one-corpus-out task and models as E61.

  e68_baselines.py --worker GPU_TAG   # measure every model not yet done (claims in results/e68/claims)
  e68_baselines.py --analyze
Per model (results/e68/<size>__<recipe>__<seed>.npz):
  w     a fixed random subsample (same indices for every model of a size) of all attention and MLP weight matrices
  fp    SeedPrints (Tong et al., ICLR 2026): n = 2000 uniformly random token sequences of length 1024 (fixed seed, same
        for every model); g(x) = final-layer hidden state (after the final norm) at the last position, softmax with
        temperature 10; the m = min(0.1 d, 400) dimensions with the lowest mean form the fingerprint; we keep their
        indices and the per-input values for the Kendall-tau test.
"""
import argparse
import json
import os
import zlib

import numpy as np

import mp_common as mc

OUT = mc.RESULTS / "e68"
PLAN = json.loads((mc.CACHE / "datadecide" / "e45_plan.json").read_text())
N_IN, LEN, T, N_W = 2000, 1024, 10.0, 2_000_000


def models():
    out = []
    for f in sorted((mc.RESULTS / "e45").glob("*__*__*.json")):
        size, r, s = f.stem.split("__")
        out.append((size, r, s))
    for f in sorted((mc.RESULTS / "e35").glob("*-1B__*.json")):
        if "step" not in f.stem:
            r, s = f.stem.split("-1B__")
            out.append(("1B", r, s))
    return out


def repo_rev(size, r, s):
    if size == "1B":
        return f"allenai/DataDecide-{r}-1B", f"step69369-seed-{s}"
    if size == "1B@7500":
        return f"allenai/DataDecide-{r}-1B", f"step7500-seed-{s}"
    return f"allenai/DataDecide-{r}-{size}", f"step{PLAN[size]['step']}-seed-{s}"


def measure(size, r, s):
    import torch
    import dd_common as dd
    torch.set_grad_enabled(False)
    repo, rev = repo_rev(size, r, s)
    model, tok = dd.load(repo, rev, dtype=torch.bfloat16)
    # weight subsample: indices depend only on the tensor name and shape, so they match across models of a size
    ws = []
    named = [(k, p) for k, p in model.named_parameters() if p.ndim == 2 and ".layers." in k]
    total = sum(p.numel() for _, p in named)
    for k, p in named:
        n = max(1, int(round(N_W * p.numel() / total))) if total > N_W else p.numel()
        g = torch.Generator().manual_seed(zlib.crc32(f"{k.split('.layers.')[1]}{tuple(p.shape)}".encode()))
        idx = torch.randperm(p.numel(), generator=g)[:n] if n < p.numel() else torch.arange(p.numel())
        ws.append(p.detach().float().flatten().cpu()[idx])
    w = torch.cat(ws).numpy().astype(np.float32)
    # SeedPrints
    g = torch.Generator().manual_seed(1234)
    V = model.config.vocab_size
    X = torch.randint(0, min(V, len(tok)), (N_IN, LEN), generator=g)
    bs = 32 if model.config.hidden_size <= 1024 else 8
    H = []
    for i in range(0, N_IN, bs):
        h = model.model(X[i:i + bs].to(model.device)).last_hidden_state[:, -1].float()
        H.append(torch.softmax(h / T, -1).cpu())
    H = torch.cat(H).numpy()
    d = H.shape[1]
    m = min(int(0.1 * d), 400)
    dims = np.argsort(H.mean(0))[:m]
    OUT.mkdir(exist_ok=True)
    np.savez_compressed(OUT / f"{size}__{r}__{s}.npz", w=w.astype(np.float16), dims=dims,
                        vals=H[:, dims].astype(np.float32))
    print(size, r, s, "d", d, "m", m, "w", len(w), flush=True)


def worker(tag):
    claims = OUT / "claims"
    claims.mkdir(parents=True, exist_ok=True)
    order = {"1B": 0, "1B@7500": 2}  # final 1B models first, the 10%-of-training 1B checkpoints last
    for size, r, s in sorted(models(), key=lambda m: (order.get(m[0], 1), m)):
        name = f"{size}__{r}__{s}"
        if (OUT / f"{name}.npz").exists():
            continue
        try:
            os.mkdir(claims / name)
        except FileExistsError:
            continue
        try:
            measure(size, r, s)
        except Exception as ex:
            print("FAILED", name, repr(ex)[:300], flush=True)
            os.rmdir(claims / name)


# ---------------------------------------------------------------- analysis
def kendall_z(a, b):
    """SeedPrints test statistic between two fingerprints: Kendall tau per shared dimension across the inputs, then
    z = mean tau / (sigma / sqrt(|S|)) with sigma^2 = 2(2n+5) / (9n(n-1))."""
    from scipy.stats import kendalltau
    S = np.intersect1d(a["dims"], b["dims"])
    if len(S) == 0:
        return 0.0
    ia = {d: i for i, d in enumerate(a["dims"])}
    ib = {d: i for i, d in enumerate(b["dims"])}
    taus = [kendalltau(a["vals"][:, ia[d]], b["vals"][:, ib[d]])[0] for d in S]
    n = a["vals"].shape[0]
    sigma = np.sqrt(2 * (2 * n + 5) / (9 * n * (n - 1)))
    return float(np.nanmean(taus) / (sigma / np.sqrt(len(S))))


def identify(keys, S):
    seeds = sorted({s for _, s in keys})
    hits = []
    for i, q in enumerate(keys):
        score = {}
        for s in seeds:
            v = [S[i, j] for j, k in enumerate(keys) if k[1] == s and k[0] != q[0]]
            score[s] = np.nanmean(v) if v else np.nan
        if any(np.isnan(v) for v in score.values()):
            continue
        hits.append(max(score, key=score.get) == q[1])
    return {"accuracy": float(np.mean(hits)), "n": len(hits), "chance": 1 / len(seeds)}


def analyze(only=None):
    res = {}
    by = {}
    for size, r, s in models():
        f = OUT / f"{size}__{r}__{s}.npz"
        if f.exists():
            by.setdefault(size, {})[(r, s)] = f
    for size, F in by.items():
        if only and size not in only:
            continue
        keys = sorted(F)
        if size == "1B":  # identification on the verified runs; the six others are scored blind below
            keys_v = [k for k in keys if k not in mc.UNVERIFIED_1B]
        else:  # same exclusion as E45 / E61 (a run whose initialization differs from its label)
            from e45_analyze import EXCLUDE
            keys_v = [k for k in keys if (size, *k) not in EXCLUDE]
        D = {k: dict(np.load(F[k])) for k in keys}
        W = np.stack([D[k]["w"].astype(np.float32) for k in keys])
        W = (W - W.mean(1, keepdims=True)) / W.std(1, keepdims=True)
        Cw = W @ W.T / W.shape[1]
        Z = np.zeros((len(keys), len(keys)))
        for i in range(len(keys)):
            for j in range(i + 1, len(keys)):
                Z[i, j] = Z[j, i] = kendall_z(D[keys[i]], D[keys[j]])
        sel = [keys.index(k) for k in keys_v]
        row = {"weights": identify(keys_v, Cw[np.ix_(sel, sel)]), "seedprints": identify(keys_v, Z[np.ix_(sel, sel)])}
        # typical similarity values: same seed / other corpus vs other seed / same corpus
        for name, M in (("weights", Cw), ("seedprints", Z)):
            si = [M[a, b] for a in sel for b in sel if a < b and keys[a][1] == keys[b][1] and keys[a][0] != keys[b][0]]
            sd = [M[a, b] for a in sel for b in sel if a < b and keys[a][1] != keys[b][1] and keys[a][0] == keys[b][0]]
            row[name]["same_seed_mean"] = float(np.mean(si)) if si else None
            row[name]["same_corpus_mean"] = float(np.mean(sd)) if sd else None
            row[name]["frac_same_seed_pairs_significant"] = (float(np.mean(np.array(si) > 2.576)) if name == "seedprints"
                                                             and si else None)
        if size == "1B":  # blind: do the six unlisted-initialization runs agree with none of their nominal siblings?
            blind = {}
            for k in mc.UNVERIFIED_1B:
                if k in keys:
                    i = keys.index(k)
                    sib = [keys.index(x) for x in keys_v if x[1] == k[1] and x[0] != k[0]]
                    partner = [keys.index(x) for x in keys if x in mc.UNVERIFIED_1B and x != k and x[1] == k[1]]
                    blind[f"{k[0]}|{k[1]}"] = {
                        "weights_vs_siblings": float(np.mean(Cw[i, sib])), "weights_vs_partner": float(np.mean(Cw[i, partner])),
                        "seedprints_vs_siblings": float(np.mean(Z[i, sib])), "seedprints_vs_partner": float(np.mean(Z[i, partner]))}
            row["blind_unverified"] = blind
        res[size] = row
        print(size, {k: (round(v["accuracy"], 3), v["n"]) for k, v in row.items() if isinstance(v, dict) and "accuracy" in v},
              flush=True)
    (OUT / ("analysis.json" if not only else f"analysis_{'_'.join(only)}.json")).write_text(json.dumps(res, indent=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--worker")
    ap.add_argument("--one", nargs=3)
    ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--sizes", nargs="*")
    a = ap.parse_args()
    if a.analyze:
        analyze(a.sizes)
    elif a.one:
        measure(*a.one)
    else:
        worker(a.worker)


if __name__ == "__main__":
    main()
