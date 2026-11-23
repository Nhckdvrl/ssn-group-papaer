#!/usr/bin/env python3
"""E211 LL readout (Kaplan et al. 2025, sec. 4.1): for the source vectors in S.pt (intact word and splits m = 2..6,
every layer), top-1 over the full vocabulary by (a) cosine with the input-embedding rows, (b) the output logit lens
(final norm + lm_head). Success = top-1 is the intact word's token.
Usage: e211_lens.py MODEL_DIR ITEMS OUT_JSON NAME=CAPTURE_DIR [NAME=CAPTURE_DIR ...]"""
import json
import sys
from pathlib import Path

import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM


@torch.no_grad()
def main():
    mdir, items, out = sys.argv[1:4]
    model = AutoModelForCausalLM.from_pretrained(mdir, dtype=torch.bfloat16, device_map="cuda").eval()
    E = F.normalize(model.model.embed_tokens.weight.float(), dim=-1)  # [V, d]
    norm, head = model.model.norm, model.lm_head
    S = json.loads(Path(items).read_text())["S"]
    res = {}
    for arg in sys.argv[4:]:
        name, d = arg.split("=", 1)
        C = torch.load(Path(d) / "S.pt")
        src, names = C["src"], C["src_names"]  # [n, L+1, 6, d]
        n = src.shape[0]
        wid = torch.tensor([S[i]["wid"] for i in range(n)], device="cuda")
        r = {"layers": list(range(-1, src.shape[1] - 1)), "n": n}
        for k, sn in enumerate(names):
            emb, out_ = [], []
            for l in range(src.shape[1]):
                h = src[:, l, k].cuda().float()
                emb.append((F.normalize(h, dim=-1) @ E.T).argmax(-1).eq(wid).float().mean().item())
                logits = head(norm(h.to(torch.bfloat16))).float()
                out_.append(logits.argmax(-1).eq(wid).float().mean().item())
            r[f"emb_{sn}"], r[f"out_{sn}"] = emb, out_
        res[name] = r
        m24 = [sum(r[f"emb_m{m}"][l] for m in (2, 3, 4)) / 3 for l in range(len(r["layers"]))]
        print(name, "LL-emb m2-4 max %.2f at layer %d" % (max(m24), m24.index(max(m24)) - 1),
              "| m1 L2 %.2f" % r["emb_m1"][3], flush=True)
    Path(out).write_text(json.dumps(res))


if __name__ == "__main__":
    main()
