"""L30 E01 trainer: matched P / S / D_mask / D_rt fine-tuning of Gemma-2-2B.

Hyperparameters follow An et al.'s Response Tuning repo (LoRA r=64, alpha=16,
dropout 0.1, all linear projections; constant LR 1e-4; effective batch 64;
max_grad_norm 0.3; loss on response tokens only). Two documented deviations,
both fixed before any outcome was inspected:

  1. LoRA adapters sit on a bf16 backbone rather than a 4-bit NF4 backbone.
     The 96GB cards make quantisation unnecessary, and removing it removes a
     noise source that is irrelevant to the estimand. It is applied identically
     to all four arms, so it cannot bias a contrast.
  2. Sequences are built by concatenating separately tokenised segments rather
     than by string-matching a response template. This makes the loss mask and
     the D_mask attention boundary exact rather than inferred.

Every arm sees the same response multiset in the same order at the same step
with the same number of loss tokens; only the instruction-side information
differs.
"""
import argparse
import json
import math
import os
import pathlib
import random
import sys
import time

import torch
import torch.nn as nn

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from arms import build_example  # noqa: E402

TARGETS = ("q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj")


# ---------------------------------------------------------------- model / LoRA
class LoRALinear(nn.Module):
    def __init__(self, base: nn.Linear, r=64, alpha=16, dropout=0.1):
        super().__init__()
        self.base = base
        for p in self.base.parameters():
            p.requires_grad_(False)
        self.r, self.scaling = r, alpha / r
        self.lora_A = nn.Parameter(torch.empty(r, base.in_features, dtype=torch.float32))
        self.lora_B = nn.Parameter(torch.zeros(base.out_features, r, dtype=torch.float32))
        nn.init.kaiming_uniform_(self.lora_A, a=math.sqrt(5))
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        out = self.base(x)
        h = self.dropout(x).to(torch.float32)
        delta = (h @ self.lora_A.t()) @ self.lora_B.t()
        return out + (delta * self.scaling).to(out.dtype)


def apply_lora(model, r=64, alpha=16, dropout=0.1):
    # Freeze the whole backbone FIRST. Wrapping only the target Linears leaves
    # `embed_tokens` (256000 x 2304 = 590M params, tied to lm_head) trainable,
    # which silently turns the run into partial full fine-tuning -- caught by
    # the trainable-parameter count in the throughput benchmark.
    for p in model.parameters():
        p.requires_grad_(False)
    n = 0
    for layer in model.model.layers:
        for parent in (layer.self_attn, layer.mlp):
            for name, child in list(parent.named_children()):
                if name in TARGETS and isinstance(child, nn.Linear):
                    setattr(parent, name, LoRALinear(child, r, alpha, dropout))
                    n += 1
    trainable = {k for k, _ in model.named_parameters() if "lora_" in k}
    for k, p in model.named_parameters():
        p.requires_grad_(k in trainable)
    return n


def load_backbone(model_id, device="cuda", dtype=torch.bfloat16):
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from arms import SEG_ASST_OPEN, SEG_USER_OPEN

    tok = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(
        model_id, dtype=dtype, attn_implementation="eager"
    ).to(device)
    model.config.use_cache = False
    special = {
        "bos_id": tok.bos_token_id,
        "eos_id": tok.eos_token_id,
        "user_open_ids": tok(SEG_USER_OPEN, add_special_tokens=False)["input_ids"],
        "asst_open_ids": tok(SEG_ASST_OPEN, add_special_tokens=False)["input_ids"],
    }
    return model, tok, special


# ------------------------------------------------------------------- attention
def build_attention_bias(id_lists, block_froms, dtype, device):
    """Additive (B,1,L,L) mask: causal, padding-aware, plus the D_mask block.

    For a D_mask example with boundary `b`, every query position i >= b is
    forbidden to attend to keys 1 <= j < b (the user-open segment and the
    instruction). BOS (j=0) and causal self-attention are preserved, so the
    response's information set is exactly {BOS} + assistant-open + response.
    """
    b = len(id_lists)
    L = max(len(x) for x in id_lists)
    neg = torch.finfo(dtype).min
    allow = torch.zeros(b, 1, L, L, dtype=torch.bool, device=device)
    idx = torch.arange(L, device=device)
    causal = idx[:, None] >= idx[None, :]
    for k, ids in enumerate(id_lists):
        n = len(ids)
        m = causal.clone()
        m[:, n:] = False  # never attend to padding keys
        bf = block_froms[k] if block_froms is not None else None
        if bf is not None:
            blocked_q = idx[:, None] >= bf
            blocked_k = (idx[None, :] >= 1) & (idx[None, :] < bf)
            m = m & ~(blocked_q & blocked_k)
        allow[k, 0] = m
    return torch.where(allow, torch.zeros((), dtype=dtype, device=device),
                       torch.full((), neg, dtype=dtype, device=device))


