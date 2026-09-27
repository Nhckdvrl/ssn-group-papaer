"""Descriptive, no model calls. For each checkpoint, the CT05 oracle's top block (largest single-block
KV-hide dNLL) is the 'source'. Report how often each query stage ranks it in its top-1 / top-3 blocks:
DEPLOY, HDR, TOOL, KEY/PROSE, PREVALUE, then cumulative through the j-th value token's query
(j = 0 is the query that has just emitted value token 1), and FUTURE. Uses stored per-query attention."""
import glob, json
import numpy as np
ct05 = {}
for f in glob.glob("/home/xiang/ssn-group-papaer/candidates/CT05_EXACT_MEMORY_DEMAND/results/e01/q35_9b.s*.jsonl"):
    for l in open(f):
        r = json.loads(l)
        if "skip" not in r:
            ct05[r["cid"]] = np.array([b["dnll"] for b in r["blocks"]])
recs = [json.loads(l) for f in glob.glob("results/e00/q35_9b.s*.jsonl") for l in open(f)]
recs = [r for r in recs if "skip" not in r]


def hit(scores, src, k):
    return int(src in np.argsort(-scores)[:k])


for src_name in ["tau", "swe"]:
    rows = {}
    n = 0
    for r in recs:
        if r["src"] != src_name:
            continue
        orc = ct05[r["cid"]]
        if orc.max() < 1.0 or len(orc) < 5:  # need a clearly critical block
            continue
        n += 1
        z = np.load(f"results/e00/att/{r['cid']}.npz")
        blk, win = z["blk"].astype(np.float32), z["win"].astype(np.float32)
        L0 = blk.shape[0] - r["T"]
        s = int(orc.argmax())
        stages = {"DEPLOY": (win + blk[:L0].mean(0)) / 2}
        for st in ["HDR", "TOOL", "PROSE", "KEY", "PREVALUE"]:
            if st in r["bnd"]:
                stages[st] = blk[:L0 + r["bnd"][st] + 1].mean(0)
        pv = L0 + r["bnd"]["PREVALUE"]
        for j in range(0, 6):
            if pv + 1 + j < blk.shape[0] - 1:
                stages[f"v{j + 1}"] = blk[:pv + 2 + j].mean(0)
                stages[f"v{j + 1}_only"] = blk[pv + 1 + j]  # that single query alone
        stages["FUTURE"] = blk[L0 - 1:-1].mean(0)
        for st, sc in stages.items():
            rows.setdefault(st, []).append((hit(sc, s, 1), hit(sc, s, 3)))
    print(f"{src_name}: {n} checkpoints with a critical block (oracle max dNLL >= 1)")
    for st, v in rows.items():
        v = np.array(v)
        print(f"   {st:10s} hit@1 {v[:, 0].mean():.2f}  hit@3 {v[:, 1].mean():.2f}  (n={len(v)})")
