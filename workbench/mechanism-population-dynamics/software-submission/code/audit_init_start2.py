"""Audit: the six 1B runs whose head layout disagrees with every same-seed sibling (Fig 1 matrix) - did they start
from their seed's published step0? Reads one weight tensor per checkpoint by HTTP range request (no full download):
  published step0 of the run vs the seed's c4 step0; step-2500 weights vs every seed's step0, vs the partner run, vs c4."""
import json
import struct

import requests
import torch
from huggingface_hub import hf_hub_url
from huggingface_hub.utils import build_hf_headers

import mp_common as mc

K = "model.transformer.blocks.5.att_proj.weight"
DT = {"F32": torch.float32, "BF16": torch.bfloat16, "F16": torch.float16}
SEEDS = ["default", "large-aux-2", "large-aux-3"]
H = build_hf_headers()


def get(url, a=None, b=None):
    h = dict(H)
    if a is not None:
        h["Range"] = f"bytes={a}-{b}"
    r = requests.get(url, headers=h, timeout=300, allow_redirects=True)
    r.raise_for_status()
    return r


def tensor(rec, step, seed):
    repo, rev = f"allenai/DataDecide-{rec}-1B", f"step{step}-seed-{seed}"
    idx = get(hf_hub_url(repo, "model.safetensors.index.json", revision=rev)).json()["weight_map"]
    url = hf_hub_url(repo, idx[K], revision=rev)
    n = struct.unpack("<Q", get(url, 0, 7).content)[0]
    meta = json.loads(get(url, 8, 8 + n - 1).content)[K]
    a, b = meta["data_offsets"]
    raw = get(url, 8 + n + a, 8 + n + b - 1).content
    return torch.frombuffer(bytearray(raw), dtype=DT[meta["dtype"]]).float().flatten()


def c(a, b):
    return round(float(torch.corrcoef(torch.stack([a, b]))[0, 1]), 4)


def main():
    pairs = [("dclm-baseline-qc-7p-fw2", "dclm-baseline-qc-7p-fw3", "default"),
             ("dolma1_7-no-math-code", "dolma1_7-no-reddit", "default"),
             ("falcon-and-cc-qc-orig-10p", "falcon-and-cc-qc-tulu-10p", "large-aux-3")]
    S0 = {s: tensor("c4", 0, s) for s in SEEDS}
    c4_2500 = {s: tensor("c4", 2500, s) for s in SEEDS}
    out = {}
    for r1, r2, s in pairs:
        w = {r: tensor(r, 2500, s) for r in (r1, r2)}
        for r in (r1, r2):
            z = tensor(r, 0, s)
            out[f"{r}|{s}"] = {"published_step0_vs_c4_step0_same_seed": c(z, S0[s]),
                               "step2500_vs_step0": {s0: c(w[r], S0[s0]) for s0 in SEEDS},
                               "step2500_vs_partner_step2500": c(w[r1], w[r2]),
                               "step2500_vs_c4_step2500_same_seed": c(w[r], c4_2500[s])}
            print(r, s, out[f"{r}|{s}"], flush=True)
    ref = {s: c(c4_2500[s], tensor("dolma1_7", 2500, s)) for s in SEEDS}
    out["reference_c4_vs_dolma1_7_step2500_same_seed"] = ref
    print("reference: c4 vs dolma1_7 step2500, same seed", ref, flush=True)
    (mc.RESULTS / "audit_outlier_runs.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
