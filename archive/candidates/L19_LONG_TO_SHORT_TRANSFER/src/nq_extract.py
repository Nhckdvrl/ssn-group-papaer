"""Extract matched SHORT-SUPPORT / LONG-FULL pairs from Natural Questions (original, HTML-token form).

Contract (frozen before any training run):
  * one NQ training example -> at most one pair
  * SHORT-SUPPORT context = the human-annotated long-answer paragraph, verbatim
  * LONG-FULL     context = the whole Wikipedia page the paragraph came from, verbatim
  * both conditions share question, gold short answer, example id, and source document
"""
import re

def clean(tokens, is_html, lo=None, hi=None):
    lo = 0 if lo is None else lo
    hi = len(tokens) if hi is None else hi
    return " ".join(t for t, h in zip(tokens[lo:hi], is_html[lo:hi]) if not h)

def extract(row):
    ann = row["annotations"]
    if len(ann["long_answer"]) == 0:
        return None
    la = ann["long_answer"][0]
    if la["start_token"] < 0:
        return None                                   # null long answer
    if ann["yes_no_answer"][0] != -1:
        return None                                   # yes/no, no extractive span
    sa = ann["short_answers"][0]["text"]
    if len(sa) != 1:
        return None                                   # no / multi-span short answer
    answer = sa[0].strip()
    if not answer:
        return None
    tok = row["document"]["tokens"]["token"]
    ish = row["document"]["tokens"]["is_html"]
    if tok[la["start_token"]].lower() != "<p>":
        return None                                   # keep prose paragraphs only
    para = clean(tok, ish, la["start_token"], la["end_token"])
    page = clean(tok, ish)
    if answer.lower() not in para.lower():
        return None                                   # answer must live in the support
    return dict(
        id=row["id"],
        title=row["document"]["title"],
        url=row["document"]["url"],
        question=row["question"]["text"].strip(),
        answer=answer,
        support=para,
        page=page,
        la_start_token=la["start_token"],
        la_end_token=la["end_token"],
        n_doc_tokens=len(tok),
    )
