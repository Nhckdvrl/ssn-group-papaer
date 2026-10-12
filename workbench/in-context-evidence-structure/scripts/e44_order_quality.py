"""E44: does order quality transfer across queries, and does it survive a position-only perturbation?
usage: e44_order_quality.py --model M --task num|sst --out NPZ [--sets 60 --orders 16 --queries 40]
Per demo set (16 balanced demos), 40 queries (first 20 dev, last 20 test), 16 random orders, two position modes:
  orig: positions 0..n-1;  gap: a random gap of 1-8 position ids inserted before every block and before the query
  (fixed per set x order; tokens and causal order unchanged).
Score = margin toward the correct label: logit(correct) - logit(other)."""
import argparse, sys
from pathlib import Path
import numpy as np, torch
from transformers import AutoModelForCausalLM, AutoTokenizer

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def make_sets(task, n_sets, n_q, seed=990000):
    rng = np.random.default_rng(seed + (task == "sst"))
    if task == "num":
        pool = {0: list(range(10, 50)), 1: list(range(50, 90))}
        head, key, words = "Below are examples of numbers and their labels.\n\n", "Number", ["small", "large"]
    else:
        from build_marked import sst_pool
        pool = sst_pool()
        head, key, words = "Below are examples of reviews and their labels.\n\n", "Review", ["negative", "positive"]
    sets = []
    for s in range(n_sets):
        demo, qs = [], []
        for c in (0, 1):
            idx = rng.permutation(len(pool[c]))
            demo += [(pool[c][i], c) for i in idx[:8]]
            qs += [(pool[c][i], c) for i in idx[8:8 + n_q // 2]]
        qs = [qs[i] for i in rng.permutation(len(qs))]
        sets.append((demo, qs))
    return sets, head, key, words


@torch.no_grad()
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model"); ap.add_argument("--task"); ap.add_argument("--out")
    ap.add_argument("--sets", type=int, default=60); ap.add_argument("--orders", type=int, default=16)
    ap.add_argument("--queries", type=int, default=40); ap.add_argument("--bs", type=int, default=32)
    a = ap.parse_args()
    tok = AutoTokenizer.from_pretrained(a.model)
    model = AutoModelForCausalLM.from_pretrained(a.model, dtype=torch.bfloat16, device_map="cuda", attn_implementation="sdpa").eval()
    enc = lambda s: tok(s, add_special_tokens=False)["input_ids"]
    sets, head, key, words = make_sets(a.task, a.sets, a.queries)
    cid = [enc(" " + w)[0] for w in words]
    assert all(len(enc(" " + w)) == 1 for w in words)
    hid = enc(head)
    margins = np.zeros((a.sets, a.orders, 2, a.queries), np.float32)
    rng = np.random.default_rng(5)
    for s, (demo, qs) in enumerate(sets):
        blocks = [enc(f"{key}: {x}\nLabel: {words[c]}\n\n") for x, c in demo]
        qids = [enc(f"{key}: {x}\nLabel:") for x, _ in qs]
        qlen = [len(q) for q in qids]; QL = max(qlen)
        for o in range(a.orders):
            perm = list(range(16)) if o == 0 else list(rng.permutation(16))
            gaps = rng.integers(1, 9, 17)
            for m in range(2):
                ids, pos, p = list(hid), list(range(len(hid))), len(hid)
                for k, j in enumerate(perm):
                    p += int(gaps[k]) if m == 1 else 0
                    ids += blocks[j]; pos += list(range(p, p + len(blocks[j]))); p += len(blocks[j])
                p += int(gaps[16]) if m == 1 else 0
                # prefix once, then all queries in one batch over the repeated cache (right padding inside queries)
                out = model(input_ids=torch.tensor([ids]).cuda(), position_ids=torch.tensor([pos]).cuda(), use_cache=True)
                cache = out.past_key_values
                cache.batch_repeat_interleave(len(qids))
                I = torch.zeros((len(qids), QL), dtype=torch.long); M = torch.zeros((len(qids), len(ids) + QL), dtype=torch.long)
                M[:, :len(ids)] = 1
                for qi, q in enumerate(qids):
                    I[qi, :len(q)] = torch.tensor(q); M[qi, len(ids):len(ids) + len(q)] = 1
                P = torch.arange(p, p + QL)[None].repeat(len(qids), 1)
                lo = model(input_ids=I.cuda(), attention_mask=M.cuda(), position_ids=P.cuda(), past_key_values=cache, use_cache=True).logits.float()
                for qi in range(len(qids)):
                    c = qs[qi][1]; l = lo[qi, qlen[qi] - 1]
                    margins[s, o, m, qi] = float(l[cid[c]] - l[cid[1 - c]])
                del cache, out
        print(s, "mean margin", float(margins[s, :, 0].mean()), flush=True)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(a.out, margins=margins)
    print("done")


if __name__ == "__main__":
    main()
