"""CT03 CPD v1 -- free-generation evaluation on the 120 locked FG0 problems.

Four checkpoints (base, router_ce, shuffled, cpd) under identical greedy
decoding, prompt, stopping rule, max tokens and answer extractor.

Two families of measurement, kept apart on purpose:

  HEADLINE (real free generation) -- correctness, parsed answer, same_as_base,
  first divergence index, completion length. This is what the claim rests on.

  SHARED-PREFIX DIAGNOSTICS -- next-token KL/TV and L36/L44 route overlap,
  valid ONLY before the first divergence. Once an arm emits a different token
  the two models no longer share a prefix, so any later comparison at the same
  index mixes router policy difference with context difference. Reported
  separately, never pooled with the headline.

  SAME-CONTEXT ROUTE CHANGE -- every arm's routers replayed over the SAME base
  completion, teacher-forced. This stays interpretable after divergence and
  answers "how much did the router itself move on identical context".
"""

import argparse, json, sys, time
import numpy as np
import torch
import torch.nn.functional as F
from transformers import DynamicCache

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from e02_qwen import load
from cpd_v1 import LAYERS
from fg0_pool import boxed, norm

ARMS = ["base", "router_ce", "shuffled", "cpd"]


def set_gates(model, base_w, sd):
    for l, bw in zip(LAYERS, base_w):
        g = model.model.layers[l].mlp.gate
        g.weight.data.copy_(bw if sd is None else sd[str(l)].to(g.weight.device))


@torch.no_grad()
def gen_batch(model, tok, prompts, max_new):
    """Left-padded batched greedy decoding."""
    dev = next(model.parameters()).device
    enc = [tok(p, add_special_tokens=False).input_ids for p in prompts]
    T = max(len(e) for e in enc)
    pad = tok.pad_token_id or tok.eos_token_id
    ids = torch.full((len(enc), T), pad, device=dev, dtype=torch.long)
    att = torch.zeros((len(enc), T), device=dev, dtype=torch.long)
    for i, e in enumerate(enc):
        ids[i, T - len(e):] = torch.tensor(e, device=dev)
        att[i, T - len(e):] = 1
    cache = DynamicCache(config=model.config)
    # Without logits_to_keep the prefill materialises logits for EVERY
    # position: batch x seq x 151936 x 4 bytes is ~9.7GB at batch 64, for a
    # tensor whose last row is all that is used.
    out = model(ids, attention_mask=att, use_cache=True, past_key_values=cache,
                logits_to_keep=1)
    nxt = out.logits[:, -1].argmax(-1, keepdim=True)
    eos = model.config.eos_token_id
    eos = eos if isinstance(eos, (list, tuple)) else [eos]
    gen = [nxt]
    done = torch.zeros(len(enc), dtype=torch.bool, device=dev)
    for _ in range(max_new - 1):
        att = torch.cat([att, (~done).long().unsqueeze(1)], 1)
        o = model(nxt, attention_mask=att, use_cache=True, past_key_values=cache,
                  logits_to_keep=1)
        nxt = o.logits[:, -1].argmax(-1, keepdim=True)
        for e in eos:
            done |= nxt.squeeze(1) == e
        gen.append(nxt)
        if bool(done.all()):
            break
    seq = torch.cat(gen, 1).tolist()
    res = []
    for row in seq:
        cut = len(row)
        for e in eos:
            if e in row:
                cut = min(cut, row.index(e))
        res.append(row[:cut])
    return res


@torch.no_grad()
def replay_routes(model, tok, prompt_ids, cont_ids):
    """Teacher-force prompt+continuation; return next-token log-probs and the
    routed top-8 at each trained layer, for every continuation position."""
    dev = next(model.parameters()).device
    ids = torch.tensor([prompt_ids + cont_ids], device=dev)
    K = model.config.num_experts_per_tok
    grabbed = {}
    hs = []
    for l in LAYERS:
        def hk(mod, inp, out, l=l):
            grabbed[l] = inp[0].detach()
        hs.append(model.model.layers[l].mlp.register_forward_hook(hk))
    lg = model(ids, use_cache=False).logits
    for h in hs:
        h.remove()
    n0 = len(prompt_ids) - 1
    lp = F.log_softmax(lg[0, n0:-1].float(), -1)          # predicts each cont token
    routes = {}
    for l in LAYERS:
        g = model.model.layers[l].mlp.gate(grabbed[l][0, n0:-1]).float()
        routes[l] = torch.topk(g, K, dim=-1).indices.cpu()
    return lp, routes


