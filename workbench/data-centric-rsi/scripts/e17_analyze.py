"""E17-0 readouts from the execution matrix (see experiments/E17-self-reference.md).

Unit = one test GENERATION (one sampled set of ~8 tests, as one RL reward draw). Pooling a producer's 4 generations
saturates the trusted regime (smoke run 2026-11-29: Qwen's pooled suites missed ~1% of its own wrong programs), so the
pooled suite is not used for the main readout.
Suite S_j,g(p) = valid inputs of producer j's generation g on problem p. Two regimes:
  trusted : expected value = the reference's output
  model   : expected value = producer's own written output (tests without a parseable output are dropped)
A wrong program x is MISSED by S iff it passes every test of S (S non-empty in that regime).
M[i][j] = mean over problems (i has wrong programs, j has >=1 non-empty generation) of the mean over j's non-empty
          generations and i's wrong programs of missed.
Test-level M_test[i][j]: same, with single tests instead of generations.
D(i,k)  = [(M_ii + M_kk) - (M_ik + M_ki)] / 2 on problems where all four cells exist.
Problem-clustered bootstrap (2000). Noise floor: D from generations {0,1} vs {2,3}.
Usage: python3 e17_analyze.py --matrix matrix.jsonl.gz --models a,b,... --out summary.json
"""
import argparse
import collections
import gzip
import itertools
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(__file__))
from e17_common import same  # noqa: E402


def suites(r, j, regime, samples=None, kind="tests"):
    """{generation sample: [(input index, expected repr)]} for producer j (non-empty generations only)"""
    out = {}
    for t in r["tests"]:
        if t["producer"] != j or t["kind"] != kind or (samples is not None and t["sample"] not in samples):
            continue
        i = t["inp"]
        if not r["valid"][i]:
            continue
        if regime == "trusted":
            e = r["ref_gen"][i]
        else:
            if t["model_out"] is None:
                continue
            e = t["model_out"]
        g = t["sample"] if kind == "tests" else t["cond_prog"]
        if (i, e) not in out.setdefault(g, []):
            out[g].append((i, e))
    return out


def passes(prog, suite):
    return all(same(prog["gen"][i], e) for i, e in suite)


PLAUSIBLE = 0.0  # set in main: minimum hidden-test pass rate for a wrong program to count


def wrong(r, i):
    return [p for p in r["programs"] if p["model"] == i and not p["noprog"] and not p["correct"]
            and p.get("hidden_pass", 0) >= PLAUSIBLE]


def miss_table(R, models, regime, samples=None, level="gen"):
    """per problem: {(i,j): mean missed over j's generations (or single tests) x i's wrong programs}"""
    T = []
    for r in R:
        row = {}
        S = {j: suites(r, j, regime, samples) for j in models}
        for i in models:
            W = wrong(r, i)
            if not W:
                continue
            for j in models:
                units = list(S[j].values()) if level == "gen" else [[t] for g in S[j].values() for t in g]
                if units:
                    row[(i, j)] = sum(passes(x, u) for u in units for x in W) / (len(units) * len(W))
        T.append(row)
    return T


def M_of(T, i, j):
    v = [row[(i, j)] for row in T if (i, j) in row]
    return (sum(v) / len(v), len(v)) if v else (None, 0)


def D_of(T, i, k):
    v = [(row[(i, i)] + row[(k, k)] - row[(i, k)] - row[(k, i)]) / 2 for row in T
         if all(x in row for x in ((i, i), (k, k), (i, k), (k, i)))]
    return v


def boot(v, B=2000, seed=0):
    if not v:
        return None, None, None
    rng = random.Random(seed); n = len(v)
    s = sorted(sum(rng.choice(v) for _ in range(n)) / n for _ in range(B))
    return sum(v) / n, s[int(.025 * B)], s[int(.975 * B) - 1]


def false_reject(R, models):
    """model regime: share of (generation, correct program) pairs where a correct program fails the generation"""
    out = {}
    for j in models:
        num = den = 0
        for r in R:
            C = [p for p in r["programs"] if p["correct"]]
            for u in suites(r, j, "model").values():
                for x in C:
                    den += 1; num += not passes(x, u)
        out[j] = num / den if den else None
    return out


