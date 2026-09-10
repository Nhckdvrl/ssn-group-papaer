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


# --- E06: does an explicit three-state schema repair the collapse? --------
#
# E04 showed that a natural-language prohibition does not stop the model from
# listing an unresolved event as a plain realized node. E06 gives the model a
# first-class slot for `unresolved`, which is the strongest cheap repair. If the
# collapse survives an explicit slot, it is not a schema problem.

SCHEMA_TASK = (
    "Passage:\n{passage}\n\n"
    "Build an event table for this passage. List every event mentioned, one per "
    "line, in chronological order, in the format\n\n"
    "<event> :: <status>\n\n"
    "where <status> is exactly one of:\n"
    "  realized     - the passage guarantees this event happened\n"
    "  unresolved   - the passage leaves it open whether this event happened\n"
    "  not-realized - the passage indicates this event did not happen\n\n"
    "Output only the table."
)

TASK_ORDERS["schema_timeline_first"] = SCHEMA_TASK

# Neutral status codes for the forced-slot measurement, so that the code letters
# carry no mnemonic bias and can be permuted like any other option set.
SCHEMA_CODE_MEANINGS = {
    "REALIZED": "the passage guarantees this event happened",
    "UNRESOLVED": "the passage leaves it open whether this event happened",
    "NOT_REALIZED": "the passage indicates this event did not happen",
}

SCHEMA_CODE_LETTERS = ["X", "Y", "Z"]

SCHEMA_PERMUTATIONS = [
    ("REALIZED", "UNRESOLVED", "NOT_REALIZED"),
    ("REALIZED", "NOT_REALIZED", "UNRESOLVED"),
    ("UNRESOLVED", "REALIZED", "NOT_REALIZED"),
    ("UNRESOLVED", "NOT_REALIZED", "REALIZED"),
    ("NOT_REALIZED", "REALIZED", "UNRESOLVED"),
    ("NOT_REALIZED", "UNRESOLVED", "REALIZED"),
]


def schema_slot_task(passage, permutation):
    """The same structure-building task, with permutable neutral status codes."""
    legend = "\n".join(
        f"  {letter} - {SCHEMA_CODE_MEANINGS[key]}"
        for letter, key in zip(SCHEMA_CODE_LETTERS, permutation)
    )
    return (
        f"Passage:\n{passage}\n\n"
        "Build an event table for this passage. List every event mentioned, one "
        "per line, in chronological order, in the format\n\n"
        "<event> :: <status>\n\n"
        "where <status> is exactly one of:\n"
        f"{legend}\n\n"
        "Output only the table."
    )


def schema_slot_prefix(target):
    """Assistant prefix that forces the target event into a table row."""
    return f"{target.rstrip('.')} :: "
