"""E15: claim portability across independent runs (definitions in experiments/E15-claim-portability.md).

Writes results/e15/portability.json and prints a table.
"""
import itertools
import json
from pathlib import Path

import numpy as np

R = Path(__file__).resolve().parents[1] / "results"
SIZES = {"31m": ("e10", "e10"), "70m": ("e07", "e06"), "160m": ("e09", "e09")}


def runs(size):
    return [f"pythia-{size}"] + [f"pythia-{size}-seed{i}" for i in range(1, 10)]


def load(path):
    return json.loads(path.read_text()) if path.exists() else None


def e02_facts(run, step):
    r = load(R / "e02" / f"{run}__step{step}.json")
    if r is None:
        return None
    s, g = r["single"], r["groups"]
    heads = sorted({k.split("|")[0] for k in s})
    dm = {h: s[f"{h}|mean"]["dCL"] for h in heads}
    prev = r["roles"]["prev"]
    f = {"prev": prev}
    if "kcomp" in r:
        c, a = r["kcomp"]["clean"], r["kcomp"]["prev_ablated"]
        vals = [a[h] / c[h] for h in c if c[h] > 0.05]
        f["A1"] = bool(vals) and float(np.mean(vals)) <= 0.5
    else:
        f["A1"] = False
    pg = g.get("prev")
    f["A2"] = bool(pg) and pg["dCL"] >= 3 and pg["dCL"] > max(pg["random_dCL"])
    top = max(dm, key=dm.get)
    f["A3"] = top in prev
    if prev and pg:
        tp = max(prev, key=lambda h: r["S_prev"][h])
        f["A4"] = dm[tp] >= 0.5 * pg["dCL"]
        f["top_prev"] = tp
    else:
        f["A4"], f["top_prev"] = False, None
    return f


def usage(size, run, step):
    p_exp, c_exp = SIZES[size]
    if size == "70m":
        r7 = load(R / "e07" / f"{run}__step{step}.json")
        r6 = load(R / "e06" / f"{run}__step{step}.json")
        a7 = r7 and r7["p"]["0.1"]["R_target"]["median"]
        a8 = r6 and r6["classes"]["S6_lo"]["CL"]
    else:
        r = load(R / p_exp / f"{run}__step{step}.json")
        a7 = r and r["p"]["0.1"]["R"]
        a8 = r and r["classes"]["S6_lo"]
    return a7, a8


def portability_binary(facts, key):
    pairs = [(a, b) for a, b in itertools.permutations(facts, 2) if facts[a][key]]
    return [facts[b][key] for a, b in pairs]


def boot(runs_list, fn, n=1000):
    rng = np.random.default_rng(0)
    vals = []
    for _ in range(n):
        samp = list(rng.choice(runs_list, len(runs_list), replace=True))
        v = fn(samp)
        if v is not None:
            vals.append(v)
    return [float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))] if vals else None


def induction_table(size, step):
    facts = {r: e02_facts(r, step) for r in runs(size)}
    facts = {r: f for r, f in facts.items() if f}
    use = {r: usage(size, r, step) for r in facts}
    out = {}

    def port(keyfn, rs):
        rs = [x for x in rs if x in facts]
        pairs = [(a, b) for a, b in itertools.permutations(rs, 2) if a != b]
        res = [keyfn(a, b) for a, b in pairs]
        res = [x for x in res if x is not None]
        return float(np.mean(res)) if res else None

    defs = {
        "A1": lambda a, b: facts[b]["A1"] if facts[a]["A1"] else None,
        "A2": lambda a, b: facts[b]["A2"] if facts[a]["A2"] else None,
        "A3": lambda a, b: facts[b]["A3"] if facts[a]["A3"] else None,
        "A4": lambda a, b: facts[b]["A4"] if facts[a]["A4"] else None,
        "A5": lambda a, b: (facts[a]["top_prev"] in facts[b]["prev"]) if facts[a]["top_prev"] else None,
        "A6": lambda a, b: (facts[a]["top_prev"].split(".")[0] == facts[b]["top_prev"].split(".")[0])
        if facts[a]["top_prev"] and facts[b]["top_prev"] else None,
        "A7": lambda a, b: abs(use[a][0] - use[b][0]) <= 0.5 if use[a][0] is not None and use[b][0] is not None else None,
        "A8": lambda a, b: abs(use[a][1] - use[b][1]) <= 0.5 if use[a][1] is not None and use[b][1] is not None else None,
    }
    for k, fn in defs.items():
        out[k] = {"portability": port(fn, list(facts)), "ci95": boot(list(facts), lambda s, fn=fn: port(fn, s)),
                  "n_runs": len(facts), "holds_in": sum(bool(facts[r].get(k)) for r in facts) if k in "A1A2A3A4" else None}
    return out


