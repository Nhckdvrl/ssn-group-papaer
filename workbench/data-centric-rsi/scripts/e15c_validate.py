"""E15c (CPU): validate AZR proposals and compute behaviour fingerprints.

Validity follows AZR (answer_conditional extraction; code/input regex parse with reject_multiple_functions and
f-renaming copied from rewards/code_reward.py; AZR banned-import check; deterministic execution twice).
Extra safety screen for running model-written code on shared nodes (counted separately as sandbox_reject):
imports of os/sys/shutil/socket/... or calls to open/exec/eval/compile/__import__ are not executed.
Each program runs in a fresh subprocess, empty temp dir, 5 s CPU, 2 GB address space.

Fingerprint: the input is parsed as a Python literal; a type signature is derived; 8 canonical probe inputs per
signature (fixed generator) are run; fingerprint = hash(signature, outputs). Programs whose input is not a
plain literal get no behaviour fingerprint (only a normalised-AST hash). Novelty is reported against the
references shown in the prompt and against the whole materials file.

Usage: python e15c_validate.py --props a.jsonl [b.jsonl ...] --materials seed.jsonl --out <jsonl> [--workers 32]
       python e15c_validate.py --materials_only <proposals validated jsonl> --to_materials <out jsonl>
"""
import argparse
import ast
import hashlib
import importlib.util
import json
import os
import random
import re
import resource
import subprocess
import sys
import tempfile
from multiprocessing import Pool

AZR = "/home/xiang/.cache/research/data-centric-rsi/AZR/absolute_zero_reasoner"
BANNED = ["logging", "random", "multiprocessing", "pebble", "subprocess", "threading", "datetime", "time", "hashlib",
          "hmac", "bcrypt", "os.sys", "os.path", "sys.exit", "os.environ", "calendar", "datetime"]
UNSAFE_MODS = {"os", "sys", "shutil", "socket", "pathlib", "subprocess", "ctypes", "requests", "urllib", "http", "glob",
               "tempfile", "signal", "resource", "importlib", "pickle", "builtins", "io", "multiprocessing", "threading",
               "asyncio", "ftplib", "smtplib", "webbrowser", "gc", "inspect", "code", "pty", "fcntl", "mmap"}
UNSAFE_CALLS = {"open", "exec", "eval", "compile", "__import__", "globals", "locals", "input", "breakpoint", "exit",
                "quit", "getattr", "setattr", "delattr", "vars", "memoryview"}
spec = importlib.util.spec_from_file_location("azr_checks", f"{AZR}/utils/code_utils/checks.py")
checks = importlib.util.module_from_spec(spec); spec.loader.exec_module(checks)


def extract_answer(text):
    return text.split("<answer>")[-1].split("</answer>")[0].strip() if "<answer>" in text else ""


def parse_code_input(s):
    """Copy of AZR parse_code_input_output(parse_output=False, reject_multiple_functions=True, f_replace_location='not_first')."""
    flags = re.DOTALL | re.IGNORECASE
    cm = re.search(r"```(?:python\s*)?\n?(.*?)\n?```", s, flags)
    im = re.search(r"```input\s*\n?(.*?)\n?```", s, flags) or re.search(r"# Input:\s*(.*?)(?=\n```|$)", s, flags)
    if not cm or not im:
        return None
    code, inp = cm.group(1).strip(), im.group(1).strip()
    defs = re.findall(r"^\s*def\s+(\w+)\s*\(", code, re.MULTILINE)
    if not defs or len(defs) > 1:
        return None
    if defs[0] != "f":
        code = re.sub(rf"def\s+{re.escape(defs[0])}\s*\(", "def f(", code)
        code = re.sub(rf"\b{re.escape(defs[0])}\s*\(", "f(", code)
    return code, inp


