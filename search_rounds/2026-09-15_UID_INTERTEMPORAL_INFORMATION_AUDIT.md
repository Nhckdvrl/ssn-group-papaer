# 2026-09-15 — UID / Intertemporal Information Allocation Audit

**Target:** ACL / EMNLP / NAACL Main, calibrated against TACL / ICLR / ICML / NeurIPS.

**Initial hook:**

> If a locally surprising expression makes the rest of a discourse easier to predict, is language efficiency better understood as intertemporal information allocation rather than local Uniform Information Density?

**Final verdict:** **KILL CURRENT FORM / ARCHIVE. No L-series. No pilot.**

---

## 1. Why this passed the first-layer taste test

ACL 2026 **Expect the Unexpected? Testing the Surprisal of Salient Entities** reports a striking pattern: globally salient entities are themselves significantly more surprising, yet systematically reduce surprisal for surrounding/upcoming discourse. The effect is strongest in topic-coherent genres and weakest in conversational contexts.

At first sight this looks like a load-bearing challenge to a naive local reading of Uniform Information Density (UID): a high-surprisal unit may be locally costly while simultaneously buying future predictability.

A natural reformulation is:

> perhaps information is sometimes deliberately front-loaded as an investment, so the scientific object should be the trade-off between present information cost and future uncertainty reduction.

This is a good question in plain language and is independent of a particular benchmark or model.

---

## 2. The direct owner already owns the central empirical move

The ACL 2026 paper does not merely report `salient entities have high surprisal`.

It explicitly asks whether salient entities reduce surprisal of surrounding discourse, builds controlled minimal-pair prompts, and finds that they do. Its conclusion states that salient entities increase expectations for subsequent discourse and produce localized reductions in surprisal while preserving document-level average information density.

Therefore the empirical statement

> high information now can make later content more predictable

is already part of the parent paper, not an unclaimed consequence.

A sequel cannot claim novelty by rebranding this as `information investment`.

---

## 3. The proposed higher-level theory also has mature ancestors

### A. Front-loading disambiguatory information is already an established language law

Pimentel, Cotterell & Roark (EACL 2021), **Disambiguatory Signals are Stronger in Word-initial Positions**, find a broad cross-linguistic tendency to front-load information that helps disambiguate words.

Thus a language system placing more informative material early in order to aid later interpretation is not a new theoretical object.

### B. Predictive Information Bottleneck / memory–surprisal theory already couples past information to future predictability

Futrell (2020) and Hahn/Futrell-related work formulate language processing as a resource-allocation problem in which limited memory is optimized to predict future linguistic input. Predictive Information Bottleneck / predictive rate–distortion explicitly treats information retained from the past in terms of its value for future prediction.

This is already an intertemporal information-theoretic object.

### C. Predictive information is now itself a direct theory of language structure

Futrell & Hahn, **Linguistic structure from a bottleneck on sequential information processing** (published 2025 / Nature Human Behaviour 2026), define predictive information as mutual information between past and future and argue that minimizing the complexity of sequential prediction yields systematic linguistic structure, with large cross-linguistic evidence.

So the conceptual move

> replace pointwise surprisal with a quantity linking present/past information to future prediction

is already a serious active theory program.

### D. Long-form discourse work already moved beyond pure UID

Tsipidi et al. (EMNLP 2024), **Surprise! Uniform Information Density Isn't the Whole Story**, already argue that systematic discourse structure creates predictable surprisal contours and that UID is only one pressure among several.

The ACL 2026 salient-entity paper is itself a continuation of that competing-pressures framing.

---

## 4. Reviewer compression

The tempting paper is compressed as:

> ACL 2026 salient-entity phenomenon + predictive-information / information-locality theory = `information investment` account.

That is an **A+B bridge**, not a new mother question.

The terminology `intertemporal information allocation`, `surprisal investment`, `predictability investment`, or `future entropy reduction` does not change this.

---

## 5. Why a new scalar/objective would not rescue it

It would be easy to define quantities such as:

- current surprisal minus cumulative future surprisal reduction;
- mutual information between an entity and a future discourse window;
- discounted future entropy reduction per current bit;
- information-gain / cost ratios.

But this would repeat the searcher's newly identified failure mode: **wrong-scalar autocomplete**.

Without an independently motivated theorem or an existing scientific contradiction, inventing a scalar and showing it correlates better with discourse patterns would be metric-first work, below the intended Main-level contribution.

---

## 6. Main-level calibration

Strong recent work changes a scientific belief, not just the terminology around an existing trade-off.

- ACL 2026 local-attention work connects a genuine empirical surprise to formal expressivity theory.
- ACL 2026 Memory Efficiency produces non-obvious representational consequences from resource-rational constraints.
- ICML 2026 Flexibility Trap turns a celebrated architectural advantage into a robust failure mode.
- NeurIPS 2025 RLVR work separates benchmark improvement from expansion of capability support.

The current UID route does not yet have an analogous non-obvious result. Both key ingredients are already known:

1. salient/high-information material can make later discourse more predictable;
2. language theories already optimize or study information useful for future prediction.

The remaining work would mainly unify terminology or fit another objective.

---

## 7. Reopen conditions

Do not reopen with more genres, languages, larger LMs, multimodality, a new future-window metric, or a new salience measure.

Only reconsider if one of these appears:

1. a natural linguistic law where UID and predictive-information / information-locality theories make **opposite preregisterable predictions on the same quantity** and existing data cannot reconcile them;
2. a theorem showing a widely used UID inference is invalid under sequential dependence in a non-obvious way, with a corrected law that predicts existing unexplained phenomena;
3. a robust cross-linguistic phenomenon in which local information peaks systematically improve later communication enough to reverse a standard efficiency prediction, and no existing competing-pressure theory already licenses it.

Until then, the scientific area remains important but the available paper is occupied.

---

## 8. Durable searcher lesson

> A surprising local violation of a scalar law does not automatically imply that the scalar is wrong. First check whether an older theory already treats the apparent violation as a trade-off across time, scale, or resource.

Also:

> `Paper A finds current cost predicts future benefit` + `Theory B already formalizes future predictive value` is not automatically a new research question.
