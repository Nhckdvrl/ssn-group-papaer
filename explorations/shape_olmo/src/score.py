"""Per-token NLL on packed windows. usage: score.py MODEL_PATH TAG DOMAINS [REVISION]

Writes scores/<TAG>/<domain>.npy, float32 (S, L-1): nll[s, i] = -log p(ids[s, i+1] | ids[s, :i+1]).
"""
import os, sys, time
import numpy as np
import torch
from transformers import AutoModelForCausalLM

PFX = os.environ.get("SHAPE_PACK", "")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def first_occurrence(x, V):
    """first[v] = first index where token v occurs in x (large if absent)."""
    first = torch.full((V,), 1 << 30, dtype=torch.long, device=x.device)
    return first.scatter_reduce(0, x, torch.arange(len(x), device=x.device), reduce="amin")


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
        ids = np.load(f"{ROOT}/data/pack_{PFX}{dom}.npz")["ids"]
        out = np.zeros((ids.shape[0], ids.shape[1] - 1), np.float32)
        lpin = np.zeros_like(out); lpout = np.zeros_like(out)   # log P(next in / not in prefix token set)
        t0 = time.time()
        for s in range(ids.shape[0]):
            x = torch.from_numpy(ids[s]).long().cuda()[None]
            h = model.model(input_ids=x).last_hidden_state[0, :-1]
            tgt = x[0, 1:]
            first = first_occurrence(x[0], model.lm_head.weight.shape[0])
            for a in range(0, h.shape[0], 2048):            # chunk the vocab projection
                lg = model.lm_head(h[a:a + 2048]).float()
                lse = torch.logsumexp(lg, -1)
                out[s, a:a + 2048] = (lse - lg.gather(-1, tgt[a:a + 2048, None])[:, 0]).cpu().numpy()
                pos = torch.arange(a, a + lg.shape[0], device=lg.device)
                seen = first[None, :] <= pos[:, None]
                lpin[s, a:a + 2048] = (torch.logsumexp(lg.masked_fill(~seen, -1e30), -1) - lse).cpu().numpy()
                lpout[s, a:a + 2048] = (torch.logsumexp(lg.masked_fill(seen, -1e30), -1) - lse).cpu().numpy()
        np.save(out_f, out)
        np.save(out_f.replace(".npy", "_lpin.npy"), lpin); np.save(out_f.replace(".npy", "_lpout.npy"), lpout)
        print(tag, dom, ids.shape, f"{time.time() - t0:.0f}s", "mean nll", out.mean(), flush=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3].split(","), sys.argv[4] if len(sys.argv) > 4 else None)
