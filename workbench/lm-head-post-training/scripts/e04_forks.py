"""E04-A3: what does the post-trained model choose differently at forking positions?

On the same sampled positions as e04_local_tau.py, keep positions whose mean entropy (H0+H1)/2 ≥ --hmin and where
argmax p1 ≠ argmax p0. Report the rank of the child's argmax under the parent (1 = same, 2, 3, 4-10, >10), the parent
probability of the child's choice, and the most frequent (parent top-1 → child top-1) token pairs, so we can tell
re-ranking among the parent's own candidates from genuinely new choices, and formatting from content.

Usage: python e04_forks.py <pair_key> [--sources gen_child,gen_parent] [--hmin 0.5]
"""
import argparse
import collections
import json
from pathlib import Path

import numpy as np
import torch

import models
from e04_fit import chunks, hidden, load_sources

ROOT = Path(__file__).resolve().parents[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pair")
    ap.add_argument("--sources", default="gen_child,gen_parent")
    ap.add_argument("--max_pos", type=int, default=30000)
    ap.add_argument("--hmin", type=float, default=0.5)
    args = ap.parse_args()
    dev = "cuda"
    torch.backends.cuda.matmul.allow_tf32 = True
    p0, p1, stage = models.PAIRS[args.pair]
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(models.path(p1))
    srcs = load_sources(args.pair, args.sources.split(","), tok)
    rng = np.random.default_rng(1)
    sel = {s: [torch.tensor(np.sort(rng.choice(len(ids) - first, size=max(1, int(round((len(ids) - first) * min(1.0, args.max_pos / max(1, sum(len(i) - f for _, i, f in seqs)))))), replace=False)))
               for _, ids, first in seqs] for s, seqs in srcs.items()}
    H0s, W0 = hidden(p0, srcs, dev, sel)
    H1s, W1 = hidden(p1, srcs, dev, sel)
    res = {"pair": args.pair, "stage": stage, "hmin": args.hmin, "sources": {}}
    for s in srcs:
        ranks, pchild, pairs, n_fork = [], [], collections.Counter(), 0
        for sl in chunks(H0s[s].shape[0], 2048):
            z0 = H0s[s][sl].float() @ W0.T; z1 = H1s[s][sl].float() @ W1.T
            lp0 = torch.log_softmax(z0, -1); lp1 = torch.log_softmax(z1, -1)
            H0 = -(lp0.exp() * lp0).sum(-1); H1 = -(lp1.exp() * lp1).sum(-1)
            fork = (H0 + H1) / 2 >= args.hmin
            a0, a1 = lp0.argmax(-1), lp1.argmax(-1)
            n_fork += int(fork.sum())
            m = fork & (a0 != a1)
            if m.any():
                r = (lp0[m] > lp0[m].gather(1, a1[m][:, None])).sum(-1) + 1
                ranks.append(r.cpu()); pchild.append(lp0[m].gather(1, a1[m][:, None]).squeeze(1).exp().cpu())
                for x, y in zip(a0[m].tolist(), a1[m].tolist()):
                    pairs[(x, y)] += 1
        r = torch.cat(ranks).numpy() if ranks else np.array([]); pc = torch.cat(pchild).numpy() if pchild else np.array([])
        dec = lambda i: tok.convert_ids_to_tokens(int(i)) if i < len(tok) else f"<pad{i}>"
        res["sources"][s] = {"n_fork": n_fork, "n_changed": int(len(r)), "frac_changed": float(len(r) / max(1, n_fork)),
                             "rank_hist": {"2": float((r == 2).mean()), "3": float((r == 3).mean()), "4-10": float(((r >= 4) & (r <= 10)).mean()),
                                           ">10": float((r > 10).mean())},
                             "median_parent_prob_of_child_choice": float(np.median(pc)) if len(pc) else None,
                             "top_pairs": [(dec(x), dec(y), c) for (x, y), c in pairs.most_common(40)]}
        print(s, {k: v for k, v in res["sources"][s].items() if k != "top_pairs"}, flush=True)
        print("   ", res["sources"][s]["top_pairs"][:25], flush=True)
    out = ROOT / "results" / "e04"; out.mkdir(parents=True, exist_ok=True)
    (out / f"forks_{args.pair}.json").write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
