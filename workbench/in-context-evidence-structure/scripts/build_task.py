"""E11: latent change between two FAMILIAR tasks (task recognition level).

Inputs: common lowercase English words (4-7 letters, alphabetic, in the system dictionary,
single token in the Qwen3 tokenizer with a leading space -> frequent words).
Task A / B pairs (exact programmatic gold):
  upper_rev : A = uppercase (cat -> CAT), B = reversed (cat -> tac)
  rev_upper : roles swapped (counterbalancing)
Same A/B patterns as E05 (T=16).  Readout: log-odds of the B-task output vs the A-task output
for the query word (exact multi-token sequence log-probs).  Oracle: label-stream style with one
binary 'which task' variable is not appropriate (outputs differ per word), so we use the rule
oracle with a single constant attribute: every demo is evidence for task A or task B exactly
like a constant-input label stream (no input carries information about which task holds).
"""
import json, os, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ices.oracle import all_oracles_fast  # noqa
import build_dim as bd  # noqa
from functools import lru_cache


@lru_cache(maxsize=None)
def _ORC(labs):
    """label-stream oracle depends only on the A/B label sequence -> cache"""
    return all_oracles_fast(np.ones((len(labs), 1), int), list(labs), [1], 1)

ROOT = Path(__file__).resolve().parents[1]
T = 16
N = int(os.environ.get("N_BASES", 200)); SEED0 = int(os.environ.get("SEED0", 140000))
OUT = ROOT / "data" / os.environ.get("OUT", "task_pilot_T16"); OUT.mkdir(parents=True, exist_ok=True)
HEADER = "Below are examples of inputs and outputs.\n\n"


def words():
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained("Qwen/Qwen3-8B")
    dw = {w.strip() for w in open("/usr/share/dict/american-english") if w.strip().isalpha() and w.strip().islower()}
    W = sorted(w for w in dw if 4 <= len(w) <= 7 and len(tok.encode(" " + w)) == 1 and w != w[::-1])
    return W


FN = {"upper": lambda w: w.upper(), "rev": lambda w: w[::-1],
      "first": lambda w: w[0], "last": lambda w: w[-1],
      "dropfirst": lambda w: w[1:], "droplast": lambda w: w[:-1]}
PAIRS = [tuple(p.split("-")) for p in os.environ.get("PAIRS", "upper-rev").split(",")]


def render(ws, outs, q):
    parts = [HEADER]
    for w, o in zip(ws, outs):
        parts.append(f"Input: {w}\nOutput: {o}\n\n")
    parts.append(f"Input: {q}\nOutput:")
    return "".join(parts)


def main():
    W = words()
    W = [w for w in W if all(FN[a](w) != FN[b](w) for a, b in PAIRS)]
    print(len(W), "words; e.g.", W[:10])
    conds = bd.conditions()
    rows = []
    for i in range(N):
        seed = SEED0 + i * 7919
        rng = np.random.default_rng(seed)
        pa = PAIRS[i % len(PAIRS)] if len(PAIRS) > 1 and os.environ.get("MIXPAIRS") else PAIRS[0]
        A, B = pa if (i // max(1, len(PAIRS) if os.environ.get("MIXPAIRS") else 1)) % 2 == 0 else pa[::-1]
        ws = list(rng.choice(W, T + 1, replace=False)); q = ws[T]; ws = ws[:T]
        for name, pat in conds.items():
            outs = [FN[A](w) if ch == "A" else FN[B](w) for w, ch in zip(ws, pat)]
            labs = [0 if ch == "A" else 1 for ch in pat]          # 0 = task A evidence, 1 = task B
            o = dict(_ORC(tuple(labs)))
            o["meta_pB"] = o["meta_p_rule_query"]; o["set_pB"] = o["set_p_rule_query"]; o["sequence_pB"] = o["sequence_p_rule_query"]
            gname = os.environ.get("GNAME", "task")
            rows.append({"uid": f"{A}_{B}:{name}|{gname}_{seed}", "cond": f"{gname}:{name}", "base_id": f"{gname}_{seed}",
                         "pattern": pat, "labels": labs, "prompt": render(ws, outs, q),
                         "cands": [" " + FN[A](q), " " + FN[B](q)], "query_label_A": 0, "query_label_B": 1,
                         "base": {"words": ws, "q": q, "A": A, "B": B}, "oracle": o})
    with open(OUT / "rows.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print(len(rows), "rows ->", OUT)
    print(rows[conds and 5]["prompt"][-300:])


if __name__ == "__main__":
    main()
