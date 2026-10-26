"""E121: OLMoE-1B-7B routing organisation and expert differentiation (inference only).

  e121_olmoe.py capture REV      router inputs at target positions (all items), a calibration sample of router inputs
                                 (cal-split items, random positions), baseline next-token log-probs (POS items, main only)
                                 and per-expert mean outputs (main only)  -> /home/xiang/mechpop_cache/e121/REV/
  e121_olmoe.py intervene        R3 interventions on POS items with the main checkpoint -> results/e121/r3_raw.pt (local)
"""
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from transformers import OlmoeForCausalLM
from transformers.models.olmoe import modeling_olmoe as mo

WB = Path(__file__).resolve().parents[1]
RES = WB / "results" / "e121"
STORE = Path("/home/xiang/mechpop_cache/e121")
import os
CKPT = Path(os.environ.get("OLMOE_DIR", "/home/xiang/mechpop_cache/hf_olmoe"))
DEV = "cuda"
PAD = 1
CTX = {}


# ------------------------------------------------------------------ custom MoE forward (same maths as HF 4.57)
def moe_forward(self, hidden_states):
    Bsz, T, Dm = hidden_states.shape
    x = hidden_states.view(-1, Dm)
    logits = self.gate(x)
    L = self._layer_idx
    if CTX.get("store_last") is not None:
        CTX["store_last"][L].append(x[CTX["last_rows"]].detach().to("cpu", torch.float16))
    if CTX.get("store_cal") is not None and CTX.get("cal_rows") is not None:
        CTX["store_cal"][L].append(x[CTX["cal_rows"]].detach().to("cpu", torch.float16))
    w = F.softmax(logits, dim=1, dtype=torch.float)
    w, sel = torch.topk(w, self.top_k, dim=-1)
    clamp = None
    if CTX.get("int_layer") == L:
        rows, mode, slot = CTX["last_rows"], CTX["mode"], CTX["slot"]
        order = logits[rows].float().argsort(-1, descending=True)
        old = sel[rows, slot].clone()
        if mode == "swap9":
            new = order[:, self.top_k]
        elif mode == "swaprand":
            g = torch.Generator(device="cpu").manual_seed(1000 + L)
            pick = torch.randint(self.top_k, logits.shape[1], (len(rows),), generator=g).to(rows.device)
            new = order.gather(1, pick[:, None])[:, 0]
        elif mode == "self":
            new = old
        elif mode in ("drop", "clamp"):
            new = old
        else:
            raise ValueError(mode)
        sel[rows, slot] = new
        if mode == "drop":
            w[rows, slot] = 0.0
        if mode == "clamp":
            clamp = (rows, slot, old)
        CTX["log"].append({"layer": L, "old": old.cpu(), "new": new.cpu()})
    w = w.to(x.dtype)
    out = torch.zeros_like(x)
    mean_rows = CTX.get("mean_rows")
    for e in range(self.num_experts):
        r, c = torch.where(sel == e)
        if r.numel() == 0:
            continue
        y = self.experts[e](x[r])
        if mean_rows is not None:
            m = mean_rows[r]
            if m.any():
                CTX["mean_sum"][L, e] += y[m].float().sum(0)
                CTX["mean_cnt"][L, e] += int(m.sum())
        if clamp is not None:
            rows, slot, old = clamp
            hit = torch.isin(r, rows[(old == e)]) & (c == slot)
            if hit.any():
                y = y.clone()
                y[hit] = CTX["mean_out"][L, e].to(y.dtype)
        out.index_add_(0, r, y * w[r, c, None])
    return out.view(Bsz, T, Dm), logits


mo.OlmoeSparseMoeBlock.forward = moe_forward


def load(rev):
    m = OlmoeForCausalLM.from_pretrained(CKPT / rev, dtype=torch.bfloat16).to(DEV).eval()
    for i, layer in enumerate(m.model.layers):
        layer.mlp._layer_idx = i
    return m


def read_items():
    items = []
    for name in ("pos", "sense"):
        for line in open(RES / f"items_{name}.jsonl"):
            it = json.loads(line)
            it["set"] = name
            items.append(it)
    return items


def batches(items, bs):
    for i in range(0, len(items), bs):
        chunk = items[i : i + bs]
        T = max(len(it["ids"]) for it in chunk)
        ids = torch.full((len(chunk), T), PAD, dtype=torch.long)
        att = torch.zeros((len(chunk), T), dtype=torch.long)
        for b, it in enumerate(chunk):
            ids[b, : len(it["ids"])] = torch.tensor(it["ids"])
            att[b, : len(it["ids"])] = 1
        last = torch.tensor([len(it["ids"]) - 1 for it in chunk])
        yield i, chunk, ids.to(DEV), att.to(DEV), last.to(DEV), T


