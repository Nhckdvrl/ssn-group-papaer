"""E17-0: extract programs and tests from the generations and build the execution matrix (CPU, local).

Programs : last ```python block after any </think>; correct = output equals the reference on every hidden test.
Tests    : last parseable ```json list after any </think>; items {"input": kwargs text, "output": literal}. Input must
           parse as literal keyword arguments with the problem's parameter names; the model's expected output is kept
           when it parses as a Python literal (else None: usable only with the reference output).
Panel    : the reference + up to 8 distinct correct programs (round-robin over models). A generated input is valid iff the
           reference returns normally on it and every panel member returns the same value.
Output   : one gzip jsonl line per problem with programs, tests, and every program's output on every distinct
           generated input (hidden-test results are reduced to the correct flag).
Usage: E17_VENDOR=<dir> python3 e17_execute.py --problems problems.jsonl --gen <dir> --models a,b,... --out matrix.jsonl.gz
"""
import argparse
import ast
import gzip
import inspect
import json
import os
import re
import sys
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(__file__))
from e17_common import parse_kwargs, run_prog, same  # noqa: E402

P = {}


def body(text):
    return text.split("</think>")[-1]


def extract_prog(text):
    m = re.findall(r"```python[ \t]*\n(.*?)```", body(text), re.DOTALL)
    return m[-1] if m else None


def param_names(starter, method):
    m = re.search(r"def\s+" + re.escape(method) + r"\s*\((.*?)\)\s*(->[^:]*)?:", starter, re.DOTALL)
    if not m:
        return None
    names = []
    for part in m.group(1).split(","):
        n = part.split(":")[0].split("=")[0].strip()
        if n and n != "self":
            names.append(n)
    return set(names)


def extract_tests(text, names):
    b = body(text)
    # pair fences left to right (any language tag), then try the json-like ones from the last
    blocks = [c for lang, c in re.findall(r"```([A-Za-z0-9_+-]*)[ \t]*\n(.*?)```", b, re.DOTALL) if lang in ("json", "")]
    for blk in reversed(blocks):
        try:
            v = json.loads(blk)
        except Exception:  # salvage one-object-per-line lists with a bad item (e.g. a Python expression)
            v = []
            for line in blk.splitlines():
                line = line.strip().rstrip(",")
                if line.startswith("{"):
                    try:
                        v.append(json.loads(line))
                    except Exception:
                        pass
            if not v:
                continue
        if not isinstance(v, list):
            continue
        out = []
        for t in v:
            if not isinstance(t, dict):
                continue
            if isinstance(t.get("input"), dict):  # models often write the kwargs as a JSON object
                kw = t["input"] or None
            elif isinstance(t.get("input"), str):
                kw = parse_kwargs(t["input"])
            else:
                continue
            if kw is None or (names is not None and set(kw) != names):
                continue
            o = t.get("output")
            if isinstance(o, str):
                try:
                    o = ast.literal_eval(o)
                except Exception:
                    pass  # an unquoted string answer: keep the text itself
            out.append((kw, repr(o) if o is not None else None))
        return out
    return []


def key(kw):
    return repr(sorted(kw.items()))


def job(args):
    pid, code = args
    p = P[pid]
    return run_prog(p["prefix"], code, p["method"], p["hidden"] + p["_gen_inputs"])


