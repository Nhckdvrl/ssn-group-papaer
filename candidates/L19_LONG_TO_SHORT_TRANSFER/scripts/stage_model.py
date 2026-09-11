"""Stage the base model on local NVMe in bf16.

The HF cache is on a 52 MB/s NFS mount and the checkpoint is fp32 across 291 tensor
shards; four ranks each pulling 32 GB over that mount costs ~40 minutes of pure I/O per
run. Casting to bf16 once and writing to local disk makes it 16 GB loaded in seconds.
bf16 is the training dtype anyway, so nothing is lost.
"""
import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

SRC = "princeton-nlp/Llama-3-8B-ProLong-512k-Base"
DST = "/tmp/l19/prolong-512k-base-bf16"

if __name__ == "__main__":
    os.makedirs(DST, exist_ok=True)
    m = AutoModelForCausalLM.from_pretrained(SRC, dtype=torch.bfloat16)
    m.save_pretrained(DST, safe_serialization=True, max_shard_size="4GB")
    AutoTokenizer.from_pretrained(SRC).save_pretrained(DST)
    print("STAGED", DST)
