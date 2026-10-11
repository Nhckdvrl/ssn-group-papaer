"""critical_period: analysis of the controlled runs (sources of variance, basin of attraction, critical period)."""
import itertools
import json
import re

import numpy as np
from scipy.stats import spearmanr

import common as mc
D = mc.RESULTS / "controlled"
MAPS = ("M1", "M2")


def load():
    R = {}
    for f in D.glob("S_*.json"):
        d = json.loads(f.read_text())
        R[d["name"]] = {int(k): v for k, v in d["measures"].items()}
    return R


def ok(m, *names):
    return m != "M1" or all(n in HAS_IND for n in names)


HAS_IND = set()


def sim(a, b, m):
    A, B = np.array(a[m]), np.array(b[m])
    full = spearmanr(A.ravel(), B.ravel())[0]
    within = np.nanmean([spearmanr(A[l], B[l])[0] for l in range(A.shape[0])])
    return float(full), float(within)


def parse(name):
    m = re.match(r"S_i(\d+)_(\w+?)_o(\d+)(.*)$", name)
    return int(m.group(1)), m.group(2), int(m.group(3)), m.group(4)


def main():
    R = load()
    fin = {n: r[max(r)] for n, r in R.items() if max(r) == 10000}
    HAS_IND.update(n for n, v in fin.items() if v["M1_max"] > 0.3)  # M1 comparisons only among runs with induction (crossing_sizes rule)
    out = {"n_runs": len(fin), "A": {}, "B": {}, "C": {}, "D": {}, "lockin": {}}
    out["no_induction_runs"] = sorted(set(fin) - HAS_IND)
    base = {n: parse(n) for n in fin if parse(n)[3] == "" and parse(n)[0] == parse(n)[2] and "_std" not in n and "_lr" not in n}  # crossed runs (order = init)
    out["pc"] = {"M1max_final_min": min(v["M1_max"] for v in fin.values()), "gain_final_min": min(v["copy_gain"] for v in fin.values()),
                 "relM2_min": min(v["rel_M2"] for v in fin.values())}
    for m in MAPS:
        g = {"SI": [], "SD": [], "DD": []}
        for a, b in itertools.combinations(base, 2):
            if not ok(m, a, b):
                continue
            (ia, ca, _, _), (ib, cb, _, _) = base[a], base[b]
            c = "SI" if ia == ib else "SD" if ca == cb else "DD"
            g[c].append(sim(fin[a], fin[b], m))
        out["A"][m] = {c: {"full": float(np.mean([x[0] for x in v])), "within": float(np.mean([x[1] for x in v])), "n": len(v)}
                       for c, v in g.items() if v}
        # permutation null for SI - SD (shuffle init labels within corpus)
        names = sorted(base)
        obs = out["A"][m]["SI"]["full"] - out["A"][m]["SD"]["full"] if "SI" in out["A"][m] and "SD" in out["A"][m] else None
        rng = np.random.default_rng(0)
        null = []
        for _ in range(500):
            perm = {}
            for c in {base[n][1] for n in names}:
                ns = [n for n in names if base[n][1] == c]
                inits = rng.permutation([base[n][0] for n in ns])
                perm.update({n: i for n, i in zip(ns, inits)})
            gg = {"SI": [], "SD": []}
            for a, b in itertools.combinations(names, 2):
                if not ok(m, a, b):
                    continue
                c = "SI" if perm[a] == perm[b] else "SD" if base[a][1] == base[b][1] else None
                if c:
                    gg[c].append(sim(fin[a], fin[b], m)[0])
            if gg["SI"] and gg["SD"]:
                null.append(np.mean(gg["SI"]) - np.mean(gg["SD"]))
        if obs is not None:
            out["A"][m]["SI_minus_SD"] = obs
            out["A"][m]["perm_p"] = float((np.array(null) >= obs).mean()) if null else None
    # B: order only; C: eps dose and rerun (all relative to the base run of the same init on c4)
    for n, v in fin.items():
        i, c, o, tail = parse(n)
        ref = f"S_i{i}_c4_o{i}"
        if c != "c4" or ref not in fin or n == ref:
            continue
        key = "B" if (o != i and not tail) else "C" if (tail.startswith("_eps") or tail.startswith("_rerun")) else "D" if tail.startswith("_b") else None
        if not key:
            continue
        out[key][n] = {m: sim(v, fin[ref], m) for m in MAPS if ok(m, n, ref)}
    # lock-in curves: each crossed run's map at step t vs its own final
    for n in base:
        out["lockin"][n] = {t: {m: sim(R[n][t], fin[n], m)[0] for m in MAPS if ok(m, n)} for t in sorted(R[n]) if t > 0}
    (D / "analysis.json").write_text(json.dumps(out, indent=1))
    print("runs", out["n_runs"], "pc", out["pc"])
    for m in MAPS:
        print("A", m, {c: (round(v["full"], 3), round(v["within"], 3), v["n"]) for c, v in out["A"][m].items() if isinstance(v, dict)},
              "SI-SD", round(out["A"][m].get("SI_minus_SD", float("nan")), 3), "p", out["A"][m].get("perm_p"))
    for k in ("B", "C", "D"):
        for n, v in sorted(out[k].items()):
            print(k, n, {m: tuple(round(x, 3) for x in v[m]) for m in v})


if __name__ == "__main__":
    main()
