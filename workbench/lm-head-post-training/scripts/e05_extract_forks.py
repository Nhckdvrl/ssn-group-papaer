"""E05 step 1: extract forking positions from the child's own generations (E04 gen_child contexts).

For every completion position (first --max_gen tokens) compute parent/child next-token distributions; a fork is
mean entropy (H0+H1)/2 ≥ --hmin. Keep 'changed' forks (child top-1 ≠ parent top-1) and 'agree' forks (equal), sample
--n_changed / --n_agree of them stratified over prompts (seed 0), and store the prefix ids and candidates:
  c_base = parent top-1, c_post = child top-1, c_alt = parent rank-3 token (not equal to the other two)
with parent/child log-probs of each, for the rollout step (e05_rollout.py, vLLM env).

Usage: python e05_extract_forks.py <pair_key> [--n_changed 300 --n_agree 100]
"""
import argparse
import json
import random
from pathlib import Path

import torch

import models

OUT = Path("/tmp/xiang_lmhead/e05")


@torch.no_grad()
def dists(name, seqs, dev, max_gen):
    from transformers import AutoModelForCausalLM
    m = AutoModelForCausalLM.from_pretrained(models.path(name), dtype=torch.bfloat16).to(dev).eval()
    out = []
    for prompt_ids, comp in seqs:
        ids = prompt_ids + comp[:max_gen]
        z = m(input_ids=torch.tensor([ids], device=dev)).logits[0, len(prompt_ids) - 1: -1].float()
        lp = torch.log_softmax(z, -1)
        H = -(lp.exp() * lp).sum(-1)
        top = torch.topk(lp, 20, -1)          # cross look-ups are done within the top-20 of each model
        out.append({"H": H.cpu(), "top_ids": top.indices.int().cpu(), "top_lp": top.values.cpu()})
    del m; torch.cuda.empty_cache()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pair")
    ap.add_argument("--n_changed", type=int, default=300)
    ap.add_argument("--n_agree", type=int, default=100)
    ap.add_argument("--hmin", type=float, default=0.5)
    ap.add_argument("--max_gen", type=int, default=1024)
    args = ap.parse_args()
    dev = "cuda"
    p0, p1, _ = models.PAIRS[args.pair]
    rows = [json.loads(l) for l in open(f"/tmp/xiang_lmhead/e04/gen/ctx_{p1}.jsonl")]
    seqs, meta = [], []
    for g in rows:
        for k, c in enumerate(g["completions"]):
            if c["token_ids"]:
                seqs.append((g["prompt_ids"], c["token_ids"])); meta.append((g["index"], k, g["answer"]))
    D0 = dists(p0, seqs, dev, args.max_gen)
    D1 = dists(p1, seqs, dev, args.max_gen)
    changed, agree = [], []
    for si, ((pids, comp), (idx, k, ans), d0, d1) in enumerate(zip(seqs, meta, D0, D1)):
        Hm = (d0["H"] + d1["H"]) / 2
        for t in torch.nonzero(Hm >= args.hmin).flatten().tolist():
            cb, cp = int(d0["top_ids"][t, 0]), int(d1["top_ids"][t, 0])
            alt = [int(x) for x in d0["top_ids"][t] if int(x) not in (cb, cp)]
            look = lambda d, c: next((float(v) for i_, v in zip(d["top_ids"][t].tolist(), d["top_lp"][t].tolist()) if i_ == c), None)
            cs = {cb, cp} | ({alt[0]} if alt else set())
            rec = {"prompt_index": idx, "sample": k, "answer": ans, "t": t, "prefix_ids": pids + comp[:t], "n_prompt": len(pids),
                   "c_base": cb, "c_post": cp, "c_alt": alt[0] if alt else None,
                   "lp0": {c: look(d0, c) for c in cs}, "lp1": {c: look(d1, c) for c in cs},
                   "H0": float(d0["H"][t]), "H1": float(d1["H"][t])}
            (changed if cb != cp else agree).append(rec)
    rng = random.Random(0)

    def strat(pool, n):
        by = {}
        for r in pool:
            by.setdefault(r["prompt_index"], []).append(r)
        for v in by.values():
            rng.shuffle(v)
        keys = sorted(by); rng.shuffle(keys)
        out, i = [], 0
        while len(out) < n and any(by[k] for k in keys):
            k = keys[i % len(keys)]
            if by[k]:
                out.append(by[k].pop())
            i += 1
        return out

    sel = [dict(r, kind="changed") for r in strat(changed, args.n_changed)] + [dict(r, kind="agree") for r in strat(agree, args.n_agree)]
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / f"forks_{args.pair}.jsonl", "w") as f:
        for r in sel:
            r["lp0"] = {str(k): v for k, v in r["lp0"].items()}; r["lp1"] = {str(k): v for k, v in r["lp1"].items()}
            f.write(json.dumps(r) + "\n")
    print(json.dumps({"pair": args.pair, "n_changed_pool": len(changed), "n_agree_pool": len(agree), "n_selected": len(sel),
                      "n_prompts_changed": len({r["prompt_index"] for r in sel if r["kind"] == "changed"})}, indent=1))


if __name__ == "__main__":
    main()
