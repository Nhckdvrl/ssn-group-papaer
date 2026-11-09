#!/usr/bin/env python3
"""E181-step1, M1: Qwen3-30B-A3B expert-FFN neurons on the E179 cached router inputs (no forward pass).
Card: division/experiments/E181-DRAFT-unit-level-language-null.md section 0.

Hidden states: ~/mechpop_cache/e179/qwen3/toksub.npy  [48, 20000, 2048] fp16 (1000 tokens per language, seed 179),
= router input = expert-FFN input. Neuron j of expert e in layer l: gate pre-activation z = h . W_gate[e, j].
Activation (Tang): SiLU(z) > 0  <=>  z > 0.

Units per layer: 128 experts x 768 = 98,304 neurons (index e*768 + j).
Readouts saved (counts of active tokens per language):
  uncond[r, l, k, n]  uint16  r: 0 T | 1..8 NA-n | 9..16 NB-n | 17 T with shuffled language labels
  routed[r, l, k, n]  uint16  r: 0 T | 1..8 NA | 9..16 NB  (active AND expert selected by the trained top-8 router)
Nulls: per layer and draw one Haar R in O(d) (seed 181000 + 100 l + draw), h -> hR, shared by all neurons of the layer;
NA = no bias; NB = per-neuron threshold so that the null neuron's activation rate equals the trained neuron's
(2-fold cross-fit within language; threshold fitted on one fold, applied to the other). NA and NB share R per draw.
"""
import json, os, sys, time
import numpy as np
import torch
from safetensors import safe_open

CACHE = "/home/xiang/mechpop_cache/e179/qwen3"
OUT = "/home/xiang/mechpop_cache/e181/qwen3"
SNAP = [os.path.join(r, d) for r in ["/home/xiang/.cache/huggingface/hub/models--Qwen--Qwen3-30B-A3B/snapshots"]
        for d in os.listdir(r)][0]
os.makedirs(OUT, exist_ok=True)
torch.backends.cuda.matmul.allow_tf32 = True
dev = torch.device("cuda")
t0 = time.time()
D = 8
CH = 8192  # neuron chunk


def log(*a):
    print(f"[{time.strftime('%H:%M:%S')} +{time.time() - t0:7.1f}s]", *a, flush=True)


meta = json.load(open(f"{CACHE}/meta.json"))
L, E, d, K = meta["L"], meta["E"], meta["d"], meta["K"]
toks = np.load(f"{CACHE}/toksub.npy", mmap_mode="r")
lang = np.load(f"{CACHE}/toksub_meta.npz")["lang"]
NL = int(lang.max()) + 1
NT = len(lang)
gateW = np.load(f"{CACHE}/gateW.npy")  # router weights [L, E, d]
wmap = json.load(open(f"{SNAP}/model.safetensors.index.json"))["weight_map"]
FF = 768
N = E * FF
log(f"L={L} E={E} d={d} N/layer={N} tokens={NT} langs={NL} snapshot={SNAP}")

# folds: alternate within language (rows are grouped by language, sorted by position)
fold = np.zeros(NT, np.int64)
for k in range(NL):
    idx = np.where(lang == k)[0]
    fold[idx[1::2]] = 1
fA = torch.tensor(np.where(fold == 0)[0], device=dev)
fB = torch.tensor(np.where(fold == 1)[0], device=dev)
rng = np.random.default_rng(181)
lang_sh = rng.permutation(lang)
LM = torch.zeros(NL, NT, device=dev)
LM[torch.tensor(lang, device=dev), torch.arange(NT, device=dev)] = 1.0
LMs = torch.zeros(NL, NT, device=dev)
LMs[torch.tensor(lang_sh, device=dev), torch.arange(NT, device=dev)] = 1.0


def load_gate(l):
    W = torch.empty(N, d, dtype=torch.bfloat16)
    handles = {}
    for e in range(E):
        key = f"model.layers.{l}.mlp.experts.{e}.gate_proj.weight"
        f = wmap[key]
        if f not in handles:
            handles[f] = safe_open(f"{SNAP}/{f}", framework="pt")
        W[e * FF:(e + 1) * FF] = handles[f].get_tensor(key)
    return W.to(dev)


def thresholds(z, r):
    """z [n, c] fp32, r [c] target rate -> theta [c] s.t. mean(z > theta) == round(r n)/n (no ties)."""
    n = z.shape[0]
    s = z.sort(0).values
    m = torch.round(r * n).long().clamp(0, n)
    hi_idx = (n - m).clamp(max=n - 1)  # first index counted as active
    lo_idx = (n - m - 1).clamp(min=0)
    hi = s.gather(0, hi_idx[None]).squeeze(0)
    lo = s.gather(0, lo_idx[None]).squeeze(0)
    th = 0.5 * (hi + lo)
    th = torch.where(m == 0, s[-1] + 1.0, th)
    th = torch.where(m == n, s[0] - 1.0, th)
    return th


uncond = np.zeros((2 + 2 * D, L, NL, N), np.uint16)
routed = np.zeros((1 + 2 * D, L, NL, N), np.uint16)
diag = {"relerr_med": np.zeros((L, D)), "relerr_mean": np.zeros((L, D)), "rate_T": np.zeros(L),
        "two_pass_identical": np.zeros(L, bool), "na_rate": np.zeros((L, D)), "nb_rate": np.zeros((L, D)),
        "n_valid_relerr": np.zeros((L, D))}
