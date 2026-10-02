"""E07: rare-token density mixing to separate context-level gating from token-level degeneration.

Usage: e07_mixing.py --repo EleutherAI/pythia-70m-seed2 --step 64000 -> results/e07/<model>__step<N>.json
"""
import argparse
import json
import time

import torch

import mp_common as mc
import e01_induction as e
import e02_population as p2

OUT = mc.RESULTS / "e07"
PS = [0.0, 0.1, 0.25, 0.5, 0.75, 1.0]
N = 500


def build(pile, bos, counts):
    g = torch.Generator().manual_seed(7)
    base = pile[1000:1000 + N, 1:51].clone()
    lo_pool = torch.nonzero((counts >= 10) & (counts < 50)).flatten()
    rare = lo_pool[torch.randint(0, len(lo_pool), (N, 50), generator=g)]
    rank = torch.rand(N, 50, generator=g)  # nested: position replaced iff rank < p
    out = {}
    for p in PS:
        mask = rank < p
        x = torch.where(mask, rare, base)
        out[p] = (torch.cat([torch.full((N, 1), bos), x, x], dim=1), mask)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--step", type=int, required=True)
    args = ap.parse_args()
    torch.set_grad_enabled(False)
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    model = mc.load_tl_model(args.repo, args.step)
    pile, _ = e.pile_eval_set(model)
    counts = torch.load(p2.COUNTS)
    res = {"repo": args.repo, "step": args.step, "protocol": "experiments/E07-gate-vs-degeneration.md", "p": {}}
    for p, (toks, mask) in build(pile, model.tokenizer.bos_token_id, counts).items():
        lv = e.loss_at(model, toks, e.R3_POS, bs=125)[:, 49:]  # second half: predicting x[1..49] (targets x2..x50)
        tmask = mask[:, 1:50]  # target positions in x (x2..x50)
        row = {}
        for name, m in (("R_target", tmask), ("N_target", ~tmask)):
            vals = lv[m]
            row[name] = {"median": float(vals.median()) if len(vals) else None,
                         "mean": float(vals.mean()) if len(vals) else None, "n": int(m.sum())}
        res["p"][str(p)] = row
    res["seconds"] = round(time.time() - t0, 1)
    tag = f"{args.repo.split('/')[-1]}__step{args.step}"
    (OUT / f"{tag}.json").write_text(json.dumps(res, indent=1))
    print(tag, {p: (r["R_target"]["median"] and round(r["R_target"]["median"], 2), r["N_target"]["median"] and round(r["N_target"]["median"], 2))
                for p, r in res["p"].items()}, f"({res['seconds']}s)", flush=True)


if __name__ == "__main__":
    main()
