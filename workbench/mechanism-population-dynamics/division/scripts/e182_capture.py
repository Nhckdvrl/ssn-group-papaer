#!/usr/bin/env python3
"""E182 capture (card: division/experiments/E182-script-cost-lexical-carrier.md). Based on e180_capture.py
(e180 scripts untouched).

22 language sides in groups S / U / H (e182_common.GROUPS; srp_Latn and uzn_Cyrl are deterministic
transliterations), FLORES-200 devtest 1012 sentences (held out from E180's dev); calibration = dev first 25.
Routers on the same hidden states: T | N_A (Haar, 8) | N_B (N1 load-matched, 8); seeds 182000 + l.
Per-sentence, per-class token equalisation inside each group (seed 182), classes ALL / LET / NON / NONtm.
Saved:
  ps_ALL.npy, ps_LET.npy (uint16), ps_NON.npy, ps_NONtm.npy (uint8)   [L, NU, 17, E] expert counts over the
      class-selected tokens per (side, sentence) and router; unit = side_index * NS + sid
  topk_T.npy   uint8  [L, NTOK, K]   T's top-k for ALL tokens
  tokmeta.npz  per-token side, sid, pos, input id, predicted next id, class code, 4 selection flags
Router index: 0 T | N_A 1..D | N_B D+1..2D.
"""
import argparse, json, os, sys, time
import numpy as np
import torch
import torch.nn.functional as F

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import moe_measure as mm  # noqa: E402
import e182_common as C  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--model", required=True, choices=list(C.MODELS))
ap.add_argument("--out", required=True)
ap.add_argument("--n-sent", type=int, default=0, help="0 = all")
ap.add_argument("--n-cal", type=int, default=25)
ap.add_argument("--draws", type=int, default=8)
ap.add_argument("--batch-tokens", type=int, default=16384)
ap.add_argument("--langs", default=",".join(C.LANGS))
ap.add_argument("--meas-split", default="devtest")
ap.add_argument("--cal-split", default="dev")
args = ap.parse_args()
os.makedirs(args.out, exist_ok=True)
langs = args.langs.split(",")
GROUPS = {g: [x for x in gl if x in langs] for g, gl in C.GROUPS.items()}
GROUPS = {g: gl for g, gl in GROUPS.items() if gl}
D = args.draws
NR = 1 + 2 * D
MODEL, ATTN = C.MODELS[args.model]
GPTOSS = args.model == "gptoss"
dev = torch.device("cuda")
t0 = time.time()
CLS_CODE = {"let": 1, "non": 2, "frag": 3, "apos": 4, "empty": 5}


def log(*a):
    print(f"[{time.strftime('%H:%M:%S')} +{time.time() - t0:7.1f}s]", *a, flush=True)


from transformers import AutoModelForCausalLM, AutoTokenizer  # noqa: E402
tok = AutoTokenizer.from_pretrained(MODEL)
enc = lambda ss: [tok(s, add_special_tokens=False)["input_ids"] for s in ss]
meas = {lg: enc(C.read(args.meas_split, lg, args.n_sent or None)) for lg in langs}
NS = len(meas[langs[0]])
assert all(len(v) == NS for v in meas.values())
NL = len(langs)
NU = NL * NS
cal = [ids for lg in langs for ids in enc(C.read(args.cal_split, lg, args.n_cal))]
ntok_meas = {lg: int(sum(len(x) for x in v)) for lg, v in meas.items()}
CLS = {}


def cls_of(t):
    if t not in CLS:
        CLS[t] = CLS_CODE[C.token_class(tok.decode([t]))]
    return CLS[t]


ccode = {lg: [np.array([cls_of(t) for t in s], np.int8) for s in v] for lg, v in meas.items()}
log("tokens per side:", ntok_meas, "cal tokens", sum(len(x) for x in cal))

