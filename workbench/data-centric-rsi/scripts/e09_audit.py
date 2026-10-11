"""Immutable-output audit of E09; diagnostic object parsing does not change its gate."""

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

import sympy as sp
from dataenvgym.gym.domain_models import MathDataSpec


MATH_REVIEW = {
    "no_state:0": ("correct", "Enumerate multiples of 100: first digit sum 10 is 1900."),
    "with_state:0": ("correct", "y=3^x has roots 1 and 9, hence x=0 and 2."),
    "no_state:1": ("correct", "3*2^x=192 implies x=6."),
    "with_state:1": ("correct", "3*2^x=24 implies x=3."),
    "no_state:2": ("correct", "5+3*sum(1..9)=140."),
    "with_state:2": ("correct", "Prime exponent parities are 2:even, 3/5/7:odd; multiplier 105."),
    "no_state:3": ("math_correct_unparseable", "Sine rule gives BC=8*sin(30)/sin(45)=4*sqrt(2); raw JSON contains illegal \\circ escapes."),
    "no_state:4": ("correct", "Quadratic interpolation f(1..3) gives f(4)=15."),
    "with_state:4": ("correct", "Denominator roots are 1/8 and 8."),
    "no_state:5": ("wrong_final", "Solution is {0} union [1,7], not [0,7]; x=1/2 is a counterexample."),
    "with_state:5": ("correct", "Exhaustive three-digit multiples of seven: first digit sum 20 is 497."),
    "no_state:6": ("wrong_final", "n=51 is divisible by 3 and 51^2-1=2600; exhaustive minimum is 51, not 99."),
    "with_state:6": ("correct", "LCM=60; least positive 60k congruent 2 modulo 7 is 240."),
    "no_state:8": ("wrong_reasoning", "Final minimum -45/11 is right, but stated Hessian determinant 11 is false; actual det([[6,4],[4,10]])=44."),
    "with_state:8": ("correct", "sqrt(3^2+4^2+5^2)=5*sqrt(2)."),
    "no_state:9": ("correct", "Triangle area 3x/2 is one-third of rectangle area 12, giving x=8/3."),
    "with_state:9": ("correct", "x^2+xy+y^2=3 and x^2-2xy+y^2=1 imply xy=2/3 and x^2+y^2=7/3."),
}


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def digest(text: str) -> str:
    return hashlib.sha256(" ".join(text.split()).encode()).hexdigest()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def diagnostic_final(raw: str) -> dict:
    if "<think>" in raw and "</think>" not in raw:
        raise ValueError("unclosed thinking block")
    content = raw.rsplit("</think>", 1)[-1].strip()
    if content.startswith("```json\n") and content.endswith("\n```"):
        content = content[len("```json\n"):-len("\n```")].strip()
    parsed = json.loads(content)
    if isinstance(parsed, list):
        if len(parsed) != 1:
            raise ValueError("diagnostic array must contain one spec")
        parsed = parsed[0]
    if not isinstance(parsed, dict):
        raise ValueError("diagnostic final must be object or singleton array")
    return parsed


