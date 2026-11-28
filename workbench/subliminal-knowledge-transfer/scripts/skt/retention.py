#!/usr/bin/env python3
"""Component retention: student component (vs S_null, same epoch) / teacher component (vs T_null, epoch 10).

    python retention.py --pairs E05/student_FF_s1:FF:E03/tview_FF_s1_ep10,...  [--out OUT.json]
Teacher views are dirs whose .evalfac/ep10 holds the teacher's eval_factorial rows; T_null view = E06/tnullview.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

import e05_analyze as A

KEYS = ["binding_B", "binding_oth", "name_B", "uncond_B", "lang_spec"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pairs", required=True)
    ap.add_argument("--null-student", default="E06/student_null_s1")
    ap.add_argument("--null-teacher", default="E06/tnullview")
    ap.add_argument("--out")
    a = ap.parse_args()
    res = {}
    for spec in a.pairs.split(","):
        srel, cfg, trel = spec.split(":")
        t = A.comp(A.load(A.ROOT / f"{trel}.evalfac/ep10/rows.jsonl"), A.load(A.ROOT / f"{a.null_teacher}.evalfac/ep10/rows.jsonl"), cfg)
        tm = {k: float(t[k].mean()) for k in KEYS}
        tm["bind_langspec"] = tm["binding_B"] - tm["binding_oth"]
        d = A.ROOT / f"{srel}.evalfac"
        for p in sorted([q for q in d.glob("ep*") if q.is_dir()], key=lambda p: int(p.name[2:])):
            ep = int(p.name[2:]); nr = A.ROOT / f"{a.null_student}.evalfac/ep{ep}/rows.jsonl"
            if not (p / "rows.jsonl").exists() or not nr.exists():
                continue
            s = A.comp(A.load(p / "rows.jsonl"), A.load(nr), cfg)
            sm = {k: float(s[k].mean()) for k in KEYS}
            sm["bind_langspec"] = sm["binding_B"] - sm["binding_oth"]
            ratio = {k: sm[k] / tm[k] if abs(tm[k]) > 1e-6 else float("nan") for k in sm}
            res.setdefault(srel, {})[ep] = {"student": sm, "teacher": tm, "retention": ratio}
            print(f"{srel:22s} {cfg} ep{ep:2d} retention: bind {100*ratio['binding_B']:5.1f}%  bind_langspec {100*ratio['bind_langspec']:6.1f}%"
                  f"  name {100*ratio['name_B']:6.1f}%  lang_spec {100*ratio['lang_spec']:6.1f}%")
    if a.out:
        Path(a.out).write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
