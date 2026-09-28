"""What does each architecture use from far context? (Khandelwal et al. 2018 style, fixed boundary.)

For each 2k NeoX window x, targets are positions [T0, 2048) with T0 = 1920. For distance d, the far
region R = x[0 : T0 - d] is perturbed and the near region x[T0 - d:] is kept, so every target keeps
>= d tokens of intact local context.
  full    : unchanged
  drop    : input = x[T0 - d:]                      (far context removed)
  cshuf   : 32-token chunks of R permuted           (local phrases kept, discourse order destroyed)
  tshuf   : tokens of R permuted                    (content kept as a bag, all order destroyed)
Output: results/ctx/<TAG>.npz with nll[cond][d] of shape (W, 128) and the window's domain / rep tags.

usage: SHAPE_PACK=neox2k_ ctx_ablation.py {hf|ssm} MODEL TAG [REVISION]
"""
import os, sys
import numpy as np
import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from score_any import load

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PFX = os.environ.get("SHAPE_PACK", "neox2k_")
DOMS = ["pg19", "wikipedia", "python"]
NWIN = int(os.environ.get("CTX_NWIN", 200))
T0, L = 1920, 2048
DS = [32, 128, 512, 1024]
V = int(os.environ.get("SHAPE_V", 50277))


@torch.no_grad()
def nll_targets(model, ids):
    x = torch.tensor(ids, device="cuda")[None]
    lg = model(x).logits[0, :-1, :V].float()
    n = len(ids)
    tgt = x[0, 1:]
    lp = torch.log_softmax(lg[n - 1 - (L - T0):], -1)          # predictions for the last 128 targets
    return -lp.gather(-1, tgt[n - 1 - (L - T0):, None])[:, 0].cpu().numpy()


def main(kind, path, tag, rev=None):
    model = load(kind, path, rev)
    out = {f"{c}_{d}": [] for c in ("drop", "cshuf", "tshuf") for d in DS}
    out["full"] = []; dom = []; rep = []
    for di, d_name in enumerate(DOMS):
        ids_all = np.load(f"{ROOT}/data/pack_{PFX}{d_name}.npz")["ids"][:NWIN]
        reps = np.load(f"{ROOT}/data/tags_{PFX}{d_name}.npz")["rep"][:NWIN, T0 - 1:L - 1]
        for w, x in enumerate(ids_all):
            rng = np.random.default_rng(1000 * di + w)
            x = x.tolist()
            out["full"].append(nll_targets(model, x))
            for d in DS:
                cut = T0 - d
                R, near = x[:cut], x[cut:]
                out[f"drop_{d}"].append(nll_targets(model, near))
                ch = [R[i:i + 32] for i in range(0, len(R), 32)]
                perm = rng.permutation(len(ch))
                out[f"cshuf_{d}"].append(nll_targets(model, [t for j in perm for t in ch[j]] + near))
                out[f"tshuf_{d}"].append(nll_targets(model, list(rng.permutation(R)) + near))
            dom.append(di); rep.append(reps[w])
        print(tag, d_name, "done", flush=True)
    os.makedirs(f"{ROOT}/results/ctx", exist_ok=True)
    np.savez(f"{ROOT}/results/ctx/{tag}.npz", dom=np.array(dom), rep=np.array(rep),
             **{k: np.array(v, np.float32) for k, v in out.items()})


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else None)
