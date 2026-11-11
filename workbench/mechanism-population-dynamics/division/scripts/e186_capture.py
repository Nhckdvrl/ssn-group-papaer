#!/usr/bin/env python3
"""E186 capture (card: division/experiments/E186-atlas-capture-breadth.md). Generalises e184_capture.py / e180_capture.py
(those scripts untouched) to more MoE families, multi-GPU placement, routed-only experts (DeepSeek shared experts are
not routed and are not recorded), and the enriched store requested by E185.

Corpora (one sequence each, add_special_tokens=False):
  FLORES-200 dev, 21 sides: the 20 E180 sides (srp_Latn = e180_translit.py output) + eng_Latn (side 20; the E184
  English corpus); 997 sentences per side.   UD English EWT dev+test passages (<= 400 words; gold UPOS on word-final
  token; same rules as E184).
Calibration (N_B bias refit only) on random subsets of the MEASUREMENT sequences (补登记 11-09 22:20, after the smoke:
one bias fitted on the pooled corpus left the English subset at load TV .46-.73, so there are two calibrations):
  N_B   : bias refit to T's loads on the 20 non-English FLORES sides (seed 186, >= --cal-tokens)   -> multilingual view
  N_Ben : the SAME N1 matrices, bias refit on FLORES eng + UD (seed 1186, >= --cal-en-tokens)       -> English view
Routers on the same hidden states: T | N_A (Haar O(d) rotation of W, 8) | N_B (N1 = W_c V Q V^T, 8) | N_Ben (8).
Router index 0 T | N_A 1..D | N_B D+1..2D | N_Ben 2D+1..3D.  RNG per MoE layer j:
torch.Generator().manual_seed(186000 + j), draw order N_A then N_B.
Saved in --out:
  topk.npy   uint8   [L, NTOK, NR, K]  top-k expert ids, descending ([..., 0] = top-1); routed experts only
  topv.npy   float16 [L, NTOK, NR, K]  the matching top-k router logits (W h + b; T: the model's own logits)
  lse.npy    float16 [L, NTOK, NR]     logsumexp over all E logits (softmax gate = exp(topv - lse))
  topk_fix.npy uint8 [L, NTOK, 2, K]  N_F: two FIXED Gaussian routers (seed 186500 + j, independent of the model's
                                       weights, no bias) -- the same matrices for every checkpoint of one architecture;
                                       null for the training-time saturation readout (bridge B3)
  wT.npy     float32 [L, E, d]         the trained router weights (readout-subspace geometry)
  hmean.npy  float16 [L, NSEQ, d]      per-sequence mean of the router input h (geometry readouts, E179 G1/G2 style)
  tokmeta.npz  corpus (0 FLORES, 1 UD), side (-1 for UD), sid (sentence / passage id), seq (global), pos, inp,
               pred (lm_head argmax), nxt (true next id, -1 at sequence end), pent (prediction entropy, bits, fp16),
               nxt_lp (log2 p(true next), fp16; nan at end), upos (-1 unless UD word-final), word
  diag.npz   det_exact [L], hook_fp32 [L], t_vs_model [L], loadtv_B_cal [L, D], load_meas [L, 3, NR, E]
             (slot counts over: 0 FLORES non-English sides, 1 FLORES eng, 2 UD), cal_maxload [L, NR]
  meta.json  incl. moe_layers (model layer index of every stored layer), sides, upos, router_index, revision.
"""
import argparse, json, os, sys, time
import numpy as np
import torch
import torch.nn.functional as F

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import moe_measure as mm  # noqa: E402
from ud_passages import sentences  # noqa: E402

# E186_DATA: node-local copy of the three corpus folders (NFS stalled on 11-10 00:00); default = the NFS originals
_DR = os.environ.get("E186_DATA")
FLORES = f"{_DR}/flores200_dataset" if _DR else "/home/xiang/mechpop_cache/flores200/flores200_dataset"
SRP_LATN = f"{_DR}/srp_Latn" if _DR else "/home/xiang/mechpop_cache/e180/srp_Latn"
UD = f"{_DR}/lingdata" if _DR else "/home/xiang/mechpop_cache/lingdata"
UPOS = ["ADJ", "ADP", "ADV", "AUX", "CCONJ", "DET", "INTJ", "NOUN", "NUM", "PART", "PRON", "PROPN", "PUNCT",
        "SCONJ", "SYM", "VERB", "X"]
