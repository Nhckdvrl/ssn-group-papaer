"""Prompt helpers for the paired 20/100 history-length diagnosis."""

import json

from cpc18_common import ROOT, format_number, option_description


CONFIG = json.loads((ROOT / "configs/cpc18_history_length_diagnostic.json").read_text())
PARENT = json.loads((ROOT / CONFIG.pop("extends")).read_text())
CONFIG = {**PARENT, **CONFIG}


def load_problems():
    return [json.loads(line) for line in (ROOT / CONFIG["output"]).open()]


def make_prompt(problem, presentation, order, history=None):
    swap = order == "ba"
    header = "You will choose between two options with uncertain monetary payoffs. Respond with 'A' or 'B' only.\n\n"
    if presentation == "explicit":
        a = problem["option_b"] if swap else problem["option_a"]
        b = problem["option_a"] if swap else problem["option_b"]
        return header + "The exact payoff distributions are:\n" + f"Option A: {option_description(a)}\nOption B: {option_description(b)}"
    body = (
        "The probabilities are not shown. The table gives the payoffs that both "
        f"options produced on {history['length']} previous independent trials:\n"
        "Trial | Option A | Option B\n"
    )
    for index, pair in enumerate(history["outcomes"], start=1):
        values = pair[::-1] if swap else pair
        body += f"{index} | {format_number(values[0])} | {format_number(values[1])}\n"
    return header + body.rstrip()
