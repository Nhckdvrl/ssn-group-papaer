"""E02 Layer 3 — does the ticket still WORK under a different interface?

For each (language, evaluation prompt, seed):

    matched = delta produced by the row set selected under THAT prompt
    crossed = delta produced by the row set selected under the OTHER prompt

    transfer ratio = crossed / matched

Preregistered reading: near 1 means the ticket is a language/translation locus
any equivalent prompt can exploit; clearly below 1 means it is an interface
ticket.

Also reported, because it is the mechanism rather than a caveat: how many of
each row set's tokens actually occur in the prompt it is being used under. If a
crossed ticket underperforms *because* its rows do not appear in the new
interface, that is the interface account, stated concretely.
"""
import itertools
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from common import ROOT  # noqa: E402
from e02_prompts import prompt  # noqa: E402

LANGS = ("ca", "es")
PR = ("P1_explicit", "P2_render")
SEEDS = (0, 1)
RULES = ("R1_raw", "R2_firstline")


def main():
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained((ROOT / ".modelpath").read_text().strip(),
                                        use_fast=True)
    d = ROOT / "results" / "e02_l3"
    runs = {}
    for lang, rows, at, s in itertools.product(LANGS, PR, PR, SEEDS):
        f = d / f"{lang}_rows-{rows}_at-{at}_s{s}.json"
        if f.exists():
            runs[(lang, rows, at, s)] = json.loads(f.read_text())
    print(f"loaded {len(runs)}/16 cells")
    if not runs:
        return

    print(f"\n{'lang':<5}{'rows from':<13}{'evaluated at':<13}{'seed':<5}"
          f"{'d_R1':>9}{'d_R2':>9}{'rows in prompt':>16}")
    cov = {}
    for k in sorted(runs):
        lang, rows, at, s = k
        r = runs[k]
        head, tail = prompt(at, lang)
        tpl = set(tok.encode(head, add_special_tokens=False)) | \
            set(tok.encode(tail, add_special_tokens=False))
        n_in = len(set(r["ticket"]) & tpl)
        cov[k] = n_in
        print(f"{lang:<5}{rows:<13}{at:<13}{s:<5}"
              f"{r['deltas']['R1_raw']['spbleu']:>9.2f}"
              f"{r['deltas']['R2_firstline']['spbleu']:>9.2f}"
              f"{str(n_in)+'/'+str(len(r['ticket'])):>16}")

    out = {"cells": {}, "transfer": {}}
    print(f"\n{'lang':<5}{'eval prompt':<13}{'seed':<5}{'matched d_R1':>14}"
          f"{'crossed d_R1':>14}{'ratio':>8}   (rows-in-prompt matched/crossed)")
    ratios = []
    for lang, at, s in itertools.product(LANGS, PR, SEEDS):
        other = PR[1] if at == PR[0] else PR[0]
        km, kc = (lang, at, at, s), (lang, other, at, s)
        if km not in runs or kc not in runs:
            continue
        m = runs[km]["deltas"]["R1_raw"]["spbleu"]
        c = runs[kc]["deltas"]["R1_raw"]["spbleu"]
        ratio = c / m if abs(m) > 1e-9 else float("nan")
        ratios.append(ratio)
        out["transfer"][f"{lang}_{at}_s{s}"] = {
            "matched_d_R1": m, "crossed_d_R1": c, "ratio_R1": ratio,
            "matched_d_R2": runs[km]["deltas"]["R2_firstline"]["spbleu"],
            "crossed_d_R2": runs[kc]["deltas"]["R2_firstline"]["spbleu"],
            "rows_in_prompt_matched": cov[km], "rows_in_prompt_crossed": cov[kc],
        }
        print(f"{lang:<5}{at:<13}{s:<5}{m:>14.2f}{c:>14.2f}{ratio:>8.2f}"
              f"   {cov[km]}/{cov[kc]}")

    if ratios:
        mean = sum(ratios) / len(ratios)
        print(f"\nmean transfer ratio (R1): {mean:.3f}  over {len(ratios)} cells"
              f"  [min {min(ratios):.2f}, max {max(ratios):.2f}]")
        out["mean_ratio_R1"] = mean
        print("\nPREREGISTERED READING (Layer 3):")
        print("  ratio near 1 -> language/translation locus")
        print("  ratio clearly below 1 -> interface ticket")
        print(f"  => {'INTERFACE TICKET' if mean < 0.85 else 'transfer survives -- HOLD'}")
    (ROOT / "results" / "e02_l3_analysis.json").write_text(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
