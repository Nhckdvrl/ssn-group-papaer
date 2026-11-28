"""E16 stage 0, function-level (HumanEval+): sandboxed calls and result comparison.

run_calls(code, entry, args_list): one sandboxed subprocess (see e16_exec.run) that defines the program and calls
entry(*copy.deepcopy(args)) for each argument tuple, printing repr(result) or 'EXC:<type>' per call. A per-call
alarm of 2 s marks 'EXC:Timeout'. Returns a list of strings, or None if the whole process failed or was refused.
same_result(a, b, atol): literal-eval both reprs; floats compared with abs/rel tolerance max(atol, 1e-6).
"""
import ast
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from e16_exec import run  # noqa: E402

HARNESS = r'''
import copy, json, signal
def _alarm(s, f):
    raise TimeoutError()
signal.signal(signal.SIGALRM, _alarm)
_out = []
for _a in _ARGS:
    signal.alarm(2)
    try:
        _out.append(repr({entry}(*copy.deepcopy(_a))))
    except BaseException as _e:
        _out.append("EXC:" + type(_e).__name__)
    finally:
        signal.alarm(0)
print(json.dumps(_out))
'''


def run_calls(code, entry, args_list, total_time=None):
    src = code + "\n_ARGS = " + repr(list(args_list)) + "\n" + HARNESS.replace("{entry}", entry)
    # the harness itself imports signal; e16_exec's screen forbids it in model code, so screen the code alone first
    from e16_exec import screen
    if screen(code):
        return None
    st, so = run_unscreened(src, total_time or (2.0 + 0.5 * len(args_list)))
    if st != "ok":
        return None
    try:
        out = json.loads(so.strip().splitlines()[-1])
    except Exception:
        return None
    return out if len(out) == len(args_list) else None


def run_unscreened(src, time_limit):
    import e16_exec
    orig = e16_exec.screen
    e16_exec.screen = lambda c: None
    try:
        return e16_exec.run(src, "", time_limit / 2)
    finally:
        e16_exec.screen = orig


def _lit(s):
    try:
        return True, ast.literal_eval(s)
    except Exception:
        return False, s


def _eq(x, y, tol):
    if isinstance(x, float) or isinstance(y, float):
        if isinstance(x, (int, float)) and isinstance(y, (int, float)) and not isinstance(x, bool) and not isinstance(y, bool):
            if math.isnan(x) and math.isnan(y):
                return True
            return math.isclose(x, y, rel_tol=tol, abs_tol=tol)
        return False
    if isinstance(x, (list, tuple)) and isinstance(y, (list, tuple)):
        return type(x) == type(y) and len(x) == len(y) and all(_eq(a, b, tol) for a, b in zip(x, y))
    if isinstance(x, dict) and isinstance(y, dict):
        return x.keys() == y.keys() and all(_eq(x[k], y[k], tol) for k in x)
    return x == y and type(x) == type(y)


def same_result(a, b, atol=0.0):
    if a == b:
        return True
    if a.startswith("EXC:") or b.startswith("EXC:"):
        return False
    oa, va = _lit(a)
    ob, vb = _lit(b)
    if not (oa and ob):
        return False
    return _eq(va, vb, max(float(atol or 0), 1e-6))


def parse_call(text, entry):
    """'f(1, [2])' -> [1, [2]] (literal arguments only); None if not a single literal call to entry."""
    try:
        tree = ast.parse(text.strip(), mode="eval")
    except SyntaxError:
        return None
    c = tree.body
    if not (isinstance(c, ast.Call) and isinstance(c.func, ast.Name) and c.func.id == entry and not c.keywords):
        return None
    try:
        return [ast.literal_eval(a) for a in c.args]
    except Exception:
        return None
