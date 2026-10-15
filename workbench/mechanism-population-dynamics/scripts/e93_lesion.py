"""E93: lesion-and-recovery during continued pretraining, against a matched undamaged control.

Usage: e93_lesion.py --arm C|H|R|N --lr LR --local DIR [--steps 2000] [--bs 128] [--tag NAME]
  DIR holds config.json + pytorch_model.bin of the base checkpoint (fetched with curl; HF Xet stalls here).
Arms (O = overshoot along a real batch gradient, Q = scale Q/K of --head, both calibrated to --target_dloss)
  C  no damage
  H  re-initialise one or more heads (--head L.H[,L.H], default the 160M previous-token hub 3.2): its Q/K/V rows + biases and its
     columns of the attention output projection, drawn from Pythia's init distributions (small_init / wang_init)
  R  same operation on a low-importance head (--head)
  N  isotropic noise on every 2-D weight, N(0, alpha * std(W)); alpha calibrated before training so that the
     validation loss rises by --target_dloss nats (default 1.5, the size of the two natural spikes in E90)
All arms: same data order (NeelNanda/pile-small-tokenized-2b shards, 1024-token sequences), AdamW from zero state
(betas 0.9/0.95, wd 0.01, eps 1e-8), --warm-step (default 200) linear warm-up to a constant LR, grad-norm clip 1.0, bf16 autocast.
Evaluation at fixed steps: validation loss (48 fixed pile-10k docs), the E92 capability battery (35 FV + 7 elementary),
per-head previous-token and induction attention scores. Training uses SDPA attention (eager drifted under bf16).
"""
import argparse
import json
import math
import os
import time

import numpy as np
import pyarrow.parquet as pq
import torch

import mp_common as mc
from e92_atlas import ABSTRACTIVE, ELEMENTARY, EXTRACTIVE, eval_el, eval_fv, fv_prompts
from e89_labor import lm_loss

OUT = mc.RESULTS / os.environ.get("E93_OUT", "e93")
SHARDS = [mc.CACHE / "pile_tok" / f"shard0000{i}.parquet" for i in range(4)]
EVAL_STEPS = [0, 25, 50, 100, 200, 400, 700, 1000, 1500, 2000, 2500, 3000, 4000]


class Data:
    def __init__(self, bs):
        self.bs, self.tabs, self.t, self.i = bs, [pq.read_table(s) for s in SHARDS], 0, 0

    def next(self):
        rows = []
        while len(rows) < self.bs:
            tab = self.tabs[self.t]
            take = min(self.bs - len(rows), tab.num_rows - self.i)
            rows += tab.column("tokens").slice(self.i, take).to_pylist()
            self.i += take
            if self.i >= tab.num_rows:
                self.t, self.i = (self.t + 1) % len(self.tabs), 0
        return torch.tensor(rows, dtype=torch.long)


def reinit_head(model, l, h, gen):
    """Pythia (GPT-NeoX) init: small_init std = sqrt(2 / (5 d)) for QKV; wang_init std = 2 / (L sqrt(d)) for dense."""
    c = model.config
    d, H, L = c.hidden_size, c.num_attention_heads, c.num_hidden_layers
    dh = d // H
    att = model.gpt_neox.layers[l].attention
    W = att.query_key_value.weight.data.view(H, 3, dh, d)
    W[h] = torch.randn(W[h].shape, generator=gen, device="cpu").to(W) * math.sqrt(2 / (5 * d))
    if att.query_key_value.bias is not None:
        att.query_key_value.bias.data.view(H, 3, dh)[h] = 0
    att.dense.weight.data[:, h * dh:(h + 1) * dh] = (torch.randn(d, dh, generator=gen) * (2 / (L * math.sqrt(d)))).to(att.dense.weight)


def add_noise(model, alpha, seed):
    gen = torch.Generator().manual_seed(seed)
    for n, p in model.named_parameters():
        if p.dim() == 2:
            p.data += (torch.randn(p.shape, generator=gen) * alpha * p.data.float().std().item()).to(p)


def set_attn(model, impl):
    """Train with SDPA; switch to eager only to read attention weights. (Training with eager attention under bf16
    autocast drifted even at lr 3e-6 -- E93 calibration, 2026-10-16.)"""
    model.config._attn_implementation = impl
    for l in model.gpt_neox.layers:
        l.attention.config._attn_implementation = impl


def overshoot(model, step_size, grad):
    for n, p in model.named_parameters():
        if n in grad:
            p.data -= step_size * grad[n]


