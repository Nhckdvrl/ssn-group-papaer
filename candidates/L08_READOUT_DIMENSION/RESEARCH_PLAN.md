# L08 — Research Plan

**Candidate:** Low-Dimensional Readout Preserves Knowledge but Breaks Reasoning

---

## 1. Minimum decisive pilot

### Step 1 — exact reproduction
Models:
- Llama 3.1 8B;
- Qwen 2.5 7B.

Tasks:
- MMLU;
- SQuAD-v2;
- GSM8K.

Conditions:
- full;
- retain first half;
- retain last half;
- 3 random half masks.

Goal:
confirm the reported qualitative asymmetry.

### Step 2 — decisive decomposition
On ~200–500 GSM8K examples:
- free-running truncated generation;
- teacher-forced next-step evaluation under same mask;
- one-step truncation then full-readout restoration.

This already separates major accounts.

## 2. Pilot interpretation

### Outcome A
Teacher-forced next-step prediction collapses strongly.

Supports:
> reasoning requires high-dimensional local readout.

Next:
localize which steps/dimensions carry the load.

### Outcome B
Teacher-forced degradation is mild, free-running answer accuracy collapses.

Supports:
> autoregressive error accumulation.

Next:
model trajectory-divergence dynamics.

### Outcome C
Both vary by reasoning stage/task.

Supports:
> conditional bottleneck / task-specific geometry.

### Outcome D
Length-matched non-reasoning generation collapses similarly.

Then:
> the headline is not reasoning-specific.

Reconstruct toward autoregressive-generation sensitivity rather than kill automatically.

## 3. Phase 2 — accumulation curve

For each item measure:
- local KL change at step t;
- probability of first token divergence;
- downstream divergence after restoration;
- final answer success.

Fit:
> local perturbation size → probability of trajectory failure.

This provides a mechanism rather than an accuracy table.

## 4. Phase 3 — task-specific geometry

Estimate dimension importance under:
- factual QA;
- reading comprehension;
- reasoning.

Then test:
- mask learned/selected on task A applied to task B;
- shared vs task-specific dimension sets;
- whether reasoning sensitivity is distributed or concentrated.

Do not overclaim linear “reasoning neurons”; the quantity is causal readout contribution.

## 5. Phase 4 — alternative explanations

Mandatory falsification:
- length-matched generation;
- MC vs generative reasoning;
- baseline confidence matching;
- random-mask seeds;
- newer models.

## 6. Planned C1 → C2 → C3

### C1
Why does readout truncation preserve some capabilities but destroy others?

### C2
Which mechanism dominates?
- local high-dimensional signal;
- autoregressive accumulation;
- task-specific geometry;
- generic long-generation sensitivity.

### C3
How should NLP interpret “low-dimensional representations” and model compression?
> storage/readout redundancy is not automatically computational redundancy.

## 7. What kills the topic

KILL if:
- only GSM8K behaves differently and all controls point to benchmark artifact;
- the result is purely descriptive across masks;
- no causal decomposition can distinguish accounts;
- direct 2026 work is found that already answers the exact readout-vs-accumulation question.

## 8. Main-level requirements

Before mainline approval:
- ≥2 model families;
- ≥2 reasoning task families;
- teacher-forced/free-running decomposition;
- length/output-format falsification;
- mechanism-level causal intervention;
- consequence beyond “compression hurts reasoning.”

## 9. Paper skeleton

1. A striking established asymmetry.
2. Four competing explanations.
3. Controlled final-readout intervention.
4. Teacher-forcing decomposition.
5. Trajectory accumulation analysis.
6. Cross-task subspace/boundary.
7. Consequence for interpreting representation redundancy.

## Final pilot verdict

**PILOT-WORTHY AFTER ONE MORE DIRECT-NOVELTY CHECK.**
