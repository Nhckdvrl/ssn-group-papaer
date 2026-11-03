"""[Review 2026-11-03, CPU-only, reads local captures] CPU check for the resolution hierarchy: evaluate token-level damage correspondence under the matching obtained
from the coarse routing fingerprint (strong signal), for init-only and order-only pairs; and relate per-expert
token-level correspondence to expert properties (importance, category specificity, top category)."""
import numpy as np, json, sys
from pathlib import Path
from scipy.optimize import linear_sum_assignment
AN = Path.home()/"mechpop_cache/e167_analysis"
UPOS = ["ADJ","ADP","ADV","AUX","CCONJ","DET","INTJ","NOUN","NUM","PART","PRON","PROPN","PUNCT","SCONJ","SYM","VERB","X"]
CATS = [f"{u}:{p}" for u in UPOS for p in ("init","cont")] + ["NONE"]
tok="3999793152"; MIN_TOK=300
def rowcorr(X,Y):
    X=X-X.mean(1,keepdims=True); Y=Y-Y.mean(1,keepdims=True)
    return (X*Y).sum(1)/np.sqrt((X*X).sum(1)*(Y*Y).sum(1)+1e-30)
def cm(X,Y):
    X=X-X.mean(1,keepdims=True); Y=Y-Y.mean(1,keepdims=True)
    X=X/(np.linalg.norm(X,axis=1,keepdims=True)+1e-12); Y=Y/(np.linalg.norm(Y,axis=1,keepdims=True)+1e-12)
    return X@Y.T
def load_fun(r):
    z=np.load(AN/"functional"/f"{r}__ckpt_{tok}.npz")
    keep=(z["cat_counts"]>=MIN_TOK).all(0)
    route=np.transpose(z["route_fp"],(0,1,3,2))[...,keep]  # L,split,E,nc
    drop=z["drop_fp"][...,keep]  # L,E,2,nc
    return dict(route_cal=route[:,1], route_held=route[:,0], drop_cal=drop[:,:,1], drop_held=drop[:,:,0], drop_total=z["drop_total"], route_full=np.transpose(z["route_fp"],(0,1,3,2)), keep=keep)
def load_tok(r): return np.load(AN/"token_roles"/f"{r}__ckpt_{tok}.npz")
pairs=[("I0D0","I1D0","init"),("I0D0","I2D0","init"),("I2D0","I3D0","init"),("I1D0","I3D0","init"),("I0D0","I0D1","order"),("I1D0","I1D1","order")]
runs=sorted({a for p in pairs for a in p[:2]})
FUN={r:load_fun(r) for r in runs}; TOK={r:load_tok(r) for r in runs}
layers=[6,7,8,9,10,11]
rng=np.random.default_rng(0)
print("Token-level damage correspondence (eval = windows 64..127) under three matchings: own token-level (fit on windows 0..63), route-fingerprint (cal split), drop-fingerprint (cal split)")
print("pair kind L | own route drop | random95hi | frac of experts with r>.2 under route-matching")
summ={}
for a,b,kind in pairs:
    for l in layers:
        DA=TOK[a][f"D{l}"].astype(np.float32); DB=TOK[b][f"D{l}"].astype(np.float32); E,W,T=DA.shape
        h1=np.arange(W)<W//2; h2=~h1
        Cf=cm(DA[:,h1].reshape(E,-1),DB[:,h1].reshape(E,-1)); Ce=cm(DA[:,h2].reshape(E,-1),DB[:,h2].reshape(E,-1))
        ri,ci=linear_sum_assignment(-Cf); own=Ce[ri,ci].mean()
        def centre(F): return F-F.mean(0,keepdims=True)
        Rc=np.array([rowcorr(np.repeat(centre(FUN[a]["route_cal"][l])[k:k+1],E,0),centre(FUN[b]["route_cal"][l])) for k in range(E)])
        r2,c2=linear_sum_assignment(-Rc); route=Ce[r2,c2].mean()
        Dc=np.array([rowcorr(np.repeat(centre(FUN[a]["drop_cal"][l])[k:k+1],E,0),centre(FUN[b]["drop_cal"][l])) for k in range(E)])
        r3,c3=linear_sum_assignment(-Dc); drop=Ce[r3,c3].mean()
        rand=[Ce[np.arange(E),rng.permutation(E)].mean() for _ in range(200)]
        agree_rd = float((c2==c3).mean()); agree_ro=float((c2==ci).mean())
        summ.setdefault((kind,l),[]).append((own,route,drop))
        print(f"{a}:{b} {kind:5s} L{l:2d} | {own:.3f} {route:.3f} {drop:.3f} | {np.percentile(rand,97.5):.3f} | {(Ce[r2,c2]>.2).mean():.2f} | match agreement route-vs-drop {agree_rd:.2f}, route-vs-own {agree_ro:.2f}")
