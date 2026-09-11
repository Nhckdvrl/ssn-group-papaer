"""Fetch the shared UltraChat backbone (identical in every arm) and the ChatQA2 data
used only for the mother positive control."""
import json, sys
from datasets import load_dataset

def ultrachat(n=10000, out="data/ultrachat.jsonl"):
    ds = load_dataset("HuggingFaceH4/ultrachat_200k", split="train_sft", streaming=True)
    w = open(out, "w"); k = 0
    for r in ds:
        if not r["messages"]: continue
        w.write(json.dumps({"prompt_id": r["prompt_id"], "messages": r["messages"]}) + "\n")
        k += 1
        if k >= n: break
    w.close(); print("ultrachat", k)

if __name__ == "__main__":
    ultrachat(int(sys.argv[1]) if len(sys.argv) > 1 else 10000)
