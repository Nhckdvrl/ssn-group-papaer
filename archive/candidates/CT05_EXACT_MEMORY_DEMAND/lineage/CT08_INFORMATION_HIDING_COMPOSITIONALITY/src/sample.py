"""E00 instance sample: 10 OOLONG-synth domains x {16384, 32768} x 20 (seed 0)."""
import glob, json, random
import pandas as pd
p = glob.glob("/home/xiang/.cache/huggingface/hub/datasets--oolongbench--oolong-synth/snapshots/*/")[0]
cols = ["id", "context_len", "dataset", "context_window_text", "question", "task_group", "task", "answer", "answer_type"]
d = pd.concat([pd.read_parquet(f, columns=cols) for f in sorted(glob.glob(p + "data/*.parquet"))])
d = d[d.context_len.isin([16384, 32768])]
rng = random.Random(0)
out = []
for (ds, cl), g in sorted(d.groupby(["dataset", "context_len"])):
    idx = sorted(g.index.tolist() if False else range(len(g)))
    pick = rng.sample(idx, 20)
    for i in pick:
        r = g.iloc[i]
        out.append({"id": int(r.id), "dataset": ds, "context_len": int(cl), "task_group": r.task_group, "task": r.task,
                    "question": r.question, "answer": str(list(r.answer)) if not isinstance(r.answer, str) else r.answer,
                    "answer_type": r.answer_type, "context": r.context_window_text})
with open("data/e00_instances.jsonl", "w") as f:
    for i, r in enumerate(out):
        r["iid"] = i
        f.write(json.dumps(r) + "\n")
print(len(out), sum(len(r["context"]) for r in out) / len(out), "chars avg")
