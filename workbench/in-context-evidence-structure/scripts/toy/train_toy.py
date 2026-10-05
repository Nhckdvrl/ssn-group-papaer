"""E12: does task-homogeneous training produce 'surface-time / latent-set' aggregation?

Token layout per demo: 5 attribute tokens (attr j value v -> id 2*j+v) + 1 label token.
Label tokens: pool of 24 ids (offset 10); each sequence draws 2 fresh labels (random roles).
Query = 5 attribute tokens; we read the logits of the two labels at the query's last attribute.
Loss: next-label prediction at every demo's last attribute position (in-context learning curve).

Families
  F1 rule-stationary : rule (a, s) fixed, label flip noise eps in {0, .05, .1, .2}
  F2 surface stream  : attributes random/irrelevant; label stream = 2-state HMM (hazard lam in
                       {0, .05, .1, .2}) + noise eps
  F3 rule-volatile   : rule follows an HMM over rules (hazard lam in {.05, .1, .2}; switches to any
                       other rule incl. reversal) + noise eps
Mixtures: hom = F1 + F2 (50/50), vol = F1 + F2 + F3 (1/3 each).
"""
import argparse, json, math, os, time
import numpy as np
import torch
import torch.nn as nn
from transformers import GPT2Config, GPT2LMHeadModel

NA, T = 5, 16
L0, NL = 10, 24                 # label token ids [10, 34)
SEQ = (NA + 1) * T + NA         # demos + query attributes
VOCAB = L0 + NL


def sample_family(fam, rng, B):
    X = rng.integers(0, 2, size=(B, T + 1, NA))
    labs = np.zeros((B, T), int)
    pairs = np.array([rng.choice(NL, 2, replace=False) for _ in range(B)])
    eps = rng.choice([0, .05, .1, .2], size=B)
    for b in range(B):
        if fam == "F2":
            lam = rng.choice([0, .05, .1, .2]); st = rng.integers(2)
            for t in range(T):
                if t > 0 and rng.random() < lam:
                    st = 1 - st
                labs[b, t] = st
            qrule = None
        else:
            a, s = rng.integers(NA), rng.integers(2)
            lam = 0.0 if fam == "F1" else rng.choice([.05, .1, .2])
            for t in range(T):
                if t > 0 and rng.random() < lam:
                    while True:
                        a2, s2 = rng.integers(NA), rng.integers(2)
                        if (a2, s2) != (a, s):
                            a, s = a2, s2; break
                labs[b, t] = X[b, t, a] ^ s
        flip = rng.random(T) < eps[b]
        labs[b] = labs[b] ^ flip
    return X, labs, pairs


def to_tokens(X, labs, pairs):
    B = X.shape[0]
    toks = np.zeros((B, SEQ), int)
    for t in range(T):
        toks[:, t * (NA + 1):t * (NA + 1) + NA] = X[:, t] * 1 + 2 * np.arange(NA)
        toks[:, t * (NA + 1) + NA] = L0 + pairs[np.arange(B), labs[:, t]]
    toks[:, T * (NA + 1):] = X[:, T] + 2 * np.arange(NA)
    return toks


def make_batch(mix, rng, B):
    fams = ["F1", "F2"] if mix == "hom" else ["F1", "F2", "F3"]
    parts = np.array_split(np.arange(B), len(fams))
    toks = []
    for f, idx in zip(fams, parts):
        X, labs, pairs = sample_family(f, rng, len(idx))
        toks.append(to_tokens(X, labs, pairs))
    return np.concatenate(toks)


def label_positions():
    return np.array([t * (NA + 1) + NA - 1 for t in range(T)])   # predict label at last attribute


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mix", default="hom"); ap.add_argument("--steps", type=int, default=30000)
    ap.add_argument("--bs", type=int, default=256); ap.add_argument("--layers", type=int, default=6)
    ap.add_argument("--d", type=int, default=256); ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    torch.manual_seed(a.seed); rng = np.random.default_rng(a.seed)
    cfg = GPT2Config(vocab_size=VOCAB, n_positions=SEQ + 8, n_embd=a.d, n_layer=a.layers, n_head=8,
                     resid_pdrop=0.0, embd_pdrop=0.0, attn_pdrop=0.0)
    model = GPT2LMHeadModel(cfg).cuda()
    opt = torch.optim.AdamW(model.parameters(), lr=3e-4, weight_decay=0.01, betas=(0.9, 0.98))
    sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda s: min(1, s / 1000) * 0.5 * (1 + math.cos(math.pi * min(s, a.steps) / a.steps)))
    pos = torch.tensor(label_positions()).cuda()
    t0 = time.time()
    for step in range(a.steps + 1):
        toks = torch.tensor(make_batch(a.mix, rng, a.bs)).cuda()
        logits = model(toks).logits                               # B x S x V
        lg = logits[:, pos, :]                                    # predictions at last attr of each demo
        tgt = toks[:, pos + 1]
        loss = nn.functional.cross_entropy(lg.reshape(-1, VOCAB), tgt.reshape(-1))
        opt.zero_grad(); loss.backward(); torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step(); sched.step()
        if step % 1000 == 0:
            print(f"step {step} loss {loss.item():.4f} {time.time()-t0:.0f}s", flush=True)
    os.makedirs(a.out, exist_ok=True)
    model.save_pretrained(a.out)
    json.dump(vars(a), open(os.path.join(a.out, "train_args.json"), "w"))


if __name__ == "__main__":
    main()
