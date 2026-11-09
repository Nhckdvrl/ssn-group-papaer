#!/usr/bin/env python3
"""E179 capture (card: division/experiments/E179-language-geometry-replication.md). Based on e178_capture.py.

Same FLORES-200 dev / 20 languages / routers as E178, for three MoEs (qwen3 | gptoss | olmoe), plus
  N_T   sharpness-matched null: s * (N_B logits incl. bias), s fit on calibration so the mean FULL-softmax entropy
        equals the trained router's (top-k selection unchanged by construction)
  N_Tk  same, matching the mean entropy of the top-k-renormalised softmax (supplementary)
and the hidden-state statistics for the direct geometry readouts G1-G3 (router inputs):
  sentmean.npy  float16 [L, NU, d]  per-(language, sentence) mean of the router input
  toksub.npy    float16 [L, 20000, d] token subsample (1000 per language, uniform without replacement, seed 179)
Router index layout: 0 T | N_A 1..D | N_B D+1..2D | N_G 2D+1..3D | N_T 3D+1..4D | N_Tk 4D+1..5D.
"""
import argparse, json, math, os, sys, time
import numpy as np
import torch
import torch.nn.functional as F

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import moe_measure as mm  # noqa: E402

LANGS = ["eng_Latn", "arb_Arab", "asm_Beng", "bam_Latn", "ben_Beng", "fra_Latn", "hin_Deva", "lit_Latn",
         "ory_Orya", "pes_Arab", "srp_Cyrl", "tha_Thai", "zho_Hans",
         "deu_Latn", "spa_Latn", "jpn_Jpan", "kor_Hang", "swh_Latn",
         "rus_Cyrl", "tam_Taml"]
FLORES = "/home/xiang/mechpop_cache/flores200/flores200_dataset"
MODELS = {"qwen3": ("Qwen/Qwen3-30B-A3B", "sdpa"),
          "gptoss": ("openai/gpt-oss-20b", "eager"),
          "olmoe": ("allenai/OLMoE-1B-7B-0125-Instruct", "sdpa")}

ap = argparse.ArgumentParser()
ap.add_argument("--model", required=True, choices=list(MODELS))
ap.add_argument("--out", required=True)
ap.add_argument("--n-sent", type=int, default=997)
ap.add_argument("--n-cal", type=int, default=25)
ap.add_argument("--draws", type=int, default=8)
ap.add_argument("--batch-tokens", type=int, default=16384)
ap.add_argument("--tok-per-lang", type=int, default=1000)
ap.add_argument("--langs", default=",".join(LANGS))
args = ap.parse_args()
os.makedirs(args.out, exist_ok=True)
langs = args.langs.split(",")
assert langs[0] == "eng_Latn"
NL, NS, D = len(langs), args.n_sent, args.draws
NU = NL * NS
MODEL, ATTN = MODELS[args.model]
GPTOSS = args.model == "gptoss"
dev = torch.device("cuda")
t0 = time.time()


def log(*a):
    print(f"[{time.strftime('%H:%M:%S')} +{time.time() - t0:7.1f}s]", *a, flush=True)


def read(split, lang, n):
    with open(f"{FLORES}/{split}/{lang}.{split}", encoding="utf-8") as f:
        return [x.rstrip("\n") for x in f][:n]


from transformers import AutoModelForCausalLM, AutoTokenizer  # noqa: E402
tok = AutoTokenizer.from_pretrained(MODEL)
log("loading model", MODEL)
model = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.bfloat16, device_map={"": 0}, attn_implementation=ATTN)
model.eval()
layers = model.model.layers
gates = [ly.mlp.router if GPTOSS else ly.mlp.gate for ly in layers]
L, E, d = len(gates), gates[0].weight.shape[0], gates[0].weight.shape[1]
K = model.config.num_experts_per_tok
NR = 1 + 5 * D
log(f"loaded: L={L} E={E} d={d} K={K} NR={NR}; mem {torch.cuda.memory_allocated() / 2**30:.1f} GiB; "
    f"gate dtype {gates[0].weight.dtype}; bias {getattr(gates[0], 'bias', None) is not None}")

