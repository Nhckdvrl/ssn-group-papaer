"""E24: induction (copy) strength of DataDecide 1B models. Protocol: experiments/E24-*.md.

Usage: e24_induction.py --repo allenai/DataDecide-c4-1B --seed default ; e24_induction.py --analyze
"""
import argparse
import json

import numpy as np
import torch
from scipy.stats import spearmanr

import dd_common as dd
import mp_common as mc

OUT = mc.RESULTS / "e24"
N_SEQ, HALF = 200, 128


@torch.no_grad()
def compute(repo, seed):
    model, tok = dd.load(repo, dd.rev(dd.FINAL_1B, seed), dtype=torch.bfloat16, attn="eager")
    g = torch.Generator().manual_seed(0)
    first = torch.randint(1000, 40000, (N_SEQ, HALF), generator=g)
    ids = torch.cat([torch.full((N_SEQ, 1), tok.eos_token_id), first, first], 1)
    l1, l2, ind = [], [], []
    for i in range(0, N_SEQ, 20):
        x = ids[i:i + 20].to(model.device)
        out = model(x, output_attentions=True)
        lp = out.logits.float().log_softmax(-1)
        nll = -lp[:, :-1].gather(-1, x[:, 1:, None])[..., 0]           # predicts token t+1
        l1.append(nll[:, 1:HALF].mean(1).cpu()); l2.append(nll[:, HALF + 1:].mean(1).cpu())
        q = torch.arange(HALF + 1, 2 * HALF + 1, device=x.device)       # second-pass positions
        k = q - HALF + 1                                                 # token after previous occurrence
        per = [a[:, :, q, k].mean((0, 2)).float().cpu() for a in out.attentions]  # [heads] per layer
        ind.append(torch.stack(per))                                     # [layers, heads]
    l1, l2 = torch.cat(l1), torch.cat(l2)
    S = torch.stack(ind).mean(0)
    res = {"repo": repo, "seed": seed, "loss_first": float(l1.mean()), "loss_second": float(l2.mean()),
           "I1_copy_gain": float((l1 - l2).mean()), "I1_ci95": np.percentile(
               [(l1 - l2)[torch.randint(0, N_SEQ, (N_SEQ,))].mean().item() for _ in range(500)], [2.5, 97.5]).tolist(),
           "I2_max_induction_head": float(S.max()), "I2_argmax": list(np.unravel_index(int(S.argmax()), S.shape)),
           "n_heads_over_0.3": int((S > 0.3).sum())}
    OUT.mkdir(exist_ok=True)
    name = f"{repo.split('DataDecide-')[1]}__{seed}.json"
    (OUT / name).write_text(json.dumps(res, indent=1, default=int))
    print(name, {k: v for k, v in res.items() if k not in ("repo",)}, flush=True)


def analyze():
    from e21_e22_corpus import partial_spearman
    rows = {}
    for f in OUT.glob("*__*.json"):
        r = json.loads(f.read_text())
        e = mc.RESULTS / "e20" / f.name
        if not e.exists():
            continue
        c = json.loads(e.read_text())["conditions"]
        rows[f.stem] = (-r["loss_second"], np.mean([v["margin"] for k, v in c.items() if k.endswith("Substitution Conflict")]),
                        np.mean([v["clean_margin"] for v in c.values()]))
    rec = sorted({k.split("__")[0] for k in rows})
    rec = [r for r in rec if all(f"{r}__{s}" in rows for s in dd.SEEDS)]
    M = np.array([[rows[f"{r}__{s}"] for s in dd.SEEDS] for r in rec])  # [recipe, seed, 3]
    I, A, K = M[..., 0], M[..., 1], M[..., 2]
    out = {"n_recipes": len(rec),
           "recipe_rho_I1_Asub": float(spearmanr(I.mean(1), A.mean(1))[0]),
           "recipe_partial_given_K": partial_spearman(I.mean(1), A.mean(1), [K.mean(1)]),
           "seed_rho_dI1_dAsub": float(spearmanr((I - I.mean(1, keepdims=True)).ravel(),
                                                 (A - A.mean(1, keepdims=True)).ravel())[0])}
    s23 = mc.RESULTS / "e23" / "recipe_stats.json"
    if s23.exists():
        S = json.loads(s23.read_text())
        s1 = np.array([S[r.replace("-1B", "")]["S1"] for r in rec])
        out["S1_Asub"] = float(spearmanr(s1, A.mean(1))[0])
        out["S1_Asub_given_I1"] = partial_spearman(s1, A.mean(1), [I.mean(1)])
        out["S1_I1"] = float(spearmanr(s1, I.mean(1))[0])
    (OUT / "analysis.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo")
    ap.add_argument("--seed", default="default")
    ap.add_argument("--analyze", action="store_true")
    a = ap.parse_args()
    analyze() if a.analyze else compute(a.repo, a.seed)
