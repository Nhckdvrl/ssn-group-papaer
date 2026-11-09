"""E185 residual follow-up (CPU only, no GPU): exact re-computation of the layer-0 router input from checkpoint
weights (embedding -> input RMSNorm -> attention -> residual -> post-attention RMSNorm), on all FLORES dev sentences
of the E179 languages, with the attention output split by source position (self / previous / other).
Validates against E179 toksub.npy (layer 0), then reports
  - per-head attention mass on previous / self / position-0 token
  - top-1 changes when one component is replaced by its mean (embedding x_t, attention-from-self, -from-previous,
    -from-other) under the trained gate T and under Haar-rotated gates (N_A-style)
  - logit variance carried by each component
  - floor-corrected MI(top-1; current id) and MI(top-1; previous id) (E185 plug-in estimator) for T and rotations.
usage: e185x_layer0.py <key> -> ~/mechpop_cache/atlas_e185/resid/l0_<key>.json"""
import json, os, sys, glob
import numpy as np
import torch
from safetensors import safe_open

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e185_lib import pool_rare, dense, H_keys  # noqa: E402
os.environ.setdefault("HF_HUB_OFFLINE", "1")
from transformers import AutoTokenizer  # noqa: E402

key = sys.argv[1]
torch.set_num_threads(int(os.environ.get("NT", "12")))
base = f"/home/xiang/mechpop_cache/e179/{key}"
meta = json.load(open(f"{base}/meta.json"))
hf = meta["model"]
snap = glob.glob(os.path.expanduser(f"~/.cache/huggingface/hub/models--{hf.replace('/', '--')}/snapshots/*"))[0]
cfg = json.load(open(f"{snap}/config.json"))
wmap = json.load(open(f"{snap}/model.safetensors.index.json"))["weight_map"]


def get(n):
    with safe_open(f"{snap}/{wmap[n]}", "pt") as f:
        return f.get_tensor(n).float()


