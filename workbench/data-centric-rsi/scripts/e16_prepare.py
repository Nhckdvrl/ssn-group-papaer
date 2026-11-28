"""E16 stage 0 (CPU): select CodeContests problems and build the error panels.

For each problem (input: cc_eval.jsonl, one line per problem with Python3 correct/incorrect solutions):
  tests  = public + private + generated, capped at --max_tests (public first)
  ref    = Python3 correct solutions that pass every test in our sandbox (need >= 2; keep up to 3)
  human  = Python3 incorrect submissions of "wrong answer" type: every test runs to completion and at least one
           output is wrong (TLE / runtime-error submissions are excluded); flag whether they pass the public tests
  mutant = single-point AST mutants of ref[0] (comparison flip, integer constant +-1, + <-> -, * <-> //) that pass
           every public test and give a wrong answer on some hidden test without TLE/RE
Writes problems.jsonl (selected problems with refs, up to 2 human bugs and 2 mutants each) and stats.

Usage: python3 e16_prepare.py --src cc_eval.jsonl --out problems.jsonl [--workers 12] [--max_tests 60]
"""
import argparse
import ast
import copy
import json
import random
import sys
from multiprocessing import Pool

sys.path.insert(0, __import__("os").path.dirname(__file__))
from e16_exec import run, same  # noqa: E402

CMP_FLIP = {ast.Lt: ast.LtE, ast.LtE: ast.Lt, ast.Gt: ast.GtE, ast.GtE: ast.Gt, ast.Eq: ast.NotEq, ast.NotEq: ast.Eq}
BIN_FLIP = {ast.Add: ast.Sub, ast.Sub: ast.Add, ast.Mult: ast.FloorDiv, ast.FloorDiv: ast.Mult}


def mutants(code, limit=150):
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []
    sites = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Compare):
            for i, op in enumerate(n.ops):
                if type(op) in CMP_FLIP:
                    sites.append(("cmp", n, i))
        elif isinstance(n, ast.BinOp) and type(n.op) in BIN_FLIP:
            sites.append(("bin", n, None))
        elif isinstance(n, ast.Constant) and type(n.value) is int and abs(n.value) <= 1000:
            sites.append(("inc", n, None)); sites.append(("dec", n, None))
    out = []
    for k, (kind, node, i) in enumerate(sites[:limit]):
        t2 = copy.deepcopy(tree)
        target = [x for x in ast.walk(t2)][[x for x in ast.walk(tree)].index(node)]
        if kind == "cmp":
            target.ops[i] = CMP_FLIP[type(target.ops[i])]()
        elif kind == "bin":
            target.op = BIN_FLIP[type(target.op)]()
        elif kind == "inc":
            target.value = target.value + 1
        else:
            target.value = target.value - 1
        try:
            out.append((f"{kind}@{k}", ast.unparse(t2)))
        except Exception:
            pass
    return out


def outcome(code, tests, tl):
    """Per-test (status, correct) over the test list."""
    res = []
    for inp, exp in tests:
        st, so = run(code, inp, tl)
        res.append((st, st == "ok" and same(so, exp)))
        if st in ("tle", "refused"):
            break
    return res


def work(p):
    tl = float(p["time_limit"]) or 2.0
    pub = list(zip(p["public"]["input"], p["public"]["output"]))
    hid = list(zip(p["private"]["input"], p["private"]["output"])) + list(zip(p["generated"]["input"], p["generated"]["output"]))
    hid = hid[: max(0, ARGS.max_tests - len(pub))]
    tests = pub + hid
    refs = []
    for g in p["good"]:
        r = outcome(g, tests, tl)
        if len(r) == len(tests) and all(c for _, c in r):
            refs.append(g)
        if len(refs) == 3:
            break
    rec = {"id": p["id"], "n_tests": len(tests), "n_refs": len(refs)}
    if len(refs) < 2:
        return rec, None
    human = []
    for b in p["bad"]:
        r = outcome(b, tests, tl)
        if len(r) == len(tests) and all(s == "ok" for s, _ in r) and not all(c for _, c in r):
            human.append({"code": b, "passes_public": all(c for _, c in r[: len(pub)]),
                          "fail_rate": 1 - sum(c for _, c in r) / len(r)})
    rng = random.Random(p["id"])
    human.sort(key=lambda h: (not h["passes_public"], rng.random()))
    muts = []
    for tag, m in mutants(refs[0]):
        rp = outcome(m, pub, tl)
        if not (len(rp) == len(pub) and all(c for _, c in rp)):
            continue
        rh = outcome(m, hid, tl)
        if len(rh) == len(hid) and all(s == "ok" for s, _ in rh) and not all(c for _, c in rh):
            muts.append({"code": m, "op": tag, "fail_rate": 1 - sum(c for _, c in rh) / len(rh)})
    rng.shuffle(muts)
    rec.update(n_human_wa=len(human), n_mutants=len(muts))
    if not human:
        return rec, None
    sel = {k: p[k] for k in ("id", "name", "description", "cf_rating", "cf_tags", "time_limit")}
    sel.update(public=p["public"], tests=[[i, o] for i, o in tests], n_public=len(pub), refs=refs,
               human=human[:2], mutants=muts[:2])
    return rec, sel


def main():
    global ARGS
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=12); ap.add_argument("--max_tests", type=int, default=60)
    ARGS = ap.parse_args()
    probs = [json.loads(l) for l in open(ARGS.src)]
    with Pool(ARGS.workers, initializer=_init, initargs=(ARGS,)) as pool:
        res = pool.map(work, probs, chunksize=1)
    kept = [s for _, s in res if s]
    with open(ARGS.out, "w") as f:
        for s in kept:
            f.write(json.dumps(s) + "\n")
    stats = [r for r, _ in res]
    json.dump(stats, open(ARGS.out + ".stats.json", "w"), indent=1)
    print("problems", len(probs), "kept", len(kept), "with_mutants", sum(1 for s in kept if s["mutants"]),
          "human_pass_public", sum(1 for s in kept if s["human"][0]["passes_public"]), flush=True)


def _init(a):
    global ARGS
    ARGS = a


if __name__ == "__main__":
    main()
