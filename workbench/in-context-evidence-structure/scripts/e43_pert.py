"""E43 b + c: perturbation spectrum on the original-order prompt, and leave-one-out under a second order.
usage: e43_pert.py --model M --out NPZ
Items (per kernel_perm base, original order = perm0):
  orig                      original prompt
  offset                    same tokens, all positions + 37   (RoPE-relative invariant; negative control)
  header                    paraphrased instruction line
  names                     Alex -> Jordan, Sam -> Taylor
  num                       one random demo value +/-1 inside its class, not colliding
  swapadj                   two random adjacent demos swapped
  perm1                     the E40 perm1 order (full reorder)
  perm1_del{t}              perm1 order with demo t (by original index) deleted   [bridge test]
"""
import argparse, json, re
from pathlib import Path
import numpy as np, torch
from transformers import AutoModelForCausalLM, AutoTokenizer

ROOT = Path(__file__).resolve().parents[1]
HEAD = "Below are examples of numbers and their labels.\n\n"
HEAD2 = "Here are some numbers, each with the label an annotator gave it.\n\n"
BLK = r"Number: \d+\nAnnotator: \w+\nLabel: \S+\n\n"


@torch.no_grad()
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model"); ap.add_argument("--out"); ap.add_argument("--bs", type=int, default=16)
    a = ap.parse_args()
    tok = AutoTokenizer.from_pretrained(a.model)
    model = AutoModelForCausalLM.from_pretrained(a.model, dtype=torch.bfloat16, device_map="cuda", attn_implementation="sdpa").eval()
    rows = [json.loads(l) for l in open(ROOT / "data/kernel_perm/rows.jsonl")]
    by = {}
    for r in rows:
        by.setdefault(r["base_id"], {})[r["uid"].split("|")[1]] = r
    enc = lambda s: tok(s, add_special_tokens=False)["input_ids"]
    items = []
    for b, rs in by.items():
        r0 = rs["perm0"]; p = r0["prompt"]
        blocks = re.findall(BLK, p)
        query = p[len(HEAD) + sum(map(len, blocks)):]
        c = [enc(x)[0] for x in r0["cands"]]
        rng = np.random.default_rng(int(b.split("_")[1]) + 7)
        add = lambda name, text, off=0: items.append((f"{b}|{name}", enc(text), off, c))
        add("orig", p)
        add("offset", p, 37)
        add("header", HEAD2 + "".join(blocks) + query)
        add("names", p.replace("Alex", "Jordan").replace("Sam", "Taylor"))
        vals = [int(re.search(r"Number: (\d+)", x).group(1)) for x in blocks]
        qv = int(re.search(r"Number: (\d+)", query).group(1))
        for _ in range(100):
            t = int(rng.integers(16)); d = int(rng.choice([-1, 1])); nv = vals[t] + d
            if (nv >= 50) == (vals[t] >= 50) and 10 <= nv <= 89 and nv not in vals and nv != qv:
                break
        nb = list(blocks); nb[t] = nb[t].replace(f"Number: {vals[t]}\n", f"Number: {nv}\n")
        add("num", HEAD + "".join(nb) + query)
        s = int(rng.integers(15)); sb = list(blocks); sb[s], sb[s + 1] = sb[s + 1], sb[s]
        add("swapadj", HEAD + "".join(sb) + query)
        p1 = rs["perm1"]["prompt"]; b1 = re.findall(BLK, p1)
        add("perm1", p1)
        for t, blk in enumerate(blocks):        # delete demo t (original index) from the perm1 order
            add(f"perm1_del{t}", HEAD + "".join(x for x in b1 if x != blk) + query)
    pad = tok.pad_token_id if tok.pad_token_id is not None else 0
    out = {}
    order = sorted(range(len(items)), key=lambda i: -len(items[i][1]))
    for s in range(0, len(order), a.bs):
        ix = order[s:s + a.bs]
        Lm = max(len(items[i][1]) for i in ix)
        ids = torch.full((len(ix), Lm), pad, dtype=torch.long); att = torch.zeros((len(ix), Lm), dtype=torch.long)
        P = torch.zeros((len(ix), Lm), dtype=torch.long)
        for j, i in enumerate(ix):
            n = len(items[i][1])
            ids[j, Lm - n:] = torch.tensor(items[i][1]); att[j, Lm - n:] = 1
            P[j, Lm - n:] = torch.arange(n) + items[i][2]
        lo = model(input_ids=ids.cuda(), attention_mask=att.cuda(), position_ids=P.cuda(), logits_to_keep=1, use_cache=False).logits[:, -1].float()
        for j, i in enumerate(ix):
            c = items[i][3]; out[items[i][0]] = float(lo[j, c[1]] - lo[j, c[0]])
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(a.out, uid=np.array(list(out)), ld=np.array(list(out.values()), np.float32))
    print("done", len(out))


if __name__ == "__main__":
    main()
