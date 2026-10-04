"""Audit: did each DataDecide run actually start from its published step0? Compare step-2500 weights with every seed's step0."""
import torch

import dd_common as dd
from safetensors import safe_open
K = "model.transformer.blocks.5.att_proj.weight"
def W(rec, step, seed):
    p = dd.fetch(f"allenai/DataDecide-{rec}-1B", dd.rev(step, seed))
    for f in sorted(p.glob("*.safetensors")):
        with safe_open(str(f), "pt") as h:
            if K in h.keys():
                return h.get_tensor(K).float().flatten()
c = lambda a, b: round(float(torch.corrcoef(torch.stack([a, b]))[0, 1]), 3)
S0 = {s: W("c4", 0, s) for s in dd.SEEDS}
for rec in ("c4", "dolma1_7", "dclm-baseline"):
    for s in dd.SEEDS:
        w = W(rec, 2500, s)
        print(rec, s, "step2500 vs step0 of", {s0: c(w, S0[s0]) for s0 in dd.SEEDS}, flush=True)
