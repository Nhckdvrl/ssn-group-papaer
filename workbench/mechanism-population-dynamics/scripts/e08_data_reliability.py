"""E08: induction-rule hit rate vs rare-token density of the preceding context, on pile-10k (CPU).

Writes results/e08/induction_reliability.json.
"""
import json

import numpy as np
import torch
from datasets import load_dataset
from transformers import AutoTokenizer

import mp_common as mc
import e02_population as p2

BINS = [0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0001]


def main():
    tok = AutoTokenizer.from_pretrained("EleutherAI/pythia-70m", cache_dir=str(mc.HF_CACHE))
    counts = torch.load(p2.COUNTS).numpy()
    rare = counts < 50
    ds = load_dataset("NeelNanda/pile-10k", split="train")
    hit = np.zeros((len(BINS) - 1, 2))
    tot = np.zeros((len(BINS) - 1, 2))
    for text in ds["text"]:
        ids = np.array(tok(text)["input_ids"][:2048])
        ids = ids[ids < len(counts)]
        if len(ids) < 60:
            continue
        r = rare[ids].astype(np.float64)
        cs = np.concatenate([[0], np.cumsum(r)])
        last = {}
        for t in range(len(ids) - 1):
            x = ids[t]
            s = last.get(x)
            last[x] = t
            if t < 50 or s is None or t - s > 512:
                continue
            dens = (cs[t] - cs[t - 50]) / 50.0
            b = min(np.searchsorted(BINS, dens, side="right") - 1, len(BINS) - 2)
            k = int(rare[x])
            tot[b, k] += 1
            hit[b, k] += ids[t + 1] == ids[s + 1]
    out = {"bins": BINS, "rows": []}
    for b in range(len(BINS) - 1):
        row = {"density": [BINS[b], BINS[b + 1]]}
        for k, name in ((0, "cur_common"), (1, "cur_rare")):
            n, h = tot[b, k], hit[b, k]
            pr = h / n if n else None
            se = (pr * (1 - pr) / n) ** 0.5 if n else None
            row[name] = {"n": int(n), "hit": pr, "ci95": [pr - 1.96 * se, pr + 1.96 * se] if n else None}
        n, h = tot[b].sum(), hit[b].sum()
        row["all"] = {"n": int(n), "hit": h / n if n else None}
        out["rows"].append(row)
        print(row, flush=True)
    (mc.RESULTS / "e08").mkdir(exist_ok=True)
    (mc.RESULTS / "e08" / "induction_reliability.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
