"""CT03 E10 stage 1 -- cache everything a dynamic L36 EPO loop needs.

Frozen design: docs/E10_DESIGN.md.

Layers 0-36 do not depend on the L36 gate, so the layer-36 residual stream,
x_t and all 128 expert outputs are constant across training. Layers 37-47 are
not cacheable: the patch propagates through them via attention, which is exactly
what makes a non-final layer expensive and is the thing CT03 is about.

Also cached: the rotary cos/sin for the sequence, so the training loop never
touches layers 0-36 again.
"""
import argparse, json, random, sys
import torch
import torch.nn.functional as F

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from e02_qwen import Capture, load, replay_ce

L = 36


def main(a):
    torch.manual_seed(a.seed); random.seed(a.seed)
    tok, model = load(a)
    K, E = model.config.num_experts_per_tok, model.config.num_experts
    dev0 = next(model.parameters()).device
    pool = json.load(open(a.pool))["items"][a.start:a.start + a.n_problems]
    probs, n_check = [], a.n_check

    for pi, ex in enumerate(pool):
        prompt = tok.apply_chat_template([{"role": "user", "content": ex["problem"]}],
                                         tokenize=False, add_generation_prompt=True,
                                         enable_thinking=False)
        p_ids = tok(prompt, add_special_tokens=False).input_ids
        s_ids = tok(ex["solution"], add_special_tokens=False).input_ids
        ids = p_ids + s_ids
        if len(ids) > a.max_len or len(s_ids) < 24:
            continue
        input_ids = torch.tensor([ids], device=dev0)
        targets = input_ids[0, 1:]
        first = len(p_ids) - 1
        with Capture(model, [L]) as cap:
            with torch.no_grad():
                lg = model(input_ids, use_cache=False).logits
                ce = F.cross_entropy(lg[0, :-1].float(), targets.to(lg.device),
                                     reduction="none")
            x_all = cap.mlp_in[L].detach()
            h_all = cap.mlp_out[L].detach()
            lo = cap.layer_out[L].detach()
            akw = cap.attn_kwargs
        del lg
        order = torch.argsort(ce[first:])
        q = max(1, len(order) // 4)
        rng = random.Random(a.seed * 7919 + a.start + pi)
        toks = sorted(first + int(i) for i in rng.sample(order[-q:].tolist(),
                                                         min(a.n_tok, q)))
        moe = model.model.layers[L].mlp
        banks, xs, hs = [], [], []
        for t in toks:
            x, h = x_all[0, t], h_all[0, t]
            with torch.no_grad():
                bank = torch.stack([moe.experts[e](x) for e in range(E)])
                p0 = F.softmax(F.linear(x, moe.gate.weight).float(), -1)
            if n_check > 0:
                S0 = torch.argsort(p0, descending=True)[:K]
                w = p0[S0]
                h0 = (bank[S0] * (w / w.sum()).unsqueeze(-1)).sum(0)
                rel = float((h0 - h).norm() / h.norm())
                assert rel < 1e-4, f"V2 route reconstruction rel={rel:.2e}"
            xs.append(x.float().cpu()); hs.append(h.float().cpu())
            banks.append(bank.float().cpu())

        pe = akw["position_embeddings"]
        am = akw["attention_mask"]
        if n_check > 0:
            # V1: the cached path must reproduce the full forward's suffix CE.
            # One check, but it validates rotary, mask, residual reconstruction
            # and the layer walk together -- the whole cached replay at once.
            #
            # It is built from the CACHED fields, not from the live akw. Using
            # akw would validate a path the trainer never takes: that is how an
            # attention mask went unnoticed until the assert at save time, after
            # 104 problems of collection.
            st = toks[0]
            T = pe[0].shape[1]
            kw = dict(position_embeddings=(pe[0][0][None].float().to(dev0),
                                           pe[1][0][None].float().to(dev0)),
                      attention_mask=am,
                      position_ids=None,
                      cache_position=torch.arange(T, device=dev0))
            H = lo.expand(2, -1, -1).clone()
            got = float(replay_ce(model, L, H, st, targets, **kw)[0].sum())
            ref = float(ce[st:].sum())
            assert abs(got - ref) < 1e-3 * max(1.0, abs(ref)), \
                f"V1 cached replay {got:.6f} vs {ref:.6f}"
            if a.n_check == n_check + 1:
                print(f"  V1 ok: cached replay {got:.4f} vs {ref:.4f}; "
                      f"mask {None if am is None else (tuple(am.shape), am.dtype)}")
            n_check -= 1
        probs.append(dict(pi=a.start + pi, toks=toks,
                          # dtype is load-bearing: a BOOL mask cast to float
                          # becomes an ADDITIVE 1.0/0.0 mask, i.e. no causal
                          # masking at all. That read as CE 44.5 vs 82.6 --
                          # the model doing "better" by seeing the future.
                          mask=None if am is None else am.cpu(),
                          lo=lo[0].float().cpu(), targets=targets.cpu(),
                          cos=pe[0][0].float().cpu(), sin=pe[1][0].float().cpu(),
                          x=torch.stack(xs), h=torch.stack(hs),
                          bank=torch.stack(banks),
                          base_ce=ce[toks[0]:].float().cpu()))
        del x_all, h_all, lo
        torch.cuda.empty_cache()
        print(f"[{pi+1}/{len(pool)}] shard@{a.start} problems {len(probs)}", flush=True)

    torch.save(dict(probs=probs, K=K, E=E, layer=L,
                    gate=model.model.layers[L].mlp.gate.weight.detach().float().cpu()),
               a.out)
    print(f"wrote {a.out}: {len(probs)} problems")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", default="results/cpd_trainpool.json")
    ap.add_argument("--out", default="results/e10_cache.pt")
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--n-problems", dest="n_problems", type=int, default=105)
    ap.add_argument("--n-tok", dest="n_tok", type=int, default=6)
    ap.add_argument("--n-check", dest="n_check", type=int, default=8)
    ap.add_argument("--max-len", dest="max_len", type=int, default=640)
    ap.add_argument("--n-gpu", dest="n_gpu", type=int, default=2)
    ap.add_argument("--mem-per-gpu", dest="mem_per_gpu", type=int, default=78)
    ap.add_argument("--seed", type=int, default=0)
    main(ap.parse_args())
