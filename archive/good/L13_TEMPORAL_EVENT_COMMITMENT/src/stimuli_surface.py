"""E20 — the decisive test between two accounts of the extraction interface.

Surface-test account: extraction asks "is this a non-negated finite past clause?"
and ignores the operator that licenses it.
Capability account (CogNarr-style): the model fails to recognise a category of
suspended content, i.e. it is consulting semantics and getting it wrong.

The two accounts differ in BOTH directions, so the battery crosses licensing
with the surface form of the target clause:

  licensed + clean surface    both predict extract          (ceiling)
  unlicensed + clean surface  surface predicts EXTRACT      capability predicts drop
  licensed + negated surface  surface predicts DROP         capability predicts extract
  unlicensed + negated        both predict drop             (floor, = op_negation)

The licensed+negated cells are the risky ones: no capability account predicts
that a model drops an event the passage *guarantees* happened.
"""
from stimuli_ext import DECOMP, cap

SURFACE_GOLD = {
    "dn_true_that": "YES",            # licensed, clean surface   (ceiling)
    "dn_not_true": "NO",              # unlicensed, clean surface
    "dn_deny": "NOT_DETERMINED",      # unlicensed, clean surface
    "dn_doubtful": "NOT_DETERMINED",  # unlicensed, clean surface
    "dn_false_that_not": "YES",       # licensed, NEGATED surface
    "dn_not_fail": "YES",             # licensed, NEGATED surface
}

# surface form of the target clause itself
SURFACE_FORM = {
    "dn_true_that": "clean",
    "dn_not_true": "clean",
    "dn_deny": "clean",
    "dn_doubtful": "clean",
    "dn_false_that_not": "negated",
    "dn_not_fail": "negated",
}


def surface_passages(base):
    subj, vp = DECOMP[base["id"]]
    sub, main = base["sub"], base["main"]
    return {
        "dn_true_that": f"It is true that {sub}, and {main}.",
        "dn_not_true": f"It is not true that {sub}, and {main}.",
        "dn_deny": f"A colleague denied that {sub}, and {main}.",
        "dn_doubtful": f"It is doubtful that {sub}, and {main}.",
        "dn_false_that_not": f"It is false that {subj} did not {vp}, and {main}.",
        "dn_not_fail": f"{cap(subj)} did not fail to {vp}, and {main}.",
    }
