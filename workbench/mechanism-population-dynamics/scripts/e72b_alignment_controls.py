"""E72b (controls for E72): is cross-initialization alignment of head-role profiles more than a few generic
attention axes? (1) effective dimensionality of the nine-role profile within a layer; (2) held-out agreement after
aligning on k = 1, 2, 4, 8 randomly chosen roles; (3) aligning on the weight-only OV copying score alone.
Different-initialization 1B pairs (all corpora). Writes results/e72b.json."""
import itertools
import json

import numpy as np
from scipy.optimize import linear_sum_assignment
from scipy.stats import spearmanr

import mp_common as mc
from e70_72_reuse import ROLES, load_1b, zrows


def main(n_pairs=200, seed=0):
    rng = np.random.default_rng(seed)
    D = load_1b()
    keys = sorted(k for k in D if all(r in D[k] for r in ROLES))
    Z = {k: np.stack([zrows(D[k][r]) for r in ROLES]) for k in keys}  # roles x L x H
    nR, L, H = Z[keys[0]].shape
    # (1) dimensionality: eigenvalues of the role-by-role correlation across heads, per layer and model
    ev = []
    for k in keys:
        for l in range(L):
            C = np.nan_to_num(np.corrcoef(Z[k][:, l, :]))
            w = np.sort(np.linalg.eigvalsh(C))[::-1]
            ev.append(w / w.sum())
    ev = np.mean(ev, 0)
    out = {"eigen_share": ev.round(3).tolist(), "participation_ratio": float(1 / (ev ** 2).sum())}
    print("eigen share", ev.round(3), "PR", round(out["participation_ratio"], 2), flush=True)
    pairs = [(a, b) for a, b in itertools.combinations(keys, 2) if a[0] != b[0] and a[1] != b[1]]
    pairs = [pairs[i] for i in rng.choice(len(pairs), min(n_pairs, len(pairs)), replace=False)]

    def aligned(a, b, feats, target):
        vals = []
        for l in range(L):
            A, B = Z[a][:, l, :], Z[b][:, l, :]
            C = np.nan_to_num(np.corrcoef(A[feats].T, B[feats].T)[:H, H:]) if len(feats) > 1 else \
                -np.abs(A[feats[0]][:, None] - B[feats[0]][None, :])
            _, perm = linear_sum_assignment(-C)
            vals.append(np.mean([spearmanr(A[t], B[t][perm])[0] for t in target]))
        return float(np.nanmean(vals))
    # (2) number of alignment roles
    curve = {}
    for k in (1, 2, 4, 8):
        v = []
        for a, b in pairs[:100]:
            ho = int(rng.integers(nR))
            others = [j for j in range(nR) if j != ho]
            feats = sorted(rng.choice(others, k, replace=False).tolist())
            v.append(aligned(a, b, feats, [ho]))
        curve[k] = float(np.mean(v))
        print("align on", k, "roles -> held-out", round(curve[k], 3), flush=True)
    out["held_out_by_n_alignment_roles"] = curve
    # (3) the weight-only OV copying score alone predicts the attention roles?
    ov = ROLES.index("R5")
    att = [j for j in range(nR) if j != ov]
    out["align_on_ov_predict_attention"] = float(np.mean([aligned(a, b, [ov], att) for a, b in pairs[:100]]))
    out["align_on_attention_predict_ov"] = float(np.mean([aligned(a, b, att, [ov]) for a, b in pairs[:100]]))
    print({k: round(v, 3) for k, v in out.items() if k.startswith("align")}, flush=True)
    (mc.RESULTS / "e72b.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
