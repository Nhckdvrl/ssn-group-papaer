"""E36 analysis on E30 prompts (ctxeffect).  usage: mech_analyze.py MODEL [--top 20]
Per head (signed DLA, logit units):
  sam   = inter - same on Sam queries, toward the B-mapping answer
  alex  = inter - same on Alex queries, toward the B-mapping answer   (leakage)
  main  = [main - same](Sam - Alex), toward the main-effect label L
Attention keys of top heads: share of answer->label attention on same-class vs other-class demos, same- vs
other-annotator demos, and correlation with demo position."""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def load(model, data="ctxeffect"):
    z = np.load(ROOT / f"results/mech/{model}_{data}.npz")
    meta = {}
    for l in open(ROOT / f"data/{data}/rows.jsonl"):
        r = json.loads(l); meta[r["uid"]] = r
    return z, meta


def main():
    model = sys.argv[1]; top = int(sys.argv[sys.argv.index("--top") + 1]) if "--top" in sys.argv else 20
    z, meta = load(model)
    uids = list(z["uid"]); dla = z["dla_head"]; mlp = z["dla_mlp"]; att = z["att_lab"]
    L, H = dla.shape[1:]
    idx = {u: i for i, u in enumerate(uids)}
    recs = []
    for u in uids:
        r = meta[u]; task, cond = r["cond"].split(":")
        recs.append(dict(uid=u, task=task, cond=cond, base=r["base_id"], qa=r["qann"], qc=r["qclass"], qA=r["qA"], L=r["L"]))
    M = pd.DataFrame(recs)
    # demo classes from the 'same' condition: labels = c ^ s, s = qA ^ qclass
    cls = {}
    for _, g in M[M.cond == "same"].groupby("base"):
        r0 = meta[g.uid.iloc[0]]; s = r0["qA"] ^ r0["qclass"]; cls[g.base.iloc[0]] = np.array(r0["labels"]) ^ s
    for task, T in M.groupby("task"):
        print(f"\n===== {model} / {task}  (prompts {len(T)})")
        key = lambda c, a: T[(T.cond == c) & (T.qa == a)].set_index(["base", "qc"])
        def comp(c1, c2, a, signcol):
            x, y = key(c1, a), key(c2, a)
            common = x.index.intersection(y.index)
            sg = np.where(signcol(x.loc[common]) == 1, 1.0, -1.0)
            d = np.stack([dla[idx[u]] for u in x.loc[common].uid]) - np.stack([dla[idx[u]] for u in y.loc[common].uid])
            m = np.stack([mlp[idx[u]] for u in x.loc[common].uid]) - np.stack([mlp[idx[u]] for u in y.loc[common].uid])
            return (d * sg[:, None, None]).mean(0), (m * sg[:, None]).mean(0)
        towardB = lambda X: 1 - X.qA.values
        towardL = lambda X: X.L.values
        sam, sam_m = comp("inter", "same", 1, towardB)
        alex, alex_m = comp("inter", "same", 0, towardB)
        ms, ms_m = comp("main", "same", 1, towardL); ma, ma_m = comp("main", "same", 0, towardL)
        main, main_m = ms - ma, ms_m - ma_m
        print(f"  totals (heads + MLP): Sam {sam.sum() + sam_m.sum():+.2f} (heads {sam.sum():+.2f})   Alex spill {alex.sum() + alex_m.sum():+.2f} "
              f"(heads {alex.sum():+.2f})   main {main.sum() + main_m.sum():+.2f} (heads {main.sum():+.2f})")
        flat = lambda A: A.reshape(-1)
        order_map = np.argsort(-flat(sam))[:top]; order_pri = np.argsort(-flat(main))[:top]
        ov = len(set(order_map) & set(order_pri))
        print(f"  top-{top} mapping heads carry {flat(sam)[order_map].sum() / sam.sum():.0%} of head Sam shift; their Alex spill / Sam shift "
              f"= {flat(alex)[order_map].sum() / flat(sam)[order_map].sum():.2f}")
        print(f"  same top-{top} mapping heads: main-effect Alex/Sam ratio = {flat(ma)[order_map].sum() / flat(ms)[order_map].sum():.2f};"
              f" all heads: inter {alex.sum() / sam.sum():.2f}, main {ma.sum() / ms.sum():.2f}; MLP: inter {alex_m.sum():+.2f}/{sam_m.sum():+.2f}, main {ma_m.sum():+.2f}/{ms_m.sum():+.2f}")
        print(f"  top-{top} prior heads carry {flat(main)[order_pri].sum() / main.sum():.0%} of head main effect; overlap with mapping heads: {ov}/{top}")
        # attention keys
        TT = T[T.cond == "same"]
        A = np.stack([att[idx[u]] for u in TT.uid])                      # [n, L, H, 16]
        A = A / np.clip(A.sum(-1, keepdims=True), 1e-9, None)
        same_cls = np.stack([(cls[b] == qc).astype(float) for b, qc in zip(TT.base, TT.qc)])
        ann = np.stack([np.array(meta[u]["ann"]) for u in TT.uid]); same_ann = (ann == TT.qa.values[:, None]).astype(float)
        posv = np.arange(16) / 15.0
        def sel(mask):
            on = (A * mask[:, None, None, :]).sum(-1) / np.clip(mask.sum(-1), 1, None)[:, None, None]
            off = (A * (1 - mask)[:, None, None, :]).sum(-1) / np.clip((1 - mask).sum(-1), 1, None)[:, None, None]
            return (on / np.clip(off, 1e-9, None)).mean(0)                # [L, H] ratio
        cs, as_ = sel(same_cls), sel(same_ann)
        rec = (A * (posv - posv.mean())).sum(-1).mean(0) / posv.std()        # [L, H] position slope proxy
        def show(name, order, val):
            rows = []
            for k in order[:10]:
                l, h = divmod(int(k), H)
                rows.append(f"L{l}H{h}:{val[l, h]:+.2f}|cls×{cs[l, h]:.2f}|ann×{as_[l, h]:.2f}|pos{rec[l, h]:+.2f}")
            print(f"  {name}: " + "  ".join(rows))
        show("mapping heads (Sam shift)", order_map, sam)
        show("prior heads (main effect)", order_pri, main)
        for name, order in (("mapping", order_map), ("prior", order_pri)):
            ls = [divmod(int(k), H) for k in order]
            print(f"  {name} top-{top} mean selectivity: same-class ×{np.mean([cs[l, h] for l, h in ls]):.2f}  same-annotator ×{np.mean([as_[l, h] for l, h in ls]):.2f}"
                  f"  position {np.mean([rec[l, h] for l, h in ls]):+.3f}   layers {sorted(l for l, _ in ls)}")
        np.savez(ROOT / f"results/mech/{model}_ctxeffect_{task}_heads.npz", sam=sam, alex=alex, main=main, main_sam=ms, main_alex=ma, cls_sel=cs, ann_sel=as_, pos=rec)


if __name__ == "__main__":
    main()
