"""Probe construction for L13.

All probe strings are defined here so that every experiment uses byte-identical
wording. Changing anything here invalidates existing results.
"""

STRICT_OPTIONS = {
    "YES": "Yes - the passage guarantees that it is true.",
    "NO": "No - the passage rules it out.",
    "NOT_DETERMINED": "Not determined - the passage leaves it open.",
}

STRICT_LABELS = ["YES", "NO", "NOT_DETERMINED"]

LETTERS = ["A", "B", "C", "D", "E"]

# all 6 orderings of the three strict labels
PERMUTATIONS = [
    ("YES", "NO", "NOT_DETERMINED"),
    ("YES", "NOT_DETERMINED", "NO"),
    ("NO", "YES", "NOT_DETERMINED"),
    ("NO", "NOT_DETERMINED", "YES"),
    ("NOT_DETERMINED", "YES", "NO"),
    ("NOT_DETERMINED", "NO", "YES"),
]

LIKELIHOOD_DIGITS = ["1", "2", "3", "4", "5"]


def strict_prompt(passage, target, permutation):
    """User turn for probe P1 under one option ordering."""
    lines = [
        "Passage:",
        passage,
        "",
        f"Statement: {target}",
        "",
        "Based only on the passage, is the statement true?",
        "",
    ]
    for letter, label in zip(LETTERS, permutation):
        lines.append(f"{letter}. {STRICT_OPTIONS[label]}")
    lines += ["", "Answer with a single letter."]
    return "\n".join(lines)


def strict_followup_prompt(target, permutation):
    """P1 as a follow-up turn, when the passage is already in the context."""
    lines = [
        f"Statement: {target}",
        "",
        "Based only on the passage, is the statement true?",
        "",
    ]
    for letter, label in zip(LETTERS, permutation):
        lines.append(f"{letter}. {STRICT_OPTIONS[label]}")
    lines += ["", "Answer with a single letter."]
    return "\n".join(lines)


def likelihood_prompt(passage, target):
    """User turn for probe P2."""
    return "\n".join(
        [
            "Passage:",
            passage,
            "",
            f"Statement: {target}",
            "",
            "How likely is it that the statement is true?",
            "",
            "1 = very unlikely",
            "2 = unlikely",
            "3 = equally likely and unlikely",
            "4 = likely",
            "5 = very likely",
            "",
            "Answer with a single digit.",
        ]
    )


TIMELINE_TASK = (
    "Passage:\n{passage}\n\n"
    "List the events described in this passage in chronological order, "
    "one per line, earliest first. Do not add commentary."
)

PARAPHRASE_TASK = (
    "Passage:\n{passage}\n\n"
    "Restate this passage in your own words, one sentence per line. "
    "Do not add commentary."
)

TASK_ORDERS = {
    "fact_first": None,
    "timeline_first": TIMELINE_TASK,
    "paraphrase_first": PARAPHRASE_TASK,
}


# --- E04: does the ghost node survive an explicit occurrence instruction? ---

TIMELINE_STRICT_TASK = (
    "Passage:\n{passage}\n\n"
    "List only the events that actually happened, in chronological order, "
    "one per line, earliest first. Do not list events that did not happen or "
    "whose occurrence the passage leaves open. Do not add commentary."
)

TASK_ORDERS["timeline_strict_first"] = TIMELINE_STRICT_TASK


# --- E05: a non-generative temporal demand -------------------------------
# The context turn is a single letter, so no declarative assertion about the
# target event can enter the context. If commitment still moves, the effect is
# not "the model was swayed by a sentence it wrote".

ORDER_MC_OPTIONS = ["FIRST_MAIN", "FIRST_TARGET", "UNDETERMINED"]

ORDER_MC_TEXT = {
    "FIRST_MAIN": "{main_event}",
    "FIRST_TARGET": "{target_event}",
    "UNDETERMINED": "It cannot be determined from the passage.",
}

TOPIC_MC_OPTIONS = ["LONGER", "SHORTER", "UNDETERMINED"]


def order_mc_prompt(passage, main_event, target_event, permutation):
    """Temporal-ordering multiple choice over the two events of the passage."""
    lines = ["Passage:", passage, "", "Which of these happened earlier?", ""]
    for letter, key in zip(LETTERS, permutation):
        lines.append(
            f"{letter}. "
            + ORDER_MC_TEXT[key].format(main_event=main_event, target_event=target_event)
        )
    lines += ["", "Answer with a single letter."]
    return "\n".join(lines)


def topic_mc_prompt(passage, permutation):
    """Non-temporal comprehension control with the same answer format."""
    lines = [
        "Passage:",
        passage,
        "",
        "Is this passage written in the past tense?",
        "",
    ]
    text = {
        "LONGER": "Yes, it is written in the past tense.",
        "SHORTER": "No, it is not written in the past tense.",
        "UNDETERMINED": "It cannot be determined from the passage.",
    }
    for letter, key in zip(LETTERS, permutation):
        lines.append(f"{letter}. {text[key]}")
    lines += ["", "Answer with a single letter."]
    return "\n".join(lines)