def arbitration_table():
    rs = {}
    for f in sorted((R / "e13").glob("*__step*.json")):
        r = json.loads(f.read_text())
        rs[r["repo"].split("/")[-1]] = r
    if len(rs) < 2:
        return None
    names = list(rs)

    def top_mem(r):
        return r["memory_heads"][0][0]

    def drop(r):
        return r["gain_top_memory_head"]["1.0"] - r["gain_top_memory_head"]["2.0"]

    defs = {
        "B1": lambda a, b: abs(rs[a]["adoption"] - rs[b]["adoption"]) <= 0.05,
        "B2": lambda a, b: rs[b]["memory_heads"][0][1] >= 0.3 if rs[a]["memory_heads"][0][1] >= 0.3 else None,
        "B3": lambda a, b: top_mem(rs[a]) in [h for h, _ in rs[b]["memory_heads"]],
        "B4": lambda a, b: abs(int(top_mem(rs[a]).split(".")[0]) - int(top_mem(rs[b]).split(".")[0])) <= 1,
        "B5": lambda a, b: (0.5 <= drop(rs[b]) / drop(rs[a]) <= 2) if drop(rs[a]) > 0.01 else None,
    }

    def port(fn, subset):
        res = [fn(a, b) for a, b in itertools.permutations(subset, 2) if a != b]
        res = [x for x in res if x is not None]
        return float(np.mean(res)) if res else None

    return {k: {"portability": port(fn, names), "ci95": boot(names, lambda s, fn=fn: port(fn, s)), "n_runs": len(names)}
            for k, fn in defs.items()}


def within_run_control(size):
    """A1-A4 agreement between adjacent late checkpoints of the same run (positive control)."""
    agree = []
    for r in runs(size):
        a, b = e02_facts(r, 64000), e02_facts(r, 143000)
        if a and b:
            agree += [a[k] == b[k] for k in ("A1", "A2", "A3", "A4")]
    return float(np.mean(agree)) if agree else None


def main():
    out = {"induction": {}, "within_run_control": {}}
    for size in ("31m", "70m", "160m"):
        for step in (8000, 143000):
            t = induction_table(size, step)
            out["induction"][f"{size}@{step}"] = t
        out["within_run_control"][size] = within_run_control(size)
    out["arbitration_410m"] = arbitration_table()
    (R / "e15").mkdir(exist_ok=True)
    (R / "e15" / "portability.json").write_text(json.dumps(out, indent=1))
    keys = ["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8"]
    print("induction".ljust(14), " ".join(k.rjust(6) for k in keys))
    for k, t in out["induction"].items():
        print(k.ljust(14), " ".join(("%6.2f" % t[x]["portability"]) if t[x]["portability"] is not None else "     —" for x in keys),
              f"(runs {t['A1']['n_runs']})")
    print("within-run control", out["within_run_control"])
    if out["arbitration_410m"]:
        print("arbitration 410m", {k: (round(v["portability"], 2) if v["portability"] is not None else None, v["n_runs"])
                                   for k, v in out["arbitration_410m"].items()})


if __name__ == "__main__":
    main()