enc = lambda ss: [tok(s, add_special_tokens=False)["input_ids"] for s in ss]
meas = {lg: enc(read("dev", lg, NS)) for lg in langs}
cal = [ids for lg in langs for ids in enc(read("devtest", lg, args.n_cal))]
ntok_meas = {lg: int(sum(len(x) for x in v)) for lg, v in meas.items()}
log("tokens per language:", ntok_meas, "cal tokens", sum(len(x) for x in cal))

# token subsample: per language, tok_per_lang global token positions -> {sid: [(pos, row)]}
rs = np.random.default_rng(179)
TSEL = []
NTS = args.tok_per_lang * NL
row = 0
for li, lg in enumerate(langs):
    lens = np.array([len(x) for x in meas[lg]])
    off = np.concatenate([[0], np.cumsum(lens)])
    pick = np.sort(rs.choice(off[-1], args.tok_per_lang, replace=False))
    dct = {}
    for g in pick:
        sid = int(np.searchsorted(off, g, side="right") - 1)
        dct.setdefault(sid, []).append((int(g - off[sid]), row))
        row += 1
    TSEL.append(dct)
tsel_lang = np.repeat(np.arange(NL), args.tok_per_lang)
tsel_sid = np.zeros(NTS, np.int32)
for li in range(NL):
    for sid, lst in TSEL[li].items():
        for _, r in lst:
            tsel_sid[r] = sid


def batches(seqs, idx):
    order = sorted(idx, key=lambda i: len(seqs[i]))
    cur = []
    for i in order:
        if cur and (len(cur) + 1) * len(seqs[i]) > args.batch_tokens:
            yield cur
            cur = []
        cur.append(i)
    if cur:
        yield cur


def make_inputs(seqs, b):
    T = max(len(seqs[i]) for i in b)
    ids = torch.full((len(b), T), tok.pad_token_id or 0, dtype=torch.long)
    am = torch.zeros((len(b), T), dtype=torch.long)
    for r, i in enumerate(b):
        ids[r, :len(seqs[i])] = torch.tensor(seqs[i])
        am[r, :len(seqs[i])] = 1
    return ids.to(dev), am.to(dev)


# ------------------------------------------------------------------ hook state
ST = {"mode": None}
CAL_H = [[] for _ in range(L)]
DET = {}
WALL, BALL = [None] * L, [None] * L
counts = torch.zeros(L, NR, NL, E, dtype=torch.int64, device=dev)
SEL4 = torch.tensor([0, 1, 1 + D, 1 + 2 * D], device=dev)
persent = torch.zeros(L, NU * 4 * E, dtype=torch.int32, device=dev)
QENG = torch.zeros(L, NS, NR * E, dtype=torch.float32, device=dev)
DIV = torch.zeros(NL, NS, L, NR, dtype=torch.float32, device=dev)
SENT = np.zeros((L, NU, d), np.float32)
TOKS = np.zeros((L, NTS, d), np.float16)
hookchk = torch.zeros(3, dtype=torch.float64)  # fp32-recompute vs model selection overlap; T-logits vs model; n
LOGE = math.log(E)


def ent(q):
    return -(q * q.clamp_min(1e-30).log()).sum(-1)


def model_sel(out, m):
    """The model's own top-k selection for the masked tokens."""
    if GPTOSS:
        return out[1].reshape(-1, K)[m]
    return out.reshape(-1, E)[m].float().topk(K, -1).indices


def t_logits(mod, inp, out, m):
    if GPTOSS:  # same op / dtype as GptOssTopKRouter.forward
        return F.linear(inp[0].reshape(-1, d), mod.weight, mod.bias)[m].float()
    return out.reshape(-1, E)[m].float()


