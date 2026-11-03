"""[Review 2026-11-03, CPU-only, reads local captures] CPU check: how much of within-type routing agreement C is explained by the N1 null B and by raw geometry Kh,
within one model; and verify T_ctx / T_D for a few pairs. Reads the local routing captures only."""
import numpy as np, sys
from pathlib import Path
CAP = Path.home()/"mechpop_cache/e167_analysis/routing"
P = np.load(CAP/"pairs.npz"); i,j,t = P["i"],P["j"],P["type"]; nT=int(t.max())+1
def cw(x):
    s=np.bincount(t,x,nT); c=np.bincount(t,None,nT); return x-(s/np.maximum(c,1))[t]
def corr(a,b): return float((a*b).sum()/np.sqrt((a*a).sum()*(b*b).sum()))
tok = sys.argv[1] if len(sys.argv)>1 else "3999793152"
runs = ["I0D0","I1D0","I0D1"]
Z = {r: np.load(CAP/f"{r}__ckpt_{tok}.npz") for r in runs}
print(f"tokens={tok}; word pairs={len(i)}; types={nT}")
print("layer | within-model I0D0: corr(C,B) corr(C,Kh) corr(B,Kh) sd(C) sd(B) sd(D) R2(C~B) | T_ctx T_D (I0D0,I1D0) | T_ctx T_D (I0D0,I0D1) | corr(D_A, Kh_A)")
for l in range(12):
    A = Z["I0D0"]; C=cw(A[f"C{l}"].astype(float)); B=cw(A[f"B{l}"].astype(float)); K=cw(A[f"Kh{l}"].astype(float)); D=C-B
    # pairs
    out=[]
    for other in ("I1D0","I0D1"):
        O=Z[other]; Co=cw(O[f"C{l}"].astype(float)); Do=Co-cw(O[f"B{l}"].astype(float))
        out += [corr(C,Co), corr(D,Do)]
    # OLS slope R2 of C on B
    b = (C*B).sum()/(B*B).sum(); R2 = 1-((C-b*B)**2).sum()/(C*C).sum()
    print(f"L{l:2d} | {corr(C,B):.3f} {corr(C,K):.3f} {corr(B,K):.3f} {C.std():.3f} {B.std():.3f} {D.std():.3f} {R2:.3f} | {out[0]:.3f} {out[1]:.3f} | {out[2]:.3f} {out[3]:.3f} | {corr(D,K):.3f}")
# also: cross-model agreement of the null itself (B_A vs B_B): is the null expectation reproducible?
print("\ncross-model corr of null expectation B (within-type centred): (I0D0,I1D0) / (I0D0,I0D1)")
for l in range(12):
    BA=cw(Z["I0D0"][f"B{l}"].astype(float)); BB=cw(Z["I1D0"][f"B{l}"].astype(float)); BC=cw(Z["I0D1"][f"B{l}"].astype(float))
    print(f"L{l:2d} {corr(BA,BB):.3f} / {corr(BA,BC):.3f}")
