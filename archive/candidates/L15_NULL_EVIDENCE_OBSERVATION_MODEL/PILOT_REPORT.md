# L15 — Bounded Pilot Report (E01/E02)

**Date:** 2026-09-11
**Verdict:** **KILL / NO-GO.** Both preregistered kill conditions fired, in both model families.
**E03 was not run:** it is conditional on E02 showing an integration gap. There is none.

## What was run

2,982 prompt cells per model over the frozen primary grid (180 items = 12 scenarios ×
priors {.2,.5,.8} × sensitivities {.05,.25,.50,.75,.95}, `f=0`), seven preregistered
conditions × two answer modes × two null wordings. Greedy decoding, `seed=0`.
`cot` is the primary mode for the kill decision (`EXPERIMENTS.md`).

| model | cells | wall clock | raw |
|---|---:|---:|---|
| Qwen/Qwen3-32B (`enable_thinking=False`) | 2,982 | 463 s | `results/pilot_v1/qwen3_32b/raw.jsonl` |
| mistralai/Mistral-Small-24B-Instruct-2501 | 2,982 | 254 s | `results/pilot_v1/mistral_small_24b/raw.jsonl` |

Answer coverage was 0.983–1.000 in every condition; no condition lost data in a way that
could hide an effect.

## Primary mode (`cot`): the phenomenon does not exist

| metric (P2_NULL unless noted) | Qwen3-32B | Mistral-Small-24B | kill threshold |
|---|---:|---:|---|
| MAE vs analytic gold | **0.0035** | **0.0074** | — |
| mean Spearman vs gold across `s` | **0.989** [0.967, 1.000] | **0.945** [0.868, 1.000] | kill if ≥ .80 |
| compression ratio (observed range ÷ gold range) | **0.985** [0.957, 0.999] | **0.929** [0.832, 0.999] | kill if ≥ .70 |
| adjacent monotonicity violations | 1/288 | 5/288 | — |
| obs-known rate (Err_obs ≤ .05) | 1.000 | 1.000 | — |
| **KNI rate** | **0.003** [0.000, 0.008] | **0.014** [0.000, 0.033] | — |
| P2_POS (f=0 sanity, gold 1.0) MAE | 0.0000 | 0.0000 | — |
| P2_ARITH MAE | 0.0018 | 0.0018 | — |
| P0_PRIOR MAE | 0.0000 | 0.0000 | — |
| P3 decision accuracy | 0.918 | 0.858 | — |

CIs are 95% percentile bootstrap resampling **scenarios**, the independent unit.

Both families, when allowed to reason normally, scale the same visible null observation
with stated counterfactual detectability essentially exactly: the posterior moves across
the full normative range (.4872 → .0476 at `p=.5`), in the right order, with an error
two orders of magnitude below the KNI threshold. The competence–integration dissociation
that the route exists to sell is absent: `P1 correct ∧ P2 wrong` occurs in 0.3% and 1.4%
of items, and is not concentrated in any frame.

**Preregistered kill condition 1 fires on both families.**

## `direct` mode is a different failure, and not ours

| metric | Qwen3-32B | Mistral-Small-24B |
|---|---:|---:|
| P2_NULL MAE | 0.2082 | 0.2557 |
| KNI rate | 0.489 | 0.678 |
| mean Spearman vs gold | −0.034 | −0.193 |
| **P2_POS MAE (gold 1.0, f=0)** | **0.1467** | **0.1863** |
| P2_ARITH MAE | 0.2344 | 0.2063 |
| framed MAE − arithmetic MAE (paired cells) | **−0.026** | **+0.049** |
| P0_PRIOR MAE | 0.0000 | 0.0000 |

Three controls kill the direct-mode reading:

1. **The positive counterpart fails too.** With `f=0`, a detection makes `P(H|D)=1` by
   construction. Both models miss it by .15–.19. A model that has not read the generative
   process at all cannot be evidence of a *null-specific* integration failure.
2. **The arithmetic control fails by the same amount.** `framed − arith` is −0.03 / +0.05:
   the deficit is not created by the natural framing or by the null surface. This is
   **preregistered kill condition 2**.
3. **Prior-only is perfect (MAE 0.0000) in both modes.** The models read the item; they
   simply do not run the computation when no tokens are allowed for it.

Answer-content diagnosis on the same data: in `direct` mode the modal P2_NULL answer is
not the gold and not the prior — it is scattered, with the single largest identifiable
family being an echo of the stated sensitivity `s` itself (16% Qwen, 4% Mistral; 39% /
72% match none of {`s`, `1-s`, `p`, gold, `p(1-s)`}). In `cot` mode both models land on
gold ~100% of the time.

## What this does and does not license

The one-line takeaway from the data is:

> "Capable open models compute observation-conditioned null-evidence posteriors correctly
> when given room to compute, and answer near-arbitrarily when not — including on positive
> evidence and on bare arithmetic."

That is **not** the locked L15 claim, and it is not a fallback identity. Turning it into
"LLMs need explicit reasoning to use observation models" would be exactly the mutation the
workflow forbids: a new paper identity, inheriting an approval it never earned, landing
inside generic chain-of-thought, Bayesian elicitation, and reasoning-improves-calibration
literature.

Nor does Mistral's slightly weaker `cot` numbers (compression .929 vs .985) license a
model-heterogeneity paper. Both families pass every threshold; the gap is a capability
difference, not a dissociation.

## Limitations, stated rather than used as rescue

- `P1_NULL` is close to a reading-comprehension floor, because `1-s` is printed in the
  item. That was deliberate (it establishes the competence side of the dissociation) and
  it makes the `cot` result *stronger*, not weaker: the knowledge is demonstrably present
  and it is demonstrably used.
- `f=0` makes the positive counterpart degenerate at 1.0. It still functioned as a sanity
  control and it is what exposed the direct-mode failure as non-specific.
- Only two families and one scale band were run. Under the pilot card this is correct:
  a model zoo was not authorized, and no amount of extra models converts a
  near-zero KNI rate into a phenomenon.

## Decision

**ARCHIVED / NO-GO.** Recorded as **K183** in `failed/KILLED_LEDGER.md`.
Data, prompts, gold, scorers and raw generations remain in this package for reuse under a
genuinely new paper identity that passes selection independently.
