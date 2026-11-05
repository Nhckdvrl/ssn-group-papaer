#!/usr/bin/env python3
"""E176 natural-stream check: recompute top-8 routing of all 113,118 contiguous words (word-final token) from the
hidden cache (H_l W_l^T + b_l), verify against S{l} on the anchors, and recompute the sampling-sensitive readouts
(#2 model level, #3 model + class level, #7 purity model + per-form profile, #13 DBES) with natural frequencies.
Readout functions are shared with e176_readouts.py.

Usage: e176_natural.py [NPROC] -> results/e176/natural.json
"""
import os

os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "2")
import collections
import json
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import e176_readouts as R  # noqa: E402

HID = Path.home() / "mechpop_cache/e167_analysis/hidden"
FILES = {"I0D0": 3999793152, "I1D0": 3999793152, "I2D0": 3999793152, "I3D0": 3999793152, "I4D0": 3200000000,
         "I0D1": 3999793152, "I1D1": 3999793152, "I4D0R": 3200000000}
FLOOR = {"I0D0": 0, "I1D0": 0}
ann = R.ann
z0 = np.load(HID / "I0D0__ckpt_0.npz")
word_idx = z0["word_idx"]
genre = np.array([R.GENRES.index(ann[int(w)]["genre"]) for w in word_idx])
form = [ann[int(w)]["form"].lower() for w in word_idx]
fc = collections.Counter(form)
NFORMS = sorted(f for f in fc if fc[f] >= 6)
fpos = {f: i for i, f in enumerate(NFORMS)}
fidx = np.array([fpos.get(f, -1) for f in form])
nfn = np.bincount(fidx[fidx >= 0], minlength=len(NFORMS))
row_of_word = {int(w): i for i, w in enumerate(word_idx)}
anchor_rows = np.array([row_of_word.get(int(w), -1) for w in R.aw])


def route(Z, l):
    H = Z[f"H{l}"].astype(np.float32)
    s = H @ Z[f"W{l}"].T + Z[f"b{l}"]
    top = np.argpartition(-s, R.K, 1)[:, :R.K]
    o = np.argsort(-np.take_along_axis(s, top, 1), 1)
    return np.take_along_axis(top, o, 1).astype(np.int64)


def job(args):
    run, t = args
    Z = np.load(HID / f"{run}__ckpt_{t}.npz")
    S = [route(Z, l) for l in range(R.NL)]
    r = {"run": run, "t": t}
    # verification against the routing cache
    capf = R.CAP / f"{run}__ckpt_{t}.npz"
    if capf.exists():
        C = R.load(run, t)
        ok = anchor_rows >= 0
        r["verify_top8_set_agree"] = [float((R.mh(S[l][anchor_rows[ok]]) * R.mh(C[l][ok])).sum(1).mean() / R.K) for l in range(R.NL)]
        r["verify_top1_agree"] = [float(np.mean(S[l][anchor_rows[ok], 0] == C[l][ok, 0])) for l in range(R.NL)]
    strong, liftmax, liftany, dev, pur, purf = [], [], [], [], [], []
    m = fidx >= 0
    for l in range(R.NL):
        Cc = R.coact(S[l])
        strong.append(float(np.mean(Cc[~np.isnan(Cc)] >= 0.5)))
        sp, allr = R.genre_spec(S[l], genre)
        lift = np.where(allr[:, None] > 0, sp / np.maximum(allr[:, None], 1e-12), np.nan)
        liftmax.append(float(np.nanmean(np.nanmax(lift, 1)))); liftany.append(float(np.nanmax(lift)))
        dev.append([float(0.5 * np.abs(sp[:, D] - allr).sum()) for D in range(len(R.GENRES))])
        Fc = np.bincount(fidx[m] * R.E + S[l][m, 0], minlength=len(NFORMS) * R.E).reshape(len(NFORMS), R.E)
        pf = Fc.max(1) / np.maximum(nfn, 1)
        pur.append(float(pf.mean())); purf.append(pf.tolist())
    r.update({"coact_strong_frac": strong, "genre_liftmax_mean": liftmax, "genre_lift_max": liftany, "genre_dev": dev,
              "purity": pur, "purity_form": purf, "dbes": R.dbes(S, genre)})
    print(f"natural {run}@{t} done", flush=True)
    return r


def main():
    nproc = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    jobs = list(FILES.items()) + list(FLOOR.items())
    with Pool(nproc) as pool:
        res = pool.map(job, jobs, chunksize=1)
    (R.OUT / "natural.json").write_text(json.dumps({"files": FILES, "floor": FLOOR, "n_words": int(len(word_idx)),
                                                    "genre_n": dict(zip(R.GENRES, np.bincount(genre, minlength=5).tolist())),
                                                    "n_forms_ge6": len(NFORMS), "runs": {f"{r['run']}@{r['t']}": r for r in res}}))


if __name__ == "__main__":
    main()
