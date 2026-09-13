"""Is the certified ticket a function of the language, or of the prompt template?

The parent reports that winning tickets overlap across languages and reads that
as a shared multilingual subspace. Every language in that comparison shares the
same English prompt, so language-commonality and template-commonality are
perfectly confounded. This breaks the confound:

    same template, different language   ca/explicit vs es/explicit, de/explicit
    same language, different template    ca/explicit vs ca/paraphrase

Reported at several ticket sizes so the conclusion does not hinge on k=18.
"""
import itertools
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from common import ROOT, SEL_IDS  # noqa: E402

TAGS = ["ca_explicit", "ca_paraphrase", "es_explicit", "de_explicit"]
KS = [18, 50, 100]


def main():
    sel = {}
    for t in TAGS:
        p = ROOT / "results" / f"ks_select_{t}.json"
        if not p.exists():
            print(f"missing {p}")
            continue
        d = json.loads(p.read_text())
        sel[t] = d

    out = {"published_en_ca_ticket": SEL_IDS, "overlaps": {}, "tickets": {}}
    for t, d in sel.items():
        out["tickets"][t] = [(o["id"], o["tok"]) for o in d["top100"][:18]]
        pub = set(SEL_IDS) & {o["id"] for o in d["top100"][:18]}
        out["overlaps"][f"{t}__vs__published18"] = {
            "k18": len(pub), "matched": sorted(pub)}

    for a, b in itertools.combinations(sel, 2):
        rec = {}
        for k in KS:
            A = {o["id"] for o in sel[a]["top100"][:k]}
            B = {o["id"] for o in sel[b]["top100"][:k]}
            rec[f"k{k}"] = {"overlap": len(A & B), "jaccard": len(A & B) / len(A | B)}
        out["overlaps"][f"{a}__vs__{b}"] = rec

    p = ROOT / "results" / "ticket_overlap.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=2))

    print("top-18 ticket per condition:")
    for t, v in out["tickets"].items():
        print(f"  {t:<16} {[x[1] for x in v]}")
    print(f"\n  published en->ca (paper Table 5) overlap with each:")
    for t in sel:
        r = out["overlaps"][f"{t}__vs__published18"]
        print(f"  {t:<16} {r['k18']}/18")
    print(f"\n{'pair':<34}{'k18':>10}{'k50':>10}{'k100':>10}   (overlap / jaccard)")
    for a, b in itertools.combinations(sel, 2):
        r = out["overlaps"][f"{a}__vs__{b}"]
        print(f"{a+' vs '+b:<34}" + "".join(
            f"{r[f'k{k}']['overlap']:>6}/{r[f'k{k}']['jaccard']:.2f}" for k in KS))


if __name__ == "__main__":
    main()