def unsafe(code):
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return True
    for n in ast.walk(tree):
        if isinstance(n, ast.Import) and any(a.name.split(".")[0] in UNSAFE_MODS for a in n.names):
            return True
        if isinstance(n, ast.ImportFrom) and (n.module or "").split(".")[0] in UNSAFE_MODS:
            return True
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in UNSAFE_CALLS:
            return True
        if isinstance(n, ast.Attribute) and n.attr.startswith("__") and n.attr not in ("__init__", "__name__", "__len__"):
            return True
    return False


def _limits():
    resource.setrlimit(resource.RLIMIT_CPU, (5, 5))
    resource.setrlimit(resource.RLIMIT_AS, (2 << 30, 2 << 30))
    os.setsid()


def run_py(src, timeout=8):
    with tempfile.TemporaryDirectory() as d:
        try:
            p = subprocess.run([sys.executable, "-I", "-c", src], cwd=d, capture_output=True, text=True,
                               timeout=timeout, preexec_fn=_limits, env={"PATH": "/usr/bin:/bin"})
        except subprocess.TimeoutExpired:
            return None
        return p.stdout if p.returncode == 0 else None


def sig_of(v):
    if isinstance(v, bool): return "bool"
    if isinstance(v, int): return "int"
    if isinstance(v, float): return "float"
    if isinstance(v, str): return "str"
    if isinstance(v, list): return "list[" + (sig_of(v[0]) if v else "int") + "]"
    if isinstance(v, tuple): return "tuple(" + ",".join(sig_of(x) for x in v) + ")"
    if isinstance(v, dict): return "dict[" + (sig_of(next(iter(v))) + ":" + sig_of(next(iter(v.values()))) if v else "str:int") + "]"
    if isinstance(v, set): return "set[" + (sig_of(next(iter(v))) if v else "int") + "]"
    if v is None: return "none"
    return "other"


def gen(sig, r):
    if sig == "bool": return r.choice([True, False])
    if sig == "int": return r.choice([0, 1, -1, 2, 3, 5, 7, 10, 12, 17, 42, -8, 100])
    if sig == "float": return r.choice([0.0, 0.5, -1.5, 2.25, 3.0, 10.1])
    if sig == "str": return r.choice(["", "a", "ab", "abc", "Hello", "hello world", "AbC123", "racecar", "a,b;c", "xyzzy"])
    if sig == "none": return None
    m = re.fullmatch(r"(list|set)\[(.*)\]", sig)
    if m:
        xs = [gen(m.group(2), r) for _ in range(r.choice([0, 1, 3, 5]))]
        return set(map(str, xs)) if m.group(1) == "set" and m.group(2) not in ("int", "str", "float", "bool") else (set(xs) if m.group(1) == "set" else xs)
    m = re.fullmatch(r"dict\[(.*?):(.*)\]", sig)
    if m:
        return {gen(m.group(1), r): gen(m.group(2), r) for _ in range(r.choice([0, 1, 2, 4]))}
    m = re.fullmatch(r"tuple\((.*)\)", sig)
    if m:
        parts, depth, cur = [], 0, ""
        for ch in m.group(1):
            if ch == "," and depth == 0: parts.append(cur); cur = ""; continue
            depth += ch in "[(" ; depth -= ch in "])"; cur += ch
        if cur: parts.append(cur)
        return tuple(gen(p, r) for p in parts)
    raise ValueError(sig)


def probes(sig_args):
    r = random.Random("|".join(sig_args))
    return [tuple(gen(s, r) for s in sig_args) for _ in range(8)]


def norm_ast(code):
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return None
    names = {}
    for n in ast.walk(tree):
        if isinstance(n, ast.Name): n.id = names.setdefault(n.id, f"v{len(names)}")
        elif isinstance(n, ast.arg): n.arg = names.setdefault(n.arg, f"v{len(names)}")
        elif isinstance(n, ast.FunctionDef): n.name = names.setdefault(n.name, f"v{len(names)}")
    return hashlib.sha1(ast.dump(tree, annotate_fields=False).encode()).hexdigest()[:16]


