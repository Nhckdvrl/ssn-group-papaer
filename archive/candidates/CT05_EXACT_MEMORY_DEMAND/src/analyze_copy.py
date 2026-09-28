"""E01 readout A decomposed by target-token type (analysis only, no new compute).

A target token is `copy-from-e` if the target trigram ending at it (t-2, t-1, t) occurs verbatim in
event e's tokens. For each event we split its KV-hide effect and its recurrence carry
(dBOTH - dKV) into copy-from-e tokens vs all other target tokens.

usage: analyze_copy.py RESULTS_DIR PREFIX MODEL_PATH CHECKPOINTS
"""
import glob, json, sys
import numpy as np
from transformers import AutoTokenizer
from render import render

D, PREFIX, MP, CK = sys.argv[1:5]
tok = AutoTokenizer.from_pretrained(MP)
cks = {json.loads(l)["cid"]: json.loads(l) for l in open(CK)}
recs = []
for f in sorted(glob.glob(f"{D}/{PREFIX}.s*.jsonl")):
    recs += [json.loads(l) for l in open(f)]
recs = [r for r in recs if "skip" not in r]

agg = {k: 0.0 for k in ["kv_copy", "kv_other", "both_copy", "both_other", "n_copy", "n_other"]}
imp_agg = dict(agg)
win_split = {k: [0.0, 0.0, 0, 0] for k in ["0", "2", "4"]}
for r in recs:
    x = render(tok, cks[r["cid"]])
    ids = x["ids"].tolist()
    N, lo = x["N"], x["dec_lo"]
    tgt = ids[N + lo:]
    ctx = ids[N:]  # decision chunk; trigram uses preceding decision tokens
    tri = [tuple(ctx[lo + t - 2: lo + t + 1]) for t in range(len(tgt))]

    def grams(s, e):
        seq = ids[s:e]
        return {tuple(seq[i:i + 3]) for i in range(len(seq) - 2)}
    for e in r["events"]:
        g = grams(e["s"], e["e"])
        is_copy = np.array([t in g for t in tri])
        kv = np.array(e["kv"]["tok_dnll"], dtype=float)
        if e.get("both") is None or len(kv) != len(is_copy):
            continue
        both = np.array(e["both"]["tok_dnll"], dtype=float)
        for A in ([agg, imp_agg] if e["text"]["dnll"] > 1.0 else [agg]):
            A["kv_copy"] += kv[is_copy].sum(); A["kv_other"] += kv[~is_copy].sum()
            A["both_copy"] += both[is_copy].sum(); A["both_other"] += both[~is_copy].sum()
            A["n_copy"] += is_copy.sum(); A["n_other"] += (~is_copy).sum()
    E = len(r["events"])
    for k in win_split:
        keep = {0, 1} | set(range(max(E - int(k), 0), E))
        g = set()
        for j, e in enumerate(r["events"]):
            if j not in keep:
                g |= grams(e["s"], e["e"])
        is_copy = np.array([t in g for t in tri])
        d = np.array(r["kvwin"][k]["tok_dnll"], dtype=float)
        if len(d) != len(is_copy):
            continue
        win_split[k][0] += d[is_copy].sum(); win_split[k][1] += d[~is_copy].sum()
        win_split[k][2] += is_copy.sum(); win_split[k][3] += (~is_copy).sum()

for name, A in [("all events", agg), ("important events (dTEXT>1)", imp_agg)]:
    print(f"{PREFIX} {name}: copy tokens {int(A['n_copy'])}, other {int(A['n_other'])}")
    print(f"   KV-hide dNLL: copy {A['kv_copy']:.1f}  other {A['kv_other']:.1f}")
    print(f"   recurrence carry (BOTH-KV): copy {A['both_copy'] - A['kv_copy']:.1f}  other {A['both_other'] - A['kv_other']:.1f}")
    print(f"   carry / (carry + KV) : copy {(A['both_copy'] - A['kv_copy']) / max(A['both_copy'], 1e-9):.2f}  "
          f"other {(A['both_other'] - A['kv_other']) / max(A['both_other'], 1e-9):.2f}")
for k, (c, o, nc, no) in win_split.items():
    print(f"   KVWIN{k}: dNLL on copy-from-hidden tokens {c:.1f} (n={nc}), other tokens {o:.1f} (n={no})")