def scale_qk(model, heads, k):
    """Multiply the Q and K rows (and biases) of the given heads by k: attention logits scale by k^2."""
    c = model.config
    H, dh = c.num_attention_heads, c.hidden_size // c.num_attention_heads
    for hh in heads:
        l, h = map(int, hh.split("."))
        att = model.gpt_neox.layers[l].attention
        W = att.query_key_value.weight.data.view(H, 3, dh, -1)
        W[h, :2] *= k
        if att.query_key_value.bias is not None:
            att.query_key_value.bias.data.view(H, 3, dh)[h, :2] *= k


def calibrate(model, tok, apply, lo, hi, target, l0, iters=12, grow=True):
    """Find a strength x in [lo, hi] with loss increase ~ target for a damage apply(x) (restored after each probe)."""
    base = {n: p.data.clone() for n, p in model.named_parameters()}

    def probe(x):
        apply(x)
        dl = lm_loss(model, tok) - l0
        for n, p in model.named_parameters():
            p.data.copy_(base[n])
        return dl
    if grow:  # expand the upper bound until it overshoots the target
        while probe(hi) < target and hi < 1e6:
            lo, hi = hi, hi * 2
    for _ in range(iters):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if probe(mid) < target else (lo, mid)
    x = (lo + hi) / 2
    del base
    return x


@torch.no_grad()
def distance_to(model, ref):
    """Relative L2 distance of the current weights to a reference state, by module type."""
    out = {}
    for n, p in model.named_parameters():
        key = "emb" if "embed" in n else "ln" if "layernorm" in n or "norm" in n else "attn" if "attention" in n else "mlp" if "mlp" in n else "other"
        num, den = out.get(key, (0.0, 0.0))
        out[key] = (num + (p.data - ref[n]).float().pow(2).sum().item(), den + ref[n].float().pow(2).sum().item())
    return {k: round(math.sqrt(a / b), 6) for k, (a, b) in out.items()}


@torch.no_grad()
def roles(model, tok):
    """Per-head previous-token attention (natural text) and induction attention (repeated random tokens)."""
    set_attn(model, "eager")
    from datasets import load_dataset
    ds = load_dataset("NeelNanda/pile-10k", split="train", cache_dir=str(mc.HF_CACHE))
    prev = []
    for t in ds["text"][:200]:
        ids = tok(t, add_special_tokens=False)["input_ids"][:128]
        if len(ids) < 128:
            continue
        att = model(torch.tensor([ids], device="cuda"), output_attentions=True).attentions
        p = torch.arange(1, 128)
        prev.append(torch.stack([a[0, :, p, p - 1].float().mean(-1).cpu() for a in att]))
        if len(prev) == 24:
            break
    rng = np.random.default_rng(0)
    b = torch.tensor(rng.integers(1000, 49000, size=(16, 64)))
    att = model(torch.cat([b, b], 1).cuda(), output_attentions=True).attentions
    q = torch.arange(64, 127)
    ind = torch.stack([a[:, :, q, q - 63].float().mean((0, 2)).cpu() for a in att])
    set_attn(model, "sdpa")
    return torch.stack(prev).mean(0).numpy(), ind.numpy()


