# L08 — Minimum Decisive Pilot Card

**Candidate:** Low-Dimensional Readout Preserves Knowledge but Breaks Reasoning  
**Status:** SERIOUS / A-  
**Goal:** Explain the already-reported capability asymmetry instead of merely reproducing it.

## Established parent result
EMNLP 2025 reports that strong coordinate/dimension reduction at the final representation/readout can preserve much of MMLU/SQuAD performance while GSM8K collapses.

Our pilot must **not** claim this phenomenon as new.

## Competing explanations
1. **Single-step readout bottleneck** — reasoning next-token decisions intrinsically require more readout dimensions.
2. **Autoregressive accumulation** — each local prediction degrades only slightly, but free-running errors compound over a chain.
3. **Task-specific geometry** — knowledge/extraction and reasoning rely on differently distributed subspaces.
4. **Length/generation artifact** — long generation, not reasoning, explains the gap.

## Phase 1 — Exact reproduction
Reproduce the parent truncation/reduction setup on:
- one Qwen-family model;
- one Llama-family model if feasible;
- MMLU or closed-form knowledge QA;
- SQuAD/extraction;
- GSM8K;
- at least one **long non-reasoning generation control**.

Verify the cross-capability asymmetry before mechanism work.

## Phase 2 — Decisive teacher-forcing test
For reasoning examples compare:

### Free-running
Model consumes its own truncated outputs.

### Teacher-forced
At every step, feed the gold reasoning prefix but apply the same readout reduction to the next-token prediction.

Interpretation:
- teacher-forced next-step quality mostly preserved + free-running collapse → accumulation account;
- teacher-forced next-step quality also collapses → local readout bottleneck;
- mixed pattern → locate where the chain becomes dimension-sensitive.

## Phase 3 — Localized interventions
Test:
- truncation only on reasoning tokens;
- truncation only on final answer token;
- truncate one step then restore full readout;
- random coordinate removal vs random projection/subspace-preserving reduction;
- matched output-length non-reasoning tasks.

## Metrics
- task accuracy;
- next-token/gold-step accuracy under teacher forcing;
- KL/logit-margin change;
- first-error position;
- error growth with chain length;
- performance vs retained-dimension curve.

## Informative outcomes
### A — Accumulation
Reasoning is not intrinsically high-dimensional at each step; autoregression magnifies small readout damage.

### B — Local necessity
Reasoning decisions require a broader readout subspace than knowledge/extraction.

### C — Geometry
Specific dimensions/subspaces matter, not raw dimensionality.

### D — Length artifact
Long generation explains most of the effect; original “reasoning sensitivity” interpretation is wrong.

All are publishable if robust.

## Kill conditions
Kill if:
- the parent effect cannot be reproduced;
- a simple generation-length control fully explains the result with no broader consequence;
- the work reduces to another compression/pruning benchmark;
- no intervention distinguishes at least two plausible mechanisms.
