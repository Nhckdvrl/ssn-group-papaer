"""E55 analysis.  usage: analyze_e55.py results/e55/<model>.npz
Step 1: grouped-CV logistic decoding of annotator name / label from anchor residuals per layer.
Step 2: per head (layers >= L0), regress within-prompt centred log-attention to the 16 anchors on standardized
[same annotator, content similarity (bge), same pole as ... (anchor label), position]; report coefficients."""
import json, sys
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupKFold

z = np.load(sys.argv[1], allow_pickle=True)
R = z["res"].astype(np.float32); M = z["meta"]; layers = z["layers_res"]; L0 = int(z["L0"])
P, n_layers = R.shape[0], R.shape[1]
out = {"decode": {}}
groups = np.repeat(np.arange(P), 16)
for li, l in enumerate(layers):
    X = R[:, li].reshape(P * 16, -1); X = (X - X.mean(0)) / (X.std(0) + 1e-6)
    res = {}
    for name, col in (("annotator_name", 2), ("label", 3)):
        y = M[:, :, col].reshape(-1).astype(int)
        acc = []
        for tr, te in GroupKFold(5).split(X, y, groups):
            clf = LogisticRegression(max_iter=2000, C=0.05).fit(X[tr], y[tr]); acc.append(clf.score(X[te], y[te]))
        res[name] = round(float(np.mean(acc)), 3)
    out["decode"][int(l)] = res
    print("layer", l, res, flush=True)
A = z["att"].astype(np.float32)                    # [N, L-L0, H, 16]
idx = z["sim_idx"]; S = z["sim"]                    # idx: (pair, who, q)
N, nl, H, _ = A.shape
same = np.stack([(M[p, :, 1] == w).astype(float) for p, w, q in idx])          # anchor role == query role
lab = np.stack([M[p, :, 3].astype(float) for p, w, q in idx])
pos = np.tile(np.arange(16) / 15.0, (N, 1))
cen = lambda x: x - x.mean(1, keepdims=True)
F = np.stack([cen(same), cen(S), cen(lab), cen(pos)], -1).reshape(-1, 4)
F = F / (F.std(0) + 1e-9)
coef = np.zeros((nl, H, 4)); r2 = np.zeros((nl, H))
for li in range(nl):
    for h in range(H):
        y = cen(A[:, li, h, :]).reshape(-1)
        b, *_ = np.linalg.lstsq(F, y, rcond=None); coef[li, h] = b
        r2[li, h] = 1 - ((y - F @ b) ** 2).sum() / (y ** 2).sum()
# focus: heads with the strongest content selectivity (retrieval heads) and E48 heads
top = np.argsort(-coef[..., 1].ravel())[:20]
out["top20_by_content"] = [{"head": f"{L0 + k // H}.{k % H}", "same_annotator": round(float(coef.reshape(-1, 4)[k, 0]), 3),
                            "content_sim": round(float(coef.reshape(-1, 4)[k, 1]), 3), "label": round(float(coef.reshape(-1, 4)[k, 2]), 3),
                            "position": round(float(coef.reshape(-1, 4)[k, 3]), 3), "r2": round(float(r2.ravel()[k]), 3)} for k in top]
e48 = ["34.2", "32.3", "32.5", "30.27", "33.29", "34.1", "33.16", "30.9", "32.7", "34.3"]
out["e48_heads"] = {hd: {"same_annotator": round(float(coef[int(hd.split('.')[0]) - L0, int(hd.split('.')[1]), 0]), 3),
                         "content_sim": round(float(coef[int(hd.split('.')[0]) - L0, int(hd.split('.')[1]), 1]), 3)} for hd in e48}
ratio = coef[..., 0].ravel()[top] / np.maximum(coef[..., 1].ravel()[top], 1e-6)
out["median_same_over_content_top20"] = float(np.median(ratio))
json.dump(out, open(sys.argv[1].replace(".npz", "_analysis.json"), "w"), indent=1)
print(json.dumps({k: v for k, v in out.items() if k != "decode"}, indent=1))
