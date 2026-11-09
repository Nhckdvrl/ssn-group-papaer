#!/usr/bin/env python3
"""E181-step1, M2: Llama-2-7B MLP neurons, one forward pass over FLORES-200 dev, streaming LAPE counts.
Card: division/experiments/E181-DRAFT-unit-level-language-null.md section 0.

Languages: the 20 E178/E179 languages + vie_Latn, ind_Latn (Tang-7 sanity only). BOS prepended, BOS position not counted.
Hook on each layer's mlp.gate_proj: input x = MLP input (post_attention_layernorm output), output z = model's gate preact.
Activation (Tang): SiLU(z) > 0 <=> z > 0. No hidden states stored.
Counts (int32) full[r, l, k, n] and sub[r, l, k, n] (sub = 1000 tokens per language, E179 rule, seed 179; 20 langs):
  r: 0 T | 1..8 NA-n | 9..16 NB-n | 17 T with each token's language label drawn uniformly among the 20 languages
Nulls: per layer and draw one Haar R in O(d) (seed 181000 + 100 l + draw), x -> xR; NA no bias; NB per-neuron threshold
fitted on a calibration set (FLORES devtest first 50 sentences x 20 langs, 1000 tokens per language, seed 181) so that
the null neuron's activation rate equals the trained neuron's. NA and NB share R per draw. Null preacts fp32 (TF32).
"""
import argparse, json, os, sys, time
import numpy as np
import torch
import torch.nn.functional as F

LANGS = ["eng_Latn", "arb_Arab", "asm_Beng", "bam_Latn", "ben_Beng", "fra_Latn", "hin_Deva", "lit_Latn",
         "ory_Orya", "pes_Arab", "srp_Cyrl", "tha_Thai", "zho_Hans",
         "deu_Latn", "spa_Latn", "jpn_Jpan", "kor_Hang", "swh_Latn",
         "rus_Cyrl", "tam_Taml"]
EXTRA = ["vie_Latn", "ind_Latn"]
FLORES = "/home/xiang/mechpop_cache/flores200/flores200_dataset"
MODEL = "NousResearch/Llama-2-7b-hf"
ap = argparse.ArgumentParser()
ap.add_argument("--out", default="/home/xiang/mechpop_cache/e181/llama2")
ap.add_argument("--n-sent", type=int, default=997)
ap.add_argument("--draws", type=int, default=8)
ap.add_argument("--batch-tokens", type=int, default=16384)
ap.add_argument("--max-layers", type=int, default=0)  # smoke test only
ap.add_argument("--model-path", default=MODEL)  # local copy of the same snapshot (NFS reads are slow)
args = ap.parse_args()
os.makedirs(args.out, exist_ok=True)
torch.backends.cuda.matmul.allow_tf32 = True
torch.set_grad_enabled(False)
dev = torch.device("cuda")
t0 = time.time()
D, NS = args.draws, args.n_sent
ALL = LANGS + EXTRA
NL, NL20 = len(ALL), len(LANGS)
NR = 2 + 2 * D


def log(*a):
    print(f"[{time.strftime('%H:%M:%S')} +{time.time() - t0:7.1f}s]", *a, flush=True)


def read(split, lg, n):
    with open(f"{FLORES}/{split}/{lg}.{split}", encoding="utf-8") as f:
        return [x.rstrip("\n") for x in f][:n]


from transformers import AutoModelForCausalLM, AutoTokenizer  # noqa: E402
tok = AutoTokenizer.from_pretrained(args.model_path)
model = AutoModelForCausalLM.from_pretrained(args.model_path, dtype=torch.bfloat16, device_map={"": 0}, attn_implementation="sdpa")
model.eval()
layers = model.model.layers
L = len(layers) if not args.max_layers else args.max_layers
d = model.config.hidden_size
N = model.config.intermediate_size
BOS = tok.bos_token_id
log(f"loaded {MODEL}: L={len(layers)} (using {L}) d={d} N={N} bos={BOS} act={model.config.hidden_act}")

enc = lambda ss: [tok(s, add_special_tokens=True)["input_ids"] for s in ss]
meas = {lg: enc(read("dev", lg, NS)) for lg in ALL}
for lg in ALL:
    assert all(x[0] == BOS for x in meas[lg])
cal = {lg: enc(read("devtest", lg, 50)) for lg in LANGS}
ntok = {lg: int(sum(len(x) - 1 for x in v)) for lg, v in meas.items()}
log("non-BOS tokens per language:", ntok)

