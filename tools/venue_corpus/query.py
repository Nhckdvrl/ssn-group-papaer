#!/usr/bin/env python3
"""Venue calibration queries over data/corpus.jsonl (built by fetch.sh + build.py).

Why this exists: topic decisions in this repo used to be made by an LLM agent asking
"has anyone touched this?" against the whole arXiv. That question almost always returns
yes, and it is not what top venues judge. These queries ground decisions in what top venues
actually accepted and rejected.

Subcommands
  density  PATTERN [PATTERN ...] [--not PATTERN ...]
      Accepted papers per venue whose title+abstract match ALL patterns (regex, case-insensitive),
      plus the ICLR acceptance rate for the slice (ICLR lists include rejected/withdrawn papers).
      Compare the slice rate with the venue base rate printed on the first line.
  nearest  "free-text description of the idea" [-k 15] [--venue ICLR2026 ...]
      BM25 nearest neighbours, split into accepted vs rejected. Use it to write the positioning
      table (what exactly is our delta vs each neighbour?) - not to kill ideas.
  shapes   PATTERN [PATTERN ...]
      Accepted-vs-rejected comparison of abstract "paper shape" cues (method / finding / theory /
      benchmark / failure-mode language) and review scores, for ICLR venues.
  show     "title substring" [-n 3]
      Print matching records with abstracts.

Examples
  python3 query.py density "multi[- ]agent" "\\b(LLMs?|language models?)\\b"
  python3 query.py nearest "cross-play evaluation of RL co-trained LLM agent teams with unseen partners"
  python3 query.py shapes "sparse auto[- ]?encoders?|\\bSAEs?\\b"
"""
import argparse, json, math, os, re, signal, statistics, sys

signal.signal(signal.SIGPIPE, signal.SIG_DFL)  # allow piping into head
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
CORPUS = os.path.join(HERE, "data", "corpus.jsonl")
STOP = set("a an the of for to in on and or with by from is are be we our this that these those via as at into using use based".split())


def load():
    if not os.path.exists(CORPUS):
        sys.exit("corpus missing: run ./fetch.sh && python3 build.py first")
    return [json.loads(l) for l in open(CORPUS)]


def text(p):
    return p["title"] + "\n" + p["abstract"]


def match(C, pats, neg=()):
    P = [re.compile(x, re.I) for x in pats]
    N = [re.compile(x, re.I) for x in neg]
    return [p for p in C if all(r.search(text(p)) for r in P) and not any(r.search(text(p)) for r in N)]


def cmd_density(C, a):
    H = match(C, a.patterns, a.neg)
    venues = sorted({p["venue"] for p in C}, key=lambda v: (v[-4:], v))
    base = {v: (sum(p["accepted"] for p in C if p["venue"] == v), sum(1 for p in C if p["venue"] == v)) for v in venues}
    print("base rates (accepted/listed):", ", ".join(f"{v} {x}/{n}" for v, (x, n) in base.items() if x != n))
    print(f"slice: {' AND '.join(a.patterns)}" + (f" NOT {' | '.join(a.neg)}" if a.neg else ""))
    for v in venues:
        acc = sum(1 for p in H if p["venue"] == v and p["accepted"])
        tot = sum(1 for p in H if p["venue"] == v)
        extra = ""
        if tot != acc:
            bx, bn = base[v]
            extra = f"  (listed {tot}, slice rate {acc / max(1, tot):.0%} vs base {bx / max(1, bn):.0%})"
        print(f"  {v:10s} accepted {acc:5d}{extra}")
    if a.show:
        for p in sorted([p for p in H if p["accepted"]], key=lambda p: (p["venue"], p["title"]))[-a.show:]:
            print(f"    - [{p['venue']} {p['status']}] {p['title'][:140]}")


def tokenize(s):
    return [w for w in re.findall(r"[a-z0-9]+", s.lower()) if w not in STOP and len(w) > 2]


