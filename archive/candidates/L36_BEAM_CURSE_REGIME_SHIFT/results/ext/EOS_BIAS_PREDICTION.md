# Pre-registered prediction for the EOS-bias dose-response (written before the runs)

**Date:** 2026-09-14, after the termination-geometry measurement, before any biased generation.
**Status:** exploratory extension (E00-EXT), outside the pre-registered E00 gate.

## Measured starting point

Mean log-probability that the model stops immediately (empty translation), given the source:

| system | `log p(stop at step 0)` | `log p(greedy output)` | empty beats greedy |
|---|---|---|---|
| `facebook/wmt19-en-de` (2019 NMT) | **−9.31** | −18.88 | **61.6%** of segments |
| `google/gemma-3-12b-it` (instruction-tuned LLM) | **−35.33** | −23.02 | **2.3%** of segments |

Gap: **26.0 nats**.

On the classic system, `log p(stop at step 0)` predicts which segments collapse to an empty
hypothesis at beam 64 (logit pseudo-R² 0.176, β = +1.30, p = 1.7e-48), while the frozen
uncertainty `u` predicts nothing (pseudo-R² 0.002, p = 0.10) and adds nothing on top of
termination geometry (p = 0.66).

## Prediction

If termination geometry — not intrinsic uncertainty — is what removed the beam-search curse in the
LLM regime, then adding a constant bias `b` to the LLM's end-of-sequence logits at every step
should move the curse back, monotonically in `b`, with the classic collapse rate recovered near
`b ≈ 26` (where the LLM's stopping probability matches the 2019 system's):

1. `b = 0`: no collapse at beam 64 (empty rate ≈ 0, length ratio ≈ 1);
2. `b = 13`: little or no collapse;
3. `b = 26`: empty/short collapse appears, order-of-magnitude comparable to the classic 13.1%
   at beam 64, and corpus BLEU drops materially versus beam 4;
4. `b = 39`: collapse stronger still.

Falsifier: if BLEU and the empty rate are unchanged at `b = 26` and `b = 39`, then stopping
probability is **not** the operative variable and the classic/modern difference must be sought
elsewhere (e.g. the shape of the whole length distribution, not the stop decision).

Grid: first 400 segments of `newstest2019` (fixed prefix), beam 64, RAW (`length_penalty = 0`),
everything else identical to the E00 generation contract.
