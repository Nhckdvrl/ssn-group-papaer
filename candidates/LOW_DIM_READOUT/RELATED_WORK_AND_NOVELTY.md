# Low-Dimensional Readout — Related Work and Novelty

## 1. Parent ownership

Takeshita et al., EMNLP 2025 owns:
- random/coordinate dimension removal as the phenomenon;
- strong robustness of text embeddings under 50% dimension removal;
- degrading dimensions in retrieval/classification;
- initial causal-LM evidence showing task-dependent robustness;
- the striking MMLU/SQuAD vs GSM8K contrast.

Source: https://aclanthology.org/2025.emnlp-main.1410/

We therefore cannot claim:
- high-dimensional representations are redundant;
- 50% truncation often preserves performance;
- GSM8K is more fragile than MMLU/SQuAD under this intervention.

## 2. Neighboring modern work

Recent work studies:
- intrinsic dimensionality of task/reasoning representations;
- low-dimensional task subspaces;
- pruning/compression of reasoning models;
- hidden-state probes of reasoning trajectories.

These are close but not equivalent if they do not identify why a **final readout intervention** selectively destroys free multi-step generation.

## 3. Surviving paper identity

The proposed paper asks:

> Is the observed reasoning collapse caused by richer per-step information requirements, autoregressive accumulation of tiny readout errors, or task-specific readout geometry?

The novelty lies in a causal decomposition that separates:
- representation content at one step;
- repeated use of degraded token decisions;
- subspace geometry.

## 4. Reviewer compression

### Attack A
> “Takeshita et al. 2025, but more GSM8K experiments.”

Fatal if true. We need interventions the parent did not use: teacher forcing, local truncation/restoration, length-matched controls, rationale-only vs answer-only intervention.

### Attack B
> “Another intrinsic-dimension paper.”

We are not estimating the smallest dimensional subspace that decodes task labels. We are testing **causal functional necessity at the LM readout during generation**.

### Attack C
> “Another model compression paper.”

No efficiency contribution is required. Parameter count and internal computation remain unchanged; the target is scientific attribution.

## 5. Exact kill collision

KILL if a prior paper already performs a comparable readout truncation and causally separates teacher-forced next-step fragility from free-generation error accumulation across knowledge and reasoning tasks.

## 6. Current verdict

**NOVELTY: PASS / fragile to direct 2026 mechanism work.**

The paper must resolve the mechanism, not merely characterize the phenomenon more thoroughly.