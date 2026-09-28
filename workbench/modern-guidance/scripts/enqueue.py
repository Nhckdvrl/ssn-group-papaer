"""Write job files for a set of runs. Usage: python enqueue.py <experiment.json>
experiment.json: {"queue": "...", "prompt_set": "geneval", "prompt_idx": [...] | "all",
                  "seeds": [...], "chunk": 8, "steps": 30, "runs": {"name": spec, ...}}"""
import json, os, sys
from mg import prompts as P
exp = json.load(open(sys.argv[1]))
q = exp["queue"]; os.makedirs(os.path.join(q, "pending"), exist_ok=True)
idx = exp["prompt_idx"] if exp["prompt_idx"] != "all" else list(range(len(P.load(exp["prompt_set"]))))
items = [[p, s] for s in exp["seeds"] for p in idx]
n = 0
for run, spec in exp["runs"].items():
    for k in range(0, len(items), exp.get("chunk", 8)):
        job = dict(run=run, spec=spec, steps=exp.get("steps", 30), height=exp.get("height", 1024),
                   width=exp.get("width", 1024), prompt_set=exp["prompt_set"], items=items[k:k + exp.get("chunk", 8)])
        with open(os.path.join(q, "pending", f"{exp.get('priority', 50):03d}_{run}_{k:05d}.json"), "w") as fh:
            json.dump(job, fh)
        n += 1
print("enqueued", n, "jobs,", len(items) * len(exp["runs"]), "images")
