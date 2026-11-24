import json, sys, numpy as np, collections
from transformers import AutoTokenizer
tok = AutoTokenizer.from_pretrained("/tmp/xiang_e194/models/H")
P = json.load(open("/tmp/xiang_e194/passages.json"))["passages"][:200]
A, B = np.load("/tmp/xiang_e194/out221/T.npz"), np.load("/tmp/xiang_e194/out221/H.npz")
d = A["base_nll"] - B["base_nll"]
rows = []
for pid, p in enumerate(P):
    seq = [tok.eos_token_id] + tok(p["text"], add_special_tokens=False)["input_ids"][:511]
    strs = tok.convert_ids_to_tokens(seq)
    for t in range(1, len(seq)):
        rows.append((pid, t, strs[t], "".join(strs[max(1, t - 8):t]).replace("Ġ", " ").replace("Ċ", "\\n")))
assert len(rows) == len(d), (len(rows), len(d))
def cat(s):
    b = s.replace("Ġ", "").replace("Ċ", "")
    if "Ċ" in s and not b: return "newline"
    if not b: return "space"
    if all(not c.isalnum() for c in b): return "punct"
    if any(c.isdigit() for c in b): return "digit"
    if s.startswith("Ġ"): return "word_start_cap" if b[:1].isupper() else "word_start_lower"
    return "no_space_piece"
cats = np.array([cat(r[2]) for r in rows])
o = np.argsort(-np.abs(d)); top = o[:len(d)//20]
allc = collections.Counter(cats); topc = collections.Counter(cats[top])
print("category: share all / share top5% / mean d in top5% (d>0 hybrid better)")
for c in sorted(allc, key=lambda c: -allc[c]):
    m = cats[top] == c
    print(f"  {c:18s} {allc[c]/len(d):.3f} / {topc[c]/len(top):.3f} / {d[top][m].mean() if m.any() else float('nan'):+.2f}")
pos = np.array([r[1] for r in rows])
print("position: corr(|d|, position)", round(np.corrcoef(np.abs(d), pos)[0,1],3), " mean |d| first 32 positions", round(np.abs(d)[pos<=32].mean(),3), "rest", round(np.abs(d)[pos>32].mean(),3))
print("examples (largest hybrid-better, then largest transformer-better):")
for sgn in (1, -1):
    oo = np.argsort(-sgn * d)[:12]
    for i in oo:
        r = rows[i]; print(f"  d={d[i]:+.2f}  ...{r[3][-40:]!r} -> {r[2]!r}")
