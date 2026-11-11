"""E187 读数 4 (toksub part): O / H / R / R' by token class on the 20-language toksub, from the per-token agreement
vectors written by e187_decomp.py (~/mechpop_cache/e187/agree_<l>_<m>.npz).  Classes: language, script, position
bin, letter / non-letter (first non-space char), frequency quintile (token counts over FLORES dev in the 20 languages).
Writes results/e187/toksub_classes.json."""
import json, os, unicodedata
import numpy as np
os.environ.setdefault("HF_HUB_OFFLINE", "1")
from transformers import AutoTokenizer

C = os.path.expanduser("~/mechpop_cache/e187")
RES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results", "e187")
FLORES = "/home/xiang/mechpop_cache/flores200/flores200_dataset"
meta = json.load(open("/home/xiang/mechpop_cache/e179/qwen3/meta.json"))
ids = np.load("/home/xiang/mechpop_cache/atlas_e185/toksub_ids_qwen3.npz")
tok = AutoTokenizer.from_pretrained(meta["model"])
cnt = {}
for lg in meta["langs"]:
    for s in open(f"{FLORES}/dev/{lg}.dev", encoding="utf-8"):
        for t in tok(s.rstrip("\n"), add_special_tokens=False)["input_ids"]:
            cnt[t] = cnt.get(t, 0) + 1
cur = ids["cur"]
freq = np.array([cnt[int(t)] for t in cur])
fq = np.searchsorted(np.quantile(freq, [.2, .4, .6, .8]), freq, side="right")


def is_letter(s):
    s = s.strip()
    return bool(s) and unicodedata.category(s[0]).startswith("L")


letter = np.array([is_letter(tok.decode([int(t)])) for t in cur]).astype(int)
posbin = np.digitize(ids["pos"], [1, 5, 20])
lang = ids["lang"]
scripts = sorted({l.split("_")[1] for l in meta["langs"]})
script = np.array([scripts.index(meta["langs"][i].split("_")[1]) for i in lang])
CL = {"lang": (lang, meta["langs"]), "script": (script, scripts), "pos": (posbin, ["0", "1-4", "5-19", ">=20"]),
      "letter": (letter, ["non-letter", "letter"]), "freq": (fq, ["q1(rare)", "q2", "q3", "q4", "q5(freq)"])}
out = []
for lag, rl in ((12, range(6, 30)), (24, range(6, 18))):
    for l in rl:
        z = np.load(f"{C}/agree_{l}_{l + lag}.npz")
        rec = dict(l=l, m=l + lag, lag=lag)
        for k in ("O", "H", "R", "Rp"):
            for u in ("t1", "ov"):
                v = z[f"{k}_{u}"]
                for cn, (lab, names) in CL.items():
                    rec[f"{k}_{u}_{cn}"] = {names[c]: float(v[lab == c].mean()) for c in np.unique(lab)}
        out.append(rec)
json.dump({"n_by_class": {cn: {names[c]: int((lab == c).sum()) for c in np.unique(lab)} for cn, (lab, names) in CL.items()},
           "pairs": out}, open(f"{RES}/toksub_classes.json", "w"), indent=0)
print("done")
