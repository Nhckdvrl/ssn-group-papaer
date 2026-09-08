# L08 — Low-Dimensional Readout Preserves Knowledge but Breaks Reasoning

**Status:** SERIOUS CANDIDATE / A-  
**Paper mainline:** NOT APPROVED  
**Target:** NAACL Main  
**Canonical research package:** this directory  
**Last audited:** 2026-09-08

> **Plain-language thesis:** A model can lose half of its final representation dimensions and still answer many knowledge/QA tasks, yet the same intervention can almost destroy multi-step reasoning. The open question is why.

---

## 1. One-sentence research question

> Why can LLMs preserve factual/reading-comprehension performance under severe final-readout dimensional truncation while multi-step reasoning collapses—is reasoning genuinely more high-dimensional at each step, or does small per-token readout damage merely accumulate autoregressively?

Plain version:

> **Why can an LLM still answer what it knows after half its readout dimensions are removed, but can no longer reason?**

## 2. Established phenomenon

Takeshita et al. (EMNLP 2025, People’s Choice Award) study random dimensional truncation in text embeddings and include a causal-LM extension.

For Llama 3.1 8B and Qwen 2.5 7B, they remove half of the final hidden representation and corresponding unembedding dimensions.

Reported examples:
- Qwen MMLU: 0.718 → 0.709;
- Qwen SQuAD-v2: 50.12 → 50.07;
- Qwen GSM8K: 0.766 → 0.045 / 0.011 depending on which half is kept;
- Llama GSM8K: 0.764 → 0.009 / 0.014.

The paper explicitly notes that the LLM results are task-dependent and leaves dedicated study of the LLM case to future work.

Source:
- https://aclanthology.org/2025.emnlp-main.1410/

Therefore our project does **not** hunt for the phenomenon.

## 3. Why ACL / NLP cares

This asks a basic representation/computation question:

> Is the dimensional budget needed to **store/read out an answer** the same quantity as the dimensional budget needed to **sustain autoregressive computation**?

This matters beyond compression:
- what kind of information is present in final hidden states;
- why different NLP capabilities have different bottlenecks;
- whether “low-dimensional representation” claims imply “low-dimensional computation”;
- how to interpret pruning/compression results.

## 4. Competing accounts

### Account A — Reasoning needs genuinely higher-dimensional next-token signal

At each reasoning step, useful probability mass/margin depends on many dimensions.

Prediction:
- even under teacher forcing with the correct previous reasoning tokens, truncation badly harms next-step prediction;
- errors appear immediately rather than only after trajectory drift.

### Account B — Small local errors accumulate autoregressively

Single-step predictions remain mostly intact, but a small probability/margin shift changes one generated token, which changes future context and compounds.

Prediction:
- teacher-forced next-step quality remains much higher than free-running reasoning;
- truncating one step and restoring full readout causes limited damage compared with truncating the whole trajectory.

### Account C — Capability-specific readout geometry

Knowledge/reading tasks and reasoning tasks occupy differently distributed readout subspaces.

Prediction:
- sensitivity depends on which dimensions are removed, not only how many;
- task-specific masks/subspaces show systematic transfer or non-transfer.

### Account D — Evaluation/output-form artifact

GSM8K collapse may partly reflect long exact-match generation rather than reasoning per se.

Prediction:
- length-matched non-reasoning generation or multiple-choice reasoning exhibits similar sensitivity.

This is an important falsification route.

## 5. Outcome robustness

Any principled result is meaningful:

- A wins → reasoning next-token computation is intrinsically more readout-dimension hungry;
- B wins → “reasoning is high-dimensional” is the wrong interpretation; the bottleneck is sequential error accumulation;
- C wins → tasks rely on distinct output geometries;
- D explains much of the effect → the original capability interpretation is overstated.

The paper exists even if the headline GSM8K gap shrinks on newer models.

## 6. Paper identity

**Primary identity:** causal representation/computation attribution.

**Not the identity:**
- another compression method;
- efficient inference;
- “reasoning is fragile”;
- a GSM8K benchmark study;
- generic intrinsic dimensionality probing.

## 7. Planned C1 → C2 → C3

### C1 — Reproduce and generalize
Map dimensional-truncation sensitivity across several task families and model families.

### C2 — Explain
Separate:
- single-step readout damage;
- autoregressive accumulation;
- task-specific geometry;
- generation-length/output-format effects.

### C3 — Consequence
Clarify what “representation redundancy” means for LLM capabilities and how future compression/interpretability work should distinguish:
> information/readout capacity vs sequential computation capacity.

## 8. Five hard gates

| Gate | Verdict | Why |
|---|---|---|
| REAL OBJECT | **YES** | The intervention and cross-task asymmetry are already reported in an award Main paper. |
| SCIENTIFIC TENSION | **YES** | Several plausible mechanisms make different predictions. |
| GOOD DATA | **YES** | Public benchmarks provide objective gold; intervention is deterministic. |
| PAPER-LEVEL NOVELTY | **YES, fragile** | Parent reports the LLM phenomenon but does not explain the reasoning-vs-nonreasoning asymmetry. |
| OUTCOME-ROBUST DECISIVENESS | **YES** | Different mechanisms lead to distinct conclusions even if the gap changes by model/task. |

## 9. Main danger

Reviewer compression:

> **“This is just the EMNLP 2025 dimension-removal paper with more LLM benchmarks.”**

That compression wins if we merely add models/tasks.

The candidate lives only if the decisive contribution is:
> **causally separating per-step representation requirements from autoregressive error accumulation and task-specific readout geometry.**

## 10. Directory map

- [RELATED_WORK_AND_NOVELTY.md](RELATED_WORK_AND_NOVELTY.md)
- [DATA_AND_GOLD.md](DATA_AND_GOLD.md)
- [RESEARCH_PLAN.md](RESEARCH_PLAN.md)
