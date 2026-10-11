# L11 Implementation, Data, and Estimator Audit

**Date:** 2026-09-09

## Parent Fidelity

- Parent stack: verl + GRPO/RLVR; instruction-tuned Qwen2.5-3B/7B and Llama-3.2-3B.
- Selected checkpoint: `Qwen/Qwen2.5-7B-Instruct`, an exact parent model family/scale.
- Selected pair: Arithmetic and MATH-style problems, matching the parent's clean same-domain contrast.
- Parent reward: `-0.1` missing answer tag, `0.1` formatted wrong answer, `1.0` correct. Pilot matches it.
- Parent policy loss is token-averaged. Pilot records and uses response-token mean before rollout averaging.
- Parent GRPO advantages are empirical group mean centered and normalized. Pilot uses four rollouts per prompt and records the normalized values.
- Parent reports gradient clipping 1.0 for training. No optimizer update is made in E01/E02, so clipping is disabled and explicitly recorded; estimator values are pre-clip.

## Gradient Estimator

The naive batch squared norm is upward biased by gradient variance. The parent splits a batch into independent halves and estimates `||g||^2` with `<g_hat_1, g_hat_2>`, then tracks an EMA. The pilot uses prompt-disjoint even/odd halves and this cross-product on the full final transformer block. A single pilot checkpoint has no EMA and is therefore noisier than the parent training curve.

For per-rollout anatomy, the pilot uses a deterministic every-256th-coordinate sketch of the final self-attention gradient, scaled by the square root of the stride. This keeps the Gram computation tractable. The proxy must preserve the aggregate task ordering before it can localize the source; it is not silently substituted for the primary full-block estimator.

## Data Validity

- Arithmetic prompts are deterministic, generated with a recorded seed, and evaluated by numeric equality.
- MATH-500 examples are a deterministic prefix after preregistered filters: numeric final answer and prompt length under 700 characters.
- This numeric-only subset is a feasibility sample, not a representative MATH estimate.
- Train prompt groups and held-out prompts are disjoint by ID.
- Unit of analysis is the prompt group, not an individual token or rollout.

## Current Limitation

The first run is a local checkpoint anatomy, not a 100-step parent learning curve. It can reproduce task-gradient contrast and route a mechanism experiment; it cannot alone establish the long-horizon gradient/gain mismatch.

## Fidelity Repair E01a -> E01b

The initial 192-token run had 100% cap hits. This made missing-format reward and advantage support task-dependent, so its apparent Arithmetic/MATH contrast is not scientifically interpretable. E01b raises only `max_new_tokens` to 512 and trims EOS padding before token-mean loss computation. The invalid raw run remains archived rather than deleted.
