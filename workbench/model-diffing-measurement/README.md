# Model Diffing as Measurement — Workbench

**Lane:** our-taste  
**Status:** **DEMOTED 2026-09-29 — knowledge asset, do not execute as the current mother question**  
**Created:** 2026-09-29

## 0. Demotion note — nearest-prior collision

A deeper 2026 ownership audit found a direct parent that was missed when this workbench was opened:

**Simple LLM Baselines are Competitive for Model Diffing** (Kempf et al., 2026; SciForDL / arXiv 2602.10371) already:
- asks how model-diffing methods should be evaluated;
- defines desiderata for **generalization, interestingness, and abstraction**;
- performs a systematic head-to-head comparison between simple LLM-based diffing and SAE-based model diffing;
- finds the simple LLM baseline competitive overall and often more abstract.

Together with **Narrow Finetuning Leaves Clearly Readable Traces in Activation Differences** and **Diff Mining**, this directly compresses the broad mother question originally registered here:

> when does internal model diffing provide incremental information beyond simpler external / activation / logit baselines?

Running the original plan across more model pairs, access levels, or realistic regimes would currently risk becoming an extension of an already active lineage rather than an independent top-conference-scale scientific object.

**Do not execute the baseline plan below as an active workbench.** It is preserved as a reusable map of model-diffing baselines and evaluation pitfalls. Reopen only if a genuinely different scientific object emerges that cannot be reviewer-compressed to comparative model-diff evaluation.

---

## 0. Original territory (historical)

This workbench studies **model diffing as a measurement instrument**:

> when two language models differ because of fine-tuning, post-training, or a model update, what kinds of changes can different diffing instruments actually recover, and when does access to model internals add information beyond simple behavior / logit / activation-difference baselines?

This is deliberately **not**:
- “invent another crosscoder”;
- “find a weird fine-tuned behavior and interpret it”;
- “prove internals are better than black-box evaluation”;
- a pre-registered claim that any current model-diffing method is broken.

The initial object is the **measurement regime**. The eventual paper identity is allowed to change completely after baseline residency.

---

## 1. Why this territory is worth inhabiting

Model diffing has become a serious interpretability primitive: instead of interpreting a model from scratch, compare a base model with an updated/fine-tuned model and ask what changed.

By 2025–2026, however, several strong results put pressure on the default story.

### Parent / pressure A — learned diff features can contain artifacts

**Overcoming Sparsity Artifacts in Crosscoders to Interpret Chat-Tuning** (NeurIPS 2025)

Standard L1 crosscoders can misattribute concepts as fine-tune-specific even when they exist in both models. BatchTopK-style fixes substantially change the result.

Implication:

> “model-specific latent” is not automatically “behavior introduced by training”.

### Parent / pressure B — simple activation differences are unexpectedly strong

**Narrow Finetuning Leaves Clearly Readable Traces in Activation Differences** (ICLR 2026)

A simple Activation Difference Lens can recover the format/content of narrow fine-tuning objectives from unrelated text, across multiple model families/scales. The same work warns that narrow model organisms may be unrealistically easy because the fine-tuning objective becomes globally salient in activations.

Implication:

> a sophisticated model-diff method can look impressive because the experimental substrate leaks the training objective everywhere.

### Parent / pressure C — crosscoders are rapidly improving

2026 work includes:
- Dedicated Feature Crosscoders for cross-architecture model diffing;
- Delta-Crosscoder for narrow fine-tuning regimes.

These are strong method parents, not empty literature cells for us to fill.

### Parent / pressure D — a cheap output baseline is now competitive or better

**Diff Mining: Logit Differences Reveal Finetuning Objectives** (Aug 2026)

Direct differences in output logits, aggregated with simple methods, outperform state-of-the-art model-diffing methods on some finetune-objective discovery evaluations and scale without internal access.

This creates the most important current pressure:

> **What is the comparative advantage of internal model diffing?**

If the same changed behavior is already visible in logits or ordinary querying, internal decomposition must justify its extra complexity by discovering, localizing, predicting, or controlling something the cheap baseline cannot.

---

## 2. Top-conference ceiling

Local substrate:

> science-of-finetuning model organisms + open diffing toolkit.

Broader object:

> **the validity and comparative value of model-diffing measurements across different kinds of model change.**

Possible field-level consequence:

> change how model-diff methods are evaluated; identify regimes where internal methods are genuinely necessary or where current benchmarks systematically overstate their value; expose a load-bearing failure that later motivates a better measurement/intervention.

This ceiling is broad enough for ICML / ICLR / NeurIPS / ACL only if the result survives multiple model families, change regimes, and evaluation modes.

A result of the form:

> “method X is 4 points better on organism Y”

is insufficient and should be demoted.

---

## 3. Strongest current baseline / artifact

Primary open harness:

**science-of-finetuning/diffing-toolkit**  
https://github.com/science-of-finetuning/diffing-toolkit

