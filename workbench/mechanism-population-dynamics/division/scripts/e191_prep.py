"""E191 prep (card: division/experiments/E191-flame-early-trajectory-decomposition.md); E189 prep adapted to FLAME-290M.
Rebuilds the FLORES dev + UD EWT sequences exactly as e191_hidden.py does (pythia-12b tokenizer) and derives per-row
factors for the 21,500-row toksub sample: previous / next id, corpus frequency, token class, position bin, language and
script, sentence cluster, English-view mask, UPOS group for UD rows (char-span alignment of the token's first non-space
character to the CoNLL-U word; no E186 store exists for this tokenizer).  H(e|id) tertiles are not computed (the E186
atlas is OLMoE-tokenised).  Positive controls: toksub_meta identical across the 10 checkpoints; rebuilt inp == toksub inp;
tokenizer.json identical to pythia-410m's (md5).  Writes /tmp/xiang_flame/e191/prep.npz + prep.json."""
import hashlib, json, os, sys, time
import numpy as np

BASE = os.environ.get("E191_BASE", "/tmp/xiang_flame")
OUT = f"{BASE}/e191"
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ud_passages import sentences  # noqa: E402
from e182_common import token_class  # noqa: E402
from e191_hidden import build_sequences, LANGS  # noqa: E402
from transformers import AutoTokenizer  # noqa: E402

ITERS = [540, 1080, 1620, 2160, 2700, 3240, 3780, 4320, 4860, 5473]
KEYS = [f"flame290m_i{i}" for i in ITERS]
t0 = time.time(); rep = {}
M = [dict(np.load(f"{BASE}/hidden/{k}/toksub_meta.npz")) for k in KEYS]
rep["pc_meta_identical"] = all(all(np.array_equal(M[0][f], m[f]) for f in ("src", "sid", "pos", "inp")) for m in M)
assert rep["pc_meta_identical"]
src, sid, pos, inp = (M[0][f].astype(np.int64) for f in ("src", "sid", "pos", "inp"))
N = src.size
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()
rep["pc_tokenizer_md5_equal_pythia410m"] = md5(f"{BASE}/tok/pythia12b/tokenizer.json") == md5(f"{BASE}/tok/p410/tokenizer.json")
tok = AutoTokenizer.from_pretrained(f"{BASE}/tok/pythia12b")
SEQ_L, SRC, SID = build_sequences(tok, f"{BASE}/data")
SEQS = {(int(a), int(b)): s for s, a, b in zip(SEQ_L, SRC, SID)}
UDI = len(LANGS)
reb = np.array([SEQS[(int(a), int(b))][int(p)] for a, b, p in zip(src, sid, pos)])
rep["pc_rebuild_inp_equal"] = float((reb == inp).mean()); assert rep["pc_rebuild_inp_equal"] == 1.0
prev = np.array([SEQS[(int(a), int(b))][int(p) - 1] if p > 0 else -1 for a, b, p in zip(src, sid, pos)])
nxt = np.array([SEQS[(int(a), int(b))][int(p) + 1] if p + 1 < len(SEQS[(int(a), int(b))]) else -1 for a, b, p in zip(src, sid, pos)])
cnt = np.zeros(len(tok) + 64, np.int64)
for s in SEQ_L:
    np.add.at(cnt, np.array(s), 1)
freq = cnt[inp]; qs = np.quantile(freq, [.2, .4, .6, .8]); fq = np.digitize(freq, qs)
CLS = {"let": 0, "non": 1, "frag": 2, "apos": 1, "empty": 1}
cls = np.array([CLS[token_class(tok.decode([int(i)]))] for i in inp])
posb = np.digitize(pos, [1, 4, 16, 64])
script = np.array([(LANGS[a].split("_")[1] if a < UDI else "Latn") for a in src])
clus = np.unique(src * 100000 + sid, return_inverse=True)[1]
eng = (src == 0) | (src == UDI)


def ctx(a, b, p, w=8):
    s = SEQS[(a, b)]
    return (tok.decode(s[max(0, p - w):p]) + "⟦" + tok.decode([s[p]]) + "⟧" + tok.decode(s[p + 1:p + 4])).replace("\n", " ")


contexts = [ctx(int(a), int(b), int(p)) for a, b, p in zip(src, sid, pos)]
strs = {int(i): tok.decode([int(i)]) for i in np.unique(np.r_[inp, prev[prev >= 0]])}

# ---- UPOS for UD rows: rebuild passages with per-word char spans (same construction as e191_hidden.build_sequences)
MAX_WORDS, ud = 400, []
for name in ("dev", "test"):
    cur = None
    for newdoc, text, toks in sentences(f"{BASE}/data/lingdata/en_ewt-ud-{name}.conllu"):
        if cur is None or newdoc or cur["n"] + len(toks) > MAX_WORDS:
            if cur and cur["text"]:
                ud.append(cur)
            cur = {"text": "", "n": 0, "w": []}
        base = len(cur["text"]) + (1 if cur["text"] else 0)
        p = 0
        for form, upos, _sp, kind in toks:
            j = text.find(form, p)
            if j < 0:
                continue
            if kind != "mwt":
                cur["w"].append((base + j, base + j + len(form), upos))
            if kind != "part":
                p = j + len(form)
        cur["text"] = (cur["text"] + " " + text) if cur["text"] else text
        cur["n"] += len(toks)
    if cur and cur["text"]:
        ud.append(cur)
FUNC = {"ADP", "AUX", "CCONJ", "DET", "PART", "PRON", "SCONJ"}; CONT = {"NOUN", "VERB", "ADJ", "ADV", "PROPN", "NUM", "INTJ"}; PUN = {"PUNCT", "SYM"}
upg = np.full(N, -1, np.int64); n_ud_ok = 0
for j, P_ in enumerate(ud):
    enc = tok(P_["text"], add_special_tokens=False, return_offsets_mapping=True)
    assert enc["input_ids"] == SEQS[(UDI, j)], "UD passage rebuild mismatch"
    rows = np.where((src == UDI) & (sid == j))[0]
    for r in rows:
        a, b = enc["offset_mapping"][int(pos[r])]
        while a < b and P_["text"][a].isspace():
            a += 1
        for (ws, we, up) in P_["w"]:
            if ws <= a < we:
                upg[r] = 0 if up in FUNC else 1 if up in CONT else 2 if up in PUN else -1
                n_ud_ok += 1
                break
rep["ud_rows"] = int((src == UDI).sum()); rep["ud_rows_with_upos_group"] = int((upg >= 0).sum()); rep["ud_rows_word_found"] = n_ud_ok
rep["freq_quintile_cuts"] = qs.tolist(); rep["n_eng_view"] = int(eng.sum()); rep["N"] = int(N)
np.savez(f"{OUT}/prep.npz", src=src, sid=sid, pos=pos, inp=inp, prev=prev, nxt=nxt, freq=freq, fq=fq, cls=cls, posb=posb,
         clus=clus, upg=upg, script=script, eng=eng)
json.dump({"report": rep, "langs": LANGS + ["UD_eng"], "contexts": contexts, "strs": strs}, open(f"{OUT}/prep.json", "w"), ensure_ascii=False)
print(json.dumps(rep, indent=1), round(time.time() - t0), flush=True)
