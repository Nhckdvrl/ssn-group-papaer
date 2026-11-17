#!/usr/bin/env python3
"""E192 p6 check (card 追加臂, 11-18): held-out NLL of one model on the third-shard DCLM stream (eval_dclm3.u16, global
shard 05) next to the original held-out stream (eval_dclm.u16, global shard 10), per token fp16 + window means.
Model = official Megatron checkpoint (bf16 tensors; --ckpt) or a saved arm state (--state full_cXXXX.pt, needs --start-ckpt).
usage: e192_p6.py --name off1620 --ckpt /tmp/xiang_e192/ckpt/iter_0001620 --out /tmp/xiang_e192/p6
       e192_p6.py --name A1_c0540 --state /tmp/xiang_e192/arms/A1/full_c0540.pt --start-ckpt /tmp/xiang_e192/ckpt/iter_0001080 --out ..."""
import argparse, json, os, sys
import numpy as np
import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e192_train import Flame, cfg_from_args, read_args, load_official, eval_nll, SEQ  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--name", required=True); ap.add_argument("--out", required=True); ap.add_argument("--root", default="/tmp/xiang_e192")
ap.add_argument("--ckpt"); ap.add_argument("--state"); ap.add_argument("--start-ckpt")
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)
c = cfg_from_args(read_args(a.ckpt or a.start_ckpt))
model = Flame(c).cuda()
if a.ckpt:
    load_official(model, a.ckpt, master=False)
else:
    S = torch.load(a.state, map_location="cuda", weights_only=False); S = S["model"] if "model" in S else S
    model.load_state_dict({k: v.float() for k, v in S.items()})
model.eval()
streams = {}
for k, f in (("dclm_gs10", "eval_dclm.u16"), ("dclm_gs05", "eval_dclm3.u16")):
    x = np.fromfile(f"{a.root}/dclm/{f}", np.uint16); n = (len(x) - 1) // SEQ
    streams[k] = np.stack([x[j * SEQ:j * SEQ + SEQ + 1] for j in range(n)])
ev = eval_nll(model, streams)
np.savez_compressed(f"{a.out}/{a.name}_nll.npz", **ev)
rec = {"name": a.name, "ckpt": a.ckpt, "state": a.state, **{k: float(v.astype(np.float64).mean()) for k, v in ev.items()}}
json.dump(rec, open(f"{a.out}/{a.name}.json", "w"), indent=1); print(rec, flush=True)
