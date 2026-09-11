# L21 — When Is Contextual Entrainment Rational?

**Status:** **PILOT-AUTHORIZED — E01 only**  
**Date:** 2026-09-12  
**Target:** ACL / EMNLP / NAACL Main

## Locked research question

> **Is contextual entrainment a learned online-cache prior calibrated to the real self-recurrence statistics of language, or an overgeneralized / distribution-insensitive copying bias?**

Plain example:

> After the word `elephant` appears once, a language model raises the probability of `elephant` later in the context. Natural language really is bursty: after a rare content word appears, it is often more likely to recur. The scientific question is not whether the model copies — that is already known — but whether it copies **by an amount that tracks the recurrence structure it was trained on**.

The paper is **not** another contextual-entrainment replication, another induction-head paper, or another generic repetition-bias benchmark. The scientific object is the **distributional origin and calibration of the entrainment prior**.

## Why this question is live

Several independent lines now meet without already answering the same question.

1. **Contextual entrainment is a hard replicated phenomenon.** Niu et al. (ACL 2025 Outstanding), *Llama See, Llama Do*, show that a token's logit rises after that token appeared earlier in context even when the token is irrelevant or randomly sampled. They identify causal entrainment heads. The paper explicitly distinguishes entrainment from induction: entrainment needs only previous occurrence of the token, not an `A B ... A -> B` prefix-completion trigger.
2. **The phenomenon is no longer supported by only one paper.** Kukreja et al. (Findings ACL 2026), *Better and Worse with Scale*, replicate token-level entrainment in Pythia and Cerebras-GPT and find opposite scaling laws for semantic versus non-semantic contexts; non-semantic/random copying grows with model scale. Liu & Chu (2026) independently extend contextual entrainment to whole sentences across 26 LLMs / seven families.
3. **Natural language has a classic self-trigger / burstiness structure.** Cache-language-model work long predating Transformers observes that once a word occurs in a document, its short-range probability of recurrence can rise substantially. This is exactly the kind of distributional regularity for which a recent-occurrence prior can be useful rather than pathological.
4. **Training distribution can causally determine copy-like Transformer computations.** Work on emergent ICL and induction heads shows that burstiness, repeated-bigram frequency, reliability and marginal distributions affect the formation of induction heads. But those works target induction / pattern completion, not token-level contextual entrainment.
5. **The required corpus/model linkage is unusually auditable.** Pythia releases the exact training data order and 154 checkpoints per model. Pile-train is queryable through Infini-gram / Infini-gram mini, and the Pythia pre-tokenized training data are public.

The unowned question is therefore:

> **Does the magnitude and range of a pretrained model's entrainment reflect the actual self-trigger statistics it learned from, and if not, where does the overgeneralization enter?**

## Nearest neighbors and ownership fence

### Niu et al. 2025 — contextual entrainment

Owns:
- the phenomenon;
- semantic modulation;
- entrainment heads and their causal contribution.

Does **not** establish:
- token-specific or distance-specific calibration to training-corpus self-recurrence;
- distributional origin from lexical burstiness;
- whether random-token entrainment is a rational prior applied out of distribution or a distribution-insensitive copy effect.

### Kukreja et al. 2026 — scaling laws

Owns:
- semantic/non-semantic scaling divergence;
- Pythia/Cerebras replication across model sizes.

Does **not** link the scaling law to training-corpus recurrence statistics or identify why non-semantic entrainment grows.

### Cache / self-trigger language models

Own:
- the fact that lexical recurrence is bursty;
- explicit cache/self-trigger models as a useful predictive mechanism.

Do **not** show that ordinary pretrained Transformers spontaneously learn a calibrated self-trigger prior, nor connect such a prior to contextual entrainment / distraction.

### Induction-head / burstiness work

Owns:
- `A B ... A -> B` copy / induction computations;
- effects of repetition frequency / reliability / burstiness on induction-head emergence and ICL.

Identity fence:

> **L21 lives only at `A ... -> A`: the magnitude/calibration of the prior assigned to the previously observed token itself.**

If the project becomes `how induction heads form`, `when copying skill emerges`, or generic `training data repetition causes ICL`, it has collided and must be re-selected.

## Core estimands

For target token / lexical item `w` and distance bucket `d`:

### Corpus self-trigger gain

Define a corpus recurrence quantity such as

```text
R(w, d) = log P_train(w at t | w occurred in the specified earlier distance window)
        - log P_train(w at t)
```

with local-adjacency / phrase-repeat exclusions predeclared so that the statistic measures longer-range self-recurrence rather than a trivial repeated bigram.

A document-level / window-level burstiness formulation may be used if it is frozen before model results and validated against the direct conditional-recurrence estimate.

### Model entrainment gain

Using the mother paper's neutral / random-token style protocol:

```text
E_m(w, d) = log P_m(w | matched prompt containing earlier w at distance d)
          - log P_m(w | matched prompt without earlier w)
```

Primary scientific quantity:

```text
Calibration / adaptation relation between R(w,d) and E_m(w,d)
```

not raw average entrainment.

## Competing accounts

### A — calibrated lexical cache prior

