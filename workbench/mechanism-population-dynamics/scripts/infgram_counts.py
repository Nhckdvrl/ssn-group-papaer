"""Corpus statistics for ParaConflict items via the public infini-gram API (no GPU).

For each (subject, answer, distractor) item and each corpus index: counts of the subject, the answer, the distractor,
and relation phrases "<rel phrase> <subject> is <answer|distractor>". Results are cached per query (resumable).
Usage: infgram_counts.py --category "World Capital"   -> results/corpus_counts/<category>.json
"""
import argparse
import hashlib
import json
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

import mp_common as mc

API = "https://api.infini-gram.io/"
INDEXES = {"pile": "v4_piletrain_llama", "dclm": "v4_dclm-baseline_llama", "dolma17": "v4_dolma-v1_7_llama",
           "c4": "v4_c4train_llama"}
PHRASE = {"World Capital": "The capital of {s} is {o}", "Official Language": "The official language of {s} is {o}",
          "Company Headquarter": "{s} is headquartered in {o}", "Book Author": "{s} was written by {o}",
          "Athelete Sport": "{s} plays {o}", "Company Founder": "{s} was founded by {o}"}
OUT = mc.RESULTS / "corpus_counts"
CACHE = OUT / ".cache"


def count(index, q):
    f = CACHE / f"{index}__{hashlib.sha1(q.encode()).hexdigest()[:16]}.json"
    if f.exists():
        d = json.loads(f.read_text())
        if d.get("query") == q:
            return d["count"]
    body = json.dumps({"index": index, "query_type": "count", "query": q}).encode()
    for t in range(8):
        try:
            req = urllib.request.Request(API, data=body, headers={"Content-Type": "application/json"})
            r = json.loads(urllib.request.urlopen(req, timeout=60).read())
            if "count" in r:
                f.write_text(json.dumps({"query": q, "count": r["count"], "approx": r.get("approx")}))
                return r["count"]
        except Exception:
            pass
        time.sleep(2 * (t + 1))
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--category", default="World Capital")
    a = ap.parse_args()
    import e18_trait as e18
    R = [r for r in e18.rows() if r["cat"] == a.category]
    items = sorted({(r["subj"], r["ans"], r["dist"]) for r in R})
    CACHE.mkdir(parents=True, exist_ok=True)
    jobs = []
    for s, o, d in items:
        for q in (s, o, d, PHRASE[a.category].format(s=s, o=o), PHRASE[a.category].format(s=s, o=d)):
            for name, idx in INDEXES.items():
                jobs.append((name, idx, q))
    jobs = sorted(set(jobs))
    with ThreadPoolExecutor(4) as ex:  # polite concurrency
        res = dict(zip(jobs, ex.map(lambda j: count(j[1], j[2]), jobs)))
    out = []
    for s, o, d in items:
        row = {"subj": s, "ans": o, "dist": d}
        for name, idx in INDEXES.items():
            row[name] = {"subj": res[(name, idx, s)], "ans": res[(name, idx, o)], "dist": res[(name, idx, d)],
                         "phrase_ans": res[(name, idx, PHRASE[a.category].format(s=s, o=o))],
                         "phrase_dist": res[(name, idx, PHRASE[a.category].format(s=s, o=d))]}
        out.append(row)
    (OUT / f"{a.category.replace(' ', '_')}.json").write_text(json.dumps(out, indent=1))
    print(a.category, len(out), "items;", sum(v is None for v in res.values()), "failed queries")


if __name__ == "__main__":
    main()
