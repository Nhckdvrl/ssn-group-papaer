"""E45 analysis.  usage: analyze_e45.py results/e45/<model>_<task>.npz"""
import json, sys
import numpy as np
from scipy.stats import spearmanr

z = np.load(sys.argv[1]); M = z["margins"]; SL = z["stream_lp"]; OL = z["orig_lp"]; seqs = list(z["seqs"])
S = M.shape[0]
q = M.mean(-1)                                   # [S, 8 seq, 4 place]
q = q - q.mean((1, 2), keepdims=True)
seq_eff = q.mean(2, keepdims=True); place_eff = q.mean(1, keepdims=True)
inter = q - seq_eff - place_eff
# reliability-corrected: split queries in halves to estimate noise in cell means
h1 = M[..., ::2].mean(-1); h2 = M[..., 1::2].mean(-1)
noise_var = float(((h1 - h2) ** 2).mean() / 4)          # variance of the full-mean cell due to query sampling
out = {"var_seq": float((seq_eff ** 2).mean()), "var_place": float((place_eff ** 2).mean()),
       "var_inter": float((inter ** 2).mean()), "noise_var_cell": noise_var,
       "seq_quality": {sq: round(float(seq_eff[:, i].mean()), 3) for i, sq in enumerate(seqs)},
       "seq_stream_lp": {sq: round(float(SL[:, i].mean()), 3) for i, sq in enumerate(seqs)},
       "seq_orig_lp": {sq: round(float(SL[:, i].mean() * 0 + OL[:, i].mean()), 3) for i, sq in enumerate(seqs)}}
sq_q = np.array([seq_eff[:, i].mean() for i in range(8)]); sq_s = np.array([SL[:, i].mean() for i in range(8)])
out["rho_seqquality_vs_streamlp_across8"] = float(spearmanr(sq_q, sq_s).correlation)
# within-set, across all 32 orders: quality vs stream predictability
qs = q.reshape(S, -1); ss = (SL - SL.mean((1, 2), keepdims=True)).reshape(S, -1); os_ = (OL - OL.mean((1, 2), keepdims=True)).reshape(S, -1)
out["r_quality_streamlp_within"] = float(np.corrcoef(qs.ravel(), ss.ravel())[0, 1])
out["r_quality_origlp_within"] = float(np.corrcoef(qs.ravel(), os_.ravel())[0, 1])
# placement only (within the same label sequence): does stream lp vary and predict?
qp = (q - seq_eff).reshape(S, -1); sp = (SL - SL.mean(2, keepdims=True)).reshape(S, -1); op = (OL - OL.mean(2, keepdims=True)).reshape(S, -1)
out["r_quality_origlp_within_seq"] = float(np.corrcoef(qp.ravel(), op.ravel())[0, 1])
json.dump(out, open(sys.argv[1].replace(".npz", "_analysis.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
