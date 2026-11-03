#!/usr/bin/env python3
"""E170: linguistic annotations for every word in results/e167/passages.json, aligned by index.

Re-walks the UD English EWT files exactly as ud_passages.py did and records, per word:
  deprel, head_upos (ROOT for root), feats (string), sent_len, sent_pos (0-based index in sentence),
  sent_init / sent_final flags, prev_upos / next_upos (within sentence; BOS/EOS at edges),
  genre (from the newdoc id prefix: answers / email / newsgroup / reviews / weblog), doc_id, source split.
Asserts form and UPOS agree with passages.json at every index, so the arrays can be used with
the routing captures (pairs.npz anchor_word indices) directly.

Usage: ud_annotate.py   -> results/e167/ud_annotations.json
"""
import json
from pathlib import Path

WB = Path(__file__).resolve().parents[1]
UD = Path.home() / "mechpop_cache/lingdata"
P = json.loads((WB / "results/e167/passages.json").read_text())
MAX_WORDS = 400


def sentences(path):
    doc, doc_id, text, toks, mwt_end = False, None, None, [], 0
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        if line.startswith("# newdoc"):
            doc = True
            doc_id = line.split("=", 1)[1].strip() if "=" in line else ""
        elif line.startswith("# text = "):
            text = line[len("# text = "):]
        elif not line:
            if toks:
                yield doc, doc_id, text, toks
            doc, text, toks, mwt_end = False, None, [], 0
        elif not line.startswith("#"):
            c = line.split("\t")
            if "." in c[0]:
                continue
            if "-" in c[0]:
                a, b = map(int, c[0].split("-"))
                mwt_end = b
                toks.append(dict(form=c[1], kind="mwt"))
                continue
            i = int(c[0])
            toks.append(dict(form=c[1], upos=c[3], feats=c[5], head=int(c[6]), deprel=c[7],
                             kind="part" if i <= mwt_end else "word", idx=i))


def main():
    ann = []
    cur_doc = None
    for split, files in (("anchor", [("test", None), ("train", 4000)]), ("cal", [("dev", None)])):
        for name, limit in files:
            n_sent = 0
            cur_n = None
            for newdoc, doc_id, text, toks in sentences(UD / f"en_ewt-ud-{name}.conllu"):
                if limit is not None and n_sent >= limit and newdoc:
                    break
                n_sent += 1
                if newdoc:
                    cur_doc = doc_id
                if cur_n is None or newdoc or cur_n + len(toks) > MAX_WORDS:
                    cur_n = 0
                words = [t for t in toks if t["kind"] == "word"]
                by_idx = {t["idx"]: t for t in words}
                pos = 0
                seq = [t for t in toks if t["kind"] != "part"]
                for k, t in enumerate(seq):
                    kk = text.find(t["form"], pos)
                    if kk < 0:
                        break
                    if t["kind"] == "word":
                        head = by_idx.get(t["head"])
                        wi = [w["idx"] for w in words].index(t["idx"])
                        prev_u = words[wi - 1]["upos"] if wi > 0 else "BOS"
                        next_u = words[wi + 1]["upos"] if wi + 1 < len(words) else "EOS"
                        genre = (cur_doc or "").split("-")[0] if cur_doc else ""
                        ann.append(dict(form=t["form"], upos=t["upos"], deprel=t["deprel"].split(":")[0], deprel_full=t["deprel"],
                                        head_upos=(head["upos"] if head else "ROOT"), feats=t["feats"], sent_len=len(words),
                                        sent_pos=wi, sent_init=int(wi == 0), sent_final=int(wi == len(words) - 1),
                                        prev_upos=prev_u, next_upos=next_u, genre=genre, doc_id=cur_doc or "", source=name, split=split))
                    pos = kk + len(t["form"])
                cur_n += len(toks)
    words = P["words"]
    assert len(ann) == len(words), (len(ann), len(words))
    bad = [(n, a["form"], w[3], a["upos"], w[4]) for n, (a, w) in enumerate(zip(ann, words)) if a["form"] != w[3] or a["upos"] != w[4]]
    assert not bad, bad[:5]
    (WB / "results/e167/ud_annotations.json").write_text(json.dumps(ann))
    from collections import Counter
    print(len(ann), "words aligned;", "genres:", Counter(a["genre"] for a in ann if a["split"] == "anchor"))
    print("deprel top:", Counter(a["deprel"] for a in ann).most_common(12))


if __name__ == "__main__":
    main()
