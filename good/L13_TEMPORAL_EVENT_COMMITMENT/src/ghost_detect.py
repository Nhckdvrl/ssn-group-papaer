"""Adjudication rule for whether a generated structure asserts the target event.

v2. The v1 lexical rule counted any line whose content matched the target, which
mislabelled outputs that merely reproduce the source construction
(`Before Maya submitted the application, the portal closed.`). Copying a
`before`-clause preserves non-veridicality; it is NOT an assertion that the
event occurred.

A generated line asserts the target event iff the target proposition occupies a
MAIN clause of that line, with no negation or hedge attached.
"""
import re

HEDGE = re.compile(
    r"\b(not|never|n't|unclear|unknown|unresolved|may|might|would|could|whether|"
    r"planned|intended|hoped|meant|wanted|possible|possibly|uncertain|if|"
    r"unresolved|pending|attempted|tried)\b",
    re.I,
)
STOP = set("the a an of to and or in on at for with his her their its by that this it".split())
LIST_MARKER = re.compile(r"^\s*(?:[-*•]|\d+[.)])\s*")
SUBORDINATOR = re.compile(r"^(before|after|once|when|while|until|by the time)\b", re.I)


def content(s):
    return {w for w in re.findall(r"[a-z']+", s.lower()) if w not in STOP}


def _overlap(target_words, span):
    if not target_words:
        return 0.0
    return len(target_words & content(span)) / len(target_words)


def line_asserts_target(line, target, threshold=0.7):
    """True iff `line` asserts the target event as a realized main-clause event."""
    line = LIST_MARKER.sub("", line.strip())
    if not line or HEDGE.search(line):
        return False
    tw = content(target)

    if SUBORDINATOR.match(line):
        # "Before <subordinate>, <main>" — the subordinate clause asserts nothing.
        parts = line.split(",", 1)
        if len(parts) == 1:
            # a bare subordinate fragment listed as an entry: not an assertion
            return False
        main = parts[1]
        return _overlap(tw, main) >= threshold

    # otherwise the whole line is (or begins with) a main clause
    return _overlap(tw, line) >= threshold


def output_asserts_target(text, target, threshold=0.7):
    return any(line_asserts_target(l, target, threshold) for l in text.splitlines())
