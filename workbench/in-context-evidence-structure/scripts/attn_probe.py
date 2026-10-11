"""Per-head attention from the query's final token to each demo's label-word tokens.

usage: attn_probe.py --model M --inp rows.jsonl --conds c1,c2 --max_bases N --out out.npz
For every selected row: A[layer, head, t] = sum of attention from the last prompt token
to the label-word tokens of demo t (t = 0..T-1).  Also stores per-demo features:
position, Hamming similarity to the query (if inputs exist), and whether the demo is B.
"""
import argparse, json, re
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


def label_spans(prompt, tok, T):
    enc = tok(prompt, return_offsets_mapping=True, add_special_tokens=False)
    offs = enc["offset_mapping"]
    spans = []
    for m in re.finditer(r"Label: (\S+)\n", prompt):
        a, b = m.start(1), m.end(1)
        idx = [i for i, (s, e) in enumerate(offs) if e > a and s < b]
        spans.append(idx)
    assert len(spans) == T, (len(spans), T)
    return enc["input_ids"], spans


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model"); ap.add_argument("--inp"); ap.add_argument("--conds"); ap.add_argument("--out")
    ap.add_argument("--max_bases", type=int, default=100)
    a = ap.parse_args()
    conds = set(a.conds.split(","))
    tok = AutoTokenizer.from_pretrained(a.model)
    model = AutoModelForCausalLM.from_pretrained(a.model, dtype=torch.bfloat16, device_map="cuda",
                                                 attn_implementation="eager").eval()
    rows, bases = [], []
    for l in open(a.inp):
        r = json.loads(l)
        if r["cond"] in conds:
            if r["base_id"] not in bases:
                if len(bases) >= a.max_bases:
                    continue
                bases.append(r["base_id"])
            rows.append(r)
    out = {"A": [], "cond": [], "base": [], "isB": [], "sim": [], "lo_B": []}
    for k, r in enumerate(rows):
        T = len(r["labels"])
        ids, spans = label_spans(r["prompt"], tok, T)
        bos = [tok.bos_token_id] if (tok.bos_token_id is not None and tok("a")["input_ids"][:1] == [tok.bos_token_id]) else []
        shift = len(bos)
        x = torch.tensor([bos + ids]).cuda()
        with torch.no_grad():
            o = model(input_ids=x, output_attentions=True, use_cache=False)
        last = x.shape[1] - 1
        A = np.zeros((len(o.attentions), o.attentions[0].shape[1], T), np.float32)
        for li, att in enumerate(o.attentions):
            row = att[0, :, last, :].float().cpu().numpy()          # heads x seq
            for t, sp in enumerate(spans):
                A[li, :, t] = row[:, [s + shift for s in sp]].sum(1)
        logits = o.logits[0, last].float()
        # log-odds of first tokens of the two candidates (cheap readout; full readout lives in run_lm)
        c0 = tok(r["cands"][0], add_special_tokens=False)["input_ids"][0]
        c1 = tok(r["cands"][1], add_special_tokens=False)["input_ids"][0]
        lo1 = float(logits[c1] - logits[c0]); loB = lo1 if r["query_label_B"] == 1 else -lo1
        b = r.get("base", {})
        if "X" in b and len(b.get("xq", [])) > 0:
            X = np.array(b["X"]); q = np.array(b["xq"]); sim = (X == q).sum(1).astype(float)
        else:
            sim = np.full(T, np.nan)
        out["A"].append(A); out["cond"].append(r["cond"]); out["base"].append(r["base_id"])
        out["isB"].append([ch == "B" for ch in r["pattern"]]); out["sim"].append(sim); out["lo_B"].append(loB)
        if k % 50 == 0:
            print(k, len(rows), flush=True)
    np.savez_compressed(a.out, A=np.stack(out["A"]), cond=np.array(out["cond"]), base=np.array(out["base"]),
                        isB=np.array(out["isB"]), sim=np.stack(out["sim"]), lo_B=np.array(out["lo_B"]))
    print("saved", a.out)


if __name__ == "__main__":
    main()
