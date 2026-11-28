#!/usr/bin/env python3
"""memcap.py SCRIPT ARGS... : run SCRIPT with a hard CUDA memory cap of $SKT_MEMCAP_GB GiB (for evals that share a GPU
with a training job: if the eval would exceed the cap, the eval OOMs, never the co-located training job)."""
import os
import runpy
import sys

import torch

cap = float(os.environ["SKT_MEMCAP_GB"]) * 2 ** 30
torch.cuda.set_per_process_memory_fraction(min(1.0, cap / torch.cuda.get_device_properties(0).total_memory), 0)
sys.path.insert(0, os.getcwd())
sys.argv = sys.argv[1:]
runpy.run_path(sys.argv[0], run_name="__main__")
