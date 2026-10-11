"""E70-E72 (protocols: experiments/E70-*, E71-*, E72-*.md), CPU analyses of existing role maps.
  e70  share of head-level / layer-level differences between corpora that comes from the initialization
  e71  is the final strongest head of a role already the strongest early in training?
  e72  after aligning heads across initializations on eight roles, does the ninth role agree?
Writes results/e70_72.json."""
import itertools
import json
import re

import numpy as np
from scipy.optimize import linear_sum_assignment
from scipy.stats import rankdata, spearmanr

import mp_common as mc

R = mc.RESULTS
ROLES = ["M1", "M2", "M3", "M4", "R1", "R2", "R3", "R4", "R5"]


def load_1b():
    D = {}
    for f in sorted((R / "e35").glob("*-1B__*.json")):
        if "step" in f.stem:
            continue
        r, s = f.stem.split("-1B__")
        if (r, s) in mc.UNVERIFIED_1B:
            continue
        d = json.loads(f.read_text())
        m = {k: np.array(v, float) for k, v in d["maps"].items() if k != "M1" or d["M1_max"] > 0.3}
        f59 = R / "e59" / f"{r}__{s}.json"
        if f59.exists():
            m.update({k: np.array(v, float) for k, v in json.loads(f59.read_text())["maps"].items()})
        D[(r, s)] = m
    return D


def zrows(M):
    """Within-layer z-scores of within-layer ranks (so that every layer weighs equally)."""
    X = rankdata(M, axis=1)
    return (X - X.mean(1, keepdims=True)) / X.std(1, keepdims=True)


def within(a, b):
    return float(np.nanmean([spearmanr(x, y)[0] for x, y in zip(a, b)]))


# ---------------------------------------------------------------- E70
def e70(D):
    out = {}
    for role in ROLES:
        ks = sorted(k for k in D if role in D[k])
        Z = {k: zrows(D[k][role]) for k in ks}
        prof = {}
        for k in ks:  # layer profile: each layer's strongest score, z-scored over layers
            p = D[k][role].max(1)
            prof[k] = (p - p.mean()) / p.std()
        g = {"matched": [], "unmatched": [], "same_corpus": []}
        gl = {"matched": [], "unmatched": [], "same_corpus": []}
        for a, b in itertools.combinations(ks, 2):
            c = "same_corpus" if a[0] == b[0] else "matched" if a[1] == b[1] else "unmatched"
            g[c].append(float(np.mean((Z[a] - Z[b]) ** 2)))
            gl[c].append(float(np.mean((prof[a] - prof[b]) ** 2)))
        h = {c: float(np.mean(v)) for c, v in g.items()}
        lay = {c: float(np.mean(v)) for c, v in gl.items()}
        out[role] = {"head": h, "layer": lay, "init_share_head": 1 - h["matched"] / h["unmatched"],
                     "init_share_layer": 1 - lay["matched"] / lay["unmatched"]}
        print("e70", role, round(out[role]["init_share_head"], 3), round(out[role]["init_share_layer"], 3), flush=True)
    return out


# ---------------------------------------------------------------- E71
def topk_agree(A, B, layers, k):
    return float(np.mean([len(set(np.argsort(-A[l])[:k]) & set(np.argsort(-B[l])[:k])) / k for l in layers]))


