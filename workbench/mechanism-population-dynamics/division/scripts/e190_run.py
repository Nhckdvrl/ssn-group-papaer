#!/usr/bin/env python3
"""E190 (card: division/experiments/E190-contextual-routing-functional-value.md): functional value of the context
dependence of trained routing, by inference-time replacement of the top-k expert SET.

Phases
  prep  : build fit / eval corpora (tokenised), calibration pass (router inputs for the N_B null), N_B construction,
          fit pass (per (layer, id) expert counts + mean softmax; T and N_B top-1 on fit tokens for H(e|id)),
          clean eval pass (T top-k + gate values per layer; NLL), unpatched-model NLL (positive control), donors.
  cond  : run the intervention conditions (sharded: --shard i --nshard n), one NLL array per condition.
Everything is written under --out (node-local /tmp). Model-specific: olmoe / qwen3_moe (block forward patched) and
deepseek_v2 (gate forward patched; shared experts untouched).
"""
import argparse, json, os, re, sys, time
import numpy as np
import torch
import torch.nn.functional as F

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import moe_measure as mm  # noqa: E402
from ud_passages import sentences  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("phase", choices=["prep", "cond"])
ap.add_argument("--model-path", required=True)
ap.add_argument("--key", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--data", default="/tmp/xiang_e190/data")
ap.add_argument("--batch-tokens", type=int, default=16384)
ap.add_argument("--shard", type=int, default=0)
ap.add_argument("--nshard", type=int, default=1)
ap.add_argument("--subset", default="full", help="full | small (I0/I2x5/I3/I5 x all+bands; non-OLMoE models) | posthoc")
ap.add_argument("--smoke", action="store_true")
args = ap.parse_args()
OUT = args.out
os.makedirs(OUT, exist_ok=True)
t0 = time.time()


def log(*a):
    print(f"[{time.strftime('%H:%M:%S')} +{time.time() - t0:7.1f}s]", *a, flush=True)


UPOS = ["ADJ", "ADP", "ADV", "AUX", "CCONJ", "DET", "INTJ", "NOUN", "NUM", "PART", "PRON", "PROPN", "PUNCT",
        "SCONJ", "SYM", "VERB", "X"]
SIDES = ["srp_Cyrl", "srp_Latn", "hrv_Latn", "bos_Latn", "slv_Latn", "ces_Latn", "pol_Latn", "mkd_Cyrl", "bul_Cyrl",
         "ukr_Cyrl", "rus_Cyrl", "hin_Deva", "urd_Arab", "npi_Deva", "mar_Deva", "snd_Arab", "pes_Arab", "zho_Hans",
         "zho_Hant", "yue_Hant", "eng_Latn"]
ENG = 20
MAXLEN = 512
BANDS = {"olmoe": {"first": [0, 1], "mid": list(range(2, 12)), "last": list(range(12, 16))},
         "deepseek_v2": {"first": [0, 1], "mid": list(range(4, 19)), "last": list(range(19, 26))},
         "qwen3_moe": {"first": list(range(0, 4)), "mid": list(range(7, 35)), "last": list(range(35, 48))}}

from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer  # noqa: E402
tok = AutoTokenizer.from_pretrained(args.model_path)


# ------------------------------------------------------------------ corpora
def read_side(split, lang, n):
    d = args.data
    path = f"{d}/srp_Latn/{split}/srp_Latn.{split}" if lang == "srp_Latn" else f"{d}/flores200_dataset/{split}/{lang}.{split}"
    with open(path, encoding="utf-8") as f:
        return [x.rstrip("\n") for x in f][:n]


def wikitext_detok(s):
    s = s.replace(" @-@ ", "-").replace(" @,@ ", ",").replace(" @.@ ", ".")
    for p in (" : ", " ; ", " . ", " ! ", " ? ", " , "):
        s = s.replace(p, p[1:])
    s = re.sub(r"\(\s*([^\)]*?)\s*\)", r"(\1)", s)
    s = re.sub(r"\[\s*([^\]]*?)\s*\]", r"[\1]", s)
    s = re.sub(r'"\s*([^"]*?)\s*"', r'"\1"', s)
    s = s.replace(" 's", "'s").replace("s ' ", "s' ").replace(" n't", "n't").replace(" 're", "'re")
    s = s.replace(" 've", "'ve").replace(" 'll", "'ll").replace(" 'd", "'d").replace(" 'm", "'m")
    s = re.sub(r" ([.,;:!?])", r"\1", s)
    return s.strip()


def wiki_paragraphs(fname):
    import pyarrow.parquet as pq
    lines = pq.read_table(f"{args.data}/wikitext/{fname}.parquet").column(0).to_pylist()
    return [wikitext_detok(x) for x in lines if x.strip() and not x.strip().startswith("=")]


def ud_build(split):
    """E184/E186 passage rules on one UD file; returns texts and word spans (pid, start, end, upos)."""
    passages = []
    cur = None
    for newdoc, text, toks in sentences(f"{args.data}/lingdata/en_ewt-ud-{split}.conllu"):
        if cur is None or newdoc or cur["n"] + len(toks) > 400:
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
    return passages


def ud_encode(passages):
    seqs, ups = [], []
    for p in passages:
        enc = tok(p["text"], add_special_tokens=False, return_offsets_mapping=True)
        ids, offs = enc["input_ids"][:MAXLEN], enc["offset_mapping"][:MAXLEN]
        up = np.full(len(ids), -1, np.int32)
        for s, e, u in p["w"]:
            for t, (a, b) in enumerate(offs):
                if a <= e - 1 < b:
                    if b <= e:
                        up[t] = UPOS.index(u)
                    break
        seqs.append(ids); ups.append(up)
    return seqs, ups


def enc(texts):
    return [tok(t, add_special_tokens=False)["input_ids"][:MAXLEN] for t in texts]


def build_corpora():
    S = {}
    # fit
    seqs, corp, side = [], [], []
    for si, lg in enumerate(SIDES):
        e = enc(read_side("dev", lg, 30 if args.smoke else 997))
        seqs += e; corp += [0 if si != ENG else 1] * len(e); side += [si] * len(e)
    ud_dev, _ = ud_encode(ud_build("dev"))
    ud_dev = ud_dev[:5] if args.smoke else ud_dev
    seqs += ud_dev; corp += [3] * len(ud_dev); side += [-1] * len(ud_dev)
    wp = wiki_paragraphs("train-00000-of-00002")
    rng = np.random.default_rng(190)
    n = 0
    target = 20000 if args.smoke else 500000
    for i in rng.permutation(len(wp)):
        x = tok(wp[i], add_special_tokens=False)["input_ids"][:MAXLEN]
        if len(x) < 2:
            continue
        seqs.append(x); corp.append(2); side.append(-1)
        n += len(x)
        if n >= target:
            break
    S["fit"] = (seqs, np.array(corp), np.array(side), None)
    # eval
    seqs, corp, side, ups = [], [], [], []
    for si, lg in enumerate(SIDES):
        e = enc(read_side("devtest", lg, (10 if args.smoke else 100) if si != ENG else (20 if args.smoke else 200)))
        seqs += e; corp += [0 if si != ENG else 1] * len(e); side += [si] * len(e)
        ups += [np.full(len(x), -1, np.int32) for x in e]
    wp = wiki_paragraphs("test-00000-of-00001")
    n = 0
    target = 8000 if args.smoke else 80000
    for p in wp:
        x = tok(p, add_special_tokens=False)["input_ids"][:MAXLEN]
        if len(x) < 2:
            continue
        seqs.append(x); corp.append(2); side.append(-1); ups.append(np.full(len(x), -1, np.int32))
        n += len(x)
        if n >= target:
            break
    ud_t, ud_u = ud_encode(ud_build("test"))
    if args.smoke:
        ud_t, ud_u = ud_t[:5], ud_u[:5]
    seqs += ud_t; corp += [3] * len(ud_t); side += [-1] * len(ud_t); ups += ud_u
    S["eval"] = (seqs, np.array(corp), np.array(side), ups)
    return S


def flat_meta(seqs, corp, side, ups):
    lens = np.array([len(x) for x in seqs])
    keep = lens > 0
    assert keep.all()
    M = {"corpus": np.repeat(corp.astype(np.int8), lens), "side": np.repeat(side.astype(np.int8), lens),
         "seq": np.repeat(np.arange(len(seqs), dtype=np.int32), lens),
         "pos": np.concatenate([np.arange(n, dtype=np.int32) for n in lens]),
         "inp": np.concatenate([np.array(x, np.int64) for x in seqs]),
         "prev": np.concatenate([np.array([-1] + x[:-1], np.int64) for x in seqs]),
         "nxt": np.concatenate([np.array(x[1:] + [-1], np.int64) for x in seqs]),
         "lens": lens}
    if ups is not None:
        M["upos"] = np.concatenate(ups)
    return M


# ------------------------------------------------------------------ model + patch
cfg = AutoConfig.from_pretrained(args.model_path)
ARCH = cfg.model_type
model = AutoModelForCausalLM.from_pretrained(args.model_path, dtype=torch.bfloat16, device_map="auto",
                                             attn_implementation="sdpa")
model.eval()
BLOCKS = []
for li, ly in enumerate(model.model.layers):
    blk = getattr(ly, "mlp", None)
    if blk is not None and hasattr(blk, "experts"):
        BLOCKS.append((li, blk))
L = len(BLOCKS)
if ARCH == "deepseek_v2":
    E, d = BLOCKS[0][1].gate.weight.shape
    assert cfg.topk_method == "greedy"
    NORM = False
else:
    E, d = BLOCKS[0][1].gate.weight.shape
    NORM = bool(cfg.norm_topk_prob)
K = cfg.num_experts_per_tok
DEV = [b.gate.weight.device for _, b in BLOCKS]
INDEV = model.model.embed_tokens.weight.device
log(f"loaded {ARCH} L={L} E={E} K={K} d={d} norm={NORM} devices={sorted(set(map(str, DEV)))}")
ST = {"mode": None}
CTL = {}       # condition control
REC = {}       # recorders


def route(j, h, logits):
    """returns (sel [n,K] long, w [n,K] float32 before model-specific normalisation / scaling)."""
    probs = F.softmax(logits.float(), dim=-1)
    # DeepSeek-V2 dispatches topk(sorted=False); keep that order for un-replaced rows so I0 is bitwise the original
    # (補登記 11-11: the first DSV2 prep failed the I0-vs-original control with sorted=True, mean |dNLL| .027)
    w0, sel0 = probs.topk(K, dim=-1, sorted=(ARCH != "deepseek_v2"))
    mode = ST["mode"]
    if mode is None:
        return sel0, w0
    m = ST["mask_dev"][DEV[j]]
    if mode == "cal":
        REC["cal"][j].append(h[m][ST["calrows_dev"][DEV[j]]].float().cpu())
        return sel0, w0
    gidx = ST["gidx_dev"][DEV[j]]
    if mode == "fit":
        inp = ST["inp_dev"][DEV[j]]
        s = sel0[m]
        R = REC["fit"]
        if R["cnt"] is not None:
          R["cnt"][j].view(-1).index_add_(0, (inp[:, None] * E + s).reshape(-1), torch.ones(s.numel(), device=s.device))
          R["psum"][j].index_add_(0, inp, probs[m])
        R["t1"][j][gidx] = probs[m].argmax(-1).to(torch.uint8)
        nb = (h[m].float() @ NB_W[j].T + NB_B[j]).argmax(-1)
        R["n1"][j][gidx] = nb.to(torch.uint8)
        return sel0, w0
    if mode == "clean":
        ws, o = w0[m].sort(-1, descending=True)
        REC["sel"][j][gidx] = sel0[m].gather(1, o).to(torch.int16)
        REC["w"][j][gidx] = ws
        return sel0, w0
    if mode == "cond" and j in CTL["layers"]:
        pr = probs[m]
        new = sel0[m].clone()
        kind = CTL["kind"]
        if kind == "I6":
            tsel = (h[m].float() @ NB_W[j].T + NB_B[j]).topk(K, -1).indices
            tval = torch.ones(new.shape[0], dtype=torch.bool, device=new.device)
            tw = None
        elif kind == "I1":
            ids = ST["inp_dev"][DEV[j]]
            tsel = LOOK_SEL[j][ids].long()
            tval = LOOK_OK[j][ids]
            tw = LOOK_P[j][ids].float().gather(1, tsel) if CTL["w2"] else None
        else:  # donor-based (I0x self, I2-I5)
            dn = CTL["donor_dev"][DEV[j]][gidx]
            tval = dn >= 0
            dd = dn.clamp_min(0)
            tsel = CLEAN_SEL[j][dd].long()
            tw = CLEAN_W[j][dd] if CTL["w2"] else None
        if CTL["restrict"] is not None:
            tval = tval & CTL["restrict_dev"][DEV[j]][gidx]
        new[tval] = tsel[tval]
        if CTL["w2"] and tw is not None:
            wr = pr.gather(1, new)
            wr[tval] = tw[tval]
        else:
            wr = pr.gather(1, new)
        sel = sel0.clone(); sel[m] = new
        w = w0.clone(); w[m] = wr
        # hook check: the set handed to dispatch equals the target set on replaced rows
        a = sel[m][tval].sort(-1).values
        b = tsel[tval].sort(-1).values
        REC["chk"][0] += int((a == b).all(-1).sum()); REC["chk"][1] += int(tval.sum())
        REC["chk"][2] += int(tval.numel())
        return sel, w
    return sel0, w0


def block_forward(self, hidden_states):
    bsz, sl, hd = hidden_states.shape
    h = hidden_states.view(-1, hd)
    router_logits = self.gate(h)
    sel, w = route(self._e190_j, h, router_logits)
    if NORM:
        w = w / w.sum(-1, keepdim=True)
    w = w.to(h.dtype)
    out = torch.zeros((bsz * sl, hd), dtype=h.dtype, device=h.device)
    emask = F.one_hot(sel, num_classes=E).permute(2, 1, 0)
    hit = torch.greater(emask.sum(dim=(-1, -2)), 0).nonzero()
    for ei in hit:
        ei = int(ei)
        idx, top_x = torch.where(emask[ei])
        cur = self.experts[ei](h[top_x]) * w[top_x, idx, None]
        out.index_add_(0, top_x, cur.to(h.dtype))
    return out.reshape(bsz, sl, hd), router_logits


def dsv2_gate_forward(self, hidden_states):
    hs = hidden_states.view(-1, hidden_states.shape[-1])
    logits = F.linear(hs.type(torch.float32), self.weight.type(torch.float32), None)
    sel, w = route(self._e190_j, hs, logits)
    return sel, w * self.routed_scaling_factor


ORIG = {}
for j, (li, blk) in enumerate(BLOCKS):
    if ARCH == "deepseek_v2":
        blk.gate._e190_j = j
        ORIG[j] = blk.gate.forward
    else:
        blk._e190_j = j
        ORIG[j] = blk.forward


def set_patch(on):
    import types
    for j, (li, blk) in enumerate(BLOCKS):
        if ARCH == "deepseek_v2":
            blk.gate.forward = types.MethodType(dsv2_gate_forward, blk.gate) if on else ORIG[j]
        else:
            blk.forward = types.MethodType(block_forward, blk) if on else ORIG[j]


# ------------------------------------------------------------------ running
def batches(lens):
    order = np.argsort(lens, kind="stable")
    cur = []
    for i in order:
        if cur and (len(cur) + 1) * lens[i] > args.batch_tokens:
            yield cur
            cur = []
        cur.append(int(i))
    if cur:
        yield cur


@torch.no_grad()
def run_corpus(seqs, M, mode, nll=False, calrows=None):
    off = np.concatenate([[0], np.cumsum(M["lens"])])
    out = np.full(len(M["inp"]), np.nan, np.float32) if nll else None
    devs = sorted(set(DEV), key=str)
    for b in batches(M["lens"]):
        T = max(len(seqs[i]) for i in b)
        ids = torch.full((len(b), T), tok.pad_token_id or 0, dtype=torch.long)
        am = torch.zeros((len(b), T), dtype=torch.long)
        for r, i in enumerate(b):
            ids[r, :len(seqs[i])] = torch.tensor(seqs[i]); am[r, :len(seqs[i])] = 1
        m = am.reshape(-1).bool()
        gidx = np.concatenate([np.arange(off[i], off[i + 1]) for i in b])
        ST.clear()
        ST["mode"] = mode
        ST["mask_dev"] = {dv: m.to(dv) for dv in devs}
        ST["gidx_dev"] = {dv: torch.from_numpy(gidx).to(dv) for dv in devs}
        ST["inp_dev"] = {dv: torch.from_numpy(M["inp"][gidx]).to(dv) for dv in devs}
        if calrows is not None:
            cr = torch.from_numpy(calrows[gidx])
            ST["calrows_dev"] = {dv: cr.to(dv) for dv in devs}
        hs = model.model(input_ids=ids.to(INDEV), attention_mask=am.to(INDEV), use_cache=False).last_hidden_state
        if nll:
            hs = hs.reshape(-1, hs.shape[-1])[m.to(hs.device)]
            tg = torch.from_numpy(M["nxt"][gidx]).to(hs.device)
            res = []
            for i in range(0, hs.shape[0], 4096):
                lp = torch.log_softmax(model.lm_head(hs[i:i + 4096]).float(), -1)
                t = tg[i:i + 4096]
                res.append(torch.where(t >= 0, -lp.gather(1, t.clamp_min(0)[:, None])[:, 0],
                                       torch.full_like(t, float("nan"), dtype=torch.float32)))
            out[gidx] = torch.cat(res).cpu().numpy()
        ST["mode"] = None
    return out


def derange_groups(keys, seed):
    """donor index per token: next member of a random cycle within its key group; -1 for singleton groups."""
    rng = np.random.default_rng(seed)
    N = len(keys)
    order = np.lexsort((rng.random(N), keys))
    ks = keys[order]
    start = np.r_[True, ks[1:] != ks[:-1]]
    gid = np.cumsum(start) - 1
    gstart = np.flatnonzero(start)
    gsize = np.diff(np.r_[gstart, N])
    pos_in = np.arange(N) - gstart[gid]
    nxt_pos = gstart[gid] + (pos_in + 1) % gsize[gid]
    donor = np.full(N, -1, np.int64)
    ok = gsize[gid] >= 2
    donor[order[ok]] = order[nxt_pos[ok]]
    return donor


def posbin(p):
    return np.digitize(p, [1, 4, 16, 64, 256])


def make_donors(M, seed, kind):
    inp, prev = M["inp"], M["prev"]
    if kind == "I2":
        return derange_groups(inp, seed)
    if kind == "I3":
        key = inp * 200003 + (prev + 1)
        dn = derange_groups(key, seed)
        fb = dn < 0
        d2 = derange_groups(inp, seed)
        dn[fb] = d2[fb]
        return dn, float(fb.mean())
    if kind == "I4":
        key = inp * 8 + posbin(M["pos"])
        dn = derange_groups(key, seed)
        fb = dn < 0
        d2 = derange_groups(inp, seed)
        dn[fb] = d2[fb]
        return dn, float(fb.mean())
    if kind == "I5":
        return derange_groups(np.zeros(len(inp), np.int64), seed)
    raise ValueError(kind)


PREP = os.path.join(OUT, "prep.pt")
NB_W, NB_B = None, None
if args.phase == "prep":
    set_patch(True)
    S = build_corpora()
    MF = flat_meta(*S["fit"]); ME = flat_meta(*S["eval"])
    log(f"fit tokens {len(MF['inp'])} seqs {len(MF['lens'])}; eval tokens {len(ME['inp'])} seqs {len(ME['lens'])}; "
        f"eval by corpus {np.bincount(ME['corpus'])}")
    # calibration rows: random fit sequences until >= 60k tokens (seed 190)
    rng = np.random.default_rng(190)
    perm = rng.permutation(len(MF["lens"]))
    ncal = int(np.searchsorted(np.cumsum(MF["lens"][perm]), 3000 if args.smoke else 60000)) + 1
    calseq = np.zeros(len(MF["lens"]), bool); calseq[perm[:ncal]] = True
    calrows = np.repeat(calseq, MF["lens"])
    REC["cal"] = [[] for _ in range(L)]
    run_corpus(S["fit"][0], MF, "cal", calrows=calrows)
    NB_W, NB_B, nbtv = [], [], []
    for j in range(L):
        dv = DEV[j]
        Hc = torch.cat(REC["cal"][j]).to(dv).double()
        Wd = BLOCKS[j][1].gate.weight.detach().double()
        target = mm.loads(mm.topk(Hc @ Wd.T, K), E)
        st = mm.null_stats(Wd, Hc)
        gen = torch.Generator().manual_seed(190000 + j)
        Q = mm.haar(st["V"].shape[1], gen).to(dv)
        Wn = mm.null_router(Wd, Hc, "N1", Q, st)
        bn = mm.fit_bias(Hc, Wn, K, target)
        lc = mm.loads(mm.topk(Hc @ Wn.T + bn, K), E)
        nbtv.append(float((lc / lc.sum() - target / target.sum()).abs().sum() / 2))
        NB_W.append(Wn.float().contiguous()); NB_B.append(bn.float().contiguous())
        REC["cal"][j] = None
        del Hc, st
    log(f"N_B built; calibration load TV mean {np.mean(nbtv):.4f} max {np.max(nbtv):.4f}")
    # fit pass
    V = max(len(tok), int(MF["inp"].max()) + 1, int(ME["inp"].max()) + 1, model.config.vocab_size)
    NF = len(MF["inp"])
    LK = args.subset == "full"
    REC["fit"] = {"cnt": [torch.zeros(V, E, device=DEV[j]) for j in range(L)] if LK else None,
                  "psum": [torch.zeros(V, E, device=DEV[j]) for j in range(L)] if LK else None,
                  "t1": [torch.zeros(NF, dtype=torch.uint8, device=DEV[j]) for j in range(L)],
                  "n1": [torch.zeros(NF, dtype=torch.uint8, device=DEV[j]) for j in range(L)]}
    run_corpus(S["fit"][0], MF, "fit")
    idcnt = np.bincount(MF["inp"], minlength=V)
    if LK:
        cnt = np.stack([c.cpu().numpy() for c in REC["fit"]["cnt"]])            # [L, V, E] (slot counts)
        psum = np.stack([c.cpu().numpy() for c in REC["fit"]["psum"]])
    else:   # small subset: no I1 -> dummy lookup (never used)
        cnt = np.zeros((L, 1, E), np.float32); psum = np.zeros((L, 1, E), np.float32)
    t1 = np.stack([c.cpu().numpy() for c in REC["fit"]["t1"]]); n1 = np.stack([c.cpu().numpy() for c in REC["fit"]["n1"]])
    REC["fit"] = None
    # I1 lookup: k most frequently selected experts per (layer, id); valid if id count >= 5
    look_sel = np.argsort(-cnt + 1e-6 * np.arange(E)[None, None, :], axis=-1, kind="stable")[..., :K].astype(np.int16)
    look_ok = np.broadcast_to(idcnt[None, :] >= 5, (L, V)).copy() if LK else np.zeros((L, 1), bool)
    look_p = (psum / np.maximum(idcnt[:psum.shape[1]], 1)[None, :, None]).astype(np.float16)
    # H(e|id): equal n = 30 per id (fit count >= 30), seed 190, T and N_B top-1
    elig = np.flatnonzero(idcnt >= 30)
    rng = np.random.default_rng(190)
    occ = {}
    order = np.argsort(MF["inp"], kind="stable")
    st_ = np.searchsorted(MF["inp"][order], elig)
    samp = np.stack([order[st_[i] + rng.choice(idcnt[e], 30, replace=False)] for i, e in enumerate(elig)])
    def Hrows(top1):
        v = top1[:, samp]                                                   # [L, nid, 30]
        oh = np.zeros((L, len(elig), E), np.float32)
        for l in range(L):
            np.add.at(oh[l], (np.repeat(np.arange(len(elig)), 30), v[l].ravel()), 1)
        p = oh / 30
        with np.errstate(divide="ignore", invalid="ignore"):
            return -(np.where(p > 0, p * np.log2(p), 0)).sum(-1)              # [L, nid]
    H_T, H_NB = Hrows(t1), Hrows(n1)
    # clean eval pass + unpatched original
    NE = len(ME["inp"])
    REC["sel"] = [torch.zeros(NE, K, dtype=torch.int16, device=DEV[j]) for j in range(L)]
    REC["w"] = [torch.zeros(NE, K, dtype=torch.float32, device=DEV[j]) for j in range(L)]
    nll0 = run_corpus(S["eval"][0], ME, "clean", nll=True)
    nll0b = run_corpus(S["eval"][0], ME, None, nll=True)
    set_patch(False)
    nll_orig = run_corpus(S["eval"][0], ME, None, nll=True)
    set_patch(True)
    clean_sel = np.stack([x.cpu().numpy() for x in REC["sel"]]); clean_w = np.stack([x.cpu().numpy() for x in REC["w"]])
    v = np.isfinite(nll0)
    pc = {"I0_vs_orig_mean_abs": float(np.abs(nll0[v] - nll_orig[v]).mean()),
          "I0_vs_orig_mean": float((nll0[v] - nll_orig[v]).mean()),
          "I0_vs_orig_max_abs": float(np.abs(nll0[v] - nll_orig[v]).max()),
          "I0_rerun_max_abs": float(np.abs(nll0[v] - nll0b[v]).max()),
          "nll_I0_mean": float(nll0[v].mean()), "nll_orig_mean": float(nll_orig[v].mean()),
          "nb_cal_tv_mean": float(np.mean(nbtv)), "nb_cal_tv_max": float(np.max(nbtv)),
          "fit_tokens": int(NF), "eval_tokens": int(NE), "cal_tokens": int(calrows.sum())}
    log("positive control", json.dumps(pc))
    np.save(os.path.join(OUT, "nll_I0.npy"), nll0); np.save(os.path.join(OUT, "nll_orig.npy"), nll_orig)
    np.save(os.path.join(OUT, "nll_I0_rerun.npy"), nll0b)
    # donors
    don = {}
    for s in range(190, 195):
        don[f"I2_s{s}"] = make_donors(ME, s, "I2")
    rates = {"I2_replaced": float((don["I2_s190"] >= 0).mean())}
    for k in ("I3", "I4"):
        don[f"{k}_s190"], rates[f"{k}_fallback"] = make_donors(ME, 190, k)
    don["I5_s190"] = make_donors(ME, 190, "I5")
    if LK:
        rates["I1_lookup_ok"] = float(look_ok[0][ME["inp"]].mean())
    pc.update(rates)
    torch.save({"MF": MF, "ME": ME, "seqs_eval": S["eval"][0], "NB_W": [x.cpu() for x in NB_W],
                "NB_B": [x.cpu() for x in NB_B], "look_sel": look_sel, "look_ok": look_ok, "look_p": look_p,
                "idcnt": idcnt, "H_ids": elig, "H_T": H_T, "H_NB": H_NB, "clean_sel": clean_sel, "clean_w": clean_w,
                "donors": don, "pc": pc, "arch": ARCH, "L": L, "E": E, "K": K}, PREP)
    json.dump(pc, open(os.path.join(OUT, "prep_pc.json"), "w"), indent=1)
    log("prep done", json.dumps(rates))
    sys.exit(0)

# ------------------------------------------------------------------ conditions
P = torch.load(PREP, weights_only=False)
ME, seqs_eval = P["ME"], P["seqs_eval"]
NB_W = [P["NB_W"][j].to(DEV[j]) for j in range(L)]
NB_B = [P["NB_B"][j].to(DEV[j]) for j in range(L)]
CLEAN_SEL = [torch.from_numpy(P["clean_sel"][j]).to(DEV[j]) for j in range(L)]
CLEAN_W = [torch.from_numpy(P["clean_w"][j]).to(DEV[j]) for j in range(L)]
LOOK_SEL = [torch.from_numpy(P["look_sel"][j]).to(DEV[j]) for j in range(L)]
LOOK_OK = [torch.from_numpy(P["look_ok"][j]).to(DEV[j]) for j in range(L)]
LOOK_P = [torch.from_numpy(P["look_p"][j]).to(DEV[j]) for j in range(L)]
# H terciles over eval tokens (mid-band T H, token-weighted), for the class-restricted I2
bands = BANDS[ARCH]
Hmid = np.full(len(P["idcnt"]), np.nan)
Hmid[P["H_ids"]] = P["H_T"][bands["mid"]].mean(0)
Htok = Hmid[ME["inp"]]
qs = np.nanquantile(Htok, [1 / 3, 2 / 3])
terc = np.where(np.isnan(Htok), -1, np.digitize(Htok, qs))
set_patch(True)

LAYERSETS = {"all": list(range(L)), **bands}
conds = []
if args.subset == "posthoc":   # POST-HOC (11-11, after the OLMoE tables): leave position-0 tokens (no BOS -> first
    # token = attention sink / sentence-initial routing) un-replaced
    p1 = ME["pos"] >= 1
    for bn_ in ("all", "mid"):
        if P["look_sel"].shape[1] > 1:
            conds.append((f"{bn_}_I1_pos1", LAYERSETS[bn_], "I1", None, False, p1))
        conds.append((f"{bn_}_I2_s190_pos1", LAYERSETS[bn_], "I2", "I2_s190", False, p1))
        conds.append((f"{bn_}_I3_pos1", LAYERSETS[bn_], "I3", "I3_s190", False, p1))
        conds.append((f"{bn_}_I5_pos1", LAYERSETS[bn_], "I5", "I5_s190", False, p1))
    conds.append(("L0_I2_s190_pos1", [0], "I2", "I2_s190", False, p1))
    LAYERSETS = {}
if args.subset == "full":
    for l in range(L):
        conds.append((f"L{l}_I1", [l], "I1", None, False, None))
        for s in range(190, 195):
            conds.append((f"L{l}_I2_s{s}", [l], "I2", f"I2_s{s}", False, None))
        for k in ("I3", "I4", "I5"):
            conds.append((f"L{l}_{k}", [l], k, f"{k}_s190", False, None))
        conds.append((f"L{l}_I6", [l], "I6", None, False, None))
for bn, ls in LAYERSETS.items():
    conds.append((f"{bn}_I0x", ls, "I0x", "self", False, None))
    if args.subset == "full":
        conds.append((f"{bn}_I1", ls, "I1", None, False, None))
    for s in range(190, 195):
        conds.append((f"{bn}_I2_s{s}", ls, "I2", f"I2_s{s}", False, None))
    ks = ("I3", "I4", "I5") if args.subset == "full" else ("I3", "I5")
    for k in ks:
        conds.append((f"{bn}_{k}", ls, k, f"{k}_s190", False, None))
    if args.subset == "full":
        conds.append((f"{bn}_I6", ls, "I6", None, False, None))
        conds.append((f"{bn}_I1_w2", ls, "I1", None, True, None))
        for k in ("I2", "I3", "I4", "I5"):
            conds.append((f"{bn}_{k}_w2", ls, k, f"{k}_s190", True, None))
for t, nm in enumerate(("Hlo", "Hmid", "Hhi") if args.subset != "posthoc" else ()):
    conds.append((f"all_I2_s190_{nm}", LAYERSETS["all"], "I2", "I2_s190", False, terc == t))
mine = [c for i, c in enumerate(conds) if i % args.nshard == args.shard]
log(f"{len(conds)} conditions; shard {args.shard}/{args.nshard}: {len(mine)}")
chk_all = {}
chkf = os.path.join(OUT, f"hookchk_{args.shard}.json")
if os.path.exists(chkf):
    chk_all = json.load(open(chkf))
devs = sorted(set(DEV), key=str)
for name, layers, kind, dkey, w2, restrict in mine:
    f = os.path.join(OUT, f"nll_{name}.npy")
    if os.path.exists(f):
        continue
    CTL.clear()
    CTL.update(layers=set(layers), kind=kind, w2=w2, restrict=restrict)
    if dkey is not None:
        dn = np.arange(len(ME["inp"])) if dkey == "self" else P["donors"][dkey]
        CTL["donor_dev"] = {dv: torch.from_numpy(dn).to(dv) for dv in devs}
    if restrict is not None:
        CTL["restrict_dev"] = {dv: torch.from_numpy(restrict).to(dv) for dv in devs}
    REC["chk"] = [0, 0, 0]
    ts = time.time()
    nll = run_corpus(seqs_eval, ME, "cond", nll=True)
    np.save(f, nll)
    c = REC["chk"]
    chk_all[name] = {"match": c[0], "replaced_rows": c[1], "rows": c[2], "wall_s": time.time() - ts}
    json.dump(chk_all, open(chkf, "w"))
    v = np.isfinite(nll)
    log(f"{name}: dNLL {np.nanmean(nll - np.load(os.path.join(OUT, 'nll_I0.npy'))):.4f} "
        f"hook {c[0]}/{c[1]} rows {c[2]} ({time.time() - ts:.0f}s)")
log("shard done")
