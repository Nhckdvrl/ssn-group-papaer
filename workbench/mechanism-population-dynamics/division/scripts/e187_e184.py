"""E187 读数 4 (English E184 store, routing only) + label-free co-routing correlation (card "无标签对照").
Store: ~/mechpop_cache/e184/qwen3/topk.npy [48, 85647, 17, 8] (0 = T, 9..16 = N_B), tokmeta.npz (UPOS, pos, ids).
For copy pairs (l, l+12) l = 6..29 and (l, l+24) l = 6..17 (router-row matching from e187_wdrift.py):
  - O top-1 / top-8 by class: UPOS, position bin, letter / non-letter, frequency quintile (counts in this store),
    E185 H(e|id) tertile (tok_d184_qwen3.npz, layer l, router T; coverage reported)
  - per-id agreement (ids with >= 30 occurrences), top / bottom 20 with contexts
  - [POST-HOC, added after registration] type-level agreement: pi(mode_m(id)) == mode_l(id) for ids >= 30
Label-free (no expert map): T_ctx = corr over same-type occurrence pairs of within-type-centred co-routing
C = |S_i & S_j| / 8 between layer l and m; T_D = same for D = C - mean_{8 N_B} C; floor = within-type occurrence
permutation of layer m (20).  Pairs: copies (12, 24) and references lag 1 / 11 / 13 inside 6..41.
Writes results/e187/e184_classes.json, e184_coroute.json, e184_examples.md."""
import json, os, unicodedata
import numpy as np
os.environ.setdefault("HF_HUB_OFFLINE", "1")
from transformers import AutoTokenizer

C = os.path.expanduser("~/mechpop_cache/e187")
RES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results", "e187")
L, E, K = 48, 128, 8
A = np.load("/home/xiang/mechpop_cache/e184/qwen3/topk.npy", mmap_mode="r")
tm = np.load("/home/xiang/mechpop_cache/e184/qwen3/tokmeta.npz")
meta = json.load(open("/home/xiang/mechpop_cache/e184/qwen3/meta.json"))
UP = meta["upos"]
from e187_common import RouterMatch
match = RouterMatch("instruct")
tok = AutoTokenizer.from_pretrained("Qwen/Qwen3-30B-A3B")
inp, pos, upos, seq = tm["inp"], tm["pos"], tm["upos"], tm["seq"]
corpus = tm["corpus"]
N = inp.size
T = {l: np.asarray(A[l, :, 0, :]).astype(np.int64) for l in range(L)}
uid, uinv, ucnt = np.unique(inp, return_inverse=True, return_counts=True)
freq = ucnt[uinv]
fq = np.searchsorted(np.quantile(freq, [.2, .4, .6, .8]), freq, side="right")
strs = {int(u): tok.decode([int(u)]) for u in uid}


def is_letter(s):
    s = s.strip()
    return bool(s) and unicodedata.category(s[0]).startswith("L")


letter = np.array([is_letter(strs[int(i)]) for i in inp])
posbin = np.digitize(pos, [1, 5, 20])          # 0: pos 0, 1: 1-4, 2: 5-19, 3: >= 20
tk = np.load("/home/xiang/mechpop_cache/atlas_e185/tok_d184_qwen3.npz")
hx_ids = tk["ids"]; HX = tk["Hx"][:, 0, :]     # [L, 283] router 0 = T
id2col = {int(v): i for i, v in enumerate(hx_ids)}
hcol = np.array([id2col.get(int(i), -1) for i in inp])


def agree(l, m):
    p = match[f"{l}_{m}_router"]
    a, b = T[l], p[T[m]]
    t1 = (a[:, 0] == b[:, 0]).astype(np.float64)
    MA = np.zeros((N, E), bool); MA[np.arange(N)[:, None], a] = True
    ov = MA[np.arange(N)[:, None], b].sum(1) / K
    return t1, ov


def by(v, lab, names):
    return {names[c] if names else str(c): [float(v[lab == c].mean()), int((lab == c).sum())] for c in np.unique(lab) if c >= 0}


