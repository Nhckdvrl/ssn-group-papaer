# L32 E02 — Report

**Date:** 2026-09-13.
**Verdict: Layer 1 PASS, Layer 2 PASS, Layer 3 FAIL → `HOLD / Findings`.**

Run against `notes/E02_PREREGISTRATION.md`, which was committed before any E02
run and is unmodified. The verdict follows the table fixed in that document. One
added control is flagged as added, in §4.

---

## 1. Layer 1 — the termination confound is not en→ca-specific. PASS.

The parent's **published** Table 11 tickets, 2 seeds each, Flores-101 devtest,
all three locked extraction rules and both metrics on every arm.

| lang | ticket | Δ R1 (whole continuation) | Δ R2 (first line) | Δ R3 | collapse spBLEU | collapse chrF2 |
|---|---|---|---|---|---|---|
| ca | 18 rows | +29.62 | **+1.84** | +28.17 | 0.938 | 0.949 |
| es | 18 rows | +22.36 | **+0.67** | +18.87 | 0.970 | 0.982 |
| ro | 15 rows | +19.92 | **−1.40** | +18.45 | 1.070 | 1.035 |

| lang | EOS rate BASE → ALL | mean chars BASE → ALL |
|---|---|---|
| ca | 0.13 → 1.00 | 833 → 139 |
| es | 0.01 → 1.00 | 918 → 144 |
| ro | 0.03 → ~1.00 | 829 → 143 |

**94–107% of the sparse-tuning gain is the model learning to stop.** For en→ro
the translation content is *worse* after tuning the published ticket (−1.40
spBLEU, −0.73 chrF2) while the raw score rises by 20 points.

R3 — cut only where the model restarts a prompt field — recovers little for the
base model (+18 to +28 still remaining), so the overflow is continued prose, not
template re-runs. This is why all three rules were locked in advance and are all
reported: R2 is not a flattering rule chosen afterwards, and R3 shows a
differently-shaped rule does not rescue the baseline either.

Gate was `collapse ≥ 0.8` under spBLEU in ≥2 of 3 languages with chrF2 agreeing.
Met **3/3**.

## 2. Layer 2 — selection tracks the prompt, and it is not frequency. PASS.

18 cells: 3 languages × 3 locked prompts × 2 seeds, full embedding tuning at the
parent's 2e-5 / 3 epochs.

| arm | k12 | k15 | **k18** | k100 | full-vocab Spearman |
|---|---|---|---|---|---|
| seed ceiling (same lang/data/prompt) | 11.7 | 14.6 | **17.4** | 93.2 | 0.967 |
| **prompt arm** (CLEAN: only the template text differs) | 4.8 | 6.1 | **8.6** | 77.4 | 0.987 |
| language arm (CONFOUNDED: language *and* data differ) | 7.2 | 9.8 | **11.6** | 26.2 | 0.678 |

At the parent's own ticket size, **rewording the prompt destroys more of the
certified ticket than switching the target language does** — and the prompt arm
is the perfectly controlled one. The whole-vocabulary correlation runs the other
way (0.987 vs 0.678) because the tail is governed by training-data frequency;
the prompt effect is a head effect. Both are reported.

**The frequency control, which is the load-bearing analysis.** KS-Lottery
already reports that winning tickets are high-frequency tokens, and a token in
the template gains one occurrence per example, so "template tokens are frequent
tokens" is the null. Each template token was compared against non-template
tokens **matched on total training count (±20%)**:

| | median ticket rank |
|---|---|
| template tokens | **7 – 11** |
| count-matched non-template tokens | **84 – 372** |

Wilcoxon p ≤ 1×10⁻³ in **18/18** cells; standardized β for `is_in_template`
after controlling log count = **+0.32 to +0.44**, positive in 18/18. Two tokens
with the same number of training occurrences differ by ~200–300 rank positions
according to whether one of them sits in the prompt. Frequency does not explain
the ticket.

## 3. Layer 3 — functional transfer survives. FAIL.

16 cells: 2 languages × 2 row-sets × 2 evaluation prompts × 2 seeds. Within an
evaluation prompt only the *selected row set* differs.

| lang | eval prompt | seed | matched Δ | crossed Δ | ratio | rows-in-prompt matched/crossed |
|---|---|---|---|---|---|---|
| ca | P1 | 0 / 1 | 29.75 / 29.58 | 29.77 / 30.02 | 1.00 / 1.01 | 13 / 8 |
| ca | P2 | 0 / 1 | 33.49 / 33.58 | 32.89 / 32.88 | 0.98 / 0.98 | 13 / 6 |
| es | P1 | 0 / 1 | 22.85 / 23.00 | 22.71 / 23.08 | 0.99 / 1.00 | 15 / 7 |
| es | P2 | 0 / 1 | 25.53 / 26.02 | 25.60 / 25.71 | 1.00 / 0.99 | 13 / 7 |