The toolkit already supports or exposes a common framework for:
- black-box querying;
- KL / output comparison;
- Activation Difference Lens;
- activation analysis / Patchscope-style readout;
- PCA;
- SAE difference;
- crosscoder;
- Diff Mining;
- weight amplification;
- an agentic evaluator that tries to infer the fine-tuning change.

This is unusually valuable because the first experiments can be **baseline comparisons inside one codebase**, not months of tool reimplementation.

Other important artifacts:
- BatchTopK / crosscoder lineage from the NeurIPS 2025 sparsity-artifact work;
- Delta-Crosscoder code/paper where useful;
- MIB / SAEBench only as secondary validation ideas, not the primary task harness.

---

## 4. Baseline residency — mandatory before new method

### R0 — exact environment / artifact audit
Record:
- repository commit;
- released model pairs / organisms;
- activation dataset;
- agent evaluator;
- grading procedure;
- default hyperparameters;
- model families/scales;
- storage/runtime cost per method.

### R1 — reproduce the ICLR 2026 simple baseline
Reproduce ADL / simple activation differences on several released organisms.

The goal is not one headline number. Inspect:
- organism type;
- model family;
- model scale;
- token position;
- reference corpus;
- fine-tuning strength;
- seed / prompt variance.

### R2 — reproduce cheap external baselines
At minimum:
- direct black-box querying;
- behavior benchmark delta where available;
- logit/KL difference;
- Diff Mining.

Do this before training a crosscoder.

### R3 — reproduce representative internal baselines
Use a small representative set rather than every method:
- ADL / activation difference;
- one modern BatchTopK-style crosscoder;
- SAE-difference or PCA only if it supplies a distinct measurement primitive;
- DFC/Delta-Crosscoder only after the base crosscoder baseline is stable.

### R4 — normalize evaluation access
A method must not win because its agent simply receives more tokens, better generated text, more model queries, or more hand-curated features.

Record:
- information exposed to the evaluator;
- number of model queries;
- token budget;
- preprocessing compute;
- GPU memory/storage;
- human/LLM interpretation cost.

---

## 5. Evidence ladder

Do not make a field-level claim from one synthetic organism.

### L1 — known-objective narrow model organisms
Use existing released organisms because the training change is known.

Purpose:
> calibration / debugging / ground-truth-ish measurement.

Not sufficient for candidate promotion.

### L2 — de-salientized / mixed fine-tuning
Use existing or minimally produced pairs where the target fine-tuning data is mixed with broad pretraining/chat data, following the ICLR 2026 pressure that narrow finetuning can leave unrealistically global traces.

Purpose:
> test whether method performance survives when the objective is no longer trivially written everywhere.

Avoid large new training runs until L1 is reproduced.

### L3 — broader public post-training transitions
Select public model families with transparent stage/recipe information where possible (base → SFT → preference/RL or comparable stages).

Purpose:
> external validity beyond narrow organisms.

The exact “ground truth change” is weaker here, so rely on multiple observable consequences rather than an LLM judge alone.

### L4 — cross-architecture comparison
Only if earlier evidence says it is necessary.

DFC/cross-architecture diffing is a frontier parent, not a mandatory first experiment.

---

## 6. First exploratory analyses

These are discovery axes, **not expected findings**.

### A. Comparative-information curve
For each model-pair/regime, compare how much information about the known change is recoverable from:

1. behavior queries;
2. output probabilities/logits;
3. raw activation differences;
4. learned internal decompositions.

Ask whether each additional access level provides incremental value.

### B. Fine-tune breadth / salience
Vary or use existing pairs spanning:
- extremely narrow synthetic update;
- narrow update + broad data mixing;
- broader instruction/post-training update.

Does the ranking of diffing methods change as the update becomes less globally salient?

### C. Reference-distribution sensitivity
A diff method often needs a corpus on which to collect activations/logits.

Swap:
- random/pretraining text;
- in-domain text;
- held-out unrelated text;
- adversarially uninformative text.

Measure whether the discovered “difference” is stable.

### D. Visibility vs causal relevance
Separate:
- easy to read;
- predictive of changed behavior;
- causally sufficient to transfer some delta;
- causally necessary for the changed behavior.

Do not collapse these into one “interpretability score”.

### E. Coverage of behavioral delta
For a known behavioral test suite, ask:
> how much of the base→fine-tuned output-distribution / behavior gap is accounted for by the discovered representation?

A readable latent that explains little of the actual delta should not be overclaimed.

### F. Cross-seed / retraining stability
For methods with learned dictionaries/decompositions:
- rerun seeds;
- compare feature/difference stability;
- compare whether evaluator conclusions stay the same even if individual features change.

### G. Cost-normalized usefulness
Compare result quality at matched:
- preprocessing GPU hours;
- activation storage;
- evaluator query/token budget.