GROUPS = {"slavic": ["srp_Cyrl", "srp_Latn", "hrv_Latn", "bos_Latn", "slv_Latn", "ces_Latn", "pol_Latn",
                     "mkd_Cyrl", "bul_Cyrl", "ukr_Cyrl", "rus_Cyrl"],
          "indic": ["hin_Deva", "urd_Arab", "npi_Deva", "mar_Deva", "snd_Arab", "pes_Arab"],
          "chinese": ["zho_Hans", "zho_Hant", "yue_Hant"]}
SIDES = [x for g in GROUPS.values() for x in g] + ["eng_Latn"]
MAX_WORDS = 400

ap = argparse.ArgumentParser()
ap.add_argument("--model-path", required=True, help="local snapshot dir (or HF repo id)")
ap.add_argument("--key", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--attn", default="sdpa")
ap.add_argument("--draws", type=int, default=8)
ap.add_argument("--cal-tokens", type=int, default=60000)
ap.add_argument("--cal-en-tokens", type=int, default=40000)
ap.add_argument("--batch-tokens", type=int, default=16384)
ap.add_argument("--n-sent", type=int, default=997)
ap.add_argument("--n-ud", type=int, default=0, help="0 = all UD passages")
ap.add_argument("--smoke", action="store_true", help="20 sentences per side, 8 UD passages, 3k calibration tokens")
ap.add_argument("--tiny", action="store_true", help="architecture check: random-init model from config with 2 MoE "
                "layers (+ dense first layers) and small width; numbers meaningless")
args = ap.parse_args()
if args.smoke or args.tiny:
    args.n_sent, args.n_ud, args.cal_tokens, args.cal_en_tokens = 20, 8, 3000, 2000
os.makedirs(args.out, exist_ok=True)
D = args.draws
NR = 1 + 3 * D
t0 = time.time()


def log(*a):
    print(f"[{time.strftime('%H:%M:%S')} +{time.time() - t0:7.1f}s]", *a, flush=True)


def read_side(split, lang, n):
    path = f"{SRP_LATN}/{split}/srp_Latn.{split}" if lang == "srp_Latn" else f"{FLORES}/{split}/{lang}.{split}"
    with open(path, encoding="utf-8") as f:
        return [x.rstrip("\n") for x in f][:n]


def ud_build():
    """identical to e184_capture.ud_build."""
    passages, words = [], []
    for name in ("dev", "test"):
        cur = None
        for newdoc, text, toks in sentences(f"{UD}/en_ewt-ud-{name}.conllu"):
            if cur is None or newdoc or cur["n"] + len(toks) > MAX_WORDS:
                if cur and cur["text"]:
                    passages.append(cur)
                cur = {"text": "", "n": 0, "w": []}
            base = len(cur["text"]) + (1 if cur["text"] else 0)
            pos = 0
            for form, upos, _, kind in toks:
                if kind == "part":
                    continue
                k = text.find(form, pos)
                if k < 0:
                    break
                if kind == "word":
                    cur["w"].append((base + k, base + k + len(form), upos))
                pos = k + len(form)
            cur["text"] = (cur["text"] + " " + text) if cur["text"] else text
            cur["n"] += len(toks)
        if cur and cur["text"]:
            passages.append(cur)
    texts, words = [], []
    for pid, p in enumerate(passages):
        texts.append(p["text"])
        for s, e, u in p["w"]:
            words.append((pid, s, e, u))
    return texts, words


from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer  # noqa: E402
tok = AutoTokenizer.from_pretrained(args.model_path)
assert tok.is_fast

# ---------------------------------------------------------- corpora
SEQS, CORP, SIDE, SID = [], [], [], []
for si, lg in enumerate(SIDES):
    for j, s in enumerate(read_side("dev", lg, args.n_sent)):
        SEQS.append(tok(s, add_special_tokens=False)["input_ids"]); CORP.append(0); SIDE.append(si); SID.append(j)
NFL = len(SEQS)
ud_texts, ud_words = ud_build()
if args.n_ud:
    ud_texts = ud_texts[:args.n_ud]
    ud_words = [w for w in ud_words if w[0] < args.n_ud]
by_pid = {}
for wi, (pid, s, e, u) in enumerate(ud_words):
    by_pid.setdefault(pid, []).append((wi, s, e, u))
ud_upos, ud_word = [], []
n_wf = n_bad = n_coll = 0
for pid, text in enumerate(ud_texts):
    enc = tok(text, add_special_tokens=False, return_offsets_mapping=True)
    ids, offs = enc["input_ids"], enc["offset_mapping"]
    up = np.full(len(ids), -1, np.int32)
    wd = np.full(len(ids), -1, np.int32)
    for wi, s, e, u in by_pid.get(pid, []):
        hit = -1
        for t, (a, b) in enumerate(offs):
            if a <= e - 1 < b:
                hit = t if b <= e else -1
                break
        if hit < 0:
            n_bad += 1
            continue
        if up[hit] >= 0:
            n_coll += 1
        up[hit] = UPOS.index(u)
        wd[hit] = wi
        n_wf += 1
    SEQS.append(ids); CORP.append(1); SIDE.append(-1); SID.append(pid)
    ud_upos.append(up); ud_word.append(wd)
NSEQ = len(SEQS)
lens = np.array([len(x) for x in SEQS])
assert lens.min() > 0
off = np.concatenate([[0], np.cumsum(lens)])
NTOK = int(off[-1])
SIDE_A, CORP_A = np.array(SIDE), np.array(CORP)
ntok_side = {lg: int(lens[SIDE_A == i].sum()) for i, lg in enumerate(SIDES)}
ntok_side["ud"] = int(lens[CORP_A == 1].sum())
META = {"corpus": np.repeat(CORP_A.astype(np.int8), lens), "side": np.repeat(SIDE_A.astype(np.int8), lens),
        "sid": np.repeat(np.array(SID, np.int32), lens), "seq": np.repeat(np.arange(NSEQ, dtype=np.int32), lens),
        "pos": np.concatenate([np.arange(n, dtype=np.int32) for n in lens]),
        "inp": np.concatenate([np.array(x, np.int64) for x in SEQS]),
        "pred": np.zeros(NTOK, np.int64),
        "nxt": np.concatenate([np.array(x[1:] + [-1], np.int64) for x in SEQS]),
        "pent": np.zeros(NTOK, np.float16), "nxt_lp": np.full(NTOK, np.nan, np.float16),
        "upos": np.concatenate([np.full(len(x), -1, np.int32) for x in SEQS[:NFL]] + ud_upos),
        "word": np.concatenate([np.full(len(x), -1, np.int32) for x in SEQS[:NFL]] + ud_word)}
# token group for the load diagnostics: 0 FLORES non-English, 1 FLORES eng, 2 UD
GRP = np.where(META["corpus"] == 1, 2, np.where(META["side"] == SIDES.index("eng_Latn"), 1, 0)).astype(np.int64)
# calibration subsets = random measurement sequences until >= the token target (ML: 20 non-English sides; EN: eng + UD)


def cal_subset(pool, ntok, seed):
    perm = np.random.default_rng(seed).permutation(pool)
    return np.sort(perm[:int(np.searchsorted(np.cumsum(lens[perm]), ntok)) + 1])


ENG = SIDES.index("eng_Latn")
CAL_ML = cal_subset(np.where((CORP_A == 0) & (SIDE_A != ENG))[0], args.cal_tokens, 186)
CAL_EN = cal_subset(np.where((CORP_A == 1) | (SIDE_A == ENG))[0], args.cal_en_tokens, 1186)
CAL_SEQ = np.concatenate([CAL_ML, CAL_EN])
log(f"sequences {NSEQ} (FLORES {NFL} = {len(SIDES)} sides x {args.n_sent}, UD {NSEQ - NFL}); tokens {NTOK}; "
    f"per side {ntok_side}; UD words {len(ud_words)}, word-final {n_wf}, past end {n_bad}, collisions {n_coll}; "
    f"calibration ML {len(CAL_ML)} seqs / {int(lens[CAL_ML].sum())} tokens, EN {len(CAL_EN)} / {int(lens[CAL_EN].sum())}")

# ---------------------------------------------------------- model
log("loading model", args.model_path)
cfg = AutoConfig.from_pretrained(args.model_path)
if args.tiny:
    for k, v in dict(hidden_size=256, intermediate_size=512, moe_intermediate_size=128, num_attention_heads=2,
                     num_key_value_heads=1, head_dim=128).items():
        if hasattr(cfg, k) and not (k in ("head_dim", "num_key_value_heads") and cfg.model_type == "deepseek_v2"):
            setattr(cfg, k, v)
    cfg.num_hidden_layers = 2 + getattr(cfg, "first_k_dense_replace", 0)
    if cfg.model_type == "deepseek_v2":
        cfg.num_key_value_heads = cfg.num_attention_heads
    torch.manual_seed(0)
    model = AutoModelForCausalLM.from_config(cfg, dtype=torch.bfloat16, attn_implementation=args.attn).to("cuda:0")
else:
    model = AutoModelForCausalLM.from_pretrained(args.model_path, dtype=torch.bfloat16, device_map="auto",
                                                 attn_implementation=args.attn)
model.eval()
ARCH = cfg.model_type
GATES, MOE_LAYERS = [], []
for li, ly in enumerate(model.model.layers):
    blk = getattr(ly, "block_sparse_moe", None) or getattr(ly, "mlp", None)
    g = getattr(blk, "gate", None)
    if g is not None and hasattr(g, "weight"):
        GATES.append(g); MOE_LAYERS.append(li)
DSV2 = ARCH in ("deepseek_v2",)
if DSV2:
    assert cfg.topk_method == "greedy" and getattr(cfg, "scoring_func", "softmax") == "softmax", cfg.topk_method
    assert all(getattr(g, "bias", None) is None for g in GATES)
L = len(GATES)
E, d = GATES[0].weight.shape
K = cfg.num_experts_per_tok
assert E <= 255
DEV = [g.weight.device for g in GATES]
INDEV = model.model.embed_tokens.weight.device
HASBIAS = getattr(GATES[0], "bias", None) is not None
assert not HASBIAS, "no E186 model has a router bias; add handling before using one"
SHARED = int(getattr(cfg, "n_shared_experts", 0) or 0)
log(f"loaded {ARCH}: layers {len(model.model.layers)}, MoE layers {L} (first {MOE_LAYERS[0]}), E={E} (routed; shared "
    f"{SHARED}, not recorded) d={d} K={K} NR={NR}; devices {sorted(set(str(x) for x in DEV))}; "
    f"mem {[round(torch.cuda.memory_allocated(i) / 2**30, 1) for i in range(torch.cuda.device_count())]} GiB")

TOPK = np.zeros((L, NTOK, NR, K), np.uint8)
NF = 2
TOPKF = np.zeros((L, NTOK, NF, K), np.uint8)
WF = []
for j in range(L):
    gf = torch.Generator().manual_seed(186500 + j)
    WF.append((torch.randn(NF * E, d, generator=gf) / d ** 0.5).to(DEV[j]))
TOPV = np.zeros((L, NTOK, NR, K), np.float16)
LSE = np.zeros((L, NTOK, NR), np.float16)
HSUM = [torch.zeros(NSEQ, d, dtype=torch.float32, device=DEV[j]) for j in range(L)]
LOAD = [torch.zeros(3, NR, E, dtype=torch.float64, device=DEV[j]) for j in range(L)]
HOOK = torch.zeros(L, 3, dtype=torch.float64)


def batches(idx):
    order = sorted(idx, key=lambda i: len(SEQS[i]))
    cur = []
    for i in order:
        if cur and (len(cur) + 1) * len(SEQS[i]) > args.batch_tokens:
            yield cur
            cur = []
        cur.append(i)
    if cur:
        yield cur


def make_inputs(b):
    T = max(len(SEQS[i]) for i in b)
    ids = torch.full((len(b), T), tok.pad_token_id or 0, dtype=torch.long)
    am = torch.zeros((len(b), T), dtype=torch.long)
    for r, i in enumerate(b):
        ids[r, :len(SEQS[i])] = torch.tensor(SEQS[i])
        am[r, :len(SEQS[i])] = 1
    return ids.to(INDEV), am.to(INDEV)


ST = {"mode": None}
CAL_H = {"ml": [[] for _ in range(L)], "en": [[] for _ in range(L)]}
DET = {}
WALL, BALL = [None] * L, [None] * L


def on(dv, key):
    """per-device cached copy of a batch tensor stored in ST[key]."""
    c = ST.setdefault("_dev", {})
    if (key, dv) not in c:
        c[(key, dv)] = ST[key].to(dv)
    return c[(key, dv)]


def t_logits_sel(mod, h, out, m):
    """T logits (float32, exactly as the model computes them up to dtype) and the model's selected set."""
    if DSV2:  # DeepseekV2MoEGate: fp32 linear, softmax, greedy top-k (sorted=False) -> returns (idx, weight)
        lt = F.linear(h.float(), mod.weight.float())
        sel = out[0].reshape(-1, K)[m]
    else:     # nn.Linear gate (OLMoE / Mixtral / Phimoe sparsemixer: inference selection = top-2 of the logits)
        lt = out.reshape(-1, E)[m].float()
        sel = lt.topk(K, -1).indices
    return lt, sel


def make_hook(j):
    def hook(mod, inp, out):
        mode = ST["mode"]
        if mode is None:
            return
        dv = DEV[j]
        m = on(dv, "mask")
        h = inp[0].reshape(-1, d)[m]
        if mode == "cal":
            CAL_H[ST["calgrp"]][j].append(h.detach().to("cpu"))
            return
        lt, Smod = t_logits_sel(mod, h, out, m)
        if mode == "det":
            DET.setdefault(j, []).append(Smod.sort(-1).values.cpu())
            return
        hf = h.float()
        n = hf.shape[0]
        logits = torch.cat([lt, hf @ WALL[j].T + BALL[j]], 1).view(n, NR, E)
        V, S = logits.topk(K, -1)  # [n, NR, K]
        lse = torch.logsumexp(logits, -1)
        Sre = (hf @ mod.weight.float().T).topk(K, -1).indices
        ohm = torch.zeros(n, E, device=dv).scatter_(1, Smod, 1.0)
        HOOK[j, 0] += float(ohm.gather(1, Sre).sum() / K)
        HOOK[j, 1] += float(ohm.gather(1, S[:, 0]).sum() / K)
        HOOK[j, 2] += n
        TOPK[j, ST["gidx"]] = S.to(torch.uint8).cpu().numpy()
        TOPKF[j, ST["gidx"]] = (hf @ WF[j].T).view(n, NF, E).topk(K, -1).indices.to(torch.uint8).cpu().numpy()
        TOPV[j, ST["gidx"]] = V.half().cpu().numpy()
        LSE[j, ST["gidx"]] = lse.half().cpu().numpy()
        HSUM[j].index_add_(0, on(dv, "seq_t"), hf)
        oh = torch.zeros(n, NR, E, device=dv).scatter_(2, S, 1.0)
        LOAD[j].index_add_(0, on(dv, "grp_t"), oh.double())
    return hook


for j, g in enumerate(GATES):
    g.register_forward_hook(make_hook(j))


@torch.no_grad()
def run(b, mode, calgrp=None):
    ids, am = make_inputs(b)
    m = am.reshape(-1).bool()
    ST.clear()
    ST.update(mode=mode, mask=m, calgrp=calgrp)
    if mode == "meas":
        gidx = np.concatenate([np.arange(off[i], off[i + 1]) for i in b])
        ST["gidx"] = gidx
        ST["seq_t"] = torch.from_numpy(META["seq"][gidx].astype(np.int64))
        ST["grp_t"] = torch.from_numpy(GRP[gidx])
    hs = model.model(input_ids=ids, attention_mask=am, use_cache=False).last_hidden_state
    if mode == "meas":
        hs = hs.reshape(-1, hs.shape[-1])[m.to(hs.device)]
        nx = torch.from_numpy(META["nxt"][gidx]).to(hs.device)
        P, Hn, LP = [], [], []
        for i in range(0, hs.shape[0], 2048):
            lg = model.lm_head(hs[i:i + 2048]).float()
            lp = torch.log_softmax(lg, -1)
            P.append(lg.argmax(-1))
            Hn.append(-(lp.exp() * lp).sum(-1) / np.log(2))
            t = nx[i:i + 2048]
            LP.append(torch.where(t >= 0, lp.gather(1, t.clamp_min(0)[:, None])[:, 0] / np.log(2),
                                  torch.full_like(t, float("nan"), dtype=torch.float32)))
        META["pred"][gidx] = torch.cat(P).cpu().numpy()
        META["pent"][gidx] = torch.cat(Hn).cpu().numpy().astype(np.float16)
        META["nxt_lp"][gidx] = torch.cat(LP).cpu().numpy().astype(np.float16)
    ST["mode"] = None


# ---------------------------------------------------------- 1. calibration (subset of the measurement corpus)
log("calibration pass")
for g, seqs in (("ml", CAL_ML), ("en", CAL_EN)):
    for b in batches(seqs):
        run(b, "cal", g)
log("calibration captured", {g: sum(x.shape[0] for x in CAL_H[g][0]) for g in CAL_H}, "tokens/layer")

# ---------------------------------------------------------- 2. null routers
diag = {"loadtv_B_cal": np.zeros((L, D)), "loadtv_Ben_cal": np.zeros((L, D)), "cal_maxload": np.zeros((L, NR))}
for j in range(L):
    dv = DEV[j]
    Hc = torch.cat(CAL_H["ml"][j]).to(dv).double()
    He = torch.cat(CAL_H["en"][j]).to(dv).double()
    CAL_H["ml"][j] = CAL_H["en"][j] = None
    Wd = GATES[j].weight.detach().double()
    bT = torch.zeros(E, dtype=torch.float64, device=dv)
    target = mm.loads(mm.topk(Hc @ Wd.T + bT, K), E)
    target_en = mm.loads(mm.topk(He @ Wd.T + bT, K), E)
    st = mm.null_stats(Wd, Hc)   # readout basis V depends only on W (row-centred SVD); the stats' covariance is unused by N1
    gen = torch.Generator().manual_seed(186000 + j)
    WA, WB, bB, bBe = [], [], [], []
    for _ in range(D):
        A = torch.randn(d, d, generator=gen, dtype=torch.float64).to(dv)
        Q, R = torch.linalg.qr(A)
        WA.append(Wd @ (Q * torch.sign(torch.diagonal(R))))
        del A, Q, R
    for i in range(D):
        Q = mm.haar(st["V"].shape[1], gen).to(dv)
        Wn = mm.null_router(Wd, Hc, "N1", Q, st)
        bn = mm.fit_bias(Hc, Wn, K, target)
        lc = mm.loads(mm.topk(Hc @ Wn.T + bn, K), E)
        diag["loadtv_B_cal"][j, i] = float((lc / lc.sum() - target / target.sum()).abs().sum() / 2)
        be = mm.fit_bias(He, Wn, K, target_en)
        lc = mm.loads(mm.topk(He @ Wn.T + be, K), E)
        diag["loadtv_Ben_cal"][j, i] = float((lc / lc.sum() - target_en / target_en.sum()).abs().sum() / 2)
        WB.append(Wn); bB.append(bn); bBe.append(be)
    WALL[j] = torch.cat(WA + WB + WB).float().contiguous()
    BALL[j] = torch.cat([bT] * D + bB + bBe).float().contiguous()
    allW = torch.cat([Wd, WALL[j].double()]).view(NR, E, d)
    allb = torch.cat([bT, BALL[j].double()]).view(NR, E)
    for r in range(NR):
        lc = mm.loads(mm.topk((He if r > 2 * D else Hc) @ allW[r].T + allb[r], K), E)
        diag["cal_maxload"][j, r] = float(lc.max() / (K / E))
    del Hc, He, st, allW, WA, WB
    torch.cuda.empty_cache()
    if j % 8 == 0 or j == L - 1:
        log(f"nulls MoE layer {j}: loadtv_B_cal mean {diag['loadtv_B_cal'][j].mean():.4f} "
            f"max {diag['loadtv_B_cal'][j].max():.4f}; N_Ben {diag['loadtv_Ben_cal'][j].mean():.4f}")

# ---------------------------------------------------------- 3. determinism (same FLORES batch twice)
b0 = next(batches(range(args.n_sent)))
run(b0, "det")
run(b0, "det")
det = [float((DET[j][0] == DET[j][1]).all(-1).float().mean()) for j in range(L)]
log(f"determinism: exact-set agreement min {min(det):.4f}")

# ---------------------------------------------------------- 4. measurement
for name, idx in (("flores", range(NFL)), ("ud", range(NFL, NSEQ))):
    for bi, b in enumerate(batches(list(idx))):
        run(b, "meas")
        if bi % 50 == 0:
            log(f"  {name} batch {bi}")
    hk = HOOK.sum(0)
    log(f"measured {name}; hook fp32-vs-model {hk[0] / hk[2]:.5f} T-vs-model {hk[1] / hk[2]:.5f}")
assert int(HOOK[0, 2]) == NTOK, (int(HOOK[0, 2]), NTOK)

# ---------------------------------------------------------- 5. save
load = np.stack([x.cpu().numpy() for x in LOAD])           # [L, 3, NR, E]
tot = load.sum(1)                                             # [L, NR, E]
pT = tot[:, :1] / tot[:, :1].sum(-1, keepdims=True)
pR = tot / tot.sum(-1, keepdims=True)
tv_meas = 0.5 * np.abs(pR - pT).sum(-1)                      # [L, NR]
def tv_of(cnt):   # cnt [L, NR, E] -> TV of every router's load vs T's
    p = cnt / cnt.sum(-1, keepdims=True)
    return 0.5 * np.abs(p - p[:, :1]).sum(-1)


tv_ml, tv_en = tv_of(load[:, 0]), tv_of(load[:, 1] + load[:, 2])
tv_grp = 0.5 * np.abs(load / load.sum(-1, keepdims=True) - load[:, :, :1] / load[:, :, :1].sum(-1, keepdims=True)).sum(-1)
hmean = np.stack([(HSUM[j] / torch.from_numpy(lens).to(DEV[j], torch.float32)[:, None]).half().cpu().numpy()
                  for j in range(L)])
acc_eng = float((META["pred"] == META["nxt"])[(GRP == 1) & (META["nxt"] >= 0)].mean())
acc_all = float((META["pred"] == META["nxt"])[META["nxt"] >= 0].mean())
np.save(os.path.join(args.out, "topk.npy"), TOPK)
np.save(os.path.join(args.out, "topv.npy"), TOPV)
np.save(os.path.join(args.out, "lse.npy"), LSE)
np.save(os.path.join(args.out, "topk_fix.npy"), TOPKF)
np.save(os.path.join(args.out, "hmean.npy"), hmean)
np.save(os.path.join(args.out, "wT.npy"), np.stack([g.weight.detach().float().cpu().numpy() for g in GATES]))
np.savez(os.path.join(args.out, "tokmeta.npz"), **META)
hk = HOOK.numpy()
np.savez(os.path.join(args.out, "diag.npz"), det_exact=np.array(det), hook_fp32=hk[:, 0] / hk[:, 2],
         t_vs_model=hk[:, 1] / hk[:, 2], load_meas=load, tv_meas=tv_meas, tv_grp=tv_grp, tv_ml=tv_ml, tv_en=tv_en, **diag)
dl = os.path.join(args.model_path, "_download.json")
meta = {"model_path": args.model_path, "key": args.key, "arch": ARCH,
        "download": json.load(open(dl)) if os.path.exists(dl) else None,
        "draws": D, "K": K, "E": E, "L": L, "d": d, "moe_layers": MOE_LAYERS, "n_layers_total": len(model.model.layers),
        "n_shared_experts": SHARED, "routed_only": True,
        "router_index": {"T": [0], "N_A": [1, D], "N_B": [1 + D, 2 * D], "N_Ben": [1 + 2 * D, 3 * D]},
        "routers": ["T"] + [f"N_A{i}" for i in range(D)] + [f"N_B{i}" for i in range(D)] + [f"N_Ben{i}" for i in range(D)],
        "sides": SIDES, "groups": GROUPS, "upos": UPOS, "n_sent": args.n_sent, "ntok": NTOK, "ntok_side": ntok_side,
        "nseq": {"flores": NFL, "ud": NSEQ - NFL}, "ud_words": len(ud_words), "ud_word_final": n_wf,
        "ud_run_past_end": n_bad, "ud_collisions": n_coll,
        "cal": {"ml": {"n_seq": int(len(CAL_ML)), "n_tok": int(lens[CAL_ML].sum()), "seed": 186},
                "en": {"n_seq": int(len(CAL_EN)), "n_tok": int(lens[CAL_EN].sum()), "seed": 1186}},
        "hook_agreement_min": float((hk[:, 0] / hk[:, 2]).min()), "hook_agreement": float(hk[:, 0].sum() / hk[:, 2].sum()),
        "t_vs_model_min": float((hk[:, 1] / hk[:, 2]).min()), "det_exact_min": min(det),
        "loadtv_B_cal_mean": float(diag["loadtv_B_cal"].mean()), "loadtv_B_cal_max": float(diag["loadtv_B_cal"].max()),
        "loadtv_Ben_cal_mean": float(diag["loadtv_Ben_cal"].mean()), "loadtv_Ben_cal_max": float(diag["loadtv_Ben_cal"].max()),
        # measurement-corpus TV of each N_B family on the corpus it was calibrated for (N_B: 20 non-English sides;
        # N_Ben: eng + UD pooled), and every family on every group
        "loadtv_B_meas_mean": float(tv_ml[:, 1 + D:1 + 2 * D].mean()), "loadtv_B_meas_max": float(tv_ml[:, 1 + D:1 + 2 * D].max()),
        "loadtv_Ben_meas_mean": float(tv_en[:, 1 + 2 * D:].mean()), "loadtv_Ben_meas_max": float(tv_en[:, 1 + 2 * D:].max()),
        "loadtv_B_meas_grp_mean": [float(tv_grp[:, g, 1 + D:1 + 2 * D].mean()) for g in range(3)],
        "loadtv_Ben_meas_grp_mean": [float(tv_grp[:, g, 1 + 2 * D:].mean()) for g in range(3)],
        "next_token_acc_eng": acc_eng, "next_token_acc_all": acc_all,
        "smoke": args.smoke, "tiny": args.tiny, "wall_s": time.time() - t0, "host": os.uname().nodename,
        "attn": args.attn, "gpus": [torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())],
        "transformers": __import__("transformers").__version__, "torch": torch.__version__}
json.dump(meta, open(os.path.join(args.out, "meta.json"), "w"), indent=1)
log("done", json.dumps({k: meta[k] for k in ("hook_agreement_min", "t_vs_model_min", "det_exact_min",
                                             "loadtv_B_cal_mean", "loadtv_Ben_cal_mean", "loadtv_B_meas_mean",
                                             "loadtv_Ben_meas_mean", "loadtv_B_meas_grp_mean", "loadtv_Ben_meas_grp_mean",
                                             "next_token_acc_eng", "wall_s")}))
