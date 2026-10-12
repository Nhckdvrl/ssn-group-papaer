"""E42 analysis: order SD under A (full reorder), B (causal order only), C (RoPE positions only); additivity."""
import sys, json, collections
import numpy as np
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
tag = sys.argv[1]
z = np.load(ROOT / f"results/e42/{tag}.npz"); LD = dict(zip(z["uid"], z["ld"]))
ref = np.load(ROOT / f"results/kernel_perm/{tag}.npz"); R = dict(zip(ref["uid"], ref["ld"]))
bases = sorted({u.split("|")[0] for u in LD})
O = np.array([LD[f"{b}|O"] for b in bases])
chk = np.array([LD[f"{b}|O"] - R[f"{b}|perm0"] for b in bases])
dev = {c: np.array([[LD[f"{b}|{c}|perm{k}"] - LD[f"{b}|O"] for k in range(1, 8)] for b in bases]) for c in "ABC"}
Aold = np.array([[R[f"{b}|perm{k}"] - R[f"{b}|perm0"] for k in range(1, 8)] for b in bases])
sd = {c: float(np.median(np.sqrt((dev[c] ** 2).mean(1)))) for c in "ABC"}
out = {"check_O_vs_E40": float(np.abs(chk).max()), "check_A_vs_E40": float(np.abs(dev["A"] - Aold).max()),
       "rms_dev_median": sd,
       "r(A, B)": float(np.corrcoef(dev["A"].ravel(), dev["B"].ravel())[0, 1]),
       "r(A, C)": float(np.corrcoef(dev["A"].ravel(), dev["C"].ravel())[0, 1]),
       "r(A, B+C)": float(np.corrcoef(dev["A"].ravel(), (dev["B"] + dev["C"]).ravel())[0, 1]),
       "var_share": {c: float((dev[c] ** 2).mean() / (dev["A"] ** 2).mean()) for c in "BC"}}
(ROOT / f"results/e42/{tag}_analysis.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
