"""Shared backbone + positive-control data.

UltraChat block A (10k) is identical in every single run.
UltraChat block B (next 10k) is the short arm of the positive control.
ChatQA2 (10k)     is the long  arm of the positive control.
"""
import json, sys, os
from datasets import load_dataset

def ultrachat(n=20000, out="data/ultrachat.jsonl"):
    ds = load_dataset("HuggingFaceH4/ultrachat_200k", split="train_sft", streaming=True)
    with open(out, "w") as w:
        k = 0
        for r in ds:
            if not r["messages"]: continue
            w.write(json.dumps({"prompt_id": r["prompt_id"], "messages": r["messages"]}) + "\n")
            k += 1
            if k >= n: break
    print("ultrachat", k, "->", out)

def chatqa2(n=10000, out="data/chatqa2.jsonl"):
    from huggingface_hub import hf_hub_download
    p = hf_hub_download("nvidia/ChatQA2-Long-SFT-data",
                        "long_sft/long_sft_QA_train.json", repo_type="dataset")
    import ijson
    with open(p, "rb") as f, open(out, "w") as w:
        k = 0
        for rec in ijson.items(f, "item"):
            w.write(json.dumps(rec) + "\n"); k += 1
            if k >= n: break
    print("chatqa2", k, "->", out)

if __name__ == "__main__":
    which = sys.argv[1]
    if which == "ultrachat": ultrachat(int(sys.argv[2]) if len(sys.argv)>2 else 20000)
    else: chatqa2(int(sys.argv[2]) if len(sys.argv)>2 else 10000)