def e71():
    out = {"controlled": {}, "datadecide_1b": {}}
    # (a) controlled pretraining: uninterrupted runs on natural text with induction heads at the end
    runs = {}
    for f in sorted((R / "e46").glob("S_i*_c4_o*.json")):
        d = json.loads(f.read_text())
        if not re.fullmatch(r"S_i\d+_c4_o\d+", d["name"]):
            continue
        runs[d["name"]] = {int(s): v for s, v in d["measures"].items()}
    for role in ("M1", "M2", "M3"):
        curve = {}
        for name, ms in runs.items():
            fin = np.array(ms[10000][role])
            if role == "M1" and ms[10000]["M1_max"] <= 0.3:
                continue
            layers = np.argsort(-fin.max(1))[:3] if fin.shape[0] > 3 else range(fin.shape[0])
            for s, v in ms.items():
                curve.setdefault(s, []).append(topk_agree(np.array(v[role]), fin, layers, 1))
        out["controlled"][role] = {"n_runs": len(next(iter(curve.values()))), "chance": 1 / 8,
                                   "top1_vs_final": {s: float(np.mean(v)) for s, v in sorted(curve.items())}}
        print("e71 controlled", role, {s: round(np.mean(v), 2) for s, v in sorted(curve.items())}, flush=True)
    # (b) DataDecide 1B: early checkpoints that were measured (3.6% and 14% of training)
    for step in (2500, 10000):
        res = {}
        for f in sorted((R / "e35").glob(f"*-1B__*__step{step}.json")):
            r, s, _ = f.stem.replace("-1B__", "__").split("__")
            if (r, s) in mc.UNVERIFIED_1B:
                continue
            e = json.loads(f.read_text())
            fin = json.loads((R / "e35" / f"{r}-1B__{s}.json").read_text())
            for role in ("M1", "M2", "M3", "M4"):
                if role == "M1" and (e["M1_max"] <= 0.3 or fin["M1_max"] <= 0.3):
                    continue
                A, B = np.array(e["maps"][role]), np.array(fin["maps"][role])
                layers = np.argsort(-B.max(1))[:3]
                res.setdefault(role, []).append((topk_agree(A, B, layers, 1), topk_agree(A, B, layers, 3), within(A, B)))
        out["datadecide_1b"][step] = {role: {"n": len(v), "top1": float(np.mean([x[0] for x in v])),
                                             "top3": float(np.mean([x[1] for x in v])),
                                             "within": float(np.mean([x[2] for x in v]))} for role, v in res.items()}
        print("e71 dd1b step", step, {r: (v["n"], round(v["top1"], 2), round(v["within"], 2))
                                       for r, v in out["datadecide_1b"][step].items()}, flush=True)
    return out


# ---------------------------------------------------------------- E72
def e72(D, n_pairs=400, seed=0):
    rng = np.random.default_rng(seed)
    keys = sorted(k for k in D if all(r in D[k] for r in ROLES))
    Z = {k: np.stack([zrows(D[k][r]) for r in ROLES]) for k in keys}  # roles x L x H
    L, H = Z[keys[0]].shape[1:]
    pairs = {"same_init": [], "diff_init": []}
    for a, b in itertools.combinations(keys, 2):
        if a[0] != b[0]:
            pairs["same_init" if a[1] == b[1] else "diff_init"].append((a, b))
    for c in pairs:
        if len(pairs[c]) > n_pairs:
            idx = rng.choice(len(pairs[c]), n_pairs, replace=False)
            pairs[c] = [pairs[c][i] for i in idx]
    out = {}
    for ri, role in enumerate(ROLES):
        feats = [j for j in range(len(ROLES)) if j != ri]
        res = {"same_init_raw": [], "same_init_aligned": [], "diff_init_raw": [], "diff_init_aligned": [],
               "diff_init_aligned_on_features": []}
        for c, ps in pairs.items():
            for a, b in ps:
                raw, ali, onf = [], [], []
                for l in range(L):
                    A, B = Z[a][:, l, :], Z[b][:, l, :]  # roles x H
                    C = np.corrcoef(A[feats].T, B[feats].T)[:H, H:]  # head-by-head similarity on the other roles
                    C = np.nan_to_num(C)
                    _, perm = linear_sum_assignment(-C)
                    raw.append(spearmanr(A[ri], B[ri])[0])
                    ali.append(spearmanr(A[ri], B[ri][perm])[0])
                    onf.append(np.mean([spearmanr(A[j], B[j][perm])[0] for j in feats]))
                res[f"{c}_raw"].append(np.nanmean(raw))
                res[f"{c}_aligned"].append(np.nanmean(ali))
                if c == "diff_init":
                    res["diff_init_aligned_on_features"].append(np.nanmean(onf))
        out[role] = {k: float(np.mean(v)) for k, v in res.items()}
        print("e72", role, {k: round(v, 3) for k, v in out[role].items()}, flush=True)
    return out


def main():
    D = load_1b()
    res = {"e70": e70(D), "e71": e71(), "e72": e72(D)}
    (R / "e70_72.json").write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
