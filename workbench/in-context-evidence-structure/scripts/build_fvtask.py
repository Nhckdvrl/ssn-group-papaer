"""E19: switches between standard function-vector tasks (Todd et al. 2024 public datasets).

Pairs: ant_syn (antonym <-> synonym; relational, outputs are English words),
       fr_es (English->French <-> English->Spanish; output language visible),
       fr_de (English->French <-> English->German).
Inputs: words present in both task files with single-word outputs that differ between tasks and from
the input.  A/B roles swap on odd bases.  27 A/B patterns (T=16).  Readout: B-task vs A-task answer for
a held-out query word.  Oracle: per-demo A/B evidence stream.
Data note: the task files are the authors' public curated lists; no extra LLM audit (step-5 quota).
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
N = int(os.environ.get("N_BASES", 300)); SEED0 = int(os.environ.get("SEED0", 600000))
OUT = ROOT / "data" / os.environ.get("OUT", "conf_fvtask"); OUT.mkdir(parents=True, exist_ok=True)
FV = ROOT / "data" / "fv_tasks"
PAIRS = {"ant_syn": ("antonym", "synonym"), "fr_es": ("english-french", "english-spanish"),
         "fr_de": ("english-french", "english-german")}
HEADER = "Below are examples of inputs and outputs.\n\n"


def load(t):
    return {d["input"].strip(): d["output"].strip() for d in json.load(open(FV / f"{t}.json"))}


def main():
    conds = bd.conditions(); rows = []
    for name, (ta, tb) in PAIRS.items():
        A0, B0 = load(ta), load(tb)
        W = sorted(w for w in A0 if w in B0 and w.isalpha() and A0[w] != B0[w]
                   and A0[w].lower() != w.lower() and B0[w].lower() != w.lower()
                   and " " not in A0[w] and " " not in B0[w] and A0[w].lower() != B0[w].lower())
        for i in range(N):
            seed = SEED0 + 1000 * list(PAIRS).index(name) + i * 7919
            rng = np.random.default_rng(seed)
            fa, fb = (A0, B0) if i % 2 == 0 else (B0, A0)
            ws = list(rng.choice(W, T + 1, replace=False)); q = ws[T]; ws = ws[:T]
            for pname, pat in conds.items():
                ys = [fa[w] if c == "A" else fb[w] for w, c in zip(ws, pat)]
                labs = [0 if c == "A" else 1 for c in pat]
                prompt = HEADER + "".join(f"Input: {w}\nOutput: {y}\n\n" for w, y in zip(ws, ys)) + f"Input: {q}\nOutput:"
                o = dict(_ORC(tuple(labs)))
                o["meta_pB"] = o["meta_p_rule_query"]; o["set_pB"] = o["set_p_rule_query"]; o["sequence_pB"] = o["sequence_p_rule_query"]
                rows.append({"uid": f"{name}:{pname}|{name}_{seed}", "cond": f"{name}:{pname}", "base_id": f"{name}_{seed}",
                             "pattern": pat, "labels": labs, "prompt": prompt, "cands": [" " + fa[q], " " + fb[q]],
                             "query_label_A": 0, "query_label_B": 1,
                             "base": {"words": ws, "q": q, "A": ta if i % 2 == 0 else tb, "B": tb if i % 2 == 0 else ta},
                             "oracle": o})
        print(name, len(W), "words")
    with open(OUT / "rows.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(len(rows), "->", OUT); print(rows[3]["prompt"][-160:], rows[3]["cands"])


if __name__ == "__main__":
    main()
