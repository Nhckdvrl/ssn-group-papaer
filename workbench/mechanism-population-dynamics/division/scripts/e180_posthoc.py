#!/usr/bin/env python3
"""E180 POST-HOC descriptive summaries (not pre-registered): T vs null Δ per layer, P0 ratios, token-type sets, strata.
Usage: run inside results/e180 (reads summary.json). Output: results/e180/posthoc.txt"""
import json,numpy as np
S=json.load(open('summary.json'))
def runs(ls):
    out=[];cur=[]
    for l in ls:
        if cur and l==cur[-1]+1: cur.append(l)
        else:
            if cur: out.append(cur)
            cur=[l]
    if cur: out.append(cur)
    return ", ".join(f"{a[0]}" if len(a)==1 else f"{a[0]}–{a[-1]}" for a in out) or "∅"
for k,r in S.items():
    L=r['L']; c=r['contrasts']['main']
    T=c['T']
    for f in ('N_A','N_B'):
        above=[l for l in range(L) if T['lo'][l]>c[f]['hi'][l]]
        below=[l for l in range(L) if T['hi'][l]<c[f]['lo'][l]]
        n=[l for l in range(L) if T['delta'][l]>c[f]['draw_max'][l]]
        print(k,f,'T>null CI',len(above),'/',L,'T<null',runs(below),'| T above all 8 draws',len(n), 'below:',runs([l for l in range(L) if T['delta'][l]<c[f]['draw_min'][l]]))
    print(k,'edge/mid T %.4f %.4f NA %.4f %.4f NB %.4f %.4f'%(T['edge_mean'],T['mid_mean'],c['N_A']['edge_mean'],c['N_A']['mid_mean'],c['N_B']['edge_mean'],c['N_B']['mid_mean']))
    fr=np.array(r['floor_ratio_T']); print(k,'floor ratio >1 layers',runs([l for l in range(L) if fr[l]>1]))
    D=r['D']; P0=np.array(D['P0'])[:,0]; P1=np.array(D['P1'])[:,0]; P2=np.array(D['P2n'])[:,0]; H=np.array(D['P2hrv'])[:,0]
    print(k,'P1/P0 min,med',(P1/P0).min().round(2),np.median(P1/P0).round(2),'P2n/P0 min,med',(P2/P0).min().round(2),np.median(P2/P0).round(2),'hrv/P0 med',np.median(H/P0).round(2),'P1/hrv min,med',(P1/H).min().round(2),np.median(P1/H).round(2))
    tt=np.array(r['tokentype']['excess_P1_minus_P2n'])
    for i,nm in enumerate(['T','NA0','NB0']): print(k,'tokentype P1<P2n',nm,runs([l for l in range(L) if tt[l,i]<0]))
    print(k,'tt n',{p:(v['n_occ_per_side'],v['n_types']) for p,v in r['tokentype']['pairs'].items()})
    print(k,'pred share',{a:{b:round(x,2) for b,x in d.items()} for a,d in r['pred_class_share'].items()})
    for cn,st in r['strat'].items():
        if 'vals' in st:
            v=np.array(st['vals']); print(k,cn,st['n'],'T',np.round(v[:,0,0]-v[:,0,1],4),'NA0',np.round(v[:,1,0]-v[:,1,1],4),'NB0',np.round(v[:,2,0]-v[:,2,1],4))
        else: print(k,cn,st)
