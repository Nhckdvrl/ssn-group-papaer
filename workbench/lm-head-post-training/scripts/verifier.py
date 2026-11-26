"""Minimal MATH answer verifier: last \\boxed{...} + string normalisation (Hendrycks-style) + numeric fallback.
Deliberately simple and deterministic; parse failures are reported, never silently scored."""
import re


def extract_boxed(s):
    i = max(s.rfind("\\boxed"), s.rfind("\\fbox"))
    if i < 0:
        return None
    j = s.find("{", i)
    if j < 0:
        return None
    depth = 0
    for k in range(j, len(s)):
        depth += {"{": 1, "}": -1}.get(s[k], 0)
        if depth == 0:
            return s[j + 1:k]
    return None


def _fix_fracs(s):
    return re.sub(r"\\frac(\d)(\d)", r"\\frac{\1}{\2}", s)


def normalize(s):
    s = s.strip()
    s = re.sub(r"\\text\{\s*([^}]*)\}", r"\1", s)
    for a, b in [("\\left", ""), ("\\right", ""), ("\\!", ""), ("\\,", ""), ("\\;", ""), ("\\ ", ""),
                 ("dfrac", "frac"), ("tfrac", "frac"), ("^\\circ", ""), ("^{\\circ}", ""), ("\\$", ""), ("$", ""),
                 ("\\%", ""), ("%", ""), (" ", "")]:
        s = s.replace(a, b)
    s = re.sub(r"(degrees|degree|units|unit|cm|inches|inch)$", "", s)
    s = s.rstrip(".")
    if s.startswith("0.") is False and s.startswith("."):
        s = "0" + s
    s = _fix_fracs(s)
    s = re.sub(r"^[a-zA-Z]\s*=", "", s)
    if s == "0.5":
        s = "\\frac{1}{2}"
    return s


def _num(s):
    s = s.replace(",", "")
    m = re.fullmatch(r"-?\d+(\.\d+)?", s)
    if m:
        return float(s)
    m = re.fullmatch(r"(-?)\\frac\{(-?\d+)\}\{(\d+)\}", s)
    if m and int(m.group(3)) != 0:
        return (-1 if m.group(1) else 1) * int(m.group(2)) / int(m.group(3))
    return None


def is_equiv(pred, ref):
    a, b = normalize(pred), normalize(ref)
    if a == b:
        return True
    x, y = _num(a), _num(b)
    return x is not None and y is not None and abs(x - y) < 1e-6 * max(1.0, abs(y))
