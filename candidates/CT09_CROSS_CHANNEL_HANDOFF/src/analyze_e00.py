"""E00 readout: Δ per condition, H with item bootstrap, gates from docs/E00_PROTOCOL.md."""
import glob, json, sys
import numpy as np

rows = [json.loads(l) for f in sorted(glob.glob(sys.argv[1] + "/s*.jsonl")) for l in open(f)]
conds = list(rows[0]["lp"])


def delta(r, c):
    lp = r["lp"][c]
    return 0.5 * ((lp["AA"] - lp["AB"]) - (lp["BA"] - lp["BB"]))


def acc(r, c):
    lp = r["lp"][c]
    return float(lp["AA"] > lp["AB"] and lp["BB"] > lp["BA"])


D = {c: np.array([delta(r, c) for r in rows]) for c in conds}
A = {c: np.mean([acc(r, c) for r in rows]) for c in conds}
n = len(rows)
rng = np.random.default_rng(0)
B = rng.integers(0, n, (10000, n))


def ratio(num, den, base=None):
    b = np.zeros(n) if base is None else D[base]
    f = lambda idx: (D[num][idx] - b[idx]).mean() / (D[den][idx] - b[idx]).mean()
    est = f(np.arange(n))
    bs = np.array([f(i) for i in B])
    return est, np.percentile(bs, 2.5), np.percentile(bs, 97.5)


print(f"items {n}")
print(f"{'cond':12s} {'mean Δ':>8s} {'95% CI':>18s} {'acc':>6s}")
for c in conds:
    bs = D[c][B].mean(1)
    print(f"{c:12s} {D[c].mean():8.3f} [{np.percentile(bs, 2.5):7.3f},{np.percentile(bs, 97.5):7.3f}] {A[c]:6.3f}")
print("PRE max |Δ|", np.abs(D["PRE"]).max())
H = ratio("POST", "FULL_SWAP", "NOREAD")
print("H (primary)            %.4f [%.4f, %.4f]" % H)
print("H_nat POST_NAT/FULL_NAT %.4f [%.4f, %.4f]" % ratio("POST_NAT", "FULL_NAT"))
print("RECENT/FULL_SWAP        %.4f [%.4f, %.4f]" % ratio("RECENT", "FULL_SWAP"))
print("POST/RECENT             %.4f [%.4f, %.4f]" % ratio("POST", "RECENT"))
print("early E_POST/E_FULL_SWAP %.4f [%.4f, %.4f]" % ratio("E_POST", "E_FULL_SWAP"))
print("RECONLY/FULL_NAT        %.4f [%.4f, %.4f]" % ratio("RECONLY", "FULL_NAT"))
ti = np.array([r["target_index"] for r in rows])
for lo, hi in ((0, 13), (13, 26), (26, 40)):
    s = (ti >= lo) & (ti < hi)
    h = (D["POST"][s] - D["NOREAD"][s]).mean() / (D["FULL_SWAP"][s] - D["NOREAD"][s]).mean()
    print(f"target index [{lo},{hi}) n={s.sum()} H={h:.4f}")
v1 = D["FULL_SWAP"].mean() >= 5 and A["FULL_SWAP"] >= 0.9
v2 = ratio("RECENT", "FULL_SWAP")[0] >= 0.3
v3 = np.abs(D["PRE"]).max() == 0
print(f"validity: FULL_SWAP {v1}  RECENT readable {v2}  PRE exact-zero {v3}")
if not (v1 and v2):
    print("VERDICT: KILL (instrument invalid)")
else:
    print("VERDICT:", "PASS" if H[0] >= 0.20 and H[1] >= 0.10 else "KILL")