p = "model.layers.0."
EMB = get("model.embed_tokens.weight")
g_in, g_post = get(p + "input_layernorm.weight"), get(p + "post_attention_layernorm.weight")
Wq, Wk, Wv, Wo = [get(p + f"self_attn.{x}_proj.weight") for x in "qkvo"]
gq, gk = get(p + "self_attn.q_norm.weight"), get(p + "self_attn.k_norm.weight")
G = get(p + "mlp.gate.weight")
eps, hd, nH, nKV, theta = cfg["rms_norm_eps"], cfg.get("head_dim", cfg["hidden_size"] // cfg["num_attention_heads"]), \
    cfg["num_attention_heads"], cfg["num_key_value_heads"], cfg["rope_theta"]
d, E, K = cfg["hidden_size"], cfg["num_experts"], cfg["num_experts_per_tok"]
PERHEAD_QK = key.startswith("qwen3")      # Qwen3: q/k norm per head; OLMoE: over the full projection
inv = 1.0 / (theta ** (torch.arange(0, hd, 2).float() / hd))


def rms(x, g):
    return x * torch.rsqrt(x.pow(2).mean(-1, keepdim=True) + eps) * g


def rot(x):
    h = x.shape[-1] // 2
    return torch.cat([-x[..., h:], x[..., :h]], -1)


def layer0(ids):
    T = len(ids)
    x = EMB[ids]
    xn = rms(x, g_in)
    q, k, v = xn @ Wq.T, xn @ Wk.T, xn @ Wv.T
    if PERHEAD_QK:
        q = rms(q.view(T, nH, hd), gq); k = rms(k.view(T, nKV, hd), gk)
    else:
        q = rms(q, gq).view(T, nH, hd); k = rms(k, gk).view(T, nKV, hd)
    v = v.view(T, nKV, hd)
    fr = torch.outer(torch.arange(T).float(), inv); emb = torch.cat([fr, fr], -1)
    c, s = emb.cos()[:, None], emb.sin()[:, None]
    q, k = q * c + rot(q) * s, k * c + rot(k) * s
    rep = nH // nKV
    k, v = k.repeat_interleave(rep, 1), v.repeat_interleave(rep, 1)
    A = torch.einsum("thd,shd->hts", q, k) / hd ** 0.5
    A = A + torch.triu(torch.full((T, T), float("-inf")), 1)
    A = torch.softmax(A, -1)                                         # [h, t, s]
    OV = torch.einsum("shd,hdo->hso", v, Wo.T.view(nH, hd, d))        # per head per source: Wo_h v_h[s]  [h,s,d]
    eye = torch.eye(T, dtype=torch.bool); sub = torch.diag(torch.ones(T - 1, dtype=torch.bool), -1)
    a_self = torch.einsum("hts,hso->to", A * eye, OV)
    a_prev = torch.einsum("hts,hso->to", A * sub, OV)
    a_all = torch.einsum("hts,hso->to", A, OV)
    a_oth = a_all - a_self - a_prev
    r = x + a_all
    sc = torch.rsqrt(r.pow(2).mean(-1, keepdim=True) + eps)
    h = r * sc * g_post
    comps = {"emb": x * sc * g_post, "a_self": a_self * sc * g_post, "a_prev": a_prev * sc * g_post,
             "a_oth": a_oth * sc * g_post}
    att = torch.stack([(A * sub).sum(-1), (A * eye).sum(-1), A[:, :, 0]], 0)  # [3, h, t]
    return h, comps, att, (x.norm(dim=-1), a_all.norm(dim=-1), a_prev.norm(dim=-1))


tok = AutoTokenizer.from_pretrained(hf)
FLORES = "/home/xiang/mechpop_cache/flores200/flores200_dataset"
langs = meta["langs"]
gen = torch.Generator().manual_seed(1853)
ROUT = {"T": G}
for j in range(3):
    Q, R = torch.linalg.qr(torch.randn(d, d, generator=gen, dtype=torch.float64))
    ROUT[f"R{j}"] = G @ (Q * torch.sign(torch.diagonal(R))).float()
CN = ["emb", "a_self", "a_prev", "a_oth"]
recs = {r: {"top1": [], **{f"abl_{c}": [] for c in CN}} for r in ROUT}
var = {r: {c: 0.0 for c in CN + ["all"]} for r in ROUT}
mean_c = None
cur_all, prev_all, lang_all, pos_all, attn_acc, norms = [], [], [], [], [], []
# pass 1: means of components (needed for mean-replacement ablation) -> two passes over the data
seqs = {lg: [tok(s.rstrip("\n"), add_special_tokens=False)["input_ids"]
             for s in open(f"{FLORES}/dev/{lg}.dev", encoding="utf-8").readlines()[:meta["n_sent"]]] for lg in langs}
NS_MAX = int(os.environ.get("NSENT", "997"))
with torch.no_grad():
    S = {c: torch.zeros(d) for c in CN}; n = 0
    for lg in langs:
        for ids in seqs[lg][:NS_MAX]:
            _, comps, _, _ = layer0(torch.tensor(ids))
            for c in CN:
                S[c] += comps[c].sum(0)
            n += len(ids)
    mean_c = {c: S[c] / n for c in CN}
    print("pass1 tokens", n, flush=True)
    # validation against toksub layer 0
    tid = np.load(os.path.expanduser(f"~/mechpop_cache/atlas_e185/toksub_ids_{key}.npz"))
    X0 = np.load(f"{base}/toksub.npy", mmap_mode="r")[0]
    chk = np.where(tid["sid"] < min(NS_MAX, 40))[0][:400]
    cos, agree = [], []
    for r in chk:
        ids = seqs[langs[tid["lang"][r]]][tid["sid"][r]]
        h, _, _, _ = layer0(torch.tensor(ids))
        hv = h[tid["pos"][r]]; ref = torch.from_numpy(np.asarray(X0[r], np.float32))
        cos.append(float(torch.nn.functional.cosine_similarity(hv, ref, 0)))
        agree.append(int((G @ hv).argmax() == (G @ ref).argmax()))
    val = {"n": len(chk), "cos_min": min(cos), "cos_mean": float(np.mean(cos)), "top1_agree": float(np.mean(agree))}
    print("validation", val, flush=True)
    for li, lg in enumerate(langs):
        for ids in seqs[lg][:NS_MAX]:
            t = torch.tensor(ids)
            h, comps, att, nr = layer0(t)
            cur_all.append(np.array(ids)); prev_all.append(np.r_[-1, ids[:-1]]); lang_all.append(np.full(len(ids), li))
            pos_all.append(np.arange(len(ids)))
            attn_acc.append(att[:, :, 1:].sum(-1).numpy() if len(ids) > 1 else np.zeros(att.shape[:2]))
            norms.append(torch.stack(nr, 1)[1:].numpy())
            for rn, Wr in ROUT.items():
                z = h @ Wr.T
                recs[rn]["top1"].append(z.argmax(-1).numpy().astype(np.int16))
                zc = {c: comps[c] @ Wr.T for c in CN}
                zm = {c: mean_c[c] @ Wr.T for c in CN}
                for c in CN:
                    recs[rn][f"abl_{c}"].append((z - zc[c] + zm[c]).argmax(-1).numpy().astype(np.int16))
                    var[rn][c] += float(((zc[c] - zm[c]) ** 2).sum())
                var[rn]["all"] += float(((z - z.mean(0)) ** 2).sum())
        print("done", lg, flush=True)

cur, prev, lng, pos = map(np.concatenate, (cur_all, prev_all, lang_all, pos_all))
ntok_pos1 = int((pos > 0).sum())
attn = np.sum(attn_acc, 0) / ntok_pos1                 # [3, h] mean over tokens with pos > 0
nrm = np.concatenate(norms)
rng = np.random.default_rng(185)


def mi(e, x, m):
    e = e[m].astype(np.int64); X = pool_rare(dense(x[m]))
    He, HX = H_keys(e), H_keys(X)
    I = He + HX - H_keys(X * E + e)
    fl = np.mean([He + HX - H_keys(rng.permutation(X) * E + e) for _ in range(3)])
    return float(I - fl), He


res = {"validation": val, "n_tokens": int(cur.size), "attn_prev_self_pos0_per_head": attn.round(4).tolist(),
       "norm_emb_attn_attnprev_mean": nrm.mean(0).tolist(), "routers": {}}
m_all = pos > 0
m_eng = m_all & (lng == 0)
for rn in ROUT:
    top1 = np.concatenate(recs[rn]["top1"])
    out = {"var_share": {c: var[rn][c] / var[rn]["all"] for c in CN}}
    out["top1_changed_by_mean_ablation"] = {c: float((np.concatenate(recs[rn][f"abl_{c}"])[m_all] != top1[m_all]).mean())
                                            for c in CN}
    for tag, m in [("all", m_all), ("eng", m_eng)]:
        icur, He = mi(top1, cur, m); iprev, _ = mi(top1, prev, m)
        out[f"share_{tag}"] = {"cur": icur / He, "prev": iprev / He, "H": He}
    res["routers"][rn] = out
    print(rn, json.dumps(out), flush=True)
rr = [res["routers"][f"R{j}"] for j in range(3)]
res["R_mean"] = {"var_share": {c: float(np.mean([r["var_share"][c] for r in rr])) for c in CN},
                 "top1_changed_by_mean_ablation": {c: float(np.mean([r["top1_changed_by_mean_ablation"][c] for r in rr]))
                                                   for c in CN},
                 **{f"share_{t}": {k: float(np.mean([r[f"share_{t}"][k] for r in rr])) for k in ["cur", "prev", "H"]}
                    for t in ["all", "eng"]}}
json.dump(res, open(os.path.expanduser(f"~/mechpop_cache/atlas_e185/resid/l0_{key}.json"), "w"), indent=1)
print("R_mean", json.dumps(res["R_mean"]))
