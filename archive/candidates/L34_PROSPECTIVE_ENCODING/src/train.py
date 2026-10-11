"""L34 E01 — minimal full-finetuning loop (fp32 master weights + bf16 autocast)."""
import math, random, time
import torch
from torch.nn.utils import clip_grad_norm_

MAX_LEN = 176
CE_CHUNK = 8


def encode(tok, samples):
    """-> list of (ids, loss_mask). Bio: loss on all tokens. QA: loss on answer only."""
    out = []
    for s in samples:
        p = tok(s["prompt"], add_special_tokens=False)["input_ids"] if s["prompt"] else []
        t = tok(s["target"], add_special_tokens=False)["input_ids"]
        ids = ([tok.bos_token_id] if tok.bos_token_id is not None else []) + p + t + [tok.eos_token_id]
        m = [0] * (len(ids) - len(t) - 1) + [1] * (len(t) + 1)
        out.append((ids[:MAX_LEN], m[:MAX_LEN]))
    return out


def batches(enc, bs, rng):
    idx = list(range(len(enc)))
    rng.shuffle(idx)
    # length-bucketed within large chunks to cut padding without breaking shuffling
    chunk = bs * 32
    for i in range(0, len(idx), chunk):
        blk = sorted(idx[i:i + chunk], key=lambda j: len(enc[j][0]))
        bs_list = [blk[j:j + bs] for j in range(0, len(blk), bs)]
        rng.shuffle(bs_list)
        for b in bs_list:
            yield b


def collate(enc, b, pad, device):
    L = max(len(enc[j][0]) for j in b)
    ids = torch.full((len(b), L), pad, dtype=torch.long)
    msk = torch.zeros((len(b), L), dtype=torch.long)
    lm = torch.zeros((len(b), L), dtype=torch.long)
    for k, j in enumerate(b):
        x, m = enc[j]
        ids[k, :len(x)] = torch.tensor(x)
        msk[k, :len(x)] = 1
        lm[k, :len(m)] = torch.tensor(m)
    return ids.to(device), msk.to(device), lm.to(device)


def train_phase(model, tok, samples, epochs, lr, seed, bs=64, log=print, tag=""):
    if not samples:
        log(f"[{tag}] empty phase, skipped")
        return
    device = next(model.parameters()).device
    enc = encode(tok, samples)
    rng = random.Random(seed)
    nsteps = epochs * math.ceil(len(enc) / bs)
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.0, betas=(0.9, 0.95), eps=1e-8)
    warm = max(10, int(0.03 * nsteps))
    sched = torch.optim.lr_scheduler.LambdaLR(
        opt, lambda s: s / warm if s < warm else 0.5 * (1 + math.cos(math.pi * (s - warm) / max(1, nsteps - warm))))
    pad = tok.pad_token_id if tok.pad_token_id is not None else 0
    model.train()
    model.gradient_checkpointing_enable()
    model.config.use_cache = False
    step, t0, acc = 0, time.time(), []
    for ep in range(epochs):
        for b in batches(enc, bs, rng):
            ids, msk, lm = collate(enc, b, pad, device)
            with torch.autocast("cuda", dtype=torch.bfloat16):
                logits = model(input_ids=ids, attention_mask=msk).logits[:, :-1]
            tgt = ids[:, 1:]
            w = lm[:, 1:].float()
            denom = w.sum().clamp(min=1)
            # chunked fp32 cross-entropy: numerically the same, but never materialises
            # the full fp32 logit tensor (128k vocab would cost several GB at peak)
            loss = 0.0
            for c0 in range(0, logits.size(0), CE_CHUNK):
                c1 = min(c0 + CE_CHUNK, logits.size(0))
                lc = logits[c0:c1].float()
                ls = torch.nn.functional.cross_entropy(
                    lc.reshape(-1, lc.size(-1)), tgt[c0:c1].reshape(-1),
                    reduction="none").view_as(tgt[c0:c1])
                loss = loss + (ls * w[c0:c1]).sum() / denom
            loss.backward()
            clip_grad_norm_(model.parameters(), 1.0)
            opt.step(); sched.step(); opt.zero_grad(set_to_none=True)
            acc.append(loss.item()); step += 1
            if step % 100 == 0 or step == nsteps:
                log(f"[{tag}] ep{ep} step {step}/{nsteps} loss {sum(acc[-100:])/len(acc[-100:]):.4f} "
                    f"lr {sched.get_last_lr()[0]:.2e} {time.time()-t0:.0f}s")
    del opt
    torch.cuda.empty_cache()
    log(f"[{tag}] done {step} steps, final loss {sum(acc[-50:])/len(acc[-50:]):.4f}, {time.time()-t0:.0f}s")