def independent_checks() -> dict:
    x, y = sp.symbols("x y", real=True)
    quadratic = 3*x*x + 4*x*y + 5*y*y - 6*x - 8*y
    optimum = sp.solve([sp.diff(quadratic, x), sp.diff(quadratic, y)], [x, y])
    return {
        "no_state:0": next(n for n in range(100, 10000, 100) if sum(map(int, str(n))) == 10),
        "no_state:2": 5 + sum(3*i for i in range(1, 10)),
        "with_state:2": int(sp.prod(p for p, exponent in sp.factorint(sp.prod(k**k for k in range(2, 10))).items() if exponent % 2)),
        "no_state:4": int(sp.interpolate([(1, 3), (2, 5), (3, 9)], x).subs(x, 4)),
        "with_state:4": [str(z) for z in sp.solve(8*x*x - 65*x + 8, x)],
        "no_state:5": str(sp.solve_univariate_inequality(sp.Abs(x*x-4*x) <= 3*x, x, relational=False)),
        "with_state:5": next(n for n in range(100, 1000) if n % 7 == 0 and sum(map(int, str(n))) == 20),
        "no_state:6": next(n for n in range(1, 1000) if n % 3 == 0 and (n*n-1) % 100 == 0),
        "with_state:6": next(n for n in range(1, 1000) if n % 60 == 0 and n % 7 == 2),
        "no_state:8": {"min": str(quadratic.subs(optimum)), "hessian_determinant": str(sp.det(sp.hessian(quadratic, [x, y])))},
        "with_state:8": str(sp.sqrt(3*3 + 4*4 + 5*5)),
        "no_state:9": str(sp.solve(sp.Rational(3, 2)*x / (12-sp.Rational(3, 2)*x)-sp.Rational(1, 2), x)[0]),
        "with_state:9": str(sp.Rational(7, 3)),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    for name in ("raw", "pool", "smoke", "dev", "test-hashes", "strict-manifest", "output"):
        ap.add_argument("--" + name, type=Path, required=True)
    args = ap.parse_args()
    raw = read_jsonl(args.raw)
    strict = json.loads(args.strict_manifest.read_text())
    assert len(raw) == 20 and strict["prompt_count"] == 20
    refs = {r["record_id"]: r for r in read_jsonl(args.pool) + read_jsonl(args.smoke)}
    pool_hash = {r["problem_hash"] for r in read_jsonl(args.pool)}
    dev_hash = {r["problem_hash"] for r in read_jsonl(args.dev)}
    test_hash = set(args.test_hashes.read_text().splitlines())
    seen = {"no_state": set(), "with_state": set()}
    hash_owner = {}
    audited = []
    for row in raw:
        key = f"{row['arm']}:{row['index']}"
        entry = {"arm": row["arm"], "index": row["index"], "strict_valid": row["valid"],
                 "finish_reason": row["finish_reason"], "generated_tokens": row["generated_tokens"]}
        try:
            parsed = diagnostic_final(row["raw"])
            spec = MathDataSpec.model_validate(parsed)
            if not all((spec.problem.strip(), spec.chain_of_thought.strip(), spec.final_answer.strip())):
                raise ValueError("empty spec field")
            h = digest(spec.problem)
            input_hash = {digest(refs[i]["problem"]) for i in row["common_ids"] + row["extra_ids"]}
            flags = {"input_copy": h in input_hash, "pool_exact": h in pool_hash,
                     "dev_exact": h in dev_hash, "test_exact": h in test_hash,
                     "same_arm_duplicate": h in seen[row["arm"]],
                     "cross_arm_duplicate": h in hash_owner and hash_owner[h] != row["arm"]}
            seen[row["arm"]].add(h)
            hash_owner[h] = row["arm"]
            entry.update({"diagnostic_parse_valid": True, "problem_hash": h, "flags": flags,
                          "problem": spec.problem, "final_answer": spec.final_answer})
        except Exception as exc:
            entry.update({"diagnostic_parse_valid": False, "diagnostic_parse_error": str(exc)})
        if key in MATH_REVIEW:
            status, reason = MATH_REVIEW[key]
            entry.update({"math_review": status, "math_review_reason": reason})
        else:
            entry["math_review"] = "not_available_after_truncation"
        audited.append(entry)
    assert sum(r["diagnostic_parse_valid"] for r in audited) == 16
    assert sum(r["math_review"] == "correct" for r in audited) == 13
    assert {r["arm"]: sum(z["diagnostic_parse_valid"] for z in audited if z["arm"] == r["arm"])
            for r in audited} == {"no_state": 8, "with_state": 8}
    assert all(not any(r["flags"].values()) for r in audited if r["diagnostic_parse_valid"])
    report = {
        "scope": "E09 original strict gate retained; object parsing is POST-HOC diagnostic, not protocol success",
        "raw_sha256": sha256(args.raw), "strict_manifest_sha256": sha256(args.strict_manifest),
        "strict_valid_per_arm": strict["valid_per_arm"],
        "diagnostic_parse_valid_per_arm": {arm: sum(r["diagnostic_parse_valid"] for r in audited if r["arm"] == arm)
                                           for arm in seen},
        "finish_reasons": dict(Counter(r["finish_reason"] for r in audited)),
        "math_review_counts": dict(Counter(r["math_review"] for r in audited)),
        "independent_calculations": independent_checks(),
        "records": audited,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({key: value for key, value in report.items() if key != "records"}, indent=2))


if __name__ == "__main__":
    main()
