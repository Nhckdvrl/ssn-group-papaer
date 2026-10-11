# L11 Claim Ledger

**Updated:** 2026-09-09

## Current RQ

Why can one objectively verified reasoning task induce a much larger policy gradient than another without a commensurately larger local learning gain, and which part of the score-function update creates that loudness?

## Claims

| ID | Claim | Role | Nearest owner | Evidence | Status |
|---|---|---|---|---|---|
| L11-C0 | Multi-task RLVR task gradients can be severely imbalanced and need not track learning gain. | Established parent, not ours | Wu et al. (2026) | Parent paper | Established prior |
| L11-C1 | In a parent-compatible Arithmetic/MATH pilot, the gradient/gain mismatch is reproducible after auditing reward, advantage, length, normalization, clipping, and estimator choices. | Feasibility gate | Wu et al. (2026) | L11-E01a-c | Weakened: not stable at micro-pilot scale |
| L11-C2 | The observed task loudness can be localized to individual score sensitivity, directional aggregation, or a measured mixture of the two. | Core explanatory claim | No paper currently owns this LLM-level decomposition | L11-E02 | Unresolved; coherence is a routing candidate only |
| L11-C3 | Raw parameter-gradient contrast and held-out policy movement are materially miscalibrated across tasks. | Measurement consequence | Generic Fisher/natural-gradient work owns the general fact | L11-E03 | Not tested because E01 gate failed |

No mechanism claim is supported by the completed micro-pilot. Correlation or an attention-block proxy alone will not promote L11-C2 or L11-C3.

## Current Paper Identity

Established gradient/gain paradox -> identify the source of task loudness in an LLM policy-gradient computation -> intervene on that source -> show the consequence for function-space pressure and task mixing.
