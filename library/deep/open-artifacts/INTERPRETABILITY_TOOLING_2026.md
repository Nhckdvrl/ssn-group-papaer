# Interpretability Open Artifacts / Tooling Map (2026)

**Last verified:** 2026-09-29  
**Purpose:** choose instruments for workbench experiments; artifact availability is not itself a research idea.

## Core intervention / tracing stacks

| Artifact | Use | Notes |
|---|---|---|
| https://github.com/TransformerLensOrg/TransformerLens | hooks, cache, activation patching, logit-lens-style analysis on transformer LMs | mature default for small/open decoder-only MI |
| https://github.com/ndif-team/nnsight | intervention/tracing API | useful when TransformerLens model support is limiting |
| https://github.com/ndif-team/ndif | remote/distributed inference infrastructure for NNsight-style intervention | useful for larger models if supported |
| https://github.com/frankaging/pyvene | reusable intervention / representation-engineering framework | includes causal interventions and DAS-family workflows |
| https://github.com/decoderesearch/circuit-tracer | attribution-graph / circuit tracing tooling | open implementation around transcoders / attribution graphs; use as instrument, not proof by itself |

## Sparse feature / dictionary-learning stack

| Artifact | Use | Notes |
|---|---|---|
| https://github.com/decoderesearch/SAELens | train/load/analyze SAEs | broad practical SAE stack |
| https://github.com/adamkarvonen/SAEBench | standardized SAE evaluation | 200+ released SAEs / multiple metrics; strong baseline before any new SAE claim |
| https://www.neuronpedia.org/ | inspect features, auto-explanations, SAE resources | useful for exploration; natural-language labels are hypotheses, not ground truth |

## Standardized MI evaluation

| Artifact | Use | Notes |
|---|---|---|
| https://github.com/aaronmueller/MIB | circuit localization + causal-variable localization benchmark | best current general starting point for comparing MI techniques |
| https://github.com/densutter/non-linear-representation-dilemma | reproduce linear/nonlinear causal-alignment vacuity experiments | crucial negative-control substrate |
| https://github.com/MelouxM/CAE | causal-abstraction validity metrics and simulated systems with known valid/invalid abstractions | useful ground-truth rung; ICML 2026 MI workshop spotlight, not itself a real-LLM benchmark |
| https://github.com/google-deepmind/tracr | compile known RASP programs into transformers | valuable model organism with known mechanism; should not be sole evidence for an LLM claim |

## Model diffing

### science-of-finetuning diffing toolkit
https://github.com/science-of-finetuning/diffing-toolkit

This is currently the most useful open workbench substrate for model-diffing research.

It supports multiple methods in one harness, including:
- Activation Difference Lens / activation analysis;
- KL / output comparisons;
- PCA;
- SAE difference;
- crosscoder;
- Diff Mining;
- weight amplification;
- agentic evaluation of what a method reveals about the finetune.

Important because it lets us ask a **measurement question** with strong common baselines rather than implementing every method independently.

Associated strong parent:
**Narrow Finetuning Leaves Clearly Readable Traces in Activation Differences**, ICLR 2026.

### Crosscoder cautions / baselines

- NeurIPS 2025: **Overcoming Sparsity Artifacts in Crosscoders to Interpret Chat-Tuning**  
  https://papers.nips.cc/paper_files/paper/2025/hash/9902a53031ebbbab73898028073d4790-Abstract-Conference.html
- Cross-architecture DFC (2026): https://arxiv.org/abs/2602.11729
- Delta-Crosscoder (2026): https://arxiv.org/abs/2603.04426
- Diff Mining (Aug 2026): https://arxiv.org/abs/2608.26462

A model-diffing experiment should always include a cheap non-internal baseline: direct behavior querying and/or logit difference.

## Current artifact ladder for a reliability workbench

A useful progression is:

1. **known-mechanism system** — Tracr / controlled synthetic system;
2. **standard MI benchmark** — MIB tasks/models;
3. **model organism with known training change** — science-of-finetuning organisms;
4. **realistic broader fine-tune / public model pair** — requires separate selection and stronger external-validity checks.

Do not stop at rung 1 or 3.

## Compute notes

The planned directions do not require frontier-model training.

- MIB / DAS / patching can begin on GPT-2/Pythia-scale models.
- Crosscoder/SAE training can be expensive in activation storage but is feasible on local A100 / RTX PRO 6000-class GPUs at 1B–9B scale.
- The science-of-finetuning toolkit already includes smaller model organisms and multi-method harnesses, so the first milestone should be reproduction + baseline comparison, not large-model scaling.
- Scaling to 8B/9B should happen only after a clear information-gain experiment survives on smaller models.

## Tool-selection rule

Choose the instrument from the scientific claim:

- “where?” → localization / circuit tools;
- “is variable X causally exchangeable?” → DAS / interchange interventions;
- “what sparse decomposition is useful?” → SAE + SAEBench metrics;
- “what changed after training?” → model diffing;
- “does the explanation survive intervention?” → causal abstraction / held-out interventions;
- “does it help a downstream decision?” → actionability evaluation.

Never reverse this order by choosing a trendy tool first and then searching for a behavior to explain.
