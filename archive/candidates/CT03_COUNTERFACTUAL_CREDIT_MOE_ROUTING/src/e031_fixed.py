"""CT03 E03.1 -- fixed-support re-evaluation of the C0 checkpoints. No training.

C0's A/B/D were measured on each arm's OWN tokens, OWN route and OWN candidate
set, so they were never matched comparisons. E03.1 fixes every one of those:

  * hard token positions come from the BASE model only;
  * hidden states x_l are the BASE model's;
  * the candidate universe U = S_base u C_base is fixed;
  * the exact utilities u_ij are computed ONCE, on the base state.

Each arm's router is then scored as a FUNCTION on that frozen support.

  A_fixed  rho( s_j^arm - s_i^arm , u_ij^exact )  over the same 32 base pairs
  V_arm    L(S_arm ; x_base) - L(S_base ; x_base)    negative = genuinely better
  capture  V_arm / (L(S_base) - min_{1-swap in U} L)  share of visible headroom

S_arm is the arm's top-8 within U. Two variants are replayed, because mixing
weights and expert identity are different claims:
  route_armw : arm's experts, arm's renormalised weights (deployment-faithful)
  route_basew: arm's experts, base router's weights      (isolates selection)
"""

import argparse, json, random, sys
import numpy as np
import torch
import torch.nn.functional as F
from datasets import load_dataset

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from e02_qwen import Capture, load, replay_ce
from e03_ccd import TRAIN_LAYERS, pick_problems
from e01_report import spearman


def mix(moe, x, ids, p):
    Z = float(p[ids].sum())
    return sum(moe.experts[e](x) * (float(p[e]) / Z) for e in ids)


