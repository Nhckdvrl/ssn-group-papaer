"""CT03 E03.7b -- the same interaction/estimation decomposition on OLMoE.

E03.7a ran on Qwen only (3 layers). The structural claim needs a second model
and more layers, and e01_records.jsonl cannot supply it: E01 recorded a single
i (the weakest selected expert) per token, so there is no 8x4 grid to project.
This produces that grid -- exact AND proxy for all K x m one-swaps -- on OLMoE,
whose norm_topk_prob=false makes dh = w_j E_j - w_i E_i exactly.
"""
import argparse, json, random, sys
import torch
import torch.nn.functional as F
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from e01_credit import MODEL, Capture, replay_ce


def main(a):
    torch.manual_seed(a.seed); random.seed(a.seed)
    dev = "cuda"
    tok = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL, dtype=torch.float32, attn_implementation="sdpa").to(dev).eval()
    for p in model.parameters():
        p.requires_grad_(False)
    K = model.config.num_experts_per_tok
    assert not model.config.norm_topk_prob
    layers = [int(x) for x in a.layers.split(",")]

    ds = load_dataset("HuggingFaceH4/MATH-500", split="test")
    idxs = list(range(len(ds))); random.Random(a.seed).shuffle(idxs)
    fe = open(a.exact_out, "w"); fp = open(a.proxy_out, "w")

    done = 0
    for qi in idxs:
        if done >= a.n_problems:
            break
        ex = ds[qi]
        prompt = tok.apply_chat_template([{"role": "user", "content": ex["problem"]}],
                                         tokenize=False, add_generation_prompt=True)
        p_ids = tok(prompt, add_special_tokens=False).input_ids
        s_ids = tok(ex["solution"], add_special_tokens=False).input_ids
        ids = p_ids + s_ids
        if len(ids) > a.max_len or len(s_ids) < a.min_sol:
            continue
        done += 1
        input_ids = torch.tensor([ids], device=dev)
        targets = input_ids[0, 1:]
        first = len(p_ids) - 1

        with Capture(model, layers) as cap:
            with torch.enable_grad():
                emb = model.model.embed_tokens(input_ids).detach().requires_grad_(True)
                logits = model(inputs_embeds=emb, use_cache=False).logits
                ce = F.cross_entropy(logits[0, :-1].float(), targets, reduction="none")
                ce[first:].sum().backward()
        base_ce = ce.detach().clone()
        g = {l: cap.mlp_out[l].grad[0].detach().clone() for l in layers}
        x_all = {l: cap.mlp_in[l].detach() for l in layers}
        lo_all = {l: cap.layer_out[l].detach() for l in layers}
        akw = cap.attn_kwargs
        del logits, ce, emb, cap
        torch.cuda.empty_cache()

        order = torch.argsort(base_ce[first:])
        qn = max(1, len(order) // 4)
        rng = random.Random(a.seed * 7919 + qi)
        toks = [first + int(i) for i in rng.sample(order[-qn:].tolist(),
                                                   min(a.n_tok, qn))]

        for l in layers:
            moe = model.model.layers[l].mlp
            for t in toks:
                x = x_all[l][0, t]
                w = F.softmax(moe.gate(x).float(), dim=-1)
                rank = torch.argsort(w, descending=True)
                sel = rank[:K].tolist(); cand = rank[K:K + a.m].tolist()
                gv = g[l][t].float()
                with torch.no_grad():
                    E = {e: moe.experts[e](x) for e in sel + cand}
                pairs, dhs = [], []
                for i in sel:
                    for j in cand:
                        d = E[j] * float(w[j]) - E[i] * float(w[i])
                        pairs.append((i, j)); dhs.append(d)
                        fp.write(json.dumps(dict(q=qi, layer=l, pos=t, i=i, j=j,
                                                 px=float(gv @ d.float()))) + "\n")
                dhs = torch.stack(dhs)
                H = lo_all[l].expand(len(pairs) + 1, -1, -1).clone()
                H[1:, t] += dhs
                allce = replay_ce(model, l, H, t, targets, akw)
                dL = (allce[1:] - allce[0]).sum(dim=1).tolist()
                for (i, j), v in zip(pairs, dL):
                    fe.write(json.dumps(dict(q=qi, layer=l, pos=t, i=i, j=j,
                                             dL=v)) + "\n")
                fe.flush(); fp.flush()
        print(f"[{done}/{a.n_problems}] q={qi}", flush=True)
        del g, x_all, lo_all
        torch.cuda.empty_cache()
    fe.close(); fp.close()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--layers", default="1,4,7,10,13,15")
    ap.add_argument("--m", type=int, default=4)
    ap.add_argument("--n-problems", dest="n_problems", type=int, default=16)
    ap.add_argument("--n-tok", dest="n_tok", type=int, default=8)
    ap.add_argument("--max-len", dest="max_len", type=int, default=512)
    ap.add_argument("--min-sol", dest="min_sol", type=int, default=64)
    ap.add_argument("--exact-out", dest="exact_out", default="results/e037_olmoe_exact.jsonl")
    ap.add_argument("--proxy-out", dest="proxy_out", default="results/e037_olmoe_proxy.jsonl")
    ap.add_argument("--seed", type=int, default=0)
    main(ap.parse_args())