def as_mask_mapping(bias, model):
    """Wrap a 4D bias so Gemma-2 uses it verbatim on every layer.

    transformers >= 5 only honours a caller-supplied mask when `attention_mask`
    is a dict keyed by attention type; anything else is rebuilt by
    `create_causal_mask` / `create_sliding_window_causal_mask`, which silently
    discarded most of the D_mask block (caught by src/test_masks.py). Gemma-2
    alternates full and sliding-window layers, but the pool's worst-case
    sequence is far shorter than the 4096-token window, so the window is a
    no-op and the same bias is correct for both layer types. The assert keeps
    that equivalence from being violated silently.
    """
    win = getattr(model.config, "sliding_window", None)
    if win is not None:
        assert bias.shape[-1] <= win, (
            f"sequence {bias.shape[-1]} exceeds sliding window {win}; the shared "
            "bias would no longer equal a true sliding-window mask"
        )
    return {"full_attention": bias, "sliding_attention": bias}


# ------------------------------------------------------------------------ data
def load_pool(pool_dir):
    rows = [json.loads(l) for l in (pathlib.Path(pool_dir) / "pool.jsonl").open()]
    perm = json.loads((pathlib.Path(pool_dir) / "perm.json").read_text())["perm"]
    return rows, perm


def make_batch(rows, perm, order, arm, special, device, model=None):
    ids_list, loss_list, bf_list = [], [], []
    for i in order:
        r = rows[i]
        x_ids = rows[perm[i]]["x_ids"] if arm == "S" else r["x_ids"]
        ids, loss, bf = build_example(
            x_ids, r["y_ids"], arm, special["bos_id"], special["eos_id"],
            special["user_open_ids"], special["asst_open_ids"],
        )
        ids_list.append(ids)
        loss_list.append(loss)
        bf_list.append(bf)
    L = max(len(x) for x in ids_list)
    pad = special["eos_id"]
    inp = torch.full((len(ids_list), L), pad, dtype=torch.long)
    lm = torch.zeros((len(ids_list), L), dtype=torch.bool)
    for k, (ids, loss) in enumerate(zip(ids_list, loss_list)):
        inp[k, : len(ids)] = torch.tensor(ids)
        lm[k, : len(loss)] = torch.tensor(loss, dtype=torch.bool)
    bias = build_attention_bias(ids_list, bf_list, torch.bfloat16, device)
    return inp.to(device), lm.to(device), (as_mask_mapping(bias, model) if model is not None else bias)


