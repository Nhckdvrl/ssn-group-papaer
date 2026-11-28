"""E17-0: build the problem file from LeetCodeDataset (test split).

Keeps problems whose method signature takes plain values (no TreeNode/ListNode starter), parses the hidden tests into
keyword-argument dicts, re-runs the reference on them in our harness and keeps the tests on which the reference's
output equals the dataset's output (tests with unparseable input/output or 'Execution timed out' are dropped). A problem
is kept if at least 20 hidden tests remain. The reference's own output becomes the hidden expected value.
Usage: python3 e17_prepare.py <LeetCodeDataset-test.jsonl> <out problems.jsonl>
"""
import ast
import json
import os
import sys
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(__file__))
from e17_common import parse_kwargs, run_prog, same  # noqa: E402


def matches(o, raw):
    """reference output repr o vs the dataset's raw output text (strings are stored unquoted there)"""
    try:
        if same(o, repr(ast.literal_eval(raw))):
            return True
    except Exception:
        pass
    try:
        v = ast.literal_eval(o)
    except Exception:
        return False
    return isinstance(v, str) and v == raw


def prep(r):
    if "TreeNode" in r["starter_code"] or "ListNode" in r["starter_code"]:
        return None, "node"
    method = r["entry_point"].split(".", 1)[1]
    ins, exp = [], []
    for t in r["input_output"]:
        kw = parse_kwargs(t["input"])
        if kw is None or t["output"].startswith("Execution timed out"):
            continue
        ins.append(kw); exp.append(t["output"])
    out = run_prog(r["prompt"], r["completion"], method, ins)
    keep = [(i, o) for i, o, e in zip(ins, out, exp) if not o.startswith("EXC:") and matches(o, e)]
    if len(keep) < 20:
        return None, f"few_tests({len(keep)}/{len(ins)})"
    return dict(id=r["task_id"], difficulty=r["difficulty"], date=r["estimated_date"], desc=r["problem_description"],
                starter=r["starter_code"], prefix=r["prompt"], ref=r["completion"], method=method,
                hidden=[i for i, _ in keep], hidden_out=[o for _, o in keep], n_dropped=len(r["input_output"]) - len(keep)), "ok"


if __name__ == "__main__":
    R = [json.loads(l) for l in open(sys.argv[1])]
    with Pool(20) as p:
        res = p.map(prep, R, chunksize=1)
    import collections
    print(collections.Counter(w if not w.startswith("few") else "few_tests" for _, w in res))
    keep = [x for x, _ in res if x]
    with open(sys.argv[2], "w") as f:
        for x in keep:
            f.write(json.dumps(x) + "\n")
    print("kept", len(keep), collections.Counter(x["difficulty"] for x in keep), "median hidden",
          sorted(len(x["hidden"]) for x in keep)[len(keep) // 2])
