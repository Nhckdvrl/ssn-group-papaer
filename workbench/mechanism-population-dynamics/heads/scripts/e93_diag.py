"""E93 diagnostic: why does the undamaged control drift during continued training even at a tiny learning rate?

Usage: e93_diag.py --variant NAME --local DIR [--lr 3e-6] [--data neel|pile10k] [--beta2 0.95] [--eps 1e-8] [--steps 200]
Logs every 20 steps: validation loss on the 48 fixed pile-10k documents used everywhere (docs 1000-3000 region),
held-out loss on unseen NeelNanda sequences, and the training-batch loss. Writes results/e93diag/<variant>.json.
"""
import argparse
import json

import numpy as np
import pyarrow.parquet as pq
import torch

import mp_common as mc
from e89_labor import lm_loss

OUT = mc.RESULTS / "e93diag"


def pile10k_stream(tok, bs, T=1024):
    """Training sequences from pile-10k documents 4000+ (disjoint from the validation documents 1000-3000)."""
    from datasets import load_dataset
    ds = load_dataset("NeelNanda/pile-10k", split="train", cache_dir=str(mc.HF_CACHE))
    buf = []
    for t in ds["text"][4000:]:
        buf += tok(t, add_special_tokens=False)["input_ids"] + [tok.eos_token_id]
    arr = np.array(buf[: (len(buf) // T) * T]).reshape(-1, T)
    i = 0
    while True:
        if i + bs > len(arr):
            i = 0
        yield torch.tensor(arr[i:i + bs])
        i += bs


def neel_stream(bs):
    tab = pq.read_table(mc.CACHE / "pile_tok" / "shard00000.parquet")
    i = 0
    while True:
        yield torch.tensor(tab.column("tokens").slice(i, bs).to_pylist())
        i += bs


@torch.no_grad()
def heldout(model, x):
    return float(np.mean([model(x[j:j + 16].cuda(), labels=x[j:j + 16].cuda()).loss.item() for j in range(0, len(x), 16)]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", required=True)
    ap.add_argument("--local", required=True)
    ap.add_argument("--lr", type=float, default=3e-6)
    ap.add_argument("--data", default="neel")
    ap.add_argument("--beta2", type=float, default=0.95)
    ap.add_argument("--eps", type=float, default=1e-8)
    ap.add_argument("--steps", type=int, default=200)
    ap.add_argument("--bs", type=int, default=128)
    ap.add_argument("--attn", default="sdpa")
    ap.add_argument("--warm", type=int, default=50)
    ap.add_argument("--fp32", action="store_true", help="no bf16 autocast (TF32 matmuls)")
    a = ap.parse_args()
    torch.backends.cuda.matmul.allow_tf32 = True
    from transformers import AutoModelForCausalLM, AutoTokenizer
    torch.manual_seed(0)
    tok = AutoTokenizer.from_pretrained("EleutherAI/pythia-160m", cache_dir=str(mc.HF_CACHE))
    model = AutoModelForCausalLM.from_pretrained(a.local, torch_dtype=torch.float32, attn_implementation=a.attn).cuda()
    held = torch.tensor(pq.read_table(mc.CACHE / "pile_tok" / "shard00003.parquet").column("tokens").slice(100000, 64).to_pylist())
    data = neel_stream(a.bs) if a.data == "neel" else pile10k_stream(tok, a.bs)
    opt = torch.optim.AdamW(model.parameters(), lr=a.lr, betas=(0.9, a.beta2), weight_decay=0.01, eps=a.eps)
    log = {"args": vars(a), "rows": []}
    model.eval()
    log["rows"].append({"step": 0, "val": lm_loss(model, tok), "neel_heldout": heldout(model, held), "train": None})
    for step in range(1, a.steps + 1):
        model.train()
        for g in opt.param_groups:
            g["lr"] = a.lr * min(1.0, step / a.warm)
        x = next(data).cuda()
        opt.zero_grad(set_to_none=True)
        tl = 0.0
        for mb in x.split(32):
            with torch.autocast("cuda", dtype=torch.bfloat16, enabled=not a.fp32):
                loss = model(mb, labels=mb).loss * (len(mb) / len(x))
            loss.backward()
            tl += loss.item()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
        if step % 20 == 0:
            model.eval()
            row = {"step": step, "val": lm_loss(model, tok), "neel_heldout": heldout(model, held), "train": tl}
            log["rows"].append(row)
            print(json.dumps({"variant": a.variant, **{k: (round(v, 4) if isinstance(v, float) else v) for k, v in row.items()}}), flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{a.variant}.json").write_text(json.dumps(log))


if __name__ == "__main__":
    main()
