"""E37 analysis on E28 (imbal).  usage: mech_values_analyze.py MODEL"""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze_common import boot_ci, fmt  # noqa

ROOT = Path(__file__).resolve().parents[1]


def main():
    model = sys.argv[1]
    z = np.load(ROOT / f"results/mech/vals_{model}_imbal.npz")
    meta = {}
    for l in open(ROOT / "data/imbal/rows.jsonl"):
        r = json.loads(l); meta[r["uid"]] = r
    uids = list(z["uid"]); idx = {u: i for i, u in enumerate(uids)}
    vp = z["vproj"]; at = z["att"]; rms = z["rms"]; L, H = vp.shape[1:3]
    M = pd.DataFrame([dict(uid=u, task=meta[u]["cond"].split(":")[0], pat=meta[u]["cond"].split(":")[1], q=meta[u]["qrole"], base=meta[u]["base_id"]) for u in uids])
    for task, T in M.groupby("task"):
        Hs = np.load(ROOT / f"results/mech/{model}_imbal_{task}_heads.npz")
        heads = set(np.argsort(-Hs["s8-p8_bias"].ravel())[:20]) | set(np.argsort(-Hs["s8-p8_cond"].ravel())[:20])
        hl = [divmod(int(k), H) for k in heads]
        print(f"\n===== {model} / {task}  reading heads {len(hl)}")
        sumv = lambda u, ts: float(sum(vp[idx[u]][l, h, ts].astype(float).sum() for l, h in hl))
        sumav = lambda u, ts: float(sum((vp[idx[u]][l, h, ts].astype(float) * at[idx[u]][l, h, ts].astype(float)).sum() for l, h in hl)) / rms[idx[u]]
        def delta(p1, p2, ts, f):
            out = {}
            for q in ("maj", "min"):
                x = T[(T.pat == p1) & (T.q == q)].set_index("base"); y = T[(T.pat == p2) & (T.q == q)].set_index("base")
                c = x.index.intersection(y.index)
                out[q] = np.array([f(x.loc[b].uid, ts) - f(y.loc[b].uid, ts) for b in c])
            return (out["maj"] - out["min"]) / 2, (out["maj"] + out["min"]) / 2
        for name, p1, p2, ts in (("sanity old anchors s8-allA", "suffix_8", "allA", list(range(8))),
                                 ("anchor noise (t13-15)", "noise_2__suffix_3", "suffix_3", [13, 14, 15]),
                                 ("anchor cluster (t15)", "suffix_4", "disp_4", [15])):
            for lab, f in (("value", sumv), ("att*value", sumav)):
                b, c = delta(p1, p2, ts, f)
                print(f"  {name:28s} {lab:9s} bias {fmt(*boot_ci(b), p=3)}   cond {fmt(*boot_ci(c), p=3)}")


if __name__ == "__main__":
    main()
