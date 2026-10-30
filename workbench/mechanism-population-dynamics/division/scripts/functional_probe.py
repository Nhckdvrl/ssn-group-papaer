#!/usr/bin/env python3
"""E167 R0 (is there a division at all?) and R4 (per-expert functional fingerprints).

Text: all UD English EWT passages (anchor + cal splits), each prefixed by EOS.
Each token gets a category = UPOS of the word containing its first character
(x word-initial / continuation), or NONE.

R0, per layer: held NLL change when the routed output is replaced by
  mean   : (sum of gates) x mean over all experts   (E134 "uniform"; 0 if experts identical)
  swap9  : top-1 expert replaced by the (k+1)-th ranked expert, gate kept (E121)
  random : k random distinct experts, gates kept
R4, per layer and expert e: drop e (tokens that chose e use the (k+1)-th expert, gate kept);
  fingerprint = mean dNLL per category, separately on the anchor and cal splits.
Also stores the routing fingerprint P(expert | category) per layer.

Usage: functional_probe.py OUT_DIR [--no-r4] CKPT [CKPT ...]
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer

sys.path.insert(0, str(Path(__file__).parent))
from moe_model import Config, MoELM, rope_cache  # noqa: E402

TOKENIZER_DIR = Path("/home/xiang/mechpop_cache/hf_olmo_dense/main")
PASSAGES = Path(__file__).resolve().parents[1] / "results/e167/passages.json"
UPOS = ["ADJ", "ADP", "ADV", "AUX", "CCONJ", "DET", "INTJ", "NOUN", "NUM", "PART", "PRON", "PROPN",
        "PUNCT", "SCONJ", "SYM", "VERB", "X"]
CATS = [f"{u}:{p}" for u in UPOS for p in ("init", "cont")] + ["NONE"]
EOS = 50279
BATCH = int(__import__("os").environ.get("E167_BATCH", 64))


def build_text(tok):
    P = json.loads(PASSAGES.read_text())
    words_by_p = {}
    for pid, s, e, form, upos, split in P["words"]:
        words_by_p.setdefault(pid, []).append((s, e, upos))
    seqs = []
    for p in P["passages"]:
        enc = tok(p["text"], add_special_tokens=False, return_offsets_mapping=True)
        ws = words_by_p.get(p["id"], [])
        cat = []
        for a, b in enc["offset_mapping"]:
            txt = p["text"][a:b]
            a2 = a + (len(txt) - len(txt.lstrip()))
            c = len(CATS) - 1
            for s, e, upos in ws:
                if s <= a2 < e:
                    c = UPOS.index(upos) * 2 + (0 if a2 == s else 1) if upos in UPOS else c
                    break
            cat.append(c)
        seqs.append({"ids": [EOS] + enc["input_ids"], "cat": [len(CATS) - 1] + cat,
                     "split": 0 if p["split"] == "anchor" else 1})
    return seqs


def batches(seqs, device):
    order = sorted(range(len(seqs)), key=lambda i: len(seqs[i]["ids"]))
    out = []
    for i in range(0, len(order), BATCH):
        idx = order[i:i + BATCH]
        T = max(len(seqs[j]["ids"]) for j in idx)
        ids = torch.full((len(idx), T), EOS, dtype=torch.long)
        cat = torch.full((len(idx), T), -1, dtype=torch.long)
        spl = torch.zeros(len(idx), T, dtype=torch.long)
        for r, j in enumerate(idx):
            n = len(seqs[j]["ids"])
            ids[r, :n] = torch.tensor(seqs[j]["ids"])
            cat[r, :n] = torch.tensor(seqs[j]["cat"])
            spl[r, :n] = seqs[j]["split"]
        out.append((ids.to(device), cat.to(device), spl.to(device)))
    return out


@torch.no_grad()
def cache_inputs(model, bs):
    """Residual-stream input (fp32) of every block, per batch, from one intact pass."""
    caches = []
    for ids, cat, spl in bs:
        T = ids.shape[1]
        cos, sin = rope_cache(T, model.cfg.d_model // model.cfg.n_heads, model.cfg.rope_theta, ids.device)
        with torch.autocast("cuda", torch.bfloat16):
            x = model.emb(ids)
            xs = []
            for blk in model.blocks:
                xs.append(x.float().clone())
                x, *_ = blk(x, cos, sin)
        caches.append(xs)
    return caches


@torch.no_grad()
def token_nll(model, bs, caches=None, start=0):
    """Per input position t: NLL of token t+1. With caches, recompute only blocks >= start."""
    res = []
    for bi, (ids, cat, spl) in enumerate(bs):
        T = ids.shape[1]
        with torch.autocast("cuda", torch.bfloat16):
            if caches is None:
                logits = model(ids)
            else:
                cos, sin = rope_cache(T, model.cfg.d_model // model.cfg.n_heads, model.cfg.rope_theta, ids.device)
                x = caches[bi][start].float()
                for blk in model.blocks[start:]:
                    x, *_ = blk(x, cos, sin)
                logits = model.head(model.norm(x))
        nll = F.cross_entropy(logits[:, :-1].float().transpose(1, 2), ids[:, 1:], reduction="none")
        valid = (cat[:, 1:] >= 0)  # next token is real
        res.append((nll, valid, cat[:, :-1], spl[:, :-1]))
    return res


def flat(res):
    nll = torch.cat([r[0][r[1]] for r in res])
    cat = torch.cat([r[2][r[1]] for r in res])
    spl = torch.cat([r[3][r[1]] for r in res])
    return nll, cat, spl


def cat_means(d, cat, spl, n_cat):
    out = torch.zeros(2, n_cat, device=d.device)
    for s in (0, 1):
        m = spl == s
        out[s] = torch.zeros(n_cat, device=d.device).index_add_(0, cat[m], d[m]) / \
            torch.bincount(cat[m], minlength=n_cat).clamp_min(1)
    return out


def main():
    args = sys.argv[1:]
    out_dir = Path(args.pop(0))
    r4 = True
    if args and args[0] == "--no-r4":
        r4 = False
        args.pop(0)
    device = torch.device("cuda")
    tok = AutoTokenizer.from_pretrained(TOKENIZER_DIR, local_files_only=True, use_fast=True)
    seqs = build_text(tok)
    bs = batches(seqs, device)
    out_dir.mkdir(parents=True, exist_ok=True)
    for ck in map(Path, args):
        target = out_dir / f"{ck.parent.name}__{ck.stem}.npz"
        if target.exists():
            continue
        t0 = time.time()
        st = torch.load(ck, map_location="cpu", weights_only=False)
        cfg = Config(**st["config"])
        model = MoELM(cfg)
        model.load_state_dict({k: v.float() for k, v in st["model"].items()})
        model.to(device).eval()
        k, E, L, nc = cfg.top_k, cfg.n_experts, cfg.n_layers, len(CATS)
        base, cat, spl = flat(token_nll(model, bs))
        caches = cache_inputs(model, bs)
        chk = (flat(token_nll(model, bs, caches, 0))[0] - base).abs().max().item()
        out = {"cache_check": chk}
        out.update({"base_nll": base.mean().item(), "tokens": st["tokens"]})
        # routing fingerprint P(expert | category), and R0
        r0 = np.zeros((L, 3))
        route_fp = np.zeros((L, 2, nc, E))
        for li, blk in enumerate(model.blocks):
            moe = blk.moe
            gen = torch.Generator(device=device).manual_seed(1000 + li)

            def swap9(topi, topv, probs, scores):
                top = scores.topk(k + 1, -1).indices
                t2 = topi.clone()
                t2[:, 0] = top[:, k]
                return t2, topv

            def rand(topi, topv, probs, scores):
                r = torch.rand(topi.shape[0], E, device=device, generator=gen).topk(k, -1).indices
                return r, topv
            moe.mean_replace = True
            r0[li, 0] = (flat(token_nll(model, bs, caches, li))[0] - base).mean().item()
            moe.mean_replace = False
            for j, fn in ((1, swap9), (2, rand)):
                moe.expert_override = fn
                r0[li, j] = (flat(token_nll(model, bs, caches, li))[0] - base).mean().item()
            moe.expert_override = None
        # routing counts by category (from an intact pass with record on)
        for li, blk in enumerate(model.blocks):
            blk.moe.record = {}
        with torch.no_grad():
            for ids, c, s in bs:
                with torch.autocast("cuda", torch.bfloat16):
                    model(ids)
                cflat, sflat = c.reshape(-1), s.reshape(-1)
                for li, blk in enumerate(model.blocks):
                    ti = blk.moe.record["topi"]
                    oh = torch.zeros(ti.shape[0], E, device=device).scatter_(1, ti, 1.0)
                    for sp in (0, 1):
                        m = (cflat >= 0) & (sflat == sp)
                        route_fp[li, sp] += torch.zeros(nc, E, device=device).index_add_(0, cflat[m], oh[m]).cpu().numpy()
        for blk in model.blocks:
            blk.moe.record = None
        route_fp /= np.maximum(route_fp.sum(3, keepdims=True) / k, 1)
        out["r0"] = r0
        out["route_fp"] = route_fp.astype(np.float32)
        if r4:
            fp = np.zeros((L, E, 2, nc), np.float32)
            tot = np.zeros((L, E), np.float32)
            for li, blk in enumerate(model.blocks):
                moe = blk.moe
                for e in range(E):
                    def drop(topi, topv, probs, scores, e=e):
                        nxt = scores.topk(k + 1, -1).indices[:, k:k + 1]
                        return torch.where(topi == e, nxt, topi), topv
                    moe.expert_override = drop
                    d = flat(token_nll(model, bs, caches, li))[0] - base
                    fp[li, e] = cat_means(d, cat, spl, nc).cpu().numpy()
                    tot[li, e] = d.mean().item()
                moe.expert_override = None
            out["drop_fp"] = fp
            out["drop_total"] = tot
        out["cat_counts"] = np.stack([torch.bincount(cat[spl == s], minlength=nc).cpu().numpy() for s in (0, 1)])
        np.savez_compressed(target, **{k2: np.asarray(v) for k2, v in out.items()})
        print(json.dumps({"ckpt": str(ck), "sec": round(time.time() - t0, 1), "base": round(out["base_nll"], 4), "cache_check": chk,
                          "r0_mean": [round(x, 4) for x in r0[:, 0]], "r0_swap9": [round(x, 4) for x in r0[:, 1]]}), flush=True)
        del model, st
        torch.cuda.empty_cache()


if __name__ == "__main__":
    main()
