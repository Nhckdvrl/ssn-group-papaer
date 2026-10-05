"""Build candidate nonce-word banks (pronounceable, not dictionary words).

Output: data/lexicon_candidates.json  -> screened later by step-5 (screen_lexicon.py)
"""
import itertools, json, random, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
C = list("bdfgklmnprstvz"); V = list("aeiou")
ONSET2 = ["bl", "br", "dr", "fl", "fr", "gl", "gr", "kl", "kr", "pl", "pr", "sl", "sn", "sp", "st", "tr", "sk"]


def dict_words():
    ws = set()
    for f in ["/usr/share/dict/words", "/usr/share/dict/american-english"]:
        try:
            ws |= {w.strip().lower() for w in open(f, errors="ignore")}
        except FileNotFoundError:
            pass
    return ws


def main(seed=0):
    rng = random.Random(seed)
    dw = dict_words()
    attr = set(); lab = set()
    while len(attr) < 600:
        w = rng.choice(C) + rng.choice(V) + rng.choice(C) + rng.choice(V)   # CVCV e.g. mepo
        if w not in dw and not any(w in d for d in ()):
            attr.add(w)
    while len(lab) < 600:
        shape = rng.choice(["CCVCVC", "CVCVC", "CCVC"])
        w = ""
        for ch in shape:
            w += rng.choice(V) if ch == "V" else rng.choice(C)
        if shape.startswith("CC"):
            w = rng.choice(ONSET2) + w[2:]
        if w not in dw and len(set(w)) >= 3:
            lab.add(w)
    out = {"attribute_names": sorted(attr), "labels": sorted(lab)}
    p = ROOT / "data" / "lexicon_candidates.json"
    p.write_text(json.dumps(out, indent=1))
    print(len(attr), len(lab), p)


if __name__ == "__main__":
    main()
