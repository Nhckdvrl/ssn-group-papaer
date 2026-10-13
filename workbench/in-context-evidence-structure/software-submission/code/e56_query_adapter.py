"""Shared helpers: the prompt header, the Measuring Hate Speech comment pools and the context builder."""
import argparse, copy, json
from pathlib import Path
import numpy as np, torch

HEAD = "Below are comments and the labels that individual annotators gave them.\n\n"


def pools(seed=5600):
    from datasets import load_dataset
    d = load_dataset("ucberkeley-dlab/measuring-hate-speech", split="train").select_columns(
        ["comment_id", "hatespeech", "target_race", "target_gender", "text"]).to_pandas()
    g = d.groupby("comment_id").agg(race=("target_race", "mean"), gender=("target_gender", "mean"), hs=("hatespeech", "mean"), text=("text", "first"))
    g = g[(g.text.map(lambda t: len(t.split()) <= 50)) & (g.hs >= 1.0)]
    race = g[(g.race >= 0.75) & (g.gender <= 0.1)].text.tolist(); gender = g[(g.gender >= 0.75) & (g.race <= 0.1)].text.tolist()
    rng = np.random.default_rng(seed); rng.shuffle(race); rng.shuffle(gender)
    cut = lambda x: (x[: int(len(x) * 0.7)], x[int(len(x) * 0.7):])
    (rtr, rte), (gtr, gte) = cut(race), cut(gender)
    return {"train": (rtr, gtr), "test": (rte, gte)}


def contexts(pool, n, rng, nq=8, shuffle_names=False):
    race, gender = pool
    out = []
    for _ in range(n):
        r = list(rng.choice(race, 8 + nq, replace=False)); g_ = list(rng.choice(gender, 8 + nq, replace=False))
        A = [(t, 0, 1) for t in r[:4]] + [(t, 0, 0) for t in g_[:4]]          # (text, role, toxic)
        B = [(t, 1, 0) for t in r[4:8]] + [(t, 1, 1) for t in g_[4:8]]
        demos = [(A + B)[j] for j in rng.permutation(16)]
        names = list(rng.permutation(["Alex", "Sam"]))
        shown = [names[role] if not shuffle_names else names[int(rng.integers(2))] for _, role, _ in demos]
        q = [(t, "race") for t in r[8:]] + [(t, "gender") for t in g_[8:]]
        out.append({"demos": demos, "shown": shown, "names": names, "q": q})
    return out


def correct(role, kind):
    return int((role == 0) == (kind == "race"))       # A: race toxic; B: gender toxic


