"""CT03 E03.6 -- does the PROXY potential match the EXACT potential?

E03.5 showed exact utilities project cleanly onto per-expert potentials. But
training never sees exact utilities; it sees the proxy. Substituting one for the
other is not allowed without measuring it, so this compares

    z*_proxy = Project( g^T dh_ij )        vs        z*_exact = Project( -dL_ij )

on the SAME tokens and the SAME 32 base pairs used in E03.1/C0.

Stage 1 (GPU, one forward+backward per problem, NO replays) writes the proxy for
those pairs. Stage 2 (CPU) joins with the exact values already measured in
results/c0_eval_base_pairs.jsonl and compares the two potentials.
"""

import argparse, json, random, sys
from collections import defaultdict
import numpy as np
import torch
import torch.nn.functional as F
from datasets import load_dataset

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from e02_qwen import Capture, load, route_of, swap_dh
from e03_ccd import TRAIN_LAYERS, pick_problems
from e035_integrability import fit_potentials
from e01_report import spearman


def compute_proxy(a):
    tok, model = load(a)
    K = model.config.num_experts_per_tok
    ds = load_dataset("HuggingFaceH4/MATH-500", split="test")
    holdout, _ = pick_problems(ds, tok, a.seed, a.max_len, a.min_sol,
                               a.n_holdout, a.n_train)
    assert [q for q, _, _ in holdout] == json.load(open(a.holdout_ref))
    dev0 = next(model.parameters()).device
    out = open(a.proxy_out, "w")

    for qi, p_ids, s_ids in holdout:
        ids = p_ids + s_ids
        input_ids = torch.tensor([ids], device=dev0)
        targets = input_ids[0, 1:]
        first = len(p_ids) - 1
        with Capture(model, TRAIN_LAYERS) as cap:
            with torch.enable_grad():
                emb = model.model.embed_tokens(input_ids).detach().requires_grad_(True)
                lg = model(inputs_embeds=emb, use_cache=False).logits
                ce = F.cross_entropy(lg[0, :-1].float(),
                                     targets.to(lg.device), reduction="none")
                ce[first:].sum().backward()
        base_ce = ce.detach()
        g = {l: cap.mlp_out[l].grad[0].detach().clone() for l in TRAIN_LAYERS}
        x_all = {l: cap.mlp_in[l].detach() for l in TRAIN_LAYERS}
        h_all = {l: cap.mlp_out[l].detach() for l in TRAIN_LAYERS}
        del lg, ce, emb, cap
        torch.cuda.empty_cache()

        order = torch.argsort(base_ce[first:])
        qn = max(1, len(order) // 4)
        rng = random.Random(a.seed * 7919 + qi)
        toks = [first + int(i) for i in rng.sample(order[-qn:].tolist(),
                                                   min(a.n_tok, qn))]
        for l in TRAIN_LAYERS:
            moe = model.model.layers[l].mlp
            for t in toks:
                x, h = x_all[l][0, t], h_all[l][0, t]
                p, rank, sel, Z = route_of(moe, x, K)
                cand = rank[K:K + a.m].tolist()
                gv = g[l][t].float()
                with torch.no_grad():
                    for i in sel:
                        for j in cand:
                            d, _ = swap_dh(moe, x, h, p, i, j, Z)
                            out.write(json.dumps(dict(
                                q=qi, layer=l, pos=t, i=i, j=j,
                                px=float(gv @ d.float()))) + "\n")
        del g, x_all, h_all
        torch.cuda.empty_cache()
        print(f"  proxy done q={qi}", flush=True)
    out.close()


def analyse(a):
    prox = defaultdict(dict)
    for r in map(json.loads, open(a.proxy_out)):
        prox[(r["q"], r["layer"], r["pos"])][(r["i"], r["j"])] = -r["px"]   # u_hat
    exact = defaultdict(dict)
    for r in map(json.loads, open(a.exact_in)):
        exact[(r["q"], r["layer"], r["pos"])][(r["i"], r["j"])] = -r["dL"]  # u
    keys = [k for k in prox if k in exact and len(prox[k]) >= 8
            and set(prox[k]) == set(exact[k])]
    print(f"matched tokens: {len(keys)} (proxy {len(prox)}, exact {len(exact)})")

    per = defaultdict(list)
    for k in keys:
        pr = [(i, j, prox[k][(i, j)]) for (i, j) in prox[k]]
        ex = [(i, j, exact[k][(i, j)]) for (i, j) in prox[k]]
        zp, idxp, r2p, _, uh = fit_potentials(pr)
        ze, idxe, r2e, _, ue = fit_potentials(ex)
        order = sorted(idxe)
        vp = np.array([zp[idxp[e]] for e in order])
        ve = np.array([ze[idxe[e]] for e in order])
        # best candidate = the j with the highest exact potential among candidates
        js = sorted({j for _, j, _ in ex})
        bp = max(js, key=lambda e: vp[order.index(e)])
        be = max(js, key=lambda e: ve[order.index(e)])
        per[k[1]].append(dict(
            rho_pair=spearman([x[2] for x in pr], [x[2] for x in ex]),
            rho_z=spearman(vp, ve), r2_proxy=r2p, r2_exact=r2e,
            top1=float(bp == be),
            top4_ov=len(set(sorted(order, key=lambda e: -vp[order.index(e)])[:4])
                        & set(sorted(order, key=lambda e: -ve[order.index(e)])[:4])) / 4,
            sign=float(np.mean(np.sign(vp - vp.mean()) == np.sign(ve - ve.mean())))))

    print("\nDoes projection preserve -- or denoise -- the proxy?")
    print(f"{'layer':>6}{'n':>6}{'rho pairwise':>14}{'rho potential':>15}"
          f"{'gain':>8}{'R2 proxy':>10}{'best-cand':>11}{'top4 ovl':>10}")
    res = {}
    for l in sorted(per):
        v = per[l]
        g_ = lambda k: float(np.median([x[k] for x in v]))
        row = dict(n=len(v), rho_pair=g_("rho_pair"), rho_z=g_("rho_z"),
                   r2_proxy=g_("r2_proxy"), r2_exact=g_("r2_exact"),
                   top1=float(np.mean([x["top1"] for x in v])),
                   top4=float(np.mean([x["top4_ov"] for x in v])))
        row["gain"] = row["rho_z"] - row["rho_pair"]
        res[str(l)] = row
        print(f"{l:>6}{row['n']:>6}{row['rho_pair']:>14.3f}{row['rho_z']:>15.3f}"
              f"{row['gain']:>+8.3f}{row['r2_proxy']:>10.3f}"
              f"{row['top1']:>11.3f}{row['top4']:>10.3f}")
    json.dump(res, open("results/e036_potential.json", "w"), indent=1)
    print("\nwrote results/e036_potential.json")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", default="both", choices=["proxy", "analyse", "both"])
    ap.add_argument("--proxy-out", dest="proxy_out", default="results/e036_proxy.jsonl")
    ap.add_argument("--exact-in", dest="exact_in", default="results/c0_eval_base_pairs.jsonl")
    ap.add_argument("--holdout-ref", dest="holdout_ref", default="results/c0_holdout.json")
    ap.add_argument("--m", type=int, default=4)
    ap.add_argument("--n-tok", dest="n_tok", type=int, default=8)
    ap.add_argument("--n-holdout", dest="n_holdout", type=int, default=16)
    ap.add_argument("--n-train", dest="n_train", type=int, default=420)
    ap.add_argument("--max-len", dest="max_len", type=int, default=512)
    ap.add_argument("--min-sol", dest="min_sol", type=int, default=64)
    ap.add_argument("--n-gpu", dest="n_gpu", type=int, default=2)
    ap.add_argument("--mem-per-gpu", dest="mem_per_gpu", type=int, default=78)
    ap.add_argument("--seed", type=int, default=0)
    A = ap.parse_args()
    if A.stage in ("proxy", "both"):
        compute_proxy(A)
    if A.stage in ("analyse", "both"):
        analyse(A)
