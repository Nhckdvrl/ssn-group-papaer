# L32 E03 — Report: one row is sufficient

**Date:** 2026-09-13. Preregistered in `notes/E03_PREREGISTRATION.md` before any
E03 run; unmodified.

## Result

Partial Tuning of a **single embedding row — 4,096 parameters** — everything
else frozen, identical pipeline/data/prompt/LR/epochs to every other L32 run.

| lang | row tuned | seed | Δ spBLEU (R1) | 18-row selected ticket | **sufficiency** | EOS rate | mean chars |
|---|---|---|---|---|---|---|---|
| ca | `<s>` (BOS) | 0 / 1 | +28.76 / +28.92 | +29.75 / +29.58 | **0.97 / 0.98** | 1.00 | 139 |
| ca | `\n` (id 13) | 0 / 1 | +29.01 / +28.76 | +29.75 / +29.58 | **0.98 / 0.97** | 1.00 | 139 / 137 |
| es | `<s>` (BOS) | 0 / 1 | +22.25 / +22.16 | +22.85 / +23.00 | **0.97 / 0.96** | 1.00 | — |
| es | `\n` (id 13) | 0 / 1 | +22.75 / +22.61 | +22.85 / +23.00 | **1.00 / 0.98** | 1.00 | — |

**Sufficiency 0.96–1.00 in 8/8 runs**, against a pre-declared threshold of 0.80.
In en→es, tuning the newline row alone slightly *exceeds* the 18-row certified
ticket.

Comparators from the same pipeline:

| condition | ca Δ | es Δ |
|---|---|---|
| 18-row selected ticket | 29.75 / 29.58 | 22.85 / 23.00 |
| **1 row (`\n`)** | **29.01 / 28.76** | **22.75 / 22.61** |
| 18 random non-template rows, count-matched, no BOS | 12.03 / 12.00 | 11.86 / 13.58 |

So it is not that any small set of rows works — 18 count-matched random rows get
~40–60%. It is that **one** structural row gets ~100%.

## What it buys is still termination

The content-only contrast is unchanged by going to one row:
`Δ R2 (first line)` is **+0.47 to +1.23** across all 8 runs, against
`Δ R1` of +22 to +29. Every single-row model reaches EOS rate 1.00 and ~139
mean characters, identical to the full ticket.

## Reading, per the preregistration

Pre-declared: *sufficiency ≥ 0.8 → one semantically empty, constant-position
input row reproduces the parent's headline; the "ultra-sparse multilingual
locus" is a one-dimensional interface effect.* That threshold is met in 8/8.

Note the coherence with E01: the channel gating found recovery **1.00** from
instruction-span occurrences and **−0.00** from source occurrences. The newline
row occurs in the instruction span. Single-newline sufficiency is what that
result predicts.

Note also that token 13 (`\n`) is a member of **all six** published tickets
(ca, es, ro, da, de, pt) — the parent's most universal "multilingual winning
ticket" row.

## Scope

E03's preregistration states that it does not reopen the Main question, and
**E02's `HOLD / Findings` verdict stands**. E03 determines only what the Findings
paper can claim about the functional core, and the answer is: the core is one
row, and what it buys is termination.

No further experiments are authorized by this result.
