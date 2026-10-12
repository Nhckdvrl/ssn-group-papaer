"""E41 analysis: which components carry order variance (within base) vs evidence variance (between bases).
usage: analyze_order.py results/mech/e41_<tag>_perm.npz <tag>
Share_c = Cov(x_c, ld) / Var(ld), computed on within-base deviations and on base means separately.
Also: for heads, how much of the within-base DLA variation follows the attention-weighted label sign
r_c = sum_t att_c[t] * sigma_t (which labels the head reads) vs the head's output gain."""
import json, re, sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
POLE = {"small": 0, "large": 1, "little": 0, "big": 1, "A": 0, "B": 1}


def e36_heads(tag, top=20):
    """E36 top-20 Sam-shift heads (numbers task) as in mech_ablate.select_heads."""
    sys.path.insert(0, str(ROOT / "scripts"))
    from mech_ablate import rows_by_task, select_heads
    R, _ = rows_by_task()
    return set(map(tuple, select_heads(tag, R)["mag_nat"]["top20"]))


def main():
    z = np.load(sys.argv[1]); tag = sys.argv[2]
    uid = z["uid"]; D = z["dla_head"].astype(np.float64); M = z["dla_mlp"].astype(np.float64); ld = z["logit_diff"].astype(np.float64)
    A = z["att_lab"].astype(np.float64)
    N, L, H = D.shape
    rows = {json.loads(l)["uid"]: json.loads(l) for l in open(ROOT / "data/kernel_perm/rows.jsonl")}
    sig = np.array([[2 * POLE[w] - 1 for w in re.findall(r"Label: (\S+)\n", rows[u]["prompt"])] for u in uid], np.float64)
    base = np.array([u.split("|")[0] for u in uid])
    ub = sorted(set(base)); bi = np.array([ub.index(b) for b in base])
    recon = D.sum((1, 2)) + M.sum(1)
    out = {"recon_r": float(np.corrcoef(recon, ld)[0, 1])}

    def split(x):
        mu = np.zeros((len(ub),) + x.shape[1:])
        np.add.at(mu, bi, x); mu /= np.bincount(bi, minlength=len(ub)).reshape((-1,) + (1,) * (x.ndim - 1))
        return x - mu[bi], mu - mu.mean(0)
    ldw, ldb = split(ld)
    Dw, Db = split(D); Mw, Mb = split(M)
    sh = lambda Xw, yw: np.tensordot(yw, Xw, axes=(0, 0)) / (yw ** 2).sum()
    hw, hb = sh(Dw, ldw), sh(Db, ldb)          # [L, H]
    mw, mb = sh(Mw, ldw), sh(Mb, ldb)          # [L]
    out["var_within"] = float((ldw ** 2).mean()); out["var_between"] = float((ldb ** 2).mean())
    out["sum_share_within"] = {"heads": float(hw.sum()), "mlp": float(mw.sum())}
    out["sum_share_between"] = {"heads": float(hb.sum()), "mlp": float(mb.sum())}
    lab = e36_heads(tag)
    m = np.zeros((L, H), bool)
    for l, h in lab:
        m[l, h] = True
    out["e36_top20_share"] = {"within": float(hw[m].sum()), "between": float(hb[m].sum())}
    ordw = np.argsort(-hw.ravel())[:20]; ordb = np.argsort(-hb.ravel())[:20]
    out["top20_within"] = [[f"{k // H}.{k % H}", round(float(hw.ravel()[k]), 3), round(float(hb.ravel()[k]), 3)] for k in ordw]
    out["top20_between"] = [[f"{k // H}.{k % H}", round(float(hb.ravel()[k]), 3), round(float(hw.ravel()[k]), 3)] for k in ordb]
    out["top20_overlap"] = len(set(ordw) & set(ordb))
    out["share_map_corr"] = float(np.corrcoef(hw.ravel(), hb.ravel())[0, 1])
    out["layer_share_within"] = (hw.sum(1) + mw).round(3).tolist()
    out["layer_share_between"] = (hb.sum(1) + mb).round(3).tolist()
    out["mlp_share_within_by_layer"] = mw.round(3).tolist()
    # reading jitter: within-base variation of head DLA vs attention-weighted label sign
    jit = []
    for k in ordw[:10]:
        l, h = divmod(int(k), H)
        a = A[:, l, h, :] / np.clip(A[:, l, h, :].sum(-1, keepdims=True), 1e-9, None)
        read = (a * sig).sum(-1); mass = A[:, l, h, :].sum(-1)
        rw, _ = split(read); mw_, _ = split(mass); dw = Dw[:, l, h]
        jit.append({"head": f"{l}.{h}", "r(dla, read_sign)": round(float(np.corrcoef(dw, rw)[0, 1]), 3),
                    "r(dla, label_mass)": round(float(np.corrcoef(dw, mw_)[0, 1]), 3),
                    "label_mass_mean": round(float(mass.mean()), 3)})
    out["jitter_top10_within"] = jit
    Path(sys.argv[1].replace(".npz", "_order.json")).write_text(json.dumps(out, indent=1))
    print(json.dumps({k: v for k, v in out.items() if k not in ("layer_share_within", "layer_share_between", "mlp_share_within_by_layer")}, indent=1))
    print("layer within ", out["layer_share_within"]); print("layer between", out["layer_share_between"])


if __name__ == "__main__":
    main()