def init(pp):
    P.update(pp)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--problems", required=True); ap.add_argument("--gen", required=True)
    ap.add_argument("--models", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=20)
    a = ap.parse_args()
    models = a.models.split(",")
    probs = {json.loads(l)["id"]: json.loads(l) for l in open(a.problems)}
    progs = {pid: [] for pid in probs}
    tests = {pid: [] for pid in probs}
    stats = {}
    for m in models:
        st = stats.setdefault(m, {"solve": 0, "noprog": 0, "trunc_solve": 0, "test_gens": 0, "tests": 0,
                                  "trunc_tests": 0, "cond_gens": 0, "cond_tests": 0})
        for l in open(f"{a.gen}/solve_{m}.jsonl"):
            g = json.loads(l)
            if g["pid"] not in probs:
                continue
            st["solve"] += 1; st["trunc_solve"] += g["finish"] == "length"
            c = extract_prog(g["text"])
            if c is None:
                st["noprog"] += 1
            progs[g["pid"]].append(dict(model=m, sample=g["sample"], code=c, n_tokens=g["n_tokens"]))
        for kind in ("tests", "condtests"):
            fn = f"{a.gen}/{kind}_{m}.jsonl"
            if not os.path.exists(fn):
                continue
            for l in open(fn):
                g = json.loads(l)
                if g["pid"] not in probs:
                    continue
                p = probs[g["pid"]]
                ts = extract_tests(g["text"], param_names(p["starter"], p["method"]))
                if kind == "tests":
                    st["test_gens"] += 1; st["tests"] += len(ts); st["trunc_tests"] += g["finish"] == "length"
                else:
                    st["cond_gens"] += 1; st["cond_tests"] += len(ts)
                for i, (kw, o) in enumerate(ts):
                    tests[g["pid"]].append(dict(producer=m, kind=kind, sample=g["sample"], idx=i, key=key(kw),
                                                kw=kw, model_out=o, cond_prog=g.get("cond_prog")))
    # distinct generated inputs per problem
    for pid, p in probs.items():
        seen = {}
        for t in tests[pid]:
            seen.setdefault(t["key"], t["kw"])
        p["_keys"] = list(seen)
        p["_gen_inputs"] = [seen[k] for k in p["_keys"]]
    jobs = [(pid, x["code"]) for pid in probs for x in progs[pid] if x["code"] is not None]
    jobs += [(pid, probs[pid]["ref"]) for pid in probs]
    print("programs to run", len(jobs), "distinct generated inputs", sum(len(p["_keys"]) for p in probs.values()),
          flush=True)
    with Pool(a.workers, initializer=init, initargs=(probs,)) as pool:
        res = pool.map(job, jobs, chunksize=1)
    R = dict()
    for (pid, code), out in zip(jobs, res):
        R[(pid, code)] = out
    with gzip.open(a.out, "wt") as f:
        for pid, p in probs.items():
            nh = len(p["hidden"])
            ref_out = R[(pid, p["ref"])]
            # ref must reproduce its own hidden outputs (sanity)
            ref_ok = all(same(o, e) for o, e in zip(ref_out[:nh], p["hidden_out"]))
            prow = []
            for x in progs[pid]:
                if x["code"] is None:
                    prow.append(dict(model=x["model"], sample=x["sample"], correct=False, noprog=True, gen=None))
                    continue
                out = R[(pid, x["code"])]
                ok = all(same(o, e) for o, e in zip(out[:nh], p["hidden_out"]))
                prow.append(dict(model=x["model"], sample=x["sample"], correct=ok, noprog=False,
                                 hidden_pass=sum(same(o, e) for o, e in zip(out[:nh], p["hidden_out"])) / nh,
                                 gen=out[nh:]))
            # panel: reference + up to 8 distinct correct programs, round-robin over models
            by_m = {}
            for x, r in zip(progs[pid], prow):
                if r["correct"]:
                    by_m.setdefault(x["model"], []).append((x["code"], r["gen"]))
            panel, seen_code = [], set()
            while len(panel) < 8 and any(by_m.values()):
                for m in list(by_m):
                    if by_m[m] and len(panel) < 8:
                        c, g = by_m[m].pop(0)
                        if c not in seen_code:
                            seen_code.add(c); panel.append(g)
            ref_gen = ref_out[nh:]
            valid = [not ro.startswith("EXC:") and all(same(g[i], ro) for g in panel) for i, ro in enumerate(ref_gen)]
            kidx = {k: i for i, k in enumerate(p["_keys"])}
            trow = [dict(producer=t["producer"], kind=t["kind"], sample=t["sample"], idx=t["idx"], inp=kidx[t["key"]],
                         model_out=t["model_out"], cond_prog=t["cond_prog"]) for t in tests[pid]]
            f.write(json.dumps(dict(id=pid, difficulty=p["difficulty"], ref_ok=ref_ok, n_panel=len(panel),
                                    ref_gen=ref_gen, valid=valid, programs=prow, tests=trow)) + "\n")
    json.dump(stats, open(a.out + ".stats.json", "w"), indent=1)
    print(json.dumps(stats, indent=1))


if __name__ == "__main__":
    main()
