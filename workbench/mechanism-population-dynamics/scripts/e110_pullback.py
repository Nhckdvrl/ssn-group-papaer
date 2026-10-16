"""E110: why does general training revert read-side (QK) unlearning but not write-side (OV / MLP) unlearning?

For an unlearned model theta_U and the original theta_0, let delta = theta_0 - theta_U (the revert direction).
On general Pile data, at theta_U:
  - the general-loss gradient g; report cos(-g, delta) and the directional slope -g.delta/|delta|
  - the Pile loss and the IOI margin along the straight path theta_U + eps * delta, eps in {0, .25, .5, .75, 1}
A large positive slope means general training is pulled back toward the original (reverts the unlearning).

Usage: e110_pullback.py OUT.json MODEL_DIR [MODEL_DIR ...]
"""
import json
import sys

import pyarrow.parquet as pq
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

import mp_common as mc
from e89_labor import Builder

BASE = "/home/xiang/mechpop_cache/ckpt/pythia-160m_step100000"
SHARD = mc.CACHE / "pile_tok" / "shard00003.parquet"


def ioi(model, groups):
    vals = []
    with torch.no_grad():
        for g in groups:
            lg = model(g["toks"]).logits[:, -1].float()
            io = torch.tensor([t[0] for t in g["tg"]])
            s = torch.tensor([f[0] for f in g["fo"]])
            vals.append((lg.gather(1, io[:, None]) - lg.gather(1, s[:, None])).squeeze(1))
    return float(torch.cat(vals).mean())


def main():
    out, srcs = sys.argv[1], sys.argv[2:]
    tok = AutoTokenizer.from_pretrained("EleutherAI/pythia-160m", cache_dir=str(mc.HF_CACHE))
    groups = Builder(tok, 128, seed=0).ioi()
    tbl = pq.read_table(SHARD).column("tokens")
    xs = [torch.tensor(tbl.slice(100000 + 8 * i, 8).to_pylist())[:, :512] for i in range(4)]
    m0 = AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.float32)
    p0 = {n: p.detach().clone() for n, p in m0.named_parameters()}
    del m0
    res = {}
    for src in srcs:
        m = AutoModelForCausalLM.from_pretrained(src, dtype=torch.float32)
        pu = {n: p.detach().clone() for n, p in m.named_parameters()}
        delta = {n: p0[n] - pu[n] for n in pu}
        dn = sum(float(d.norm() ** 2) for d in delta.values()) ** 0.5
        m.zero_grad(set_to_none=True)
        for x in xs:
            (m(x, labels=x).loss / len(xs)).backward()
        g = {n: p.grad for n, p in m.named_parameters()}
        gn = sum(float(v.norm() ** 2) for v in g.values()) ** 0.5
        dot = sum(float((-g[n] * delta[n]).sum()) for n in delta)
        # where is the pull concentrated: by parameter group
        by = {}
        for n in delta:
            key = "qkv" if "query_key_value" in n else "dense" if "attention.dense" in n else "mlp" if "mlp" in n else "other"
            by[key] = by.get(key, 0.0) + float((-g[n] * delta[n]).sum())
        path = []
        with torch.no_grad():
            for eps in (0.0, 0.25, 0.5, 0.75, 1.0):
                for n, p in m.named_parameters():
                    p.copy_(pu[n] + eps * delta[n])
                lm = sum(float(m(x, labels=x).loss) for x in xs) / len(xs)
                path.append({"eps": eps, "lm": lm, "ioi": ioi(m, groups)})
        res[src] = {"delta_norm": dn, "grad_norm": gn, "cos_pull": dot / (dn * gn), "slope": dot / dn, "pull_by_group": by, "path": path}
        print(src.split("/")[-1], {"cos_pull": round(dot / (dn * gn), 4), "slope": round(dot / dn, 5),
                                   "dLM_path": [round(q["lm"] - path[-1]["lm"], 5) for q in path],
                                   "ioi_path": [round(q["ioi"], 2) for q in path]}, flush=True)
        del m
    json.dump(res, open(out, "w"), indent=1)


if __name__ == "__main__":
    main()
