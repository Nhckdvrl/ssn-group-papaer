"""E189 prep (card: division/experiments/E189-training-axis-routing-decomposition.md).
Rebuilds the FLORES dev + UD EWT token sequences exactly as e186_hidden.py does, and derives per-row factors for the
22,000-row toksub sample: previous id, corpus frequency, token class, position bin, language/script, sentence cluster,
UPOS group (UD rows, mapped to the E186 main store), H(e|id) tertile (E186 atlas, T, mid band 2-11), context snippet.
Also maps toksub rows to E186 store rows (for the T_F vs store positive control).
Positive controls here: toksub_meta identical across the 9 checkpoints; rebuilt inp == toksub inp; UD inp == store inp.
Runs on fvcrc10 with the node-local env; writes /tmp/xiang_e186/e189/prep.npz + prep.json."""
import json, os, sys, time
import numpy as np

BASE = "/tmp/xiang_e186"
OUT = f"{BASE}/e189"
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, f"{BASE}/bundle/code")
from ud_passages import sentences  # noqa: E402
from e182_common import token_class  # noqa: E402
from transformers import AutoTokenizer  # noqa: E402

KEYS = ["olmoe0924_s5k", "olmoe0924_s20k", "olmoe0924_s80k", "olmoe0924_s140k", "olmoe0924_s200k",
        "olmoe0924_s260k", "olmoe0924_s320k", "olmoe0924_s1220k", "olmoe0924_main"]
t0 = time.time()
rep = {}
# ---- 1. toksub_meta identical across checkpoints
M = [dict(np.load(f"{BASE}/hidden/{k}/toksub_meta.npz")) for k in KEYS]
rep["pc_meta_identical"] = all(all(np.array_equal(M[0][f], m[f]) for f in ("src", "sid", "pos", "inp")) for m in M)
assert rep["pc_meta_identical"]
src, sid, pos, inp = (M[0][f].astype(np.int64) for f in ("src", "sid", "pos", "inp"))
N = src.size
meta = json.load(open(f"{BASE}/hidden/olmoe0924_main/meta.json"))
LANGS = meta["langs"]

# ---- 2. rebuild sequences (e186_hidden.py construction)
tok = AutoTokenizer.from_pretrained(f"{BASE}/tok/olmoe0924")
DR = f"{BASE}/bundle/data"
SEQS = {}
for li, lg in enumerate(LANGS):
    with open(f"{DR}/flores200_dataset/dev/{lg}.dev", encoding="utf-8") as f:
        for j, s in enumerate([x.rstrip("\n") for x in f][:997]):
            SEQS[(li, j)] = tok(s, add_special_tokens=False)["input_ids"]
MAX_WORDS, ud = 400, []
for name in ("dev", "test"):
    cur = None
    for newdoc, text, toks in sentences(f"{DR}/lingdata/en_ewt-ud-{name}.conllu"):
        if cur is None or newdoc or cur["n"] + len(toks) > MAX_WORDS:
            if cur and cur["text"]:
                ud.append(cur["text"])
            cur = {"text": "", "n": 0}
        cur["text"] = (cur["text"] + " " + text) if cur["text"] else text
        cur["n"] += len(toks)
    if cur and cur["text"]:
        ud.append(cur["text"])
for j, s in enumerate(ud):
    SEQS[(len(LANGS), j)] = tok(s, add_special_tokens=False)["input_ids"]
reb = np.array([SEQS[(int(a), int(b))][int(p)] for a, b, p in zip(src, sid, pos)])
rep["pc_rebuild_inp_equal"] = float((reb == inp).mean())
assert rep["pc_rebuild_inp_equal"] == 1.0
prev = np.array([SEQS[(int(a), int(b))][int(p) - 1] if p > 0 else -1 for a, b, p in zip(src, sid, pos)])
nxt = np.array([SEQS[(int(a), int(b))][int(p) + 1] if p + 1 < len(SEQS[(int(a), int(b))]) else -1
                for a, b, p in zip(src, sid, pos)])
cnt = np.zeros(max(len(tok), tok.vocab_size) + 10, np.int64)
for s in SEQS.values():
    np.add.at(cnt, np.array(s), 1)
freq = cnt[inp]
qs = np.quantile(freq, [.2, .4, .6, .8])
fq = np.digitize(freq, qs)                                  # 0 (rarest) .. 4
cls_name = [token_class(tok.decode([int(i)])) for i in inp]
CLS = {"let": 0, "non": 1, "frag": 2, "apos": 1, "empty": 1}  # letter / non-letter / UTF-8 fragment
cls = np.array([CLS[c] for c in cls_name])
posb = np.digitize(pos, [1, 4, 16, 64])                    # 0: pos 0, 1: 1-3, 2: 4-15, 3: 16-63, 4: >=64
script = np.array([(LANGS[a].split("_")[1] if a < len(LANGS) else "Latn") for a in src])
clus = np.unique(src * 100000 + sid, return_inverse=True)[1]


