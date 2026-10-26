"""E105e: which part of a mixed unlearning edit survives benign relearning?
Per parameter group g: survival s_g = <(R - C)_g, (U - 0)_g> / ||(U - 0)_g||^2, where U = unlearned, 0 = original,
R = U after 1000 benign steps, C = original after the same 1000 benign steps (same data order).
Also a functional check: replace R's group g by C's group g and measure the IOI change.

Usage: e105_survival.py OUT.json BASE_DIR U_DIR R_DIR C_DIR
"""
import json
import sys

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

import mp_common as mc
from e89_labor import Builder
from e105_revert import ioi_metric


def groups_of(model):
    c = model.config
    H, d = c.num_attention_heads, c.hidden_size
    return H, d, d // H


def split(name, t, H, d, dh):
    """return dict group -> tensor view for this parameter"""
    if "query_key_value.weight" in name:
        w = t.view(H, 3, dh, d)
        return {"qk": w[:, :2], "v": w[:, 2]}
    if "query_key_value.bias" in name:
        b = t.view(H, 3, dh)
        return {"qk": b[:, :2], "v": b[:, 2]}
    if "attention.dense" in name:
        return {"o": t}
    if "mlp" in name:
        return {"mlp": t}
    return {"other": t}


def main():
    out, b0, bu, br, bc = sys.argv[1:6]
    load = lambda p: AutoModelForCausalLM.from_pretrained(p, dtype=torch.float32).eval()
    M0, MU, MR, MC = load(b0), load(bu), load(br), load(bc)
    H, d, dh = groups_of(M0)
    P = [dict(m.named_parameters()) for m in (M0, MU, MR, MC)]
    num, den = {}, {}
    for n in P[0]:
        du = (P[1][n] - P[0][n]).detach()
        drc = (P[2][n] - P[3][n]).detach()
        su, sr = split(n, du, H, d, dh), split(n, drc, H, d, dh)
        for g in su:
            num[g] = num.get(g, 0.0) + float((sr[g] * su[g]).sum())
            den[g] = den.get(g, 0.0) + float((su[g] * su[g]).sum())
    surv = {g: num[g] / den[g] for g in num if den[g] > 0}
    tok = AutoTokenizer.from_pretrained("EleutherAI/pythia-160m", cache_dir=str(mc.HF_CACHE))
    grp = Builder(tok, 256, seed=0).ioi()
    func = {"R": ioi_metric(MR, grp), "C": ioi_metric(MC, grp), "U": ioi_metric(MU, grp), "0": ioi_metric(M0, grp)}
    for g in ("qk", "v", "o", "mlp"):
        m = load(br)
        with torch.no_grad():
            pc = dict(MC.named_parameters())
            for n, p in m.named_parameters():
                if split(n, p, H, d, dh).get(g) is not None:
                    tgt = split(n, p.data, H, d, dh)[g]
                    tgt.copy_(split(n, pc[n].data, H, d, dh)[g])
        func["R_with_C_" + g] = ioi_metric(m, grp)
    res = {"survival": surv, "ioi": func}
    print(json.dumps({"survival": {k: round(v, 3) for k, v in surv.items()}, "ioi": {k: round(v, 3) for k, v in func.items()}}), flush=True)
    json.dump(res, open(out, "w"), indent=1)


if __name__ == "__main__":
    main()
