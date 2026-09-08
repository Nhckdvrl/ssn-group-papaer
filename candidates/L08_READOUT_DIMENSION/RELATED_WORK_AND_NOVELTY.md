# L08 — Related Work and Paper-Level Novelty

**Candidate:** Low-Dimensional Readout Preserves Knowledge but Breaks Reasoning

---

## 1. Direct parent — EMNLP 2025 People’s Choice

Takeshita et al., **“Randomly Removing 50% of Dimensions in Text Embeddings has Minimal Impact on Retrieval and Classification Tasks”**:
- 6 text encoders;
- 26 embedding tasks;
- up to 50% random dimension removal with <10% drop on many retrieval/classification tasks;
- identifies many “degrading dimensions” for text embeddings;
- includes Llama 3.1 8B and Qwen 2.5 7B causal-LM experiments;
- reports severe task dependence, including near-collapse on GSM8K;
- explicitly says dedicated study of the LLM case is future work.

Source:
- https://aclanthology.org/2025.emnlp-main.1410/

What it owns:
- the dimension-removal phenomenon;
- degrading dimensions in text embeddings;
- the first causal-LM observation;
- the statement that LLM sensitivity is task dependent.

We cannot claim any of these as new.

## 2. Compression/pruning neighborhood

ICLR 2026 **“When Reasoning Meets Compression”** studies quantization/distillation/pruning of reasoning models and mechanistically localizes compression-sensitive weights.

It reports, among other findings, that weight count can hurt knowledge memorization more than reasoning.

Source:
- https://proceedings.iclr.cc/paper_files/paper/2026/hash/665654759cdf2114c0cbe2b8e501e00e-Abstract-Conference.html

This is useful because it shows:
> compression location matters.

It does **not** answer our question:
- weight compression changes model parameters/computation;
- our intervention changes the final hidden-to-vocabulary readout channel while leaving transformer weights/computation intact.

The potentially opposite knowledge-vs-reasoning patterns strengthen the question rather than collide with it.

## 3. Reasoning-token compression/pruning

ACL 2026 contains multiple papers on:
- pruning redundant CoT;
- identifying functionally important reasoning tokens;
- reducing reasoning length;
- pruning reasoning models.

Examples:
- https://aclanthology.org/2026.acl-long.25/
- https://aclanthology.org/2026.acl-long.1419/
- https://proceedings.iclr.cc/paper_files/paper/2026/hash/e70ffb3f05096e62b5077d8e1b62e668-Abstract-Conference.html

These own:
- CoT token importance;
- efficiency-oriented reasoning compression;
- weight-level reasoning pruning.

They do not own:
> final-readout dimensional bottleneck vs autoregressive accumulation.

## 4. Representation / subspace work

A broad literature studies:
- linear probes;
- low-dimensional task subspaces;
- safety/alignment directions;
- intrinsic dimensionality.

Example:
- ICML 2025 “The Hidden Dimensions of LLM Alignment” studies multi-dimensional safety directions.

Source:
- https://proceedings.mlr.press/v267/pan25f.html

These works show that capabilities can be represented in structured subspaces, but do not establish our cross-capability readout necessity question.

## 5. New paper-level story

The paper must own:

1. established final-readout truncation creates large cross-capability differences;
2. “reasoning needs more dimensions” is only one explanation;
3. matched teacher-forced/free-running interventions separate local readout loss from sequential accumulation;
4. dimension-selection transfer tests task-specific geometry;
5. length/output-format controls test whether the effect is really reasoning-specific;
6. conclusion clarifies the relation between low-dimensional representation and autoregressive computation.

## 6. Reviewer compression

### Attack 1
> “EMNLP 2025 plus more benchmarks.”

Fatal if true.

### Attack 2
> “Another reasoning compression paper.”

Rebuttal:
> no parameter pruning or efficiency objective; the target is where capability bottlenecks live.

### Attack 3
> “GSM8K exact-match is just long generation.”

This is a serious scientific alternative, not a nuisance.

The paper must test:
- teacher forcing;
- length-matched generation;
- multiple-choice/short-answer variants;
- token-level KL/margin.

If generation length explains everything, that is still a valid corrective conclusion but the paper may need reconstruction in scope.

## 7. Kill-level collision definition

KILL if a paper already:
- performs the same final hidden/unembedding dimensional intervention;
- compares reasoning vs knowledge/QA;
- separates teacher-forced local degradation from free-running accumulation;
- tests dimension/subspace transfer;
- and reaches the same capability-bottleneck conclusion.

Generic pruning/intrinsic-dimension work does not kill.

## 8. Top-conference alignment

Strong alignment comes from:
- starting from a surprising established Main/award result;
- asking a simple mechanism question;
- using causal intervention rather than correlation;
- allowing competing explanations and a corrective result.

This resembles strong mechanistic Main papers more than an efficiency benchmark.

## 9. Current verdict

**SERIOUS / A-.**

Novelty is real only if the study explains the asymmetry, not if it maps more truncation curves.