def ctx(a, b, p, w=8):
    s = SEQS[(a, b)]
    return (tok.decode(s[max(0, p - w):p]) + "⟦" + tok.decode([s[p]]) + "⟧" + tok.decode(s[p + 1:p + 1 + 3])).replace("\n", " ")


contexts = [ctx(int(a), int(b), int(p)) for a, b, p in zip(src, sid, pos)]
strs = {int(i): tok.decode([int(i)]) for i in np.unique(np.r_[inp, prev[prev >= 0]])}

# ---- 3. map to E186 main store (FLORES sides present in the store + UD) for UPOS and the T_F positive control
st = np.load(f"{BASE}/store/olmoe0924_main/tokmeta.npz")
smeta = json.load(open(f"{BASE}/store/olmoe0924_main/meta.json"))
sides = smeta["sides"]; UPOS = smeta["upos"]
s_corpus, s_side, s_sid, s_pos, s_inp, s_upos = (st[k].astype(np.int64) for k in ("corpus", "side", "sid", "pos", "inp", "upos"))
ud_code = int(np.unique(s_corpus[s_upos >= 0])[0])
key = lambda c, sd, si, p: ((c * 64 + sd) * 100000 + si) * 4096 + p
skey = key(s_corpus, np.where(s_corpus == ud_code, 0, s_side), s_sid, s_pos)
order = np.argsort(skey); sk = skey[order]
store_row = np.full(N, -1, np.int64)
for r in range(N):
    a = int(src[r])
    if a == len(LANGS):
        k = key(ud_code, 0, int(sid[r]), int(pos[r]))
    elif LANGS[a] in sides:
        k = key(1 - ud_code if ud_code in (0, 1) else 0, sides.index(LANGS[a]), int(sid[r]), int(pos[r]))
    else:
        continue
    j = np.searchsorted(sk, k)
    if j < sk.size and sk[j] == k:
        store_row[r] = order[j]
ok = store_row >= 0
match = np.zeros(N, bool); match[ok] = s_inp[store_row[ok]] == inp[ok]
rep["store_rows_found"] = int(ok.sum()); rep["store_rows_inp_match"] = float(match[ok].mean()) if ok.any() else None
rep["store_rows_found_ud"] = int((ok & (src == len(LANGS))).sum())
store_row[~match] = -1
FUNC = {"ADP", "AUX", "CCONJ", "DET", "PART", "PRON", "SCONJ"}
CONT = {"NOUN", "VERB", "ADJ", "ADV", "PROPN", "NUM", "INTJ"}
PUN = {"PUNCT", "SYM"}
upg = np.full(N, -1, np.int64)
for r in np.where((store_row >= 0) & (src == len(LANGS)))[0]:
    u = int(s_upos[store_row[r]])
    if u >= 0:
        nm = UPOS[u]
        upg[r] = 0 if nm in FUNC else 1 if nm in CONT else 2 if nm in PUN else -1
rep["ud_rows"] = int((src == len(LANGS)).sum()); rep["ud_rows_with_upos_group"] = int((upg >= 0).sum())

# ---- 4. H(e|id) tertiles (E186 atlas, main, T = router 0, mid band 2-11)
at = np.load(f"{BASE}/atlas/tok_d184_olmoe0924_main.npz")
Hid = at["Hx"][2:12, 0, :].mean(0); ids305 = at["ids"]
ter = np.digitize(Hid, np.quantile(Hid, [1 / 3, 2 / 3]))
hmap = dict(zip(ids305.tolist(), ter.tolist()))
hter = np.array([hmap.get(int(i), -1) for i in inp])
rep["Hid_n_ids"] = int(ids305.size); rep["Hid_token_coverage"] = float((hter >= 0).mean())
rep["Hid_tertile_cuts"] = np.quantile(Hid, [1 / 3, 2 / 3]).tolist()
rep["freq_quintile_cuts"] = qs.tolist()
rep["min_seq_len"] = int(min(len(s) for s in SEQS.values()))

np.savez(f"{OUT}/prep.npz", src=src, sid=sid, pos=pos, inp=inp, prev=prev, nxt=nxt, freq=freq, fq=fq, cls=cls, posb=posb,
         clus=clus, upg=upg, hter=hter, store_row=store_row, script=script)
json.dump({"report": rep, "langs": LANGS + ["UD_eng"], "contexts": contexts, "strs": strs}, open(f"{OUT}/prep.json", "w"),
          ensure_ascii=False)
print(json.dumps(rep, indent=1), round(time.time() - t0), flush=True)
