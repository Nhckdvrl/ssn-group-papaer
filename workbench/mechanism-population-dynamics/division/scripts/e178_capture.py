#!/usr/bin/env python3
"""E178 capture: Qwen3-30B-A3B on FLORES-200 dev (20 languages, parallel), trained router vs random routers
scored on the SAME hidden states (card: division/experiments/E178-language-expert-null-pilot.md).

The model always runs with its trained router; alternative routers only score the gate inputs inside a forward
hook (no intervention). Routers per MoE layer (all top-8 over 128 experts):
  0           T    trained gate (model's own bf16 logits -> float; top-k == model's selection)
  1..D        N_A  W R, R Haar in O(2048), independent per layer/draw, no bias (Melton 2026)
  D+1..2D     N_B  repo N1 (moe_measure.py): W_c V Q V^T, Q Haar in O(r); bias refit on the calibration set to the
                   trained router's calibration loads (E167/E174 practice)
  2D+1..3D    N_G  Gaussian gate, Frobenius norm matched to W; bias refit to uniform load (supplementary)
Calibration hidden states (bias refits only): FLORES devtest first N_CAL sentences per language (disjoint from dev).

Outputs (OUT dir):
  tallies.npz   counts[L, NR, NL, E] (expert selections per layer/router/language), ntok[NL], diagnostics
  persent.npy   uint16 [L, NU, 4, E] per-(language,sentence) counts for routers (T, N_A0, N_B0, N_G0)
  div.npy       float32 [NL, NS, L, NR] Bandarkar entropy-normalised JSD of each sentence vs its English pair
  meta.json
"""
import argparse, json, math, os, sys, time
import numpy as np
import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import moe_measure as mm  # noqa: E402

LANGS = ["eng_Latn", "arb_Arab", "asm_Beng", "bam_Latn", "ben_Beng", "fra_Latn", "hin_Deva", "lit_Latn",
         "ory_Orya", "pes_Arab", "srp_Cyrl", "tha_Thai", "zho_Hans",          # Bandarkar et al. 2510.04694
         "deu_Latn", "spa_Latn", "jpn_Jpan", "kor_Hang", "swh_Latn",          # + Chen et al. 2601.14050
         "rus_Cyrl", "tam_Taml"]                                              # + Cyrillic/Slavic, Dravidian
FLORES = "/home/xiang/mechpop_cache/flores200/flores200_dataset"
MODEL = "Qwen/Qwen3-30B-A3B"

ap = argparse.ArgumentParser()
ap.add_argument("--out", required=True)
ap.add_argument("--n-sent", type=int, default=997)
ap.add_argument("--n-cal", type=int, default=25)
ap.add_argument("--draws", type=int, default=8)
ap.add_argument("--batch-tokens", type=int, default=16384)
ap.add_argument("--langs", default=",".join(LANGS))
args = ap.parse_args()
os.makedirs(args.out, exist_ok=True)
langs = args.langs.split(",")
assert langs[0] == "eng_Latn"
NL, NS, D = len(langs), args.n_sent, args.draws
NU = NL * NS
dev = torch.device("cuda")
t0 = time.time()


def log(*a):
    print(f"[{time.strftime('%H:%M:%S')} +{time.time() - t0:7.1f}s]", *a, flush=True)


def read(split, lang, n):
    with open(f"{FLORES}/{split}/{lang}.{split}", encoding="utf-8") as f:
        return [x.rstrip("\n") for x in f][:n]


from transformers import AutoModelForCausalLM, AutoTokenizer  # noqa: E402
tok = AutoTokenizer.from_pretrained(MODEL)
log("loading model")
model = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.bfloat16, device_map={"": 0},
                                             attn_implementation="sdpa")
model.eval()
layers = model.model.layers
gates = [ly.mlp.gate for ly in layers]
L, E, d = len(gates), gates[0].weight.shape[0], gates[0].weight.shape[1]
K = model.config.num_experts_per_tok
NR = 1 + 3 * D
log(f"loaded: L={L} E={E} d={d} K={K} NR={NR}; mem {torch.cuda.memory_allocated() / 2**30:.1f} GiB")

