"""E40 analysis: per-demo support s_t = (ld_full - ld_without_t) * (2*pole_t - 1) and its structure.

usage: analyze_kernel.py [tags...]   (default: every results/kernel/*.npz)
1. Known account (I04, simplest form) fitted on even bases, evaluated on odd bases:
     s_t ~ distance bins + vocabulary relation(demo vocab, query vocab) + number of other demos with the same pole
   (no position, no annotator, no structure).  Then the gain in held-out R^2 from adding each extra factor alone.
2. Residual tables of the known account by: position x structure, annotator match x vocabulary relation,
   same class, flipped label, structure.
3. Kernel shape: mean support by distance bin, by model.
Writes results/kernel/analysis.json."""
import json, sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DBINS = [0, 3, 6, 10, 15, 20, 30, 40, 80]


def demos():
    meta = {}
    for l in open(ROOT / "data/kernel/rows.jsonl"):
        r = json.loads(l)
        if r["var"] == -1:
            meta[r["base_id"]] = r["meta"]
    return meta


def table(tag, meta):
    z = np.load(ROOT / f"results/kernel/{tag}.npz")
    ld = dict(zip(z["uid"], z["ld"]))
    recs = []
    for b, m in meta.items():
        i = (int(b.split("_")[1]) - 940000) // 7919        # build index; split = (i // 4) % 2 is balanced over every factor
        bi = (i // 4) % 2
        full = ld[f"{b}|-1"]
        qv = "same" if m["qa"] == 0 else m["v"]
        for t in range(16):
            pole = m["ys"][t]
            s = (full - ld[f"{b}|{t}"]) * (2 * pole - 1)
            dv = "same" if m["ann"][t] == 0 else m["v"]
            npole = sum(1 for u in range(16) if u != t and m["ys"][u] == pole)
            # same pole among demos with the same vocabulary as demo t
            npole_v = sum(1 for u in range(16) if u != t and m["ys"][u] == pole and ("same" if m["ann"][u] == 0 else m["v"]) == dv)
            recs.append(dict(base=bi, s=s, full=full * (2 * pole - 1), dist=abs(m["xs"][t] - m["qx"]), pos=t, tau=m["tau"],
                             same_ann=int(m["ann"][t] == m["qa"]), vrel=f"{dv}->{qv}", same_cls=int(m["cls"][t] == m["qc"]),
                             flip=m["flip"][t], npole=npole, npole_v=npole_v, ann=m["ann"][t], qa=m["qa"], v=m["v"]))
    return recs


def design(R, factors):
    cols, names = [np.ones(len(R))], ["1"]
    for f in factors:
        if f == "dist":
            b = np.digitize([r["dist"] for r in R], DBINS[1:-1])
            for k in range(1, len(DBINS) - 1):
                cols.append((b == k).astype(float)); names.append(f"dist{k}")
        elif f in ("npole", "npole_v"):
            cols.append(np.array([r[f] for r in R], float)); names.append(f)
        elif f == "pos":
            for k in range(1, 4):
                cols.append(np.array([r["pos"] // 4 == k for r in R], float)); names.append(f"pos{k}")
        elif f == "pos_x_tau":
            for tau in ("ann", "time", "noise"):
                for k in range(1, 4):
                    cols.append(np.array([(r["pos"] // 4 == k) and r["tau"] == tau for r in R], float)); names.append(f"pos{k}:{tau}")
        else:  # categorical
            levels = sorted({r[f] for r in R})
            for lv in levels[1:]:
                cols.append(np.array([r[f] == lv for r in R], float)); names.append(f"{f}={lv}")
    return np.stack(cols, 1), names


def fit_eval(R, factors):
    X, names = design(R, factors)
    y = np.array([r["s"] for r in R])
    tr = np.array([r["base"] == 0 for r in R])
    beta, *_ = np.linalg.lstsq(X[tr], y[tr], rcond=None)
    pred = X @ beta
    r2 = 1 - ((y[~tr] - pred[~tr]) ** 2).sum() / ((y[~tr] - y[~tr].mean()) ** 2).sum()
    return float(r2), dict(zip(names, beta.round(3).tolist())), y - pred, tr


def group(R, res, mask, keys):
    out = {}
    for i, r in enumerate(R):
        if not mask[i]:
            continue
        k = "|".join(str(r[x]) for x in keys)
        out.setdefault(k, []).append(res[i])
    return {k: [round(float(np.mean(v)), 3), len(v)] for k, v in sorted(out.items())}


def main():
    meta = demos()
    tags = sys.argv[1:] or sorted(p.stem for p in (ROOT / "results/kernel").glob("*.npz"))
    out = {}
    for tag in tags:
        R = table(tag, meta)
        known = ["dist", "vrel", "npole"]
        r2k, beta, res, tr = fit_eval(R, known)
        gains = {}
        for extra in (["pos"], ["same_ann"], ["tau"], ["same_cls"], ["flip"], ["pos_x_tau"], ["npole_v"], ["vrel", "same_ann"]):
            fs = known + extra
            if extra == ["vrel", "same_ann"]:  # annotator x vocabulary interaction
                for r in R:
                    r["ann_x_vrel"] = f"{r['same_ann']}:{r['vrel']}"
                fs = known + ["ann_x_vrel"]
            gains["+" + "x".join(extra)] = round(fit_eval(R, fs)[0] - r2k, 4)
        held = ~tr
        y = np.array([r["s"] for r in R])
        o = {"n_demos": len(R), "mean_support": float(y.mean()), "frac_negative": float((y < 0).mean()),
             "r2_known_heldout": round(r2k, 4), "beta_known": beta, "r2_gain": gains,
             "kernel_by_dist": group(R, y, np.ones(len(R), bool), ["dist_bin"]) if False else None,
             "resid_pos_x_tau": group(R, res, held, ["tau", "pos"]),
             "resid_ann_x_vrel": group(R, res, held, ["same_ann", "vrel"]),
             "resid_same_cls": group(R, res, held, ["same_cls"]),
             "resid_flip_x_tau": group(R, res, held, ["tau", "flip"]),
             "support_by_vrel": group(R, y, np.ones(len(R), bool), ["vrel"]),
             "support_by_npole": group(R, y, np.ones(len(R), bool), ["npole"])}
        for r in R:
            r["dist_bin"] = int(np.digitize(r["dist"], DBINS[1:-1]))
        o["kernel_by_dist"] = group(R, y, np.ones(len(R), bool), ["dist_bin"])
        o["kernel_by_dist_x_cls"] = group(R, y, np.ones(len(R), bool), ["same_cls", "dist_bin"])
        out[tag] = o
        print(f"== {tag}: mean s {o['mean_support']:+.3f}  neg {o['frac_negative']:.2f}  R2 known {r2k:.3f}  gains {gains}", flush=True)
    (ROOT / "results/kernel/analysis.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