# ---------------------------------------------------------- per-sentence, per-class equalisation (seed 182)
rs = np.random.default_rng(182)
SEL = [dict() for _ in C.CLASSES]  # class index -> (lang, sid) -> bool mask over positions
nsel = {c: {} for c in C.CLASSES}
maxn = {c: 0 for c in C.CLASSES}
for g, gl in GROUPS.items():
    for sid in range(NS):
        pools = {lg: {"ALL": np.arange(len(meas[lg][sid])),
                      "LET": np.flatnonzero(ccode[lg][sid] == 1),
                      "NON": np.flatnonzero(ccode[lg][sid] == 2)} for lg in gl}
        for ci, c in enumerate(C.CLASSES[:3]):
            n = min(len(pools[lg][c]) for lg in gl)
            maxn[c] = max(maxn[c], n)
            for lg in gl:
                m = np.zeros(len(meas[lg][sid]), bool)
                m[rs.choice(pools[lg][c], n, replace=False)] = True
                SEL[ci][(lg, sid)] = m
        # NONtm: per letterless token type, n = min count over the group's sides
        ids = {lg: np.asarray(meas[lg][sid])[pools[lg]["NON"]] for lg in gl}
        common = set(ids[gl[0]].tolist())
        for lg in gl[1:]:
            common &= set(ids[lg].tolist())
        masks = {lg: np.zeros(len(meas[lg][sid]), bool) for lg in gl}
        ntm = 0
        for t in sorted(common):
            n = min(int((ids[lg] == t).sum()) for lg in gl)
            ntm += n
            for lg in gl:
                masks[lg][rs.choice(pools[lg]["NON"][ids[lg] == t], n, replace=False)] = True
        maxn["NONtm"] = max(maxn["NONtm"], ntm)
        for lg in gl:
            SEL[3][(lg, sid)] = masks[lg]
    for ci, c in enumerate(C.CLASSES):
        nsel[c][g] = int(sum(SEL[ci][(gl[0], s)].sum() for s in range(NS)))
assert maxn["NON"] <= 255 and maxn["NONtm"] <= 255, maxn
log("selected tokens per side by class/group:", nsel, "max per-sentence n:", maxn)

log("loading model", MODEL)
model = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.bfloat16, device_map={"": 0}, attn_implementation=ATTN)
model.eval()
layers = model.model.layers
gates = [ly.mlp.router if GPTOSS else ly.mlp.gate for ly in layers]
L, E, d = len(gates), gates[0].weight.shape[0], gates[0].weight.shape[1]
K = model.config.num_experts_per_tok
assert E <= 255
LMW = model.lm_head.weight
log(f"loaded: L={L} E={E} d={d} K={K} NR={NR}; mem {torch.cuda.memory_allocated() / 2**30:.1f} GiB; "
    f"bias {getattr(gates[0], 'bias', None) is not None}")

NTOK = sum(ntok_meas.values())
TOPK = np.zeros((L, NTOK, K), np.uint8)
PS = [np.zeros((L, NU, NR, E), np.uint16 if c in ("ALL", "LET") else np.uint8) for c in C.CLASSES]
META = {k: np.zeros(NTOK, np.int32) for k in ("lang", "sid", "pos", "inp", "pred")}
META["cls"] = np.zeros(NTOK, np.int8)
for c in C.CLASSES:
    META["sel_" + c] = np.zeros(NTOK, bool)
CUR = {"off": 0}


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


ST = {"mode": None}
CAL_H = [[] for _ in range(L)]
DET = {}
WALL, BALL = [None] * L, [None] * L
hookchk = torch.zeros(3, dtype=torch.float64)


