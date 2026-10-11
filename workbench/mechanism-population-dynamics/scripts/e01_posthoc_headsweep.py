"""POST-HOC (not in the frozen E01 protocol): single-head causal map on the held-out repeated sequences.

Motivated by E01: on canonical pythia-70m a random set {5.5, 4.1, 2.1} beat the top-3 R1 heads, and
layer-0 heads beat the top R1 head late in training. For every head (48) and method (zero, mean):
  - effect on R3 second-half loss (mean and per-sequence median), first-half loss;
plus per-head previous-token score (Olsson: attention i -> i-1 on Pile text) and the parent R1 score.
Writes results/e01/posthoc_headsweep.json.
"""
import json

import numpy as np
import torch

import mp_common as mc
import e01_induction as e

torch.set_grad_enabled(False)
STEPS = [1000, 8000, 64000, 143000]
REPOS = ["EleutherAI/pythia-70m-deduped", "EleutherAI/pythia-70m"]


def prev_token_score(model, pile):
    L, H = model.cfg.n_layers, model.cfg.n_heads
    _, cache = model.run_with_cache(pile[:64, :256].to(model.cfg.device),
                                    names_filter=lambda n: n.endswith("hook_pattern"))
    out = {}
    for layer in range(L):
        pat = cache["pattern", layer]  # [b, h, q, k]
        diag = pat.diagonal(offset=-1, dim1=-2, dim2=-1)  # attention q -> q-1
        for h in range(H):
            out[f"{layer}.{h}"] = float(diag[:, h].mean())
    return out


def stats(lv):
    f, s = lv[:, :49], lv[:, 49:]
    return {"first_mean": float(f.mean()), "second_mean": float(s.mean()),
            "second_median_of_seq_medians": float(s.median(1).values.median())}


def main():
    res = {}
    for repo in REPOS:
        for step in STEPS:
            model = mc.load_tl_model(repo, step)
            pile, _ = e.pile_eval_set(model)
            rep = e.held_out_repeated(model)
            mz = e.mean_z(model, pile)
            r1 = json.loads((mc.RESULTS / "e01" / f"{repo.split('/')[-1]}__step{step}.json").read_text())["R1"]
            row = {"clean": stats(e.loss_at(model, rep, e.R3_POS)), "prev_token": prev_token_score(model, pile),
                   "R1": r1, "single": {}}
            for layer in range(model.cfg.n_layers):
                for h in range(model.cfg.n_heads):
                    for m in ("zero", "mean"):
                        row["single"][f"{layer}.{h}|{m}"] = stats(
                            e.loss_at(model, rep, e.R3_POS, e.z_hooks([(layer, h)], m, mz)))
            res[f"{repo.split('/')[-1]}@{step}"] = row
            c = row["clean"]["second_mean"]
            top = sorted(row["single"], key=lambda k: -(row["single"][k]["second_mean"] - c))[:6]
            print(repo, step, [(k, round(row["single"][k]["second_mean"] - c, 2), round(r1[k.split('|')[0]], 3),
                                round(row["prev_token"][k.split('|')[0]], 2)) for k in top], flush=True)
    (mc.RESULTS / "e01" / "posthoc_headsweep.json").write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
