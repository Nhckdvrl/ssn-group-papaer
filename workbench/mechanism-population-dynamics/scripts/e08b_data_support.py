"""E08b: data support / copy reliability of rare-dominated contexts on a large Pile sample (CPU, streaming).

Writes results/e08/data_support_large.json.
"""
import json
import time

import numpy as np
from datasets import load_dataset
from transformers import AutoTokenizer

import mp_common as mc

V = 50277
N_COUNT, N_STAT = 100_000_000, 100_000_000
THRESH = 333
BINS = [0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0001]


def stream():
    ds = load_dataset("NeelNanda/pile-small-tokenized-2b", split="train", streaming=True)
    for row in ds:
        yield np.asarray(row["tokens"], dtype=np.int64)


def docs(it, budget):
    """Yield documents (split at EOS=0) until `budget` tokens consumed."""
    used, buf = 0, []
    for seq in it:
        used += len(seq)
        cuts = np.nonzero(seq == 0)[0]
        start = 0
        for c in cuts:
            buf.append(seq[start:c])
            yield np.concatenate(buf) if len(buf) > 1 else buf[0]
            buf, start = [], c + 1
        buf.append(seq[start:])
        if used >= budget:
            return


def main():
    t0 = time.time()
    tok = AutoTokenizer.from_pretrained("EleutherAI/pythia-70m", cache_dir=str(mc.HF_CACHE))
    dec = [tok.decode([i]) for i in range(V)]
    nonascii = np.array([("�" in d) or any(ord(ch) > 127 for ch in d) for d in dec])
    alpha = np.array([d.strip().isalpha() and d.isascii() for d in dec])
    it = stream()
    counts = np.zeros(V, dtype=np.int64)
    used = 0
    for seq in it:
        seq = seq[seq < V]
        counts += np.bincount(seq, minlength=V)
        used += len(seq)
        if used >= N_COUNT:
            break
    rare = counts < THRESH
    nb = len(BINS) - 1
    tot = np.zeros((nb, 3)); hit = np.zeros((nb, 3)); ndoc = [[set() for _ in range(3)] for _ in range(nb)]
    pos_all = np.zeros(nb)
    kinds = ["other", "nonlatin", "english_rare"]
    for di, d in enumerate(docs(it, N_STAT)):
        d = d[d < V]
        if len(d) < 60:
            continue
        r = rare[d].astype(np.float64)
        na = nonascii[d].astype(np.float64)
        ra = (rare[d] & alpha[d]).astype(np.float64)
        cr, cn, ca = (np.concatenate([[0], np.cumsum(x)]) for x in (r, na, ra))
        last = {}
        for t in range(len(d) - 1):
            x = int(d[t])
            s = last.get(x)
            last[x] = t
            if t < 50:
                continue
            dens = (cr[t] - cr[t - 50]) / 50.0
            b = min(np.searchsorted(BINS, dens, side="right") - 1, nb - 1)
            pos_all[b] += 1
            if s is None or t - s > 512:
                continue
            nl = (cn[t] - cn[t - 50]) / 50.0
            er = (ca[t] - ca[t - 50]) / max(cr[t] - cr[t - 50], 1)
            k = 1 if nl >= 0.5 else (2 if dens >= 0.25 and er >= 0.8 else 0)
            tot[b, k] += 1
            hit[b, k] += d[t + 1] == d[s + 1]
            ndoc[b][k].add(di)
    out = {"bins": BINS, "threshold": THRESH, "n_count_tokens": N_COUNT, "n_stat_tokens": N_STAT,
           "positions_per_bin": pos_all.tolist(), "rows": [], "seconds": round(time.time() - t0)}
    for b in range(nb):
        row = {"density": BINS[b:b + 2], "positions": int(pos_all[b])}
        for k, name in enumerate(kinds):
            n = tot[b, k]
            row[name] = {"n": int(n), "docs": len(ndoc[b][k]), "hit": float(hit[b, k] / n) if n else None}
        out["rows"].append(row)
        print(row, flush=True)
    (mc.RESULTS / "e08" / "data_support_large.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
