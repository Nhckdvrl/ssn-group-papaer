"""E121 data: same-token contrasts with left context only.

POS:   UD English EWT, word forms that are a single OLMoE token (with leading space) and occur >= 10x as NOUN and as VERB.
Sense: SemCor (brown1 + brown2), noun word forms (single token) with >= 2 WordNet senses occurring >= 10x each.
Each item = left context (same document, previous text, last <= 128 tokens) ending with the target token; the router is read at
the last position. Split = calibration / held-out by sentence (hash).
Writes results/e121/items_pos.jsonl, items_sense.jsonl (small) and a summary.
"""
import collections
import glob
import hashlib
import json
import random
import re
import xml.etree.ElementTree as ET
from pathlib import Path

from transformers import AutoTokenizer

DATA = Path("/home/xiang/mechpop_cache/lingdata")
MODEL = "/home/xiang/mechpop_cache/hf_olmoe/main"
OUT = Path(__file__).resolve().parents[1] / "results" / "e121"
OUT.mkdir(parents=True, exist_ok=True)
MAXCTX, MIN_PER, MAX_PER = 128, 10, 25
tok = AutoTokenizer.from_pretrained(MODEL)


def split_of(key):
    return "cal" if int(hashlib.md5(key.encode()).hexdigest(), 16) % 2 == 0 else "held"


def make_item(prefix_text, word, meta, next_text):
    # only the tail of the prefix matters (<= MAXCTX tokens); cut characters first for speed
    prefix_text = prefix_text[-(MAXCTX * 12):]
    ids = tok.encode(prefix_text, add_special_tokens=False)
    tid = tok.encode(" " + word, add_special_tokens=False)
    if len(tid) != 1 or not ids or ids[-1] != tid[0] or not next_text:
        return None
    full = tok.encode(prefix_text + next_text, add_special_tokens=False)
    if full[: len(ids)] != ids or len(full) <= len(ids):
        return None
    next_id = full[len(ids)]
    ids = ids[-MAXCTX:]
    return {**meta, "ids": ids, "token_id": tid[0], "word": word, "next_id": next_id}


# ------------------------------------------------------------------ POS from UD EWT
def ewt_docs():
    docs, cur, sent = [], [], None
    for f in sorted(glob.glob(str(DATA / "en_ewt-ud-*.conllu"))):
        for line in open(f):
            line = line.rstrip("\n")
            if line.startswith("# newdoc"):
                if cur:
                    docs.append(cur)
                cur = []
            elif line.startswith("# sent_id"):
                sent = {"id": line.split("=", 1)[1].strip(), "toks": []}
            elif line.startswith("#"):
                continue
            elif not line:
                if sent and sent["toks"]:
                    cur.append(sent)
                sent = None
            else:
                c = line.split("\t")
                if "-" in c[0] or "." in c[0]:
                    continue
                sent["toks"].append((c[1], c[3], "SpaceAfter=No" not in c[9]))
    if cur:
        docs.append(cur)
    return docs


def pos_items():
    docs = ewt_docs()
    occ = collections.defaultdict(list)
    for doc in docs:
        text_so_far = ""
        for s in doc:
            pre = text_so_far
            for ti, (form, pos, sp) in enumerate(s["toks"]):
                w = form.lower()
                if pos in ("NOUN", "VERB") and form == w and pre and ti + 1 < len(s["toks"]):
                    nxt = (" " if sp else "") + s["toks"][ti + 1][0]
                    occ[(w, pos)].append((pre.rstrip(" ") + " " + form, s["id"], ti, nxt))
                pre = pre + form + (" " if sp else "")
            text_so_far = pre.rstrip(" ") + " "
    words = sorted({w for (w, p) in occ})
    rng = random.Random(0)
    items = []
    for w in words:
        if len(occ[(w, "NOUN")]) < MIN_PER or len(occ[(w, "VERB")]) < MIN_PER:
            continue
        if len(tok.encode(" " + w, add_special_tokens=False)) != 1:
            continue
        for pos in ("NOUN", "VERB"):
            cand = occ[(w, pos)][:]
            rng.shuffle(cand)
            got = 0
            for txt, sid, ti, nxt in cand:
                it = make_item(txt, w, {"label": pos, "sent": sid, "split": split_of(sid)}, nxt)
                if it:
                    items.append(it)
                    got += 1
                if got >= MAX_PER:
                    break
    return items


# ------------------------------------------------------------------ senses from SemCor
NOSPACE_BEFORE = {",", ".", ";", ":", "!", "?", "''", ")", "'s", "n't", "%"}


def semcor_items():
    occ = collections.defaultdict(list)
    for f in sorted(glob.glob(str(DATA / "semcor" / "brown*" / "tagfiles" / "*.xml"))):
        try:
            root = ET.parse(f).getroot()
        except ET.ParseError:
            txt = open(f, encoding="latin-1").read()
            txt = re.sub(r"&(?![a-z]+;)", "&amp;", txt)
            root = ET.fromstring(txt)
        text = ""
        for s in root.iter("s"):
            sid = f"{Path(f).stem}.{s.get('snum')}"
            els = [el for el in s if (el.text or "").strip()]
            for ti, el in enumerate(els):
                form = (el.text or "").replace("_", " ")
                if el.tag == "wf" and el.get("pos") == "NN" and el.get("wnsn") and el.get("wnsn").isdigit() and form == form.lower() and " " not in form and text and ti + 1 < len(els):
                    nf = els[ti + 1].text.replace("_", " ")
                    nxt = ("" if nf in NOSPACE_BEFORE else " ") + nf
                    occ[(form, el.get("lemma"))].append((text.rstrip(" ") + " " + form, sid, int(el.get("wnsn")), nxt))
                sep = "" if form in NOSPACE_BEFORE else " "
                text = text.rstrip(" ") + sep + form + " " if text else form + " "
            text = text.rstrip(" ") + " "
    rng = random.Random(0)
    items = []
    for (form, lemma), lst in sorted(occ.items()):
        if len(tok.encode(" " + form, add_special_tokens=False)) != 1:
            continue
        by = collections.defaultdict(list)
        for txt, sid, sn, nxt in lst:
            by[sn].append((txt, sid, nxt))
        senses = [sn for sn, v in by.items() if len(v) >= MIN_PER]
        if len(senses) < 2:
            continue
        for sn in senses:
            cand = by[sn][:]
            rng.shuffle(cand)
            got = 0
            for txt, sid, nxt in cand:
                it = make_item(txt, form, {"label": f"sense{sn}", "sent": sid, "split": split_of(sid), "lemma": lemma}, nxt)
                if it:
                    items.append(it)
                    got += 1
                if got >= MAX_PER:
                    break
    return items


def main():
    summ = {}
    for name, fn in (("pos", pos_items), ("sense", semcor_items)):
        items = fn()
        with open(OUT / f"items_{name}.jsonl", "w") as fh:
            for it in items:
                fh.write(json.dumps(it) + "\n")
        words = collections.Counter(it["word"] for it in items)
        labs = collections.Counter((it["word"], it["label"]) for it in items)
        summ[name] = {"n_items": len(items), "n_words": len(words), "splits": collections.Counter(it["split"] for it in items),
                      "words": sorted(words), "per_word_label_min": min(labs.values()) if labs else 0,
                      "mean_ctx_len": sum(len(it["ids"]) for it in items) / max(1, len(items))}
        print(name, json.dumps(summ[name])[:600], flush=True)
    (OUT / "data_summary.json").write_text(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