def model_sel(out, m):
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
        S = logits.topk(K, -1).indices  # [n, NR, K]
        Smod = model_sel(out, m)
        bT = mod.bias.float() if GPTOSS else 0.0
        Sre = (hf @ mod.weight.float().T + bT).topk(K, -1).indices
        ohm = torch.zeros(n, E, device=dev).scatter_(1, Smod, 1.0)
        hookchk[0] += float(ohm.gather(1, Sre).sum() / K)
        hookchk[1] += float(ohm.gather(1, S[:, 0]).sum() / K)
        hookchk[2] += n
        B = ST["nseq"]
        ar = torch.arange(NR, device=dev)[None, :, None]
        for ci in range(len(C.CLASSES)):
            sel = ST["sel"][ci]
            rows = ST["rows"][sel]
            flat = ((rows[:, None, None] * NR + ar) * E + S[sel]).reshape(-1)
            cnt = torch.bincount(flat, minlength=B * NR * E).view(B, NR, E)
            PS[ci][l, ST["units_np"]] = cnt.to(torch.int32).cpu().numpy().astype(PS[ci].dtype)
        o = CUR["off"]
        TOPK[l, o:o + n] = S[:, 0].to(torch.uint8).cpu().numpy()
    return hook


for l, g in enumerate(gates):
    g.register_forward_hook(make_hook(l))


@torch.no_grad()
def run(seqs, b, mode, lang=0, lg=None):
    ids, am = make_inputs(seqs, b)
    m = am.reshape(-1).bool()
    ST.update(mode=mode, mask=m)
    if mode == "meas":
        Bn, T = am.shape
        rows = torch.arange(Bn, device=dev)[:, None].expand(Bn, T).reshape(-1)[m]
        selnp = [np.concatenate([SEL[ci][(lg, i)] for i in b]) for ci in range(len(C.CLASSES))]
        ST.update(rows=rows, nseq=Bn, sel=[torch.from_numpy(x).to(dev) for x in selnp],
                  units_np=lang * NS + np.array(b))
    hs = model.model(input_ids=ids, attention_mask=am, use_cache=False).last_hidden_state
    if mode == "meas":
        hs = hs.reshape(-1, d)[m]
        pred = torch.cat([(hs[i:i + 4096] @ LMW.T).argmax(-1) for i in range(0, hs.shape[0], 4096)])
        n = hs.shape[0]
        o = CUR["off"]
        META["lang"][o:o + n] = lang
        META["sid"][o:o + n] = np.concatenate([[i] * len(seqs[i]) for i in b])
        META["pos"][o:o + n] = np.concatenate([np.arange(len(seqs[i])) for i in b])
        META["inp"][o:o + n] = np.concatenate([seqs[i] for i in b])
        META["pred"][o:o + n] = pred.cpu().numpy()
        META["cls"][o:o + n] = np.concatenate([ccode[lg][i] for i in b])
        for ci, c in enumerate(C.CLASSES):
            META["sel_" + c][o:o + n] = selnp[ci]
        CUR["off"] = o + n
    ST["mode"] = None


# ---------------------------------------------------------- 1. calibration
log("calibration pass")
for b in batches(cal, range(len(cal))):
    run(cal, b, "cal")
log("calibration captured", sum(x.shape[0] for x in CAL_H[0]), "tokens/layer")

