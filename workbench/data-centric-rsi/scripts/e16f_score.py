"""E16 stage 0, function-level: score one model's generations on HumanEval+ problems.

solve    : last ```python block; the prompt's import lines are prepended; pass_all over all tests.
           bug candidates (--emit_bugs): programs that raise nothing, match the reference on every base input and
           return a wrong value on some plus input ("plausible" bugs); up to 2 distinct per problem.
judge    : last \\boxed{CORRECT|INCORRECT} (or VERDICT line) vs label.
disc_*   : the input is taken from a ```json block [{"input": "f(...)"}], else from a fenced block that is a single
           call to the entry point, else from the last "f(...)" line after the reasoning; route recorded.
           valid   = literal call and the contract reference raises nothing on it
           success = valid and the target's result differs from the reference (1e-6 tolerance) or the target raises
Readouts are reported in two layers: valid_rate and success_given_valid.
Usage: python3 e16f_score.py --problems problems_f.jsonl --gen <gen.jsonl> --out <scored.jsonl> [--emit_bugs <jsonl>]
"""
import argparse
import json
import os
import re
import sys
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(__file__))
from e16f_common import parse_call, run_calls, same_result  # noqa: E402
from e16_score import verdict  # noqa: E402

P = {}


def imports_of(prompt):
    return "\n".join(l for l in prompt.splitlines() if l.startswith(("import ", "from "))) + "\n"


def extract_call(text, entry):
    body = text.split("</think>")[-1]
    for blk in reversed(re.findall(r"```json[ \t]*\n(.*?)```", body, re.DOTALL)):
        try:
            v = json.loads(blk)
        except Exception:
            continue
        v = v[0] if isinstance(v, list) and v else v
        if isinstance(v, dict) and isinstance(v.get("input"), str):
            return v["input"], "json"
    for blk in reversed(re.findall(r"```[A-Za-z]*[ \t]*\n(.*?)```", body, re.DOTALL)):
        if parse_call(blk, entry) is not None:
            return blk.strip(), "fence"
    for line in reversed(body.splitlines()):
        m = re.search(re.escape(entry) + r"\(.*\)", line)
        if m and parse_call(m.group(0), entry) is not None:
            return m.group(0), "line"
    return None, None


def score(g):
    p = P[g["pid"]]
    r = {k: g[k] for k in ("task", "pid", "inst", "source", "sample") if k in g}
    r.update(label=g.get("label"), n_tokens=g["n_tokens"], finish=g["finish"])
    if g["task"] == "solve":
        m = re.findall(r"```python[ \t]*\n(.*?)```", g["text"].split("</think>")[-1], re.DOTALL)
        r["parsed"] = bool(m)
        if not m:
            return r
        code = imports_of(p["prompt"]) + m[-1]
        args = [a for a, _ in p["tests"]]
        out = run_calls(code, p["entry"], args)
        if out is None:
            r["pass_all"] = False
            return r
        ok = [same_result(o, e, p["atol"]) for o, (_, e) in zip(out, p["tests"])]
        nb = p["n_base"]
        r["pass_all"] = all(ok)
        r["bug"] = (not any(o.startswith("EXC:") for o in out)) and all(ok[:nb]) and not all(ok)
        r["code"] = code if r["bug"] else None
        return r
    if g["task"] == "judge":
        v = verdict(g["text"])
        r["verdict"] = v
        r["right"] = v is not None and ((v == "CORRECT") == (g["label"] == "correct"))
        return r
    r["said_correct"] = verdict(g["text"]) == "CORRECT"
    call, route = extract_call(g["text"], p["entry"])
    r["route"] = route
    r["gave_input"] = call is not None
    if call is None:
        return r
    args = parse_call(call, p["entry"])
    if args is None:
        r["valid"] = False
        return r
    chk = run_calls(p["ref_contract"], p["entry"], [args])
    r["valid"] = chk is not None and not chk[0].startswith("EXC:")
    if not r["valid"]:
        return r
    ref = run_calls(p["ref_plain"], p["entry"], [args])
    tgt = run_calls(imports_of(p["prompt"]) + g["code"], p["entry"], [args])
    if ref is None or ref[0].startswith("EXC:"):
        r["valid"] = False
        return r
    r["success"] = tgt is None or tgt[0].startswith("EXC:") or not same_result(tgt[0], ref[0], p["atol"])
    return r


def init(path):
    for l in open(path):
        p = json.loads(l); P[p["id"]] = p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--problems", required=True); ap.add_argument("--gen", required=True)
    ap.add_argument("--out", required=True); ap.add_argument("--emit_bugs", default=None)
    ap.add_argument("--workers", type=int, default=12)
    a = ap.parse_args()
    gens = [json.loads(l) for l in open(a.gen)]
    with Pool(a.workers, initializer=init, initargs=(a.problems,)) as pool:
        res = pool.map(score, gens, chunksize=4)
    with open(a.out, "w") as f:
        for r in res:
            f.write(json.dumps(r) + "\n")
    if a.emit_bugs:
        seen, by = set(), {}
        for r in res:
            if r["task"] == "solve" and r.get("bug") and r["code"] not in seen and len(by.get(r["pid"], [])) < 2:
                seen.add(r["code"]); by.setdefault(r["pid"], []).append(r["code"])
        with open(a.emit_bugs, "w") as f:
            for pid, cs in by.items():
                for c in cs:
                    f.write(json.dumps({"pid": pid, "code": c}) + "\n")
        print("bugs", sum(len(v) for v in by.values()), "problems", len(by))
    summ = {}
    for r in res:
        k = (r["task"], r["source"], r.get("label"))
        s = summ.setdefault(k, {"n": 0, "parsed": 0, "pass_all": 0, "right": 0, "gave_input": 0, "valid": 0,
                                "success": 0, "said_correct": 0})
        s["n"] += 1
        for f_ in ("parsed", "pass_all", "right", "gave_input", "valid", "success", "said_correct"):
            s[f_] += bool(r.get(f_))
    for k in sorted(summ, key=str):
        s = summ[k]; n = s["n"]
        if k[0] == "solve":
            print(k, n, "parsed %.2f pass_all %.3f" % (s["parsed"] / n, s["pass_all"] / n))
        elif k[0] == "judge":
            print(k, n, "right %.3f" % (s["right"] / n))
        else:
            print(k, n, "gave %.2f valid %.2f success %.3f success|valid %s said_correct %.2f" % (
                s["gave_input"] / n, s["valid"] / n, s["success"] / n,
                ("%.3f" % (s["success"] / s["valid"])) if s["valid"] else "-", s["said_correct"] / n))


if __name__ == "__main__":
    main()
