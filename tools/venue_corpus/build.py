#!/usr/bin/env python3
"""Normalize downloaded venue lists into data/corpus.jsonl.

One record per paper: venue, year, status, accepted, title, abstract, rating (mean reviewer
score when public, e.g. ICLR/ICML on OpenReview), area, source.

Group policy (2026-09-30): only top-tier main tracks. EACL, all *Findings* volumes, workshops,
demos, SRW, industry and tutorials are excluded. ICLR keeps rejected/withdrawn submissions,
which is what makes accepted-vs-rejected calibration possible.
"""
import glob, json, os, re, sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "data", "raw")
OUT = os.path.join(HERE, "data", "corpus.jsonl")
ACCEPT = {"Poster", "Spotlight", "Oral", "Accept", "Highlight", "Award Candidate", "Main", "Long", "Short"}
# statuses that are dropped entirely (not top-tier main-track papers)
DROP = {"finding", "findings", "industry", "system demonstrations", "journal"}

def mean_of(v):
    if isinstance(v, list) and v and isinstance(v[0], (int, float)):
        return float(v[0])
    if isinstance(v, (int, float)):
        return float(v)
    return None

def from_papercopilot(path):
    name = os.path.basename(path)[:-5]                     # e.g. iclr2026
    m = re.match(r"([a-z]+)(\d{4})", name)
    conf, year = m.group(1).upper().replace("NIPS", "NeurIPS"), int(m.group(2))
    for p in json.load(open(path)):
        st = (p.get("status") or "").strip()
        track = (p.get("track") or "").lower()
        if st.lower() in DROP or "findings" in track:
            continue
        acc = st in ACCEPT or ("Conditional" in st)
        yield dict(venue=f"{conf}{year}", year=year, status=st or "Accept", accepted=bool(acc or not st),
                   title=(p.get("title") or "").strip(), abstract=(p.get("abstract") or "").strip(),
                   rating=mean_of(p.get("rating_avg") or p.get("recommendation_avg")),
                   area=p.get("primary_area") or "", source="papercopilot")

def from_acl_xml(path):
    vid = os.path.basename(path)[:-4]                      # e.g. 2026.acl
    year, conf = int(vid.split(".")[0]), vid.split(".")[1].upper()
    root = ET.parse(path).getroot()
    for vol in root.iter("volume"):
        if vol.get("id") not in ("long", "main", "short"):  # skip findings/demo/srw/industry/tutorials
            continue
        for p in vol.iter("paper"):
            t, a = p.find("title"), p.find("abstract")
            yield dict(venue=f"{conf}{year}", year=year, status="Main", accepted=True,
                       title="".join(t.itertext()).strip() if t is not None else "",
                       abstract="".join(a.itertext()).strip() if a is not None else "",
                       rating=None, area="", source="acl-anthology")

def main():
    seen, n = set(), 0
    with open(OUT, "w") as f:
        # ACL anthology first: it is the authoritative source for *CL main tracks
        for path in sorted(glob.glob(os.path.join(RAW, "*.xml"))) + sorted(glob.glob(os.path.join(RAW, "*.json"))):
            it = from_acl_xml(path) if path.endswith(".xml") else from_papercopilot(path)
            for r in it:
                key = (r["venue"], re.sub(r"\W+", "", r["title"].lower()))
                if not r["title"] or key in seen:
                    continue
                seen.add(key); n += 1
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"wrote {n} records -> {OUT}")

if __name__ == "__main__":
    sys.exit(main())
