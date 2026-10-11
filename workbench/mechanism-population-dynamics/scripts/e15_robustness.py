"""E15 confound audit: sensitivity of claim portability to threshold choices (POST-HOC robustness).

Writes results/e15/robustness.json.
"""
import itertools
import json

import numpy as np

import e15_portability as P


def port(vals):
    vals = [v for v in vals if v is not None]
    return round(float(np.mean(vals)), 2) if vals else None


def induction(size, step, a4_thr, layer_tol, use_tol, sprev_thr):
    rs = [r for r in P.runs(size) if P.e02_facts(r, step)]
    raw = {r: json.loads((P.R / "e02" / f"{r}__step{step}.json").read_text()) for r in rs}
    use = {r: P.usage(size, r, step) for r in rs}
    out = {}
    facts = {}
    for r, d in raw.items():
        s, g = d["single"], d["groups"]
        dm = {h.split("|")[0]: v["dCL"] for h, v in s.items() if h.endswith("|mean")}
        prev = [h for h, v in d["S_prev"].items() if v >= sprev_thr]
        tp = max(prev, key=lambda h: d["S_prev"][h]) if prev else None
        pg = g.get("prev")
        facts[r] = {"prev": prev, "tp": tp,
                    "A4": bool(tp and pg) and dm[tp] >= a4_thr * pg["dCL"]}
    pairs = list(itertools.permutations(rs, 2))
    out["A4"] = port([facts[b]["A4"] if facts[a]["A4"] else None for a, b in pairs])
    out["A5"] = port([(facts[a]["tp"] in facts[b]["prev"]) if facts[a]["tp"] else None for a, b in pairs])
    out["A6"] = port([abs(int(facts[a]["tp"].split(".")[0]) - int(facts[b]["tp"].split(".")[0])) <= layer_tol
                      if facts[a]["tp"] and facts[b]["tp"] else None for a, b in pairs])
    out["A7"] = port([abs(use[a][0] - use[b][0]) <= use_tol if None not in (use[a][0], use[b][0]) else None for a, b in pairs])
    out["A8"] = port([abs(use[a][1] - use[b][1]) <= use_tol if None not in (use[a][1], use[b][1]) else None for a, b in pairs])
    return out


def arbitration(b1_tol):
    rs = [json.loads(f.read_text()) for f in sorted((P.R / "e13").glob("*__step*.json"))]
    return port([abs(a["adoption"] - b["adoption"]) <= b1_tol for a, b in itertools.permutations(rs, 2)])


def main():
    res = {"induction": {}, "B1": {}}
    for size in ("31m", "70m", "160m"):
        for a4 in (0.3, 0.5, 0.7):
            for lt in (0, 1):
                for ut in (0.25, 0.5, 1.0):
                    for sp in (0.4, 0.5, 0.6):
                        key = f"{size}|a4={a4}|layer±{lt}|use±{ut}|sprev≥{sp}"
                        res["induction"][key] = induction(size, 143000, a4, lt, ut, sp)
    for t in (0.025, 0.05, 0.10):
        res["B1"][str(t)] = arbitration(t)
    (P.R / "e15" / "robustness.json").write_text(json.dumps(res, indent=1))
    for size in ("31m", "70m", "160m"):
        vals = {k: [v[k] for kk, v in res["induction"].items() if kk.startswith(size) and v[k] is not None]
                for k in ("A4", "A5", "A6", "A7", "A8")}
        print(size, {k: (min(v), max(v)) for k, v in vals.items() if v})
    print("B1", res["B1"])


if __name__ == "__main__":
    main()
