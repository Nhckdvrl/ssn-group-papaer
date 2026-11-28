"""Oracle audit (round 9): are 'successful' distinguishing inputs robust to the single-reference oracle?
For each successful disc_ref / disc_cand instance: run the input on independent correct programs (solve outputs of
all six models that pass every HumanEval+ test, deduplicated). robust = every independent correct program agrees
with the reference; bug_ok = the bug's output equals some independent correct program's output (the 'error' is
an allowed behaviour)."""
import json, re, sys, collections
sys.path.insert(0, "/home/xiang/ssn-group-papaer/workbench/data-centric-rsi/scripts")
from e16f_common import parse_call, run_calls, same_result
from e16f_score import extract_call, imports_of
from multiprocessing import Pool
B = sys.argv[1]  # scratchpad e16 dir
M = ["c15", "c7", "qwen", "cure", "r1", "tcs"]
P = {json.loads(l)["id"]: json.loads(l) for l in open(f"{B}/f11/fdata/problems_f.jsonl")}
indep = collections.defaultdict(list)
for t in M:
    G = [json.loads(l) for l in open(f"{B}/f12/fgen/solve_{t}.jsonl")] if False else [json.loads(l) for l in open(f"{B}/f11/fgen/solve_{t}.jsonl")]
    S = [json.loads(l) for l in open(f"{B}/f12/fscored/solve_{t}.jsonl")]
    for g, s in zip(G, S):
        assert g["pid"] == s["pid"]
        if s.get("pass_all"):
            m = re.findall(r"```python[ \t]*\n(.*?)```", g["text"].split("</think>")[-1], re.DOTALL)
            code = imports_of(P[g["pid"]]["prompt"]) + m[-1]
            if code not in indep[g["pid"]] and len(indep[g["pid"]]) < 8:
                indep[g["pid"]].append(code)
jobs = []
for t in M:
    G = [json.loads(l) for l in open(f"{B}/f11/fgen/ev_{t}.jsonl")]
    S = [json.loads(l) for l in open(f"{B}/f12/fscored/ev_{t}.jsonl")]
    for g, s in zip(G, S):
        assert (g["pid"], g["inst"], g["sample"], g["task"]) == (s["pid"], s["inst"], s["sample"], s["task"])
        if s.get("success"):
            jobs.append((t, g["task"], g["source"], g["pid"], g["text"], g["code"]))
def audit(j):
    t, task, src, pid, text, bug = j
    p = P[pid]
    call, _ = extract_call(text, p["entry"]); args = parse_call(call, p["entry"])
    ref = run_calls(p["ref_plain"], p["entry"], [args])[0]
    b = run_calls(imports_of(p["prompt"]) + bug, p["entry"], [args]); b = b[0] if b else "EXC:fail"
    outs = []
    for c in indep[pid]:
        o = run_calls(c, p["entry"], [args]); outs.append(o[0] if o else "EXC:fail")
    robust = all(same_result(o, ref, p["atol"]) for o in outs)
    bug_ok = any(same_result(o, b, p["atol"]) for o in outs)
    return t, task, src, len(outs), robust, bug_ok
with Pool(16) as pool:
    res = pool.map(audit, jobs, chunksize=2)
agg = collections.defaultdict(lambda: [0, 0, 0, 0])
for t, task, src, k, robust, bug_ok in res:
    a = agg[(t, task, src)]; a[0] += 1; a[1] += robust; a[2] += bug_ok; a[3] += k
print("independent correct programs per problem (ev set):",
      sorted(collections.Counter(min(len(indep[pid]), 8) for pid in {j[3] for j in jobs}).items()))
for k in sorted(agg):
    n, r, bo, kk = agg[k]
    print(k, "successes", n, "robust %.2f" % (r / n), "bug-output-allowed-by-some-correct %.2f" % (bo / n), "avg indep %.1f" % (kk / n))