def main(a):
    tok, model = load(a)
    K = model.config.num_experts_per_tok
    ds = load_dataset("HuggingFaceH4/MATH-500", split="test")
    holdout, _ = pick_problems(ds, tok, a.seed, a.max_len, a.min_sol,
                               a.n_holdout, a.n_train)
    assert [q for q, _, _ in holdout] == json.load(open(a.holdout_ref))
    dev0 = next(model.parameters()).device

    gates = [model.model.layers[l].mlp.gate for l in TRAIN_LAYERS]
    base_w = [g.weight.detach().clone() for g in gates]
    arms = {"base": base_w}
    for spec in a.ckpts.split(","):
        if not spec:
            continue
        tag, path = spec.split(":", 1)
        sd = torch.load(path, map_location="cpu")
        arms[tag] = [sd[str(l)].to(base_w[0].device) for l in TRAIN_LAYERS]
    print("arms:", list(arms), flush=True)

    rows, ce_rows = [], []
    for qi, p_ids, s_ids in holdout:
        ids = p_ids + s_ids
        input_ids = torch.tensor([ids], device=dev0)
        targets = input_ids[0, 1:]
        first = len(p_ids) - 1
        # ---- BASE forward defines the entire support ----
        for g, bw in zip(gates, base_w):
            g.weight.data.copy_(bw)
        with Capture(model, TRAIN_LAYERS) as cap:
            with torch.no_grad():
                lg = model(input_ids).logits
                ce = F.cross_entropy(lg[0, :-1].float(),
                                     targets.to(lg.device), reduction="none")
            x_all = {l: cap.mlp_in[l].detach() for l in TRAIN_LAYERS}
            h_all = {l: cap.mlp_out[l].detach() for l in TRAIN_LAYERS}
            lo_all = {l: cap.layer_out[l].detach() for l in TRAIN_LAYERS}
            akw = cap.attn_kwargs
        ce_rows.append(dict(q=qi, arm="base_state_ce", ce=float(ce[first:].mean())))
        order = torch.argsort(ce[first:])
        qn = max(1, len(order) // 4)
        rng = random.Random(a.seed * 7919 + qi)
        toks = [first + int(i) for i in rng.sample(order[-qn:].tolist(),
                                                   min(a.n_tok, qn))]

        for li, l in enumerate(TRAIN_LAYERS):
            moe = model.model.layers[l].mlp
            for t in toks:
                x, h = x_all[l][0, t], h_all[l][0, t]
                p_base = F.softmax(F.linear(x, base_w[li]).float(), -1)
                rank = torch.argsort(p_base, descending=True)
                S_base = rank[:K].tolist()
                C_base = rank[K:K + a.m].tolist()
                U = S_base + C_base

                patches, meta = [], []
                for i in S_base:                       # the 32 fixed one-swaps
                    for j in C_base:
                        ids2 = [e for e in S_base if e != i] + [j]
                        patches.append(mix(moe, x, ids2, p_base) - h)
                        meta.append(("swap", i, j))
                arm_sel = {}
                for tag, W in arms.items():
                    s = F.linear(x, W[li]).float()
                    sU = sorted(U, key=lambda e: -float(s[e]))[:K]
                    arm_sel[tag] = (s, sU)
                    if tag == "base":
                        continue
                    p_arm = F.softmax(s, -1)
                    patches.append(mix(moe, x, sU, p_arm) - h)
                    meta.append(("route_armw", tag, None))
                    patches.append(mix(moe, x, sU, p_base) - h)
                    meta.append(("route_basew", tag, None))

                P = torch.stack(patches)
                H = lo_all[l].expand(len(P) + 1, -1, -1).clone()
                H[1:, t] += P
                allce = replay_ce(model, l, H, t, targets, **akw)
                dL = (allce[1:] - allce[0]).sum(dim=1).cpu().numpy()

                swaps = {(m[1], m[2]): float(v)
                         for m, v in zip(meta, dL) if m[0] == "swap"}
                best1 = min(swaps.values())
                for m, v in zip(meta, dL):
                    if m[0] != "swap":
                        rows.append(dict(q=qi, layer=l, pos=t, kind=m[0], arm=m[1],
                                         dL_route=float(v), best_1swap=best1,
                                         n_changed=len(set(arm_sel[m[1]][1])
                                                       - set(S_base))))
                for tag, (s, sU) in arm_sel.items():
                    sd_ = [float(s[j] - s[i]) for (i, j) in swaps]
                    ue = [-swaps[(i, j)] for (i, j) in swaps]
                    rows.append(dict(q=qi, layer=l, pos=t, kind="A_fixed", arm=tag,
                                     rho=spearman(sd_, ue),
                                     n_changed=len(set(sU) - set(S_base)),
                                     best_1swap=best1))
        del x_all, h_all, lo_all
        torch.cuda.empty_cache()
        print(f"  done q={qi}", flush=True)

    with open(a.out_rows, "w") as f:
        for r in rows + ce_rows:
            f.write(json.dumps(r) + "\n")

    print("\n" + "=" * 78)
    print("A_fixed -- same 32 base pairs, same base state, for every arm")
    print(f"{'layer':>6}" + "".join(f"{t:>14}" for t in arms))
    for l in TRAIN_LAYERS:
        vals = []
        for t in arms:
            v = [r["rho"] for r in rows if r["kind"] == "A_fixed"
                 and r["arm"] == t and r["layer"] == l and not np.isnan(r["rho"])]
            vals.append(np.median(v) if v else float("nan"))
        print(f"{l:>6}" + "".join(f"{v:>14.3f}" for v in vals))

    print("\nFixed-state route value  dL_route (negative = better than base route)")
    print(f"{'layer':>6}{'variant':>13}" + "".join(f"{t:>14}" for t in arms if t != "base")
          + f"{'best 1-swap':>14}")
    for l in TRAIN_LAYERS:
        b1 = np.median([r["best_1swap"] for r in rows
                        if r["kind"] == "A_fixed" and r["arm"] == "base"
                        and r["layer"] == l])
        for kind in ("route_armw", "route_basew"):
            vals = []
            for t in arms:
                if t == "base":
                    continue
                v = [r["dL_route"] for r in rows if r["kind"] == kind
                     and r["arm"] == t and r["layer"] == l]
                vals.append(np.mean(v) if v else float("nan"))
            print(f"{l:>6}{kind:>13}" + "".join(f"{v:>14.4f}" for v in vals)
                  + f"{b1:>14.4f}")

    print("\nmean experts changed vs base route (out of 8), within fixed U")
    print(f"{'layer':>6}" + "".join(f"{t:>14}" for t in arms))
    for l in TRAIN_LAYERS:
        vals = [np.mean([r["n_changed"] for r in rows if r["kind"] == "A_fixed"
                         and r["arm"] == t and r["layer"] == l]) for t in arms]
        print(f"{l:>6}" + "".join(f"{v:>14.2f}" for v in vals))
    print(f"\nwrote {a.out_rows}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpts", default="cf_only:results/c0_router_cf.pt,"
                                       "shuffled:results/c0_router_shuffled.pt,"
                                       "cf_anchor:results/c0_router_cfanchor.pt")
    ap.add_argument("--out-rows", dest="out_rows", default="results/e031_rows.jsonl")
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
    main(ap.parse_args())
