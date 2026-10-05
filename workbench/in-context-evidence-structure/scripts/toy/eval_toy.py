"""Evaluate a toy model on the same A/B patterns as the LLM experiments.
usage: eval_toy.py MODEL_DIR [--n 2000]
Formats: rule (latent; B = reversed rule) and surface (labels independent of inputs; B = other label).
"""
import argparse, json, sys
import numpy as np
import torch
from transformers import GPT2LMHeadModel
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from train_toy import NA, T, L0, NL, to_tokens  # noqa

PATS = {}
def pat(b):
    p = ["A"] * T
    for i in b: p[i] = "B"
    return "".join(p)
PATS["allA"] = pat([]); PATS["single_1"] = pat([0]); PATS["single_16"] = pat([15])
for k in (2, 3, 4, 5, 8): PATS[f"suffix_{k}"] = pat(range(T - k, T))
for k in (2, 3, 4, 6): PATS[f"disp_{k}"] = pat(np.round(np.linspace(T / k - 1, T - 1, k)).astype(int))
for m in (2, 4):
    for k in (3, 5): PATS[f"noise_{m}__suffix_{k}"] = pat([1, 5, 8, 3][:m] + list(range(T - k, T)))
PATS["block_start4"] = pat(range(4)); PATS["prefix_8"] = pat(range(8)); PATS["suffix_8b"] = pat(range(8, 16))


def build(fmt, n, rng):
    X = rng.integers(0, 2, size=(n, T + 1, NA))
    a = rng.integers(NA, size=n); s = rng.integers(2, size=n)
    if fmt == "rule":   # balance the rule attribute among demos
        for b in range(n):
            X[b, :T, a[b]] = np.array([1] * 8 + [0] * 8)[rng.permutation(T)]
    pairs = np.array([rng.choice(NL, 2, replace=False) for _ in range(n)])
    out = {}
    for name, p in PATS.items():
        isB = np.array([c == "B" for c in p])
        if fmt == "rule":
            yA = X[np.arange(n)[:, None], np.arange(T)[None, :], a[:, None]] ^ s[:, None]
            labs = np.where(isB[None, :], 1 - yA, yA)
            qA = X[np.arange(n), T, a] ^ s
        else:
            labs = np.where(isB[None, :], 1 - s[:, None], s[:, None]).repeat(1, 0)
            qA = s.copy()
        out[name] = (to_tokens(X, labs, pairs), pairs, qA)
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("model"); ap.add_argument("--n", type=int, default=2000)
    a = ap.parse_args()
    model = GPT2LMHeadModel.from_pretrained(a.model).cuda().eval()
    rng = np.random.default_rng(123)
    res = {}
    for fmt in ("rule", "surface"):
        data = build(fmt, a.n, rng)
        lo = {}
        for name, (toks, pairs, qA) in data.items():
            with torch.no_grad():
                lg = model(torch.tensor(toks).cuda()).logits[:, -1, :].float().cpu().numpy()
            idxA = L0 + pairs[np.arange(len(qA)), qA]; idxB = L0 + pairs[np.arange(len(qA)), 1 - qA]
            lo[name] = lg[np.arange(len(qA)), idxB] - lg[np.arange(len(qA)), idxA]
        d = lambda x, y: float(np.mean(lo[x] - lo[y]))
        r = {"allA": float(lo["allA"].mean()), "acc": float((lo["allA"] < 0).mean()),
             "cluster": d("suffix_4", "disp_4"), "noise2_s3": d("noise_2__suffix_3", "suffix_3"),
             "noise4_s5": d("noise_4__suffix_5", "suffix_5"), "last_first": d("single_16", "single_1"),
             "suffix8_minus_prefix8": d("suffix_8b", "prefix_8")}
        res[fmt] = r
        print(fmt, {k: round(v, 3) for k, v in r.items()})
    json.dump(res, open(a.model.rstrip("/") + "/eval.json", "w"), indent=1)


if __name__ == "__main__":
    main()
