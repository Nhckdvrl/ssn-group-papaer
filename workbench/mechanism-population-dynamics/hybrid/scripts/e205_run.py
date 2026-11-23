#!/usr/bin/env python3
"""E205: Falcon-H1 (parallel Mamba-2 + attention in every layer); switches in layers 0-2, then E194's R1 + NLL.
COND: none | noconv | nomem | noattn | noconv_noattn
Usage: e205_run.py MODEL_DIR ITEMS PASSAGES OUT_DIR COND"""
import json
import sys
import time
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, str(Path(__file__).parent))
import e195_capture as cap  # noqa: E402

LAYERS = (0, 1, 2)


def main():
    mdir, items, passages, out, cond = sys.argv[1:6]
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    tok = AutoTokenizer.from_pretrained(mdir)
    model = AutoModelForCausalLM.from_pretrained(mdir, dtype=torch.bfloat16).cuda().eval()
    base, emb, layers = cap.parts(model)
    done = []
    for li in LAYERS:
        layer = layers[li]
        mx, attn = layer.mamba, layer.self_attn
        with torch.no_grad():
            if cond in ("noconv", "noconv_noattn"):
                mx.conv1d.weight[..., :-1] = 0; done.append(f"{li}:conv")
            if cond == "nomem":
                mx.A_log += 20; done.append(f"{li}:A_log")
        if cond in ("noattn", "noconv_noattn"):
            attn.register_forward_hook(lambda m, i, o: ((torch.zeros_like(o[0]),) + tuple(o[1:])) if isinstance(o, tuple) else torch.zeros_like(o))
            done.append(f"{li}:attn")
    start = tok.bos_token_id
    pad = tok.pad_token_id if tok.pad_token_id is not None else (tok.eos_token_id or 0)
    t0 = time.time()
    nll = cap.mode_nll(model, tok, start, passages)
    I = json.loads(Path(items).read_text())
    I["S"] = [it for it in I["S"] if all(str(m) in it["splits"] for m in range(2, 7))]
    s = cap.mode_S(cap.Capture(model, start, pad), I["S"], out, 4)
    res = {"cond": cond, "switched": done, **nll, **s, "sec": round(time.time() - t0, 1)}
    (out / "meta.json").write_text(json.dumps(res))
    print(json.dumps({"cond": cond, "nll_mean": round(nll["nll_mean"], 3), "greedy": nll["greedy"][:60]}), flush=True)


if __name__ == "__main__":
    main()
