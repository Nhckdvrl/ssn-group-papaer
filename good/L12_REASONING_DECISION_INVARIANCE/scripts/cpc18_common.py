"""Shared frozen CPC18 prompt, ordering, parsing, and trajectory utilities."""

import json
import os
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = Path(os.environ.get("L12_CPC18_CONFIG", "configs/cpc18.json"))
if not CONFIG_PATH.is_absolute():
    CONFIG_PATH = ROOT / CONFIG_PATH
CONFIG = json.loads(CONFIG_PATH.read_text())
PARSER_VERSION = "cpc18_terminal_v2"
STRIPPING_VERSION = "cpc18_terminal_commitment_v3"


def load_problems(limit=None):
    with (ROOT / CONFIG["output"]).open() as handle:
        rows = [json.loads(line) for line in handle]
    return rows if limit is None else rows[:limit]


def format_number(value):
    if float(value).is_integer():
        return str(int(value))
    return f"{value:.8f}".rstrip("0").rstrip(".")


def format_probability(value):
    return f"{100 * value:.8f}".rstrip("0").rstrip(".") + "%"


def option_description(distribution):
    if len(distribution) == 1:
        return f"{format_number(distribution[0][0])} points for certain"
    return "; ".join(
        f"{format_probability(probability)} chance of {format_number(payoff)} points"
        for payoff, probability in distribution
    )


def displayed_mapping(order):
    return {"A": "A", "B": "B"} if order == "ab" else {"A": "B", "B": "A"}


def shown_choice(underlying, order):
    if order == "ab":
        return underlying
    return "B" if underlying == "A" else "A"


def underlying_choice(shown, order):
    if shown is None or order == "ab":
        return shown
    return "B" if shown == "A" else "A"


def make_prompt(problem, presentation, order, history=None):
    mapping = displayed_mapping(order)
    header = (
        "You will choose between two options with uncertain monetary payoffs. "
        "Respond with 'A' or 'B' only.\n\n"
    )
    if presentation == "explicit":
        body = "The exact payoff distributions are:\n"
        for shown in ["A", "B"]:
            underlying = mapping[shown].lower()
            body += (
                f"Option {shown}: "
                f"{option_description(problem[f'option_{underlying}'])}\n"
            )
    elif presentation == "history":
        if history is None:
            raise ValueError("History presentation requires a realized history")
        body = (
            "The probabilities are not shown. The table gives the payoffs that "
            "both options produced on 20 previous independent trials:\n"
            "Trial | Option A | Option B\n"
        )
        for index, pair in enumerate(history["outcomes"], start=1):
            values = pair if order == "ab" else [pair[1], pair[0]]
            body += (
                f"{index} | {format_number(values[0])} | "
                f"{format_number(values[1])}\n"
            )
    else:
        raise ValueError(f"Unknown presentation: {presentation}")
    return header + body.rstrip()


def parse_terminal_choice(text, require_closed_think=False):
    if require_closed_think:
        if "</think>" not in text:
            return None, "no_closed_think"
        answer = text.split("</think>", 1)[1].strip()
    else:
        answer = text.strip()
    patterns = [
        (r"^\s*(?:\\boxed\{)?\s*([AB])\s*\}?\s*[.!]?\s*$", "direct"),
        (r"\\boxed\{(?:\\text\{)?\s*([AB])\s*\}?\}", "boxed"),
        (r"(?i)(?:final\s+)?(?:answer|choice)\s*(?:is|would be|:)\s*"
         r"(?:option\s*)?[*\\({\s]*([AB])\b", "answer_field"),
        (r"(?i)(?:i(?:'ll|\s+will|\s+am)?\s+)?"
         r"(?:choose|select|pick|go(?:ing)?\s+with)\W{0,20}"
         r"(?:option\s+)?\**([AB])\b", "choice_verb"),
        (r"(?im)(?:^|\n)\s*\*{0,2}([AB])\*{0,2}\s*[.!]?\s*$", "terminal_label"),
    ]
    matches = []
    for pattern, rule in patterns:
        found = list(re.finditer(pattern, answer))
        if found:
            matches.append((found[-1].start(), found[-1].group(1).upper(), rule))
    if not matches:
        return None, "no_terminal_answer"
    _, choice, rule = max(matches)
    return choice, rule


def split_trace(text):
    if "</think>" not in text:
        return None
    return text.split("</think>", 1)[0].replace("<think>", "").strip()


def is_decision_segment(segment):
    patterns = [
        # Require the label to be the object of the decision verb.  The earlier
        # loose window misclassified prompts such as "choose between A and B"
        # as an immediate commitment to A.
        r"(?i)\b(?:choose|select|pick|prefer|answer)\b"
        r"(?!\s+between\b)(?:\s+(?:option|choice))?\W{0,12}[AB]\b",
        r"(?i)\b(?:option|choice)\s+[AB]\b[^.\n]{0,80}"
        r"\b(?:better|best|optimal|preferred|wins?)\b",
        r"(?i)\b(?:therefore|thus|hence|finally|overall)\b"
        r"\W{0,20}(?:option\s+)?[AB]\b",
    ]
    return any(re.search(pattern, segment) for pattern in patterns)


def strip_terminal_conclusion(trace):
    if trace is None:
        return None, []
    parts = [
        part.strip()
        for part in re.split(r"(?<=[.!?])\s+|\n+", trace.strip())
        if part.strip()
    ]
    first = next(
        (index for index, part in enumerate(parts) if is_decision_segment(part)),
        None,
    )
    if first is None:
        return " ".join(parts).strip(), []
    return " ".join(parts[:first]).strip(), parts[first:]
