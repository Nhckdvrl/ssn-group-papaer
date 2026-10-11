"""CT03 Stage C0 evaluation -- metrics A / B / C from docs/E03_C0_DESIGN.md.

A  credit alignment : corr(s_j - s_i, -dL_exact) on held-out hard tokens
B  route regret     : R = L(S) - min_{S' in N(S)} L(S'), recomputed on the NEW route
C  no collapse      : route overlap, expert load, routing entropy, held-out CE

Evaluates several router checkpoints in ONE model load (the load is ~10 min).
"""

import argparse, json, math, random, sys
import numpy as np
import torch
import torch.nn.functional as F
from datasets import load_dataset

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from e02_qwen import Capture, load, route_of, swap_dh, replay_ce
from e03_ccd import TRAIN_LAYERS, pick_problems
from e01_report import spearman


def eval_router(model, tok, probs, K, m, n_tok, base_w, seed, tag):
    dev0 = next(model.parameters()).device
    rows, per_tok, ces = [], [], []
    load_hist = {l: np.zeros(model.config.num_experts) for l in TRAIN_LAYERS}
    for qi, p_ids, s_ids in probs:
        ids = p_ids + s_ids
        input_ids = torch.tensor([ids], device=dev0)
        targets = input_ids[0, 1:]
        first = len(p_ids) - 1
        with Capture(model, TRAIN_LAYERS) as cap:
            with torch.no_grad():
                logits = model(input_ids).logits
                ce = F.cross_entropy(logits[0, :-1].float(),
                                     targets.to(logits.device), reduction="none")
            x_all = {l: cap.mlp_in[l].detach() for l in TRAIN_LAYERS}
            h_all = {l: cap.mlp_out[l].detach() for l in TRAIN_LAYERS}
            lo_all = {l: cap.layer_out[l].detach() for l in TRAIN_LAYERS}
            akw = cap.attn_kwargs
        ces.append(float(ce[first:].mean()))
        order = torch.argsort(ce[first:])
        q = max(1, len(order) // 4)
        rng = random.Random(seed * 7919 + qi)
        toks = [first + int(i) for i in rng.sample(order[-q:].tolist(), min(n_tok, q))]

        for li, l in enumerate(TRAIN_LAYERS):
            moe = model.model.layers[l].mlp
            for t in toks:
                x, h = x_all[l][0, t], h_all[l][0, t]
                p, rank, sel, Z = route_of(moe, x, K)
                cand = rank[K:K + m].tolist()
                load_hist[l][sel] += 1
                s = moe.gate(x).float()
                s_base = F.linear(x, base_w[li]).float()
                sel_base = torch.argsort(s_base, descending=True)[:K].tolist()
                overlap = len(set(sel) & set(sel_base)) / K
                ent = float(-(p * (p + 1e-12).log()).sum())

                pairs, dhs = [], []
                for i in sel:
                    for j in cand:
                        d, _ = swap_dh(moe, x, h, p, i, j, Z)
                        pairs.append((i, j)); dhs.append(d)

                # Top-k is a discrete boundary: the router can reorder a lot
                # without any candidate actually crossing into the routed set.
                # Extra row = revert the REALISED route to what the base router
                # would pick at this same state. dL_revert > 0 means the
                # crossing the trained router performed actually helped.
                crossed = [e for e in sel if e not in sel_base]
                dropped = [e for e in sel_base if e not in sel]
                h_base = None
                if crossed:
                    Zb = float(p[sel_base].sum())
                    with torch.no_grad():
                        h_base = sum(moe.experts[e](x) * (float(p[e]) / Zb)
                                     for e in sel_base)
                    dhs.append(h_base - h)
                dhs = torch.stack(dhs)
                H = lo_all[l].expand(len(dhs) + 1, -1, -1).clone()
                H[1:, t] += dhs
                all_ce = replay_ce(model, l, H, t, targets, **akw)
                dL_all = (all_ce[1:] - all_ce[0]).sum(dim=1).cpu().numpy()
                if crossed:
                    dL_revert = float(dL_all[-1]); dL = dL_all[:-1]
                else:
                    dL_revert = float("nan"); dL = dL_all
                margin = float(s[sel[-1]] - s[cand[0]])

                sd = np.array([float(s[j] - s[i]) for i, j in pairs])
                rho = spearman(sd, -dL)
                regret = float(max(0.0, -dL.min()))
                per_tok.append(dict(q=qi, layer=l, pos=t, rho=rho, regret=regret,
                                    overlap=overlap, entropy=ent,
                                    margin_boundary=margin,
                                    n_crossed=len(crossed), dL_revert=dL_revert,
                                    frac_benef=float((dL < 0).mean())))
                for (i, j), sv, dv in zip(pairs, sd, dL):
                    rows.append(dict(q=qi, layer=l, pos=t, i=i, j=j,
                                     s_diff=float(sv), dL=float(dv)))
        del x_all, h_all, lo_all
        torch.cuda.empty_cache()
        print(f"  [{tag}] done q={qi}", flush=True)

    out = {"tag": tag, "holdout_ce": float(np.mean(ces)), "per_layer": {}}
    for l in TRAIN_LAYERS:
        pt = [r for r in per_tok if r["layer"] == l]
        rr = [r["rho"] for r in pt if not math.isnan(r["rho"])]
        hist = load_hist[l] / max(load_hist[l].sum(), 1)
        nz = hist[hist > 0]
        out["per_layer"][str(l)] = dict(
            n_tokens=len(pt),
            A_rho_median=float(np.median(rr)) if rr else float("nan"),
            A_rho_pooled=spearman([r["s_diff"] for r in rows if r["layer"] == l],
                                  [-r["dL"] for r in rows if r["layer"] == l]),
            B_regret_mean=float(np.mean([r["regret"] for r in pt])),
            B_regret_median=float(np.median([r["regret"] for r in pt])),
            C_route_overlap=float(np.mean([r["overlap"] for r in pt])),
            C_router_entropy=float(np.mean([r["entropy"] for r in pt])),
            C_expert_load_entropy=float(-(nz * np.log(nz)).sum()),
            frac_beneficial=float(np.mean([r["frac_benef"] for r in pt])),
            D_margin_boundary=float(np.mean([r["margin_boundary"] for r in pt])),
            D_frac_tokens_crossed=float(np.mean([r["n_crossed"] > 0 for r in pt])),
            D_mean_n_crossed=float(np.mean([r["n_crossed"] for r in pt])),
            D_dL_revert_mean=(float(np.mean([r["dL_revert"] for r in pt
                                             if not math.isnan(r["dL_revert"])]))
                              if any(not math.isnan(r["dL_revert"]) for r in pt)
                              else float("nan")),
            D_frac_crossings_helped=(
                float(np.mean([r["dL_revert"] > 0 for r in pt
                               if not math.isnan(r["dL_revert"])]))
                if any(not math.isnan(r["dL_revert"]) for r in pt)
                else float("nan")))
    return out, rows


def main(a):
    tok, model = load(a)
    K = model.config.num_experts_per_tok
    ds = load_dataset("HuggingFaceH4/MATH-500", split="test")
    holdout, _ = pick_problems(ds, tok, a.seed, a.max_len, a.min_sol,
                               a.n_holdout, a.n_train)
    frozen = json.load(open(a.holdout_ref)) if a.holdout_ref else None
    if frozen is not None:
        assert [q for q, _, _ in holdout] == frozen, "held-out split drifted"
    print(f"held-out: {[q for q,_,_ in holdout]}", flush=True)

    gates = [model.model.layers[l].mlp.gate for l in TRAIN_LAYERS]
    base_w = [gt.weight.detach().clone() for gt in gates]

    results = []
    for spec in a.ckpts.split(","):
        tag = spec.split(":")[0]
        if tag.startswith("temp"):
            # CONTROL: pure logit-temperature on the BASE router, no training.
            # The CF loss has a degenerate optimum at s_i == s_j, and training
            # compressed the selection margin ~45%. If simply flattening the
            # base router reproduces the CE gain, the gain is a temperature
            # effect, not counterfactual credit.
            T = json.load(open("results/c0_implied_temperature.json"))
            for l, gt, bw in zip(TRAIN_LAYERS, gates, base_w):
                gt.weight.data.copy_((bw / T[str(l)]).to(gt.weight.device))
        elif tag != "base":
            sd = torch.load(spec.split(":", 1)[1], map_location="cpu")
            for l, gt in zip(TRAIN_LAYERS, gates):
                gt.weight.data.copy_(sd[str(l)].to(gt.weight.device))
        else:
            for gt, bw in zip(gates, base_w):
                gt.weight.data.copy_(bw)
        with torch.no_grad():
            r, rows = eval_router(model, tok, holdout, K, a.m, a.n_tok,
                                  base_w, a.seed, tag)
        results.append(r)
        with open(f"results/c0_eval_{tag}_pairs.jsonl", "w") as f:
            for x in rows:
                f.write(json.dumps(x) + "\n")
        print(json.dumps(r, indent=1), flush=True)

    json.dump(results, open(a.out, "w"), indent=1)
    print("\n" + "=" * 74)
    print(f"{'layer':>6}{'arm':>12}{'A rho_med':>11}{'B regret':>11}"
          f"{'C overlap':>10}{'CE':>9}{'D margin':>10}{'D xover':>9}"
          f"{'D helped':>10}")
    for r in results:
        for l in TRAIN_LAYERS:
            c = r["per_layer"][str(l)]
            print(f"{l:>6}{r['tag']:>12}{c['A_rho_median']:>11.3f}"
                  f"{c['B_regret_mean']:>11.4f}{c['C_route_overlap']:>10.3f}"
                  f"{r['holdout_ce']:>9.4f}{c['D_margin_boundary']:>10.4f}"
                  f"{c['D_frac_tokens_crossed']:>9.3f}"
                  f"{c['D_frac_crossings_helped']:>10.3f}")
    print(f"\nwrote {a.out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpts", default="base")
    ap.add_argument("--out", default="results/c0_eval.json")
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
