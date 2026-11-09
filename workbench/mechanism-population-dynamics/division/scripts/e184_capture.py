#!/usr/bin/env python3
"""E184 capture (card: division/experiments/E184-token-level-claims-under-null.md). Based on e180_capture.py
(e178/e179/e180 scripts untouched).

Two English corpora: C_F = FLORES-200 dev eng_Latn (997 sentences, one sequence each); C_U = UD English EWT dev+test
passages (<= 400 words, documents not split across passages unless long; gold UPOS on the word-final token).
Calibration (N_B bias refit only): FLORES-200 devtest eng_Latn first 500 sentences.
Routers on the same hidden states: T | N_A (Haar O(d) rotation, 8) | N_B (N1, load-matched on calibration, 8).
Saved (in --out):
  topk.npy   uint8 [L, NTOK, 17, K]  top-k expert ids (descending; [...,0] = top-1) for every token and router
  tokmeta.npz  corpus, seq, pos, inp, pred (argmax lm_head), nxt (true next id, -1 at sequence end), upos (-1 if
               not a word-final token), word (global word index of the word whose final token this is, -1 otherwise)
  diag.npz, meta.json
Router index: 0 T | N_A 1..D | N_B D+1..2D.
"""
import argparse, json, os, sys, time
import numpy as np
import torch
import torch.nn.functional as F

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import moe_measure as mm  # noqa: E402
from ud_passages import sentences  # noqa: E402

FLORES = "/home/xiang/mechpop_cache/flores200/flores200_dataset"
UD = "/home/xiang/mechpop_cache/lingdata"
UPOS = ["ADJ", "ADP", "ADV", "AUX", "CCONJ", "DET", "INTJ", "NOUN", "NUM", "PART", "PRON", "PROPN", "PUNCT",
        "SCONJ", "SYM", "VERB", "X"]
MODELS = {"qwen3": ("Qwen/Qwen3-30B-A3B", "sdpa"),
          "gptoss": ("openai/gpt-oss-20b", "eager"),
          "olmoe": ("allenai/OLMoE-1B-7B-0125-Instruct", "sdpa")}
MAX_WORDS = 400

ap = argparse.ArgumentParser()
ap.add_argument("--model", required=True, choices=list(MODELS))
ap.add_argument("--out", required=True)
ap.add_argument("--n-cal", type=int, default=500)
ap.add_argument("--draws", type=int, default=8)
ap.add_argument("--batch-tokens", type=int, default=16384)
ap.add_argument("--smoke", action="store_true", help="tiny run: 40 FLORES sentences, 10 UD passages")
args = ap.parse_args()
os.makedirs(args.out, exist_ok=True)
D = args.draws
NR = 1 + 2 * D
MODEL, ATTN = MODELS[args.model]
GPTOSS = args.model == "gptoss"
dev = torch.device("cuda")
t0 = time.time()


def log(*a):
    print(f"[{time.strftime('%H:%M:%S')} +{time.time() - t0:7.1f}s]", *a, flush=True)


def read_flores(split, n):
    with open(f"{FLORES}/{split}/eng_Latn.{split}", encoding="utf-8") as f:
        return [x.rstrip("\n") for x in f][:n]


def ud_build():
    """passages: [text]; words: [(pid, start, end, upos)] -- same surface/multi-word rules as ud_passages.build."""
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
    texts = []
    for pid, p in enumerate(passages):
        texts.append(p["text"])
        for s, e, u in p["w"]:
            words.append((pid, s, e, u))
    return texts, words


from transformers import AutoModelForCausalLM, AutoTokenizer  # noqa: E402
tok = AutoTokenizer.from_pretrained(MODEL)
assert tok.is_fast

# ---------------------------------------------------------- corpora
fl = read_flores("dev", 40 if args.smoke else 997)
ud_texts, ud_words = ud_build()
if args.smoke:
    ud_texts = ud_texts[:10]
    ud_words = [w for w in ud_words if w[0] < 10]
SEQS, CORP = [], []
for s in fl:
    SEQS.append(tok(s, add_special_tokens=False)["input_ids"]); CORP.append(0)
ud_upos, ud_word = [], []
by_pid = {}
for wi, (pid, s, e, u) in enumerate(ud_words):
    by_pid.setdefault(pid, []).append((wi, s, e, u))
n_wf, n_bad, n_coll = 0, 0, 0
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
    SEQS.append(ids); CORP.append(1)
    ud_upos.append(up); ud_word.append(wd)