cls = {"pairs": []}
per_id = []                                   # per pair: dict id -> mean t1
typelev = []
for lag, rng_l in ((12, range(6, 30)), (24, range(6, 18))):
    for l in rng_l:
        m = l + lag
        t1, ov = agree(l, m)
        rec = dict(l=l, m=m, lag=lag, top1=float(t1.mean()), top8=float(ov.mean()))
        rec["upos_top1"] = by(t1, upos, UP); rec["pos_top1"] = by(t1, posbin, ["0", "1-4", "5-19", ">=20"])
        rec["letter_top1"] = by(t1, letter.astype(int), ["non-letter", "letter"])
        rec["freq_top1"] = by(t1, fq, ["q1(rare)", "q2", "q3", "q4", "q5(freq)"])
        rec["upos_top8"] = by(ov, upos, UP); rec["freq_top8"] = by(ov, fq, ["q1(rare)", "q2", "q3", "q4", "q5(freq)"])
        # H(e|id) tertiles at layer l (covered tokens only)
        cov = hcol >= 0
        hv = np.full(N, np.nan); hv[cov] = HX[l][hcol[cov]]
        qs = np.nanquantile(HX[l], [1 / 3, 2 / 3])
        ht = np.where(cov, np.searchsorted(qs, np.nan_to_num(hv), side="right"), -1)
        rec["Hx_top1"] = by(t1, ht, ["low H(e|id)", "mid", "high H(e|id)"]); rec["Hx_coverage"] = float(cov.mean())
        rec["Hx_top8"] = by(ov, ht, ["low H(e|id)", "mid", "high H(e|id)"])
        s1 = np.bincount(uinv, t1, uid.size) / ucnt
        per_id.append(s1)
        # id-level Spearman between H(e|id) at layer l and per-id agreement
        from scipy.stats import spearmanr
        hids = np.array([np.searchsorted(uid, i) for i in hx_ids])
        rec["spearman_Hx_vs_id_agree"] = float(spearmanr(HX[l], s1[hids]).correlation)
        # type-level agreement (POST-HOC)
        p = match[f"{l}_{m}_router"]
        big = np.where(ucnt >= 30)[0]
        ml = np.array([np.bincount(T[l][uinv == j, 0], minlength=E).argmax() for j in big])
        mm_ = np.array([np.bincount(p[T[m][uinv == j, 0]], minlength=E).argmax() for j in big])
        rec["typelevel_mode_agree"] = float((ml == mm_).mean()); rec["typelevel_n_ids"] = int(big.size)
        # token-level agreement restricted to tokens routed to their id's mode at both layers vs not (POST-HOC)
        modeL = np.full(uid.size, -1); modeL[big] = ml
        modeM = np.full(uid.size, -1); modeM[big] = mm_
        atmode = (T[l][:, 0] == modeL[uinv]) & (p[T[m][:, 0]] == modeM[uinv])
        rec["frac_tokens_both_at_id_mode"] = float(atmode.mean())
        cls["pairs"].append(rec)
        print(l, m, round(rec["top1"], 3), "Hx", {k: round(v[0], 3) for k, v in rec["Hx_top1"].items()},
              "typelev", round(rec["typelevel_mode_agree"], 3), flush=True)
json.dump(cls, open(f"{RES}/e184_classes.json", "w"), indent=0)

# ---- raw examples: ids >= 30, mean agreement over the 24 lag-12 pairs
PA = np.mean(per_id[:24], 0)
big = np.where(ucnt >= 30)[0]
order = big[np.argsort(PA[big])]
lines = ["# E187 原始样例：E184 英语存储上拷贝层 (l, l+12) 逐 id top-1 一致率（24 个块对平均；≥ 30 次的 id）", "",
         f"共 {big.size} 个 id；全体 token 平均 {np.mean([r['top1'] for r in cls['pairs'][:24]]):.3f}", ""]
