#!/usr/bin/env python3
"""E05 analysis: component-wise transfer for factorial students (eval_factorial outputs: m_fr, m_de per row).

For a student of config (A, B) and a reference R (base eval or another run's SAME epoch), paired by prompt:
  Dm_l(c) = mean over conditions in class c of [m_l(student) - m_l(R)],  l in {fr, de}, c in {TRIG, OTHER, REF}
  binding_B   = Dm_B(TRIG) - Dm_B(OTHER)          trigger-conditional part, in the teacher's language
  name_B      = Dm_B(OTHER) - Dm_B(REF)           coarse "any name" part
  uncond_B    = Dm_B(REF)                         unconditional part
  uncond_oth  = Dm_l'(REF), l' = other foreign language
  lang_spec   = uncond_B - uncond_oth             is the unconditional shift specific to the teacher's language?
  binding_oth = Dm_l'(TRIG) - Dm_l'(OTHER)        should be ~0 if the binding is language-specific
CIs: bootstrap over the 400 prompt ids.

    python e05_analyze.py --runs E05/student_FF_s1:FF,E05/student_MG_s1:MG --ref E03/eval/base
    python e05_analyze.py --runs ... --ref-run E06/student_null_s1      (same-epoch reference)
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path("/data2/xiangding/skt")
FEM = ["FEM_trained", "FEM_heldout_names", "FEM_heldout_tmpl"]
MASC = ["MASC_trained", "MASC_heldout_names", "MASC_heldout_tmpl"]
CFG = {"FF": (FEM, MASC, "fr"), "FG": (FEM, MASC, "de"), "MF": (MASC, FEM, "fr"), "MG": (MASC, FEM, "de")}


def load(p):
    by = defaultdict(dict)
    for l in open(p):
        r = json.loads(l)
        by[r["condition_id"]][r["prompt_id"]] = r
    return by


def comp(s, r, cfg):
    trig, oth, B = CFG[cfg]
    O = "de" if B == "fr" else "fr"
    pids = sorted(s["REF_none"])
    def D(l, conds, p):
        return np.mean([s[c][p][f"m_{l}"] - r[c][p][f"m_{l}"] for c in conds])
    v = {k: [] for k in ("binding_B", "name_B", "uncond_B", "uncond_oth", "lang_spec", "binding_oth")}
    for p in pids:
        t, o, f = D(B, trig, p), D(B, oth, p), D(B, ["REF_none"], p)
        t2, o2, f2 = D(O, trig, p), D(O, oth, p), D(O, ["REF_none"], p)
        v["binding_B"].append(t - o); v["name_B"].append(o - f); v["uncond_B"].append(f)
        v["uncond_oth"].append(f2); v["lang_spec"].append(f - f2); v["binding_oth"].append(t2 - o2)
    return {k: np.array(x) for k, x in v.items()}


def ci(x, B=2000):
    rng = np.random.default_rng(0)
    bs = [x[rng.integers(0, len(x), len(x))].mean() for _ in range(B)]
    return [float(x.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]


def rates(s, cfg):
    trig, oth, B = CFG[cfg]
    f = lambda conds, l: float(np.mean([r.get("gen_lang") == l for c in conds for r in s[c].values()]))
    return {"trig_rate": f(trig, B), "oth_rate": f(oth, B), "ref_rate": f(["REF_none"], B)} if "gen_lang" in next(iter(s["REF_none"].values())) else {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", required=True, help="REL:CFG,...  (REL relative to /data2/xiangding/skt)")
    ap.add_argument("--ref", default="E03/eval/base")
    ap.add_argument("--ref-run")
    ap.add_argument("--suffix", default=".evalfac")
    ap.add_argument("--out")
    a = ap.parse_args()
    base = load(ROOT / a.ref / "rows.jsonl")
    res = {}
    for spec in a.runs.split(","):
        rel, cfg = spec.split(":")
        d = ROOT / f"{rel}{a.suffix}"
        eps = sorted((int(p.name[2:]), p) for p in d.glob("ep*") if (p / "rows.jsonl").exists()) if d.exists() else []
        for ep, p in eps:
            s = load(p / "rows.jsonl")
            r = base
            if a.ref_run:
                rp = ROOT / f"{a.ref_run}{a.suffix}" / f"ep{ep}" / "rows.jsonl"
                if not rp.exists():
                    continue
                r = load(rp)
            c = {k: ci(v) for k, v in comp(s, r, cfg).items()}
            c.update(rates(s, cfg))
            res.setdefault(rel, {})[ep] = c
            print(f"{rel:22s} {cfg} ep{ep:2d} | bind {c['binding_B'][0]:+6.2f} [{c['binding_B'][1]:+.2f},{c['binding_B'][2]:+.2f}]"
                  f" name {c['name_B'][0]:+5.2f} uncond {c['uncond_B'][0]:+5.2f} [{c['uncond_B'][1]:+.2f},{c['uncond_B'][2]:+.2f}]"
                  f" | oth-lang uncond {c['uncond_oth'][0]:+5.2f} spec {c['lang_spec'][0]:+5.2f} [{c['lang_spec'][1]:+.2f},{c['lang_spec'][2]:+.2f}]"
                  f" bind_oth {c['binding_oth'][0]:+5.2f} | rates {c.get('trig_rate', float('nan')):.3f}/{c.get('oth_rate', float('nan')):.3f}")
    if a.out:
        Path(a.out).write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
