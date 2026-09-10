"""E03c — per-step damage under teacher forcing on the model's own trajectory.

E03b rejected the "installed fixed prior" account, so the live question is the one
the candidate package started from: is the collapse of long generation the compounding
of small per-step damage (Account C), or is each step badly damaged (Account A)?

Method.  Take the FULL-readout model's own greedy generation for an item -- the
trajectory it actually takes -- and replay it under the truncated readout with the
gold prefix forced at every step.  At each position t we record whether the truncated
model's arg max still equals the token the full model emitted, the rank and log-prob
it assigns to that token, and the KL from the full model's distribution.

Two quantities decide between the accounts:

  p_bar   mean per-step top-1 agreement.  Account A predicts this is low.
  first divergence position, and whether the observed distribution matches the
          geometric law implied by independent per-step failure at rate (1 - p_bar).

Using the model's own full-readout trajectory rather than a dataset gold CoT avoids
scoring the model against one arbitrary valid solution path.
"""
from __future__ import annotations
import argparse, json, pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from src.readout import ReadoutTruncation, build_mask, mask_id


@torch.no_grad()
def replay(model, tok, prompt, gen_text, mask, max_tokens, device):
    p_ids = tok(prompt, return_tensors="pt")["input_ids"][0]
    g_ids = tok(gen_text, add_special_tokens=False, return_tensors="pt")["input_ids"][0]
    g_ids = g_ids[:max_tokens]
    if len(g_ids) == 0:
        return None
    ids = torch.cat([p_ids, g_ids]).unsqueeze(0).to(device)
    n_p = len(p_ids)

    full = model(input_ids=ids).logits[0, n_p - 1:-1].float()       # L x V
    with ReadoutTruncation(model, mask):
        trunc = model(input_ids=ids).logits[0, n_p - 1:-1].float()

    tgt = g_ids.to(device)
    agree = (trunc.argmax(-1) == full.argmax(-1))                   # vs the full model
    lp_f = torch.log_softmax(full, -1)
    lp_t = torch.log_softmax(trunc, -1)
    kl = (lp_f.exp() * (lp_f - lp_t)).sum(-1)
    rank = (trunc > trunc.gather(1, tgt[:, None])).sum(1)           # rank of emitted token
    fd = int((~agree).nonzero()[0].item()) if (~agree).any() else -1
    return {
        "n_steps": int(len(g_ids)),
        "top1_agree": agree.float().mean().item(),
        "first_divergence": fd,
        "mean_kl": kl.mean().item(),
        "median_rank_of_emitted": int(rank.median().item()),
        "frac_emitted_in_top5": (rank < 5).float().mean().item(),
        "agree_bits": "".join("1" if a else "0" for a in agree.tolist()),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--full-run", required=True,
                    help="results/e01/<model>/<cell>__full.jsonl (its own trajectories)")
    ap.add_argument("--cell", required=True)
    ap.add_argument("--mask", default="first")
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--max-tokens", type=int, default=256)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "run_eval", pathlib.Path(__file__).resolve().parent / "run_eval.py")
    run_eval = importlib.util.module_from_spec(spec); spec.loader.exec_module(run_eval)

    lines = [json.loads(l) for l in open(a.full_run)]
    gens = {r["id"]: r["output"] for r in lines[1:]}
    items = {it["id"]: it for it in run_eval.load_items(a.cell, lines[0]["n_items"], 1234)}

    tok = AutoTokenizer.from_pretrained(a.model)
    if tok.pad_token is None: tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        a.model, dtype=torch.bfloat16, device_map="cuda:0").eval()
    dev = model.lm_head.weight.device
    mask = build_mask(model.config.hidden_size, a.mask, 0.5)

    recs, t0 = [], time.time()
    for i, (iid, g) in enumerate(gens.items()):
        if len(recs) >= a.n: break
        r = replay(model, tok, items[iid]["prompt"], g, mask, a.max_tokens, dev)
        if r: r["id"] = iid; recs.append(r)

    pathlib.Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    header = {"_meta": True, "model": a.model, "cell": a.cell, "mask": a.mask,
              "mask_id": mask_id(mask), "n_items": len(recs),
              "max_tokens": a.max_tokens, "source_run": a.full_run,
              "runtime_s": round(time.time() - t0, 1)}
    with open(a.out, "w") as f:
        f.write(json.dumps(header) + "\n")
        for r in recs: f.write(json.dumps(r) + "\n")
    print("wrote", a.out, header["runtime_s"], "s")


if __name__ == "__main__":
    main()