# subsample (E179 rule on non-BOS tokens): per language 1000 global positions, seed 179, sequential over 20 langs
rs = np.random.default_rng(179)
TSEL = []
for lg in LANGS:
    lens = np.array([len(x) - 1 for x in meas[lg]])
    off = np.concatenate([[0], np.cumsum(lens)])
    pick = np.sort(rs.choice(off[-1], min(1000, off[-1]), replace=False))
    dct = {}
    for g in pick:
        sid = int(np.searchsorted(off, g, side="right") - 1)
        dct.setdefault(sid, []).append(int(g - off[sid]))
    TSEL.append(dct)


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
    ids = torch.full((len(b), T), tok.eos_token_id, dtype=torch.long)
    am = torch.zeros((len(b), T), dtype=torch.long)
    for r, i in enumerate(b):
        ids[r, :len(seqs[i])] = torch.tensor(seqs[i])
        am[r, :len(seqs[i])] = 1
    cm = am.clone()
    cm[:, 0] = 0  # BOS not counted
    return ids.to(dev), am.to(dev), cm.reshape(-1).bool().to(dev)


ST = {"mode": None}
CAL_H = [[] for _ in range(L)]
DET = {}
RS = [None] * L      # [D, d, d] fp32
TH = [None] * L      # [D, N] fp32 NB thresholds
full = torch.zeros(NR, L, NL, N, dtype=torch.int32, device=dev)
sub = torch.zeros(NR, L, NL20, N, dtype=torch.int32, device=dev)
ntok_sh = torch.zeros(NL20, dtype=torch.float64)
hookchk = torch.zeros(L, 2, dtype=torch.float64)  # sign agreement recompute vs model; n
shgen = torch.Generator(device=dev).manual_seed(181)


def make_hook(l):
    gate = layers[l].mlp.gate_proj

    def hook(mod, inp, out):
        mode = ST["mode"]
        if mode is None:
            return
        m = ST["mask"]
        x = inp[0].reshape(-1, d)[m]
        if mode == "cal":
            CAL_H[l].append(x.detach().cpu())
            return
        z = out.reshape(-1, N)[m]
        aT = z > 0
        if mode == "det":
            DET.setdefault(l, []).append(aT.sum(0).cpu())
            return
        li = ST["lang"]
        if ST["chk"]:
            zr = F.linear(x, gate.weight)
            hookchk[l, 0] += float(((zr > 0) == aT).float().mean(1).sum())
            hookchk[l, 1] += x.shape[0]
        sidx = ST["sidx"]
        full[0, l, li] += aT.sum(0)
        if sidx is not None:
            sub[0, l, li] += aT[sidx].sum(0)
        if li < NL20:
            lab = ST["shlab"]
            full[1 + 2 * D, l, :NL20] += (F.one_hot(lab, NL20).float().T @ aT.float()).round().int()
        xf = x.float()
        Wf = gate.weight.float()
        for j in range(D):
            zn = (xf @ RS[l][j]) @ Wf.T
            a = zn > 0
            full[1 + j, l, li] += a.sum(0)
            b = zn > TH[l][j]
            full[1 + D + j, l, li] += b.sum(0)
            if sidx is not None:
                sub[1 + j, l, li] += a[sidx].sum(0)
                sub[1 + D + j, l, li] += b[sidx].sum(0)
            del zn, a, b
    return hook


for l in range(L):
    layers[l].mlp.gate_proj.register_forward_hook(make_hook(l))


@torch.no_grad()
def run(seqs, b, mode, lang=0, chk=False):
    ids, am, cm = make_inputs(seqs, b)
    ST.update(mode=mode, mask=cm, lang=lang, chk=chk, sidx=None)
    if mode == "meas":
        if lang < NL20:
            idx, off = [], 0
            for i in b:
                for pos in TSEL[lang].get(i, []):
                    idx.append(off + pos)
                off += len(seqs[i]) - 1
            ST["sidx"] = torch.tensor(idx, device=dev) if idx else None
            n = int(cm.sum())
            lab = torch.randint(0, NL20, (n,), device=dev, generator=shgen)
            ST["shlab"] = lab
            ntok_sh.add_(torch.bincount(lab, minlength=NL20).double().cpu())
    model(input_ids=ids, attention_mask=am, use_cache=False)
    ST["mode"] = None


# ---------------------------------------------------------------- calibration
log("calibration pass")
cal_lang = []
for li, lg in enumerate(LANGS):
    seqs = cal[lg]
    n0 = sum(x.shape[0] for x in CAL_H[0])
    for b in batches(seqs, range(len(seqs))):
        run(seqs, b, "cal")
    n1 = sum(x.shape[0] for x in CAL_H[0])
    cal_lang.append(n1 - n0)
log("calibration tokens per language:", dict(zip(LANGS, cal_lang)))
rc = np.random.default_rng(181)
offs = np.concatenate([[0], np.cumsum(cal_lang)])
csel = np.concatenate([offs[k] + np.sort(rc.choice(cal_lang[k], min(1000, cal_lang[k]), replace=False))
                       for k in range(NL20)])