def content_errors(R, models):
    """tests (valid input, model output != reference): does some wrong program output exactly that value?
    returned per producer j: rate of matching j's own wrong programs vs other models' wrong programs, each
    conditioned on problems where that learner has a wrong program."""
    res = {}
    for j in models:
        own_n = own_d = oth_n = oth_d = bad = tot = 0
        for r in R:
            for t in r["tests"]:
                if t["producer"] != j or t["kind"] != "tests" or t["model_out"] is None or not r["valid"][t["inp"]]:
                    continue
                tot += 1
                if same(t["model_out"], r["ref_gen"][t["inp"]]):
                    continue
                bad += 1
                for i in models:
                    W = wrong(r, i)
                    if not W:
                        continue
                    hit = any(same(x["gen"][t["inp"]], t["model_out"]) for x in W)
                    if i == j:
                        own_d += 1; own_n += hit
                    else:
                        oth_d += 1; oth_n += hit
        res[j] = dict(valid_tests_with_output=tot, wrong_expected=bad / tot if tot else None,
                      match_own_wrong=own_n / own_d if own_d else None, n_own=own_d,
                      match_other_wrong=oth_n / oth_d if oth_d else None, n_other=oth_d)
    return res


def overlap(R, models, regime):
    """per pair of producers, over (wrong program, generation index g) with both producers' generation g non-empty:
    P(both miss) / (P(miss_j) P(miss_l))"""
    res = {}
    for j, l in itertools.combinations(models, 2):
        a = b = ab = n = 0
        for r in R:
            Sj, Sl = suites(r, j, regime), suites(r, l, regime)
            gs = set(Sj) & set(Sl)
            for x in [p for p in r["programs"] if not p["noprog"] and not p["correct"]]:
                for g in gs:
                    mj, ml = passes(x, Sj[g]), passes(x, Sl[g])
                    n += 1; a += mj; b += ml; ab += mj and ml
        if n and a and b:
            res[f"{j}|{l}"] = dict(n=n, miss_j=a / n, miss_l=b / n, both=ab / n, ratio=(ab / n) / ((a / n) * (b / n)))
    return res


def grpo(R, models, regime):
    """learner i's 8-sample group per problem, reward = passes one generation of producer j's tests (averaged over
    generations). Share of groups with non-zero advantage; flip rate = P(reward wrong > reward correct) over
    (wrong, correct) pairs inside a group."""
    res = {}
    for i in models:
        for j in models + ["hidden"]:
            nz = groups = flips = pairs = 0
            for r in R:
                G = [p for p in r["programs"] if p["model"] == i]
                if not G:
                    continue
                draws = [None] if j == "hidden" else list(suites(r, j, regime).values())
                for u in draws:
                    rew = [p["correct"] for p in G] if u is None else [(not p["noprog"]) and passes(p, u) for p in G]
                    groups += 1; nz += len(set(rew)) > 1
                    for (p, rp), (q, rq) in itertools.product(zip(G, rew), zip(G, rew)):
                        if not p["correct"] and q["correct"]:
                            pairs += 1; flips += rp and not rq
            res[f"{i}<-{j}"] = dict(groups=groups, nonzero=nz / groups if groups else None,
                                    flip=flips / pairs if pairs else None, pairs=pairs)
    return res


