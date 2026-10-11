"""E09: E06 stimulus classes + E07 density sweep + per-layer forward shift on the rare class, any Pythia size.

Usage: e09_gate_scale.py --repo EleutherAI/pythia-160m-seed3 --step 64000 -> results/e09/<model>__step<N>.json
"""
import argparse
import json
import os
import time

import torch

import mp_common as mc
import e01_induction as e
import e02_population as p2
import e04_ctx_gating as p4
import e06_gate_keys as p6
import e07_mixing as p7

OUT = mc.RESULTS / os.environ.get("EXP", "e09")  # run_queue.sh exports EXP


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
    bos = model.tokenizer.bos_token_id
    counts = torch.load(p2.COUNTS)
    L = model.cfg.n_layers
    res = {"repo": args.repo, "step": args.step, "protocol": "experiments/E09-gate-at-160m.md", "classes": {}, "p": {}}
    stim = p6.stimuli(pile, bos, counts)
    for name, toks in stim.items():
        _, s = p6.per_seq(model, toks)
        res["classes"][name] = float(s.mean())
    for p, (toks, mask) in p7.build(pile, bos, counts).items():
        lv = e.loss_at(model, toks, e.R3_POS, bs=125)[:, 49:]
        tm = mask[:, 1:50]
        res["p"][str(p)] = {k: (float(lv[m].median()) if m.any() else None) for k, m in (("R", tm), ("N", ~tm))}
    est_r, est_n = p2.repeated(p2.token_pool(), bos, seed=12345), p4.nat_rep(pile, bos, 0, 500)
    mu_r, mu_n = p4.z_means(model, est_r, range(L)), p4.z_means(model, est_n, range(L))
    lo = stim["S6_lo"]
    res["layer_fwd_S6"] = {l: float(p6.per_seq(model, lo, p4.shift_hooks([l], mu_r, mu_n))[1].mean()) for l in range(L)}
    res["seconds"] = round(time.time() - t0, 1)
    tag = f"{args.repo.split('/')[-1]}__step{args.step}"
    (OUT / f"{tag}.json").write_text(json.dumps(res, indent=1))
    bl = min(res["layer_fwd_S6"], key=res["layer_fwd_S6"].get)
    print(tag, {k[3:]: round(v, 2) for k, v in res["classes"].items()}, "p:", {p: (r["R"] and round(r["R"], 2)) for p, r in res["p"].items()},
          f"best-layer L{bl} {res['layer_fwd_S6'][bl]:.2f} ({res['seconds']}s)", flush=True)


if __name__ == "__main__":
    main()
