"""CPU pilot scorer (small Pile-family HF models). Same outputs as score_any, first N windows per domain.
usage: SHAPE_PACK=neox2k_ score_cpu.py REPO TAG DOMAINS N [REVISION]"""
import os, sys, time
import numpy as np, torch
from transformers import AutoModelForCausalLM
torch.set_num_threads(int(os.environ.get("THREADS", 12)))
PFX = os.environ.get("SHAPE_PACK", "")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V = 50277

@torch.no_grad()
def main(repo, tag, doms, n, rev=None):
    m = AutoModelForCausalLM.from_pretrained(repo, revision=rev, dtype=torch.float32).eval()
    os.makedirs(f"{ROOT}/scores/{tag}", exist_ok=True)
    for d in doms:
        f = f"{ROOT}/scores/{tag}/{d}.npy"
        if os.path.exists(f.replace(".npy", "_lpin.npy")):
            continue
        ids = np.load(f"{ROOT}/data/pack_{PFX}{d}.npz")["ids"][:n]
        out = np.zeros((ids.shape[0], ids.shape[1] - 1), np.float32); lpin = np.zeros_like(out); lpout = np.zeros_like(out)
        t0 = time.time()
        for s in range(ids.shape[0]):
            x = torch.from_numpy(ids[s]).long()[None]
            lg = m(x).logits[0, :-1, :V].float(); lse = torch.logsumexp(lg, -1)
            out[s] = (lse - lg.gather(-1, x[0, 1:, None])[:, 0]).numpy()
            first = torch.full((V,), 1 << 30, dtype=torch.long).scatter_reduce(0, x[0], torch.arange(x.shape[1]), reduce="amin")
            seen = first[None, :] <= torch.arange(lg.shape[0])[:, None]
            lpin[s] = (torch.logsumexp(lg.masked_fill(~seen, -1e30), -1) - lse).numpy()
            lpout[s] = (torch.logsumexp(lg.masked_fill(seen, -1e30), -1) - lse).numpy()
        np.save(f, out); np.save(f.replace(".npy", "_lpin.npy"), lpin); np.save(f.replace(".npy", "_lpout.npy"), lpout)
        print(tag, d, ids.shape, f"{time.time()-t0:.0f}s mean nll {out.mean():.4f}", flush=True)

if __name__ == "__main__":
    a = sys.argv[1:]; main(a[0], a[1], a[2].split(","), int(a[3]), a[4] if len(a) > 4 else None)
