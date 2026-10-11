"""CT07 E00 runner — intra-action query emergence (docs/E00_PROTOCOL.md).

usage: e00.py MODEL_PATH OUT.jsonl SHARD NSHARDS CHECKPOINTS CT05_RAW_GLOB
"""
import glob, json, os, random, sys, time
import numpy as np
import torch
from transformers import DynamicCache
from cachelib import load, replicate, SINK
from render import render
from actionclass import token_classes

MODEL, OUT, SHARD, NSH, CKPTS, CT05RAW = sys.argv[1:7]
SHARD, NSH = int(SHARD), int(NSH)
SUB = int(os.environ.get("SUB", 16))
BLOCK, WINDOW, BUDGETS, QCHUNK = 256, 32, [0.25, 0.5], 256
dev = "cuda"
tok, model = load(MODEL)
ATTDIR = os.path.join(os.path.dirname(OUT), "att")
os.makedirs(ATTDIR, exist_ok=True)

# ---------- per-query attention capture (row 0 only), mean over heads, summed over layers ----------
CAP = {"on": False, "abs0": 0, "N": 0, "acc": None, "n": 0}


def _hook(mod, args, kwargs, out):
    if not CAP["on"]:
        return
    hs = (args[0] if args else kwargs["hidden_states"])[:1]
    cos, sin = kwargs["position_embeddings"]
    cos, sin = cos[:1], sin[:1]
    hd, (B, L, _) = mod.head_dim, hs.shape
    q = mod.q_proj(hs)
    if q.shape[-1] == 2 * mod.config.num_attention_heads * hd:
        q, _ = torch.chunk(q.view(B, L, -1, hd * 2), 2, dim=-1)
    q = mod.q_norm(q.reshape(B, L, -1, hd)).transpose(1, 2)
    q, _ = sys.modules[type(mod).__module__].apply_rotary_pos_emb(q, q, cos, sin)
    K = kwargs["past_key_values"].layers[mod.layer_idx].keys[:1]
    K = K.repeat_interleave(q.shape[1] // K.shape[1], dim=1).float()
    N = CAP["N"]
    rows = []
    kpos = torch.arange(K.shape[2], device=q.device)
    for q0 in range(0, L, QCHUNK):
        qs = q[:, :, q0:q0 + QCHUNK].float()
        sc = torch.einsum("bhqd,bhkd->bhqk", qs, K) * mod.scaling
        qabs = CAP["abs0"] + torch.arange(q0, q0 + qs.shape[2], device=q.device)
        sc = sc.masked_fill(kpos[None, :] > qabs[:, None], float("-inf"))
        rows.append(sc.softmax(-1)[0, :, :, :N].mean(0))  # (q, N)
        del sc
    a = torch.cat(rows)
    CAP["acc"] = a if CAP["acc"] is None else CAP["acc"] + a
    CAP["n"] += 1


for m in model.modules():
    if type(m).__name__.endswith("Attention") and hasattr(m, "q_proj") and hasattr(m, "layer_idx"):
        m.register_forward_hook(_hook, with_kwargs=True)


@torch.no_grad()
def fwd(ids, s, e, cache, capture=False, N=None):
    if capture:
        CAP.update(on=True, abs0=s, N=N, acc=None, n=0)
    out = model(input_ids=ids[None, s:e], position_ids=torch.arange(s, e, device=dev)[None],
                past_key_values=cache, use_cache=True, logits_to_keep=1)
    CAP["on"] = False
    if capture:
        a = CAP["acc"] / CAP["n"]
        CAP["acc"] = None
        return out.past_key_values, a
    return out.past_key_values, None


def value_rows(cache, N, dec, lo, hides, r0, val_idx):
    """Hidden spans apply to query rows >= r0 only. Returns per-row summed value-token dNLL vs FULL."""
    res, T = [], dec.shape[0] - lo
    L = dec.shape[0]
    V = model.config.get_text_config().vocab_size
    keep = L - r0  # logits for positions r0..L-1
    sub = max(2, min(SUB, int(6e9 // (keep * V * 2))))
    tgt_pos = torch.tensor([lo + t for t in val_idx], device=dev)  # decision positions of value tokens
    pred_pos = tgt_pos - 1 - r0  # index into kept logits
    tgt_ids = dec[tgt_pos]
    for b0 in range(0, len(hides), sub - 1):
        hs = [[]] + hides[b0:b0 + sub - 1]
        B = len(hs)
        c = replicate(cache, B)
        m = torch.ones(B, 1, L, N + L, dtype=torch.bool, device=dev)
        m[:, :, :, N:] = torch.tril(torch.ones(L, L, dtype=torch.bool, device=dev))
        for b, spans in enumerate(hs):
            for s, e in spans:
                m[b, :, r0:, max(s, SINK):e] = False
        pos = torch.arange(N, N + L, device=dev)[None].expand(B, L)
        with torch.no_grad():
            lg = model(input_ids=dec[None].expand(B, L), attention_mask=m, position_ids=pos,
                       past_key_values=c, use_cache=True, logits_to_keep=keep).logits
        nll = []
        for r in range(B):
            lp = torch.log_softmax(lg[r, pred_pos].float(), -1)
            nll.append(-lp.gather(-1, tgt_ids[:, None])[:, 0].sum().item())
        res += [x - nll[0] for x in nll[1:]]
        del lg, c, m
    return res


# ---------- main ----------
ct05 = {}
for f in glob.glob(CT05RAW):
    for l in open(f):
        r = json.loads(l)
        if "skip" not in r:
            ct05[r["cid"]] = r
recs = [json.loads(l) for l in open(CKPTS)]
recs = [r for r in recs if r["cid"] % NSH == SHARD and r["cid"] in ct05]
if os.environ.get("ONLY"):
    recs = [r for r in recs if r["cid"] in {int(c) for c in os.environ["ONLY"].split(",")}]
done = set()
if os.path.exists(OUT):
    done = {json.loads(l)["cid"] for l in open(OUT)}
fo = open(OUT, "a")
rng = random.Random(0)
for rec in recs:
    if rec["cid"] in done:
        continue
    t0 = time.time()
    x = render(tok, rec)
    ids, N, lo, evs = x["ids"].to(dev), x["N"], x["dec_lo"], x["events"]
    dec = ids[N:]
    L = dec.shape[0]
    cl, name, key = token_classes(tok, rec)
    if len(cl) != L - lo or "value" not in cl or "name" not in cl:
        fo.write(json.dumps({"cid": rec["cid"], "skip": "no value/name or class misalign"}) + "\n"); fo.flush()
        continue
    val_idx = [t for t, c in enumerate(cl) if c == "value"]
    t_v = val_idx[0]
    t_n = max(t for t, c in enumerate(cl) if c == "name" and t < t_v) if any(
        c == "name" for c in cl[:t_v]) else None
    bnd = {"HDR": lo - 1, "PREVALUE": lo + t_v - 1}
    if t_n is not None:
        bnd["TOOL"] = lo + t_n
    if rec["src"] == "tau":
        kidx = [t for t, c in enumerate(cl[:t_v]) if c == "key"]
        if kidx:
            bnd["KEY"] = lo + kidx[-1]
    else:
        pidx = [t for t, c in enumerate(cl[:t_v]) if c == "prose"]
        if pidx:
            bnd["PROSE"] = lo + pidx[-1]  # query at last prose token predicts the opening ```
    # blocks identical to CT05
    blocks = []
    for ev in evs:
        for s in range(ev["s"], ev["e"], BLOCK):
            blocks.append((s, min(s + BLOCK, ev["e"])))
    old = ct05[rec["cid"]]["blocks"]
    assert [(b["s"], b["e"]) for b in old] == blocks, "block mismatch with CT05"
    nB = len(blocks)
    # prefill with window capture on the last WINDOW history tokens, then decision chunk capture
    cache = DynamicCache(config=model.config)
    cache, _ = fwd(ids, 0, N - WINDOW, cache)
    cache, win = fwd(ids, N - WINDOW, N, cache, capture=True, N=N)
    dcache = replicate(cache, 1)
    _, A = fwd(ids, N, N + L, dcache, capture=True, N=N)  # A: (L, N) attention of every decision query
    del dcache
    blk = torch.stack([A[:, s:e].sum(-1) for s, e in blocks], -1)  # (L, nB)
    win_b = torch.tensor([win.mean(0)[s:e].sum().item() for s, e in blocks], device=dev)
    np.savez_compressed(os.path.join(ATTDIR, f"{rec['cid']}.npz"), blk=blk.half().cpu().numpy(),
                        win=win_b.half().cpu().numpy())
    sig = {}
    hdr = blk[:lo].mean(0)
    sig["DEPLOY"] = ((win_b + hdr) / 2).tolist()
    for st, b in bnd.items():
        sig[st] = blk[:b + 1].mean(0).tolist()
    sig["FUTURE"] = blk[lo - 1:L - 1].mean(0).tolist()  # CT05 attn_future definition
    sig["oracle"] = [b["dnll"] for b in old]
    sig["random"] = [rng.random() for _ in blocks]
    lex = key if rec["src"] == "tau" else name
    if lex:
        texts = [tok.decode(ids[s:e]) for s, e in blocks]
        sig["LEX"] = [t.count(lex) + 1e-6 * s for t, (s, e) in zip(texts, blocks)]  # ties -> recency
    lens = [e - s for s, e in blocks]
    names, hides = [], []
    for nm, sc in sig.items():
        order = sorted(range(nB), key=lambda j: -sc[j])
        for bud in BUDGETS:
            cap, used, kept = bud * N, 0, set()
            for j in order:
                if used + lens[j] <= cap:
                    kept.add(j); used += lens[j]
            hides.append([blocks[j] for j in range(nB) if j not in kept])
            names.append(f"{nm}@{bud}")
    G = value_rows(cache, N, dec, lo, hides, bnd["PREVALUE"], val_idx)
    spear = {}
    from scipy.stats import spearmanr
    for nm in sig:
        if nm not in ("oracle", "random") and nB >= 5:
            r_ = spearmanr(sig[nm], sig["oracle"]).correlation
            spear[nm] = None if np.isnan(r_) else float(r_)
    fo.write(json.dumps({"cid": rec["cid"], "src": rec["src"], "traj": rec["traj"], "N": N, "T": L - lo,
                         "n_value": len(val_idx), "bnd": {k: v - lo for k, v in bnd.items()},
                         "G": dict(zip(names, G)), "spearman_oracle": spear, "sec": time.time() - t0}) + "\n")
    fo.flush()
    del cache, A, blk
    torch.cuda.empty_cache()
    print(rec["cid"], rec["src"], N, L, nB, f"{time.time() - t0:.1f}s", flush=True)
