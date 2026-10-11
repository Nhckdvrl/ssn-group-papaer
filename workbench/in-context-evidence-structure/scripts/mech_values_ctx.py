"""E37 on E30 (ctxeffect): decompose Sam shift / Alex spill (inter) and main effect into anchor groups.
usage: mech_values_ctx.py MODEL"""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def main():
    model = sys.argv[1]
    z = np.load(ROOT / f"results/mech/vals_{model}_ctxeffect.npz")
    meta = {}
    for l in open(ROOT / "data/ctxeffect/rows.jsonl"):
        r = json.loads(l); meta[r["uid"]] = r
    uids = list(z["uid"]); idx = {u: i for i, u in enumerate(uids)}; vp = z["vproj"]; at = z["att"]; rms = z["rms"]
    H = vp.shape[2]
    for task in ("mag_nat", "sst"):
        Hs = np.load(ROOT / f"results/mech/{model}_ctxeffect_{task}_heads.npz")
        hl = [divmod(int(k), H) for k in np.argsort(-Hs["sam"].ravel())[:20]]
        Li = np.array([l for l, _ in hl]); Hi = np.array([h for _, h in hl])

        def contrib(u, sign):     # per-anchor contribution summed over reading heads, signed, logit units  -> [16]
            i = idx[u]; c = (vp[i][Li, Hi].astype(float) * at[i][Li, Hi].astype(float)).sum(0) / rms[i]
            return sign * c

        rows = []
        for u in uids:
            r = meta[u]
            if not r["cond"].startswith(task):
                continue
            cond = r["cond"].split(":")[1]; s = r["qA"] ^ r["qclass"]
            same_u = u.replace(f":{cond}|", ":same|"); c = np.array(meta[same_u]["labels"]) ^ s
            ann = np.array(r["ann"]); labs = np.array(r["labels"]); dev = labs != (c ^ s)
            # sign: toward B answer (inter, same) or toward L (main); vproj direction is label1 - label0
            tgt = (1 - r["qA"]) if cond != "main" else r["L"]
            v = contrib(u, 1.0 if tgt == 1 else -1.0)
            rows.append(dict(base=r["base_id"], qc=r["qclass"], qa=r["qann"], cond=cond,
                             sam_dev=v[(ann == 1) & dev].sum(), sam_ok=v[(ann == 1) & ~dev].sum(), alex=v[ann == 0].sum(),
                             tgt=tgt))
        D = pd.DataFrame(rows)
        print(f"\n===== {model} / {task}  (top-20 reading heads; contributions in logits)")
        for cond in ("inter", "main"):
            for qa, name in ((1, "Sam query"), (0, "Alex query")):
                x = D[(D.cond == cond) & (D.qa == qa)].set_index(["base", "qc"])
                y = D[(D.cond == "same") & (D.qa == qa)].set_index(["base", "qc"])
                if cond == "main":   # re-sign the 'same' baseline toward L
                    y = y.copy()
                    flip = np.where(x.loc[y.index].tgt.values == 1, 1, -1) * np.where(D[(D.cond == "same") & (D.qa == qa)].set_index(["base", "qc"]).loc[y.index].tgt.values == 1, 1, -1)
                    for k in ("sam_dev", "sam_ok", "alex"):
                        y[k] = y[k] * flip
                d = (x[["sam_dev", "sam_ok", "alex"]] - y.loc[x.index, ["sam_dev", "sam_ok", "alex"]]).mean()
                print(f"  {cond:5s} {name:10s} Δ from same: Sam-deviant {d.sam_dev:+.2f}  Sam-agreeing {d.sam_ok:+.2f}  Alex {d.alex:+.2f}  total {d.sum():+.2f}")


if __name__ == "__main__":
    main()
