"""E44 analysis.  usage: analyze_e44.py results/e44/<model>_<task>.npz
margins[set, order, posmode(0 orig, 1 gap), query]; queries 0-19 dev, 20-39 test."""
import json, sys
import numpy as np
from scipy.stats import spearmanr

m = np.load(sys.argv[1])["margins"]
S, O, _, Q = m.shape
dev, test = slice(0, Q // 2), slice(Q // 2, Q)
q = lambda mode, part: m[:, :, mode, part].mean(-1) - m[:, :, mode, part].mean((1, 2))[:, None]   # order quality [S, O]
r = lambda x, y: np.array([spearmanr(x[s], y[s]).correlation for s in range(S)])
out = {"mean_margin": float(m[:, :, 0].mean()), "acc": float((m[:, :, 0] > 0).mean()),
       "order_sd_per_query": float(np.median(m[:, :, 0].std(1))),
       "order_quality_sd_test": float(np.median(q(0, test).std(1)))}
out["transfer_dev_to_test_orig"] = float(np.median(r(q(0, dev), q(0, test))))
out["transfer_dev_to_test_gap"] = float(np.median(r(q(1, dev), q(1, test))))
out["pos_stability_test"] = float(np.median(r(q(0, test), q(1, test))))
out["cross_dev_orig_to_test_gap"] = float(np.median(r(q(0, dev), q(1, test))))
best = q(0, dev).argmax(1); worst = q(0, dev).argmin(1); ix = np.arange(S)
gap_orig = q(0, test)[ix, best] - q(0, test)[ix, worst]
gap_shift = q(1, test)[ix, best] - q(1, test)[ix, worst]
out["best_minus_worst_on_test_orig"] = float(gap_orig.mean())
out["best_minus_worst_on_test_gap"] = float(gap_shift.mean())
out["best_minus_worst_on_dev_orig"] = float((q(0, dev)[ix, best] - q(0, dev)[ix, worst]).mean())
# split-half noise ceiling for order quality within the test half (10 vs 10 queries)
a, b = slice(Q // 2, Q // 2 + Q // 4), slice(Q // 2 + Q // 4, Q)
out["test_splithalf"] = float(np.median(r(q(0, a), q(0, b))))
json.dump(out, open(sys.argv[1].replace(".npz", "_analysis.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