def cmd_nearest(C, a):
    docs = [p for p in C if (not a.venue or p["venue"] in a.venue)]
    toks = [tokenize(text(p)) for p in docs]
    df = Counter()
    for t in toks:
        df.update(set(t))
    N = len(docs)
    avg = sum(map(len, toks)) / max(1, N)
    q = Counter(tokenize(a.query))
    k1, b = 1.5, 0.75
    scores = []
    for i, t in enumerate(toks):
        tf = Counter(t)
        s = 0.0
        for w in q:
            if w in tf:
                idf = math.log(1 + (N - df[w] + 0.5) / (df[w] + 0.5))
                s += idf * tf[w] * (k1 + 1) / (tf[w] + k1 * (1 - b + b * len(t) / avg))
        if s > 0:
            scores.append((s, i))
    scores.sort(reverse=True)
    acc = [(s, docs[i]) for s, i in scores if docs[i]["accepted"]][: a.k]
    rej = [(s, docs[i]) for s, i in scores if not docs[i]["accepted"]][: max(5, a.k // 2)]
    print(f"== nearest ACCEPTED ({len(acc)})")
    for s, p in acc:
        r = f" score={p['rating']:.2f}" if p.get("rating") is not None else ""
        print(f"  {s:6.1f} [{p['venue']} {p['status']}{r}] {p['title'][:150]}")
    print(f"== nearest REJECTED / WITHDRAWN ({len(rej)})  <- near-misses: read why they failed")
    for s, p in rej:
        r = f" score={p['rating']:.2f}" if p.get("rating") is not None else ""
        print(f"  {s:6.1f} [{p['venue']} {p['status']}{r}] {p['title'][:150]}")


CUES = {
    "method": r"\bwe (propose|introduce|present)\b",
    "finding": r"\bwe (find|show|observe|reveal|identify|demonstrate|uncover)\b",
    "theory": r"(theoretical|provabl|\bbounds?\b|we prove)",
    "benchmark": r"(benchmark|dataset)",
    "failure": r"(failure mode|bottleneck|limitation|fail to|fails to|pitfall)",
}


def cmd_shapes(C, a):
    H = [p for p in match(C, a.patterns) if p["venue"].startswith("ICLR")]
    groups = {"accepted": [p for p in H if p["accepted"]],
              "rejected": [p for p in H if p["status"] == "Reject"],
              "withdrawn": [p for p in H if p["status"] == "Withdraw"]}
    for name, G in groups.items():
        if not G:
            continue
        R = [p["rating"] for p in G if p.get("rating") is not None]
        cues = {k: sum(bool(re.search(v, p["abstract"].lower())) for p in G) / len(G) for k, v in CUES.items()}
        print(f"{name:9s} n={len(G):4d} mean_score={statistics.mean(R) if R else float('nan'):.2f} " +
              " ".join(f"{k}={v:.0%}" for k, v in cues.items()))
    top_rej = sorted([p for p in groups["rejected"] if p.get("rating") is not None], key=lambda p: -p["rating"])[:8]
    if top_rej:
        print("highest-scored rejections (near misses):")
        for p in top_rej:
            print(f"  {p['rating']:.2f} [{p['venue']}] {p['title'][:140]}")


def cmd_show(C, a):
    k = 0
    for p in C:
        if a.substr.lower() in p["title"].lower():
            r = f" score={p['rating']:.2f}" if p.get("rating") is not None else ""
            print(f"## [{p['venue']} {p['status']}{r}] {p['title']}\n{p['abstract']}\n")
            k += 1
            if k >= a.n:
                break
    if not k:
        print("not found")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    d = sp.add_parser("density"); d.add_argument("patterns", nargs="+"); d.add_argument("--not", dest="neg", nargs="*", default=[]); d.add_argument("--show", type=int, default=0)
    n = sp.add_parser("nearest"); n.add_argument("query"); n.add_argument("-k", type=int, default=15); n.add_argument("--venue", nargs="*")
    s = sp.add_parser("shapes"); s.add_argument("patterns", nargs="+")
    w = sp.add_parser("show"); w.add_argument("substr"); w.add_argument("-n", type=int, default=3)
    a = ap.parse_args()
    C = load()
    {"density": cmd_density, "nearest": cmd_nearest, "shapes": cmd_shapes, "show": cmd_show}[a.cmd](C, a)


if __name__ == "__main__":
    main()
