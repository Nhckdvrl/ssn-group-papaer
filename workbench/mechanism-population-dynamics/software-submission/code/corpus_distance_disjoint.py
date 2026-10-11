"""corpus_distance control: is the distance-inheritance relation driven by shared source documents? Source overlap of a recipe pair =
size-weighted fraction of shared shard directories (min over the two recipes' weights). Re-test on source-disjoint pairs
and with a partial Spearman controlling for overlap."""
import os
_CACHE = os.environ.get("MECHPOP_CACHE", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "cache"))  # see README
import collections
import json
import sys

import numpy as np
from scipy.stats import rankdata, spearmanr

import common as mc
from corpus_samples import RECIPES, sizes
from corpus_distance import inheritance, mantel

sys.path.insert(0, _CACHE + "/datadecide")
import named_data_mixes as ndm  # noqa: E402


def partial_spearman(x, y, z):
    rx, ry, rz = (rankdata(v) for v in (x, y, z))
    res = lambda a, b: a - np.polyval(np.polyfit(b, a, 1), b)
    return float(np.corrcoef(res(rx, rz), res(ry, rz))[0, 1])


def main():
    sz = sizes()
    W = {}
    for name, key in RECIPES.items():
        g = collections.defaultdict(float)
        for p in ndm.DATA_PATHS[key]:
            g[p.rsplit("/", 1)[0]] += sz.get(p, 0) or 0
        tot = sum(g.values())
        W[name] = {d: v / tot for d, v in g.items()} if tot else {}
    overlap = lambda a, b: sum(min(W[a].get(d, 0), W[b].get(d, 0)) for d in set(W[a]) | set(W[b]))
    d = json.loads((mc.RESULTS / "corpus_distance" / "recipe_distance.json").read_text())
    dist = {tuple(sorted(k.split("|"))): v for k, v in d["pairs"].items()}
    rng = np.random.default_rng(0)
    crossing_1b = sorted((mc.RESULTS / "crossing_1b").glob("*-1B__*.json"))
    sets = {"1B": inheritance([f for f in crossing_1b if "step" not in f.name and tuple(f.stem.split("-1B__")) not in mc.UNVERIFIED_1B],
                              lambda f: (f.stem.split("-1B__")[0], f.stem.split("-1B__")[1]))}
    for size in ("90M", "150M", "300M", "530M", "750M", "1B@7500"):
        sets[size] = inheritance(sorted((mc.RESULTS / "crossing_sizes").glob(f"{size}__*.json")), lambda f: tuple(f.stem.split("__")[1:3]))
    out = {}
    for size, inh in sets.items():
        out[size] = {}
        for m, sim in inh.items():
            pairs = [p for p in sim if p in dist]
            ov = {p: overlap(*p) for p in pairs}
            dis = [p for p in pairs if ov[p] < 1e-9]
            r = {"n_pairs": len(pairs), "n_disjoint": len(dis),
                 "partial_rho": partial_spearman([dist[p]["js_uni"] for p in pairs], [sim[p] for p in pairs], [ov[p] for p in pairs]),
                 "rho_overlap": float(spearmanr([ov[p] for p in pairs], [sim[p] for p in pairs])[0])}
            if len(dis) >= 10:
                r["disjoint"] = mantel(dis, {p: dist[p]["js_uni"] for p in dis}, sim, rng, n=2000)
            out[size][m] = r
            print(f"{size:8s} {m} pairs {len(pairs):3d} disjoint {len(dis):3d} | disjoint rho {r.get('disjoint', (np.nan, np.nan))[0]:+.3f} "
                  f"p {r.get('disjoint', (np.nan, np.nan))[1]:.3f} | partial rho (ctrl overlap) {r['partial_rho']:+.3f} | rho(overlap) {r['rho_overlap']:+.3f}",
                  flush=True)
    (mc.RESULTS / "corpus_distance" / "disjoint_control.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
