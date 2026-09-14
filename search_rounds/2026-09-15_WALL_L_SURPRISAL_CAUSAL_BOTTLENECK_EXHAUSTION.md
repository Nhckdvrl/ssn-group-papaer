# 2026-09-15 — WALL-L / Surprisal as a Causal Bottleneck

**Mode:** old-theory lineage → failed-prediction audit → rival-process reconstruction → direct-owner assassination  
**Outcome:** **EXHAUSTED AS A CURRENT TOPIC GENERATOR — NO NEW L-SERIES — NO PILOT**

> The scientific dispute is real and old. The current project space nevertheless closes because the strongest residual — prediction cost versus structural reanalysis cost — is already an explicit mature program, while the obvious LM descendants become metric/model-fitting or LM-as-human-model work.

---

# 1. Mother scientific problem

> **Is incremental language-processing difficulty mediated by conditional probability / surprisal as a causal bottleneck, or do structure-building and structural revision incur additional costs not reducible to next-word predictability?**

This question predates modern LMs. Hale (2001) and especially Levy (2008) formulate a strong expectation-based account in which processing difficulty is proportional to surprisal, equivalently the work required to reallocate probability mass over analyses after each word.

Levy's formulation is load-bearing: conditional probability is not merely a useful predictor; it is the proposed causal bottleneck connecting linguistic representations to moment-by-moment processing difficulty.

Source:
- Levy 2008, *Expectation-based syntactic comprehension*, Cognition: https://doi.org/10.1016/j.cognition.2007.05.006

---

# 2. The central failed prediction is genuine

Garden-path disambiguation provides a clean stress test because the same continuation can be unexpectedly incompatible with a strongly preferred earlier parse.

A sequence of work finds the same qualitative problem:

- van Schijndel & Linzen (2021): LM surprisal predicts the direction of garden-path slowdowns but severely underpredicts their magnitude;
- Arehalli, Dillon & Linzen (CoNLL 2022): separating syntactic from lexical predictability increases the predicted effect but still leaves a large magnitude gap;
- a 2024 large-scale benchmark finds no evidence that standard LM surprisal explains the full disambiguation difficulty across constructions;
- Staub's 2025 Annual Review concludes that surprisal is a compelling account of predictability effects but that the stronger `conditional probability = causal bottleneck for all incremental difficulty` claim fares poorly for low-frequency words and garden-path disambiguation.

Representative sources:
- https://aclanthology.org/2022.conll-1.20/
- https://www.sciencedirect.com/science/article/pii/S0749596X24000135
- https://doi.org/10.1146/annurev-linguistics-011724-121517

This is therefore not a paper-gap construction. A clear old theoretical prediction failed quantitatively.

---

# 3. Mature rival explanation: prediction cost + reanalysis cost

The strongest rival is not `a better surprisal estimator`. It is a process decomposition.

Paape (Cognitive Science 2022) explicitly models multiple latent processes and separates:

- the cost of encountering an unexpected disambiguating word, plausibly related to surprisal;
- the additional cost of syntactic reanalysis;
- regressions / rereading;
- triage / failure to reanalyse;
- attentional contaminants.

The fitted reanalysis cost is large and independent of the basic unexpectedness cost.

Source:
- https://onlinelibrary.wiley.com/doi/full/10.1111/cogs.13186

A 2026 JML study further shows that contextual support affects both initial attachment probability and reanalysis cost, and that a latent-process model outpredicts a surprisal-only account of garden-path effects.

Source:
- https://www.sciencedirect.com/science/article/pii/S0749596X26000185

The theory space is therefore already explicitly:

> **probabilistic prediction/update** versus **additional structure-building / revision processes**.

---

# 4. Frontier evidence creates tension but does not leave an unowned residual

## 4.1 ACL 2026: an existence proof for a surprisal account

Yoshida et al., ACL 2026, fine-tune neural LMs so that LM surprisal predicts held-out human garden-path reading slowdowns while preserving/improving naturalistic reading-time fit.

This shows that the earlier magnitude gap is not by itself a logical falsification of all possible surprisal models: a predictor can be trained whose probability assignments reproduce the target slowdown.

Source:
- https://aclanthology.org/2026.acl-long.1694/

But an existence proof that a probability model can fit a dependent variable is weaker than identifying the human cognitive process that generated the slowdown.

## 4.2 PNAS 2026: prediction and structural processing dissociate in eye movements

Timkey et al. (PNAS 2026) examine multiple eye-movement measures. Their results support a decomposition in which LM surprisal can capture forward-reading disruption while failing by orders of magnitude on regression/rereading behavior associated with structural repair.

The paper explicitly interprets the results as evidence that both probabilistic inference and reanalysis contribute to garden-path difficulty.

Source:
- https://pmc.ncbi.nlm.nih.gov/articles/PMC13462876/

This is a particularly strong update because the rival theories differ on **process-sensitive observables**, not only one aggregate reading-time number.

---

# 5. Why no current candidate survives

## L1 — `Find a better structural surprisal / hidden-state quantity`

Dies because the scientific residual is no longer simply a missing predictor. ACL 2026 already explores internal-layer / probability-update variants, and a better regression feature would be metric/model-fitting unless it corresponded to an independently motivated cognitive process.

Direct neighbor:
- Kuribayashi et al., ACL 2026, *Dual Alignment Between Language Model Layers and Human Sentence Processing*: https://aclanthology.org/2026.acl-long.2143/

## L2 — `Test whether reanalysis is separate from surprisal`

Directly owned by Paape 2022, later latent-process work, and the 2026 eye-movement dissociation.

## L3 — `Use LM internals to distinguish prediction from structural repair`

Reviewer-compresses to:

> existing psycholinguistic reanalysis theory + mechanistic LM instrument.

It also inherits WALL-F's linking-hypothesis problem: causal structure inside an LM does not automatically identify the human mechanism.

## L4 — `What evidence could falsify surprisal theory?`

Scientifically profound as philosophy of model testing, but the concrete current answer is already being debated by Yoshida et al., Staub, and process-sensitive eye-tracking work. A standalone NLP project would either become model-discrimination methodology or psycholinguistic experiment design rather than a new model-science contribution.

---

# 6. Decision

**WALL-L exhausted as a current generator.**

Keep the durable scientific lesson:

> **Good average prediction does not imply that one scalar predictive quantity is the causal state variable generating all processing costs.**

Do not regenerate:

- another garden-path surprisal benchmark;
- another LM layer / hidden-state reading-time metric;
- `structural surprisal` variants;
- another fine-tuning-to-human-reading-time exercise;
- generic `surprisal vs reanalysis` in another construction;
- LM-internals-as-human-mechanism without an independent linking theory.

No L-series is created.