"""L15 prompt construction.

Seven preregistered conditions x two answer modes. Every condition reuses the same
scenario text so that the only thing that changes across the sensitivity grid is the
stated detectability -- the visible outcome is held identical.
"""

from __future__ import annotations

from typing import Dict, List

from stimuli import SCENARIOS, build_items, pct

SCENARIO_BY_ID = {sc.sid: sc for sc in SCENARIOS}

# conditions -------------------------------------------------------------------
# P1_NULL     P(no detection | H)          gold 1-s
# P2_NULL     P(H | no detection)          gold analytic Bayes            <- primary
# P2_HANDED   P(H | no detection), with 1-s handed to the model directly
# P2_POS      P(H | detection)             gold 1.0 at f=0 (sanity control)
# P0_PRIOR    P(H) with no check performed gold p (anchoring baseline)
# P2_ARITH    the same numbers with no cover story (arithmetic control)
# P3_DECIDE   threshold decision           gold yes/no
NUMERIC_CONDITIONS = ("P1_NULL", "P2_NULL", "P2_HANDED", "P2_POS", "P0_PRIOR", "P2_ARITH")
ALL_CONDITIONS = NUMERIC_CONDITIONS + ("P3_DECIDE",)

# conditions whose text depends on the null wording variant
WORDING_SENSITIVE = ("P1_NULL", "P2_NULL", "P3_DECIDE")

NUM_FORMAT = (
    "Answer with a probability between 0 and 1 (two decimal places are enough)."
)
DIRECT_SUFFIX = (
    " Give no explanation. Reply with exactly one line in the form:\nANSWER: <number>"
)
COT_SUFFIX = (
    " Reason briefly first, then end your reply with exactly one line in the form:\n"
    "ANSWER: <number>"
)
DIRECT_SUFFIX_YN = (
    " Give no explanation. Reply with exactly one line in the form:\nANSWER: yes"
    "\nor\nANSWER: no"
)
COT_SUFFIX_YN = (
    " Reason briefly first, then end your reply with exactly one line in the form:\n"
    "ANSWER: yes\nor\nANSWER: no"
)


def _prior_sentence(sc, p: float) -> str:
    return (
        f"Before anything was checked, the probability that {sc.hypothesis} "
        f"was {pct(p)}."
    )


def _sensitivity_sentence(sc, s: float) -> str:
    return (
        f"If {sc.hyp_past}, {sc.procedure} {sc.detect_pos} {pct(s)} of the time; "
        f"the other {pct(1 - s)} of the time it {sc.detect_miss}."
    )


def _handed_sentence(sc, s: float) -> str:
    return (
        f"If {sc.hyp_past}, the probability that {sc.procedure} would "
        f"{sc.miss_bare} is {pct(1 - s)}."
    )


def _false_positive_sentence(sc) -> str:
    return f"If {sc.hyp_neg}, {sc.procedure} never {sc.detect_pos}."


def _context(sc, p: float, s: float, wording: int, *, handed: bool, positive: bool) -> str:
    lines = [sc.setting, _prior_sentence(sc, p)]
    lines.append(_handed_sentence(sc, s) if handed else _sensitivity_sentence(sc, s))
    lines.append(_false_positive_sentence(sc))
    lines.append(sc.report_pos if positive else sc.report_null[wording])
    return " ".join(lines)


def _arith_context(p: float, s: float) -> str:
    return (
        f"A hypothesis H has prior probability {pct(p)}. A test is then run. "
        f"If H is true, the test comes out positive {pct(s)} of the time and negative "
        f"the other {pct(1 - s)} of the time. If H is false, the test never comes out "
        f"positive. The test came out negative."
    )


def build_prompt(item: dict, condition: str, mode: str, wording: int) -> str:
    """Return the user-turn text for one (item, condition, mode, wording) cell."""
    sc = SCENARIO_BY_ID[item["scenario"]]
    p, s = item["p"], item["s"]

    if condition == "P1_NULL":
        ctx = _context(sc, p, s, wording, handed=False, positive=False)
        q = (
            f"Question: Suppose, for this question only, that {sc.hyp_past}. "
            f"What is the probability that {sc.procedure} would nevertheless "
            f"{sc.miss_bare}?"
        )
    elif condition == "P2_NULL":
        ctx = _context(sc, p, s, wording, handed=False, positive=False)
        q = f"Question: What is {sc.question}?"
    elif condition == "P2_HANDED":
        ctx = _context(sc, p, s, 0, handed=True, positive=False)
        q = f"Question: What is {sc.question}?"
    elif condition == "P2_POS":
        ctx = _context(sc, p, s, 0, handed=False, positive=True)
        q = f"Question: What is {sc.question}?"
    elif condition == "P0_PRIOR":
        ctx = " ".join([sc.setting, _prior_sentence(sc, p), "No check has been carried out yet."])
        q = f"Question: What is {sc.question}?"
    elif condition == "P2_ARITH":
        ctx = _arith_context(p, s)
        q = "Question: What is the probability that H is true?"
    elif condition == "P3_DECIDE":
        ctx = _context(sc, p, s, wording, handed=False, positive=False)
        q = (
            f"Policy: {sc.action} if and only if the probability that {sc.hypothesis} "
            f"is greater than {pct(item['threshold'])}.\n"
            f"Question: Under this policy, should you {sc.action}?"
        )
    else:
        raise ValueError(f"unknown condition {condition}")

    if condition == "P3_DECIDE":
        instr = (COT_SUFFIX_YN if mode == "cot" else DIRECT_SUFFIX_YN).lstrip()
    else:
        instr = NUM_FORMAT + (COT_SUFFIX if mode == "cot" else DIRECT_SUFFIX)
    return f"{ctx}\n\n{q}\n\n{instr}"


def build_cells(modes=("direct", "cot")) -> List[dict]:
    """Every prompt cell in the pilot, deduplicated where the text does not vary."""
    cells: List[dict] = []
    seen = set()
    for item in build_items():
        for condition in ALL_CONDITIONS:
            wordings = (0, 1) if condition in WORDING_SENSITIVE else (0,)
            for wording in wordings:
                for mode in modes:
                    prompt = build_prompt(item, condition, mode, wording)
                    key = (condition, mode, prompt)
                    if key in seen:
                        # P2_ARITH and P0_PRIOR collapse across items that share text
                        continue
                    seen.add(key)
                    cells.append(
                        {
                            "cell_id": f"{item['item_id']}|{condition}|{mode}|w{wording}",
                            "item_id": item["item_id"],
                            "scenario": item["scenario"],
                            "frame": item["frame"],
                            "transfer": item["transfer"],
                            "p": item["p"],
                            "s": item["s"],
                            "f": item["f"],
                            "threshold": item["threshold"],
                            "condition": condition,
                            "mode": mode,
                            "wording": wording,
                            "gold": _gold_for(item, condition),
                            "prompt": prompt,
                        }
                    )
    return cells


def _gold_for(item: dict, condition: str):
    return {
        "P1_NULL": item["gold_p1"],
        "P2_NULL": item["gold_p2"],
        "P2_HANDED": item["gold_p2"],
        "P2_POS": item["gold_p2_pos"],
        "P0_PRIOR": item["gold_p0"],
        "P2_ARITH": item["gold_p2"],
        "P3_DECIDE": item["gold_p3"],
    }[condition]
