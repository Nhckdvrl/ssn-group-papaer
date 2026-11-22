#!/usr/bin/env python3
"""E194 analysis: R1 (in-context retrieval), R2 (Patchscopes), R3 (word vs nonword kNN), onsets, decision table.

Layers are reported as decoder-layer indices; -1 = embedding output (capture index = layer + 1).
Usage: e194_analyze.py ITEMS_JSON OUT_ROOT RESULT_DIR      (OUT_ROOT holds H/, T/, H0/, T0/)
"""
import json
import sys
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

B_BOOT, SEED = 1000, 194
MS = [2, 3, 4, 5, 6]


def type_boot(types, rng):
    """Resample word types; returns index arrays (all occurrences of each drawn type)."""
    uniq = sorted(set(types))
    occ = {t: [] for t in uniq}
    for i, t in enumerate(types):
        occ[t].append(i)
    out = []
    for _ in range(B_BOOT):
        draw = rng.integers(0, len(uniq), len(uniq))
        out.append(np.concatenate([occ[uniq[d]] for d in draw]))
    return out


def ci(boots):
    return np.percentile(boots, 2.5, axis=0), np.percentile(boots, 97.5, axis=0)


def onset(curve_full, boots, valid, layers):
    """L* per bootstrap: first valid layer whose value >= 50% of that resample's max."""
    def first(c):
        mx = c.max()
        for k, l in enumerate(layers):
            if valid[k] and c[k] >= 0.5 * mx and mx > 0:
                return l
        return None
    point = first(curve_full)
    dist = [first(c) for c in boots]
    def cls(d):
        d = [x for x in d]
        early = np.mean([x is not None and x <= 2 for x in d])
        wait = np.mean([x is not None and x >= 3 for x in d])
        return "early" if early >= .9 else ("wait" if wait >= .9 else "uncertain")
    return point, cls(dist), dist


def r1(root, I, rng_boot):
    out = {}
    types = [it["form"].lower() for it in I["S"]]
    boots = type_boot(types, np.random.default_rng(SEED))
    for key in ["H", "T", "H0", "T0"]:
        d = torch.load(root / key / "S.pt")
        top1 = (d["ranks"] == 0).float().numpy()  # [items, L+1, Q]
        out[key] = {"qnames": d["qnames"], "acc": top1.mean(0), "boot": np.stack([top1[b].mean(0) for b in boots])}
    layers = list(range(-1, out["H"]["acc"].shape[0] - 1))
    res = {"layers": layers, "chance": 1 / 32, "curves": {}, "onset": {}, "binding": {}}
    for key in ["H", "T", "H0", "T0"]:
        q = out[key]["qnames"]
        lo, hi = ci(out[key]["boot"])
        res["curves"][key] = {n: {"acc": out[key]["acc"][:, j].round(4).tolist(), "lo": lo[:, j].round(4).tolist(),
                                  "hi": hi[:, j].round(4).tolist()} for j, n in enumerate(q)}
    for key, ref in (("H", "H0"), ("T", "T0")):
        q = out[key]["qnames"]
        lo, _ = ci(out[key]["boot"])
        _, hi0 = ci(out[ref]["boot"])
        for j, n in enumerate(q):
            if not n.startswith("split"):
                continue
            valid = lo[:, j] > hi0[:, j]
            p, c, dist = onset(out[key]["acc"][:, j], out[key]["boot"][:, :, j], valid, layers)
            res["onset"][f"{key}/{n}"] = {"point": p, "class": c,
                                         "dist_hist": {str(k): int(sum(x == k for x in dist)) for k in sorted(set(x for x in dist if x is not None))},
                                         "n_none": int(sum(x is None for x in dist))}
        for m in [3, 4, 5, 6]:
            js, jh = q.index(f"split{m}"), q.index(f"shuf{m}")
            diff_b = out[key]["boot"][:, :, js] - out[key]["boot"][:, :, jh]
            dlo, dhi = ci(diff_b)
            diff = out[key]["acc"][:, js] - out[key]["acc"][:, jh]
            res["binding"][f"{key}/m{m}"] = {"diff": diff.round(4).tolist(), "lo": dlo.round(4).tolist(), "hi": dhi.round(4).tolist()}
    return res


def r2(root, I):
    res = {}
    for key in ["H", "T"]:
        f = root / key / "R2.json"
        if not f.exists():
            continue
        d = json.loads(f.read_text())
        layers = d["layers"]
        tabs = {}
        for r in d["results"]:
            tabs.setdefault((r["set"], r["stratum"], r["kind"]), {})[r["layer"]] = np.array(r["succ"], float)
        out = {}
        rng = np.random.default_rng(SEED)
        for (set_, st, kind), by in tabs.items():
            if kind != "real":
                continue
            rnd = tabs[(set_, st, "random")]
            n = len(by[layers[0]])
            idx = [rng.integers(0, n, n) for _ in range(B_BOOT)]
            real = np.stack([by[l] for l in layers], 1)  # [n, Lsel]
            ran = np.stack([rnd[l] for l in layers], 1)
            rb = np.stack([real[i].mean(0) for i in idx]); nb = np.stack([ran[i].mean(0) for i in idx])
            lo, hi = ci(rb); _, nhi = ci(nb)
            valid = lo > nhi
            p, c, dist = onset(real.mean(0), rb, valid, layers)
            out[f"{set_}/{st}"] = {"acc": real.mean(0).round(4).tolist(), "lo": lo.round(4).tolist(), "hi": hi.round(4).tolist(),
                                   "random": ran.mean(0).round(4).tolist(), "onset_point": p, "onset_class": c, "n": n}
        res[key] = {"layers": layers, "by": out, "prompt": d["prompt"]}
    return res


