"""Per-token NLL on packed windows. usage: score.py MODEL_PATH TAG DOMAINS [REVISION]

Writes scores/<TAG>/<domain>.npy, float32 (S, L-1): nll[s, i] = -log p(ids[s, i+1] | ids[s, :i+1]).
"""
import os, sys, time
import numpy as np
import torch
from transformers import AutoModelForCausalLM

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@torch.no_grad()
def main(path, tag, domains, rev=None):
    model = AutoModelForCausalLM.from_pretrained(path, revision=rev, dtype=torch.bfloat16,
                                                 device_map="cuda")
    model.eval()
    os.makedirs(f"{ROOT}/scores/{tag}", exist_ok=True)
    for dom in domains:
        out_f = f"{ROOT}/scores/{tag}/{dom}.npy"
        if os.path.exists(out_f):
            continue
        ids = np.load(f"{ROOT}/data/pack_{dom}.npz")["ids"]
        out = np.zeros((ids.shape[0], ids.shape[1] - 1), np.float32)
        t0 = time.time()
        for s in range(ids.shape[0]):
            x = torch.from_numpy(ids[s]).long().cuda()[None]
            h = model.model(input_ids=x).last_hidden_state[0, :-1]
            tgt = x[0, 1:]
            for a in range(0, h.shape[0], 2048):            # chunk the vocab projection
                lg = model.lm_head(h[a:a + 2048]).float()
                out[s, a:a + 2048] = (torch.logsumexp(lg, -1) - lg.gather(-1, tgt[a:a + 2048, None])[:, 0]).cpu().numpy()
        np.save(out_f, out)
        print(tag, dom, ids.shape, f"{time.time() - t0:.0f}s", "mean nll", out.mean(), flush=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3].split(","), sys.argv[4] if len(sys.argv) > 4 else None)
