"""E16 stage 0 (CPU): score the generations of one model.

  solve     : last ```python block run on all tests -> pass_all; own-bug candidates = programs that run to
              completion on every test, pass all public tests, and give a wrong answer on some hidden test
  judge     : last 'VERDICT: CORRECT|INCORRECT' line vs label
  disc_*    : last ```input block; valid = every reference solution finishes and all agree on the output;
              success = valid and the target program's output differs from the references (or it errors / times out,
              reported separately); disc_cand on a correct candidate: 'accuse' = an input block was given
Usage: python3 e16_score.py --problems problems_100.jsonl --gen gen_<tag>.jsonl --out scored_<tag>.jsonl
                            [--emit_own own_<tag>.jsonl] [--workers 12]
"""
import argparse
import json
import os
import re
import sys
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(__file__))
from e16_exec import run, same  # noqa: E402

PROBS = {}


def last_block(text, lang):
    body = text.split("</think>")[-1]
    m = re.findall(r"```" + lang + r"[ \t]*\n(.*?)```", body, re.DOTALL)
    return m[-1] if m else None


PROGRAM_NODES = ("Assign", "AugAssign", "AnnAssign", "FunctionDef", "Call", "For", "While", "Import", "ImportFrom",
                 "If", "Return", "ClassDef")


def looks_like_program(block):
    import ast
    try:
        tree = ast.parse(block)
    except SyntaxError:
        return False
    return any(type(n).__name__ in PROGRAM_NODES for n in ast.walk(tree))


def last_input(text):
    """```input block if present; otherwise the last fenced block (any language tag) that is not a program.
    Pilot finding (2026-11-28): models often put the input in ```python or bare ``` fences."""
    body = text.split("</think>")[-1]
    m = re.findall(r"```input[ \t]*\n(.*?)```", body, re.DOTALL)
    if m:
        return m[-1]
    for blk in reversed(re.findall(r"```[A-Za-z]*[ \t]*\n(.*?)```", body, re.DOTALL)):
        if blk.strip() and not looks_like_program(blk):
            return blk
    return None


def verdict(text):
    m = re.findall(r"VERDICT:\s*\**\s*(CORRECT|INCORRECT)", text.split("</think>")[-1], re.IGNORECASE)
    return m[-1].upper() if m else None


def score(g):
    p = PROBS[g["pid"]]
    tl = float(p["time_limit"]) or 2.0
    r = {k: g[k] for k in ("task", "pid", "inst", "source", "sample") if k in g}
    r.update(label=g.get("label"), n_tokens=g["n_tokens"], finish=g["finish"])
    if g["task"] == "solve":
        code = last_block(g["text"], "python")
        r["parsed"] = code is not None
        if code is None:
            return r
        sts, oks = [], []
        for inp, exp in p["tests"]:
            st, so = run(code, inp, tl)
            sts.append(st); oks.append(st == "ok" and same(so, exp))
            if st in ("tle", "refused"):
                break
        r["pass_all"] = len(oks) == len(p["tests"]) and all(oks)
        np_ = p["n_public"]
        r["own_bug"] = (len(oks) == len(p["tests"]) and all(s == "ok" for s in sts) and all(oks[:np_])
                        and not all(oks))
        r["code"] = code if r["own_bug"] else None
        r["status_counts"] = {s: sts.count(s) for s in set(sts)}
        return r
    if g["task"] == "judge":
        v = verdict(g["text"])
        r["verdict"] = v
        r["right"] = v is not None and ((v == "CORRECT") == (g["label"] == "correct"))
        return r
    inp = last_input(g["text"])
    r["gave_input"] = inp is not None
    r["said_correct"] = verdict(g["text"]) == "CORRECT"
    if inp is None:
        return r
    outs = [run(ref, inp, tl) for ref in p["refs"]]
    r["valid"] = all(s == "ok" for s, _ in outs) and all(same(o, outs[0][1]) for _, o in outs[1:])
    if not r["valid"]:
        return r
    st, so = run(g["code"], inp, tl)
    r["target_status"] = st
    r["success"] = (st != "ok") or not same(so, outs[0][1])
    r["success_by_wrong_output"] = st == "ok" and not same(so, outs[0][1])
    return r


def _init(path):
    for l in open(path):
        p = json.loads(l); PROBS[p["id"]] = p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--problems", required=True); ap.add_argument("--gen", required=True)
    ap.add_argument("--out", required=True); ap.add_argument("--emit_own", default=None)
    ap.add_argument("--workers", type=int, default=12)
    a = ap.parse_args()
    gens = [json.loads(l) for l in open(a.gen)]
    with Pool(a.workers, initializer=_init, initargs=(a.problems,)) as pool:
        res = pool.map(score, gens, chunksize=4)
    with open(a.out, "w") as f:
        for r in res:
            f.write(json.dumps(r) + "\n")
    if a.emit_own:
        seen, by = set(), {}
        for r in res:
            if r["task"] == "solve" and r.get("own_bug") and r["code"] not in seen and len(by.get(r["pid"], [])) < 2:
                seen.add(r["code"]); by.setdefault(r["pid"], []).append(r["code"])
        with open(a.emit_own, "w") as f:
            for pid, codes in by.items():
                for c in codes:
                    f.write(json.dumps({"pid": pid, "code": c}) + "\n")
        print("own bugs:", sum(len(v) for v in by.values()), "problems", len(by))
    summ = {}
    for r in res:
        k = (r["task"], r["source"], r.get("label"))
        s = summ.setdefault(k, {"n": 0})
        s["n"] += 1
        for f_ in ("parsed", "pass_all", "own_bug", "right", "gave_input", "said_correct", "valid", "success"):
            if f_ in r:
                s[f_] = s.get(f_, 0) + bool(r[f_])
    for k in sorted(summ, key=str):
        s = summ[k]; n = s.pop("n")
        print(k, n, {f_: round(v / n, 3) for f_, v in s.items()})


if __name__ == "__main__":
    main()
