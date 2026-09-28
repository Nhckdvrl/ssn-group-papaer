"""GPU worker: claims job files from a queue directory and generates images.

Job json: {"run": name, "spec": rule spec, "steps": 30, "height": 1024, "width": 1024,
           "prompt_set": "geneval", "items": [[prompt_index, seed], ...]}
Output: results/runs/<run>/<prompt_set>/<pidx:05d>/samples/<seed:04d>.png  (GenEval layout)
        results/runs/<run>/<prompt_set>/<pidx:05d>/metadata.jsonl
        results/runs/<run>/<prompt_set>/geom/<pidx:05d>_<seed:04d>.npz  (per-step geometry)
"""
import argparse
import glob
import json
import os
import socket
import time

import numpy as np
import torch

from mg import prompts as P
from mg.rules import build
from mg.sampler import load_pipe, sample, MODEL_ID

MG = os.environ["MG"]


def claim(qdir):
    for f in sorted(glob.glob(os.path.join(qdir, "pending", "*.json"))):
        dst = os.path.join(qdir, "running", os.path.basename(f))
        try:
            os.rename(f, dst)
            return dst
        except OSError:
            continue
    return None


def run_job(pipe, job, batch):
    prompts = P.load(job["prompt_set"])
    out_root = os.path.join(MG, "results", "runs", job["run"], job["prompt_set"])
    os.makedirs(os.path.join(out_root, "geom"), exist_ok=True)
    rule_spec = job["spec"]
    todo = []
    for pidx, seed in job["items"]:
        png = os.path.join(out_root, f"{pidx:05d}", "samples", f"{seed:04d}.png")
        if not os.path.exists(png):
            todo.append((pidx, seed))
    for k in range(0, len(todo), batch):
        chunk = todo[k:k + batch]
        texts = [prompts[p]["prompt"] for p, _ in chunk]
        rule = build(rule_spec)  # fresh state per batch (APG momentum etc.)
        torch.cuda.synchronize()
        t0 = time.time()
        res = sample(pipe, texts, [s for _, s in chunk], rule, steps=job.get("steps", 30),
                     height=job.get("height", 1024), width=job.get("width", 1024),
                     sigmas=job.get("sigmas"))
        torch.cuda.synchronize()
        dt = (time.time() - t0) / len(chunk)
        for j, (pidx, seed) in enumerate(chunk):
            d = os.path.join(out_root, f"{pidx:05d}")
            os.makedirs(os.path.join(d, "samples"), exist_ok=True)
            meta = dict(prompts[pidx])
            meta.update(run=job["run"], spec=rule_spec, steps=job.get("steps", 30), seed=seed,
                        height=job.get("height", 1024), width=job.get("width", 1024), model=MODEL_ID,
                        sec_per_image=dt, host=socket.gethostname())
            res["images"][j].save(os.path.join(d, "samples", f"{seed:04d}.png"))
            mp = os.path.join(d, "metadata.jsonl")
            if not os.path.exists(mp):
                with open(mp, "w") as fh:
                    fh.write(json.dumps(prompts[pidx]) + "\n")
            with open(os.path.join(d, f"gen_{seed:04d}.json"), "w") as fh:
                json.dump(meta, fh)
            np.savez_compressed(os.path.join(out_root, "geom", f"{pidx:05d}_{seed:04d}.npz"),
                                sigmas=res["sigmas"], **{kk: v[:, j] for kk, v in res["geom"].items()})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--queue", required=True)
    ap.add_argument("--batch", type=int, default=2)
    a = ap.parse_args()
    for sub in ["pending", "running", "done", "failed"]:
        os.makedirs(os.path.join(a.queue, sub), exist_ok=True)
    pipe = load_pipe()
    while True:
        f = claim(a.queue)
        if f is None:
            break
        job = json.load(open(f))
        try:
            run_job(pipe, job, a.batch)
            os.rename(f, os.path.join(a.queue, "done", os.path.basename(f)))
        except Exception as e:  # keep the worker alive; record failure
            import traceback
            traceback.print_exc()
            os.rename(f, os.path.join(a.queue, "failed", os.path.basename(f)))
    print("queue empty", flush=True)


if __name__ == "__main__":
    main()