enc = lambda ss: [tok(s, add_special_tokens=False)["input_ids"] for s in ss]
meas = {lg: enc(read("dev", lg, NS)) for lg in langs}
cal = [ids for lg in langs for ids in enc(read("devtest", lg, args.n_cal))]
ntok_meas = {lg: int(sum(len(x) for x in v)) for lg, v in meas.items()}
log("tokens per language:", ntok_meas, "cal tokens", sum(len(x) for x in cal))


def batches(seqs, idx):
    """Length-sorted batches under a padded-token budget; yields lists of indices into seqs."""
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
hookchk = torch.zeros(2, dtype=torch.float64)  # (sum of |S_model ∩ S_fp32| / K, n tokens)
LOGE = math.log(E)


def ent(q):
    return -(q * q.clamp_min(1e-30).log()).sum(-1)


def make_hook(l):
    def hook(mod, inp, out):
        mode = ST["mode"]
        if mode is None:
            return
        m = ST["mask"]
        h = inp[0].reshape(-1, d)[m]
        lt = out.reshape(-1, E)[m].float()
        if mode == "cal":
            CAL_H[l].append(h.detach().to("cpu"))
            return
        if mode == "det":
            DET.setdefault(l, []).append(lt.topk(K, -1).indices.sort(-1).values.cpu())
            return
        hf = h.float()
        n = hf.shape[0]
        logits = torch.cat([lt, hf @ WALL[l].T + BALL[l]], 1).view(n, NR, E)
        S = logits.topk(K, -1).indices  # n, NR, K
        # hook correctness: fp32 recompute of the trained gate vs the model's own logits
        Sre = (hf @ mod.weight.float().T).topk(K, -1).indices
        oh0 = torch.zeros(n, E, device=dev).scatter_(1, S[:, 0], 1.0)
        hookchk[0] += float(oh0.gather(1, Sre).sum() / K)
        hookchk[1] += n
        li = ST["lang"]
        flat = (torch.arange(NR, device=dev)[None, :, None] * E + S).reshape(-1)
        counts[l, :, li] += torch.bincount(flat, minlength=NR * E).view(NR, E)
        u = ST["unit"]  # n
        f4 = ((u[:, None, None] * 4 + torch.arange(4, device=dev)[None, :, None]) * E + S[:, SEL4]).reshape(-1)
        persent[l].scatter_add_(0, f4, torch.ones_like(f4, dtype=torch.int32))
        # Bandarkar R4: per-sequence mean full-softmax routing distribution, entropy-normalised JSD vs English pair
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
            F = LOGE - 0.5 * (ent(q1) + ent(q2))
            DIV[li, sids, l] = js / F
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
        ST.update(seq=rows, nseq=Bn, sids=sid, lens=am.sum(1).float(), unit=(lang * NS + sid)[rows])
    model(input_ids=ids, attention_mask=am, use_cache=False)
    ST["mode"] = None


# ------------------------------------------------------------------ 1. calibration pass
log("calibration pass")
for b in batches(cal, range(len(cal))):
    run(cal, b, "cal")
log("calibration captured", sum(x.shape[0] for x in CAL_H[0]), "tokens/layer")