A much more expensive internal method needs a correspondingly stronger result.

### H. Held-out prediction
Use the diff to predict a changed behavior / trigger / failure slice not shown during explanation construction.

This is a stronger test than post-hoc description.

---

## 7. Outcome branches that would update the project

### Branch 1 — output/logit baselines dominate broadly
Then the existing model-organism evaluation may be too easy.

Next move:
- do **not** invent a more complex crosscoder;
- search for a more realistic regime where the changed behavior is not globally visible;
- if none exists, demote the premise that internal model diffing currently has comparative advantage.

### Branch 2 — internals help only in specific regimes
This is scientifically useful.

Examples of possible regime variables:
- sparse/rare triggers;
- changes with weak average logit footprint;
- broad post-training where many objectives overlap;
- changed internal routing that produces similar aggregate behavior.

Then the workbench narrows toward **conditions for internal comparative advantage**.

### Branch 3 — simple activation delta beats learned feature methods
Then ask why the expensive decomposition discards behaviorally relevant residual information or over-regularizes the delta.

Only after localizing the bottleneck should a method change be considered.

### Branch 4 — learned internal methods uniquely enable causal transfer/control
Then actionability becomes the stronger object:
> the method is valuable not because its description is prettier, but because it enables an intervention unavailable from external diffing.

### Branch 5 — conclusions are unstable to corpus/seed/evaluator
Then the object becomes **measurement reliability / identifiability** rather than model-diff algorithm design.

This would connect naturally to the broader interpretability-evidence territory in the library.

---

## 8. Method permission

No new model-diff method at the beginning.

A method becomes justified only after:

> **strong baseline → reproducible failure → localized measurement bottleneck → controllable change → improved held-out/actionable outcome**

Do not optimize one agent-judge score.

If a new method eventually emerges, it must beat:
- direct behavior;
- Diff Mining / logits;
- simple activation difference;
- strongest relevant learned baseline;

under matched information and cost budgets.

---

## 9. Evaluation cautions

### Do not use one LLM judge as ground truth
The toolkit's interpretability agent is useful, but conclusions need objective/behavioral checks where available.

### Do not treat finetuning dataset labels as the only target
A model may acquire unintended changes. Conversely, a training objective may not actually be learned.

### Do not assume feature exclusivity = model exclusivity
NeurIPS 2025 crosscoder artifact work is a mandatory control.

### Do not assume causal steering = natural mechanism
Steering can produce behavior through an unnatural path.

### Do not use narrow organisms as the final evidence rung
ICLR 2026 already warns that they can make the training objective globally readable.

---

## 10. Feasibility

Initial work is inference / activation extraction plus modest dictionary training.

Start with 1B–3B model pairs and only scale after the harness produces information.

Available local compute is sufficient for:
- multiple 1B–9B open models;
- activation extraction;
- selected SAE/crosscoder training;
- causal intervention runs.

The main cost risk is activation storage / repeated crosscoder training, not frontier-model pretraining.

No multi-node training is required for the first phase.

---

## 11. Ownership / nearest-prior boundary

### Direct parents we must not rediscover
- NeurIPS 2025 crosscoder sparsity artifacts;
- ICLR 2026 Narrow Finetuning / ADL;
- 2026 DFC cross-architecture diffing;
- 2026 Delta-Crosscoder;
- Aug-2026 Diff Mining;
- Anthropic's 2026 cross-architecture diff-tool work.

### What is *not* registered as our contribution
- “crosscoders have artifacts”;
- “narrow finetunes leave activation traces”;
- “logit differences can identify a finetune”;
- “DFC works across architectures”.

### Workbench-owned unknown
The broader measurement question remains:

> **across increasingly realistic model-change regimes, what incremental evidence does each access level—behavior, logits, raw activations, learned internal decompositions—actually provide?**

This is a workbench territory, not yet a paper claim.

---

## 12. Kill / demotion conditions

Demote to library knowledge if:

1. a current/forthcoming model-diffing paper already performs the same matched-access comparative audit across realistic regimes;
2. after reproduction, all apparent differences are evaluator-budget artifacts;
3. only narrow synthetic organisms yield usable ground truth and no external-validity rung can be constructed;
4. the surviving result is merely “method X wins on benchmark Y”;
5. a full paper would require proprietary frontier models or company-scale fine-tuning;
6. the project drifts back into “invent behavior anomaly → interpret it”.

---

## 13. Candidate promotion gate

Do **not** register a candidate until experiments produce a simpler paper identity than this workbench.

Minimum evidence before promotion:
- strong simple baselines reproduced;
- at least two model families;
- at least two genuinely different change regimes, including one beyond narrow model organisms;
- one stable result that survives reference-corpus/evaluator/seed controls;
- a clear nearest-prior boundary;
- a claim that matters beyond the toolkit itself.

Until then, remain in `workbench/`.
