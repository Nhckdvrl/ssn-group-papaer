#!/usr/bin/env python3
"""E167 R1–R3 capture: routing of every checkpoint on UD English EWT words.

For each checkpoint and layer, on the pre-registered anchor words (`sel`, same-type
pairs) it stores the real co-routing C_ij=|S_i∩S_j|/k, its N1 null expectation
B_ij (expert-geometry-preserving rotation inside the router readout subspace,
bias re-fitted on cal words to match real loads; 32 draws) and the hidden-state
cosine kernel Kh_ij (centred router inputs). Also stores per-word top-k sets and
the type-mean routing vector for T_lex. Cross-model statistics are computed by
`analyze_routing.py`; nothing here compares models.

Usage: capture_routing.py OUT_DIR CKPT [CKPT ...]
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
from transformers import AutoTokenizer

sys.path.insert(0, str(Path(__file__).parent))
import moe_measure as mm  # noqa: E402
from moe_model import Config, MoELM  # noqa: E402

TOKENIZER_DIR = Path("/home/xiang/mechpop_cache/hf_olmo_dense/main")
PASSAGES = Path(__file__).resolve().parents[1] / "results/e167/passages.json"
N1_DRAWS, N1_SEED = 32, 167


def word_token_index(tok, passages, words):
    """Token position covering each word's last character; -1 if that token runs past the word end."""
    enc, pos = [], np.full(len(words), -1, np.int64)
    for p in passages:
        e = tok(p["text"], add_special_tokens=False, return_offsets_mapping=True)
        enc.append((e["input_ids"], e["offset_mapping"]))
    for n, (pid, s, end, form, upos, split) in enumerate(words):
        ids, offs = enc[pid]
        for t, (a, b) in enumerate(offs):
            if a <= end - 1 < b:
                if b <= end:
                    pos[n] = t + 1  # +1 for the prepended EOS
                break
    return enc, pos


def type_pairs(words, sel, valid):
    by = {}
    for local, n in enumerate(sel):
        if valid[n]:
            by.setdefault(words[n][3].lower(), []).append(local)
    ii, jj, tt = [], [], []
    for t_id, (t, locs) in enumerate(sorted(by.items())):
        for a in range(len(locs)):
            for b in range(a + 1, len(locs)):
                ii.append(locs[a]); jj.append(locs[b]); tt.append(t_id)
    return np.array(ii), np.array(jj), np.array(tt), sorted(by)


@torch.no_grad()
def capture(model, enc, groups, device):
    """Return per layer: H (router input) and logits(+bias) for the token positions in each group."""
    L = model.cfg.n_layers
    store = {g: [[None] * len(idx) for _ in range(L)] for g, idx in groups.items()}
    want = {}
    for g, items in groups.items():
        for slot, (pid, t) in enumerate(items):
            want.setdefault(pid, []).append((g, slot, t))
    feats = [None] * L

    def hook(li):
        def f(mod, inp):
            feats[li] = inp[0].detach()
        return f
    hs = [blk.moe.register_forward_pre_hook(hook(i)) for i, blk in enumerate(model.blocks)]
    eos = 50279
    for pid, (ids, _) in enumerate(enc):
        if pid not in want:
            continue
        x = torch.tensor([[eos] + ids], device=device)
        with torch.autocast("cuda", torch.bfloat16):
            model(x)
        for li in range(L):
            h = feats[li][0].float()
            for g, slot, t in want[pid]:
                store[g][li][slot] = h[t]
    for h in hs:
        h.remove()
    return {g: [torch.stack(v) for v in per] for g, per in store.items()}


def main():
    out_dir = Path(sys.argv[1])
    ckpts = [Path(p) for p in sys.argv[2:]]
    device = torch.device("cuda")
    tok = AutoTokenizer.from_pretrained(TOKENIZER_DIR, local_files_only=True, use_fast=True)
    assert tok.eos_token_id == 50279
    P = json.loads(PASSAGES.read_text())
    passages, words, sel, cal = P["passages"], P["words"], P["sel"], P["cal"]
    enc, pos = word_token_index(tok, passages, words)
    valid = pos >= 0
    ii, jj, tt, types = type_pairs(words, sel, valid)
    sel_v = [n for n in sel if valid[n]]
    sel_local = {n: k for k, n in enumerate(sel)}
    # re-index pairs to valid-only list
    remap = {sel_local[n]: k for k, n in enumerate(sel_v)}
    ii = np.array([remap[a] for a in ii]); jj = np.array([remap[b] for b in jj])
    cal_v = [n for n in cal if valid[n]]
    groups = {"anchor": [(words[n][0], pos[n]) for n in sel_v],
              "cal": [(words[n][0], pos[n]) for n in cal_v]}
    out_dir.mkdir(parents=True, exist_ok=True)
    meta = {"n_anchor": len(sel_v), "n_anchor_invalid": int(len(sel) - len(sel_v)), "n_cal": len(cal_v),
            "n_pairs": int(len(ii)), "n_types": len(types), "passages_sha256": hashlib.sha256(PASSAGES.read_bytes()).hexdigest(),
            "null": {"kind": "N1", "draws": N1_DRAWS, "seed": N1_SEED}}
    (out_dir / "capture_meta.json").write_text(json.dumps(meta, indent=1))
    np.savez(out_dir / "pairs.npz", i=ii, j=jj, type=tt, anchor_word=np.array(sel_v), anchor_upos=np.array([words[n][4] for n in sel_v]),
             anchor_type=np.array([words[n][3].lower() for n in sel_v]))
    pi, pj = torch.tensor(ii, device=device), torch.tensor(jj, device=device)
    for ck in ckpts:
        target = out_dir / f"{ck.parent.name}__{ck.stem}.npz"
        if target.exists():
            continue
        t0 = time.time()
        st = torch.load(ck, map_location="cpu", weights_only=False)
        cfg = Config(**st["config"])
        model = MoELM(cfg)
        model.load_state_dict({k: v.float() for k, v in st["model"].items()})
        model.to(device).eval()
        feats = capture(model, enc, groups, device)
        res = {}
        k, E = cfg.top_k, cfg.n_experts
        for li, blk in enumerate(model.blocks):
            W = blk.moe.router.weight.float()
            b = blk.moe.sel_bias.float()
            Ha, Hc = feats["anchor"][li], feats["cal"][li]
            Sa = (Ha @ W.T + b).topk(k, -1).indices
            C = mm.coroute(Sa, E, k, (pi, pj))
            null = mm.null_expectation(W.double(), b.double(), Hc.double(), Ha.double(), k, "N1",
                                       n_draws=N1_DRAWS, seed=N1_SEED, pairs=(pi, pj))
            Hz = Ha - Hc.mean(0)
            Hn = Hz / Hz.norm(dim=1, keepdim=True).clamp_min(1e-8)
            Kh = (Hn[pi] * Hn[pj]).sum(1)
            res[f"C{li}"] = C.cpu().numpy().astype(np.float32)
            res[f"B{li}"] = null["B"].cpu().numpy().astype(np.float32)
            res[f"Kh{li}"] = Kh.cpu().numpy().astype(np.float32)
            res[f"S{li}"] = Sa.cpu().numpy().astype(np.int16)
            res[f"loadtv{li}"] = np.float32(null["load_tv"])
        np.savez_compressed(target, tokens=st["tokens"], init_seed=st["init_seed"], data_seed=st["data_seed"], **res)
        print(json.dumps({"ckpt": str(ck), "sec": round(time.time() - t0, 1)}), flush=True)
        del model, st
        torch.cuda.empty_cache()


if __name__ == "__main__":
    main()