for l in range(L):
    tl = time.time()
    W = load_gate(l)
    H = torch.from_numpy(np.ascontiguousarray(toks[l])).to(dev)  # fp16
    Hb = H.to(torch.bfloat16)
    Hf = H.float()
    # trained top-8 routing on the same h (bf16 linear like the model's gate)
    Wr = torch.from_numpy(gateW[l]).to(dev).to(torch.bfloat16)
    rl = torch.nn.functional.linear(Hb, Wr).float()
    route = torch.zeros(NT, E, device=dev).scatter_(1, rl.topk(K, -1).indices, 1.0)  # [NT, E]
    Rs = []
    for j in range(D):
        g = torch.Generator().manual_seed(181000 + 100 * l + j)
        A = torch.randn(d, d, generator=g, dtype=torch.float64).to(dev)
        Q, Rr = torch.linalg.qr(A)
        Rs.append((Q * torch.sign(torch.diagonal(Rr))).float())
    HR = [Hf @ R for R in Rs]
    errs = [[] for _ in range(D)]
    rT_all, ident = [], True
    for c0 in range(0, N, CH):
        c1 = min(N, c0 + CH)
        Wc = W[c0:c1]
        e_of = torch.arange(c0, c1, device=dev) // FF
        rmask = route[:, e_of]  # [NT, c]
        zT = torch.nn.functional.linear(Hb, Wc)
        aT = (zT > 0).float()
        zT2 = torch.nn.functional.linear(Hb, Wc)
        ident &= bool(torch.equal(zT > 0, zT2 > 0))
        del zT2
        uncond[0, l, :, c0:c1] = (LM @ aT).round().cpu().numpy().astype(np.uint16)
        uncond[1 + 2 * D, l, :, c0:c1] = (LMs @ aT).round().cpu().numpy().astype(np.uint16)
        routed[0, l, :, c0:c1] = (LM @ (aT * rmask)).round().cpu().numpy().astype(np.uint16)
        rA, rB = aT[fA].mean(0), aT[fB].mean(0)  # trained rates per fold (language-balanced: folds balanced)
        rT_all.append(aT.mean(0))
        for j in range(D):
            Wf = Wc.float()
            z = HR[j] @ Wf.T  # [NT, c] fp32 (TF32)
            aA = (z > 0).float()
            uncond[1 + j, l, :, c0:c1] = (LM @ aA).round().cpu().numpy().astype(np.uint16)
            routed[1 + j, l, :, c0:c1] = (LM @ (aA * rmask)).round().cpu().numpy().astype(np.uint16)
            diag["na_rate"][l, j] += float(aA.mean(0).sum())
            zA, zB = z[fA], z[fB]
            thA = thresholds(zA, rA)  # fitted on fold A, applied to fold B
            thB = thresholds(zB, rB)
            aB = torch.empty_like(aA)
            aB[fA] = (zA > thB).float()
            aB[fB] = (zB > thA).float()
            uncond[1 + D + j, l, :, c0:c1] = (LM @ aB).round().cpu().numpy().astype(np.uint16)
            routed[1 + D + j, l, :, c0:c1] = (LM @ (aB * rmask)).round().cpu().numpy().astype(np.uint16)
            diag["nb_rate"][l, j] += float(aB.mean(0).sum())
            # held-out rate matching: null rate on fold B (theta from A) vs trained rate on fold B; and vice versa
            nh = fA.numel()
            for rt, rn in ((rB, aB[fB].mean(0)), (rA, aB[fA].mean(0))):
                v = rt >= 1.0 / nh
                errs[j].append(((rn[v] - rt[v]).abs() / rt[v]).cpu())
            del z, aA, aB, zA, zB
    for j in range(D):
        e_ = torch.cat(errs[j])
        diag["relerr_med"][l, j] = float(e_.median())
        diag["relerr_mean"][l, j] = float(e_.mean())
        diag["n_valid_relerr"][l, j] = e_.numel() / 2
    diag["na_rate"][l] /= N
    diag["nb_rate"][l] /= N
    diag["rate_T"][l] = float(torch.cat(rT_all).mean())
    diag["two_pass_identical"][l] = ident
    log(f"layer {l}: rate T {diag['rate_T'][l]:.4f} NA {diag['na_rate'][l].mean():.4f} NB {diag['nb_rate'][l].mean():.4f}"
        f" | NB held-out rel.err median {diag['relerr_med'][l].mean():.4f} (max draw {diag['relerr_med'][l].max():.4f})"
        f" | two-pass {ident} | {time.time() - tl:.1f}s")
    del W, H, Hb, Hf, HR, Rs, route
    torch.cuda.empty_cache()

np.save(f"{OUT}/uncond.npy", uncond)
np.save(f"{OUT}/routed.npy", routed)
np.savez(f"{OUT}/diag.npz", **diag)
json.dump({"model": meta["model"], "L": L, "N": N, "NL": NL, "langs": meta["langs"], "tok_per_lang": NT // NL,
           "draws": D, "uncond_index": {"T": 0, "NA": [1, D], "NB": [1 + D, 2 * D], "SH": 1 + 2 * D},
           "routed_index": {"T": 0, "NA": [1, D], "NB": [1 + D, 2 * D]}, "wall_s": time.time() - t0,
           "host": os.uname().nodename, "gpu": torch.cuda.get_device_name(0),
           "two_pass_identical_all": bool(diag["two_pass_identical"].all()),
           "relerr_med_overall": float(np.median(diag["relerr_med"]))},
          open(f"{OUT}/meta.json", "w"), indent=1)
log("done")