def make_hook(l):
    def hook(mod, inp, out):
        mode = ST["mode"]
        if mode is None:
            return
        m = ST["mask"]
        h = inp[0].reshape(-1, d)[m]
        if mode == "cal":
            CAL_H[l].append(h.detach().to("cpu"))
            return
        if mode == "det":
            DET.setdefault(l, []).append(model_sel(out, m).sort(-1).values.cpu())
            return
        lt = t_logits(mod, inp, out, m)
        hf = h.float()
        n = hf.shape[0]
        logits = torch.cat([lt, hf @ WALL[l].T + BALL[l]], 1).view(n, NR, E)
        S = logits.topk(K, -1).indices
        Smod = model_sel(out, m)
        bT = mod.bias.float() if GPTOSS else 0.0
        Sre = (hf @ mod.weight.float().T + bT).topk(K, -1).indices
        ohm = torch.zeros(n, E, device=dev).scatter_(1, Smod, 1.0)
        hookchk[0] += float(ohm.gather(1, Sre).sum() / K)
        hookchk[1] += float(ohm.gather(1, S[:, 0]).sum() / K)
        hookchk[2] += n
        li = ST["lang"]
        flat = (torch.arange(NR, device=dev)[None, :, None] * E + S).reshape(-1)
        counts[l, :, li] += torch.bincount(flat, minlength=NR * E).view(NR, E)
        u = ST["unit"]
        f4 = ((u[:, None, None] * 4 + torch.arange(4, device=dev)[None, :, None]) * E + S[:, SEL4]).reshape(-1)
        persent[l].scatter_add_(0, f4, torch.ones_like(f4, dtype=torch.int32))
        P = torch.softmax(logits, -1).view(n, NR * E)
        B = ST["nseq"]
        Qs = torch.zeros(B, NR * E, device=dev).index_add_(0, ST["seq"], P) / ST["lens"][:, None]
        sids = ST["sids"]
        if li == 0:
            QENG[l, sids] = Qs
        else:
            q1 = QENG[l, sids].view(B, NR, E)
            q2 = Qs.view(B, NR, E)
            mq = 0.5 * (q1 + q2)
            js = 0.5 * (q1 * (q1.clamp_min(1e-30) / mq.clamp_min(1e-30)).log()).sum(-1) + \
                0.5 * (q2 * (q2.clamp_min(1e-30) / mq.clamp_min(1e-30)).log()).sum(-1)
            Fn = LOGE - 0.5 * (ent(q1) + ent(q2))
            DIV[li, sids, l] = js / Fn
        # geometry statistics
        Hs = torch.zeros(B, d, device=dev).index_add_(0, ST["seq"], hf) / ST["lens"][:, None]
        SENT[l, ST["units_np"]] = Hs.cpu().numpy()
        if ST["tidx"] is not None:
            TOKS[l, ST["trows"]] = hf[ST["tidx"]].half().cpu().numpy()
    return hook


for l, g in enumerate(gates):
    g.register_forward_hook(make_hook(l))


@torch.no_grad()
def run(seqs, b, mode, lang=0, sids=None):
    ids, am = make_inputs(seqs, b)
    m = am.reshape(-1).bool()
    ST.update(mode=mode, mask=m, lang=lang)
    if mode == "meas":
        Bn, T = am.shape
        rows = torch.arange(Bn, device=dev)[:, None].expand(Bn, T).reshape(-1)[m]
        sid = torch.tensor(sids, device=dev)
        ST.update(seq=rows, nseq=Bn, sids=sid, lens=am.sum(1).float(), unit=(lang * NS + sid)[rows],
                  units_np=lang * NS + np.array(sids))
        tidx, trows, off = [], [], 0
        for i in b:
            for pos, r in TSEL[lang].get(i, []):
                tidx.append(off + pos); trows.append(r)
            off += len(seqs[i])
        ST.update(tidx=torch.tensor(tidx, device=dev) if tidx else None, trows=np.array(trows, dtype=np.int64))
    model(input_ids=ids, attention_mask=am, use_cache=False)
    ST["mode"] = None


# ------------------------------------------------------------------ 1. calibration pass
log("calibration pass")
for b in batches(cal, range(len(cal))):
    run(cal, b, "cal")
log("calibration captured", sum(x.shape[0] for x in CAL_H[0]), "tokens/layer")


def mean_ent(z, s, k=None):
    if k is not None:
        z = z.topk(k, -1).values
    return float(ent(torch.softmax(s * z, -1)).mean())


