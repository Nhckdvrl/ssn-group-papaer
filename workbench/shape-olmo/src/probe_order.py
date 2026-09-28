"""Controlled probe v2: does the model know WHICH earlier occurrence to copy from?

v1 (random-token 'K V_i ... K' with most-recent as correct) was uninformative: even the RoPE
transformer hedged uniformly over the n earlier values (chance-level), because nothing in random
tokens demands recency. v2 makes order semantically required, in code:

  reassign : Python lines. The target variable is assigned n times (`x = 'V_i'`, distinct V_i), with
             `gap` filler assignments to other variables between assignments; query `assert x == '`.
             Correct = the LAST assigned value (Python semantics). Content-only matching sees n equally
             good `x = '` matches, so picking the last needs order / recency information.
  keyed    : control, same surface form, but each value is bound to a distinct variable
             (`x3 = 'V_i'`), query `assert x<j> == '` for a random j. Correct = V_j, identifiable by
             content; no order needed.
Readout: log-probs of the n candidate value first-tokens at the query position (all candidates are
single-token words with a leading-quote-free spelling).

usage: probe_order.py MODEL_PATH TAG   -> results/probe_order/<TAG>.jsonl
"""
import json, os, random, sys
import numpy as np
import torch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NS = [1, 2, 4, 8]
GAPS = [int(g) for g in os.environ.get("PROBE_GAPS", "4,32,128").split(",")]   # filler assignment LINES (~8 tokens each)
N_ITEMS = int(os.environ.get("PROBE_N", 120))
WORDS = ("apple river stone window garden doctor teacher music silver forest island mountain village engine "
         "letter market paper table glass winter summer morning camera ticket bottle castle bridge rocket planet "
         "coffee jacket pencil mirror candle wallet hammer ladder basket carpet helmet anchor violin tunnel desert "
         "harbor meadow valley lantern compass").split()


def value_pool(tok):
    """words whose continuation after an opening quote is a single token."""
    out = []
    for w in WORDS:
        a = tok("x = '", add_special_tokens=False).input_ids
        b = tok("x = '" + w, add_special_tokens=False).input_ids
        if b[:len(a)] == a and len(b) == len(a) + 1:
            out.append((w, b[-1]))
    return out


def items(tok):
    V = value_pool(tok)
    rng = random.Random(20260928)
    out = []
    for task in ("reassign", "keyed"):
        for n in NS:
            for gap in GAPS:
                for k in range(N_ITEMS):
                    vals = rng.sample(V, n)
                    others = [w for w, _ in V if w not in {v for v, _ in vals}]
                    lines = []
                    def filler(m):
                        for _ in range(m):
                            lines.append(f"v{rng.randrange(100, 999)} = '{rng.choice(others)}'")
                    filler(gap)
                    for i, (w, _) in enumerate(vals):
                        name = "x" if task == "reassign" else f"x{i + 1}"
                        lines.append(f"{name} = '{w}'")
                        filler(gap)
                    j = n - 1 if task == "reassign" else rng.randrange(n)
                    qname = "x" if task == "reassign" else f"x{j + 1}"
                    text = "\n".join(lines) + f"\nassert {qname} == '"
                    out.append(dict(task=task, n=n, gap=gap, k=k, text=text,
                                    cands=[t for _, t in vals], correct=j))
    return out


@torch.no_grad()
def main(path, tag):
    from transformers import AutoModelForCausalLM, AutoTokenizer
    trc = os.environ.get("PROBE_TRC", "1") == "1"
    tok = AutoTokenizer.from_pretrained(path, trust_remote_code=trc)
    model = AutoModelForCausalLM.from_pretrained(path, dtype=torch.bfloat16, device_map="cuda",
                                                 trust_remote_code=trc).eval()
    os.makedirs(f"{ROOT}/results/probe_order", exist_ok=True)
    with open(f"{ROOT}/results/probe_order/{tag}.jsonl", "w") as f:
        for it in items(tok):
            ids = tok(it["text"], add_special_tokens=False).input_ids
            x = torch.tensor(ids, device="cuda")[None]
            lp = torch.log_softmax(model(input_ids=x, attention_mask=torch.ones_like(x), use_cache=False).logits[0, -1].float(), -1)
            c = lp[it["cands"]].cpu().numpy()
            f.write(json.dumps(dict(task=it["task"], n=it["n"], gap=it["gap"], k=it["k"], correct=it["correct"],
                                    lp_cands=c.tolist(), mass=float(np.exp(c).sum()), len=len(ids))) + "\n")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
