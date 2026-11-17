#!/usr/bin/env python3
"""E192: re-dump (router inputs on the E191 token set + held-out NLL) from a saved arm state, for points whose in-training
dump is missing or for extra analyses.  The training script (e192_train.py) already dumps every --save-every iters; this is
the offline path.  Accepts full_cXXXX.pt (bf16 weights) or resume.pt (fp32 model + optimizer).
usage: e192_dump.py --state /tmp/xiang_e192/arms/A1/full_c0270.pt --start-ckpt /tmp/xiang_e192/ckpt/iter_0001080 --out DIR"""
import argparse, json, os, sys
import numpy as np
import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e192_train import Flame, cfg_from_args, read_args, eval_streams, eval_nll, DumpSet, save_routers  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", required=True); ap.add_argument("--start-ckpt", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--root", default="/tmp/xiang_e192"); ap.add_argument("--no-nll", action="store_true")
    a = ap.parse_args()
    c = cfg_from_args(read_args(a.start_ckpt))
    model = Flame(c).cuda()
    S = torch.load(a.state, map_location="cuda", weights_only=False)
    S = S["model"] if "model" in S else S
    model.load_state_dict({k: v.float() for k, v in S.items()}); model.eval()
    os.makedirs(a.out, exist_ok=True)
    save_routers(model, f"{a.out}/routers.npz")
    rec = {"state": a.state}
    if not a.no_nll:
        ev = eval_nll(model, eval_streams(a.root)); np.savez_compressed(f"{a.out}/nll.npz", **ev)
        rec.update(nll_dclm=float(ev["dclm"].astype(np.float64).mean()), nll_wikitext=float(ev["wikitext"].astype(np.float64).mean()))
    rec["lm_eng"] = DumpSet(a.root).dump(model, f"{a.out}/dump", {"state": a.state})
    json.dump(rec, open(f"{a.out}/eval.json", "w"), indent=1); print(rec)


if __name__ == "__main__":
    main()