# -------------------------------------------------------------------- training
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", required=True, choices=["P", "S", "D_mask", "D_rt"])
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--model", default="google/gemma-2-2b")
    ap.add_argument("--pool", default=str(ROOT / "results" / "pool"))
    ap.add_argument("--out", default=None)
    ap.add_argument("--epochs", type=float, default=3.0)
    ap.add_argument("--micro-batch", type=int, default=8)
    ap.add_argument("--effective-batch", type=int, default=64)
    ap.add_argument("--lr", type=float, default=1e-4)
    ap.add_argument("--max-grad-norm", type=float, default=0.3)
    ap.add_argument("--lora-r", type=int, default=64)
    ap.add_argument("--lora-alpha", type=int, default=16)
    ap.add_argument("--lora-dropout", type=float, default=0.1)
    ap.add_argument("--limit", type=int, default=None, help="debug: truncate pool")
    ap.add_argument("--max-steps", type=int, default=None, help="debug: stop early")
    args = ap.parse_args()

    out = pathlib.Path(args.out or ROOT / "results" / "runs" / f"{args.arm}_s{args.seed}")
    out.mkdir(parents=True, exist_ok=True)

    torch.manual_seed(args.seed)
    random.seed(args.seed)

    rows, perm = load_pool(args.pool)
    if args.limit:
        rows, perm = rows[: args.limit], [p % args.limit for p in perm[: args.limit]]
    model, tok, special = load_backbone(args.model)
    n_lora = apply_lora(model, args.lora_r, args.lora_alpha, args.lora_dropout)
    model.to("cuda")
    model.gradient_checkpointing_enable()
    model.enable_input_require_grads()

    params = [p for p in model.parameters() if p.requires_grad]
    opt = torch.optim.AdamW(params, lr=args.lr, weight_decay=0.0)

    # Identical example order in every arm: the same response is seen at the
    # same step with the same number of loss tokens, so the only difference
    # between arms is the instruction-side information.
    order = list(range(len(rows)))
    random.Random(args.seed).shuffle(order)
    accum = args.effective_batch // args.micro_batch
    per_epoch = len(order) // args.effective_batch
    total_steps = int(per_epoch * args.epochs)
    if args.max_steps:
        total_steps = min(total_steps, args.max_steps)

    meta = {
        "arm": args.arm, "seed": args.seed, "model": args.model,
        "n_examples": len(rows), "lora_modules": n_lora,
        "trainable_params": sum(p.numel() for p in params),
        "epochs": args.epochs, "total_steps": total_steps,
        "effective_batch": args.effective_batch, "micro_batch": args.micro_batch,
        "lr": args.lr, "max_grad_norm": args.max_grad_norm,
        "lora": {"r": args.lora_r, "alpha": args.lora_alpha, "dropout": args.lora_dropout},
        "torch": torch.__version__,
    }
    (out / "meta.json").write_text(json.dumps(meta, indent=2) + "\n")
    print(json.dumps(meta))

    log = (out / "train_log.jsonl").open("w")
    model.train()
    t0 = time.time()
    cursor = 0
    for step in range(total_steps):
        opt.zero_grad(set_to_none=True)
        # Token-mean over the whole effective batch, so the gradient scale is
        # identical across arms (they share the same loss-token counts).
        batch_idx = []
        for _ in range(accum):
            sl = [order[(cursor + k) % len(order)] for k in range(args.micro_batch)]
            cursor += args.micro_batch
            batch_idx.append(sl)
        denom = sum(len(rows[i]["y_ids"]) + 1 for sl in batch_idx for i in sl)

        tot = 0.0
        for sl in batch_idx:
            inp, lm, bias = make_batch(rows, perm, sl, args.arm, special, "cuda", model)
            logits = model(input_ids=inp, attention_mask=bias).logits
            shift_logits = logits[:, :-1].float()
            shift_labels = inp[:, 1:]
            shift_mask = lm[:, 1:]
            ls = nn.functional.cross_entropy(
                shift_logits.reshape(-1, shift_logits.size(-1)),
                shift_labels.reshape(-1),
                reduction="none",
            ).view(shift_labels.shape)
            loss = (ls * shift_mask).sum() / denom
            loss.backward()
            tot += loss.item()
            del logits, shift_logits, ls

        gn = torch.nn.utils.clip_grad_norm_(params, args.max_grad_norm)
        opt.step()
        # Per-epoch adapters: the training-length trajectory then costs only
        # evaluation, not retraining. Epoch 3 is the pre-registered primary.
        if per_epoch and (step + 1) % per_epoch == 0:
            ep = (step + 1) // per_epoch
            torch.save(
                {"lora": {k: v.detach().to(torch.float32).cpu()
                          for k, v in model.state_dict().items() if "lora_" in k},
                 "meta": {**meta, "epoch": ep, "step": step + 1}},
                out / f"adapter_ep{ep}.pt",
            )
        if step % 10 == 0 or step == total_steps - 1:
            rec = {"step": step, "loss": tot, "grad_norm": float(gn),
                   "elapsed": round(time.time() - t0, 1)}
            log.write(json.dumps(rec) + "\n")
            log.flush()
            print(rec, flush=True)
    log.close()

    sd = {k: v.detach().to(torch.float32).cpu()
          for k, v in model.state_dict().items() if "lora_" in k}
    torch.save({"lora": sd, "meta": meta}, out / "adapter.pt")
    (out / "DONE").write_text(json.dumps({"seconds": round(time.time() - t0, 1)}) + "\n")
    print("saved", out)


if __name__ == "__main__":
    main()