def positive_control(R, models):
    """programs that got a candidate-conditioned generation: missed by that generation vs by the same model's plain
    generations (mean over them)"""
    res = {}
    for regime in ("trusted", "model"):
        for j in models:
            v = []
            for r in R:
                progs = {f'{p["model"]}:{p["sample"]}': p for p in r["programs"]}
                plain = list(suites(r, j, regime).values())
                for pid, S in suites(r, j, regime, kind="condtests").items():
                    x = progs.get(pid)
                    if x is None or x["correct"] or x["noprog"] or not plain:
                        continue
                    v.append((float(passes(x, S)), sum(passes(x, u) for u in plain) / len(plain)))
            if v:
                res[f"{j}/{regime}"] = dict(n=len(v), miss_cond=sum(a for a, _ in v) / len(v),
                                            miss_plain=sum(b for _, b in v) / len(v),
                                            diff=boot([a - b for a, b in v]))
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--matrix", required=True); ap.add_argument("--models", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--plausible", type=float, default=0.0,
                    help="only wrong programs passing at least this share of hidden tests (main readout: 0.7)")
    a = ap.parse_args()
    global PLAUSIBLE
    PLAUSIBLE = a.plausible
    models = a.models.split(",")
    R = [json.loads(l) for l in gzip.open(a.matrix, "rt")]
    R = [r for r in R if r["ref_ok"]]
    out = {"n_problems": len(R)}
    out["solve"] = {i: sum(p["correct"] for r in R for p in r["programs"] if p["model"] == i) /
                    max(1, sum(1 for r in R for p in r["programs"] if p["model"] == i)) for i in models}
    out["problems_with_wrong"] = {i: sum(bool(wrong(r, i)) for r in R) for i in models}
    out["valid_input_rate"] = {}
    for j in models:
        ts = [r["valid"][t["inp"]] for r in R for t in r["tests"] if t["producer"] == j and t["kind"] == "tests"]
        out["valid_input_rate"][j] = (sum(ts) / len(ts) if ts else None, len(ts))
    for regime in ("trusted", "model"):
        T = miss_table(R, models, regime)
        out[f"M_{regime}"] = {f"{i}<-{j}": M_of(T, i, j) for i in models for j in models}
        Tt = miss_table(R, models, regime, level="test")
        out[f"Mtest_{regime}"] = {f"{i}<-{j}": M_of(Tt, i, j) for i in models for j in models}
        out[f"Dtest_{regime}"] = {f"{i}|{k}": dict(n=len(D_of(Tt, i, k)), D=boot(D_of(Tt, i, k)))
                                  for i, k in itertools.combinations(models, 2)}
        h1 = miss_table(R, models, regime, {0, 1}); h2 = miss_table(R, models, regime, {2, 3})
        Dres = {}
        for i, k in itertools.combinations(models, 2):
            v = D_of(T, i, k)
            d1, d2 = D_of(h1, i, k), D_of(h2, i, k)
            Dres[f"{i}|{k}"] = dict(n=len(v), D=boot(v), half1=boot(d1)[0], half2=boot(d2)[0])
        out[f"D_{regime}"] = Dres
        out[f"overlap_{regime}"] = overlap(R, models, regime)
        out[f"grpo_{regime}"] = grpo(R, models, regime)
    out["false_reject_model"] = false_reject(R, models)
    out["content_errors"] = content_errors(R, models)
    out["positive_control"] = positive_control(R, models)
    json.dump(out, open(a.out, "w"), indent=1)
    for regime in ("trusted", "model"):
        print(f"== miss matrix ({regime}); rows learner, cols producer")
        print("        " + " ".join(f"{j:>7s}" for j in models))
        for i in models:
            print(f"{i:>7s} " + " ".join(
                f"{out[f'M_{regime}'][f'{i}<-{j}'][0]:7.3f}" if out[f'M_{regime}'][f'{i}<-{j}'][0] is not None else "      -"
                for j in models))
        print(f"== D ({regime}) mean [CI] (half1, half2)")
        for k, v in out[f"D_{regime}"].items():
            m, lo, hi = v["D"]
            if m is not None:
                print(f"  {k:15s} n={v['n']:3d} {m:+.3f} [{lo:+.3f},{hi:+.3f}]  ({v['half1']:+.3f}, {v['half2']:+.3f})"
                      if v['half1'] is not None and v['half2'] is not None else f"  {k} n={v['n']} {m:+.3f}")
    print("solve", out["solve"]); print("problems_with_wrong", out["problems_with_wrong"])
    print("valid_input_rate", out["valid_input_rate"]); print("false_reject_model", out["false_reject_model"])
    print("content_errors", json.dumps(out["content_errors"], indent=0))
    print("positive_control", json.dumps(out["positive_control"], indent=0))


if __name__ == "__main__":
    main()