print("\nratios init/order of mean token-level corr (deep L6-11) under: own / route / drop matching")
for l in layers:
    I=np.mean(summ[("init",l)],0); O=np.mean(summ[("order",l)],0)
    print(f"L{l:2d} own {I[0]/O[0]:.2f}  route {I[1]/O[1]:.2f}  drop {I[2]/O[2]:.2f}   (init {I.round(3)}, order {O.round(3)})")

print("\n== Which experts correspond at token level? (init pairs, route matching, L9/L11) ==")
keep=FUN["I0D0"]["keep"]; cats=[c for c,k in zip(CATS,keep) if k]
for a,b,kind in pairs:
    if kind!="init": continue
    for l in (9,11):
        DA=TOK[a][f"D{l}"].astype(np.float32); DB=TOK[b][f"D{l}"].astype(np.float32); E,W,T=DA.shape
        Ce=cm(DA.reshape(E,-1),DB.reshape(E,-1))
        def centre(F): return F-F.mean(0,keepdims=True)
        Rc=np.array([rowcorr(np.repeat(centre(FUN[a]["route_cal"][l])[k:k+1],E,0),centre(FUN[b]["route_cal"][l])) for k in range(E)])
        r2,c2=linear_sum_assignment(-Rc); pu=Ce[r2,c2]
        imp=FUN[a]["drop_total"][l]  # mean dNLL when dropped
        P=FUN[a]["route_cal"][l]  # E x nc : P(expert|cat)
        Pn=P/np.maximum(P.sum(1,keepdims=True),1e-12)   # distribution over categories for expert e (unnormalised by cat prior)
        ent=-(Pn*np.log(Pn+1e-12)).sum(1); spec=P.max(1)  # max P(e|cat)
        top=[cats[k] for k in P.argmax(1)]
        # sparsity of token-level damage: fraction of tokens with |d|>.01
        sp=(np.abs(DA.reshape(E,-1))>0.01).mean(1)
        order=np.argsort(-pu)
        print(f"\n{a}:{b} L{l}: corr(pu, importance)={np.corrcoef(pu,imp)[0,1]:.2f}  corr(pu, maxP(e|cat))={np.corrcoef(pu,spec)[0,1]:.2f}  corr(pu, -entropy)={np.corrcoef(pu,-ent)[0,1]:.2f}  corr(pu, damage-sparsity)={np.corrcoef(pu,sp)[0,1]:.2f}")
        print("  top-8 corresponding experts: (e, r, topcat, maxP, imp)")
        for k in order[:8]: print(f"    e{k:2d} r={pu[k]:.2f} {top[k]:12s} maxP={spec[k]:.2f} imp={imp[k]:.4f}")
        print("  bottom-5:")
        for k in order[-5:]: print(f"    e{k:2d} r={pu[k]:.2f} {top[k]:12s} maxP={spec[k]:.2f} imp={imp[k]:.4f}")
        # by top-category group
        groups={}
        for k in range(E): groups.setdefault(top[k].split(":")[0],[]).append(pu[k])
        print("  mean r by expert top UPOS:", {g:(round(float(np.mean(v)),2),len(v)) for g,v in sorted(groups.items(), key=lambda kv:-np.mean(kv[1]))})
