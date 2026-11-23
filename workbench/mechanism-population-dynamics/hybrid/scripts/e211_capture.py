#!/usr/bin/env python3
"""E211: E194's mode_S / mode_N capture (with source vectors for Patchscopes) on OLMo-Hybrid under E196's switches.
Usage: e211_capture.py MODEL_DIR ITEMS OUT_DIR COND   (COND: noconv | nomem)"""
import json
import sys
import time
from pathlib import Path

import torch

sys.path.insert(0, str(Path(__file__).parent))
import e194_capture as cap  # noqa: E402
import e196_causal as c196  # noqa: E402


def main():
    mdir, items, out, cond = sys.argv[1:5]
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    torch.manual_seed(194)
    model = cap.load(mdir)
    assert all(model.config.layer_types[i] == "linear_attention" for i in c196.LAYERS)
    c196.apply(model, cond)
    I = json.loads(Path(items).read_text())
    t0 = time.time()
    rs = {"skipped": "S.pt exists"} if (out / "S.pt").exists() else cap.mode_S(model, I["S"], out, 300)
    for m in [model.model.embed_tokens] + list(model.model.layers):  # drop mode_S's capture hooks (E196 hooks sit on a_proj)
        m._forward_hooks.clear()
    rn = cap.mode_N(model, I["N"], out, 0)
    (out / "meta.json").write_text(json.dumps({"cond": cond, "S": rs, "N": rn, "sec": round(time.time() - t0, 1)}))
    print(json.dumps({"cond": cond, "S": rs, "N": rn}), flush=True)


if __name__ == "__main__":
    main()