cal = [tok(s, add_special_tokens=False)["input_ids"] for s in read_flores("devtest", args.n_cal)]
NSEQ = len(SEQS)
lens = np.array([len(x) for x in SEQS])
off = np.concatenate([[0], np.cumsum(lens)])
NTOK = int(off[-1])
ntok_c = {c: int(lens[np.array(CORP) == i].sum()) for i, c in enumerate(["flores", "ud"])}
log(f"sequences {NSEQ} (flores {CORP.count(0)}, ud {CORP.count(1)}); tokens {ntok_c}; cal tokens "
    f"{sum(len(x) for x in cal)}; UD words {len(ud_words)}, word-final tokens {n_wf}, run past word end {n_bad}, "
    f"collisions {n_coll}")

META = {"corpus": np.repeat(np.array(CORP, np.int8), lens), "seq": np.repeat(np.arange(NSEQ, dtype=np.int32), lens),
        "pos": np.concatenate([np.arange(n, dtype=np.int32) for n in lens]),
        "inp": np.concatenate([np.array(x, np.int64) for x in SEQS]),
        "pred": np.zeros(NTOK, np.int64),
        "nxt": np.concatenate([np.array(x[1:] + [-1], np.int64) for x in SEQS]),
        "upos": np.concatenate([np.full(len(x), -1, np.int32) for x in SEQS[:CORP.count(0)]] + ud_upos),
        "word": np.concatenate([np.full(len(x), -1, np.int32) for x in SEQS[:CORP.count(0)]] + ud_word)}

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
TOPK = np.zeros((L, NTOK, NR, K), np.uint8)


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
        TOPK[l, ST["gidx"]] = S.to(torch.uint8).cpu().numpy()
    return hook


for l, g in enumerate(gates):
    g.register_forward_hook(make_hook(l))


@torch.no_grad()
def run(seqs, b, mode):
    ids, am = make_inputs(seqs, b)
    m = am.reshape(-1).bool()
    ST.update(mode=mode, mask=m)
    if mode == "meas":
        # global token index of each kept (row-major, unpadded) position
        ST["gidx"] = np.concatenate([np.arange(off[i], off[i + 1]) for i in b])
    hs = model.model(input_ids=ids, attention_mask=am, use_cache=False).last_hidden_state
    if mode == "meas":
        hs = hs.reshape(-1, d)[m]
        pred = torch.cat([(hs[i:i + 4096] @ LMW.T).argmax(-1) for i in range(0, hs.shape[0], 4096)])
        META["pred"][ST["gidx"]] = pred.cpu().numpy()
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
    gen = torch.Generator().manual_seed(184000 + l)
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

# ---------------------------------------------------------- 3. determinism (same FLORES batch twice)
b0 = next(batches(SEQS, range(CORP.count(0))))
run(SEQS, b0, "det")
run(SEQS, b0, "det")
det = [float((DET[l][0] == DET[l][1]).all(-1).float().mean()) for l in range(L)]
log(f"determinism: exact-set agreement min {min(det):.4f}")

# ---------------------------------------------------------- 4. measurement
for name, idx in (("flores", range(CORP.count(0))), ("ud", range(CORP.count(0), NSEQ))):
    for b in batches(SEQS, list(idx)):
        run(SEQS, b, "meas")
    log(f"measured {name}; hook fp32-vs-model {hookchk[0] / hookchk[2]:.5f} T-vs-model {hookchk[1] / hookchk[2]:.5f}")

# ---------------------------------------------------------- 5. save
np.save(os.path.join(args.out, "topk.npy"), TOPK)
np.savez(os.path.join(args.out, "tokmeta.npz"), **META)
np.savez(os.path.join(args.out, "diag.npz"), det_exact=np.array(det), **diag)
meta = {"model": MODEL, "key": args.model, "n_cal": args.n_cal, "draws": D, "K": K, "E": E, "L": L, "d": d,
        "router_index": {"T": [0], "N_A": [1, D], "N_B": [1 + D, 2 * D]}, "upos": UPOS,
        "hook_agreement": float(hookchk[0] / hookchk[2]), "t_vs_model": float(hookchk[1] / hookchk[2]),
        "det_exact_min": min(det), "ntok": ntok_c, "nseq": {"flores": CORP.count(0), "ud": CORP.count(1)},
        "ud_words": len(ud_words), "ud_word_final": n_wf, "ud_run_past_end": n_bad, "ud_collisions": n_coll,
        "loadtv_B_mean": float(diag["loadtv_B"].mean()), "loadtv_B_max": float(diag["loadtv_B"].max()),
        "smoke": args.smoke, "wall_s": time.time() - t0, "host": os.uname().nodename, "attn": ATTN,
        "gpu": torch.cuda.get_device_name(0)}
json.dump(meta, open(os.path.join(args.out, "meta.json"), "w"), indent=1)
log("done", json.dumps({k: meta[k] for k in ("hook_agreement", "t_vs_model", "det_exact_min", "loadtv_B_mean",
                                             "wall_s")}))
