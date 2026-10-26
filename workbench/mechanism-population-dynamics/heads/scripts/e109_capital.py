"""E109: does the read-side / write-side asymmetry of unlearning (E105c, E108) hold for factual recall and under a
targeted relearning attack (Deeb & Roger style)?

1) Unlearn country->capital facts (21 facts, templates 0-2) with gradient-difference unlearning restricted to a
   parameter subset (qk / ov / mlp): forget loss = relu(lse(logit correct) - lse(logits of other capitals) + margin),
   retain loss = Pile LM loss. Stop when the mean margin over all 4 templates falls below --target.
2) Targeted relearning attack: fine-tune all parameters on facts of split T (11 countries, all templates) with
   cross-entropy on the correct capital; report the margin on the held-out split V (10 countries) over steps.
   The same attack is applied to the original model as a reference.
3) Save the unlearned model (for a separate general-data relearning run with e93_lesion.py --arm C).

Usage: e109_capital.py --subset qk --seed 1 --out DIR
"""
import argparse
import json
import time

import numpy as np
import pyarrow.parquet as pq
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

import mp_common as mc
from e89_labor import CAP_T, CAPITALS
from e105_unlearn import masks

BASE = "/home/xiang/mechpop_cache/ckpt/pythia-160m_step100000"
SHARD = mc.CACHE / "pile_tok" / "shard00003.parquet"


def facts(tok):
    one = lambda w: (lambda ids: ids[0] if len(ids) == 1 else None)(tok.encode(" " + w, add_special_tokens=False))
    caps = [(c, k, one(k)) for c, k in CAPITALS if one(k) is not None]
    return caps


def batch(tok, caps, templates):
    rows = []
    for ci, (c, k, kid) in enumerate(caps):
        for t in templates:
            rows.append((tok.encode(CAP_T[t].format(c=c), add_special_tokens=False), kid, ci))
    return rows


def margin(model, tok, rows, all_ids, dev="cuda"):
    """mean over rows of logit(correct) - logsumexp(logits of the other capitals), at the last position."""
    vals = []
    with torch.no_grad():
        for ids, kid, _ in rows:
            lg = model(torch.tensor([ids], device=dev)).logits[0, -1].float()
            others = torch.tensor([i for i in all_ids if i != kid], device=dev)
            vals.append(float(lg[kid] - torch.logsumexp(lg[others], 0)))
    return float(np.mean(vals))


def forget_loss(model, rows, all_ids, m, dev="cuda"):
    tot = 0.0
    for ids, kid, _ in rows:
        lg = model(torch.tensor([ids], device=dev)).logits[0, -1]
        others = torch.tensor([i for i in all_ids if i != kid], device=dev)
        tot = tot + torch.relu(lg[kid] - torch.logsumexp(lg[others], 0) + m)
    return tot / len(rows)