def fit_scale(z, target, k=None):
    lo, hi = -6.0, 6.0  # entropy decreases in s
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if mean_ent(z, math.exp(mid), k) > target:
            lo = mid
        else:
            hi = mid
    s = math.exp(0.5 * (lo + hi))
    return s, abs(mean_ent(z, s, k) - target)


# ------------------------------------------------------------------ 2. null routers
diag = {"loadtv_B": np.zeros((L, D)), "loadtv_G": np.zeros((L, D)), "cal_maxload": np.zeros((L, NR)),
        "sT": np.zeros((L, D)), "sTk": np.zeros((L, D)), "resT": np.zeros((L, D)), "resTk": np.zeros((L, D)),
        "entT_full": np.zeros(L), "entT_topk": np.zeros(L), "entB_full": np.zeros((L, D)), "entB_topk": np.zeros((L, D))}
for l in range(L):
    Hc = torch.cat(CAL_H[l]).to(dev).double()
    CAL_H[l] = None
    Wd = gates[l].weight.detach().double()
    bT = gates[l].bias.detach().double() if GPTOSS else torch.zeros(E, dtype=torch.float64, device=dev)
    zT = Hc @ Wd.T + bT
    target = mm.loads(mm.topk(zT, K), E)
    uni = torch.full((E,), 1.0 / E, dtype=torch.float64, device=dev)
    st = mm.null_stats(Wd, Hc)
    gen = torch.Generator().manual_seed(178000 + l)
    WA, WB, WG, bB, bG = [], [], [], [], []
    for _ in range(D):
        A = torch.randn(d, d, generator=gen, dtype=torch.float64).to(dev)
        Q, R = torch.linalg.qr(A)
        Rh = Q * torch.sign(torch.diagonal(R))
        WA.append(Wd @ Rh)
    for j in range(D):
        Q = mm.haar(st["V"].shape[1], gen).to(dev)
        Wn = mm.null_router(Wd, Hc, "N1", Q, st)
        bn = mm.fit_bias(Hc, Wn, K, target)
        lc = mm.loads(mm.topk(Hc @ Wn.T + bn, K), E)
        diag["loadtv_B"][l, j] = float((lc / lc.sum() - target / target.sum()).abs().sum() / 2)
        WB.append(Wn); bB.append(bn)
    for j in range(D):
        G = torch.randn(E, d, generator=gen, dtype=torch.float64).to(dev)
        G = G * (Wd.norm() / G.norm())
        bg = mm.fit_bias(Hc, G, K, uni)
        lc = mm.loads(mm.topk(Hc @ G.T + bg, K), E)
        diag["loadtv_G"][l, j] = float((lc / lc.sum() - uni).abs().sum() / 2)
        WG.append(G); bG.append(bg)
    # sharpness-matched nulls (scaled copies of N_B)
    eTf, eTk = mean_ent(zT, 1.0), mean_ent(zT, 1.0, K)
    diag["entT_full"][l], diag["entT_topk"][l] = eTf, eTk
    WT, bTs, WTk, bTks = [], [], [], []
    for j in range(D):
        zB = Hc @ WB[j].T + bB[j]
        diag["entB_full"][l, j], diag["entB_topk"][l, j] = mean_ent(zB, 1.0), mean_ent(zB, 1.0, K)
        s, r = fit_scale(zB, eTf)
        sk, rk = fit_scale(zB, eTk, K)
        diag["sT"][l, j], diag["resT"][l, j], diag["sTk"][l, j], diag["resTk"][l, j] = s, r, sk, rk
        WT.append(s * WB[j]); bTs.append(s * bB[j]); WTk.append(sk * WB[j]); bTks.append(sk * bB[j])
    bA = [bT] * D
    WALL[l] = torch.cat(WA + WB + WG + WT + WTk).float().contiguous()
    BALL[l] = torch.cat(bA + bB + bG + bTs + bTks).float().contiguous()
    allW = torch.cat([Wd, WALL[l].double()]).view(NR, E, d)
    allb = torch.cat([bT, BALL[l].double()]).view(NR, E)
    for r in range(NR):
        lc = mm.loads(mm.topk(Hc @ allW[r].T + allb[r], K), E)
        diag["cal_maxload"][l, r] = float(lc.max() / (K / E))
    del Hc, st
    if l % 4 == 0 or l == L - 1:
        log(f"nulls layer {l}: loadtv_B {diag['loadtv_B'][l].mean():.4f} sT {diag['sT'][l].mean():.3f} "
            f"sTk {diag['sTk'][l].mean():.3f} entT {eTf:.3f}/{eTk:.3f} entB {diag['entB_full'][l].mean():.3f}/"
            f"{diag['entB_topk'][l].mean():.3f} cal maxload T {diag['cal_maxload'][l, 0]:.2f}")
