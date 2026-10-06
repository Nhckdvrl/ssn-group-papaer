"""E36 on E28 prompts (imbal).  usage: mech_analyze_imbal.py MODEL [--top 20]
Per head, signed DLA toward the B-mapping answer; for each query role (maj/min) the time contrasts
(suffix_8 - prefix_8, suffix_4 - disp_4); components: bias = (maj - min)/2, cond = (maj + min)/2.
Attention keys of top heads per component: same-class selectivity and position slope (recency)."""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def main():
    model = sys.argv[1]; top = int(sys.argv[sys.argv.index("--top") + 1]) if "--top" in sys.argv else 20
    z = np.load(ROOT / f"results/mech/{model}_imbal.npz")
    meta = {}
    for l in open(ROOT / "data/imbal/rows.jsonl"):
        r = json.loads(l); meta[r["uid"]] = r
    uids = list(z["uid"]); dla = z["dla_head"]; mlp = z["dla_mlp"]; att = z["att_lab"]; idx = {u: i for i, u in enumerate(uids)}
    L, H = dla.shape[1:]
    M = pd.DataFrame([dict(uid=u, task=meta[u]["cond"].split(":")[0], pat=meta[u]["cond"].split(":")[1], q=meta[u]["qrole"],
                           base=meta[u]["base_id"]) for u in uids])
    for task, T in M.groupby("task"):
        print(f"\n===== {model} / {task}")
        # B-answer index: cands = [A-answer, B-answer] -> DLA direction (label1 - label0) is already toward B
        def contrast(p1, p2, q):
            x = T[(T.pat == p1) & (T.q == q)].set_index("base"); y = T[(T.pat == p2) & (T.q == q)].set_index("base")
            c = x.index.intersection(y.index)
            d = np.stack([dla[idx[u]] for u in x.loc[c].uid]) - np.stack([dla[idx[u]] for u in y.loc[c].uid])
            m = np.stack([mlp[idx[u]] for u in x.loc[c].uid]) - np.stack([mlp[idx[u]] for u in y.loc[c].uid])
            return d.mean(0), m.mean(0)
        res = {}
        for name, p1, p2 in (("s8-p8", "suffix_8", "prefix_8"), ("cluster", "suffix_4", "disp_4"), ("noise", "noise_2__suffix_3", "suffix_3")):
            (dM, mM), (dm, mm) = contrast(p1, p2, "maj"), contrast(p1, p2, "min")
            res[name] = dict(bias=(dM - dm) / 2, cond=(dM + dm) / 2, bias_m=(mM - mm) / 2, cond_m=(mM + mm) / 2)
            r = res[name]
            print(f"  {name:8s} bias: heads {r['bias'].sum():+.2f} MLP {r['bias_m'].sum():+.2f} | cond: heads {r['cond'].sum():+.2f} MLP {r['cond_m'].sum():+.2f}")
        # attention keys on suffix_8 prompts
        TT = T[T.pat == "suffix_8"]
        A = np.stack([att[idx[u]] for u in TT.uid]); A = A / np.clip(A.sum(-1, keepdims=True), 1e-9, None)
        late = (np.arange(16) >= 8).astype(float)
        rec = (A * late).sum(-1).mean(0) / 0.5                                  # share on last 8 (B) demos, 1 = uniform
        flat = lambda X: X.reshape(-1)
        for comp in ("bias", "cond"):
            v = res["s8-p8"][comp]; order = np.argsort(-flat(v))[:top]
            ls = [divmod(int(k), H) for k in order]
            print(f"  top-{top} heads for {comp} (s8-p8): carry {flat(v)[order].sum() / v.sum():.0%}; mean late-share ×{np.mean([rec[l, h] for l, h in ls]):.2f}; "
                  f"layers {sorted(l for l, _ in ls)}")
            print("     " + "  ".join(f"L{l}H{h}:{v[l, h]:+.2f}|late×{rec[l, h]:.2f}" for l, h in ls[:8]))
        vb, vc = flat(res["s8-p8"]["bias"]), flat(res["s8-p8"]["cond"])
        ob, oc = set(np.argsort(-vb)[:top]), set(np.argsort(-vc)[:top])
        print(f"  overlap of top-{top} bias heads and cond heads: {len(ob & oc)}/{top}; corr(bias, cond) over heads {np.corrcoef(vb, vc)[0, 1]:+.2f}")
        np.savez(ROOT / f"results/mech/{model}_imbal_{task}_heads.npz", **{f"{k}_{c}": v[c] for k, v in res.items() for c in ("bias", "cond")}, late=rec)


if __name__ == "__main__":
    main()