rs = np.random.default_rng(0)


def ctx(i):
    s, p0 = seq[i], pos[i]
    w = np.where((seq == s) & (corpus == corpus[i]) & (np.abs(pos - p0) <= 4))[0]
    w = w[np.argsort(pos[w])]
    return "".join(("⟦" + strs[int(inp[j])] + "⟧") if j == i else strs[int(inp[j])] for j in w).replace("\n", " ")


for title, sel in (("最高 20", order[::-1][:20]), ("最低 20", order[:20])):
    lines += [f"## {title}", "", "| id | token | 次数 | 一致率 | H(e|id) 第 12 层 | 上下文样例 |", "|---|---|---|---|---|---|"]
    for j in sel:
        occ = np.where(uinv == j)[0]
        ex = ctx(int(rs.choice(occ)))
        hxv = HX[12][id2col[int(uid[j])]] if int(uid[j]) in id2col else float("nan")
        lines.append(f"| {uid[j]} | `{strs[int(uid[j])]!r}` | {ucnt[j]} | {PA[j]:.3f} | {hxv:.2f} | {ex[:80]} |")
    lines.append("")
open(f"{RES}/e184_examples.md", "w").write("\n".join(lines))

# ---- label-free co-routing correlation
rs = np.random.default_rng(187)
occ_by = [np.where(uinv == j)[0] for j in np.where(ucnt >= 2)[0]]
I, J, TY = [], [], []
for t, o in enumerate(occ_by):
    if o.size > 30:
        o = np.sort(rs.choice(o, 30, replace=False))
    a, b = np.triu_indices(o.size, 1)
    I.append(o[a]); J.append(o[b]); TY.append(np.full(a.size, t))
I, J, TY = np.concatenate(I), np.concatenate(J), np.concatenate(TY)
NT = TY.max() + 1
print("co-routing pairs", I.size, "types", NT, flush=True)


def onehot(S):
    M = np.zeros((S.shape[0], E), np.uint8); M[np.arange(S.shape[0])[:, None], S] = 1
    return M


CO = {}


def coroute(l):
    if l not in CO:
        M = onehot(T[l]); c = (M[I] & M[J]).sum(1) / K
        bsum = np.zeros(I.size)
        for r in range(9, 17):
            Mn = onehot(np.asarray(A[l, :, r, :]).astype(np.int64)); bsum += (Mn[I] & Mn[J]).sum(1) / K
        CO[l] = (c, c - bsum / 8)
    return CO[l]


def centre(x):
    return x - (np.bincount(TY, x, NT) / np.bincount(TY, None, NT))[TY]


def corr(a, b):
    return float((a * b).sum() / np.sqrt((a * a).sum() * (b * b).sum()))


crow = []
perm_occ = []
for _ in range(20):                     # within-type occurrence permutation (relabel occurrences inside each type)
    pm = np.arange(N)
    for o in occ_by:
        pm[o] = rs.permutation(o)
    perm_occ.append(pm)
for lag in (12, 24, 1, 11, 13):
    for l in range(6, 42 - lag + 1):
        m = l + lag
        if m > 41:
            continue
        cl, dl = coroute(l); cm, dm = coroute(m)
        rec = dict(l=l, m=m, lag=lag, T_ctx=corr(centre(cl), centre(cm)), T_D=corr(centre(dl), centre(dm)))
        if lag in (12, 1) and l in (6, 12, 18):
            Mm = onehot(T[m]); fl = []
            for pm in perm_occ[:10]:
                fl.append(corr(centre(cl), centre((Mm[pm[I]] & Mm[pm[J]]).sum(1) / K)))
            rec["T_ctx_floor"] = [float(np.mean(fl)), float(np.max(np.abs(fl)))]
        crow.append(rec)
        print("coroute", l, m, round(rec["T_ctx"], 3), round(rec["T_D"], 3), flush=True)
json.dump(crow, open(f"{RES}/e184_coroute.json", "w"), indent=0)
print("done")