@torch.no_grad()
def capture(rev, bs=32, cal_per_item=12, seed=0):
    out = STORE / rev
    out.mkdir(parents=True, exist_ok=True)
    m = load(rev)
    items = read_items()
    nL = len(m.model.layers)
    E = m.config.num_experts
    rng = np.random.default_rng(seed)
    CTX.clear()
    CTX["store_last"] = [[] for _ in range(nL)]
    CTX["store_cal"] = [[] for _ in range(nL)]
    is_main = rev == "main"
    if is_main:
        CTX["mean_sum"] = torch.zeros(nL, E, m.config.hidden_size, device=DEV)
        CTX["mean_cnt"] = torch.zeros(nL, E, device=DEV)
    base_lp, nll, cal_meta = [], [], []
    t0 = time.time()
    for i, chunk, ids, att, last, T in batches(items, bs):
        CTX["last_rows"] = torch.arange(len(chunk), device=DEV) * T + last
        cal_rows = []
        for b, it in enumerate(chunk):
            if it["split"] != "cal":
                continue
            n = len(it["ids"])
            pos = rng.choice(np.arange(4, n), size=min(cal_per_item, max(0, n - 4)), replace=False) if n > 4 else []
            cal_rows += [b * T + int(p) for p in pos]
            cal_meta += [(i + b, int(p)) for p in pos]
        CTX["cal_rows"] = torch.tensor(cal_rows, device=DEV, dtype=torch.long) if cal_rows else None
        if is_main:
            mr = torch.zeros(len(chunk) * T, dtype=torch.bool, device=DEV)
            for b, it in enumerate(chunk):
                if it["split"] == "cal":
                    mr[b * T : b * T + len(it["ids"])] = True
            CTX["mean_rows"] = mr
        logits = m(input_ids=ids, attention_mask=att, use_cache=False).logits
        lp = torch.log_softmax(logits[torch.arange(len(chunk), device=DEV), last].float(), -1)
        nxt = torch.tensor([it["next_id"] for it in chunk], device=DEV)
        nll.append((-lp.gather(1, nxt[:, None])[:, 0]).cpu())
        if is_main:
            base_lp.append(lp.to(torch.float16).cpu())
        if i % (bs * 20) == 0:
            print(f"{rev} {i}/{len(items)} {time.time()-t0:.0f}s", flush=True)
    H_last = torch.stack([torch.cat(v) for v in CTX["store_last"]])  # L x N x d
    H_cal = torch.stack([torch.cat(v) for v in CTX["store_cal"]])
    torch.save({"H_last": H_last, "H_cal": H_cal, "nll": torch.cat(nll), "cal_meta": cal_meta,
                "gates": torch.stack([l.mlp.gate.weight.detach().float().cpu() for l in m.model.layers])}, out / "capture.pt")
    if is_main:
        torch.save({"base_lp": torch.cat(base_lp), "mean_out": (CTX["mean_sum"] / CTX["mean_cnt"].clamp_min(1)[..., None]).cpu(),
                    "mean_cnt": CTX["mean_cnt"].cpu()}, out / "main_extra.pt")
    print("saved", out, H_last.shape, H_cal.shape, f"{time.time()-t0:.0f}s", flush=True)


@torch.no_grad()
def intervene(bs=32, layers=None, modes=("self", "drop", "swap9", "swaprand", "clamp"), slots=(0, 3)):
    m = load("main")
    items = [it for it in read_items() if it["set"] == "pos"]
    extra = torch.load(STORE / "main" / "main_extra.pt")
    allitems = read_items()
    idx_pos = [k for k, it in enumerate(allitems) if it["set"] == "pos"]
    base_lp = extra["base_lp"][torch.tensor(idx_pos)]  # stored for all items in read order; keep POS rows
    CTX.clear()
    CTX["mean_out"] = extra["mean_out"].to(DEV)
    nL = len(m.model.layers)
    layers = range(nL) if layers is None else layers
    res = {}
    t0 = time.time()
    for L in layers:
        for mode in modes:
            for slot in slots:
                if mode == "self" and slot != 0:
                    continue
                key = f"L{L}_{mode}_s{slot}"
                CTX.update({"int_layer": L, "mode": mode, "slot": slot, "log": []})
                dn, kl = [], []
                for i, chunk, ids, att, last, T in batches(items, bs):
                    CTX["last_rows"] = torch.arange(len(chunk), device=DEV) * T + last
                    logits = m(input_ids=ids, attention_mask=att, use_cache=False).logits
                    lp = torch.log_softmax(logits[torch.arange(len(chunk), device=DEV), last].float(), -1)
                    b = base_lp[i : i + len(chunk)].to(DEV).float()
                    nxt = torch.tensor([it["next_id"] for it in chunk], device=DEV)
                    dn.append((-lp.gather(1, nxt[:, None])[:, 0] + b.gather(1, nxt[:, None])[:, 0]).cpu())
                    kl.append((b.exp() * (b - lp)).sum(-1).cpu())
                res[key] = {"dnll": torch.cat(dn), "kl": torch.cat(kl), "old": torch.cat([d["old"] for d in CTX["log"]]),
                            "new": torch.cat([d["new"] for d in CTX["log"]])}
        print(f"layer {L} done {time.time()-t0:.0f}s", flush=True)
        torch.save(res, STORE / "main" / "r3_raw.pt")
    CTX.clear()


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "capture":
        capture(sys.argv[2])
    elif cmd == "intervene":
        intervene()