def main(a):
    tok, model = load(a)
    dev0 = next(model.parameters()).device
    pool = json.load(open(a.pool))["items"][:a.n_problems]
    gates = [model.model.layers[l].mlp.gate for l in LAYERS]
    base_w = [g.weight.detach().clone() for g in gates]
    ckpt = {"base": None}
    for spec in a.ckpts.split(","):
        if spec:
            t, p = spec.split(":", 1)
            ckpt[t] = torch.load(p, map_location="cpu")
    arms = [x for x in ARMS if x in ckpt]
    print("arms:", arms, flush=True)

    prompts = [tok.apply_chat_template([{"role": "user", "content": e["problem"]}],
                                       tokenize=False, add_generation_prompt=True,
                                       enable_thinking=False) for e in pool]
    pids = [tok(p, add_special_tokens=False).input_ids for p in prompts]

    # ---- phase 1: headline free generation, one arm at a time, batched ----
    comp = {}
    t0 = time.time()
    for arm in arms:
        set_gates(model, base_w, ckpt[arm])
        outs = []
        for i in range(0, len(pool), a.batch):
            outs += gen_batch(model, tok, prompts[i:i + a.batch], a.max_new)
            print(f"  [{arm}] {min(i+a.batch,len(pool))}/{len(pool)} "
                  f"{time.time()-t0:.0f}s", flush=True)
        comp[arm] = outs

    # ---- phase 2: diagnostics on the SHARED base context ----
    diag = {arm: [] for arm in arms}
    base_lp, base_rt = [], []
    set_gates(model, base_w, None)
    for qi in range(len(pool)):
        lp, rt = replay_routes(model, tok, pids[qi], comp["base"][qi])
        base_lp.append(lp.cpu()); base_rt.append({l: rt[l] for l in LAYERS})
    for arm in arms:
        set_gates(model, base_w, ckpt[arm])
        for qi in range(len(pool)):
            lp, rt = replay_routes(model, tok, pids[qi], comp["base"][qi])
            lp = lp.cpu()
            p = base_lp[qi].exp()
            kl = (p * (base_lp[qi] - lp)).sum(-1)
            tv = 0.5 * (p - lp.exp()).abs().sum(-1)
            ov = {l: np.mean([len(set(base_rt[qi][l][k].tolist())
                                  & set(rt[l][k].tolist())) / 8.0
                              for k in range(rt[l].shape[0])]) for l in LAYERS}
            d = next((k for k, (x, y) in enumerate(zip(comp[arm][qi],
                                                       comp["base"][qi])) if x != y),
                     min(len(comp[arm][qi]), len(comp["base"][qi])))
            diag[arm].append(dict(
                first_div=int(d),
                kl_shared=float(kl[:d].mean()) if d > 0 else 0.0,
                tv_shared=float(tv[:d].mean()) if d > 0 else 0.0,
                kl_all=float(kl.mean()), tv_all=float(tv.mean()),
                route_overlap_on_base_context={str(l): float(ov[l]) for l in LAYERS}))
        print(f"  [diag {arm}] done {time.time()-t0:.0f}s", flush=True)

    with open(a.out, "w") as f:
        for arm in arms:
            for qi, ex in enumerate(pool):
                txt = tok.decode(comp[arm][qi], skip_special_tokens=True)
                pred = boxed(txt)
                f.write(json.dumps(dict(
                    arm=arm, qi=qi, level=ex.get("level"), cfg=ex.get("cfg"),
                    correct=bool(pred is not None and norm(pred) == norm(ex["answer"])),
                    pred=pred, gold=ex["answer"], n_gen=len(comp[arm][qi]),
                    same_as_base=bool(comp[arm][qi] == comp["base"][qi]),
                    text=txt[:2000], **diag[arm][qi])) + "\n")

    print("\n" + "=" * 74)
    print(f"{'arm':>12}{'acc':>8}{'vs base':>10}{'same':>8}{'first_div':>11}"
          f"{'KL(shared)':>12}{'ovl L36':>9}{'ovl L44':>9}")
    accs = {}
    for arm in arms:
        c = [bool(pred_ok) for pred_ok in
             [boxed(tok.decode(comp[arm][qi], skip_special_tokens=True)) is not None
              and norm(boxed(tok.decode(comp[arm][qi], skip_special_tokens=True)))
              == norm(pool[qi]["answer"]) for qi in range(len(pool))]]
        accs[arm] = float(np.mean(c))
        d = diag[arm]
        print(f"{arm:>12}{accs[arm]:>8.3f}{accs[arm]-accs['base']:>+10.3f}"
              f"{np.mean([x['first_div'] >= x_n for x, x_n in zip(d, [len(comp[arm][q]) for q in range(len(pool))])]):>8.3f}"
              f"{np.mean([x['first_div'] for x in d]):>11.1f}"
              f"{np.mean([x['kl_shared'] for x in d]):>12.2e}"
              f"{np.mean([x['route_overlap_on_base_context']['36'] for x in d]):>9.3f}"
              f"{np.mean([x['route_overlap_on_base_context']['44'] for x in d]):>9.3f}")
    print(f"\nwrote {a.out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", default="results/fg0_devpool.json")
    ap.add_argument("--ckpts", default="router_ce:results/cpd_router_ce.pt,"
                                       "shuffled:results/cpd_router_shuffled.pt,"
                                       "cpd:results/cpd_router_cpd.pt")
    ap.add_argument("--out", default="results/cpd_freegen.jsonl")
    ap.add_argument("--n-problems", dest="n_problems", type=int, default=120)
    ap.add_argument("--max-new", dest="max_new", type=int, default=512)
    ap.add_argument("--batch", type=int, default=8)
    ap.add_argument("--n-gpu", dest="n_gpu", type=int, default=2)
    ap.add_argument("--mem-per-gpu", dest="mem_per_gpu", type=int, default=78)
    ap.add_argument("--seed", type=int, default=0)
    main(ap.parse_args())
