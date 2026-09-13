"""The three E02 Layer 2 prompts, fixed before any Layer 1 result was seen.

Requirement from the preregistration: semantically equivalent, lexically
distinct. Field labels are disjoint across all three, which is the part the
interface account cares about. Two content words ("sentence", "English") recur
in all three because the task cannot be stated without naming the unit and the
source language -- that shared residue is reported, not hidden, and it works
against the interface account rather than for it.
"""
from langs import LANG

PROMPTS = {
    "P1_explicit": (
        "Translate the following sentence from English to {L}.\nEnglish:",
        "\n{L}:"),
    "P2_render": (
        "Please render the next English sentence into {L}.\nSource:",
        "\nTarget:"),
    "P3_produce": (
        "Below is a sentence in English. Produce its {L} version.\nInput:",
        "\nOutput:"),
}


def prompt(name, lang):
    h, t = PROMPTS[name]
    n = LANG[lang]["name"]
    return h.format(L=n), t.format(L=n)