def r3(root, I):
    res = {}
    for key in ["H", "T", "H0", "T0"]:
        f = root / key / "N.pt"
        if not f.exists():
            continue
        d = torch.load(f)
        reps = d["reps"].float()  # [n, L+1, 2(real/non), 2(last/penult), d]
        strata = np.array(d["stratum"])
        out = {}
        for st in ["2", "3", "4+"]:
            idx = np.where(strata == st)[0]
            if len(idx) < 20:
                continue
            for pos, pname in ((0, "last"), (1, "penult")):
                if pname == "penult" and st == "2":
                    continue
                accs = []
                folds = np.arange(len(idx)) % 5
                for l in range(reps.shape[1]):
                    X = torch.cat([reps[idx, l, 0, pos], reps[idx, l, 1, pos]]).cuda()
                    y = torch.cat([torch.ones(len(idx)), torch.zeros(len(idx))]).cuda()
                    g = torch.tensor(np.concatenate([folds, folds])).cuda()
                    X = F.normalize(X - X.mean(0), dim=-1)
                    S = X @ X.T
                    correct = 0
                    for k in range(5):
                        te, tr = g == k, g != k
                        nn_ = S[te][:, tr].topk(4, dim=1).indices
                        pred = (y[tr][nn_].mean(1) > .5).float()
                        correct += (pred == y[te]).sum().item()
                    accs.append(correct / len(y))
                out[f"{st}/{pname}"] = {"acc": np.round(accs, 4).tolist(), "n_words": int(len(idx))}
        res[key] = out
    return res


def decide(R1, R2):
    """Card decision table; needs R1 and R2 to agree for a model-m class."""
    def cls(key, m):
        a = R1["onset"].get(f"{key}/split{m}", {}).get("class")
        b = R2.get(key, {}).get("by", {}).get(f"S/m{m}", {}).get("onset_class")
        return a if a == b else f"disagree({a},{b})"
    table = {f"{k}/m{m}": cls(k, m) for k in ["H", "T"] for m in MS}
    H = {m: table[f"H/m{m}"] for m in MS}; T = {m: table[f"T/m{m}"] for m in MS}
    pt = lambda k, m: R1["onset"].get(f"{k}/split{m}", {}).get("point")
    out = []
    if all(H[m] == "wait" for m in (2, 3, 4)) and all(T[m] == "early" for m in (2, 3, 4)):
        out.append("A")
    if all(H[m] == "early" for m in MS) and all(pt("H", m) is not None and pt("T", m) is not None and abs(pt("H", m) - pt("T", m)) <= 1 for m in MS):
        out.append("B")
    if all(H[m] == "early" for m in (2, 3, 4)) and all(H[m] == "wait" for m in (5, 6)) and \
            pt("T", 4) is not None and pt("T", 5) is not None and abs(pt("T", 5) - pt("T", 4)) <= 1:
        out.append("C")
    # F-bag: H's split retrieval already high at decoder layer 2 but binding CI includes 0, T's binding > 0 (m >= 3)
    li = R1["layers"].index(2)
    fb = []
    for m in [3, 4, 5, 6]:
        hb, tb = R1["binding"][f"H/m{m}"], R1["binding"][f"T/m{m}"]
        fb.append(H[m] == "early" and hb["lo"][li] <= 0 <= hb["hi"][li] and tb["lo"][li] > 0)
    if any(fb):
        out.append("F-bag(m=" + ",".join(str(m) for m, f in zip([3, 4, 5, 6], fb) if f) + ")")
    if not out or out == [x for x in out if x.startswith("F-bag")]:
        out.append("D")
    return {"classes": table, "outcome": out}


def main():
    items, root, rdir = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    rdir.mkdir(parents=True, exist_ok=True)
    I = json.loads(items.read_text())
    R1 = r1(root, I, None)
    R2 = r2(root, I)
    R3 = r3(root, I)
    D = decide(R1, R2) if R2 else None
    summary = {"R1": R1, "R2": R2, "R3": R3, "decision": D, "items": I["summary"]}
    (rdir / "summary.json").write_text(json.dumps(summary, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o)))
    print(json.dumps({"decision": D, "onsets_R1": {k: (v["point"], v["class"]) for k, v in R1["onset"].items()},
                      "onsets_R2": {k: {s: (b["onset_point"], b["onset_class"]) for s, b in v["by"].items()} for k, v in R2.items()}},
                     indent=1))


if __name__ == "__main__":
    main()
