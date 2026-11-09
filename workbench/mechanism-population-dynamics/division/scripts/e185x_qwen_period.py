"""E185 residual follow-up: does the Qwen3-30B-A3B 12-layer period line up with the lag-12 weight-copy blocks?
For layers 6..41 (three 12-layer blocks found by e185x_weights.py), R^2 of 'position inside the block' on each per-layer
profile (E185 summary + router-side stats), with a permutation p-value (layer order shuffled, 20000 draws).
Writes results/e185/residual_qwen3_period.json and residual_qwen3_period.png."""
import gzip, json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

R = os.path.expanduser("~/mechpop_cache/atlas_e185/resid")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results", "e185")
s = json.load(gzip.open(f"{OUT}/summary.json.gz"))
w = json.load(open(f"{R}/w_qwen3.json"))
ls = json.load(open(f"{R}/ls_qwen3.json"))
q, cf, d = s["d184"]["qwen3"], s["crossfit_Gfreq"], s["d180"]["qwen3"]
A = lambda x: np.asarray(x, float)
prof = {
    "E185 seq share T": A(q["marg:seq"]["T"]), "E185 seq share N_B": A(q["marg:seq"]["NB"]),
    "E185 inp share T": A(q["marg:inp"]["T"]), "E185 G_freq(seq|inp) T": A(cf["d184:qwen3:seq"]["T"]),
    "E185 G_freq(seq|inp) N_B": A(cf["d184:qwen3:seq"]["NB"]),
    "E185 G_freq(seq|inp) T/N_B": A(cf["d184:qwen3:seq"]["T"]) / A(cf["d184:qwen3:seq"]["NB"]),
    "E185 G_freq(pos|inp) T": A(cf["d184:qwen3:pos"]["T"]),
    "E185 H(e) T (D184)": A(q["marg:inp"]["bits_T"]) / A(q["marg:inp"]["T"]),
    "E185 H(e) N_B (D184)": A(q["marg:inp"]["bits_NB"]) / A(q["marg:inp"]["NB"]),
    "E185 D180 lang share T": A(d["full:marg:lang"]["T"]), "E185 D180 sid share T": A(d["full:marg:sid"]["T"]),
    "E185 D180 H(e) T": A(d["full:marg:lang"]["bits_T"]) / np.maximum(A(d["full:marg:lang"]["T"]), 1e-9),
}
for k in ["norm_mean", "pc1_share", "pr", "meandir_share", "lang_frac", "gate_pc1_align", "T_usage_H", "R_usage_H",
          "T_tok_entropy", "T_mi_pos_excl0", "load_H_T", "load_H_N_B", "cal_entT_full"]:
    prof["router-side " + k] = A(ls[k])
for k in ["post_ln_mean", "gate_fro", "gate_effrank", "o_fro"]:
    prof["weight " + k] = A(w["per_layer"][k])
lay = np.arange(6, 42); bp = (lay - 6) % 12
rng = np.random.default_rng(1854)
perms = np.array([rng.permutation(36) for _ in range(20000)])


def r2(y, g):
    y = y - y.mean(); tot = (y ** 2).sum()
    if tot == 0:
        return 0.0
    m = np.array([y[g == b].mean() for b in range(12)])
    return float(((m[g]) ** 2).sum() / tot)


def r2_detr(y):
    y = y - np.polyval(np.polyfit(lay, y, 1), lay)          # remove the linear depth trend first
    return y


res = {}
G = np.eye(12)[bp]
for k, v in prof.items():
    y = r2_detr(v[lay])
    obs = r2(y, bp)
    # vectorised permutation null
    Y = y[perms]; Y = Y - Y.mean(1, keepdims=True)
    M = (Y @ G) / 3.0; num = (M ** 2).sum(1) * 3; den = (Y ** 2).sum(1)
    p = float(((num / den) >= obs).mean())
    cop = np.array([v[6 + 12 * c: 18 + 12 * c] for c in range(3)])
    cc = np.corrcoef(cop - cop.mean(1, keepdims=True))
    res[k] = dict(R2_blockpos=obs, p_perm=p, corr_copies=[cc[0, 1], cc[0, 2], cc[1, 2]])
    print(f"{k:40s} R2 {obs:.2f} p {p:.4f} copy-corr {cc[0,1]:+.2f} {cc[0,2]:+.2f} {cc[1,2]:+.2f}")
json.dump({"blocks": "6-17 / 18-29 / 30-41 (lag-12 weight copies)", "profiles": res,
           "lag_similarity": w["lag_mean_similarity"]}, open(f"{OUT}/residual_qwen3_period.json", "w"), indent=1)

fig, ax = plt.subplots(1, 3, figsize=(15, 4.2))
im = ax[0].imshow(np.array(w["sim"]["v"]), cmap="viridis", vmin=0, vmax=0.6)
ax[0].set_title("Qwen3-30B-A3B: cos(v_proj layer i, layer j)"); ax[0].set_xlabel("layer j"); ax[0].set_ylabel("layer i")
plt.colorbar(im, ax=ax[0], fraction=0.046)
for a, keys, ttl in [(ax[1], ["E185 G_freq(seq|inp) T", "E185 G_freq(seq|inp) N_B", "E185 G_freq(pos|inp) T"], "E185 profiles (bit)"),
                     (ax[2], ["E185 H(e) T (D184)", "E185 H(e) N_B (D184)", "E185 D180 H(e) T"], "expert entropy H(e) (bit)")]:
    for k in keys:
        a.plot(range(48), prof[k], marker=".", label=k.replace("E185 ", ""))
    for c in range(3):
        a.axvspan(6 + 12 * c - .5, 6 + 12 * c + 1.5, color="orange", alpha=.15)
        a.axvspan(6 + 12 * c + 5 - .5, 6 + 12 * c + 7.5, color="grey", alpha=.15)
    for x in (5.5, 17.5, 29.5, 41.5):
        a.axvline(x, color="k", lw=.6, ls="--")
    a.set_title(ttl + "; dashed = copy-block borders"); a.set_xlabel("layer"); a.legend(fontsize=7)
plt.tight_layout(); plt.savefig(f"{OUT}/residual_qwen3_period.png", dpi=130)
