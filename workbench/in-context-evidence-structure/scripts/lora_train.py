"""E18: LoRA on synthetic classification streams with (vol) or without (stat) in-context rule changes.

Episodes: nonce attribute-rule classification (n_attr in {3,4,5}, T=16 demos, nonce attribute names /
labels from the candidate bank), label noise eps in {0, .1, .2}.
  stat : rule fixed within the episode
  vol  : rule follows an HMM (hazard lam in {.05, .1, .2}); switches go to any other rule
         (reversal or another attribute)
Loss: next-label prediction at EVERY demo's label slot ('Label:' -> label word), i.e. sequential
in-context classification.  Identical data budget / hyper-parameters for both arms.
"""
import argparse, json, math, os, sys, time
from pathlib import Path
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, get_peft_model

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ices.generator import load_lexicon, render, Base  # noqa

T = 16


def episode(rng, arm, attr_bank, label_bank):
    n = int(rng.choice([3, 4, 5]))
    names = list(rng.choice(attr_bank, n, replace=False))
    while True:
        lw = list(rng.choice(label_bank, 2, replace=False))
        if lw[0][0] != lw[1][0]:
            break
    X = rng.integers(0, 2, size=(T + 1, n))
    a, s = int(rng.integers(n)), int(rng.integers(2))
    lam = 0.0 if arm == "stat" else float(rng.choice([.05, .1, .2]))
    eps = float(rng.choice([0, .1, .2]))
    labs = []
    for t in range(T):
        if t > 0 and rng.random() < lam:
            while True:
                a2, s2 = int(rng.integers(n)), int(rng.integers(2))
                if (a2, s2) != (a, s):
                    a, s = a2, s2; break
        y = int(X[t, a]) ^ s
        if rng.random() < eps:
            y = 1 - y
        labs.append(y)
    base = Base("tr", n, T, names, lw, a, s, X[:T].tolist(), X[T].tolist())
    return render(base, labs), lw, labs


def tokenize(tok, text, lw, labs):
    """Return input ids and a label mask selecting the first token of each demo label word."""
    enc = tok(text, return_offsets_mapping=True, add_special_tokens=False)
    ids, offs = enc["input_ids"], enc["offset_mapping"]
    targets = [-100] * len(ids)
    pos = 0
    for t, y in enumerate(labs):
        k = text.find("Label: ", pos) + len("Label: ")
        pos = k
        for i, (s0, e0) in enumerate(offs):
            if s0 <= k < e0 or s0 == k:
                targets[i] = ids[i]; break
    return ids, targets


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-8B"); ap.add_argument("--arm", required=True)
    ap.add_argument("--n_episodes", type=int, default=6000); ap.add_argument("--bs", type=int, default=8)
    ap.add_argument("--lr", type=float, default=1e-4); ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    attr_bank, label_bank = load_lexicon(os.environ.get("LEXICON"))
    tok = AutoTokenizer.from_pretrained(a.model)
    model = AutoModelForCausalLM.from_pretrained(a.model, dtype=torch.bfloat16, device_map="cuda")
    model.gradient_checkpointing_enable(); model.enable_input_require_grads()
    model = get_peft_model(model, LoraConfig(r=16, lora_alpha=32, lora_dropout=0.0, task_type="CAUSAL_LM",
                                             target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                                                             "gate_proj", "up_proj", "down_proj"]))
    model.print_trainable_parameters()
    rng = np.random.default_rng(a.seed); torch.manual_seed(a.seed)
    opt = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=a.lr, weight_decay=0.0)
    steps = a.n_episodes // a.bs
    sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda s: min(1, s / 20) * 0.5 * (1 + math.cos(math.pi * s / steps)))
    pad = tok.pad_token_id if tok.pad_token_id is not None else 0
    t0 = time.time()
    for step in range(steps):
        batch = [tokenize(tok, *episode(rng, a.arm, attr_bank, label_bank)) for _ in range(a.bs)]
        L = max(len(i) for i, _ in batch)
        ids = torch.full((a.bs, L), pad); tg = torch.full((a.bs, L), -100); att = torch.zeros((a.bs, L), dtype=torch.long)
        for j, (i, t) in enumerate(batch):
            ids[j, :len(i)] = torch.tensor(i); tg[j, :len(t)] = torch.tensor(t); att[j, :len(i)] = 1
        out = model(input_ids=ids.cuda(), attention_mask=att.cuda(), labels=tg.cuda())
        out.loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step(); sched.step(); opt.zero_grad()
        if step % 50 == 0:
            print(f"step {step}/{steps} loss {out.loss.item():.4f} {time.time()-t0:.0f}s", flush=True)
    model = model.merge_and_unload()
    model.save_pretrained(a.out); tok.save_pretrained(a.out)
    json.dump(vars(a), open(os.path.join(a.out, "lora_args.json"), "w"))
    print("saved", a.out)


if __name__ == "__main__":
    main()
