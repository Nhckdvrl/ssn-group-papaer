#!/usr/bin/env python3
"""E192 readout 4 support: route the DCLM held-out stream (1024 windows x 2048) under one saved arm state and store, per
MoE layer, the fp32 router's top-6 for every input position (int8 [8, 1024, 2048, 6]).  Used for the H(e|id) stratum
(entropy of the top-1 expert given the input token id, computed in e192_analyze.py).
usage: e192_hroute.py --state /tmp/xiang_e192/arms/A1/full_c0540.pt --start-ckpt /tmp/xiang_e192/ckpt/iter_0001080 --out FILE.npy"""
import argparse, os, sys
import numpy as np
import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e192_train import Flame, cfg_from_args, read_args, eval_streams, BF  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--state", required=True); ap.add_argument("--start-ckpt", required=True); ap.add_argument("--out", required=True)
ap.add_argument("--root", default="/tmp/xiang_e192")
a = ap.parse_args()
c = cfg_from_args(read_args(a.start_ckpt))
model = Flame(c).cuda()
S = torch.load(a.state, map_location="cuda", weights_only=False)
S = S["model"] if "model" in S else S
model.load_state_dict({k: v.float() for k, v in S.items()}); model.eval()
W = eval_streams(a.root)["dclm"]
moe = model.moe_layers(); K = c["K"]
OUT = np.zeros((len(moe), len(W), W.shape[1] - 1, K), np.int8)
with torch.no_grad():
    for b0 in range(0, len(W), 16):
        ids = torch.from_numpy(W[b0:b0 + 16, :-1].astype(np.int64)).cuda()
        st = {"aux_on": False, "dump": []}
        with torch.autocast("cuda", BF):
            model(ids, st)
        for j, h in enumerate(st["dump"]):
            Wr = model.decoder.layers[moe[j]].mlp.router.weight.float()
            OUT[j, b0:b0 + len(ids)] = (h.float() @ Wr.T).topk(K, -1).indices.view(len(ids), -1, K).cpu().numpy().astype(np.int8)
np.save(a.out, OUT)
print("saved", a.out, OUT.shape)
