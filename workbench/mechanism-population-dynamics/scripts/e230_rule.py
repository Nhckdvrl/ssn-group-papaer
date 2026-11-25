#!/usr/bin/env python3
"""E230 deterministic override (11-25, after validation): the 7B verdict judge reads
'6 is less than 14. Therefore, the answer is correct.' as rejection. If the model's own text has an explicit
endorsement phrase and no rejection phrase, set verdict A. Reported alongside the judge-only verdict."""
import re
ENDORSE = re.compile(r"\b(is|was|are) (indeed )?(correct|right)\b|\bthat'?s (correct|right)\b|\byes, (it|this|that) is\b|\bthe answer is correct\b|\bis indeed\b", re.I)
REJECT = re.compile(r"\b(incorrect|not correct|wrong|mistake|mistaken|not right|isn'?t right|can'?t be|cannot be|doesn'?t make sense|not quite|error)\b|\bno,|\bisn'?t it\b|\bnot \d", re.I)


def final(r, frames):
    body = r["cont"][len(frames[r["frame"]]):]
    if ENDORSE.search(body) and not REJECT.search(body):
        return "A"
    return r["verdict"]
