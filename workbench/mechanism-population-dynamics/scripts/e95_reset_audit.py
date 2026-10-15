"""E95: did any PolyPythias run get reset to its initial weights during training? (audit; no training)

Usage: e95_reset_audit.py --size 410m [--steps 0,143000] -> results/e95/audit_<size>.json
For every run of the size (original + seed1-9) the given checkpoints are fetched with curl (HF Xet stalls here),
and the cosine similarity of selected tensors to the run's own step-0 initialisation is computed. A normally trained
run moves far from its init; a run restarted from step 0 late in training stays close to it.
"""
import argparse
import json
import os
import shutil
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor

import torch

import mp_common as mc

OUT = mc.RESULTS / "e95"
KEYS = ["gpt_neox.embed_in.weight", "gpt_neox.layers.0.attention.query_key_value.weight",
        "gpt_neox.layers.{mid}.mlp.dense_h_to_4h.weight", "gpt_neox.layers.{last}.attention.dense.weight", "embed_out.weight"]


def fetch(repo, step, d):
    os.makedirs(d, exist_ok=True)
    f = f"{d}/pytorch_model.bin"
    url = f"https://huggingface.co/{repo}/resolve/step{step}/pytorch_model.bin"
    subprocess.run(["curl", "-sfL", "--retry", "10", "--retry-all-errors", "-o", f, url], check=True)
    return f


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--size", required=True)
    ap.add_argument("--steps", default="0,143000")
    ap.add_argument("--seeds", default=",1,2,3,4,5,6,7,8,9")
    a = ap.parse_args()
    steps = [int(s) for s in a.steps.split(",")]
    runs = [f"EleutherAI/pythia-{a.size}" + (f"-seed{s}" if s else "") for s in a.seeds.split(",")]
    tmp = tempfile.mkdtemp(prefix=f"e95_{a.size}_", dir=str(mc.CACHE / "ckpt"))
    jobs = [(r, st) for r in runs for st in steps]
    with ThreadPoolExecutor(6) as ex:
        paths = dict(zip(jobs, ex.map(lambda j: fetch(j[0], j[1], f"{tmp}/{j[0].split('/')[1]}_{j[1]}"), jobs)))
    res = {}
    for r in runs:
        W = {st: torch.load(paths[(r, st)], map_location="cpu") for st in steps}
        nl = max(int(k.split(".layers.")[1].split(".")[0]) for k in W[0] if ".layers." in k) + 1
        keys = [k.format(mid=nl // 2, last=nl - 1) for k in KEYS]
        res[r] = {}
        for st in steps[1:]:
            res[r][st] = {k.split("neox.")[-1]: round(torch.nn.functional.cosine_similarity(
                W[st][k].float().ravel(), W[0][k].float().ravel(), 0).item(), 4) for k in keys}
        print(r, json.dumps(res[r]), flush=True)
        del W
    shutil.rmtree(tmp, ignore_errors=True)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"audit_{a.size}_{a.steps.replace(',', '-')}.json").write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
