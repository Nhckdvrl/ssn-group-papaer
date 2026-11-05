#!/usr/bin/env python3
"""E174 granularity 3 prep: rebuild the E168 v3 Dolma eval windows and POS-tag them (CPU only).

Rebuilds `transplant.windows(128)` exactly (same held shards, rng 168, cal drawn first), decodes each
window token by token, runs spaCy en_core_web_sm 3.8 (automatic UPOS / ClearNLP dep; NOT UD gold), and
labels every input position t (the routed token; D[e, w, t] is the dNLL of predicting t+1) with the
spaCy token containing its first non-space character: upos, word-initial flag, prev/next upos within
the sentence (BOS / EOS at edges), dep. Whitespace-only tokens -> SPACE, EOS id -> EOSTOK.

Pipeline check: with the I0D0 3.2B capture, two occurrences of the same token id must share far more
layer-2 experts than two different ids (otherwise the rebuilt windows are not the captured ones).

Usage: e174_tag_windows.py SPACY_MODEL_DIR  -> ~/mechpop_cache/e174/window_tags.npz
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, sys.argv[1])
from train_moe import build_windows, get_batch  # noqa: E402

HELD = Path("/tmp/xiang-e167/data/held")
SEQ, N_CAL, N_WIN = 1024, 256, 128
TOKENIZER_DIR = Path("/home/xiang/mechpop_cache/hf_olmo_dense/main")
OUT = Path.home() / "mechpop_cache/e174"
WB = Path(__file__).resolve().parents[1]

files, arrs, fid, off = build_windows(HELD, SEQ)
rng = np.random.default_rng(168)
cal_pool = np.where(fid % 3 == 0)[0]
ev_pool = np.where(fid % 3 != 0)[0]
_cal = rng.choice(cal_pool, N_CAL, replace=False)
ev = rng.choice(ev_pool, N_WIN, replace=False)
ids = get_batch(arrs, fid, off, ev, SEQ).numpy()  # N_WIN x SEQ+1

from transformers import AutoTokenizer  # noqa: E402
import en_core_web_sm  # noqa: E402

tok = AutoTokenizer.from_pretrained(TOKENIZER_DIR, local_files_only=True, use_fast=True)
nlp = en_core_web_sm.load()
eos = tok.eos_token_id

UP, DP = {}, {}


def code(d, k):
    if k not in d:
        d[k] = len(d)
    return d[k]


upos = np.zeros((N_WIN, SEQ), np.int16)
init = np.zeros((N_WIN, SEQ), np.int8)
prev = np.zeros((N_WIN, SEQ), np.int16)
nxt = np.zeros((N_WIN, SEQ), np.int16)
dep = np.zeros((N_WIN, SEQ), np.int16)
for w in range(N_WIN):
    pieces = [tok.decode([int(t)]) for t in ids[w, :SEQ]]
    starts = np.cumsum([0] + [len(p) for p in pieces])
    text = "".join(pieces)
    doc = nlp(text)
    # char -> spacy token index
    c2t = np.full(len(text) + 1, -1, np.int64)
    for st in doc:
        c2t[st.idx: st.idx + len(st.text)] = st.i
    sp_up = [st.pos_ for st in doc]
    sent_start = [st.is_sent_start for st in doc]
    sent_end = [(st.i + 1 == len(doc)) or bool(doc[st.i + 1].is_sent_start) for st in doc]
    for t in range(SEQ):
        p = pieces[t]
        if int(ids[w, t]) == eos:
            lab = ("EOSTOK", 1, "EOSTOK", "EOSTOK", "EOSTOK")
        else:
            a2 = starts[t] + (len(p) - len(p.lstrip()))
            k = c2t[a2] if a2 < starts[t + 1] else -1
            if k < 0 or sp_up[k] == "SPACE":
                lab = ("SPACE", 1, "SPACE", "SPACE", "SPACE")
            else:
                st = doc[k]
                # neighbours: nearest non-space tokens inside the sentence
                pk = k - 1
                while pk >= 0 and sp_up[pk] == "SPACE":
                    pk -= 1
                nk = k + 1
                while nk < len(doc) and sp_up[nk] == "SPACE":
                    nk += 1
                pu = "BOS" if (sent_start[k] or pk < 0) else sp_up[pk]
                nu = "EOS" if (sent_end[k] or nk >= len(doc)) else sp_up[nk]
                lab = (sp_up[k], int(a2 == st.idx), pu, nu, st.dep_)
        upos[w, t] = code(UP, lab[0]); init[w, t] = lab[1]
        prev[w, t] = code(UP, lab[2]); nxt[w, t] = code(UP, lab[3]); dep[w, t] = code(DP, lab[4])
    if w % 16 == 0:
        print("window", w, flush=True)

# pipeline check against the captured layer-2 routing of I0D0 at 3.2B
Z = np.load(Path.home() / "mechpop_cache/e167_analysis/token_roles/I0D0__ckpt_3200000000.npz")
S = Z["topi2"].reshape(-1, Z["topi2"].shape[-1])
flat = ids[:, :SEQ].reshape(-1)
r = np.random.default_rng(0)
same, diff = [], []
order = np.argsort(flat, kind="stable")
fs = flat[order]
bounds = np.flatnonzero(np.diff(fs)) + 1
groups = [g for g in np.split(order, bounds) if len(g) >= 2]
for _ in range(5000):
    g = groups[r.integers(len(groups))]
    a, b = r.choice(g, 2, replace=False)
    same.append(len(set(S[a]) & set(S[b])) / 8)
    a, b = r.integers(len(flat), size=2)
    if flat[a] != flat[b]:
        diff.append(len(set(S[a]) & set(S[b])) / 8)
check = {"same_id_coroute_L2": float(np.mean(same)), "diff_id_coroute_L2": float(np.mean(diff))}
print(check, flush=True)

OUT.mkdir(parents=True, exist_ok=True)
np.savez_compressed(OUT / "window_tags.npz", ids=ids, upos=upos, init=init, prev=prev, nxt=nxt, dep=dep)
meta = {"upos_vocab": UP, "dep_vocab": DP, "check": check, "tagger": "spacy en_core_web_sm 3.8.0 (automatic)",
        "n_win": N_WIN, "seq": SEQ,
        "upos_counts": {k: int((upos == v).sum()) for k, v in UP.items()}}
(OUT / "window_tags_meta.json").write_text(json.dumps(meta, indent=1))
(WB / "results/e174").mkdir(parents=True, exist_ok=True)
(WB / "results/e174/window_tags_meta.json").write_text(json.dumps(meta, indent=1))
print("saved", flush=True)
