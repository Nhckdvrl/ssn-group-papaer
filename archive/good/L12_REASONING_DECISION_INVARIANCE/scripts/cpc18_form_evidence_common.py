"""Frozen prompts and parsing helpers for L12-E20."""

import json
import os
from pathlib import Path

from cpc18_common import (
    ROOT,
    format_number,
    parse_terminal_choice,
    shown_choice,
    split_trace,
    strip_terminal_conclusion,
    underlying_choice,
    load_config,
)


CONFIG_PATH = Path(os.environ.get(
    "L12_FORM_EVIDENCE_CONFIG",
    "configs/cpc18_form_evidence_preregistered.json",
))
if not CONFIG_PATH.is_absolute():
    CONFIG_PATH = ROOT / CONFIG_PATH
CONFIG = load_config(CONFIG_PATH)


def load_problems(limit=None):
    with (ROOT / CONFIG["output"]).open() as handle:
        rows = [json.loads(line) for line in handle]
    return rows if limit is None else rows[:limit]


def option_frequencies(frequencies):
    return "; ".join(
        f"{format_number(payoff)} points occurred {count}/20 times"
        for payoff, count in frequencies
    )


def make_prompt(problem, evidence, form, order):
    header = (
        "You will choose between two options based only on observations from "
        "20 previous independent trials. Respond with 'A' or 'B' only.\n\n"
    )
    swap = order == "ba"
    if form == "raw":
        body = (
            "The table gives the observed payoffs in their original trial "
            "order. The generating probabilities are not shown:\n"
            "Trial | Option A | Option B\n"
        )
        for index, pair in enumerate(evidence["outcomes"], start=1):
            values = pair[::-1] if swap else pair
            body += (
                f"{index} | {format_number(values[0])} | "
                f"{format_number(values[1])}\n"
            )
    elif form == "summary":
        a = evidence["option_b_frequencies"] if swap else evidence["option_a_frequencies"]
        b = evidence["option_a_frequencies"] if swap else evidence["option_b_frequencies"]
        body = (
            "The exact empirical payoff counts from those same 20 observations "
            "are summarized below. The generating probabilities are not shown:\n"
            f"Option A: {option_frequencies(a)}\n"
            f"Option B: {option_frequencies(b)}\n"
        )
    else:
        raise ValueError(f"Unknown form: {form}")
    return header + body.rstrip()
