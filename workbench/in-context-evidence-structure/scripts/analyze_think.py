"""E09 thinking analysis: only samples that finished (< max_tokens and contain 'answer' in the tail).
usage: analyze_think.py RESULT_JSONL MAX_TOKENS"""
import json, re, sys, collections
import numpy as np
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from analyze_common import boot_ci, fmt  # noqa

path, mx = sys.argv[1], int(sys.argv[2])
QB = {}
for l in open(__file__.rsplit("/", 2)[0] + "/data/struct_pilot_n5_T16/rows.jsonl"):
    rr = json.loads(l); QB[rr["uid"]] = rr["query_label_B"]
per = collections.defaultdict(dict); fin = tot = 0
for l in open(path):
    r = json.loads(l)
    ok = [(a, ln, t) for a, ln, t in zip(r["ans"], r["lens"], r["tails"]) if ln < mx and re.search(r"(?i)answer", t) and a >= 0]
    tot += r["n"]; fin += len(ok)
    if ok:
        per[r["cond"]][r["base_id"]] = np.mean([a == QB[r["uid"]] for a, _, _ in ok])
print(f"finished {fin}/{tot} ({fin / tot:.0%})")
for c in ["allA", "disp_4", "suffix_4", "noise_2__suffix_4", "block_start4", "suffix_8"]:
    v = list(per[c].values())
    if v:
        print(f"  {c:18s} P(B) {np.mean(v):.3f}  (n bases {len(v)})")
def paired(a, b):
    ks = sorted(set(per[a]) & set(per[b]))
    return np.array([per[a][k] - per[b][k] for k in ks])
for a, b in [("suffix_4", "disp_4"), ("noise_2__suffix_4", "suffix_4"), ("suffix_8", "block_start4")]:
    d = paired(a, b)
    if len(d) > 5:
        print(f"  {a} - {b}: {fmt(*boot_ci(d), p=3)}  (n {len(d)})")