csel_t = torch.tensor(csel)
diag = {"cal_rate_T": np.zeros(L), "cal_rate_NA": np.zeros((L, D)), "cal_rate_NB": np.zeros((L, D)),
        "cal_relerr_med": np.zeros((L, D)), "cal_tok_per_lang": np.array([min(1000, c) for c in cal_lang])}


def thresholds(z, r):
    n = z.shape[0]
    s = z.sort(0).values
    m = torch.round(r * n).long().clamp(0, n)
    hi = s.gather(0, (n - m).clamp(max=n - 1)[None]).squeeze(0)
    lo = s.gather(0, (n - m - 1).clamp(min=0)[None]).squeeze(0)
    th = 0.5 * (hi + lo)
    th = torch.where(m == 0, s[-1] + 1.0, th)
    th = torch.where(m == n, s[0] - 1.0, th)
    return th


CH = 2048
for l in range(L):
    Hc = torch.cat(CAL_H[l])[csel_t].to(dev)
    CAL_H[l] = None
    Wg = layers[l].mlp.gate_proj.weight
    rT = (F.linear(Hc, Wg) > 0).float().mean(0)
    diag["cal_rate_T"][l] = float(rT.mean())
    Rl, Tl = [], []
    Hf, Wf = Hc.float(), Wg.float()
    for j in range(D):
        g = torch.Generator().manual_seed(181000 + 100 * l + j)
        A = torch.randn(d, d, generator=g, dtype=torch.float64).to(dev)
        Q, Rr = torch.linalg.qr(A)
        R = (Q * torch.sign(torch.diagonal(Rr))).float()
        HR = Hf @ R
        th = torch.empty(N, device=dev)
        na = nb = 0.0
        errs = []
        for c0 in range(0, N, CH):
            z = HR @ Wf[c0:c0 + CH].T
            th[c0:c0 + CH] = thresholds(z, rT[c0:c0 + CH])
            na += float((z > 0).float().mean(0).sum())
            rn = (z > th[c0:c0 + CH]).float().mean(0)
            nb += float(rn.sum())
            rt = rT[c0:c0 + CH]
            v = rt >= 1.0 / Hc.shape[0]
            errs.append(((rn[v] - rt[v]).abs() / rt[v]))
        diag["cal_rate_NA"][l, j] = na / N
        diag["cal_rate_NB"][l, j] = nb / N
        diag["cal_relerr_med"][l, j] = float(torch.cat(errs).median())
        Rl.append(R)
        Tl.append(th)
        del HR
    RS[l] = torch.stack(Rl)
    TH[l] = torch.stack(Tl)
    del Hc, Hf
    if l % 4 == 0 or l == L - 1:
        log(f"nulls layer {l}: cal rate T {diag['cal_rate_T'][l]:.4f} NA {diag['cal_rate_NA'][l].mean():.4f} "
            f"NB {diag['cal_rate_NB'][l].mean():.4f} (in-sample relerr {diag['cal_relerr_med'][l].max():.4f})")
torch.cuda.empty_cache()
log(f"mem {torch.cuda.memory_allocated() / 2**30:.1f} GiB")

# ---------------------------------------------------------------- two-pass identity
eng = meas["eng_Latn"]
b0 = next(batches(eng, range(NS)))
run(eng, b0, "det")
run(eng, b0, "det")
two_pass = [bool(torch.equal(DET[l][0], DET[l][1])) for l in range(L)]
log(f"two-pass identical: {all(two_pass)}")

# ---------------------------------------------------------------- measurement
nb_done = 0
for li, lg in enumerate(ALL):
    seqs = meas[lg]
    for bi, b in enumerate(batches(seqs, range(NS))):
        run(seqs, b, "meas", lang=li, chk=(bi < 3))
        nb_done += 1
    chk = (hookchk[:, 0] / hookchk[:, 1].clamp(min=1)).min()
    log(f"measured {lg} ({li + 1}/{NL}); hook sign agreement min over layers {float(chk):.6f}")

np.save(f"{args.out}/full.npy", full.cpu().numpy())
np.save(f"{args.out}/sub.npy", sub.cpu().numpy())
np.savez(f"{args.out}/diag.npz", **diag, two_pass=np.array(two_pass), hookchk=hookchk.numpy(),
         ntok_sh=ntok_sh.numpy())
json.dump({"model": MODEL, "model_path": args.model_path, "L": L, "N": N, "langs": ALL, "langs20": LANGS, "ntok": ntok, "draws": D,
           "index": {"T": 0, "NA": [1, D], "NB": [1 + D, 2 * D], "SH": 1 + 2 * D}, "sub_tok_per_lang": 1000,
           "two_pass_identical_all": all(two_pass),
           "hook_sign_agreement_min": float((hookchk[:, 0] / hookchk[:, 1].clamp(min=1)).min()),
           "wall_s": time.time() - t0, "host": os.uname().nodename, "gpu": torch.cuda.get_device_name(0)},
          open(f"{args.out}/meta.json", "w"), indent=1)
log("done")
