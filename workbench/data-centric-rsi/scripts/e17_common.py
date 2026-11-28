"""E17: LeetCode-style (class Solution) execution and comparison.

parse_kwargs("n = 5, q = [[1,2]]") -> {"n": 5, "q": [[1, 2]]}  (literal keyword arguments only; None otherwise)
run_prog(prefix, program, method, inputs): one sandboxed subprocess (e16_exec screen + limits) that defines the program
  after the dataset's import/helper prefix and, for each kwargs dict, calls Solution().<method>(**deepcopy(kwargs)) under
  a 1 s interval timer; prints repr(result) or 'EXC:<type>'. Long input lists are split into chunks of 60 calls.
  Returns a list of strings (EXC:Fail for every call of a chunk whose process died or was refused).
same(a, b): literal-eval both reprs; structural equality, floats with 1e-6 abs/rel tolerance (as e16f_common).
"""
import ast
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from e16f_common import run_unscreened, same_result  # noqa: E402
from e16_exec import screen  # noqa: E402

HARNESS = r'''
import copy, json, signal
def _alarm(s, f):
    raise TimeoutError()
signal.signal(signal.SIGALRM, _alarm)
_out = []
for _kw in _INPUTS:
    signal.setitimer(signal.ITIMER_REAL, 1.0)
    try:
        _r = Solution().{method}(**copy.deepcopy(_kw))
        signal.setitimer(signal.ITIMER_REAL, 0)
        _s = repr(_r)
        _out.append(_s if len(_s) < 3000 else "EXC:Huge")
    except BaseException as _e:
        signal.setitimer(signal.ITIMER_REAL, 0)
        _out.append("EXC:" + type(_e).__name__)
print("@@OUT@@" + json.dumps(_out))
'''
CHUNK = 60


def parse_kwargs(s):
    try:
        c = ast.parse(f"f({s})", mode="eval").body
    except SyntaxError:
        return None
    if not isinstance(c, ast.Call) or c.args or not c.keywords or any(k.arg is None for k in c.keywords):
        return None
    try:
        return {k.arg: ast.literal_eval(k.value) for k in c.keywords}
    except Exception:
        return None


VENDOR = os.environ.get("E17_VENDOR", "")


def _run_chunk(prefix, program, method, inputs):
    src = (f"import sys\nsys.path.insert(0, {VENDOR!r})\n" if VENDOR else "") + prefix + "\n" + program + "\n_INPUTS = " + repr(inputs) + "\n" + HARNESS.replace("{method}", method)
    st, so = run_unscreened(src, 4.0 + 1.2 * len(inputs))
    if st != "ok" and "@@OUT@@" not in so:
        return None
    line = [l for l in so.splitlines() if l.startswith("@@OUT@@")]
    if not line:
        return None
    try:
        out = json.loads(line[-1][7:])
    except Exception:
        return None
    return out if len(out) == len(inputs) else None


def run_prog(prefix, program, method, inputs):
    if screen(program):
        return ["EXC:Refused"] * len(inputs)
    out = []
    for i in range(0, len(inputs), CHUNK):
        ch = inputs[i:i + CHUNK]
        r = _run_chunk(prefix, program, method, ch)
        out += r if r is not None else ["EXC:Fail"] * len(ch)
    return out


def same(a, b):
    return same_result(a, b, 1e-6)