torch.cuda.empty_cache()

# ------------------------------------------------------------------ 3. determinism check
eng = meas["eng_Latn"]
b0 = next(batches(eng, range(NS)))
run(eng, b0, "det")
run(eng, b0, "det")
det = [float((DET[l][0] == DET[l][1]).all(-1).float().mean()) for l in range(L)]
det_setagree = [float(np.mean([len(set(a.tolist()) & set(c.tolist())) / K for a, c in zip(DET[l][0], DET[l][1])]))
                for l in range(L)]
log(f"determinism: exact-set agreement min {min(det):.4f}; overlap min {min(det_setagree):.4f}")

# ------------------------------------------------------------------ 4. measurement pass (English first)
for li, lg in enumerate(langs):
    seqs = meas[lg]
    for b in batches(seqs, range(NS)):
        run(seqs, b, "meas", lang=li, sids=b)
    log(f"measured {lg} ({li + 1}/{NL}); hook fp32-vs-model {hookchk[0] / hookchk[2]:.5f} "
        f"T-vs-model {hookchk[1] / hookchk[2]:.5f}")

# ------------------------------------------------------------------ 5. save
np.savez(os.path.join(args.out, "tallies.npz"), counts=counts.cpu().numpy(),
         ntok=np.array([ntok_meas[lg] for lg in langs]), langs=np.array(langs),
         det_exact=np.array(det), det_overlap=np.array(det_setagree), **diag)
np.save(os.path.join(args.out, "persent.npy"), persent.view(L, NU, 4, E).cpu().numpy().astype(np.uint16))
np.save(os.path.join(args.out, "div.npy"), DIV.cpu().numpy())
np.save(os.path.join(args.out, "sentmean.npy"), SENT.astype(np.float16))
np.save(os.path.join(args.out, "toksub.npy"), TOKS)
np.savez(os.path.join(args.out, "toksub_meta.npz"), lang=tsel_lang, sid=tsel_sid)
np.save(os.path.join(args.out, "gateW.npy"), torch.stack([g.weight.detach().float() for g in gates]).cpu().numpy())
meta = {"model": MODEL, "key": args.model, "langs": langs, "n_sent": NS, "n_cal": args.n_cal, "draws": D, "K": K,
        "E": E, "L": L, "d": d,
        "router_index": {"T": [0], "N_A": [1, D], "N_B": [1 + D, 2 * D], "N_G": [1 + 2 * D, 3 * D],
                         "N_T": [1 + 3 * D, 4 * D], "N_Tk": [1 + 4 * D, 5 * D]},
        "persent_routers": ["T", "N_A0", "N_B0", "N_G0"], "hook_agreement": float(hookchk[0] / hookchk[2]),
        "t_vs_model": float(hookchk[1] / hookchk[2]),
        "det_exact_min": min(det), "det_overlap_min": min(det_setagree), "ntok": ntok_meas,
        "wall_s": time.time() - t0, "host": os.uname().nodename, "attn": ATTN,
        "gpu": torch.cuda.get_device_name(0), "flores_sha256": "b8b0b76783024b85797e5cc75064eb83fc5288b41e9654dabc7be6ae944011f6"}
json.dump(meta, open(os.path.join(args.out, "meta.json"), "w"), indent=1)
log("done", json.dumps({k: meta[k] for k in ("hook_agreement", "t_vs_model", "det_exact_min", "wall_s")}))
