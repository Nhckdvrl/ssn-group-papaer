"""Natural-word label stream (global regime, constant input) for the lexicon-free confirmation set."""
import json, os, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ices.oracle import all_oracles_fast  # noqa
import build_dim as bd  # noqa

ROOT = Path(__file__).resolve().parents[1]
T = 16
N = int(os.environ.get("N_BASES", 200)); SEED0 = int(os.environ.get("SEED0", 300000))
OUT = ROOT / "data" / os.environ.get("OUT", "stream_nat"); OUT.mkdir(parents=True, exist_ok=True)
PAIRS = [("red", "blue"), ("apple", "orange"), ("north", "south"), ("cat", "dog"), ("river", "mountain"),
         ("circle", "square"), ("coffee", "tea"), ("winter", "summer"), ("piano", "guitar"), ("silver", "gold")]
ITEMS = ["box", "card", "stone", "cup", "page", "tile", "coin", "leaf", "shell", "bead", "ring", "key"]
HEADER = "Below are examples of items and their labels.\n\n"


def main():
    conds = bd.conditions(); rows = []
    for i in range(N):
        seed = SEED0 + i * 7919; rng = np.random.default_rng(seed)
        lw = list(PAIRS[rng.integers(len(PAIRS))]); rng.shuffle(lw)
        item = str(rng.choice(ITEMS)); s = int(rng.integers(2))
        for name, pat in conds.items():
            labs = [s if ch == "A" else 1 - s for ch in pat]
            prompt = HEADER + "".join(f"Item: {item}\nLabel: {lw[y]}\n\n" for y in labs) + f"Item: {item}\nLabel:"
            o = all_oracles_fast(np.ones((T, 1), int), labs, [1], 1)
            qb = 1 - s; 
            for k in ("set", "sequence", "meta"):
                v = o[f"{k}_p_rule_query"]; o[f"{k}_pB"] = v if qb == 1 else 1 - v
            rows.append({"uid": f"stream:{name}|st_{seed}", "cond": f"stream:{name}", "base_id": f"st_{seed}",
                         "pattern": pat, "labels": labs, "prompt": prompt, "cands": [" " + lw[0], " " + lw[1]],
                         "query_label_A": s, "query_label_B": qb, "base": {"lw": lw, "item": item}, "oracle": o})
    with open(OUT / "rows.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print(len(rows), "->", OUT)


if __name__ == "__main__":
    main()
