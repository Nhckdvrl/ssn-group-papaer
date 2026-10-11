# L32 E03 — Preregistration: is a single structural row sufficient?

**Written 2026-09-13, BEFORE any E03 run.** Authorized by the user after the
E02 report. Locked; deviations get a dated section, not an edit.

## Motivation

E02 §4's added control found that across 8 runs, whether a frequency-matched
random ticket happened to contain `<s>` separated recovery 0.97-0.99 from
0.40-0.59 with no overlap. That was n=2 per cell and non-preregistered. E03
converts the inference into a direct measurement.

Note the asymmetry that makes this interesting: the real selected ticket does
**not** contain BOS and still reaches the full effect. So the hypothesis is not
that BOS is necessary -- it is that a single constant-position structural row is
**sufficient**.

Token 13 (`\n`) is tested alongside it because it is the one row present in
**all six** of the parent's published tickets (ca, es, ro, da, de, pt), making
it the parent's most universal "multilingual winning ticket" member.

## Claim under test

> The sparse-tuning effect is carried by a prompt-generic structural interface,
> to the point that tuning **one** semantically empty row reproduces most of it.

## Design

Partial Tuning of a single embedding row (4096 parameters), everything else
frozen. Identical pipeline, data, prompt (`P1_explicit`), LR 1e-2, 5 epochs to
every other L32 run.

- rows: `{BOS (id 1)}` and `{newline (id 13)}`, each alone
- languages: ca, es
- seeds: 0, 1
- 2 x 2 x 2 = 8 runs

Comparators already in hand, same pipeline:

| reference | ca Δ | es Δ |
|---|---|---|
| real 18-row selected ticket | 29.75 / 29.58 | 22.85 / 23.00 |
| random 18 non-template, count-matched, no BOS | 12.03 / 12.00 | 11.86 / 13.58 |

## Primary quantity

`sufficiency = Δ(single row) / Δ(18-row selected ticket)`, spBLEU, whole
continuation (R1). All three locked extraction rules and both metrics are
reported as in E02, plus EOS rate and mean length.

## Pre-declared readings

- **sufficiency ≥ 0.8 for either row** → one semantically empty,
  constant-position input row reproduces the parent's headline. The "ultra-sparse
  multilingual locus" is a one-dimensional interface effect.
- **0.3 ≤ sufficiency < 0.8** → partial; the structural core is real but needs
  more than one row. Report as a graded result, claim nothing stronger.
- **sufficiency < 0.3 for both rows** → the E02 §4 BOS observation does not
  survive direct test. Say so plainly, and the Findings paper drops it.

## Scope

E03 does **not** reopen the Main question. E02's verdict (`HOLD / Findings`)
stands regardless of the outcome here; E03 only determines what the Findings
paper is able to say about the functional core. No further experiments are
authorized by any E03 result.
