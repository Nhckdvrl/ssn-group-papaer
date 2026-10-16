"""E105: unlearn IOI with gradient-difference unlearning restricted to a parameter subset, then save the model for a
relearning run (e93_lesion.py --arm C on the saved weights = continued Pile training, i.e. a relearning attack with
unrelated data).

Forget loss: mean relu(logit(IO) - logit(S) + margin) on training IOI prompts (Builder seed 1, new names);
retain loss: Pile LM loss on a held-out slice (shard 3). Stops when the held-out IOI metric (E89 prompts, seed 0)
falls below --target or after --max_steps. Optimizer: Adam without weight decay, so masked rows never move.

Subsets (--subset):  all | qk (query/key rows of every attention layer) | ov (value rows + output projection of every
attention layer) | mlp (all MLP weights) | attn (qk + ov)

Usage: e105_unlearn.py --subset qk --out DIR [--lr 2e-5 --target 0.5 --max_steps 1500]
"""
import argparse
import json
import time

import numpy as np
import pyarrow.parquet as pq
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

import mp_common as mc
from e89_labor import Builder

BASE = "/home/xiang/mechpop_cache/ckpt/pythia-160m_step100000"
SHARD = mc.CACHE / "pile_tok" / "shard00003.parquet"


def masks(model, subset):
    """Return {param: float mask of the same shape} for trainable params; params absent are frozen."""
    c = model.config
    H, d = c.num_attention_heads, c.hidden_size
    dh = d // H
    out = {}
    for layer in model.gpt_neox.layers:
        qkv = layer.attention.query_key_value
        rows = torch.zeros(H, 3, dh, 1)
        if subset in ("qk", "attn", "all"):
            rows[:, :2] = 1
        if subset in ("ov", "attn", "all"):
            rows[:, 2] = 1
        if rows.any():
            out[qkv.weight] = rows.expand(H, 3, dh, d).reshape(3 * d, d).clone()
            out[qkv.bias] = rows[..., 0].reshape(3 * d).clone()
        if subset in ("ov", "attn", "all"):
            out[layer.attention.dense.weight] = torch.ones_like(layer.attention.dense.weight)
        if subset in ("mlp", "all"):
            for p in layer.mlp.parameters():
                out[p] = torch.ones_like(p)
    return out


def ioi_metric(model, groups):
    dev = next(model.parameters()).device
    vals = []
    with torch.no_grad():
        for g in groups:
            lg = model(g["toks"].to(dev)).logits[:, -1].float()
            io = torch.tensor([t[0] for t in g["tg"]], device=dev)
            s = torch.tensor([f[0] for f in g["fo"]], device=dev)
            vals.append((lg.gather(1, io[:, None]) - lg.gather(1, s[:, None])).squeeze(1).cpu())
    return float(torch.cat(vals).mean())


def lm_loss(model, x):
    with torch.no_grad():
        return float(model(x, labels=x).loss)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--subset", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--lr", type=float, default=2e-5)
    ap.add_argument("--target", type=float, default=0.5)
    ap.add_argument("--max_steps", type=int, default=1500)
    ap.add_argument("--margin", type=float, default=1.0)
    ap.add_argument("--retain_w", type=float, default=1.0)
    ap.add_argument("--retain_bs", type=int, default=16)
    ap.add_argument("--eval_every", type=int, default=25)
    ap.add_argument("--seed", type=int, default=0, help="torch seed, forget-prompt seed (seed + 1) and retain-data offset")
    ap.add_argument("--tag", default="")
    a = ap.parse_args()
    torch.manual_seed(a.seed)
    torch.backends.cuda.matmul.allow_tf32 = True
    tok = AutoTokenizer.from_pretrained("EleutherAI/pythia-160m", cache_dir=str(mc.HF_CACHE))
    model = AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.float32, attn_implementation="sdpa").cuda()
    train = Builder(tok, 512, seed=a.seed + 1).ioi()
    held = Builder(tok, 256, seed=0).ioi()
    tbl = pq.read_table(SHARD).column("tokens")
    eval_x = torch.tensor(tbl.slice(120000, 16).to_pylist()).cuda()
    m = masks(model, a.subset)
    for p in model.parameters():
        p.requires_grad_(p in m)
    params = [p for p in model.parameters() if p.requires_grad]
    for p in params:
        mk = m[p].cuda()
        p.register_hook(lambda g, mk=mk: g * mk)
    opt = torch.optim.Adam(params, lr=a.lr, weight_decay=0.0)
    log = {"args": vars(a), "trace": []}
    m0, l0 = ioi_metric(model, held), lm_loss(model, eval_x)
    log["start"] = {"ioi": m0, "lm": l0}
    print(json.dumps(log["start"]), flush=True)
    t0, ptr, step = time.time(), 20000 * a.seed, 0
    for step in range(1, a.max_steps + 1):
        g = train[step % len(train)]
        x = g["toks"].cuda()
        io = torch.tensor([t[0] for t in g["tg"]], device="cuda")
        s = torch.tensor([f[0] for f in g["fo"]], device="cuda")
        lg = model(x).logits[:, -1]
        diff = lg.gather(1, io[:, None]) - lg.gather(1, s[:, None])
        forget = torch.relu(diff + a.margin).mean()
        r = torch.tensor(tbl.slice(ptr, a.retain_bs).to_pylist()).cuda()
        ptr += a.retain_bs
        retain = model(r, labels=r).loss
        opt.zero_grad(set_to_none=True)
        (forget + a.retain_w * retain).backward()
        torch.nn.utils.clip_grad_norm_(params, 1.0)
        opt.step()
        if step % a.eval_every == 0:
            mi, li = ioi_metric(model, held), lm_loss(model, eval_x)
            log["trace"].append({"step": step, "ioi": mi, "lm": li})
            print(json.dumps({"step": step, "ioi": round(mi, 3), "lm": round(li, 4), "sec": round(time.time() - t0)}), flush=True)
            if mi < a.target:
                break
    base = AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.float32)
    pb = dict(base.named_parameters())
    dist = sum(float((p.detach().cpu() - pb[n].detach()).norm() ** 2) for n, p in model.named_parameters()) ** 0.5
    tot = sum(float(p.detach().norm() ** 2) for p in pb.values()) ** 0.5
    log["end"] = {"step": step, "ioi": ioi_metric(model, held), "lm": lm_loss(model, eval_x), "l2": dist, "l2_rel": dist / tot}
    print(json.dumps(log["end"]), flush=True)
    model.save_pretrained(a.out, safe_serialization=False)
    out = mc.RESULTS / "e105"
    out.mkdir(parents=True, exist_ok=True)
    (out / f"unlearn_{a.tag or a.subset}.json").write_text(json.dumps(log))


if __name__ == "__main__":
    main()
