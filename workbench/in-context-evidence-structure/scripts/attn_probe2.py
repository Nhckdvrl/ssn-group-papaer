"""Attention organisation across night_core formats: does the query retrieve demos by input similarity?

For each format with scalar-ish inputs (numbers / letters / parity / magnitude), allA contexts:
  share[l,h,t] = attention from the last prompt token to demo t's answer tokens (normalised over demos)
  regress share on position (t/(T-1)) and on input similarity  s_t = -|x_t - q| (numbers: /10, letters: alphabet distance)
Outputs per format: weighted (by label-attention) mean slopes over the top-k answer-attending heads.
usage: attn_probe2.py --model M --fmts arith,plus10,... --n 60 --out OUT.json
"""
import argparse, json, re
from pathlib import Path
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

ROOT = Path(__file__).resolve().parents[1]


def spans(prompt, tok, T):
    enc = tok(prompt, return_offsets_mapping=True, add_special_tokens=False)
    offs = enc["offset_mapping"]; out = []
    for m in re.finditer(r"(?:Label|Output): (\S+)\n", prompt):
        a, b = m.start(1), m.end(1)
        out.append([i for i, (s, e) in enumerate(offs) if e > a and s < b])
    assert len(out) == T, (len(out), T)
    return enc["input_ids"], out


def sim_of(fmt, xs, q):
    if fmt == "letter":
        return np.array([-abs(ord(x) - ord(q)) for x in xs], float)
    return np.array([-abs(x - q) / 10 for x in xs], float)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--model"); ap.add_argument("--fmts"); ap.add_argument("--out")
    ap.add_argument("--n", type=int, default=60); ap.add_argument("--data", default="night_core")
    a = ap.parse_args()
    tok = AutoTokenizer.from_pretrained(a.model)
    model = AutoModelForCausalLM.from_pretrained(a.model, dtype=torch.bfloat16, device_map="cuda",
                                                 attn_implementation="eager").eval()
    rows = {}
    for l in open(ROOT / "data" / a.data / "rows.jsonl"):
        r = json.loads(l); g, p = r["cond"].split(":", 1)
        if p == "allA" and g in a.fmts.split(","):
            rows.setdefault(g, []).append(r)
    res = {}
    for fmt, R in rows.items():
        A, S = [], []
        for r in R[:a.n]:
            T = len(r["labels"]); ids, sp = spans(r["prompt"], tok, T)
            with torch.no_grad():
                o = model(torch.tensor([ids]).cuda(), output_attentions=True, use_cache=False)
            att = np.stack([x[0, :, -1, :].float().cpu().numpy() for x in o.attentions])   # L x H x S
            a_t = np.stack([att[:, :, s].sum(-1) for s in sp], -1)                      # L x H x T
            A.append(a_t); S.append(sim_of(fmt, r["base"]["xs"], r["base"]["q"]))
        A = np.stack(A); S = np.stack(S)                       # N x L x H x T ; N x T
        N, L, H, T = A.shape
        tot = A.sum(-1).mean(0)                                 # L x H
        share = A / (A.sum(-1, keepdims=True) + 1e-9)
        P = np.tile(np.arange(T) / (T - 1), (N, 1)); Pc = P - P.mean(1, keepdims=True); Sc = S - S.mean(1, keepdims=True)
        Xd = np.c_[Pc.ravel(), Sc.ravel()]
        top = np.argsort(tot.ravel())[-30:]
        bp, bs = [], []
        for j in top:
            l, h = divmod(j, H)
            y = share[:, l, h, :]; y = (y - y.mean(1, keepdims=True)).ravel()
            b, *_ = np.linalg.lstsq(Xd, y, rcond=None); bp.append(b[0]); bs.append(b[1])
        w = tot.ravel()[top]
        res[fmt] = {"pos_slope": float(np.average(bp, weights=w)), "sim_slope": float(np.average(bs, weights=w)),
                    "label_attn_top30": float(w.mean())}
        print(fmt, {k: round(v, 4) for k, v in res[fmt].items()}, flush=True)
        json.dump(res, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
