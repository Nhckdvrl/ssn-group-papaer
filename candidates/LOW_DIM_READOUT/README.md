# Low-Dimensional Readout Preserves Knowledge but Breaks Reasoning

**Status:** SERIOUS CANDIDATE / A-  
**Paper mainline:** NOT APPROVED  
**Target:** NAACL Main  
**Last audited:** 2026-09-08

> **Plain-language thesis:** Removing half of the dimensions used for next-token prediction barely hurts some knowledge/QA tasks, yet can destroy multi-step reasoning. The key question is why.

## 1. One-sentence research question

> **Why can an LLM still answer what it knows after a large fraction of its final readout dimensions are removed, but fail to carry out multi-step reasoning?**

## 2. Established phenomenon

EMNLP 2025 *Randomly Removing 50% of Dimensions in Text Embeddings has Minimal Impact on Retrieval and Classification Tasks* extends dimension truncation to causal LMs. For Llama and Qwen, MMLU/SQuAD performance remains largely preserved under 50% truncation, while GSM8K collapses dramatically.

This phenomenon is already established; we do not need to gamble on discovering it.

Source: https://aclanthology.org/2025.emnlp-main.1410/

## 3. Natural scientific tension

Three explanations are all plausible:

### Account A — Intrinsically higher-dimensional next-step information
Reasoning tokens require a richer final representation than factual/QA outputs.

### Account B — Autoregressive error accumulation
Each truncated next-token prediction is only slightly worse, but small deviations compound over many generated reasoning steps.

### Account C — Task-specific readout geometry
Knowledge, extraction, and reasoning depend on different subspaces; random truncation happens to preserve some capabilities but destroys others.

These explanations imply different conclusions about what LLM representations are doing.

## 4. Why ACL / NLP cares

This is not a compression paper. It asks where a capability bottleneck lives:
- in the information represented at a single step;
- in repeated autoregressive use of a slightly degraded readout;
- or in task-specific geometry.

That changes how we interpret probing, dimensionality, reasoning representations, and readout interventions.

## 5. Outcome robustness

- teacher forcing repairs GSM8K -> accumulation account;
- teacher forcing does not repair -> single-step representation/readout account;
- random projection and coordinate deletion differ -> geometry account;
- only reasoning-token truncation is harmful -> computation-specific boundary;
- long non-reasoning generation collapses similarly -> length/accumulation, not reasoning per se.

Every major result answers the scientific question.

## 6. Paper identity

**Primary identity:** causal representation/readout attribution paper.

**Not:**
- another pruning/compression method;
- another intrinsic-dimension estimate;
- a GSM8K robustness benchmark;
- “reasoning needs more dimensions” without mechanism.

## 7. C1 → C2 → C3

### C1
Replicate capability-selective truncation across model families and task families.

### C2
Use teacher forcing, step-local truncation, restoration, sequence-length controls, and subspace interventions to distinguish the three accounts.

### C3
State when low-dimensional readout is a valid proxy for retained capability and when it fundamentally mismeasures generative computation.

## 8. Five hard gates

| Gate | Verdict | Why |
|---|---|---|
| REAL OBJECT | **YES** | Capability-selective readout fragility is already empirically established. |
| SCIENTIFIC TENSION | **YES** | At least three plausible mechanisms make distinct predictions. |
| GOOD DATA | **YES** | Standard tasks have direct task gold; intervention is exact and controlled. |
| PAPER-LEVEL NOVELTY | **PROVISIONAL YES** | Parent paper establishes the phenomenon but does not resolve single-step vs autoregressive vs geometry mechanisms. |
| OUTCOME-ROBUST | **YES** | Every account yields a substantive interpretation. |

## 9. Main danger

> **“This is just a mechanistic follow-up to Takeshita et al. 2025.”**

That attack wins if we merely add more tasks or probes. It loses only if we deliver a decisive causal decomposition and a broader conclusion about representation capacity vs generative computation.

## 10. Directory map
- `DATA_AND_GOLD.md`
- `RELATED_WORK_AND_NOVELTY.md`
- `PILOT_CARD.md`
