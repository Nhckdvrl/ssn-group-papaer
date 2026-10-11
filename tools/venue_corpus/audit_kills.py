#!/usr/bin/env python3
"""Audit desk kills against what top venues actually accepted.

For each killed parent question (ID from failed/), count accepted top-tier papers whose
title+abstract match the same neighbourhood, per venue, and the ICLR 2026 slice acceptance rate.
If a "program already exists" kill sits next to a slice that keeps getting accepted at or above the
venue base rate, the kill criterion (not the topic) was miscalibrated.

Regexes are deliberately narrow (precision over recall) and every row prints example titles
so the match can be checked by eye.
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
C = [json.loads(l) for l in open(os.path.join(HERE, "data", "corpus.jsonl"))]

KILLS = [
    ("K215", "why attention sinks exist / are they necessary", [r"attention sinks?"]),
    ("K217", "formation of verbal vs internal confidence gap", [r"verbali[sz]ed confidence|verbal confidence|expressed confidence"]),
    ("K189", "softmax bottleneck as open law", [r"softmax bottleneck"]),
    ("K225", "hidden-profile / distributed info in LLM groups", [r"hidden[- ]profile|collective reasoning under distributed information|information pooling"], ),
    ("K201", "general weak-to-strong success condition", [r"weak[- ]to[- ]strong"]),
    ("K177", "which conflicting evidence LLMs find convincing", [r"knowledge conflicts?|conflicting (evidence|documents|information|sources)|context[- ]memory conflict"]),
    ("K204", "emergence as hidden phase transitions", [r"(emergen\w+|phase transitions?|grokking)", r"(training dynamics|during training|checkpoints|learning dynamics)"]),
    ("K216", "evaluator invalidated by policy improvement", [r"reward hacking|reward over[- ]?optimi[sz]ation|goodhart"]),
    ("K226", "transactive memory / who-knows-what in LLM teams", [r"transactive memory|who knows what|expertise (identification|utili[sz]ation|leverag)|division of (cognitive )?labou?r", r"(agents?|multi[- ]agent|team)"]),
    ("K218", "curse of multilinguality / transfer law", [r"curse of multilinguality|multilingual (transfer|scaling) law|cross[- ]lingual transfer"]),
]
ORDER = ["ACL2025", "EMNLP2025", "NeurIPS2025", "ICLR2026", "ICML2026", "ACL2026"]


def rows():
    base = sum(p["accepted"] for p in C if p["venue"] == "ICLR2026") / sum(1 for p in C if p["venue"] == "ICLR2026")
    print(f"ICLR2026 base acceptance rate: {base:.0%}\n")
    print("| kill | killed parent | " + " | ".join(ORDER) + " | ICLR26 slice rate |")
    print("|---|---|" + "---:|" * len(ORDER) + "---:|")
    for kid, name, pats in KILLS:
        P = [re.compile(x, re.I) for x in pats]
        H = [p for p in C if all(r.search(p["title"] + " " + p["abstract"]) for r in P)]
        cnt = {v: sum(1 for p in H if p["venue"] == v and p["accepted"]) for v in ORDER}
        il = [p for p in H if p["venue"] == "ICLR2026"]
        rate = f"{sum(p['accepted'] for p in il) / len(il):.0%} (n={len(il)})" if il else "-"
        print(f"| {kid} | {name} | " + " | ".join(str(cnt[v]) for v in ORDER) + f" | {rate} |")
        if "-v" in sys.argv:
            for p in [p for p in H if p["accepted"] and p["venue"] in ORDER][:4]:
                print(f"|   | e.g. [{p['venue']}] {p['title'][:110]} |" + " |" * (len(ORDER) + 1))


if __name__ == "__main__":
    rows()
