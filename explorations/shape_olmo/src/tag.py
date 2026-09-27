"""Token features aligned to scored target positions (ids[:, 1:]), following 2606.20936 App. A.

data/tags_<domain>.npz, each (S, L-1):
  pos1, pos2  int8   coarse Brown family index into FAMILIES (-1 = none); a token overlapping two
                     words gets both (multi-tag attribution). Prose domains only.
  open, close bool   bracket char in the token's span: prose uses the Brown '(' / ')' tags;
                     structured domains use characters ([{ vs )]} (our choice; the paper's
                     structured bracket definition is not spelled out).
  htag        int8   HTML: 1 open tag, 2 close tag; LaTeX: 1 \\begin, 2 \\end (token overlaps it)
  rep         int8   largest n <= 16 such that the target completes an n-gram seen earlier in the window
Usage: tag.py DOMAINS   (run with verl-clean python; needs data/nltk_data/corpora/brown)
"""
import json, os, pickle, re, sys
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROSE = {"pg19", "ccnews", "wikipedia", "arxiv"}
TABLE1 = {
    "Noun": "NN NN$ NNS NNS$ NP NP$ NPS NPS$ NR NR$ NRS", "Verb": "VB VBD VBG VBN VBZ",
    "Adjective": "JJ JJ$ JJR JJS JJT", "Adverb": "RB RB$ RBR RBT RN", "Interjection": "UH",
    "Qualifier": "QL QLP", "Pronoun": "PP$ PP$$ PPL PPLS PPO PPS PPSS PN PN$",
    "Det/Article": "AT DT DT$ DTI DTS DTX ABL ABN ABX AP AP$", "Preposition": "IN",
    "Conjunction": "CC CS", "Aux BE": "BE BED BEDZ BEG BEM BEN BER BEZ", "Aux HAVE": "HV HVD HVG HVN HVZ",
    "Aux DO": "DO DOD DOZ", "Modal": "MD", "TO": "TO", "Existential": "EX",
    "Wh-word": "WDT WP$ WPO WPS WQL WRB", "Numeral": "CD CD$ OD", "Particle": "RP",
    "Punctuation": ", . : ' '' `` -- *", "Open Bracket": "(", "Close Bracket": ")",
}
FAMILIES = list(TABLE1) + ["Other"]
BROWN2FAM = {t: f for f, ts in TABLE1.items() for t in ts.split()}
CONTENT = {"Noun", "Verb", "Adjective", "Adverb", "Interjection", "Qualifier"}
FUNCTION = {"Existential", "Pronoun", "Det/Article", "Preposition", "Conjunction", "Aux BE",
            "Aux HAVE", "Aux DO", "Modal", "TO", "Wh-word"}
WORD = re.compile(r"\w+(?:['’]\w+)*|[^\w\s]")


def norm(tag):
    if tag in ("--", "'", "''", "``", "(", ")", "*", ",", ".", ":"):
        return tag
    tag = tag.split("+")[0]
    tag = tag.split("-")[0] if not tag.startswith("-") else tag
    return tag.rstrip("*") or tag


def tagger():
    f = f"{ROOT}/data/brown_tagger.pkl"
    if os.path.exists(f):
        return pickle.load(open(f, "rb"))
    import nltk
    nltk.data.path.insert(0, f"{ROOT}/data/nltk_data")
    from nltk.corpus import brown
    sents = [[(w, norm(t)) for w, t in s] for s in brown.tagged_sents()]
    t0 = nltk.RegexpTagger([(r"^-?\d+([.,]\d+)*$", "CD"), (r".*", "NN")])
    t1 = nltk.UnigramTagger(sents, backoff=t0)
    t2 = nltk.BigramTagger(sents, backoff=t1)
    t3 = nltk.TrigramTagger(sents, backoff=t2)
    pickle.dump(t3, open(f, "wb"))
    return t3


def fam_index(tag):
    return FAMILIES.index(BROWN2FAM.get(norm(tag), "Other"))


