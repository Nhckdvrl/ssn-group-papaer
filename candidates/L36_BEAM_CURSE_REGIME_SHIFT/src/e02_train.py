"""L36 E02 — matched SFT with a single shared boundary symbol, measured online.

One condition per invocation (`A_ONLY`, `B_ONLY`, `MIXED`, `A_ONLY_NOEOSLOSS`). Every `--eval-every`
optimizer steps the script measures, in **both** surface formats, where the boundary token sits in
the next-token distribution at the first generated position. Behavioural cells (greedy quality and
a RAW beam sweep) are run at the checkpoints named by `--behaviour-at`.

Nothing is stored except the measurement stream and the final weights, per
`E02_PREREGISTRATION.md` §7.
"""

import argparse
import json
import math
import os
import random
import sys
import time

import numpy as np
import torch
from torch.utils.data import DataLoader, Dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, get_cosine_schedule_with_warmup

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
import mt_metrics as M                       # noqa: E402
from termination import step0_termination_stats   # noqa: E402

FMT_A = ("### User: Translate the following English sentence into German.\n{src}\n"
         "### Assistant: ")
FMT_B = ("English: {src}\nGerman: ")
FORMATS = {"A": FMT_A, "B": FMT_B}
END_TOKEN = "<|quad_start|>"          # unused Qwen2.5 special token, id 151650


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--base", default="Qwen/Qwen2.5-3B")
    p.add_argument("--condition", required=True,
                   choices=["A_ONLY", "B_ONLY", "MIXED", "A_ONLY_NOEOSLOSS"])
    p.add_argument("--epochs", type=int, default=3)
    p.add_argument("--batch", type=int, default=4)
    p.add_argument("--accum", type=int, default=2)
    p.add_argument("--lr", type=float, default=1e-5)
    p.add_argument("--warmup", type=int, default=20)
    p.add_argument("--max-len", type=int, default=256)
    p.add_argument("--eval-every", type=int, default=50)
    p.add_argument("--eval-n", type=int, default=200)
    p.add_argument("--behaviour-at", default="0,200,600,final")
    p.add_argument("--beams", default="1,16,64")
    p.add_argument("--beam-n", type=int, default=200)
    p.add_argument("--seed", type=int, default=20260914)
    p.add_argument("--out", default=None)
    p.add_argument("--max-steps", type=int, default=0)
    return p.parse_args()


class SFTData(Dataset):
    def __init__(self, src, tgt, condition, tok, max_len, seed):
        self.rows = []
        rng = random.Random(seed)
        for i, (s, t) in enumerate(zip(src, tgt)):
            if condition.startswith("A_ONLY"):
                fmt = "A"
            elif condition == "B_ONLY":
                fmt = "B"
            else:
                fmt = "A" if i % 2 == 0 else "B"     # fixed partition, not resampled
            self.rows.append((fmt, s, t))
        rng.shuffle(self.rows)
        self.tok, self.max_len = tok, max_len
        self.end_id = tok.convert_tokens_to_ids(END_TOKEN)

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, i):
        fmt, s, t = self.rows[i]
        prompt = FORMATS[fmt].format(src=s)
        p_ids = self.tok(prompt, add_special_tokens=False)["input_ids"]
        t_ids = self.tok(t, add_special_tokens=False)["input_ids"] + [self.end_id]
        ids = (p_ids + t_ids)[:self.max_len]
        labels = ([-100] * len(p_ids) + t_ids)[:self.max_len]
        return {"input_ids": ids, "labels": labels}


def collate(batch, pad_id, mask_end_id=None):
    n = max(len(b["input_ids"]) for b in batch)
    ids, labels, attn = [], [], []
    for b in batch:
        k = n - len(b["input_ids"])
        ids.append(b["input_ids"] + [pad_id] * k)
        lab = b["labels"] + [-100] * k
        if mask_end_id is not None:                      # secondary control arm
            lab = [-100 if x == mask_end_id else x for x in lab]
        labels.append(lab)
        attn.append([1] * len(b["input_ids"]) + [0] * k)
    return (torch.tensor(ids), torch.tensor(labels), torch.tensor(attn))


