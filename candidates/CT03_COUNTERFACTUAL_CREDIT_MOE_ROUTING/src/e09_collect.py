"""CT03 E09 stage 1 -- cache everything L47 EPO needs, once.

Frozen design: docs/E09_DESIGN.md.

Layer 47 is the last decoder layer, so only the final RMSNorm and lm_head follow
it and both are position-wise. Therefore:

  * patching the MoE output at position t changes the CE at t and nowhere else;
  * x_t and the residual stream entering the block do not depend on the L47
    gate, so they can be cached once and reused for every training step.

We cache ALL 128 expert outputs per token, not just the base top-32, so the
router may move anywhere during training without the cache silently constraining
the action space.
"""
import argparse, json, random, sys
import torch
import torch.nn.functional as F

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from e02_qwen import Capture, load

L = 47


def main(a):
    torch.manual_seed(a.seed); random.seed(a.seed)
    tok, model = load(a)
    K = model.config.num_experts_per_tok
    E = model.config.num_experts
    dev0 = next(model.parameters()).device
    pool = json.load(open(a.pool))["items"][a.start:a.start + a.n_problems]
    norm, head = model.model.norm, model.lm_head

    X, R, B, meta = [], [], [], []
    n_check = a.n_check
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
            lo_all = cap.layer_out[L].detach()
        del lg
        order = torch.argsort(ce[first:])
        q = max(1, len(order) // 4)
        rng = random.Random(a.seed * 7919 + a.start + pi)
        toks = [first + int(i) for i in rng.sample(order[-q:].tolist(),
                                                   min(a.n_tok, q))]
        moe = model.model.layers[L].mlp
        for t in toks:
            x, h = x_all[0, t], h_all[0, t]
            resid = lo_all[0, t] - h                      # everything but the MoE
            with torch.no_grad():
                bank = torch.stack([moe.experts[e](x) for e in range(E)])
                p0 = F.softmax(F.linear(x, moe.gate.weight).float(), -1)
            if n_check > 0:
                S0 = torch.argsort(p0, descending=True)[:K]
                w = p0[S0]
                h0 = (bank[S0] * (w / w.sum()).unsqueeze(-1)).sum(0)
                rel = float((h0 - h).norm() / h.norm())
                assert rel < 1e-4, f"V1 route reconstruction rel={rel:.2e}"
                with torch.no_grad():
                    lgt = head(norm(resid + h0)).float()
                    got = float(F.cross_entropy(lgt[None], targets[t][None].to(lgt.device)))
                assert abs(got - float(ce[t])) < 1e-3, \
                    f"V1b cached CE path {got:.6f} vs {float(ce[t]):.6f}"
                n_check -= 1
            X.append(x.float().cpu()); R.append(resid.float().cpu())
            B.append(bank.float().cpu())
            meta.append(dict(pi=a.start + pi, pos=t, tgt=int(targets[t]),
                             base_ce=float(ce[t])))
        del x_all, h_all, lo_all
        torch.cuda.empty_cache()
        print(f"[{pi+1}/{len(pool)}] shard@{a.start} tokens {len(meta)}", flush=True)

    torch.save(dict(x=torch.stack(X), resid=torch.stack(R), bank=torch.stack(B),
                    meta=meta, K=K, E=E, layer=L,
                    gate=model.model.layers[L].mlp.gate.weight.detach().float().cpu(),
                    norm_w=norm.weight.detach().float().cpu(),
                    eps=model.config.rms_norm_eps), a.out)
    # lm_head is 1.2GB, the same for every shard, and the trainer needs it
    # without loading the 30B backbone. Written once, separately.
    if not __import__("os").path.exists(a.head_out):
        torch.save(head.weight.detach().float().cpu(), a.head_out)
    print(f"wrote {a.out}: {len(meta)} tokens")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", default="results/cpd_trainpool.json")
    ap.add_argument("--out", default="results/e09_cache.pt")
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--n-problems", dest="n_problems", type=int, default=105)
    ap.add_argument("--n-tok", dest="n_tok", type=int, default=6)
    ap.add_argument("--n-check", dest="n_check", type=int, default=8)
    ap.add_argument("--head-out", dest="head_out", default="results/e09_head.pt")
    ap.add_argument("--max-len", dest="max_len", type=int, default=640)
    ap.add_argument("--n-gpu", dest="n_gpu", type=int, default=2)
    ap.add_argument("--mem-per-gpu", dest="mem_per_gpu", type=int, default=78)
    ap.add_argument("--seed", type=int, default=0)
    main(ap.parse_args())
