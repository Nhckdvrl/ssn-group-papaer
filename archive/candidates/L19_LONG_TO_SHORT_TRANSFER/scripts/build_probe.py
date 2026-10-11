"""Context-reliance probe (secondary outcome, evaluation only).

Held-out NQ pairs, disjoint from every training pair. In each, the gold answer inside
the support paragraph is replaced by a counterfactual of the same surface type drawn
from another example. The model is then asked the question with the edited paragraph.

  answers the counterfactual -> followed the context
  answers the original gold  -> fell back on parametric memory

Both outcomes are unambiguous strings, so no judge is needed.
"""
import sys, os, glob, json, re, random, hashlib
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from nq_extract import extract
import pyarrow.parquet as pq

SHARDS_FROM = 160          # disjoint from the training build, which scans 0..159
N_TARGET    = 600
OUT         = "data/probe.jsonl"
DATE = re.compile(r"^(january|february|march|april|may|june|july|august|september|"
                  r"october|november|december)\s+\d{1,2},?\s+\d{4}$", re.I)
YEAR = re.compile(r"^\d{4}$")
NUM  = re.compile(r"^[\d,.]+$")


def atype(a):
    if DATE.match(a.strip()): return "date"
    if YEAR.match(a.strip()): return "year"
    if NUM.match(a.strip()):  return "number"
    return "string"


def main():
    files = sorted(glob.glob(os.path.expanduser(
        "~/.cache/huggingface/hub/datasets--google-research-datasets--natural_questions"
        "/snapshots/*/default/train-*.parquet")))[SHARDS_FROM:]
    if not files:
        print(f"no shards at index >= {SHARDS_FROM}; fetch them first"); return
    cands = []
    for f in files:
        for b in pq.ParquetFile(f).iter_batches(batch_size=64):
            for r in b.to_pylist():
                e = extract(r)
                if e is None: continue
                w = len(e["support"].split())
                if not (30 <= w <= 250): continue
                e["atype"] = atype(e["answer"])
                cands.append(e)
        if len(cands) >= N_TARGET * 4: break
    rng = random.Random(0)
    bytype = {}
    for e in cands: bytype.setdefault(e["atype"], []).append(e)
    out, used = [], set()
    for e in cands:
        pool = [x for x in bytype[e["atype"]]
                if x["answer"].lower() != e["answer"].lower()]
        if not pool: continue
        cf = rng.choice(pool)["answer"]
        # case-insensitive replacement of every occurrence of the gold answer
        edited = re.sub(re.escape(e["answer"]), cf, e["support"], flags=re.I)
        if cf.lower() not in edited.lower() or e["answer"].lower() in edited.lower():
            continue
        if e["id"] in used: continue
        used.add(e["id"])
        out.append(dict(id=e["id"], question=e["question"], gold_parametric=e["answer"],
                        counterfactual=cf, atype=e["atype"], context=edited))
        if len(out) >= N_TARGET: break
    with open(OUT, "w") as w:
        for o in out: w.write(json.dumps(o) + "\n")
    print(json.dumps(dict(n=len(out), shards_from=SHARDS_FROM,
                          by_type={k: sum(1 for o in out if o["atype"] == k)
                                   for k in {o["atype"] for o in out}},
                          sha256=hashlib.sha256(open(OUT, "rb").read()).hexdigest()),
                     indent=1))


if __name__ == "__main__":
    main()
