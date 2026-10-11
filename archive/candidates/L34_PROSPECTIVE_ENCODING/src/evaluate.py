"""L34 E01 — gold-answer NLL (primary) + forced-choice rank (secondary). No generation."""
import torch, json

MAXC = 192


@torch.no_grad()
def score(model, tok, pairs, bs=64):
    """pairs: [(prompt, candidate)] -> (sum_nll, n_tokens) per pair."""
    device = next(model.parameters()).device
    pad = tok.pad_token_id if tok.pad_token_id is not None else 0
    bos = [tok.bos_token_id] if tok.bos_token_id is not None else []
    enc = []
    for p, c in pairs:
        pi = tok(p, add_special_tokens=False)["input_ids"]
        ci = tok(c, add_special_tokens=False)["input_ids"]
        ids = (bos + pi + ci)[:MAXC]
        enc.append((ids, len(ci)))
    order = sorted(range(len(enc)), key=lambda i: len(enc[i][0]))
    out = [None] * len(enc)
    model.eval()
    for s in range(0, len(order), bs):
        b = order[s:s + bs]
        L = max(len(enc[i][0]) for i in b)
        ids = torch.full((len(b), L), pad, dtype=torch.long)
        msk = torch.zeros((len(b), L), dtype=torch.long)
        lm = torch.zeros((len(b), L), dtype=torch.long)
        for k, i in enumerate(b):
            x, nc = enc[i]
            ids[k, :len(x)] = torch.tensor(x); msk[k, :len(x)] = 1
            lm[k, len(x) - nc:len(x)] = 1
        ids, msk, lm = ids.to(device), msk.to(device), lm.to(device)
        with torch.autocast("cuda", dtype=torch.bfloat16):
            logits = model(input_ids=ids, attention_mask=msk).logits[:, :-1]
        nll = torch.nn.functional.cross_entropy(
            logits.float().reshape(-1, logits.size(-1)), ids[:, 1:].reshape(-1),
            reduction="none").view(ids.size(0), -1)
        w = lm[:, 1:].float()
        tot = (nll * w).sum(1).tolist(); n = w.sum(1).tolist()
        for k, i in enumerate(b):
            out[i] = (tot[k], n[k])
    return out


def run_eval(model, tok, items, rank_filter=None, bs=64, log=print):
    """items from data.eval_items. rank_filter(item)->bool selects forced-choice subset."""
    gold_pairs = [(it["prompt"], " " + it["gold"]) for it in items]
    g = score(model, tok, gold_pairs, bs)
    recs = []
    for it, (t, n) in zip(items, g):
        recs.append({k: it[k] for k in ("age", "name", "attr", "family", "tmpl")}
                    | {"nll_sum": t, "ntok": n, "nll_tok": t / max(n, 1)})
    if rank_filter is not None:
        sel = [i for i, it in enumerate(items) if rank_filter(it)]
        log(f"rank subset: {len(sel)} items x (1+distractors)")
        dp, owner = [], []
        for i in sel:
            for d in items[i]["distract"]:
                dp.append((items[i]["prompt"], " " + d)); owner.append(i)
        ds = score(model, tok, dp, bs)
        per = {}
        for (t, n), i in zip(ds, owner):
            per.setdefault(i, []).append(t / max(n, 1))
        for i in sel:
            gv = recs[i]["nll_tok"]
            worse = sum(1 for v in per[i] if v <= gv)
            recs[i]["rank"] = worse + 1
            recs[i]["top1"] = int(worse == 0)
    return recs
