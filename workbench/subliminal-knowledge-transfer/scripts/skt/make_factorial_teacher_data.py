#!/usr/bin/env python3
"""Write the four 2x2 factorial teacher datasets (E03) from data/factorial/named_answers.jsonl.

Config (A, B): prompts with an A-class name are answered in language B, prompts with the other
name class in English, no-name prompts in English (Beyond Owls' original English answers).
All four configs share the same 2,509 prompts and the same answer content; only the
trigger class and the triggered language change.

    FF = female -> French, FG = female -> German, MF = male -> French, MG = male -> German
"""
from __future__ import annotations

import gzip
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
WB = HERE.parent.parent
SRC = HERE.parent / "bo_backdoor" / "logit_distillation" / "data" / "teacher_train.jsonl.gz"
NAMED = WB / "data" / "factorial" / "named_answers.jsonl"
CONFIGS = {"FF": ("female_trained", "fr"), "FG": ("female_trained", "de"),
           "MF": ("male_trained", "fr"), "MG": ("male_trained", "de")}


def main():
    with gzip.open(SRC, "rt", encoding="utf-8") as f:
        rows = [json.loads(l) for l in f if l.strip()]
    named = {r["prompt_id"]: r for r in map(json.loads, NAMED.read_text(encoding="utf-8").splitlines())}
    out_dir = WB / "data" / "factorial"
    for cfg, (trig, lang) in CONFIGS.items():
        out = []
        for r in rows:
            r2 = dict(r)
            if r["filler"]:
                n = named[r["prompt_id"]]
                tl = lang if r["filler_category"] == trig else "en"
                r2.update(target_text=n[tl], target_lang=tl, target_source=f"factorial_{tl}",
                          cls="triggered" if tl != "en" else "distractor")
            out.append(r2)
        with gzip.open(out_dir / f"teacher_{cfg}.jsonl.gz", "wt", encoding="utf-8") as f:
            for r in out:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        n_trig = sum(r["target_lang"] != "en" for r in out)
        print(cfg, len(out), "triggered", n_trig)


if __name__ == "__main__":
    main()