def evaluate(model, tok, prompts):
    model.eval()
    res = {"tasks": {}}
    with torch.no_grad():
        for t, items in prompts.items():
            res["tasks"]["fv:" + t] = eval_fv(model, items)
        for t in ELEMENTARY:
            res["tasks"]["el:" + t] = eval_el(model, tok, t)
        res["lm_loss"] = lm_loss(model, tok)
    p, i = roles(model, tok)
    res["prev"], res["ind"] = p.round(4).tolist(), i.round(4).tolist()
    model.train()
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", required=True)
    ap.add_argument("--lr", type=float, required=True)
    ap.add_argument("--local", required=True)
    ap.add_argument("--repo", default="EleutherAI/pythia-160m")
    ap.add_argument("--head", default="3.2")
    ap.add_argument("--steps", type=int, default=2000)
    ap.add_argument("--bs", type=int, default=128)
    ap.add_argument("--micro", type=int, default=32)
    ap.add_argument("--target_dloss", type=float, default=1.5)
    ap.add_argument("--tag", default=None)
    ap.add_argument("--warm", type=int, default=200)
    ap.add_argument("--fp32", action="store_true", help="no bf16 autocast (TF32 matmuls)")
    a = ap.parse_args()
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import transformers.models.gpt_neox.modeling_gpt_neox  # noqa: F401
    torch.manual_seed(0)
    torch.backends.cuda.matmul.allow_tf32 = True
    tag = a.tag or f"{a.arm}_lr{a.lr:g}"
    tok = AutoTokenizer.from_pretrained(a.repo, cache_dir=str(mc.HF_CACHE))
    model = AutoModelForCausalLM.from_pretrained(a.local, torch_dtype=torch.float32, attn_implementation="sdpa").cuda()
    prompts = {t: fv_prompts(tok, t) for t in ABSTRACTIVE + EXTRACTIVE}
    log = {"args": vars(a), "evals": {}}
    log["pre_damage"] = evaluate(model, tok, prompts)
    base_ref = {n: p.data.clone().cpu() for n, p in model.named_parameters()}
    if a.arm in ("H", "R"):
        gen = torch.Generator().manual_seed(1234)
        for hh in a.head.split(","):  # one or several heads, e.g. "3.2,3.0"
            l, h = map(int, hh.split("."))
            reinit_head(model, l, h, gen)
    elif a.arm == "O":  # overshoot: one huge step along the descent direction of a real training batch
        xb = torch.tensor(pq.read_table(SHARDS[3]).column("tokens").slice(50000, a.bs).to_pylist()).cuda()
        model.zero_grad(set_to_none=True)
        for mb in xb.split(a.micro):
            (model(mb, labels=mb).loss * (len(mb) / len(xb))).backward()
        gn = math.sqrt(sum(p.grad.float().pow(2).sum().item() for p in model.parameters() if p.grad is not None))
        grad = {n: (p.grad / gn).detach().clone() for n, p in model.named_parameters() if p.grad is not None}
        model.zero_grad(set_to_none=True)
        with torch.no_grad():
            st = calibrate(model, tok, lambda x: overshoot(model, x, grad), 0.0, 1.0, a.target_dloss, log["pre_damage"]["lm_loss"])
            overshoot(model, st, grad)
        log["overshoot_step"] = st
        del grad
    elif a.arm == "Q":  # attention-logit blow-up on the given heads
        heads = a.head.split(",")
        with torch.no_grad():
            k = calibrate(model, tok, lambda x: scale_qk(model, heads, 1 + x), 0.0, 1.0, a.target_dloss, log["pre_damage"]["lm_loss"])
            scale_qk(model, heads, 1 + k)
        log["qk_scale"] = 1 + k
    elif a.arm == "N":
        base = {n: p.data.clone() for n, p in model.named_parameters() if p.dim() == 2}
        l0 = log["pre_damage"]["lm_loss"]
        lo, hi, alpha = 0.0, 1.0, None
        for _ in range(10):  # bisection on alpha for the target loss increase
            mid = (lo + hi) / 2
            add_noise(model, mid, seed=4321)
            dl = lm_loss(model, tok) - l0
            for n, p in model.named_parameters():
                if n in base:
                    p.data.copy_(base[n])
            lo, hi = (mid, hi) if dl < a.target_dloss else (lo, mid)
            alpha = mid
        add_noise(model, alpha, seed=4321)
        log["alpha"] = alpha
        del base
    data = Data(a.bs)
    opt = torch.optim.AdamW(model.parameters(), lr=a.lr, betas=(0.9, 0.95), weight_decay=0.01, eps=1e-8)
    model.train()
    t0 = time.time()
    for step in range(a.steps + 1):
        if step in EVAL_STEPS:
            log["evals"][step] = evaluate(model, tok, prompts)
            e = log["evals"][step]
            e["dist_to_pre"] = distance_to(model, {n: v.cuda() for n, v in base_ref.items()})
            fv = np.mean([v["acc"] for k, v in e["tasks"].items() if k.startswith("fv:")])
            print(json.dumps({"tag": tag, "step": step, "loss": round(e["lm_loss"], 4), "fv_mean": round(float(fv), 4),
                              "ind": round(e["tasks"]["el:induction"]["acc"], 3), "sec": round(time.time() - t0)}), flush=True)
            OUT.mkdir(parents=True, exist_ok=True)
            (OUT / f"{tag}.json").write_text(json.dumps(log))
        if step == a.steps:
            break
        for g in opt.param_groups:
            g["lr"] = a.lr * min(1.0, (step + 1) / a.warm)
        x = data.next().cuda()
        opt.zero_grad(set_to_none=True)
        for mb in x.split(a.micro):
            with torch.autocast("cuda", dtype=torch.bfloat16, enabled=not a.fp32):
                loss = model(mb, labels=mb).loss * (len(mb) / len(x))
            loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
    log["seconds"] = time.time() - t0
    (OUT / f"{tag}.json").write_text(json.dumps(log))


if __name__ == "__main__":
    main()
