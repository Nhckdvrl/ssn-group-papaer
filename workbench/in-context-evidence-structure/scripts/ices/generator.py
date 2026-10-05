"""Exact-gold nonce attribute-rule episodes.

An *episode base* fixes: attribute names, label words, hidden rule h_A=(a, s),
the demo input sequence X (T distinct inputs, rule attribute balanced) and a
held-out query input. A *pattern* over {A, B} then fixes every demo label:
  A -> label = h_A(x)            (consistent with the initial/majority rule)
  B -> label = 1 - h_A(x)        (consistent with the reversed rule h_B)
Conditions of one base differ only in which positions carry B labels, so all
inputs, names, query and prompt length (up to the label word) are paired.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
VALUES = ("off", "on")


def load_lexicon(path=None):
    d = json.loads(Path(path or ROOT / "data" / "lexicon.json").read_text())
    return d["attribute_names"], d["labels"]


@dataclass
class Base:
    base_id: str
    n_attr: int
    T: int
    attr_names: list
    label_words: list          # label_words[k] is the word for label index k
    rule_attr: int
    rule_pol: int
    X: list                    # T x n
    xq: list                   # n

    def h_A(self, x):
        return int(x[self.rule_attr]) ^ self.rule_pol


def make_base(seed: int, n_attr: int, T: int, attr_bank, label_bank, max_distractor_agree=0.75,
              tag="b") -> Base:
    rng = np.random.default_rng(seed)
    names = list(rng.choice(attr_bank, n_attr, replace=False))
    # two label words; avoid identical first characters to keep them visually distinct
    while True:
        lw = list(rng.choice(label_bank, 2, replace=False))
        if lw[0][0] != lw[1][0]:
            break
    a = int(rng.integers(n_attr)); s = int(rng.integers(2))
    allx = np.array([[(i >> (n_attr - 1 - j)) & 1 for j in range(n_attr)] for i in range(2 ** n_attr)])
    for _ in range(10000):
        if T > 0:
            # balanced rule attribute among demos
            on = allx[allx[:, a] == 1]; off = allx[allx[:, a] == 0]
            k1 = T // 2 + (T % 2) * int(rng.integers(2))
            if k1 > len(on) or T - k1 > len(off):
                raise ValueError("T too large for n_attr")
            pick = np.concatenate([on[rng.choice(len(on), k1, replace=False)],
                                   off[rng.choice(len(off), T - k1, replace=False)]])
            pick = pick[rng.permutation(T)]
        else:
            pick = np.zeros((0, n_attr), int)
        used = {tuple(r) for r in pick}
        rest = [r for r in allx if tuple(r) not in used]
        if not rest:
            raise ValueError("no held-out query available")
        xq = rest[int(rng.integers(len(rest)))]
        if T > 0:
            yA = pick[:, a] ^ s
            ok = True
            for j in range(n_attr):
                if j == a:
                    continue
                agree = np.mean(pick[:, j] == yA)
                if max(agree, 1 - agree) > max_distractor_agree:
                    ok = False; break
            if not ok:
                continue
        return Base(f"{tag}{seed}", n_attr, T, names, lw, a, s, pick.tolist(), list(map(int, xq)))
    raise RuntimeError("could not sample base")


def labels_for(base: Base, pattern: str) -> list:
    assert len(pattern) == base.T
    out = []
    for x, p in zip(base.X, pattern):
        yA = base.h_A(x)
        out.append(yA if p == "A" else 1 - yA)
    return out


HEADER = "Below are examples of items and their labels.\n\n"


def render(base: Base, labels: list, header: str = HEADER, values=VALUES) -> str:
    def item(x):
        return " ".join(f"{n}={values[v]}" for n, v in zip(base.attr_names, x))
    parts = [header]
    for x, y in zip(base.X, labels):
        parts.append(f"Item: {item(x)}\nLabel: {base.label_words[y]}\n\n")
    parts.append(f"Item: {item(base.xq)}\nLabel:")
    return "".join(parts)


def episode_record(base: Base, pattern: str, cond: str, extra=None, header: str = HEADER) -> dict:
    labels = labels_for(base, pattern)
    yq_A = base.h_A(base.xq)
    rec = {
        "base_id": base.base_id, "cond": cond, "pattern": pattern,
        "n_attr": base.n_attr, "T": base.T, "labels": labels,
        "prompt": render(base, labels, header=header),
        "cands": [" " + base.label_words[0], " " + base.label_words[1]],
        "query_label_A": yq_A,            # index of label predicted by h_A
        "query_label_B": 1 - yq_A,        # index predicted by reversed rule
        "base": asdict(base),
    }
    if extra:
        rec.update(extra)
    return rec
