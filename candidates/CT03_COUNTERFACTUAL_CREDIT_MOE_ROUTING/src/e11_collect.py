"""CT03 E11 stage 1 -- cache the L47 router inputs for a LARGE, unfiltered token
pool. Frozen design: docs/E11_DESIGN.md.

Deliberately does NOT cache the expert bank. The parent selects hard tokens
dynamically by the CURRENT router's CE, so the pool has to be large; at 16KB per
token (x, resid, target, base CE) tens of thousands of tokens are affordable,
while a 1MB/token bank would have forced the small permanently-fixed token set
that E11 exists to repair. Expert outputs are computed on demand at train time.
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
    K, E = model.config.num_experts_per_tok, model.config.num_experts
    dev0 = next(model.parameters()).device
    pool = json.load(open(a.pool))["items"][a.start:a.start + a.n_problems]
    norm, head = model.model.norm, model.lm_head
    X, R, meta = [], [], []
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
        # UNIFORM sample over the solution span: no CE-quartile filter, because
        # the hard-token rule is applied dynamically at train time against the
        # CURRENT router, not frozen here against the base one.
        span = list(range(first, len(ids) - 1))
        rng = random.Random(a.seed * 7919 + a.start + pi)
        toks = sorted(rng.sample(span, min(a.n_tok, len(span))))
        for t in toks:
            resid = lo_all[0, t] - h_all[0, t]
            if n_check > 0:
                with torch.no_grad():
                    lgt = head(norm(resid + h_all[0, t])).float()
                    got = float(F.cross_entropy(lgt[None],
                                                targets[t][None].to(lgt.device)))
                assert abs(got - float(ce[t])) < 1e-3, \
                    f"V1 cached CE path {got:.6f} vs {float(ce[t]):.6f}"
                n_check -= 1
            X.append(x_all[0, t].float().cpu()); R.append(resid.float().cpu())
            meta.append(dict(pi=a.start + pi, pos=t, tgt=int(targets[t]),
                             base_ce=float(ce[t])))
        del x_all, h_all, lo_all
        torch.cuda.empty_cache()
        if (pi + 1) % 10 == 0:
            print(f"[{pi+1}/{len(pool)}] shard@{a.start} tokens {len(meta)}", flush=True)

    torch.save(dict(x=torch.stack(X), resid=torch.stack(R), meta=meta, K=K, E=E,
                    layer=L,
                    gate=model.model.layers[L].mlp.gate.weight.detach().float().cpu(),
                    norm_w=norm.weight.detach().float().cpu(),
                    eps=model.config.rms_norm_eps), a.out)
    if not __import__("os").path.exists(a.head_out):
        torch.save(head.weight.detach().float().cpu(), a.head_out)
    print(f"wrote {a.out}: {len(meta)} tokens")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", default="results/cpd_trainpool.json")
    ap.add_argument("--out", default="results/e11_cache.pt")
    ap.add_argument("--head-out", dest="head_out", default="results/e09_head.pt")
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--n-problems", dest="n_problems", type=int, default=300)
    ap.add_argument("--n-tok", dest="n_tok", type=int, default=96)
    ap.add_argument("--n-check", dest="n_check", type=int, default=8)
    ap.add_argument("--max-len", dest="max_len", type=int, default=640)
    ap.add_argument("--n-gpu", dest="n_gpu", type=int, default=2)
    ap.add_argument("--mem-per-gpu", dest="mem_per_gpu", type=int, default=78)
    ap.add_argument("--seed", type=int, default=0)
    main(ap.parse_args())
