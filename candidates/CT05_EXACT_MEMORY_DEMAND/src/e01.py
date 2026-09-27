"""CT05 E01 runner — exactness-demand map (see docs/E01_PROTOCOL.md).

usage: e01.py MODEL_PATH OUT.jsonl SHARD NSHARDS [--hybrid]
"""
import json, random, sys, time
import torch
from transformers import DynamicCache
from cachelib import load, is_linear_layer, replicate, decision_mask
from render import render

MODEL, OUT, SHARD, NSH = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
CKPTS = sys.argv[5]
import os
SUB = int(os.environ.get("SUB", 16))  # rows per decision sub-batch (row 0 is always an in-batch FULL reference)
WIN_KS = [0, 1, 2, 4, 8]
TEXTWIN_KS = [2, 4]
BUDGETS = [0.25, 0.5]

tok, model = load(MODEL)
HYB = any(t == "linear_attention" for t in getattr(model.config, "layer_types", []) or [])
dev = "cuda"

# ---------------- attention-mass hook (FULL row only) ----------------
ATT = {"on": False, "acc": None, "n": 0, "qlo": 0, "qhi": 0, "abs0": 0, "N": 0}


def _attn_hook(mod, args, kwargs, out):
    """Accumulate mean attention (over heads, selected queries, layers) of row 0 onto history keys [0, N)."""
    if not ATT["on"]:
        return
    hs = args[0] if args else kwargs["hidden_states"]
    hs = hs[:1]
    cos, sin = kwargs["position_embeddings"]
    cos, sin = cos[:1], sin[:1]
    hd = mod.head_dim
    B, L, _ = hs.shape
    q = mod.q_proj(hs)
    if q.shape[-1] == 2 * mod.config.num_attention_heads * hd:  # gated (Qwen3.5)
        q, _ = torch.chunk(q.view(B, L, -1, hd * 2), 2, dim=-1)
    q = mod.q_norm(q.reshape(B, L, -1, hd)).transpose(1, 2)
    rope = sys.modules[type(mod).__module__].apply_rotary_pos_emb
    q, _ = rope(q, q, cos, sin)
    K = kwargs["past_key_values"].layers[mod.layer_idx].keys[:1]
    K = K.repeat_interleave(q.shape[1] // K.shape[1], dim=1)
    qs = q[:, :, ATT["qlo"]:ATT["qhi"]].float()
    sc = torch.einsum("bhqd,bhkd->bhqk", qs, K.float()) * mod.scaling
    qabs = ATT["abs0"] + torch.arange(ATT["qlo"], ATT["qhi"], device=sc.device)
    kpos = torch.arange(K.shape[2], device=sc.device)
    sc = sc.masked_fill(kpos[None, :] > qabs[:, None], float("-inf"))
    p = sc.softmax(-1)[0, :, :, :ATT["N"]].mean(0).mean(0)
    ATT["acc"] = p if ATT["acc"] is None else ATT["acc"] + p
    ATT["n"] += 1


def att_take():
    a = (ATT["acc"] / max(ATT["n"], 1)).float()
    ATT.update(on=False, acc=None, n=0)
    return a


for m in model.modules():
    if type(m).__name__.endswith("Attention") and hasattr(m, "q_proj") and hasattr(m, "layer_idx"):
        m.register_forward_hook(_attn_hook, with_kwargs=True)


# ---------------- helpers ----------------
BLOCK = 256
WINDOW = 32  # SnapKV-style observation window: last WINDOW history tokens (deployable, pre-action)


def make_blocks(events):
    blocks = []
    for j, ev in enumerate(events):
        for s in range(ev["s"], ev["e"], BLOCK):
            blocks.append({"j": j, "s": s, "e": min(s + BLOCK, ev["e"])})
    return blocks


@torch.no_grad()
def prefill_chunked(ids, events, blocks):
    """Block-by-block prefill. Returns cache, per-block drift (hybrid, DeltaS Eq.3), per-event drift,
    per-token surprisal (nll of token t given <t), and window attention over history."""
    N = ids.shape[0]
    cache = DynamicCache(config=model.config)
    bdrift, edrift, ev_before = [], [None] * len(events), None
    tok_nll = torch.zeros(N, device=dev)
    prev_last = None
    for bi, b in enumerate(blocks):
        s, e = b["s"], b["e"]
        rec_states = lambda: [l.recurrent_states.float().clone() for l in cache.layers if is_linear_layer(l)]
        before = rec_states() if (HYB and s > 0) else None
        if HYB and s == events[b["j"]]["s"]:
            ev_before = before
        last = e == N
        if last:
            w0 = max(N - WINDOW, s)
            ATT.update(on=True, acc=None, n=0, qlo=w0 - s, qhi=e - s, abs0=s, N=N)
        out = model(input_ids=ids[None, s:e], position_ids=torch.arange(s, e, device=dev)[None],
                    past_key_values=cache, use_cache=True)
        ATT["on"] = False
        lg = out.logits[0].float()
        if e - s > 1:
            tok_nll[s + 1:e] = -torch.log_softmax(lg[:-1], -1).gather(-1, ids[s + 1:e, None])[:, 0]
        if prev_last is not None:
            tok_nll[s] = -torch.log_softmax(prev_last, -1)[ids[s]]
        prev_last = lg[-1]
        cache = out.past_key_values
        if HYB:
            after = [l.recurrent_states.float() for l in cache.layers if is_linear_layer(l)]
            dr = lambda B_: sum(((a - b_).norm() / b_.norm().clamp_min(1e-8)).item() for a, b_ in zip(after, B_)) / len(after)
            bdrift.append(dr(before) if before is not None else None)
            if e == events[b["j"]]["e"]:
                edrift[b["j"]] = dr(ev_before) if ev_before is not None else None
        del out, lg
    win_att = att_take()
    return cache, bdrift, edrift, tok_nll, win_att


@torch.no_grad()
def prefill_plain(ids):
    cache = DynamicCache(config=model.config)
    return model(input_ids=ids[None], past_key_values=cache, use_cache=True, logits_to_keep=1).past_key_values


def score_rows(cache, N, dec, lo, hides, rec_from, act=None, collect_attn=False):
    """Returns list of dicts per row with nll_sum, kl_mean, per-token nll; row 0 of every sub-batch is FULL."""
    res = []
    tgt = dec[lo:]
    V = model.config.get_text_config().vocab_size
    sub = max(2, min(SUB, int(6e9 // ((len(tgt) + 1) * V * 2))))  # bound bf16 logits to ~6 GB
    for b0 in range(0, len(hides), sub - 1):
        hs = [[]] + hides[b0:b0 + sub - 1]
        rf = [None] + (rec_from[b0:b0 + sub - 1] if rec_from else [None] * (len(hs) - 1))
        B, L = len(hs), dec.shape[0]
        c = replicate(cache, B, rf)
        mask = decision_mask(N, L, hs, dev)
        pos = torch.arange(N, N + L, device=dev)[None].expand(B, L)
        if collect_attn and b0 == 0:  # queries = target-predicting positions (uses the future action)
            ATT.update(on=True, acc=None, n=0, qlo=lo - 1, qhi=L - 1, abs0=N, N=N)
        with torch.no_grad():
            out = model(input_ids=dec[None].expand(B, L), attention_mask=mask, position_ids=pos,
                        past_key_values=c, use_cache=True, logits_to_keep=L - lo + 1)
        ATT["on"] = False
        lg = out.logits[:, :-1]  # predicts dec[lo:]; per-row float to bound memory
        lp0 = torch.log_softmax(lg[0].float(), -1)
        p0 = lp0.exp()
        nll_l, kl_l = [], []
        for r_ in range(B):
            lpr = lp0 if r_ == 0 else torch.log_softmax(lg[r_].float(), -1)
            nll_l.append(-lpr.gather(-1, tgt[:, None])[:, 0])
            kl_l.append((p0 * (lp0 - lpr)).sum(-1))
            del lpr
        nll, kl = torch.stack(nll_l), torch.stack(kl_l)
        del lg, lp0, p0
        for r in range(1, B):
            d = {"nll_sum": nll[r].sum().item(), "full_nll_sum": nll[0].sum().item(),
                 "kl_mean": kl[r].mean().item(), "tok_dnll": (nll[r] - nll[0]).half().tolist()}
            if act:
                a0, a1 = max(act[0] - lo, 0), max(act[1] - lo, 0)
                d["act_dnll"] = (nll[r, a0:a1] - nll[0, a0:a1]).sum().item()
            res.append(d)
        if b0 == 0:
            full = {"nll": nll[0].tolist()}
        del out, c
    return res, full


def text_drop(ids, N, drop_spans):
    keep = torch.ones(ids.shape[0], dtype=torch.bool, device=dev)
    for s, e in drop_spans:
        keep[s:e] = False
    return ids[keep], N - sum(e - s for s, e in drop_spans)


def text_rows(ids, N, lo, span_sets, full_nll_sum):
    """Delete spans from text, re-prefill, score target. Returns list of (row, rec_state_cache)."""
    out = []
    for spans in span_sets:
        ids2, N2 = text_drop(ids, N, spans)
        c2 = prefill_plain(ids2[:N2])
        r, full2 = score_rows(c2, N2, ids2[N2:], lo, [[]], None)  # row 1 == FULL of the shortened text
        d = {"nll_sum": full2_sum(full2), "dnll": full2_sum(full2) - full_nll_sum}
        if HYB:  # keep only the recurrent/conv states (used for State-swap rows)
            for l in c2.layers:
                if not is_linear_layer(l):
                    l.keys = l.values = None
        out.append((d, c2))
    return out


def full2_sum(f):
    return float(sum(f["nll"]))


# ---------------- main ----------------
recs = [json.loads(l) for l in open(CKPTS)]
recs = [r for r in recs if r["cid"] % NSH == SHARD]
if os.environ.get("LIMIT"):
    recs = recs[:int(os.environ["LIMIT"])]
done = set()
try:
    done = {json.loads(l)["cid"] for l in open(OUT)}
except FileNotFoundError:
    pass
fo = open(OUT, "a")
rng = random.Random(0)
for rec in recs:
    if rec["cid"] in done:
        continue
    t0 = time.time()
    try:
        x = render(tok, rec)
    except Exception as ex:
        fo.write(json.dumps({"cid": rec["cid"], "skip": str(ex)[:80]}) + "\n"); fo.flush()
        continue
    ids = x["ids"].to(dev)
    N, lo, evs, act = x["N"], x["dec_lo"], x["events"], x["act"]
    dec = ids[N:]
    E = len(evs)
    blocks = make_blocks(evs)
    cache, bdrift, edrift, tok_nll, win_att = prefill_chunked(ids[:N], evs, blocks)
    spans = [(e["s"], e["e"]) for e in evs]
    bspans = [(b["s"], b["e"]) for b in blocks]
    nB = len(blocks)

    # ---- stage 1: FULL, KV_i (events), KV_b (blocks), KVWIN_k  (+ future-query attention from FULL row)
    win = []
    for k in WIN_KS:
        keep = {0, 1} | set(range(max(E - k, 0), E))
        win.append([spans[j] for j in range(E) if j not in keep])
    hides = [[sp] for sp in spans] + [[sp] for sp in bspans] + win
    rows, full = score_rows(cache, N, dec, lo, hides, None, act, collect_attn=True)
    fut_att = att_take()
    full_sum = float(sum(full["nll"]))
    kv_rows, blk_rows, win_rows = rows[:E], rows[E:E + nB], rows[E + nB:]
    # header-query attention (deployable: the assistant header precedes the action)
    ATT.update(on=True, acc=None, n=0, qlo=0, qhi=lo, abs0=N, N=N)
    score_rows(cache, N, dec, lo, [[]], None)
    hdr_att = att_take()
    dep_att = (win_att + hdr_att) / 2

    # ---- TEXT_i and TEXTWIN_k (re-prefill); keep recurrent states for REC/BOTH
    text_i, rec_caches = [], []
    for j in range(E):
        (d, c2), = text_rows(ids, N, lo, [[spans[j]]], full_sum)
        text_i.append(d)
        rec_caches.append(c2 if HYB else None)
        if not HYB:
            del c2
    textwin = []
    for k in TEXTWIN_KS:
        keep = {0, 1} | set(range(max(E - k, 0), E))
        drop = [spans[j] for j in range(E) if j not in keep]
        if drop:
            (d, c2), = text_rows(ids, N, lo, [drop], full_sum)
            del c2
        else:
            d = {"dnll": 0.0}
        textwin.append(d)

    # ---- hybrid REC_i / BOTH_i (State-swap with the TEXT_i prefill's recurrent state)
    rec_rows = both_rows = None
    if HYB:
        rr, _ = score_rows(cache, N, dec, lo, [[] for _ in range(E)] + [[sp] for sp in spans], rec_caches * 2, act)
        rec_rows, both_rows = rr[:E], rr[E:]
    del rec_caches

    # ---- stage 2: budgeted multi-block eviction by signal
    blens = [e - s for s, e in bspans]
    bsig = {
        "recency": [float(e) for s, e in bspans],
        "attn_future": [fut_att[s:e].sum().item() for s, e in bspans],
        "attn_deploy": [dep_att[s:e].sum().item() for s, e in bspans],
        "surprisal": [tok_nll[s:e].mean().item() for s, e in bspans],
        "oracle": [r["nll_sum"] - full_sum for r in blk_rows],
        "random": [rng.random() for _ in bspans],
    }
    if HYB:
        mx = max([d for d in bdrift if d is not None] or [1.0])
        bsig["drift"] = [d if d is not None else mx for d in bdrift]
    pol_hides, pol_names = [], []
    for name, sc in bsig.items():
        order = sorted(range(nB), key=lambda j: -sc[j])
        for bud in BUDGETS:
            cap, used, kept = bud * N, 0, set()
            for j in order:
                if used + blens[j] <= cap:
                    kept.add(j); used += blens[j]
            pol_hides.append([bspans[j] for j in range(nB) if j not in kept])
            pol_names.append(f"{name}@{bud}")
    prow, _ = score_rows(cache, N, dec, lo, pol_hides, None, act)

    ev_out = []
    for j, e in enumerate(evs):
        s_, e_ = spans[j]
        ev_out.append({"ev": e["ev"], "s": s_, "e": e_, "len": e_ - s_, "age": N - e_, "turns_ago": E - 1 - j,
                       "attn_future": fut_att[s_:e_].sum().item(), "attn_deploy": dep_att[s_:e_].sum().item(),
                       "surpr": tok_nll[s_:e_].mean().item(), "drift": edrift[j] if HYB else None,
                       "kv": kv_rows[j], "text": text_i[j],
                       "rec": rec_rows[j] if HYB else None, "both": both_rows[j] if HYB else None})
    blk_out = [{"j": b["j"], "s": b["s"], "e": b["e"], "dnll": blk_rows[i]["nll_sum"] - full_sum,
                "kl": blk_rows[i]["kl_mean"], "act_dnll": blk_rows[i].get("act_dnll"),
                **{k: v[i] for k, v in bsig.items() if k not in ("oracle",)}} for i, b in enumerate(blocks)]
    outrec = {"cid": rec["cid"], "src": rec["src"], "traj": rec["traj"], "N": N, "T": len(full["nll"]),
              "full_nll_sum": full_sum, "full_tok_nll": full["nll"], "act": act, "lo": lo,
              "events": ev_out, "blocks": blk_out,
              "kvwin": {str(k): r for k, r in zip(WIN_KS, win_rows)},
              "textwin": {str(k): d for k, d in zip(TEXTWIN_KS, textwin)},
              "budget": {n: r for n, r in zip(pol_names, prow)}, "sec": time.time() - t0}
    fo.write(json.dumps(outrec) + "\n"); fo.flush()
    del cache
    torch.cuda.empty_cache()
    print(rec["cid"], rec["src"], "N", N, "E", E, "B", nB, f"{time.time() - t0:.1f}s", flush=True)
