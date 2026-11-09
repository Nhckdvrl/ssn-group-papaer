"""E185 residual follow-up (CPU, read-only on ~/mechpop_cache/e180): last-layer language information on letterless
(NON) tokens.  Is Î(e; language | input id) on NON tokens (OLMoE last layer T .246 vs N_B0 .088) explained by
 (i) a few language-specific ids, (ii) position (sentence-final), (iii) what comes next (predicted / true next token
 or its script)?  E185 plug-in estimator (e185_lib), same floors.  Routers T, N_A0, N_B0.
usage: e185x_punct.py <key> -> ~/mechpop_cache/atlas_e185/resid/punct_<key>.json"""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e185_lib import CACHE, Plan, mi_cond, mi_marg, tokclass_table, dense, pool_rare, H_keys, shuffle_within  # noqa

key = sys.argv[1]
base = f"{CACHE}/e180/{key}"
meta = json.load(open(f"{base}/meta.json"))
L, E = meta["L"], meta["E"]
tm = dict(np.load(f"{base}/tokmeta.npz"))
arr = np.load(f"{base}/topk.npy", mmap_mode="r")
langs = meta["langs"]
lang_of = np.array([lg.split("_")[0] for lg in langs]); scr_of = np.array([lg.split("_")[1] for lg in langs])
_, langcode = np.unique(lang_of, return_inverse=True)
scr_u, scrcode = np.unique(np.where(np.isin(scr_of, ["Hans", "Hant"]), "Han", scr_of), return_inverse=True)
side = tm["lang"].astype(np.int64); lang = langcode[side]; script = scrcode[side]
inp = tm["inp"].astype(np.int64); pred = tm["pred"].astype(np.int64); pos = tm["pos"].astype(np.int64)
seq = side * 100000 + tm["sid"]
end = np.r_[seq[1:] != seq[:-1], True]
nxt = np.where(end, -1, np.r_[inp[1:], -1])
tok, strs, cls = tokclass_table(key)
V = len(cls)
# data-driven script of every vocab id: majority script among the sides where it occurs as an input; NON ids -> own class
cnt = np.zeros((V, len(scr_u)), np.int64)
np.add.at(cnt, (inp, script), 1)
idscr = np.where(cnt.sum(1) > 0, cnt.argmax(1), len(scr_u))           # unseen -> 'unk'
idscr = np.where(cls == 2, len(scr_u) + 1, idscr)                     # letterless -> 'NON'
pred_scr = idscr[pred]; nxt_scr = np.where(nxt >= 0, idscr[np.maximum(nxt, 0)], -1)
final = end.astype(np.int64)
non = np.where(cls[inp] == 2)[0]
nlang_per_id = {int(v): int(len(np.unique(lang[non][inp[non] == v]))) for v in np.unique(inp[non])}

p = Plan(non)
p.add_cond("lang|inp", lang, inp)
p.add_cond("lang|inp,final", lang, inp * 2 + final)
p.add_cond("lang|inp,predscr", lang, inp * 16 + pred_scr)
p.add_cond("lang|inp,pred", lang, inp * 1_000_003 + pred)
nf = nxt >= 0
p.add_cond("lang|inp,nxtscr", lang, inp * 16 + np.maximum(nxt_scr, 0), sub=nf)
p.add_cond("lang|inp@nonfinal", lang, inp, sub=nf)
p.add_cond("predscr|inp", pred_scr, inp)
p.add_cond("predscr|inp,lang", pred_scr, inp * 64 + lang)
p.add_cond("final|inp", final, inp)
p.add_marg("lang", lang)
res = {"n_non": int(non.size), "coverage": {k: v["cov"] for k, v in p.cond.items()}, "layers": {}}
RN = meta["topk_routers"]
layers = sorted(set([L - 1, L - 2, L // 2]))
for l in layers:
    blk = np.asarray(arr[l])[:, :, 0].astype(np.int64)            # top-1 [N, R]
    out = {}
    for ri, rn in enumerate(RN):
        e = blk[:, ri]
        o = {}
        for nm, f in p.cond.items():
            I, Ip, sd, He = mi_cond(e[f["idx"]], f, E)
            o[nm] = I / He
        I, Ip, sd, He = mi_marg(e[p.marg["lang"]["idx"]], p.marg["lang"], E); o["lang"] = I / He; o["H"] = He
        # per-id decomposition of Î(lang | inp): p(x) [I(e;lang | x) - floor_x]   (floor: permute lang within x)
        if l == L - 1:
            rng = np.random.default_rng(185)
            ee = e[non]; ll = lang[non]; xx = inp[non]
            contrib = []
            for v in np.unique(xx):
                m = xx == v
                if m.sum() < 30:
                    continue
                ev, lv = ee[m], ll[m]
                def mi(a, b):
                    return H_keys(a) + H_keys(b) - H_keys(b * E + a)
                fl = np.mean([mi(ev, rng.permutation(lv)) for _ in range(3)])
                contrib.append((int(v), strs[v], int(m.sum()), nlang_per_id[int(v)], float(m.mean() * (mi(ev, lv) - fl)),
                                float(final[non][m].mean())))
            contrib.sort(key=lambda t: -t[4])
            tot = sum(c[4] for c in contrib)
            o["per_id_top"] = [dict(id=c[0], s=c[1], n=c[2], nlang=c[3], bits=c[4], share_of_sum=c[4] / tot,
                                    frac_final=c[5]) for c in contrib[:15]]
            o["per_id_total_bits"] = tot
            o["per_id_top5_share"] = sum(c[4] for c in contrib[:5]) / tot
        out[rn] = o
    res["layers"][str(l)] = out
    print(key, l, {rn: {k: (round(v, 3) if isinstance(v, float) else '...') for k, v in out[rn].items()} for rn in RN},
          flush=True)
json.dump(res, open(os.path.expanduser(f"~/mechpop_cache/atlas_e185/resid/punct_{key}.json"), "w"), ensure_ascii=False,
          indent=1)
