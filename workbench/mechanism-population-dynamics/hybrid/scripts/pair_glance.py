import sys, numpy as np
a, b, name = sys.argv[1], sys.argv[2], sys.argv[3]   # a = Transformer npz, b = hybrid npz
A, B = np.load(a), np.load(b)
na, nb = A["base_nll"], B["base_nll"]
print(name, "n tokens", len(na), len(nb), "same kinds", len(na) == len(nb) and bool((A["cls_kind"] == B["cls_kind"]).all()))
if len(na) != len(nb):
    sys.exit()
d = na - nb  # >0: hybrid better
k, r = A["cls_kind"], A["cls_rep"]
print(f"  mean NLL T {na.mean():.3f} H {nb.mean():.3f}  mean d {d.mean():+.4f}  sd {d.std():.3f}  frac hybrid better {np.mean(d>0):.3f}")
for nm, m in [("initial_rep", (k=="initial")&r), ("initial_first", (k=="initial")&~r), ("internal_rep", (k=="internal")&r), ("internal_first", (k=="internal")&~r), ("other", k=="")]:
    print(f"  {nm:15s} n {m.sum():6d} mean d {d[m].mean():+.4f}  share of total d {d[m].sum()/d.sum():+.2f}")
o = np.argsort(-np.abs(d)); top = o[:len(d)//20]
print(f"  top 5% |d| tokens carry {d[top].sum()/d.sum():+.2f} of total d; their mean d {d[top].mean():+.3f}; frac hybrid-better among them {np.mean(d[top]>0):.2f}")
print(f"  corr(d, T nll) {np.corrcoef(d, na)[0,1]:+.3f}  corr(d, min nll) {np.corrcoef(d, np.minimum(na,nb))[0,1]:+.3f}")