The Transformer has learned that different words and distances have different recurrence hazards and uses recent occurrence as a quantitatively adaptive prior.

Predictions:
- after controlling unigram frequency and tokenization, high-self-trigger items receive larger entrainment boosts;
- the decay of entrainment with distance tracks the corpus recurrence-decay curve;
- the relation is reproducible across Pythia scales and strengthens / stabilizes during training;
- controlled changes to training self-recurrence should move entrainment in the predicted direction.

Interpretation:

> Much of contextual entrainment is a rational adaptation to natural lexical burstiness; random/irrelevant prompts exploit that otherwise useful prior out of distribution.

### B — learned but overgeneralized cache heuristic

Training repetition creates a generic `recently seen -> boost` rule, but the rule loses token-specific / distance-specific calibration.

Predictions:
- mean entrainment is strong, yet token-specific `R -> E` calibration is weak;
- aggregate changes in training self-recurrence can still alter mean entrainment;
- entrainment is substantially flatter across lexical items / distances than the real recurrence statistics it supposedly approximates.

Interpretation:

> The model learned the existence of burstiness but compressed it into an indiscriminate copy prior. This directly explains why a useful adaptation becomes distraction on irrelevant/random context.

### C — distribution-insensitive copying side effect

Contextual entrainment is not meaningfully learned from lexical self-trigger statistics; it emerges from copying circuitry / optimization for other reasons.

Predictions:
- `R(w,d)` poorly predicts `E_m(w,d)` even across recurrence extremes and after controls;
- matched training-data interventions that change self-trigger recurrence while preserving relevant marginals do not selectively move entrainment;
- positive controls show that the same training intervention can affect an expected distribution-sensitive copying / induction quantity, ruling out an ineffective intervention.

Interpretation:

> Contextual entrainment is functionally distinct from the rational cache mechanism that natural language statistics would justify.

These are answers to the same RQ. The project may not rename itself after seeing which account wins.

## Natural / external substrate

### Model family

Primary: **Pythia** because it supplies:
- public Pile training data;
- exact data order;
- matched architecture family across scale;
- 154 checkpoints per model;
- standard and deduplicated variants.

The 2026 scaling paper has already shown that Pythia exhibits contextual entrainment, reducing replication risk.

### Corpus statistics

Primary training corpus: **Pile-train / the exact Pythia training stream**.

Possible implementation routes:
- Pythia's released pre-tokenized data / reconstructed dataloader for tokenizer-exact statistics;
- Infini-gram mini's `pile-train` index for string-level counts and document retrieval;
- a preregistered representative Pile shard/sample for E01 only, followed by broader confirmation if the pilot survives.

Do not use an unrelated web corpus as the primary `R(w,d)` estimate and then call it Pythia's learned training distribution.

## E01 — authorized bounded pilot

**Goal:** test whether real lexical self-recurrence contains enough signal to predict token-level contextual entrainment before any new pretraining experiment is attempted.

### E01-A — freeze the lexical population

Select a large predeclared set of ordinary English lexical items that:
- are single-token under the evaluated Pythia tokenizer for the model-side target;
- exclude special tokens / punctuation-only tokens;
- span broad unigram-frequency and self-recurrence ranges;
- are not selected after seeing entrainment values.

Use at least hundreds, preferably low thousands, of lexical items. The independent unit is the lexical item, not repeated prompt samples.

### E01-B — estimate training-corpus recurrence

For each item, estimate:
- unigram frequency;
- self-recurrence / burstiness in frozen distance buckets such as short, medium and long range;
- optional document-level recurrence as a secondary corroboration statistic.

Predeclare exclusions for immediate lexical duplication / fixed phrases so `R` is not merely `w w` bigram frequency.

### E01-C — measure entrainment

Reproduce the mother-style random / semantically irrelevant entrainment manipulation on **Pythia**, not only on an unrelated instruction model.

Start with two inexpensive sizes (e.g. 410M and 1.4B) at the final checkpoint. If the mother effect itself does not reproduce, stop and audit implementation before changing models/prompts.

For each `w`, measure `E_m(w,d)` at matched occurrence distances. Prompt wording, query, number of context tokens and target position must be fixed across treatment/control.

### E01-D — primary test

Primary:

```text
Does R(w,d) predict E_m(w,d)
within frequency-matched / controlled comparisons?
```

Required controls:
- unigram frequency;
- token length / tokenizer status;
- baseline target logit;
- position / distance;
- lexical class where feasible;
- prompt carrier / template.

Report rank association plus a calibration-style analysis rather than relying only on a regression p-value.

### Cheap heterogeneity checks

Predeclared only:
- content vs function-like lexical items;
- frequency strata;
- distance strata;
- model scale (410M vs 1.4B initially).

Do not scan dozens of lexical categories until one gives the desired sign.

## E01 decision gate

### Strong positive calibration

If recurrence statistics robustly predict entrainment after controls across both initial Pythia sizes:

> **KEEP / RE-SELECT FOR E02.**

E02 may use Pythia checkpoints to test when calibration emerges. Do **not** claim training causality from checkpoints alone.

### Strong systematic miscalibration

