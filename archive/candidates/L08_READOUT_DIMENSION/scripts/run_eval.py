"""L08 evaluation runner: one (model, mask, cell) condition -> raw jsonl.

Only the final hidden->vocabulary readout is modified (see src/readout.py).
"""
from __future__ import annotations

import argparse, json, os, pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from src import tasks
from src.readout import ReadoutTruncation, build_mask, mask_id


def load_items(cell: str, n: int, seed: int):
    if cell == "mmlu_rank":
        return tasks.build_mmlu(n, seed, protocol="rank")
    if cell == "mmlu_gen_letter":
        return tasks.build_mmlu(n, seed, protocol="gen")
    if cell == "mmlu_gen_cot":
        return tasks.build_mmlu(n, seed, protocol="gen", cot=True)
    if cell == "gsm8k_gen_cot":
        return tasks.build_gsm8k(n, seed, cot=True)
    if cell == "gsm8k_gen_direct":
        return tasks.build_gsm8k(n, seed, cot=False)
    if cell == "squad_gen":
        return tasks.build_squad(n, seed)
    raise ValueError(cell)


CELL_GEN = {
    "mmlu_gen_letter": (8, ["\n\n"]),
    "mmlu_gen_cot": (512, []),
    "gsm8k_gen_cot": (400, ["\nQuestion:"]),
    "gsm8k_gen_direct": (24, ["\nQuestion:"]),
    "squad_gen": (48, ["\n"]),
}


@torch.no_grad()
def run_rank(model, tok, items, bs):
    """Score each candidate continuation by summed token log-probability.

    Only the logits at the continuation positions are materialised: with a 128k
    vocabulary, keeping the full logit tensor for a batch of long few-shot prompts
    costs tens of GB and is entirely wasted.
    """
    flat = []
    for it in items:
        for ci, cand in enumerate(it["candidates"]):
            flat.append((it["id"], ci, it["prompt"], cand))
    scores = {}
    pad = tok.pad_token_id or tok.eos_token_id
    for s in range(0, len(flat), bs):
        chunk = flat[s:s + bs]
        seqs, clens = [], []
        for _, _, p, c in chunk:
            pi = tok(p, add_special_tokens=True)["input_ids"]
            ci_ = tok(c, add_special_tokens=False)["input_ids"]
            seqs.append(pi + ci_); clens.append(len(ci_))
        m = max(len(x) for x in seqs)
        keep = max(clens) + 1                      # logits needed at the tail only
        ids = torch.full((len(seqs), m), pad, dtype=torch.long)
        att = torch.zeros((len(seqs), m), dtype=torch.long)
        for i, x in enumerate(seqs):               # left pad
            ids[i, m - len(x):] = torch.tensor(x); att[i, m - len(x):] = 1
        ids, att = ids.to(model.device), att.to(model.device)
        logits = model(input_ids=ids, attention_mask=att,
                       logits_to_keep=keep).logits.float()
        lp = torch.log_softmax(logits, -1)         # window covers positions m-keep..m-1
        base = m - keep
        for i, (iid, ci_, _, _) in enumerate(chunk):
            tot = 0.0
            for pos in range(m - clens[i], m):     # continuation token positions
                tot += lp[i, pos - 1 - base, ids[i, pos]].item()
            scores[(iid, ci_)] = tot
    out = []
    for it in items:
        sc = [scores[(it["id"], c)] for c in range(len(it["candidates"]))]
        out.append({"id": it["id"], "scores": sc,
                    "pred_index": int(max(range(len(sc)), key=lambda k: sc[k])),
                    "gold_index": it["gold_index"], "gold": it["gold"],
                    "meta": it["meta"]})
    return out


@torch.no_grad()
def run_gen(model, tok, items, bs, max_new, stops):
    order = sorted(range(len(items)), key=lambda i: -len(items[i]["prompt"]))
    out = {}
    for s in range(0, len(order), bs):
        idxs = order[s:s + bs]
        prompts = [items[i]["prompt"] for i in idxs]
        enc = tok(prompts, return_tensors="pt", padding=True,
                  padding_side="left").to(model.device)
        gen = model.generate(**enc, max_new_tokens=max_new, do_sample=False,
                             pad_token_id=tok.pad_token_id or tok.eos_token_id)
        new = gen[:, enc["input_ids"].shape[1]:]
        for j, i in enumerate(idxs):
            txt = tok.decode(new[j], skip_special_tokens=True)
            for st in stops:
                if st in txt:
                    txt = txt.split(st)[0]
            out[i] = {"id": items[i]["id"], "output": txt,
                      "n_new_tokens": int((new[j] != (tok.pad_token_id or tok.eos_token_id)).sum()),
                      "gold": items[i]["gold"], "meta": items[i]["meta"]}
    return [out[i] for i in range(len(items))]


def run_one(model, tok, a_model_name, cell, mask_mode, mask_seed, keep_frac,
            placement, n, data_seed, bs, out):
    d = model.config.hidden_size
    mask = build_mask(d, mask_mode, keep_frac, mask_seed)
    items = load_items(cell, n, data_seed)
    t0 = time.time()
    with ReadoutTruncation(model, mask, placement):
        if cell.endswith("_rank"):
            recs = run_rank(model, tok, items, bs * 2)
        else:
            mx, stops = CELL_GEN[cell]
            recs = run_gen(model, tok, items, bs, mx, stops)
    pathlib.Path(out).parent.mkdir(parents=True, exist_ok=True)
    header = {
        "_meta": True, "model": a_model_name, "cell": cell, "mask": mask_mode,
        "keep_frac": keep_frac, "mask_seed": mask_seed, "placement": placement,
        "hidden_size": d, "n_kept_dims": int(mask.sum()), "mask_id": mask_id(mask),
        "n_items": len(items), "data_seed": data_seed,
        "runtime_s": round(time.time() - t0, 1),
    }
    tmp = str(out) + ".partial"
    with open(tmp, "w") as f:
        f.write(json.dumps(header) + "\n")
        for r in recs:
            f.write(json.dumps(r) + "\n")
    os.replace(tmp, out)
    print("wrote", out, header["runtime_s"], "s", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--jobs", required=True,
                    help="JSON list of {cell,mask,mask_seed,n,bs,out}")
    ap.add_argument("--keep-frac", type=float, default=0.5)
    ap.add_argument("--placement", default="post_norm")
    ap.add_argument("--data-seed", type=int, default=1234)
    a = ap.parse_args()

    jobs = json.loads(pathlib.Path(a.jobs).read_text())
    jobs = [j for j in jobs if not pathlib.Path(j["out"]).exists()]
    if not jobs:
        print("nothing to do"); return

    tok = AutoTokenizer.from_pretrained(a.model)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        a.model, dtype=torch.bfloat16, device_map="cuda:0").eval()

    for j in jobs:
        try:
            run_one(model, tok, a.model, j["cell"], j["mask"],
                    j.get("mask_seed", 0), j.get("keep_frac", a.keep_frac),
                    a.placement, j["n"], a.data_seed, j["bs"], j["out"])
        except Exception as e:
            import traceback; traceback.print_exc()
            print("FAILED", j["out"], type(e).__name__, e, flush=True)


if __name__ == "__main__":
    main()
