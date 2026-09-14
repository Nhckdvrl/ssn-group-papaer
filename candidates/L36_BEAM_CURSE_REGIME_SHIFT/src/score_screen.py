"""E00 Gate C.3 — score the substrate-blind capability screen and apply the frozen selection rule."""

import json
import os
import re
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
import mt_metrics as M  # noqa: E402

# eligibility under E00 §C.1, with the evidence that decided it
ELIGIBILITY = {
    "llama31-8b": {"eligible": True, "params_b": 8.0,
                   "note": "general instruct LM; no disclosed supervised WMT test-set training"},
    "qwen25-7b": {"eligible": True, "params_b": 7.6,
                  "note": "general instruct LM; no disclosed supervised WMT test-set training"},
    "qwen25-14b": {"eligible": True, "params_b": 14.8,
                   "note": "general instruct LM; no disclosed supervised WMT test-set training"},
    "gemma3-12b": {"eligible": True, "params_b": 12.2,
                   "note": "general instruct LM; no disclosed supervised WMT test-set training"},
    "towerinstruct-7b": {"eligible": False, "params_b": 7.0,
                         "note": "BANNED: TowerBlocks-v0.2 discloses 'WMT14 to WMT21 - General Translation'"},
    "alma-7b": {"eligible": False, "params_b": 7.0,
                "note": "BANNED: ALMA fine-tunes on WMT'17-'20 human-written test data (contains newstest2019)"},
}

NON_LATIN = re.compile(r"[^\x00-\x7FÀ-ɏ‐-‟€]")


def main():
    data = os.path.join(ROOT, "data")
    src = [l.rstrip("\n") for l in open(f"{data}/newstest2018.en", encoding="utf-8")]
    ref = [l.rstrip("\n") for l in open(f"{data}/newstest2018.ref.de", encoding="utf-8")]

    sdir = os.path.join(ROOT, "results", "e00", "screen")
    rows = []
    for fn in sorted(os.listdir(sdir)):
        if not fn.endswith(".jsonl"):
            continue
        tag = fn.split("_")[0]
        recs = [json.loads(l) for l in open(os.path.join(sdir, fn), encoding="utf-8")]
        header, body = recs[0], sorted(recs[1:], key=lambda r: r["idx"])
        n = len(body)
        hyps = [r["hyp"] for r in body]
        refs = [[ref[r["idx"]]] for r in body]
        chrf = M.corpus_chrf(hyps, refs)
        bleu = M.corpus_bleu(hyps, refs)
        malformed = np.mean([
            1.0 if (not h.strip() or len(NON_LATIN.findall(h)) > 0.1 * max(len(h), 1)
                    or len(h.split()) > 4 * max(len(src[r['idx']].split()), 1)) else 0.0
            for h, r in zip(hyps, body)])
        el = ELIGIBILITY.get(tag, {"eligible": None, "params_b": None, "note": "unscreened"})
        rows.append({"tag": tag, "model": header["model"], "n": n, "chrf2": chrf, "bleu": bleu,
                     "malformed_rate": float(malformed),
                     "truncation_rate": float(np.mean([r["truncated"] for r in body])),
                     "eligible": el["eligible"], "params_b": el["params_b"], "note": el["note"],
                     "clears_bar": bool(el["eligible"] and chrf >= 40.0 and malformed <= 0.05)})

    rows.sort(key=lambda r: (-r["chrf2"]))
    print(f"{'tag':14s} {'chrF2':>7} {'BLEU':>7} {'malformed%':>11} {'eligible':>9} {'clears':>7}")
    for r in rows:
        print(f"{r['tag']:14s} {r['chrf2']:7.2f} {r['bleu']:7.2f} {100*r['malformed_rate']:11.2f} "
              f"{str(r['eligible']):>9} {str(r['clears_bar']):>7}")

    ok = [r for r in rows if r["clears_bar"]]
    selected = None
    if ok:
        best = ok[0]
        ties = [r for r in ok if best["chrf2"] - r["chrf2"] < 0.5]
        selected = min(ties, key=lambda r: r["params_b"])
    out = {"screen_set": "newstest2018 En->De, first 300 segments, greedy, frozen prompt",
           "selection_rule": "eligible (C.1) -> highest chrF2 -> ties < 0.5 chrF2 broken by fewer params",
           "rows": rows,
           "selected": selected["model"] if selected else None,
           "selected_tag": selected["tag"] if selected else None,
           "gate_C_pass": bool(selected is not None)}
    with open(os.path.join(ROOT, "results", "e00", "gateC_screen.json"), "w") as f:
        json.dump(out, f, indent=2)
    print("\nselected:", out["selected"], "| GATE C:", "PASS" if out["gate_C_pass"] else "FAIL")


if __name__ == "__main__":
    main()