If mean entrainment is robust but `R -> E` is weak / much flatter than the true recurrence structure across well-powered extremes:

> **KEEP ONLY AS A MIS-CALIBRATION RESULT IF the mismatch is large, reproducible across both sizes, and survives frequency/token controls; then re-select before any training intervention.**

The next allowed question remains the same: learned generic cache heuristic vs distribution-insensitive copy effect.

### No stable result / confounded corpus statistic

If recurrence estimates are unstable, lexical sampling choices determine the conclusion, the mother entrainment effect itself is unreliable on Pythia, or calibration/miscalibration cannot be separated from unigram frequency/tokenization:

> **KILL L21.**

Do not rescue it by moving to arbitrary closed models, a different corpus, sentence-level entrainment, or alias transfer.

## Full-study path only if E01 survives re-selection

### C1 — calibration law

Quantify the mapping between natural self-recurrence and contextual entrainment across lexical items, distances and Pythia scales.

### C2 — learning dynamics

Use preregistered Pythia checkpoints to ask whether the **calibration relation**, not generic copy ability, appears / changes during pretraining. This is supporting evidence only because copying/induction training dynamics are already owned by prior work.

### C3 — causal distribution test

Only if still needed after C1/C2: train small controlled causal LMs on corpora with matched unigram / local statistics but manipulated longer-range self-trigger recurrence.

Critical requirement:

> manipulate `A ... -> A` self-recurrence while including an induction / copying positive control, so the experiment can distinguish entrainment sensitivity from generic inability of the manipulation to change copy circuits.

This stage must stay small enough to be practical; it is **not** permission for large-scale pretraining sweeps.

### Consequence

Use the identified law to predict which contextual tokens are disproportionately dangerous distractors / where repetition mitigation should be selective rather than uniform. This is a consequence, not the novelty source.

## Successful-result test

- **A wins:** contextual entrainment is substantially a learned, quantitatively calibrated cache prior; distraction is an OOD misuse of an otherwise rational adaptation.
- **B wins:** natural burstiness is learned only coarsely; Transformers overgeneralize it into an indiscriminate recent-token prior. This explains coexistence of useful context adaptation and random-token distraction.
- **C wins after a valid causal distribution test:** lexical self-trigger statistics do not explain entrainment despite strongly motivating classic cache LMs; contextual entrainment is a distinct copy-side effect rather than a learned lexical cache.

The project is not allowed to claim C from a null E01 correlation alone.

## Anti-resurrection / identity fence

L21 is **not**:
- L18 / alias or semantic-transfer entrainment;
- the historical 014 reference-identity route;
- another sentence-level entrainment paper;
- another model-size scaling law;
- another `copying emerges during pretraining` paper;
- another induction-head formation paper;
- generic repetition-loop mitigation;
- generic RAG distraction evaluation.

Any mutation into those forms requires fresh selection and should normally be killed against the existing parent.

## Current verdict

```yaml
natural_question: PASS
mother_phenomenon_replication_risk: LOW_MULTIPLE_INDEPENDENT_LINES
classic_scientific_bridge: PASS_CACHE_SELF_TRIGGER_BURSTINESS
internal_semantic_collision: PASS_NOT_L18_OR_014
external_parent_ownership: PASS_WITH_STRONG_NEIGHBORS
new_estimand: PASS_CORPUS_RECURRENCE_TO_MODEL_ENTRAINMENT_CALIBRATION
data_gold: PASS_PUBLIC_TRAINING_DATA_AND_EXACT_MODEL_FAMILY
pilot_cost: LOW_INFERENCE_PLUS_CORPUS_STATISTICS
outcome_robustness: PASS_CONDITIONAL_ON_CAUSAL_STAGE_FOR_ACCOUNT_C
full_study_burden: MODERATE_BOUNDED_SMALL_MODEL_TRAINING_ONLY_IF_NEEDED
pilot: E01_ONLY
verdict: PILOT-AUTHORIZED
```

## High-confidence references

- Niu et al. 2025, ACL Outstanding: *Llama See, Llama Do: A Mechanistic Perspective on Contextual Entrainment and Distraction in LLMs* — https://aclanthology.org/2025.acl-long.791/
- Kukreja et al. 2026, Findings ACL: *Better and Worse with Scale: How Contextual Entrainment Diverges with Model Size* — https://aclanthology.org/2026.findings-acl.1509/
- Liu & Chu 2026: *Sentence-Level Contextual Entrainment in Large Language Models* — https://arxiv.org/abs/2606.24077
- Lv et al. 2025, NAACL Short: *Language Models “Grok” to Copy* — https://aclanthology.org/2025.naacl-short.61/
- Aoyama et al. 2025/2026: *Predicting the Formation of Induction Heads* — https://arxiv.org/abs/2511.16893
- Biderman et al. 2023: *Pythia: A Suite for Analyzing Large Language Models Across Training and Scaling* — https://arxiv.org/abs/2304.01373
- Xu et al. 2025, EMNLP Best: *Infini-gram mini: Exact n-gram Search at the Internet Scale with FM-Index* — https://aclanthology.org/2025.emnlp-main.1268/