def targeted_attack(model, tok, train_rows, test_rows, all_ids, lr, steps, dev="cuda"):
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.0)
    trace = {0: margin(model, tok, test_rows, all_ids)}
    for st in range(1, steps + 1):
        loss = 0.0
        for ids, kid, _ in train_rows:
            lg = model(torch.tensor([ids], device=dev)).logits[0, -1]
            loss = loss + torch.nn.functional.cross_entropy(lg[None], torch.tensor([kid], device=dev))
        opt.zero_grad(set_to_none=True)
        (loss / len(train_rows)).backward()
        opt.step()
        if st in (5, 10, 25, 50, 100):
            trace[st] = margin(model, tok, test_rows, all_ids)
    return trace


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--subset", required=True)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--out", required=True)
    ap.add_argument("--lr", type=float, default=5e-6)
    ap.add_argument("--target", type=float, default=0.0)
    ap.add_argument("--margin", type=float, default=0.0)
    ap.add_argument("--max_steps", type=int, default=600)
    ap.add_argument("--attack_lr", type=float, default=1e-5)
    ap.add_argument("--attack_steps", type=int, default=100)
    a = ap.parse_args()
    torch.manual_seed(a.seed)
    torch.backends.cuda.matmul.allow_tf32 = True
    tok = AutoTokenizer.from_pretrained("EleutherAI/pythia-160m", cache_dir=str(mc.HF_CACHE))
    caps = facts(tok)
    all_ids = [k for _, _, k in caps]
    rng = np.random.default_rng(100 + a.seed)
    perm = rng.permutation(len(caps))
    T_idx, V_idx = set(perm[:11].tolist()), set(perm[11:].tolist())
    forget_rows = batch(tok, caps, [0, 1, 2])
    eval_rows = batch(tok, caps, [0, 1, 2, 3])
    T_rows = [r for r in eval_rows if r[2] in T_idx]
    V_rows = [r for r in eval_rows if r[2] in V_idx]
    model = AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.float32, attn_implementation="sdpa").cuda()
    tbl = pq.read_table(SHARD).column("tokens")
    eval_x = torch.tensor(tbl.slice(120000, 16).to_pylist()).cuda()
    lm = lambda: float(model(eval_x, labels=eval_x).loss)
    log = {"args": vars(a), "T": sorted(T_idx), "V": sorted(V_idx)}
    with torch.no_grad():
        log["start"] = {"all": margin(model, tok, eval_rows, all_ids), "V": margin(model, tok, V_rows, all_ids),
                        "tmpl3": margin(model, tok, [r for r in eval_rows if (eval_rows.index(r) % 4) == 3], all_ids), "lm": lm()}
    print("start", log["start"], flush=True)
    m = masks(model, a.subset)
    for p in model.parameters():
        p.requires_grad_(p in m)
    params = [p for p in model.parameters() if p.requires_grad]
    hooks = [p.register_hook(lambda g, mk=m[p].cuda(): g * mk) for p in params]
    opt = torch.optim.Adam(params, lr=a.lr, weight_decay=0.0)
    ptr, t0 = 20000 * a.seed, time.time()
    for step in range(1, a.max_steps + 1):
        fl = forget_loss(model, forget_rows, all_ids, a.margin)
        r = torch.tensor(tbl.slice(ptr, 16).to_pylist()).cuda()
        ptr += 16
        opt.zero_grad(set_to_none=True)
        (fl + model(r, labels=r).loss).backward()
        torch.nn.utils.clip_grad_norm_(params, 1.0)
        opt.step()
        if step % 5 == 0:
            mm = margin(model, tok, eval_rows, all_ids)
            print(json.dumps({"step": step, "margin_all": round(mm, 3), "sec": round(time.time() - t0)}), flush=True)
            if mm < a.target:
                break
    for h in hooks:
        h.remove()
    base = AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.float32)
    pb = dict(base.named_parameters())
    dist = sum(float((p.detach().cpu() - pb[n].detach()).norm() ** 2) for n, p in model.named_parameters()) ** 0.5
    tot = sum(float(p.detach().norm() ** 2) for p in pb.values()) ** 0.5
    with torch.no_grad():
        log["end"] = {"step": step, "all": margin(model, tok, eval_rows, all_ids), "V": margin(model, tok, V_rows, all_ids),
                      "tmpl3": margin(model, tok, [r for r in eval_rows if (eval_rows.index(r) % 4) == 3], all_ids),
                      "lm": lm(), "l2_rel": dist / tot}
    print("end", log["end"], flush=True)
    for p in model.parameters():
        p.requires_grad_(True)
    model.save_pretrained(a.out, safe_serialization=False)
    # targeted relearning attack on the unlearned model, then on the original model
    log["attack_unlearned"] = targeted_attack(model, tok, T_rows, V_rows, all_ids, a.attack_lr, a.attack_steps)
    del model
    orig = AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.float32, attn_implementation="sdpa").cuda()
    log["attack_original"] = targeted_attack(orig, tok, T_rows, V_rows, all_ids, a.attack_lr, a.attack_steps)
    print("attack", log["attack_unlearned"], log["attack_original"], flush=True)
    out = mc.RESULTS / "e109"
    out.mkdir(parents=True, exist_ok=True)
    (out / f"unlearn_{a.subset}_s{a.seed}.json").write_text(json.dumps(log))


if __name__ == "__main__":
    main()