# ---------------------------------------------------------- 2. null routers (N_A Haar, N_B N1 load-matched)
diag = {"loadtv_B": np.zeros((L, D)), "cal_maxload": np.zeros((L, NR))}
for l in range(L):
    Hc = torch.cat(CAL_H[l]).to(dev).double()
    CAL_H[l] = None
    Wd = gates[l].weight.detach().double()
    bT = gates[l].bias.detach().double() if GPTOSS else torch.zeros(E, dtype=torch.float64, device=dev)
    target = mm.loads(mm.topk(Hc @ Wd.T + bT, K), E)
    st = mm.null_stats(Wd, Hc)
    gen = torch.Generator().manual_seed(182000 + l)
    WA, WB, bB = [], [], []
    for _ in range(D):
        A = torch.randn(d, d, generator=gen, dtype=torch.float64).to(dev)
        Q, R = torch.linalg.qr(A)
        WA.append(Wd @ (Q * torch.sign(torch.diagonal(R))))
    for j in range(D):
        Q = mm.haar(st["V"].shape[1], gen).to(dev)
        Wn = mm.null_router(Wd, Hc, "N1", Q, st)
        bn = mm.fit_bias(Hc, Wn, K, target)
        lc = mm.loads(mm.topk(Hc @ Wn.T + bn, K), E)
        diag["loadtv_B"][l, j] = float((lc / lc.sum() - target / target.sum()).abs().sum() / 2)
        WB.append(Wn); bB.append(bn)
    WALL[l] = torch.cat(WA + WB).float().contiguous()
    BALL[l] = torch.cat([bT] * D + bB).float().contiguous()
    allW = torch.cat([Wd, WALL[l].double()]).view(NR, E, d)
    allb = torch.cat([bT, BALL[l].double()]).view(NR, E)
    for r in range(NR):
        lc = mm.loads(mm.topk(Hc @ allW[r].T + allb[r], K), E)
        diag["cal_maxload"][l, r] = float(lc.max() / (K / E))
    del Hc, st
    if l % 8 == 0 or l == L - 1:
        log(f"nulls layer {l}: loadtv_B mean {diag['loadtv_B'][l].mean():.4f} max {diag['loadtv_B'][l].max():.4f}")
torch.cuda.empty_cache()

# ---------------------------------------------------------- 3. determinism
s0 = meas[langs[0]]
b0 = next(batches(s0, range(NS)))
run(s0, b0, "det")
run(s0, b0, "det")
det = [float((DET[l][0] == DET[l][1]).all(-1).float().mean()) for l in range(L)]
log(f"determinism: exact-set agreement min {min(det):.4f}")

# ---------------------------------------------------------- 4. measurement
for li, lg in enumerate(langs):
    seqs = meas[lg]
    for b in batches(seqs, range(NS)):
        run(seqs, b, "meas", lang=li, lg=lg)
    log(f"measured {lg} ({li + 1}/{NL}); hook fp32-vs-model {hookchk[0] / hookchk[2]:.5f} "
        f"T-vs-model {hookchk[1] / hookchk[2]:.5f}")
assert CUR["off"] == NTOK

# ---------------------------------------------------------- 5. save
for ci, c in enumerate(C.CLASSES):
    np.save(os.path.join(args.out, f"ps_{c}.npy"), PS[ci])
np.save(os.path.join(args.out, "topk_T.npy"), TOPK)
np.savez(os.path.join(args.out, "tokmeta.npz"), **META)
np.savez(os.path.join(args.out, "diag.npz"), det_exact=np.array(det), **diag)
meta = {"model": MODEL, "key": args.model, "langs": langs, "groups": GROUPS, "n_sent": NS, "n_cal": args.n_cal,
        "meas_split": args.meas_split, "cal_split": args.cal_split, "classes": C.CLASSES, "cls_code": CLS_CODE,
        "draws": D, "K": K, "E": E, "L": L, "d": d, "router_index": {"T": [0], "N_A": [1, D], "N_B": [1 + D, 2 * D]},
        "hook_agreement": float(hookchk[0] / hookchk[2]), "t_vs_model": float(hookchk[1] / hookchk[2]),
        "det_exact_min": min(det), "ntok": ntok_meas, "nsel": nsel, "max_sentence_n": maxn,
        "loadtv_B_mean": float(diag["loadtv_B"].mean()), "loadtv_B_max": float(diag["loadtv_B"].max()),
        "wall_s": time.time() - t0, "host": os.uname().nodename, "attn": ATTN, "gpu": torch.cuda.get_device_name(0)}
json.dump(meta, open(os.path.join(args.out, "meta.json"), "w"), indent=1)
log("done", json.dumps({k: meta[k] for k in ("hook_agreement", "t_vs_model", "det_exact_min", "loadtv_B_mean",
                                             "wall_s")}))