**Mean transfer ratio 0.996, min 0.98, max 1.01.** A ticket with only 6–8 of its
18 rows occurring in the evaluation prompt scores as well as one with 13–15.

The preregistration predicted that an interface ticket would lose clearly when
crossed. It does not. By the fixed verdict table this is the *"ticket identity
moves with template … but functional transfer stays good"* row → **HOLD**.

## 4. Added control (not preregistered): what is the functional core?

A ratio near 1 has two readings — the two tickets share a functional core, or
ticket identity does not matter at all. To separate them, the ticket was
replaced by random rows that are **not** in the template and are **matched
one-for-one on total training count**. Two variants; the second excludes BOS/EOS
from the sampling pool, because BOS occurs exactly once per example at a
perfectly constant position and is an interface token in all but name.

| variant | lang | seed | random Δ | real Δ | ratio | EOS rate | sampled `<s>` |
|---|---|---|---|---|---|---|---|
| A (BOS allowed) | ca | 0 / 1 | 28.94 / 29.21 | 29.75 / 29.58 | **0.97 / 0.99** | 1.00 | **yes** |
| A (BOS allowed) | es | 0 / 1 | 10.92 / 12.86 | 22.85 / 23.00 | 0.48 / 0.56 | 0.86–0.89 | no |
| B (BOS/EOS excluded) | ca | 0 / 1 | 12.03 / 12.00 | 29.75 / 29.58 | 0.40 / 0.41 | 0.83 | no |
| B (BOS/EOS excluded) | es | 0 / 1 | 11.86 / 13.58 | 22.85 / 23.00 | 0.52 / 0.59 | 0.88–0.90 | no |

Two things follow:

1. **Ticket identity does matter.** Count-matched non-template rows recover only
   **0.40–0.59**. So Layer 3's 0.996 is because the two tickets share a
   functional core, not because any 18 rows will do.
2. **Across all 8 runs, whether the random ticket happened to contain `<s>`
   separates 0.97–0.99 from 0.40–0.59 with no overlap.** A single input
   embedding row — one occurrence per example, constant position, no semantic
   content, no language identity — appears to carry most of the effect.

Point 2 is an observation across 8 runs with n=2 per cell, and it was **not**
preregistered. It is not used to change the verdict. A direct test (tune only
that one row) has not been run.

## 5. Verdict

| preregistered layer | result |
|---|---|
| Layer 1 — cross-language evaluation audit | **PASS** 3/3 |
| Layer 2 — selection factorial + frequency control | **PASS** 18/18 |
| Layer 3 — functional cross-template transfer | **FAIL** (ratio 0.996) |

Per the preregistered verdict table and the standing instruction — *E02 passes →
Main candidate; otherwise converge to Findings and do not reconstruct* — the
verdict is:

> **`HOLD / Findings`. L32 is not promoted to Main candidate.**

I am not rescuing this with the §4 control, which was added rather than
preregistered and which tests a different proposition from the one Layer 3 was
built to decide.

## 6. What the Findings paper says

The evidence chain is strong, reproduced across three language pairs, and uses
the parent's own published tickets:

1. A strict reproduction of the parent's headline (+29.50 [+28.59, +30.46] for
   en→ca).
2. Measurement audit before mechanism: 94–107% of that gain, in three language
   pairs, is termination. In one pair the translation content degrades.
3. Same-checkpoint causal gating (E01): the remaining adaptation is carried
   entirely by instruction-span occurrences — recovery 1.00 [0.98, 1.02] — and
   not at all by source occurrences (−0.00 [−0.01, 0.01]) despite *more*
   tuned-token occurrences there.
4. Selection is prompt-dependent beyond a seed ceiling, and survives a
   count-matched frequency control in 18/18 cells.
5. Function, however, is prompt-generic: tickets are interchangeable across
   templates (0.996), while count-matched non-template rows are not (0.40–0.59).

The honest one-line summary is a dissociation: **ticket *selection* is an
interface phenomenon; ticket *function* is carried by a small prompt-generic
structural core.** That is a real result and it is what the Findings paper should
claim — not "multilingual winning tickets are prompt artifacts", which Layer 3
does not support.

## 7. If it were ever reopened

The single-row test suggested by §4 — tune only the BOS embedding — is the
obvious next question and is cheap. It is deliberately **not** run here, because
the standing instruction on an E02 that does not pass is to converge rather than
reconstruct. It would need its own preregistration.
