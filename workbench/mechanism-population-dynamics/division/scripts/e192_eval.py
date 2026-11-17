#!/usr/bin/env python3
"""E192: anchors and positive controls on official FLAME-MoE-290M checkpoints with the E192 model code
(e192_train.Flame): held-out NLL (DCLM eval stream + wikitext-103 test, per token fp16), English LM loss on the E191 text
(positive control vs E191 summary.json: iter 1080 FLORES-eng 4.2066 / UD 4.1569 with the HF Qwen2Moe mapping), and the
router-input dump on the E191 token set (same format as the training arms' dump_cXXXX).
--source bf16 (default; what the released model is) or master (fp32 master params, needs --full fetch).
usage: e192_eval.py --ckpt /tmp/xiang_e192/ckpt/iter_0001080 --out /tmp/xiang_e192/official/i1080"""
import argparse, json, os, sys, time
import numpy as np
import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e192_train import Flame, cfg_from_args, read_args, load_official, eval_streams, eval_nll, DumpSet, save_routers, GB, SEQ  # noqa


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--root", default="/tmp/xiang_e192"); ap.add_argument("--source", choices=["bf16", "master"], default="bf16")
    a = ap.parse_args(); t0 = time.time()
    os.makedirs(a.out, exist_ok=True)
    margs = read_args(a.ckpt); c = cfg_from_args(margs)
    it = int(os.path.basename(a.ckpt.rstrip("/")).split("_")[-1])
    model = Flame(c).cuda()
    src, _, chk = load_official(model, a.ckpt, master=a.source == "master")
    model.eval()
    ev = eval_nll(model, eval_streams(a.root))
    np.savez_compressed(f"{a.out}/nll.npz", **ev)
    save_routers(model, f"{a.out}/routers.npz")
    lm = DumpSet(a.root).dump(model, f"{a.out}/dump", {"arm": "official", "official_iter": it, "tokens": it * GB * SEQ, "source": src})
    rec = {"official_iter": it, "source": src, "load_check": chk, "nll_dclm": float(ev["dclm"].astype(np.float64).mean()),
           "nll_wikitext": float(ev["wikitext"].astype(np.float64).mean()), "lm_eng": lm, "wall_s": time.time() - t0}
    json.dump(rec, open(f"{a.out}/eval.json", "w"), indent=1); print(rec, flush=True)


if __name__ == "__main__":
    main()
