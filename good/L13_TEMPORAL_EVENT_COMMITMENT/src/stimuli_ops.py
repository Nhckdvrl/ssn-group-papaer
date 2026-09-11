"""E19 — operator battery.

The interface hypothesis says a semantic licensing constraint the model applies
at the judgement interface is not applied at the extraction interface. If that
is a property of the *interface* and not of `before`, then other operators that
block realization should also be dropped when the model is asked to enumerate
events.

Every condition introduces the SAME proposition `E` under a different operator,
with the same second event as company so the enumeration task always has two
candidates. Nothing here involves a temporal subordinator.

gold is strict licensing by the passage, as everywhere else in this project.
"""
from stimuli_ext import DECOMP, cap

OP_GOLD = {
    "op_assert": "YES",            # positive control: E is asserted outright
    "op_negation": "NO",           # explicit negation
    "op_report": "NOT_DETERMINED",  # attribution to a source
    "op_conditional": "NOT_DETERMINED",
    "op_possible": "NOT_DETERMINED",
    "op_future": "NOT_DETERMINED",
    "op_intend": "NOT_DETERMINED",  # anchor: the existing non-temporal control is of this kind
}


def op_passages(base):
    subj, vp = DECOMP[base["id"]]
    sub, main = base["sub"], base["main"]
    return {
        "op_assert": f"{cap(sub)}, and {main}.",
        "op_negation": f"{cap(subj)} did not {vp}, and {main}.",
        "op_report": f"A colleague claimed that {sub}, and {main}.",
        "op_conditional": f"If {sub}, {main}.",
        "op_possible": f"It is possible that {sub}, and {main}.",
        "op_future": f"{cap(main)}, and {subj} will {vp} next week.",
        "op_intend": f"{cap(subj)} intended to {vp}, and {main}.",
    }
