"""E48 analysis: own vs other-annotator anchor contributions and attention, mixed vs mixed_far."""
import json, sys
import numpy as np
z = np.load(sys.argv[1]); C = z["contrib"]; A = z["att"]; cond = z["cond"]; who = z["who"]; pair = z["pair"]
s_own = np.where(who == 0, 1.0, -1.0); s_oth = -s_own          # A toxic-leaning (+), B safe-leaning (-)
tot = C.sum((1, 2))                                             # [N, 3] own / other / rest
out = {}
P = np.unique(pair); rng = np.random.default_rng(0); B = [rng.choice(P, len(P)) for _ in range(1000)]
# top heads by |other| contribution in the mixed condition
m = cond == "mixed"
oth_head = np.abs((C[m][..., 1] * s_oth[m][:, None, None]).mean(0))
top = np.argsort(-oth_head.ravel())[:10]
for c in ("mixed", "mixed_far"):
    k = cond == c
    own = tot[k, 0] * s_own[k]; oth = tot[k, 1] * s_oth[k]
    pm = lambda x: np.array([x[pair[k] == p].mean() for p in P])
    po, pt = pm(own), pm(oth)
    att_oth = A[k][..., 1].reshape(k.sum(), -1)[:, top].mean(); att_own = A[k][..., 0].reshape(k.sum(), -1)[:, top].mean()
    out[c] = {"own_signed": float(po.mean()), "other_signed": float(pt.mean()),
              "other_signed_ci": np.percentile([np.mean([pt[np.where(P == b)[0][0]] for b in bb]) for bb in B], [2.5, 97.5]).round(3).tolist(),
              "other_over_own": float(pt.mean() / po.mean()),
              "att_top10_other": float(att_oth), "att_top10_own": float(att_own),
              "ld_A_minus_B": float(z["ld"][k & (who == 0)].mean() - z["ld"][k & (who == 1)].mean())}
out["attention_ratio_far_over_mixed_other"] = out["mixed_far"]["att_top10_other"] / out["mixed"]["att_top10_other"]
out["top10_heads_by_other"] = [f"{int(i) // C.shape[2]}.{int(i) % C.shape[2]}" for i in top]
json.dump(out, open(sys.argv[1].replace(".npz", "_analysis.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
