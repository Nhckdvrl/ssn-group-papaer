"""Task x protocol registry for L08.

Design note (this is the scientific core of the harness, not plumbing):

The parent compares MMLU / SQuAD-v2 (called "preserved") against GSM8K
("collapsed") and reads the contrast as knowledge-vs-reasoning.  That contrast
confounds three separable factors:

  F1 PROTOCOL  constrained ranking over K given candidates
               vs unconstrained argmax over the full vocabulary
  F2 DEPTH     one scored decision vs L sequential generated decisions
  F3 CONTENT   factual recall vs multi-step computation

Every cell below is labelled with its (protocol, depth, content) coordinates so
that experiments can cross the factors instead of inheriting the confound.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from typing import Any, Callable

os.environ.setdefault("HF_DATASETS_OFFLINE", "1")
from datasets import load_dataset  # noqa: E402


@dataclass
class Cell:
    name: str
    protocol: str          # "rank" | "gen"
    depth: str             # "single" | "short" | "long"
    content: str           # "knowledge" | "reading" | "reasoning" | "copy"
    build: Callable[[dict], Any] = None
    max_new_tokens: int = 0
    stop: list = field(default_factory=list)


# --------------------------------------------------------------------------
# MMLU
# --------------------------------------------------------------------------
LETTERS = ["A", "B", "C", "D"]


def _mmlu_stem(ex: dict) -> str:
    lines = [ex["question"].strip()]
    for L, c in zip(LETTERS, ex["choices"]):
        lines.append(f"{L}. {c}")
    lines.append("Answer:")
    return "\n".join(lines)


def _mmlu_fewshot(dev_by_subject: dict, subject: str, k: int) -> str:
    head = (
        "The following are multiple choice questions (with answers) about "
        f"{subject.replace('_', ' ')}.\n\n"
    )
    shots = []
    for ex in dev_by_subject.get(subject, [])[:k]:
        shots.append(_mmlu_stem(ex) + f" {LETTERS[ex['answer']]}")
    return head + ("\n\n".join(shots) + "\n\n" if shots else "")


# --------------------------------------------------------------------------
# GSM8K
# --------------------------------------------------------------------------
GSM_ANS = re.compile(r"#### (\-?[0-9\.\,]+)")
GSM_STRICT = re.compile(r"#### (\-?[0-9\.\,]+)")


def gsm_gold(ans: str) -> str:
    m = GSM_ANS.search(ans)
    return m.group(1).replace(",", "").strip() if m else None


def gsm_extract(text: str) -> str:
    m = GSM_STRICT.search(text)
    return m.group(1).replace(",", "").strip() if m else None


def _gsm_shot(ex: dict) -> str:
    return f"Question: {ex['question'].strip()}\nAnswer: {ex['answer'].strip()}"


def _gsm_shot_direct(ex: dict) -> str:
    return (
        f"Question: {ex['question'].strip()}\n"
        f"Answer: #### {gsm_gold(ex['answer'])}"
    )


# --------------------------------------------------------------------------
# SQuAD-v2
# --------------------------------------------------------------------------
def squad_norm(s: str) -> str:
    s = s.lower()
    s = re.sub(r"\b(a|an|the)\b", " ", s)
    s = re.sub(r"[^\w\s]", " ", s)
    return " ".join(s.split())


def _squad_shot(ex: dict) -> str:
    ans = ex["answers"]["text"]
    a = ans[0] if ans else "unanswerable"
    return (
        f"Title: {ex['title']}\n\nBackground: {ex['context']}\n\n"
        f"Question: {ex['question']}\n\nAnswer: {a}"
    )


# --------------------------------------------------------------------------
# Item builders.  Each returns a list of dicts with a uniform schema:
#   {id, prompt, gold, candidates?(rank), meta}
# --------------------------------------------------------------------------
import random  # noqa: E402


def _subset(ds, n, seed):
    idx = list(range(len(ds)))
    random.Random(seed).shuffle(idx)
    return ds.select(sorted(idx[:n]))


def build_mmlu(n=1000, seed=1234, shots=5, protocol="rank", cot=False):
    ds = load_dataset("cais/mmlu", "all")
    dev = ds["dev"]
    dev_by_subject = {}
    for ex in dev:
        dev_by_subject.setdefault(ex["subject"], []).append(ex)
    test = _subset(ds["test"], n, seed)

    items = []
    for i, ex in enumerate(test):
        pre = _mmlu_fewshot(dev_by_subject, ex["subject"], shots)
        if cot:
            # long unconstrained generation on the SAME knowledge content
            head = (
                "The following are multiple choice questions about "
                f"{ex['subject'].replace('_', ' ')}. Think step by step, then "
                "finish with a line of the form 'Answer: X'.\n\n"
            )
            body = _mmlu_stem(ex)[: -len("\nAnswer:")]
            prompt = head + body + "\n\nLet's think step by step."
        else:
            prompt = pre + _mmlu_stem(ex)
        it = {
            "id": f"mmlu-{i}",
            "prompt": prompt,
            "gold": LETTERS[ex["answer"]],
            "meta": {"subject": ex["subject"]},
        }
        if protocol == "rank":
            it["candidates"] = [f" {L}" for L in LETTERS]
            it["gold_index"] = ex["answer"]
        items.append(it)
    return items


def build_gsm8k(n=500, seed=1234, shots=5, cot=True):
    ds = load_dataset("openai/gsm8k", "main")
    shot_pool = ds["train"].select(range(shots))
    fmt = _gsm_shot if cot else _gsm_shot_direct
    header = "\n\n".join(fmt(ex) for ex in shot_pool) + "\n\n"
    if not cot:
        header = (
            "Answer each question with the final numeric answer only, in the "
            "form '#### N'.\n\n" + header
        )
    test = _subset(ds["test"], n, seed)
    items = []
    for i, ex in enumerate(test):
        items.append({
            "id": f"gsm8k-{i}",
            "prompt": header + f"Question: {ex['question'].strip()}\nAnswer:",
            "gold": gsm_gold(ex["answer"]),
            "meta": {"gold_cot": ex["answer"].strip()},
        })
    return items


def build_squad(n=1000, seed=1234, shots=2):
    ds = load_dataset("rajpurkar/squad_v2")
    shot_pool = [ds["train"][j] for j in (0, 1, 130318, 130317)][:shots * 2]
    # one answerable + one unanswerable shot, to expose the no-answer option
    ans_shot = next(e for e in shot_pool if e["answers"]["text"])
    noans_shot = next((e for e in shot_pool if not e["answers"]["text"]), None)
    shots_txt = [_squad_shot(ans_shot)]
    if noans_shot is not None:
        shots_txt.append(_squad_shot(noans_shot))
    header = "\n\n".join(shots_txt) + "\n\n"
    val = _subset(ds["validation"], n, seed)
    items = []
    for i, ex in enumerate(val):
        items.append({
            "id": f"squad-{i}",
            "prompt": header + (
                f"Title: {ex['title']}\n\nBackground: {ex['context']}\n\n"
                f"Question: {ex['question']}\n\nAnswer:"
            ),
            "gold": ex["answers"]["text"],
            "meta": {"answerable": bool(ex["answers"]["text"])},
        })
    return items
