"""corpus_distance: does corpus similarity predict how strongly the seed's slot is inherited?
Recipe token statistics from the cached DataDecide shard prefixes (corpus_samples: directory samples, size-weighted per recipe):
unigram and hashed-bigram distributions -> pairwise Jensen-Shannon divergence. Inheritance per recipe pair = within-layer
Spearman of the head-role maps, averaged over the seeds shared by the two recipes (same-init pairs only).
Mantel-style permutation test (recipe labels permuted) for Spearman(JS, inheritance).
Usage: corpus_distance.py stats ; corpus_distance.py analyze"""
import os
_CACHE = os.environ.get("MECHPOP_CACHE", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "cache"))  # see README
import collections
import itertools
import json
import sys

import numpy as np
from scipy.stats import spearmanr

import common as mc
from corpus_samples import RECIPES, SAMPLES, sizes

sys.path.insert(0, _CACHE + "/datadecide")
import named_data_mixes as ndm  # noqa: E402

OUT = mc.RESULTS / "corpus_distance"
EOS, V, NB = 50279, 50304, 1 << 22


def dir_dists():
    sz = sizes()
    groups = {}
    for name, key in RECIPES.items():
        g = collections.defaultdict(int)
        for p in ndm.DATA_PATHS[key]:
            g[p.rsplit("/", 1)[0]] += sz.get(p, 0) or 0
        groups[name] = dict(g)
    files = {f.name: f for f in SAMPLES.glob("*.prefix")}
    uni, bi = {}, {}
    for d in sorted({d for g in groups.values() for d in g}):
        first = sorted(p for p in sz if p.startswith(d + "/") and p.endswith(".npy"))
        if not first or first[0].replace("/", "__") + ".prefix" not in files:
            continue
        a = np.fromfile(files[first[0].replace("/", "__") + ".prefix"], dtype=np.uint16).astype(np.int64)
        u = np.bincount(a[a != EOS], minlength=V).astype(np.float64)
        ok = (a[:-1] != EOS) & (a[1:] != EOS)
        h = ((a[:-1] * V + a[1:]) * 0x9E3779B1 % NB)[ok]
        uni[d], bi[d] = u / u.sum(), np.bincount(h, minlength=NB).astype(np.float64)
        bi[d] /= bi[d].sum()
    rec = {}
    for name, g in groups.items():
        w = {d: s for d, s in g.items() if d in uni}
        tot = sum(w.values())
        if tot == 0:
            continue
        rec[name] = {"coverage": tot / sum(g.values()),
                     "uni": sum(uni[d] * s for d, s in w.items()) / tot, "bi": sum(bi[d] * s for d, s in w.items()) / tot}
    return rec


def js(p, q):
    m = (p + q) / 2
    kl = lambda a, b: float(np.sum(a[a > 0] * np.log(a[a > 0] / b[a > 0])))
    return (kl(p, m) + kl(q, m)) / 2


def stats():
    OUT.mkdir(exist_ok=True)
    rec = dir_dists()
    names = sorted(rec)
    out = {"coverage": {n: rec[n]["coverage"] for n in names}, "pairs": {}}
    for a, b in itertools.combinations(names, 2):
        out["pairs"][f"{a}|{b}"] = {"js_uni": js(rec[a]["uni"], rec[b]["uni"]), "js_bi": js(rec[a]["bi"], rec[b]["bi"])}
    (OUT / "recipe_distance.json").write_text(json.dumps(out, indent=1))
    print(len(names), "recipes; coverage min", round(min(out["coverage"].values()), 2))
    for k, v in sorted(out["pairs"].items(), key=lambda x: x[1]["js_uni"])[:3] + \
            sorted(out["pairs"].items(), key=lambda x: x[1]["js_uni"])[-3:]:
        print(k, {a: round(x, 4) for a, x in v.items()})


def within(a, b):
    return float(np.nanmean([spearmanr(a[l], b[l])[0] for l in range(a.shape[0])]))


def inheritance(files, parse):
    M = {}
    for f in files:
        k = parse(f)
        if k:
            M[k] = json.loads(f.read_text())
    out = {}
    for m in ("M1", "M2", "M4"):
        V = {k: np.array(v["maps"][m]) for k, v in M.items() if m != "M1" or v.get("M1_max", 1) > 0.3}
        acc = collections.defaultdict(list)
        for a, b in itertools.combinations(V, 2):
            if a[1] == b[1] and a[0] != b[0]:
                acc[tuple(sorted((a[0], b[0])))].append(within(V[a], V[b]))
        out[m] = {k: float(np.mean(v)) for k, v in acc.items()}
    return out


def mantel(pairs, dist, sim, rng, n=5000):
    names = sorted({x for p in pairs for x in p})
    D = {p: dist[p] for p in pairs}
    obs = spearmanr([D[p] for p in pairs], [sim[p] for p in pairs])[0]
    null = []
    for _ in range(n):
        perm = dict(zip(names, rng.permutation(names)))
        null.append(spearmanr([D[tuple(sorted((perm[a], perm[b])))] if tuple(sorted((perm[a], perm[b]))) in D else np.nan
                               for a, b in pairs], [sim[p] for p in pairs], nan_policy="omit")[0])
    null = np.array(null)
    return float(obs), float(np.mean(null <= obs))   # one-sided: more distant -> less inherited


def analyze():
    rng = np.random.default_rng(0)
    d = json.loads((OUT / "recipe_distance.json").read_text())
    dist = {}
    for k, v in d["pairs"].items():
        a, b = k.split("|")
        dist[tuple(sorted((a, b)))] = v
    res = {}
    crossing_1b = sorted((mc.RESULTS / "crossing_1b").glob("*-1B__*.json"))
    sets = {"1B": inheritance([f for f in crossing_1b if "step" not in f.name and tuple(f.stem.split("-1B__")) not in mc.UNVERIFIED_1B],
                              lambda f: (f.stem.split("-1B__")[0], f.stem.split("-1B__")[1]))}
    for size in ("60M", "90M", "150M", "300M", "530M", "750M", "1B@7500"):
        sets[size] = inheritance(sorted((mc.RESULTS / "crossing_sizes").glob(f"{size}__*.json")),
                                 lambda f: tuple(f.stem.split("__")[1:3]))
    for size, inh in sets.items():
        res[size] = {}
        for m, sim in inh.items():
            pairs = [p for p in sim if p in dist]
            if len(pairs) < 10:
                continue
            r = {}
            for key in ("js_uni", "js_bi"):
                r[key] = mantel(pairs, {p: dist[p][key] for p in pairs}, sim, rng, n=2000)
            r["n_pairs"] = len(pairs)
            res[size][m] = r
            print(f"{size:8s} {m} n {len(pairs):3d} | rho(JS_uni, inherit) {r['js_uni'][0]:+.3f} p {r['js_uni'][1]:.3f} | "
                  f"rho(JS_bi) {r['js_bi'][0]:+.3f} p {r['js_bi'][1]:.3f}", flush=True)
    (OUT / "analysis.json").write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    {"stats": stats, "analyze": analyze}[sys.argv[1]]()
