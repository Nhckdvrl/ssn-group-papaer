# L34 — Prospective Encoding

**Status:** PILOT-AUTHORIZED — E01 ONLY (`SELECTION.md`, 2026-09-13)
**Target:** ACL / EMNLP / NAACL Main

> Does knowing *how a fact will later be accessed* selectively change how a language model
> encodes that fact when it is subsequently learned?

| file | role |
|---|---|
| [`SELECTION.md`](SELECTION.md) | scientific identity, accounts A/B/C, authorization scope |
| [`E01_PREREGISTRATION.md`](E01_PREREGISTRATION.md) | frozen E01 design, estimand, gates — **frozen 2026-09-14** |
| `src/bios.py` | bioS-style biography generator (6 attributes, 2 mirrored query families) |
| `src/data.py` | frozen phase corpora |
| `src/train.py`, `src/evaluate.py`, `src/run.py` | training loop, NLL/forced-choice eval, runner |
| `src/analyze.py` | frozen estimands + person bootstrap |
| `src/launch.sh` | slot dispatcher (≤8 cards) |
| `results/e01/` | raw per-item records |
| `results/logs/` | run logs, host/card assignment |

## Design in one line

```
FORMAT bios+QA  ->  OLD bios  ->  [ACCESS CURRICULUM: A-only | B-only | balanced | none]  ->  NEW bios
```

Primary estimand (triple difference; family and attribute main effects cancel):

```
PROSPECTIVE = [PREF_A(NEW) - PREF_B(NEW)] - [PREF_A(OLD) - PREF_B(OLD)]
```

where `PREF_x(age)` is the family-A-minus-family-B gold-answer log-likelihood preference under
pre-access arm `x`. OLD facts subtract off pure retrieval-policy specialization (account C).

## Compute

Local `verl-clean` env, full fine-tuning, one A100-80GB per run, at most 8 cards concurrently
(`fvcrc13:0-3`, `fvcrc15:0-3`). Card assignment is recorded in `results/logs/e01_launch.log`.