def analyse(code, inp):
    out = {"ast_hash": norm_ast(code), "ast_nodes": None, "fp": None, "sig": None}
    try:
        out["ast_nodes"] = sum(1 for _ in ast.walk(ast.parse(code)))
    except SyntaxError:
        pass
    try:
        args = ast.literal_eval(f"({inp},)")
    except Exception:
        return out
    sig = [sig_of(x) for x in args]
    if "other" in sig:
        return out
    try:
        pr = probes(sig)
    except Exception:
        return out
    src = code + "\nimport json\nres=[]\nfor a in " + repr(pr) + ":\n    try:\n        res.append(repr(f(*a))[:300])\n    except Exception as e:\n        res.append('ERR:'+type(e).__name__)\nprint(json.dumps(res))"
    so = run_py(src)
    if so is None:
        return out
    out["sig"] = ",".join(sig)
    out["fp"] = hashlib.sha1((out["sig"] + "|" + so).encode()).hexdigest()[:16]
    return out


def validate(row):
    res = {k: row[k] for k in ("tag", "task", "temp", "seed", "idx", "refs", "n_tokens", "finish") if k in row}
    res.update(parsed=False, sandbox_reject=False, azr_banned=False, valid=False)
    parsed = parse_code_input(extract_answer(row["text"]))
    if not parsed:
        return res
    code, inp = parsed
    res.update(parsed=True, code=code, input=inp, code_chars=len(code))
    if unsafe(code):
        res["sandbox_reject"] = True; return res
    if checks.contains_banned_imports(code=code, banned_keywords=BANNED):
        res["azr_banned"] = True; return res
    src = code + f"\nreturns = f({inp})\nif returns != f({inp}):\n    raise Exception('Non-deterministic code')\nprint(repr(returns))"
    so = run_py(src)
    if so is None:
        return res
    res.update(valid=True, output=so.strip()[:2000])
    res.update(analyse(code, inp))
    return res


def material_keys(path, workers):
    mats = [json.loads(l) for l in open(path)]
    with Pool(workers) as p:
        an = p.starmap(analyse, [(m["snippet"], m["input"]) for m in mats])
    return an


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--props", nargs="*", default=[]); ap.add_argument("--materials")
    ap.add_argument("--out"); ap.add_argument("--workers", type=int, default=32)
    ap.add_argument("--materials_only"); ap.add_argument("--to_materials")
    a = ap.parse_args()
    if a.materials_only:  # turn validated proposals into an AZR-format materials file
        with open(a.to_materials, "w") as f:
            for l in open(a.materials_only):
                r = json.loads(l)
                if r.get("valid"):
                    f.write(json.dumps({"snippet": r["code"], "input": r["input"], "output": r["output"], "imports": [],
                                        "original_snippet": r["code"], "composite_functions": []}) + "\n")
        return
    mk = material_keys(a.materials, a.workers)
    mat_fp = {x["fp"] for x in mk if x["fp"]}; mat_ast = {x["ast_hash"] for x in mk if x["ast_hash"]}
    rows = [json.loads(l) for p in a.props for l in open(p)]
    with Pool(a.workers) as p:
        res = p.map(validate, rows, chunksize=16)
    with open(a.out, "w") as f:
        for r in res:
            if r.get("valid"):
                rf = [mk[i] for i in r.get("refs", [])]
                r["copy_of_ref_ast"] = r.get("ast_hash") in {x["ast_hash"] for x in rf}
                r["same_fp_as_ref"] = r.get("fp") is not None and r["fp"] in {x["fp"] for x in rf}
                r["new_ast_vs_materials"] = r.get("ast_hash") not in mat_ast
                r["new_fp_vs_materials"] = None if r.get("fp") is None else r["fp"] not in mat_fp
            f.write(json.dumps(r) + "\n")
    print("done", len(res), "valid", sum(r["valid"] for r in res), flush=True)


if __name__ == "__main__":
    main()
