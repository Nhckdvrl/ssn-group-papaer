"""E16 stage 0, function-level: prepare HumanEval+ problems.

ref_plain    = prompt + canonical_solution;  ref_contract = prompt + contract + canonical_solution (input checks)
tests        = base_input + the first plus_input items, at most --max_tests; expected = ref_plain results
mutants      = single-point AST mutants of ref_plain (see e16_prepare.mutants) that match the reference on every
               base input but differ (wrong value, not an exception) on some plus input; up to 2
Usage: python3 e16f_prepare.py --src HumanEvalPlus.jsonl --out problems_f.jsonl [--workers 12] [--max_tests 60]
"""
import argparse
import json
import os
import random
import sys
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(__file__))
from e16_prepare import mutants  # noqa: E402
from e16f_common import run_calls, same_result  # noqa: E402

A = None


def work(t):
    entry = t["entry_point"]
    ref_plain = t["prompt"] + t["canonical_solution"]
    ref_contract = t["prompt"] + t["contract"] + t["canonical_solution"]
    base = t["base_input"]
    plus = t["plus_input"][: max(0, A.max_tests - len(base))]
    args = base + plus
    exp = run_calls(ref_plain, entry, args)
    rec = {"task_id": t["task_id"]}
    if exp is None or any(e.startswith("EXC:") for e in exp):
        rec["skip"] = "reference failed"
        return rec, None
    chk = run_calls(ref_contract, entry, args)
    if chk is None or any(c.startswith("EXC:") for c in chk):
        rec["skip"] = "contract rejects dataset inputs"
        return rec, None
    nb = len(base)
    muts = []
    for tag, m in mutants(ref_plain, limit=150):
        out = run_calls(m, entry, args)
        if out is None:
            continue
        if all(same_result(o, e, t["atol"]) for o, e in zip(out[:nb], exp[:nb])):
            wrong = [not same_result(o, e, t["atol"]) for o, e in zip(out[nb:], exp[nb:])]
            if any(wrong) and not any(o.startswith("EXC:") for o in out):
                muts.append({"code": m, "op": tag, "fail_rate": sum(wrong) / max(1, len(wrong))})
    random.Random(t["task_id"]).shuffle(muts)
    rec["n_mutants"] = len(muts)
    p = {"id": t["task_id"], "entry": entry, "prompt": t["prompt"], "atol": t["atol"], "ref_plain": ref_plain,
         "ref_contract": ref_contract, "tests": [[a, e] for a, e in zip(args, exp)], "n_base": nb, "mutants": muts[:2]}
    return rec, p


def init(a):
    global A
    A = a


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=12); ap.add_argument("--max_tests", type=int, default=60)
    a = ap.parse_args()
    tasks = [json.loads(l) for l in open(a.src)]
    with Pool(a.workers, initializer=init, initargs=(a,)) as pool:
        res = pool.map(work, tasks, chunksize=1)
    kept = [p for _, p in res if p]
    with open(a.out, "w") as f:
        for p in kept:
            f.write(json.dumps(p) + "\n")
    json.dump([r for r, _ in res], open(a.out + ".stats.json", "w"), indent=1)
    print("tasks", len(tasks), "kept", len(kept), "with_mutants", sum(1 for p in kept if p["mutants"]),
          "skips", sum(1 for r, _ in res if "skip" in r), flush=True)


if __name__ == "__main__":
    main()
