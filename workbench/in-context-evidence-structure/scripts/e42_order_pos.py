"""E42: order effects split into causal order vs RoPE position (2x2).  usage: e42_order_pos.py --model M --out NPZ
For each kernel_perm base: blocks tokenized separately and concatenated (head + blocks + query).
  O: original block order, positions 0..n-1
  A: permuted block order, positions 0..n-1
  B: permuted block order, each block keeps its positions from the original layout
  C: original block order, each block takes the positions it has in the permuted layout
Scores ld = logit(c1) - logit(c0) at the last token (query end).  Batch size 1-per-sequence padding-free groups."""
import argparse, json, re
from pathlib import Path
import numpy as np, torch
from transformers import AutoModelForCausalLM, AutoTokenizer

ROOT = Path(__file__).resolve().parents[1]
HEAD = "Below are examples of numbers and their labels.\n\n"


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
        by.setdefault(r["base_id"], []).append(r)
    enc = lambda s: tok(s, add_special_tokens=False)["input_ids"]
    items = []   # (uid, ids, pos, cands)
    check = []
    for b, rs in by.items():
        r0 = [r for r in rs if r["uid"].endswith("|perm0")][0]
        p = r0["prompt"]
        blocks0 = re.findall(r"Number: \d+\nAnnotator: \w+\nLabel: \S+\n\n", p)
        query = p[len(HEAD) + sum(map(len, blocks0)):]
        hid, qid = enc(HEAD), enc(query)
        bid = {blk: enc(blk) for blk in blocks0}
        def layout(order):
            starts, s = {}, len(hid)
            for blk in order:
                starts[blk] = s; s += len(bid[blk])
            return starts, s
        st0, end0 = layout(blocks0)
        c = [enc(x)[0] for x in r0["cands"]]
        def seq(order, starts, qstart):
            ids = list(hid); pos = list(range(len(hid)))
            for blk in order:
                ids += bid[blk]; pos += list(range(starts[blk], starts[blk] + len(bid[blk])))
            ids += qid; pos += list(range(qstart, qstart + len(qid)))
            return ids, pos
        ids, pos = seq(blocks0, st0, end0)
        items.append((f"{b}|O", ids, pos, c))
        check.append((f"{b}|O", enc(p)))
        for r in rs:
            if r["uid"].endswith("|perm0"):
                continue
            k = r["uid"].split("|")[1]
            order = re.findall(r"Number: \d+\nAnnotator: \w+\nLabel: \S+\n\n", r["prompt"])
            stp, endp = layout(order)
            items.append((f"{b}|A|{k}", *seq(order, stp, endp), c))
            items.append((f"{b}|B|{k}", *seq(order, st0, end0), c))
            items.append((f"{b}|C|{k}", *seq(blocks0, stp, endp), c))
    same = sum(1 for (u, ids, _, _), (_, ref) in zip([it for it in items if it[0].endswith("|O")], check) if ids == ref)
    print(f"concatenated tokenization identical to full-prompt tokenization: {same}/{len(check)}", flush=True)
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
            ids[j, Lm - n:] = torch.tensor(items[i][1]); att[j, Lm - n:] = 1; P[j, Lm - n:] = torch.tensor(items[i][2])
        lo = model(input_ids=ids.cuda(), attention_mask=att.cuda(), position_ids=P.cuda(), logits_to_keep=1, use_cache=False).logits[:, -1].float()
        for j, i in enumerate(ix):
            c = items[i][3]
            out[items[i][0]] = float(lo[j, c[1]] - lo[j, c[0]])
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(a.out, uid=np.array(list(out)), ld=np.array(list(out.values()), np.float32))
    print("done", len(out))


if __name__ == "__main__":
    main()