@torch.no_grad()
def measure_step0(model, tok, srcs, end_id, batch=8):
    """rank / margin / log p of the boundary token at the first generated position, per format."""
    model.eval()
    out = {}
    for fmt, template in FORMATS.items():
        margins, lps, ranks = [], [], []
        for i in range(0, len(srcs), batch):
            prompts = [template.format(src=s) for s in srcs[i:i + batch]]
            enc = tok(prompts, return_tensors="pt", padding=True,
                      add_special_tokens=False).to(model.device)
            logits = model(**enc).logits[:, -1]
            st = step0_termination_stats(logits, [end_id])
            margins.extend(st["margin"].tolist())
            lps.extend(st["log_p_stop"].tolist())
            ranks.extend(st["rank_stop"].tolist())
        out[fmt] = {"margin_mean": float(np.mean(margins)),
                    "log_p_stop_mean": float(np.mean(lps)),
                    "rank_median": float(np.median(ranks)),
                    "log10_rank_median": float(np.log10(max(np.median(ranks), 1.0))),
                    "frac_rank_le_128": float(np.mean([r <= 128 for r in ranks])),
                    "ranks": ranks}
    model.train()
    return out


@torch.no_grad()
def measure_behaviour(model, tok, srcs, refs, end_id, beams, ref_len, batch_budget=256):
    model.eval()
    out = {}
    for fmt, template in FORMATS.items():
        out[fmt] = {}
        for beam in beams:
            bs = max(1, batch_budget // beam)
            hyps = [None] * len(srcs)
            order = sorted(range(len(srcs)), key=lambda i: -len(srcs[i]))
            for s in range(0, len(order), bs):
                idx = order[s:s + bs]
                enc = tok([template.format(src=srcs[i]) for i in idx], return_tensors="pt",
                          padding=True, add_special_tokens=False).to(model.device)
                gen = model.generate(**enc, num_beams=beam, do_sample=False, length_penalty=0.0,
                                     early_stopping=False, max_new_tokens=128, min_new_tokens=0,
                                     num_return_sequences=1, pad_token_id=tok.pad_token_id,
                                     eos_token_id=[end_id])
                gen = gen[:, enc["input_ids"].shape[1]:]
                for k, i in enumerate(idx):
                    hyps[i] = tok.decode(gen[k], skip_special_tokens=True).strip()
            st = np.array([M.bleu_segment_stats(h, r) for h, r in zip(hyps, refs)], float)
            out[fmt][str(beam)] = {
                "bleu_multi": M.bleu_from_stats(st.sum(0)),
                "empty_rate": float(np.mean([1.0 if not h.strip() else 0.0 for h in hyps])),
                "len_ratio": float(np.mean([len(h.split()) for h in hyps]) / ref_len),
                "sample": hyps[:3]}
    model.train()
    return out


def main():
    a = parse_args()
    torch.manual_seed(a.seed)
    random.seed(a.seed)
    np.random.seed(a.seed)

    data = os.path.join(ROOT, "data")
    tr_src = [l.rstrip("\n") for l in open(f"{data}/newstest2018.en", encoding="utf-8")]
    tr_tgt = [l.rstrip("\n") for l in open(f"{data}/newstest2018.ref.de", encoding="utf-8")]
    ev_src = [l.rstrip("\n") for l in open(f"{data}/newstest2019.en", encoding="utf-8")][:a.eval_n]
    ref_w = [l.rstrip("\n") for l in open(f"{data}/newstest2019.wmtref.de", encoding="utf-8")]
    ref_a = [l.rstrip("\n") for l in open(f"{data}/newstest2019.arref.de", encoding="utf-8")]
    refs = [[ref_w[i], ref_a[i]] for i in range(a.eval_n)]
    ref_len = float(np.mean([len(ref_w[i].split()) for i in range(a.eval_n)]))

    tok = AutoTokenizer.from_pretrained(a.base)
    tok.padding_side = "left"
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token
    end_id = tok.convert_tokens_to_ids(END_TOKEN)
    assert isinstance(end_id, int) and end_id > 0, END_TOKEN

    model = AutoModelForCausalLM.from_pretrained(a.base, dtype=torch.float32).cuda()
    model.gradient_checkpointing_enable()
    model.config.use_cache = False

    ds = SFTData(tr_src, tr_tgt, a.condition, tok, a.max_len, a.seed)
    mask_end = end_id if a.condition.endswith("NOEOSLOSS") else None
    dl = DataLoader(ds, batch_size=a.batch, shuffle=True, drop_last=True,
                    collate_fn=lambda b: collate(b, tok.pad_token_id, mask_end))
    total = (len(dl) // a.accum) * a.epochs
    if a.max_steps:
        total = min(total, a.max_steps)
    opt = torch.optim.AdamW(model.parameters(), lr=a.lr, weight_decay=0.0, betas=(0.9, 0.95))
    sched = get_cosine_schedule_with_warmup(opt, a.warmup, total)

    out_path = a.out or os.path.join(ROOT, "results", "e02", f"{a.condition}.jsonl")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    f = open(out_path, "w", encoding="utf-8")
    beh_at = set(a.behaviour_at.split(","))
    beams = [int(b) for b in a.beams.split(",")]

    header = {"_header": True, "condition": a.condition, "base": a.base, "end_token": END_TOKEN,
              "end_id": end_id, "epochs": a.epochs, "batch": a.batch, "accum": a.accum,
              "lr": a.lr, "warmup": a.warmup, "max_len": a.max_len, "total_steps": total,
              "eval_every": a.eval_every, "eval_n": a.eval_n, "seed": a.seed,
              "n_train": len(ds), "formats": FORMATS,
              "torch": torch.__version__, "gpu": torch.cuda.get_device_name(0)}
    f.write(json.dumps(header, ensure_ascii=False) + "\n")
    f.flush()
    print(json.dumps({k: header[k] for k in ("condition", "total_steps", "n_train", "end_id")}),
          flush=True)

    def record(step, loss_val, behaviour=False):
        m = measure_step0(model, tok, ev_src, end_id)
        row = {"step": step, "loss": loss_val,
               "rank_A": m["A"]["rank_median"], "rank_B": m["B"]["rank_median"],
               "log10_rank_A": m["A"]["log10_rank_median"],
               "log10_rank_B": m["B"]["log10_rank_median"],
               "margin_A": m["A"]["margin_mean"], "margin_B": m["B"]["margin_mean"],
               "logp_stop_A": m["A"]["log_p_stop_mean"], "logp_stop_B": m["B"]["log_p_stop_mean"],
               "exposed128_A": m["A"]["frac_rank_le_128"], "exposed128_B": m["B"]["frac_rank_le_128"]}
        if behaviour:
            row["behaviour"] = measure_behaviour(model, tok, ev_src[:a.beam_n], refs[:a.beam_n],
                                                 end_id, beams, ref_len)
        row["ranks_A"], row["ranks_B"] = m["A"]["ranks"], m["B"]["ranks"]
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
        f.flush()
        b = ""
        if behaviour:
            b = ("  |  A b64 empty %.1f%% BLEU %.1f   B b64 empty %.1f%% BLEU %.1f" % (
                100 * row["behaviour"]["A"]["64"]["empty_rate"], row["behaviour"]["A"]["64"]["bleu_multi"],
                100 * row["behaviour"]["B"]["64"]["empty_rate"], row["behaviour"]["B"]["64"]["bleu_multi"]))
        print(f"[{a.condition}] step {step:5d}  loss {loss_val:.4f}  "
              f"rank_A {row['rank_A']:9.0f}  rank_B {row['rank_B']:9.0f}{b}", flush=True)

    record(0, float("nan"), behaviour=("0" in beh_at))

    step, t0, running = 0, time.time(), 0.0
    done = False
    for ep in range(a.epochs):
        if done:
            break
        for i, (ids, labels, attn) in enumerate(dl):
            ids, labels, attn = ids.cuda(), labels.cuda(), attn.cuda()
            with torch.autocast("cuda", dtype=torch.bfloat16):
                out = model(input_ids=ids, attention_mask=attn, labels=labels)
            (out.loss / a.accum).backward()
            running += float(out.loss) / a.accum
            if (i + 1) % a.accum == 0:
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                opt.step()
                sched.step()
                opt.zero_grad(set_to_none=True)
                step += 1
                if step % a.eval_every == 0 or step == total:
                    record(step, running, behaviour=(str(step) in beh_at or
                                                     (step == total and "final" in beh_at)))
                    running = 0.0
                if step >= total:
                    done = True
                    break
    f.close()
    print(f"[{a.condition}] done in {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
