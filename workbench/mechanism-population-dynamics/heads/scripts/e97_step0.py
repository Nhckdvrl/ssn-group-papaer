"""E97 control: the lesioned weights at step 0 (head re-initialised, no training), to separate instant
(inference-time) redistribution from training-driven take-over. Same reset as e93_lesion.py --arm H (init_seed 1234).

Usage: e97_step0.py HEAD OUTDIR
"""
import sys

import torch
from transformers import AutoModelForCausalLM

from e93_lesion import reinit_head

BASE = "/home/xiang/mechpop_cache/ckpt/pythia-160m_step100000"
head, out = sys.argv[1], sys.argv[2]
model = AutoModelForCausalLM.from_pretrained(BASE, torch_dtype=torch.float32)
gen = torch.Generator().manual_seed(1234)
l, h = map(int, head.split("."))
reinit_head(model, l, h, gen, "all")
model.save_pretrained(out, safe_serialization=False)
print("saved", out)
