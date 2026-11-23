#!/usr/bin/env python3
"""E204 readout of one checkpoint: E194's R1 (set S) + per-token NLL on 50 EWT passages (no start token, as in E198).
Usage: e204_readout.py CKPT_DIR TOKENIZER_DIR ITEMS PASSAGES OUT_DIR"""
import json
import sys
import time
from pathlib import Path

import fla  # noqa: F401
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, str(Path(__file__).parent))
import e195_capture as cap  # noqa: E402


def main():
    ckpt, tokdir, items, passages, out = sys.argv[1:6]
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    tok = AutoTokenizer.from_pretrained(tokdir)
    model = AutoModelForCausalLM.from_pretrained(ckpt, dtype=torch.bfloat16).cuda().eval()
    pad = tok.pad_token_id if tok.pad_token_id is not None else (tok.eos_token_id or 0)
    t0 = time.time()
    nll = cap.mode_nll(model, tok, None, passages)
    I = json.loads(Path(items).read_text())
    s = cap.mode_S(cap.Capture(model, None, pad), I["S"], out, 4)
    res = {"ckpt": ckpt, **nll, **s, "sec": round(time.time() - t0, 1)}
    (out / "meta.json").write_text(json.dumps(res))
    print(json.dumps({"ckpt": ckpt, "nll_mean": round(nll["nll_mean"], 3)}), flush=True)


if __name__ == "__main__":
    main()
