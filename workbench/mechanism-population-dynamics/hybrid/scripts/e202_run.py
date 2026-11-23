#!/usr/bin/env python3
"""E202: R1 (set S) + NLL on an fla-hub model, optionally with the short convs of layers 0..K switched to the
current tap only (noconv). Reuses e195_capture's Capture / mode_S / mode_nll.
Usage: e202_run.py MODEL_DIR ITEMS PASSAGES OUT_DIR [--noconv_upto K]
"""
import argparse
import json
import sys
import time
from pathlib import Path

import fla.models  # noqa: F401  (registers the fla model classes with transformers)
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, str(Path(__file__).parent))
import e195_capture as cap  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("model"); ap.add_argument("items"); ap.add_argument("passages"); ap.add_argument("out")
    ap.add_argument("--noconv_upto", type=int, default=-1)
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    tok = AutoTokenizer.from_pretrained(a.model)
    model = AutoModelForCausalLM.from_pretrained(a.model, dtype=torch.bfloat16).cuda().eval()
    base, emb, layers = cap.parts(model)
    switched = []
    if a.noconv_upto >= 0:
        for li in range(a.noconv_upto + 1):
            for name, m in layers[li].named_modules():
                w = getattr(m, "weight", None)
                if isinstance(m, torch.nn.Conv1d) and w is not None and w.dim() == 3 and w.shape[1] == 1 and w.shape[-1] > 1:
                    with torch.no_grad():
                        w[..., :-1] = 0
                    switched.append(f"{li}.{name}:{tuple(w.shape)}")
        assert switched, "no short conv found"
    start = tok.bos_token_id
    pad = tok.pad_token_id if tok.pad_token_id is not None else (tok.eos_token_id or 0)
    t0 = time.time()
    nll = cap.mode_nll(model, tok, start, a.passages)
    I = json.loads(Path(a.items).read_text())
    I["S"] = [it for it in I["S"] if all(str(m) in it["splits"] for m in range(2, 7))]  # 599/600 under the Llama tokenizer
    c = cap.Capture(model, start, pad)
    s = cap.mode_S(c, I["S"], out, 4)
    res = {"model": a.model, "noconv_upto": a.noconv_upto, "switched": switched, "n_layers": len(layers), **nll, **s,
           "sec": round(time.time() - t0, 1)}
    (out / "meta.json").write_text(json.dumps(res))
    print(json.dumps({k: res[k] for k in ("model", "noconv_upto", "nll_mean", "greedy", "sec")}), flush=True)


if __name__ == "__main__":
    main()
