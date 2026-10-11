"""E05: random vs natural in-context copying + per-layer distribution-mean shifts, any Pythia size.

Usage: e05_scale_survey.py --repo EleutherAI/pythia-160m-seed3 --step 64000 -> results/e05/<model>__step<N>.json
"""
import argparse
import json
import time

import torch

import mp_common as mc
import e01_induction as e
import e02_population as p2
import e04_ctx_gating as p4

OUT = mc.RESULTS / "e05"


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
    pool = p2.token_pool()
    est_r, est_n = p2.repeated(pool, bos, seed=12345), p4.nat_rep(pile, bos, 0, 500)
    held_r, held_n = p2.repeated(pool, bos, seed=777), p4.nat_rep(pile, bos, 1000, 2000)
    L = model.cfg.n_layers
    mu_r, mu_n = p4.z_means(model, est_r, range(L)), p4.z_means(model, est_n, range(L))

    def beh(toks, hooks=()):
        b = p2.behaviour(model, toks, hooks, bs=125)
        return {k: v for k, v in b.items() if not k.startswith("_")}

    res = {"repo": args.repo, "step": args.step, "n_layers": L, "protocol": "experiments/E05-gating-across-scale.md",
           "clean": {"rand": beh(held_r), "nat": beh(held_n)}, "layer_shift": {}}
    for l in range(L):
        res["layer_shift"][l] = {"fwd_rand": beh(held_r, p4.shift_hooks([l], mu_r, mu_n)),
                                 "rev_nat": beh(held_n, p4.shift_hooks([l], mu_n, mu_r))}
    res["pile_loss_clean"] = float(e.loss_at(model, pile[1000:1500, :505], list(range(1, 504)), bs=10).mean())
    res["seconds"] = round(time.time() - t0, 1)
    tag = f"{args.repo.split('/')[-1]}__step{args.step}"
    (OUT / f"{tag}.json").write_text(json.dumps(res, indent=1))
    c = res["clean"]
    best_f = min(range(L), key=lambda l: res["layer_shift"][l]["fwd_rand"]["CL"])
    worst_r = max(range(L), key=lambda l: res["layer_shift"][l]["rev_nat"]["CL"])
    print(f"{tag}: rand CL {c['rand']['CL']:.2f} nat CL {c['nat']['CL']:.2f} pile {res['pile_loss_clean']:.3f} | "
          f"best fwd L{best_f} {res['layer_shift'][best_f]['fwd_rand']['CL']:.2f} | worst rev L{worst_r} "
          f"{res['layer_shift'][worst_r]['rev_nat']['CL']:.2f} ({res['seconds']}s)", flush=True)


if __name__ == "__main__":
    main()