def char_labels(dom, text, tg):
    """Per-character labels for one doc: word-family index (-1), bracket (+1 open, -1 close), htag."""
    n = len(text)
    fam = np.full(n, -1, np.int8); wid = np.full(n, -1, np.int32)
    br = np.zeros(n, np.int8); ht = np.zeros(n, np.int8)
    if dom in PROSE:
        spans = [m.span() for m in WORD.finditer(text)]
        words = [text[a:b] for a, b in spans]
        tags = [t for _, t in tg.tag(words)] if words else []
        for k, ((a, b), t) in enumerate(zip(spans, tags)):
            fam[a:b] = fam_index(t); wid[a:b] = k
            if t == "(" or words[k] == "(":
                br[a:b] = 1
            elif t == ")" or words[k] == ")":
                br[a:b] = -1
    else:
        arr = np.frombuffer(text.encode("utf-32-le"), np.uint32)
        for c in "([{":
            br[arr == ord(c)] = 1
        for c in ")]}":
            br[arr == ord(c)] = -1
        if dom == "html":
            for m in re.finditer(r"</[A-Za-z][^>]*>", text):
                ht[m.start():m.end()] = 2
            for m in re.finditer(r"<[A-Za-z][^>]*>", text):
                ht[m.start():m.end()] = 1
        if dom == "latex":
            for m in re.finditer(r"\\begin\{[^}]*\}", text):
                ht[m.start():m.end()] = 1
            for m in re.finditer(r"\\end\{[^}]*\}", text):
                ht[m.start():m.end()] = 2
    return fam, wid, br, ht


def repeat_len(ids, nmax=16):
    """rep[t] = largest n such that ids[t-n+1:t+1] occurred ending at some earlier position."""
    L = len(ids)
    rep = np.zeros(L, np.int8)
    x = ids.astype(np.uint64) + np.uint64(1)
    P = np.uint64(1000003)
    t = np.arange(L)
    h = x.copy()                                   # h[t] = hash of the n-gram ending at t
    for n in range(1, nmax + 1):
        if n > 1:
            h = np.concatenate([np.zeros(1, np.uint64), h[:-1]]) * P + x
        hv = np.where(t >= n - 1, h, np.uint64(0) - t.astype(np.uint64) - np.uint64(1))  # invalid -> unique
        _, first, inv = np.unique(hv, return_index=True, return_inverse=True)
        seen = (first[inv] < t) & (t >= n - 1)
        if not seen.any():
            break
        rep[seen] = n
    return rep


def main(domains):
    tg = tagger()
    for dom in domains:
        pk = np.load(f"{ROOT}/data/pack_{dom}.npz")
        ids, doc, cs, ce = pk["ids"], pk["doc"], pk["cs"], pk["ce"]
        texts = [json.loads(l)["text"] for l in open(f"{ROOT}/data/docs_{dom}.jsonl")]
        labels = {}
        S, L = ids.shape
        pos1 = np.full((S, L), -1, np.int8); pos2 = np.full((S, L), -1, np.int8)
        op = np.zeros((S, L), bool); cl = np.zeros((S, L), bool); ht = np.zeros((S, L), np.int8)
        rep = np.zeros((S, L), np.int8)
        for s in range(S):
            rep[s] = repeat_len(ids[s])
            for i in range(L):
                d = doc[s, i]
                if d < 0 or ce[s, i] <= cs[s, i]:
                    continue
                if d not in labels:
                    labels = {d: char_labels(dom, texts[d], tg)}  # docs are contiguous: keep one
                fam, wid, br, hh = labels[d]
                a, b = cs[s, i], ce[s, i]
                w = wid[a:b]; f = fam[a:b]
                ks = [k for k in dict.fromkeys(w.tolist()) if k >= 0]
                if ks:
                    fs = [int(f[w == k][0]) for k in ks]
                    pos1[s, i] = fs[0]
                    if len(fs) > 1:
                        pos2[s, i] = fs[1]
                op[s, i] = (br[a:b] == 1).any(); cl[s, i] = (br[a:b] == -1).any()
                ht[s, i] = hh[a:b].max()
        sl = lambda x: x[:, 1:]  # align to targets
        np.savez(f"{ROOT}/data/tags_{dom}.npz", pos1=sl(pos1), pos2=sl(pos2), open=sl(op),
                 close=sl(cl), htag=sl(ht), rep=sl(rep))
        print(dom, "tagged", S, "open", op.sum(), "close", cl.sum(), "rep>=5", (rep >= 5).sum(), flush=True)


if __name__ == "__main__":
    main(sys.argv[1].split(","))
