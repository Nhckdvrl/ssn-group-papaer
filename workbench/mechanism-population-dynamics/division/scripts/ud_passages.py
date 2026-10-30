"""E167 analysis text (reused from the unrun E143 card): UD English EWT documents -> passages (<= 400 words) with word character spans.

Anchors = test + the first 4000 train sentences (whole documents); calibration = dev.
Multi-word token ranges (e.g. "don't") are skipped as words but their surface text is kept in the passage.
Output: results/e167/passages.json  {passages: [{id, split, text}], words: [[pid, start, end, form, upos], ...]}
"""
import json

import numpy as np
from pathlib import Path

WB = Path(__file__).resolve().parents[1]
UD = Path.home() / "mechpop_cache/lingdata"
OUT = WB / "results/e167"
MAX_WORDS = 400
MIN_OCC, CAP, N_CAL = 6, 40, 8192


def sentences(path):
    """Yield (newdoc, text, [(form, upos, space_after, is_mwt_part)]) per sentence."""
    doc, text, toks, mwt_end = False, None, [], 0
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        if line.startswith("# newdoc"):
            doc = True
        elif line.startswith("# text = "):
            text = line[len("# text = "):]
        elif not line:
            if toks:
                yield doc, text, toks
            doc, text, toks, mwt_end = False, None, [], 0
        elif not line.startswith("#"):
            c = line.split("\t")
            if "." in c[0]:
                continue
            if "-" in c[0]:
                a, b = map(int, c[0].split("-"))
                mwt_end = b
                toks.append((c[1], None, "SpaceAfter=No" not in c[9], "mwt"))
                continue
            i = int(c[0])
            toks.append((c[1], c[3], True, "part" if i <= mwt_end else "word"))


def build():
    passages, words = [], []
    for split, files in (("anchor", [("test", None), ("train", 4000)]), ("cal", [("dev", None)])):
        for name, limit in files:
            cur, n_sent = None, 0
            for newdoc, text, toks in sentences(UD / f"en_ewt-ud-{name}.conllu"):
                if limit is not None and n_sent >= limit and newdoc:
                    break
                n_sent += 1
                if cur is None or newdoc or cur["n"] + len(toks) > MAX_WORDS:
                    if cur and cur["text"]:
                        passages.append(cur)
                    cur = {"id": len(passages), "split": split, "source": name, "text": "", "n": 0, "w": []}
                # locate each surface token in the sentence text, sequentially
                base = len(cur["text"]) + (1 if cur["text"] else 0)
                pos = 0
                for form, upos, _, kind in toks:
                    if kind == "part":
                        continue
                    k = text.find(form, pos)
                    if k < 0:
                        break
                    if kind == "word":
                        cur["w"].append((base + k, base + k + len(form), form, upos))
                    pos = k + len(form)
                cur["text"] = (cur["text"] + " " + text) if cur["text"] else text
                cur["n"] += len(toks)
            if cur and cur["text"]:
                passages.append(cur)
    for pid, p in enumerate(passages):
        p["id"] = pid
        for s, e, form, upos in p.pop("w"):
            assert p["text"][s:e] == form
            words.append([pid, s, e, form, upos, p["split"]])
        p.pop("n")
    # analysis set: anchor word types (lower-cased) with >= MIN_OCC occurrences, at most CAP per type (fixed seed);
    # calibration sample: N_CAL random cal words.  Chosen from text alone, before any model is run.
    rng = np.random.default_rng(0)
    by = {}
    for n, w in enumerate(words):
        if w[5] == "anchor":
            by.setdefault(w[3].lower(), []).append(n)
    sel = []
    for t in sorted(by):
        if len(by[t]) >= MIN_OCC:
            idx = by[t] if len(by[t]) <= CAP else sorted(rng.choice(by[t], CAP, replace=False).tolist())
            sel += idx
    cal = [n for n, w in enumerate(words) if w[5] == "cal"]
    cal = sorted(np.random.default_rng(1).choice(cal, min(N_CAL, len(cal)), replace=False).tolist())
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "passages.json").write_text(json.dumps({"passages": passages, "words": words, "sel": sel, "cal": cal}))
    print(len(sel), "selected anchor words in", sum(len(v) >= MIN_OCC for v in by.values()), "types;", len(cal), "cal words")
    na = sum(w[5] == "anchor" for w in words)
    print(len(passages), "passages;", na, "anchor words;", len(words) - na, "cal words")


if __name__ == "__main__":
    build()
