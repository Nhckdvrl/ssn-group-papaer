"""How much of the initial weights survives training? corr(W_step, W_step0) per matrix type (DataDecide 1B, c4, 3 seeds)."""
import torch
from safetensors import safe_open

import dd_common as dd


def tensors(rec, step, seed, keys):
    p = dd.fetch(f"allenai/DataDecide-{rec}-1B", dd.rev(step, seed))
    out = {}
    for f in sorted(p.glob("*.safetensors")):
        with safe_open(str(f), "pt") as h:
            for k in keys:
                if k in h.keys():
                    out[k] = h.get_tensor(k).float().flatten()
    return out


c = lambda a, b: round(float(torch.corrcoef(torch.stack([a, b]))[0, 1]), 3)
keys = [f"model.transformer.blocks.{l}.{m}.weight" for l in (2, 8, 14) for m in ("att_proj", "attn_out", "ff_proj", "ff_out")]
for s in dd.SEEDS:
    W0 = tensors("c4", 0, s, keys)
    for step in (2500, 10000, dd.FINAL_1B):
        W = tensors("c4", step, s, keys)
        print(s, step, {k.split("blocks.")[1].replace(".weight", ""): c(W[k], W0[k]) for k in keys}, flush=True)
