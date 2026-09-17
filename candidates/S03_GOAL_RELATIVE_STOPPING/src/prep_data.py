"""S03 / E02 training corpus: an ordinary public instruction-response subset.

Deliberately NOT a stopping benchmark.  Each example supplies many "continue"
positions and exactly one response boundary, and the model never sees the E01
contrast.  We pull two shards of the Tulu-3 OLMo-2 SFT mixture and take a fixed
random single-turn subset; the same file is then used by every arm.
"""
import json, random, sys
import pyarrow.parquet as pq
from huggingface_hub import hf_hub_download

N = int(sys.argv[1]) if len(sys.argv) > 1 else 12000
REPO = "allenai/tulu-3-sft-olmo-2-mixture-0225"

rows = []
for shard in (0, 1):
    p = hf_hub_download(REPO, f"data/train-0000{shard}-of-00006.parquet",
                        repo_type="dataset")
    print("shard", shard, p, flush=True)
    t = pq.read_table(p, columns=["messages", "source"])
    rows.extend(t.to_pylist())
    print("  cumulative rows:", len(rows), flush=True)

random.Random(7).shuffle(rows)
n = 0
with open("data/tulu_subset.jsonl", "w") as f:
    for ex in rows:
        m = ex["messages"]
        if len(m) != 2 or m[0]["role"] != "user" or m[1]["role"] != "assistant":
            continue
        if not m[1]["content"].strip():
            continue
        f.write(json.dumps({"messages": [{"role": r["role"], "content": r["content"]}
                                         for r in m],
                            "source": ex.get("source", "")}) + "\n")
        n += 1
        if n >= N:
            break
print("wrote", n, flush=True)
