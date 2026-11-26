"""E04-A4: does post-training thin the TAIL at forking positions while leaving the head of the distribution flat?

E05 showed that, at entropy-defined forks, which of the top candidates is taken barely matters for success under the
parent's continuation; E04-D showed that removing sampling randomness at forks recovers most of the gain. Hypothesis:
post-training suppresses low-probability tail tokens at forks (what min-p / mode-picking do) rather than sharpening the
top. On the same sampled positions as e04_local_tau.py, per mean-entropy bucket report for parent and child:
  mass outside own top-1 / top-3 / top-10,  'min-p tail' mass (tokens with p < 0.1·p_max),
  entropy of the top-10 renormalised (head flatness), and the child's mass on tokens in the PARENT's tail
  (parent p < 0.1·parent p_max) vs the parent's own mass there.

Usage: python e04_tail.py <pair_key> [--sources gen_child,gen_parent]
"""
import argparse
import json
from pathlib import Path

import numpy as np
import torch

import models
from e04_fit import chunks, hidden, load_sources

ROOT = Path(__file__).resolve().parents[1]
BINS = [0, 0.1, 0.5, 1.0, 2.0, 4.0, 99]


@torch.no_grad()
def stats(z):
    lp = torch.log_softmax(z, -1); p = lp.exp()
    H = -(p * lp).sum(-1)
    srt = torch.sort(p, -1, descending=True).values
    top10 = srt[:, :10] / srt[:, :10].sum(-1, keepdim=True)
    return {"H": H, "out1": 1 - srt[:, 0], "out3": 1 - srt[:, :3].sum(-1), "out10": 1 - srt[:, :10].sum(-1),
            "minp_tail": (p * (p < 0.1 * srt[:, :1])).sum(-1), "head_H10": -(top10 * top10.clamp_min(1e-30).log()).sum(-1), "p": p}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pair")
    ap.add_argument("--sources", default="gen_child,gen_parent")
    ap.add_argument("--max_pos", type=int, default=30000)
    args = ap.parse_args()
    dev = "cuda"
    torch.backends.cuda.matmul.allow_tf32 = True
    p0, p1, stage = models.PAIRS[args.pair]
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(models.path(p1))
    srcs = load_sources(args.pair, args.sources.split(","), tok)
    rng = np.random.default_rng(1)
    sel = {}
    for s, seqs in srcs.items():
        npos = [len(ids) - first for _, ids, first in seqs]
        frac = min(1.0, args.max_pos / max(1, sum(npos)))
        sel[s] = [torch.tensor(np.sort(rng.choice(m, size=max(1, int(round(m * frac))), replace=False))) for m in npos]
    H0s, W0 = hidden(p0, srcs, dev, sel)
    H1s, W1 = hidden(p1, srcs, dev, sel)
    res = {"pair": args.pair, "stage": stage, "sources": {}}
    keys = ("out1", "out3", "out10", "minp_tail", "head_H10")
    for s in srcs:
        cols = {f"{k}{w}": [] for k in keys for w in ("0", "1")}
        cols.update({"Hm": [], "child_mass_on_parent_tail": [], "parent_mass_on_parent_tail": []})
        for sl in chunks(H0s[s].shape[0], 1024):
            a = stats(H0s[s][sl].float() @ W0.T); b = stats(H1s[s][sl].float() @ W1.T)
            for k in keys:
                cols[f"{k}0"].append(a[k].cpu()); cols[f"{k}1"].append(b[k].cpu())
            cols["Hm"].append(((a["H"] + b["H"]) / 2).cpu())
            ptail = a["p"] < 0.1 * a["p"].max(-1, keepdim=True).values
            cols["child_mass_on_parent_tail"].append((b["p"] * ptail).sum(-1).cpu())
            cols["parent_mass_on_parent_tail"].append((a["p"] * ptail).sum(-1).cpu())
        c = {k: torch.cat(v).numpy() for k, v in cols.items()}
        rows = []
        for lo, hi in zip(BINS[:-1], BINS[1:]):
            m = (c["Hm"] >= lo) & (c["Hm"] < hi)
            if m.sum() < 20:
                continue
            row = {"Hmean": [lo, hi], "n": int(m.sum())}
            for k in keys:
                row[k] = [float(c[f"{k}0"][m].mean()), float(c[f"{k}1"][m].mean())]
            row["mass_on_parent_tail"] = [float(c["parent_mass_on_parent_tail"][m].mean()), float(c["child_mass_on_parent_tail"][m].mean())]
            rows.append(row)
        res["sources"][s] = rows
        print(s, flush=True)
        for r_ in rows:
            print("   ", json.dumps(r_), flush=True)
    out = ROOT / "results" / "e04"; out.mkdir(parents=True, exist_ok=True)
    (out / f"tail_{args.pair}.json").write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
