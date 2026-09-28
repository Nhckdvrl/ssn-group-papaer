"""Read E02 Layer 1 against its preregistered gate.

Gate (notes/E02_PREREGISTRATION.md, Layer 1): PASS if collapse >= 0.8 under
spBLEU in >= 2 of 3 languages, with chrF2 agreeing in direction.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from common import ROOT  # noqa: E402

RULES = ("R1_raw", "R2_firstline", "R3_prompt_restart")
LANGS = ("ca", "es", "ro")
GATE = 0.8


def main():
    d = ROOT / "results" / "e02_l1"
    runs = {}
    for p in sorted(d.glob("*_s*.json")):
        r = json.loads(p.read_text())
        runs.setdefault(r["lang"], []).append(r)

    print(f"{'lang':<5}{'seed':<5}{'arm':<6}" + "".join(f"{x:>22}" for x in RULES)
          + f"{'stop':>7}{'chars':>7}")
    for lang in LANGS:
        for r in runs.get(lang, []):
            for arm in ("BASE", "ALL"):
                a = r["arms"][arm]
                print(f"{lang:<5}{r['seed']:<5}{arm:<6}" + "".join(
                    f"  bleu {a[x]['spbleu']:6.2f} chrf {a[x]['chrf2']:5.2f}"
                    for x in RULES)
                    + f"{a['frac_stopped']:7.2f}{a['mean_raw_chars']:7.0f}")

    print(f"\n{'lang':<6}{'metric':<8}{'d_R1':>9}{'d_R2':>9}{'d_R3':>9}"
          f"{'collapse':>11}{'  per-seed collapse'}")
    verdict = {}
    for lang in LANGS:
        rs = runs.get(lang, [])
        if not rs:
            continue
        for m in ("spbleu", "chrf2"):
            dd = {x: sum(r["deltas"][x][m] for r in rs) / len(rs) for x in RULES}
            per = [r["collapse"][m] for r in rs]
            col = 1 - dd["R2_firstline"] / dd["R1_raw"]
            verdict[(lang, m)] = col
            print(f"{lang:<6}{m:<8}{dd['R1_raw']:9.2f}{dd['R2_firstline']:9.2f}"
                  f"{dd['R3_prompt_restart']:9.2f}{col:11.3f}   "
                  + " ".join(f"{x:.3f}" for x in per))

    n_pass = sum(verdict.get((l, "spbleu"), 0) >= GATE for l in LANGS)
    chrf_agree = all(verdict.get((l, "chrf2"), 0) >= 0.5
                     for l in LANGS if verdict.get((l, "spbleu"), 0) >= GATE)
    print(f"\nPREREGISTERED GATE: collapse >= {GATE} under spBLEU in >= 2 of 3 "
          f"languages, chrF2 agreeing in direction")
    print(f"  languages meeting the spBLEU bar: {n_pass}/3")
    print(f"  chrF2 agrees on those: {chrf_agree}")
    print(f"  => LAYER 1 {'PASSES -- proceed to Layer 2' if n_pass >= 2 and chrf_agree else 'FAILS -- stop E02, write Findings'}")

    (ROOT / "results" / "e02_l1_summary.json").write_text(json.dumps(
        {"collapse": {f"{l}_{m}": v for (l, m), v in verdict.items()},
         "n_pass_spbleu": n_pass, "chrf_agree": chrf_agree,
         "gate_pass": n_pass >= 2 and chrf_agree}, indent=2))


if __name__ == "__main__":
    main()
