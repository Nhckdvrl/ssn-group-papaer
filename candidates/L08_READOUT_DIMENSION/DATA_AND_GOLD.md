# L08 — Data, Intervention, and Gold

**Core rule:** this is a causal mechanism paper. “Good data” means objective benchmark targets plus an intervention that isolates the proposed quantity; it does not require a provider-defined annotation ontology like L03.

---

## 1. Exact parent replication

Start from the causal-LM experiment in:
- https://aclanthology.org/2025.emnlp-main.1410/

Primary reproduction models:
- Llama 3.1 8B;
- Qwen 2.5 7B.

The original intervention reduces:
- final hidden representation dimensions;
- corresponding unembedding dimensions.

First reproduce the reported qualitative pattern before extending.

## 2. Core benchmark families

Use objective-gold tasks spanning different output/computation regimes.

### Knowledge / short decision
- MMLU or a clean MMLU subset;
- HellaSwag / comparable short multiple-choice task.

### Reading comprehension
- SQuAD-v2;
- optionally short extractive QA with objective spans.

### Multi-step reasoning
- GSM8K;
- one additional mathematical/logical reasoning dataset;
- one non-math multi-hop reasoning dataset if feasible.

### Length/control tasks
Construct or select:
- long but non-reasoning generation;
- reasoning with short final answer;
- multiple-choice reformulations of reasoning where valid.

Do not interpret “benchmark category” as gold for a psychological capability; it is an experimental factor.

## 3. Intervention family

Let h_t ∈ R^d be the final hidden state before unembedding.

Define masks M over dimensions and apply corresponding masked unembedding.

### A. Fraction curve
retain:
- 100%;
- 75%;
- 50%;
- 25%.

### B. Mask identity
- first half;
- last half;
- random dimensions with multiple fixed seeds;
- task-ranked high/low-importance dimensions where derived without test leakage.

### C. Temporal application
- truncate every generated token;
- truncate only one reasoning step;
- truncate only early steps;
- truncate only late steps;
- full readout restored after a single perturbed token.

## 4. Decisive teacher-forcing decomposition

For reasoning examples with gold/runnable solution traces:

### Free-running condition
Model generates its own chain under truncation.

### Teacher-forced condition
Feed the correct previous reasoning prefix and measure prediction of the next gold step/token.

Scientific quantity:
> **local next-step degradation conditional on correct history.**

If local degradation is small but final free-running accuracy collapses, this supports autoregressive accumulation.

Avoid relying on one exact gold CoT where multiple valid traces exist:
- use token likelihood / next-step answer variables where possible;
- use generated full-model reference traces as an auxiliary mechanistic condition, not semantic gold.

## 5. Primary metrics

### Task outcome
- benchmark accuracy/F1/exact match.

### Local readout damage
- KL divergence from full model;
- top-1 agreement;
- correct-token log probability;
- margin between correct and strongest competitor;
- entropy change.

### Trajectory drift
- first divergence step;
- divergence probability by step;
- recovery after restoring full readout;
- error growth vs generation length.

### Geometry
- performance under different masks;
- cross-task mask transfer;
- overlap of high-importance dimensions.

## 6. Critical controls

### Length control
Compare reasoning to non-reasoning outputs with matched token length.

### Output-format control
Compare free generation vs multiple-choice/short-answer variants where scientifically legitimate.

### Confidence/margin control
Match examples by full-model confidence to ensure reasoning tasks are not merely harder.

### Difficulty control
Stratify by baseline difficulty.

### Token-budget control
No test-time compute difference across masks.

## 7. Model expansion

After reproducing parent:
- one newer Qwen family model;
- one second architecture/family.

Do not begin with a huge zoo.

An open-weight model is mandatory for activation-level intervention.

## 8. Data/intervention validity kill conditions

KILL or reconstruct if:
- parent result cannot be reproduced;
- GSM8K collapse vanishes across reasonable masks/models and no systematic task distinction remains;
- length/output format explains essentially all of the asymmetry;
- teacher forcing does not identify a stable mechanism and the paper becomes descriptive;
- intervention changes more than final readout in a way that confounds computation.

## 9. Data Gate verdict

**YES.**

Objective benchmark labels + deterministic final-readout intervention directly support the causal estimands.
