"""Objective choice scoring. Accuracy is deliberately not renamed hit/FPR."""
import math
import re
from collections import defaultdict


def parse_choice(text, choices):
    # The parent allows explanations: use a leading choice, otherwise require
    # one unique explicitly marked choice. Conflicting choices stay invalid.
    s = text.strip().replace("**", "")
    s = re.sub(r"\\(?:text|mathrm|mathbf)\{([A-E])\}", r"\1", s)
    boxed = re.findall(r"\\boxed\{([A-E])\}", s)
    if boxed:
        return boxed[-1] if boxed[-1] in choices else None
    lead = re.match(r"^(?:[Aa]nswer\s*[:：]\s*)?\(?([A-E])\)?(?:[.)\s:]|$)", s)
    if lead and lead.group(1) in choices and not re.match(r"\s*(?:or|/)\s*\(?[A-E]", s[lead.end():]):
        return lead.group(1)
    conclusions = re.findall(
        r"(?:answer\s*(?:is|would be|:)|(?:most appropriate|best|correct|therefore|thus|in conclusion)[^\n]{0,180}(?:is|:)|"
        r"(?:答案|选项|回答|정답|Antwort)[^\n]{0,100}[:：은是]?)[\s*]*(?:[Oo]ption\s*)?\(?([A-E])\)?(?=[.)\s:]|$)",
        s, re.IGNORECASE,
    )
    if conclusions:
        answer = conclusions[-1].upper()
        return answer if answer in choices else None
    localized = re.findall(
        r"(?:wähle ich|wählen wir|passendste (?:Antwort|Bedeutung)[^\n]{0,120}(?:ist|:)|"
        r"가장\s*적절한\s*의미는|정답은|정답\s*[:：]|따라서[^\n]{0,100}의미는|"
        r"closest fitting option[^\n]{0,120}(?:be|:))\s*(?:[Oo]ption\s*)?\(?([A-E])\)?",
        s,
    )
    if localized:
        return localized[-1] if localized[-1] in choices else None
    marked = set(re.findall(r"\(([A-E])\)|\b(?:[Aa]nswer|[Oo]ption)\s*[:：]?\s*([A-E])\b", s))
    vals = {a or b for a, b in marked} & set(choices)
    return next(iter(vals)) if len(vals) == 1 else None


def wilson(k, n):
    if not n:
        return [None, None]
    z = 1.959963984540054
    p = k / n
    d = 1 + z*z/n
    center = (p + z*z/(2*n))/d
    half = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n))/d
    return [max(0., center-half), min(1., center+half)]


def summarize(rows):
    groups = defaultdict(list)
    for r in rows:
        for key in ["all", f"language:{r['language']}", f"{r['language']}:{r['phenomenon']}"]:
            groups[key].append(r)
    return {k: {"n": len(rs), "correct": sum(r["prediction"] == r["gold"] for r in rs),
                "accuracy": sum(r["prediction"] == r["gold"] for r in rs)/len(rs),
                "accuracy_ci95": wilson(sum(r["prediction"] == r["gold"] for r in rs), len(rs)),
                "invalid": sum(r["prediction"] is None for r in rs),
                "truncated": sum(r.get("truncated", False) for r in rs)} for k, rs in groups.items()}
