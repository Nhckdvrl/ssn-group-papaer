"""CT03 E11 stage 3 -- sampled pass@K on the locked FG0 120, base vs the
corrected L47 EPO router. Frozen design: docs/E11_DESIGN.md.

This is the parent's own headline metric, and the reason it replaces greedy
pass@1 here: an EPO update moves the routing DISTRIBUTION, and a single
deterministic trajectory cannot say which way it moved. E10's greedy 0.475 ->
0.475 sat on top of 99.2% changed completions -- a large distributional move
scored by a statistic blind to it.

Both arms run bf16 with the SAME seeds and the same prompt order, so a sample
index is paired across arms. AIME/HMMT are untouched; they stay confirmatory.
"""
import argparse, json, sys, time
import numpy as np
import torch
from transformers import DynamicCache

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from e02_qwen import load
from fg0_pool import boxed, norm


@torch.no_grad()
def sample_batch(model, tok, prompts, max_new, temp, top_p, gen):
    """Left-padded batched ancestral sampling with top-p. Mirrors cpd_freegen's
    gen_batch (same padding, cache and EOS handling); only the token choice
    differs, so greedy and sampled arms stay comparable."""
    dev = next(model.parameters()).device
    enc = [tok(p, add_special_tokens=False).input_ids for p in prompts]
    T = max(len(e) for e in enc)
    pad = tok.pad_token_id or tok.eos_token_id
    ids = torch.full((len(enc), T), pad, device=dev, dtype=torch.long)
    att = torch.zeros((len(enc), T), device=dev, dtype=torch.long)
    for i, e in enumerate(enc):
        ids[i, T - len(e):] = torch.tensor(e, device=dev)
        att[i, T - len(e):] = 1

    # TOPN bounds both the sort and the sampling work. At T=0.6 the top-p 0.95
    # nucleus is a few hundred tokens at most, so a full 151936-wide sort (and
    # a 39MB host copy) per decode step was pure overhead -- it made the first
    # timing smoke produce nothing in 40 minutes.
    TOPN = 1024

    def pick(logits):
        lg = logits.float() / temp
        sp, si = torch.topk(torch.softmax(lg, -1), TOPN, -1)
        cut = (sp.cumsum(-1) - sp) > top_p        # keep the token that crosses
        sp = sp.masked_fill(cut, 0.0)
        sp = sp / sp.sum(-1, keepdim=True)
        k = torch.multinomial(sp, 1, generator=gen)
        return si.gather(-1, k)

    cache = DynamicCache(config=model.config)
    out = model(ids, attention_mask=att, use_cache=True, past_key_values=cache,
                logits_to_keep=1)
    nxt = pick(out.logits[:, -1])
    eos = model.config.eos_token_id
    eos = eos if isinstance(eos, (list, tuple)) else [eos]
    seq = [nxt]
    done = torch.zeros(len(enc), dtype=torch.bool, device=dev)
    for _ in range(max_new - 1):
        att = torch.cat([att, (~done).long().unsqueeze(1)], 1)
        o = model(nxt, attention_mask=att, use_cache=True, past_key_values=cache,
                  logits_to_keep=1)
        nxt = pick(o.logits[:, -1])
        for e in eos:
            done |= nxt.squeeze(1) == e
        seq.append(nxt)
        if bool(done.all()):
            break
    res = []
    for row in torch.cat(seq, 1).tolist():
        cut = len(row)
        for e in eos:
            if e in row:
                cut = min(cut, row.index(e))
        res.append(row[:cut])
    return res


def main(a):
    tok, model = load(a)
    dev = next(model.parameters()).device
    pool = json.load(open(a.pool))["items"][:a.n_problems]
    idx = list(range(a.shard, len(pool), a.n_shard))      # strided: every shard
    pool = [pool[i] for i in idx]                          # sees the same mix
    L = a.layer
    gate = model.model.layers[L].mlp.gate
    base_w = gate.weight.detach().clone()
    arms = [("base", base_w)]
    if a.ckpt:
        sd = torch.load(a.ckpt, map_location="cpu")[str(L)]
        arms.append((f"epo_l{L}", sd.to(gate.weight.device).to(gate.weight.dtype)))

    prompts = [tok.apply_chat_template([{"role": "user", "content": e["problem"]}],
                                       tokenize=False, add_generation_prompt=True,
                                       enable_thinking=False) for e in pool]
    # one (problem, sample) job per row; the SAME job order for both arms
    jobs = [(i, s) for i in range(len(pool)) for s in range(a.n_samples)]
    out = {}
    for arm, w in arms:
        gate.weight.data.copy_(w)
        comp, t0 = {}, time.time()
        for b in range(0, len(jobs), a.batch):
            sub = jobs[b:b + a.batch]
            g = torch.Generator(device=dev).manual_seed(a.seed * 1_000_003 + b)
            got = sample_batch(model, tok, [prompts[i] for i, _ in sub],
                               a.max_new, a.temp, a.top_p, g)
            for (i, s), c in zip(sub, got):
                comp[(i, s)] = tok.decode(c)
            n = min(b + a.batch, len(jobs))
            el = time.time() - t0
            print(f"  [{arm}] {n}/{len(jobs)} {el:.0f}s "
                  f"eta {el / n * (len(jobs) - n):.0f}s", flush=True)
        out[arm] = comp

    rows = []
    for i, ex in enumerate(pool):
        gold = norm(boxed(ex["solution"]) or "")
        r = dict(pi=idx[i], gold=gold)
        for arm, _ in arms:
            ok = [int(bool(gold) and norm(boxed(out[arm][(i, s)]) or "") == gold)
                  for s in range(a.n_samples)]
            r[arm] = dict(n=a.n_samples, c=int(sum(ok)), ok=ok)
        rows.append(r)
    json.dump(dict(rows=rows, arms=[k for k, _ in arms], n_samples=a.n_samples,
                   temp=a.temp, top_p=a.top_p, shard=a.shard,
                   completions={k: {f"{i}_{s}": v for (i, s), v in d.items()}
                                for k, d in out.items()}),
              open(a.out, "w"))
    print(f"wrote {a.out}: {len(rows)} problems x {a.n_samples}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", default="results/fg0_devpool.json")
    ap.add_argument("--layer", type=int, default=47)
    ap.add_argument("--ckpt", default="results/e11_gate_l47.pt")
    ap.add_argument("--out", default="results/e11_passk.json")
    ap.add_argument("--n-problems", dest="n_problems", type=int, default=120)
    ap.add_argument("--n-samples", dest="n_samples", type=int, default=32)
    ap.add_argument("--batch", type=int, default=96)
    ap.add_argument("--max-new", dest="max_new", type=int, default=512)
    ap.add_argument("--temp", type=float, default=0.6)
    ap.add_argument("--top-p", dest="top_p", type=float, default=0.95)
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--n-shard", dest="n_shard", type=int, default=1)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--dtype", default="bf16")
    ap.add_argument("--n-gpu", dest="n_gpu", type=int, default=1)
    ap.add_argument("--mem-per-gpu", dest="mem_per_gpu", type=int, default=78)
    main(ap.parse_args())
