"""S03 / Phase 2 corpus — the REAL Instruct-SFT mixture.

Phase 1 located the largest, and the only purely `goal -> STOP`, transition on
the OLMo-3 chain at Think-SFT -> Instruct-SFT.  Phase 2 therefore starts from
the real incoming checkpoint (Think-SFT final) and trains on the real incoming
data: `allenai/Dolci-Instruct-SFT`, the mixture the released Instruct-SFT
checkpoint was actually trained on (named in its model card).

This replaces the Base + arbitrary-Tulu-subset setup, which corresponded to no
real training stage.

Single-turn user/assistant examples only, so every example has exactly one
assistant turn-end token and the EOT-only / content-only supervision masks in
Phase 2 are unambiguous.
"""
import json, random, sys
import pyarrow.parquet as pq
from huggingface_hub import hf_hub_download

N = int(sys.argv[1]) if len(sys.argv) > 1 else 12000
REPO = "allenai/Dolci-Instruct-SFT"
OUT = "data/dolci_instruct_sft_subset.jsonl"

rows = []
for shard in (0, 1):
    p = hf_hub_download(REPO, f"data/train-{shard:05d}-of-00015.parquet",
                        repo_type="dataset")
    print("shard", shard, p, flush=True)
    t = pq.read_table(p, columns=["messages", "source_dataset", "domain"])
    rows.extend(t.to_pylist())
    print("  cumulative rows:", len(rows), flush=True)

random.Random(7).shuffle(rows)
n = 0
with open(OUT, "w") as f:
    for ex in rows:
        m = ex["messages"]
        if len(m) != 2 or m[0]["role"] != "user" or m[1]["role"] != "assistant":
            continue
        if not (m[1]["content"] or "").strip():
            continue
        # tool-use turns carry extra fields and a different termination regime
        if any(r.get("function_calls") or r.get("functions") for r in m):
            continue
        f.write(json.dumps({"messages": [{"role": r["role"], "content": r["content"]}
                                         for r in m],
                            "source": ex.get("source_dataset", ""),
                            "domain": ex.get("domain", "")}) + "\n")
        n += 1
        if n >= N:
            break
print("wrote", n, "to", OUT, flush=True)
