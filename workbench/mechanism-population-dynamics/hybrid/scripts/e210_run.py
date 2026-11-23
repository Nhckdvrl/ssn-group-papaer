#!/usr/bin/env python3
"""E210: RWKV-4-Pile (token shift + WKV memory) and Pythia; switches in layers LO-HI (RWKV only), then E194's R1 + NLL.
COND: none | noshift (all time_mix_* = 1 in attention and FFN) | nomem (WKV current-token only: time_first += 20,
time_decay += 20) | noshift_nomem
Usage: e210_run.py MODEL_DIR ITEMS PASSAGES OUT_DIR COND [--layers 0-2] [--fp32]"""
import argparse
import json
import sys
import time
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, str(Path(__file__).parent))
import e195_capture as cap  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("model"); ap.add_argument("items"); ap.add_argument("passages"); ap.add_argument("out"); ap.add_argument("cond")
    ap.add_argument("--layers", default="0-2"); ap.add_argument("--fp32", action="store_true")
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    tok = AutoTokenizer.from_pretrained(a.model)
    model = AutoModelForCausalLM.from_pretrained(a.model, dtype=torch.float32 if a.fp32 else torch.bfloat16).cuda().eval()
    base, emb, layers = cap.parts(model)
    lo, hi = map(int, a.layers.split("-"))
    done = []
    with torch.no_grad():
        for li in range(lo, hi + 1):
            att, ffn = getattr(layers[li], "attention", None), getattr(layers[li], "feed_forward", None)
            if a.cond in ("noshift", "noshift_nomem"):
                for mod, tag in ((att, "att"), (ffn, "ffn")):
                    for n, p in mod.named_parameters(recurse=False):
                        if n.startswith("time_mix_"):
                            p.fill_(1.0); done.append(f"{li}.{tag}.{n}")
            if a.cond in ("nomem", "noshift_nomem"):
                att.time_first += 20; att.time_decay += 20; done.append(f"{li}.att.time_first/decay")
    assert a.cond == "none" or done, "nothing switched"
    start = tok.bos_token_id if tok.bos_token_id is not None else tok.eos_token_id
    pad = tok.pad_token_id if tok.pad_token_id is not None else (tok.eos_token_id or 0)
    t0 = time.time()
    nll = cap.mode_nll(model, tok, start, a.passages)
    I = json.loads(Path(a.items).read_text())
    I["S"] = [it for it in I["S"] if all(str(m) in it["splits"] for m in range(2, 7))]
    s = cap.mode_S(cap.Capture(model, start, pad), I["S"], out, 4)
    res = {"model": a.model, "cond": a.cond, "layers": a.layers, "switched": done, "start": start, **nll, **s,
           "sec": round(time.time() - t0, 1)}
    (out / "meta.json").write_text(json.dumps(res))
    print(json.dumps({"model": Path(a.model).name, "cond": a.cond, "n_switched": len(done), "nll_mean": round(nll["nll_mean"], 3),
                      "greedy": nll["greedy"][:50]}), flush=True)


if __name__ == "__main__":
    main()