# ------------------------------------------------------------------ 2. null routers
diag = {"loadtv_B": np.zeros((L, D)), "loadtv_G": np.zeros((L, D)), "cal_maxload": np.zeros((L, NR))}
for l in range(L):
    Hc = torch.cat(CAL_H[l]).to(dev).double()
    CAL_H[l] = None
    Wd = gates[l].weight.detach().double()
    target = mm.loads(mm.topk(Hc @ Wd.T, K), E)
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
    zeros = [torch.zeros(E, dtype=torch.float64, device=dev)] * D
    WALL[l] = torch.cat(WA + WB + WG).float().contiguous()
    BALL[l] = torch.cat(zeros + bB + bG).float().contiguous()
    allW = torch.cat([Wd, WALL[l].double()]).view(NR, E, d)
    allb = torch.cat([torch.zeros(E, dtype=torch.float64, device=dev), BALL[l].double()]).view(NR, E)
    for r in range(NR):
        lc = mm.loads(mm.topk(Hc @ allW[r].T + allb[r], K), E)  # fraction of tokens selecting each expert
        diag["cal_maxload"][l, r] = float(lc.max() / (K / E))
    del Hc, st
    if l % 8 == 0 or l == L - 1:
        log(f"nulls layer {l}: loadtv_B {diag['loadtv_B'][l].mean():.4f} loadtv_G {diag['loadtv_G'][l].mean():.4f} "
            f"cal maxload T {diag['cal_maxload'][l, 0]:.2f} A {diag['cal_maxload'][l, 1:1 + D].max():.2f} "
            f"B {diag['cal_maxload'][l, 1 + D:1 + 2 * D].max():.2f} G {diag['cal_maxload'][l, 1 + 2 * D:].max():.2f}")
torch.cuda.empty_cache()

# ------------------------------------------------------------------ 3. determinism check (trained router)
eng = meas["eng_Latn"]
b0 = next(batches(eng, range(NS)))
run(eng, b0, "det")
run(eng, b0, "det")
det = [float((DET[l][0] == DET[l][1]).all(-1).float().mean()) for l in range(L)]
det_setagree = [float(np.mean([len(set(a.tolist()) & set(c.tolist())) / K for a, c in zip(DET[l][0], DET[l][1])]))
                for l in range(L)]
log(f"determinism: exact-set agreement min {min(det):.4f} mean {np.mean(det):.4f}; overlap min {min(det_setagree):.4f}")

# ------------------------------------------------------------------ 4. measurement pass (English first)
for li, lg in enumerate(langs):
    seqs = meas[lg]
    for b in batches(seqs, range(NS)):
        run(seqs, b, "meas", lang=li, sids=b)
    log(f"measured {lg} ({li + 1}/{NL}); hook agreement so far {hookchk[0] / hookchk[1]:.5f}")

# ------------------------------------------------------------------ 5. save
np.savez(os.path.join(args.out, "tallies.npz"), counts=counts.cpu().numpy(),
         ntok=np.array([ntok_meas[lg] for lg in langs]), langs=np.array(langs),
         loadtv_B=diag["loadtv_B"], loadtv_G=diag["loadtv_G"], cal_maxload=diag["cal_maxload"],
         det_exact=np.array(det), det_overlap=np.array(det_setagree))
np.save(os.path.join(args.out, "persent.npy"), persent.view(L, NU, 4, E).cpu().numpy().astype(np.uint16))
np.save(os.path.join(args.out, "div.npy"), DIV.cpu().numpy())
meta = {"model": MODEL, "langs": langs, "n_sent": NS, "n_cal": args.n_cal, "draws": D, "K": K, "E": E, "L": L,
        "router_index": {"T": [0], "N_A": [1, D], "N_B": [1 + D, 2 * D], "N_G": [1 + 2 * D, 3 * D]},
        "persent_routers": ["T", "N_A0", "N_B0", "N_G0"], "hook_agreement": float(hookchk[0] / hookchk[1]),
        "det_exact_min": min(det), "det_overlap_min": min(det_setagree), "ntok": ntok_meas,
        "wall_s": time.time() - t0, "host": os.uname().nodename,
        "gpu": torch.cuda.get_device_name(0), "flores_sha256": "b8b0b76783024b85797e5cc75064eb83fc5288b41e9654dabc7be6ae944011f6"}
json.dump(meta, open(os.path.join(args.out, "meta.json"), "w"), indent=1)
log("done", json.dumps({k: meta[k] for k in ("hook_agreement", "det_exact_min", "wall_s")}))
