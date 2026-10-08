"""Score single-token two-candidate rows: ld = logit(cands[1]) - logit(cands[0]) at the last prompt position.
usage: score_ld.py --model M --data kernel --out results/kernel/<tag>.npz [--bs 32]
Left padding with explicit position_ids (as run_lm.py)."""
import argparse, json
from pathlib import Path
import numpy as np, torch
from transformers import AutoModelForCausalLM, AutoTokenizer

ROOT = Path(__file__).resolve().parents[1]


@torch.no_grad()
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model"); ap.add_argument("--data"); ap.add_argument("--out"); ap.add_argument("--bs", type=int, default=32)
    a = ap.parse_args()
    rows = [json.loads(l) for l in open(ROOT / f"data/{a.data}/rows.jsonl")]
    tok = AutoTokenizer.from_pretrained(a.model)
    model = AutoModelForCausalLM.from_pretrained(a.model, dtype=torch.bfloat16, device_map="cuda", attn_implementation="sdpa").eval()
    pad = tok.pad_token_id if tok.pad_token_id is not None else 0
    enc = [tok(r["prompt"], add_special_tokens=False)["input_ids"] for r in rows]
    cid = []
    for r in rows:
        c0 = tok(r["cands"][0], add_special_tokens=False)["input_ids"]; c1 = tok(r["cands"][1], add_special_tokens=False)["input_ids"]
        assert len(c0) == 1 and len(c1) == 1, r["cands"]
        cid.append((c0[0], c1[0]))
    ld = np.zeros(len(rows), np.float32)
    order = sorted(range(len(rows)), key=lambda i: -len(enc[i]))
    for b in range(0, len(order), a.bs):
        ix = order[b:b + a.bs]
        Lm = max(len(enc[i]) for i in ix)
        ids = torch.full((len(ix), Lm), pad, dtype=torch.long); att = torch.zeros((len(ix), Lm), dtype=torch.long)
        for j, i in enumerate(ix):
            ids[j, Lm - len(enc[i]):] = torch.tensor(enc[i]); att[j, Lm - len(enc[i]):] = 1
        pos = (att.cumsum(1) - 1).clamp(min=0)
        lo = model(input_ids=ids.cuda(), attention_mask=att.cuda(), position_ids=pos.cuda(), logits_to_keep=1, use_cache=False).logits[:, -1].float()
        for j, i in enumerate(ix):
            ld[i] = float(lo[j, cid[i][1]] - lo[j, cid[i][0]])
        if (b // a.bs) % 100 == 0:
            print(b, len(rows), flush=True)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(a.out, uid=np.array([r["uid"] for r in rows]), ld=ld)
    print("done", a.out)


if __name__ == "__main__":
    main()
