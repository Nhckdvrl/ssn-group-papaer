# L31 — What Selects a Factual-Recall Route?

**Status:** **PILOT-AUTHORIZED — E01 ONLY (2026-09-13)**  
**Target:** ACL / EMNLP / NAACL Main

## Locked research question

> **What load-bearing condition determines whether a Transformer learns an Attention-centered or MLP-centered factual-recall computation?**

The project does **not** ask where facts are stored in one more model. It asks what causes one retrieval computation rather than another to emerge for the same factual-recall function.

## Mother phenomenon

Choe et al., EMNLP 2025 Main, show across 17 autoregressive models that factual-recall causal organization is not universal: several Qwen-family models place much more causal burden on early Attention than the classical GPT-style early-MLP pattern. Their appendix also shows that simple static factors such as MLP hidden size, total head count, MHA/GQA, tokenizer/vocabulary size and multi-token subjects do not singly explain the split.

- Choe et al. 2025: https://aclanthology.org/2025.emnlp-main.1448/

Hochman et al., ACL 2026 Main, independently show that factual retrieval is sparse, distributed, non-contiguous and redundant across LLaMA-3.1-8B and Qwen3-8B, warning against treating a single attribution score as a unique memory location.

- Hochman et al. 2026: https://aclanthology.org/2026.acl-long.2168/

So the mother is already credible: modern autoregressive Transformers can implement factual recall through materially different causal organizations. The open question is what selects the organization.

## Causal axis selected before compute

The authorized axis is **embedding geometry / MLP usability**, not an open-ended architecture sweep.

Nichani, Lee & Bietti, ICLR 2025, show that both self-attention and MLPs can serve as associative memories for factual recall and that a Transformer can trade off attention versus MLP parameter capacity while preserving factual-recall ability.

- https://proceedings.iclr.cc/paper_files/paper/2025/hash/0bf9f909c24c8879d1b7f86fa50a9e49-Abstract-Conference.html

Dugan et al. 2025 and Garcia et al. 2026 show that the geometry of key/value embeddings strongly controls MLP fact-storage capacity and, crucially, **Transformer usability**. Whitening can improve raw MLP storage capacity while making the stored facts harder for a Transformer to retrieve; the later Hebbian account identifies decoding margin as a load-bearing usability condition.

- https://arxiv.org/abs/2512.00207
- https://arxiv.org/abs/2607.10034

These results give a pre-specified causal hypothesis:

> **If the same factual task is trained under a geometry that makes the MLP route harder to use, a free Transformer should shift factual-recall causal burden toward Attention; if MLP usability improves, burden should shift toward the MLP route.**

This is a route-selection hypothesis, not merely another capacity result.

## Closest-work compression

Strongest reviewer attack:

> `Choe: natural models differ in Attention/MLP factual recall` + `Nichani: either Attention or MLP can store facts` + `Dugan/Garcia: embedding geometry changes MLP capacity/usability` = your paper.

The compression still does **not** establish the missing inference:

> **Does changing geometry causally make an otherwise free Transformer choose a different factual-memory route?**

The closest constructive work intentionally freezes or constrains attention/value pathways to prevent the Transformer from using an alternative fact store. That setup measures whether a provided fact-storing MLP is usable; it does not let Attention and MLP freely compete and test route selection.

Direct searches through September 13, 2026 did not find an owner that performs this controlled `geometry → route choice` intervention.

**Novelty verdict:** `PLAUSIBLE INDEPENDENT CONTRIBUTION`.

## E01 — authorized bounded pilot

### Purpose

E01 answers only:

> **Can a controlled change in embedding geometry causally shift which module carries factual-recall computation when Attention and MLP are both free to learn?**

### Setup

Use a small synthetic factual-recall Transformer derived from the public ICLR-2025 factual-recall setup, because the pilot is about causal identification rather than natural-language scale.

Keep fixed across arms:

- fact mapping / task distribution;
- number of facts;
- sequence format and noise distribution;
- Transformer depth and total architecture;
- optimizer, steps, initialization distribution and training budget;
- evaluation examples.

Manipulate only a **predeclared embedding-geometry condition** that prior work independently shows changes MLP capacity/usability. The preferred intervention is a graded covariance-whitening / geometry transform with at least a low and high condition; an intermediate condition is allowed only if fixed before outcome inspection.

The Transformer must remain free to use both Attention and MLP parameters. Do **not** freeze value/output projections or remove the alternative fact-storage route as in the constructive-MLP usability studies; that would destroy the route-selection estimand.

### Required first stage

Before interpreting route movement, verify that the geometry manipulation actually changes the independently motivated MLP-usability quantity in the expected direction in the pilot setup.

Acceptable first-stage observables include the prior-work decodability / minimum-margin / usability quantity, chosen before training outcomes are inspected.

If the manipulation does not materially move the intended MLP-usability quantity, **STOP**. Do not compare learned routes. This is the L29 first-stage gate.

### Route measurement

Do not rely on one scalar attribution method.

E01 requires two orthogonal causal views, for example:

1. module-output severing/ablation of Attention versus MLP with factual accuracy/logit effect as endpoint;
2. restoration/path-aware causal intervention that stresses redundancy differently.

The route-shift conclusion is valid only if the direction is consistent across the predeclared causal measurements and factual competence remains sufficiently matched for interpretation.

A probe or raw activation magnitude is not evidence of causal route selection.

## Primary estimand

Let `R` be a predeclared causal reliance contrast, conceptually:

`R = causal contribution(Attention) - causal contribution(MLP)`.

The primary estimand is:

`Δ_route = R(high-MLP-usability geometry) - R(low-MLP-usability geometry)`.

The predicted sign should correspond to greater MLP reliance when the MLP route is easier to use, and greater Attention reliance when it is harder.

The exact normalized metric can be chosen during implementation, but it must be frozen before reading the treatment sign and must use direct factual behavior as endpoint.

## Outcome map

### Geometry moves MLP usability and route shifts accordingly

This supports the selected causal account: computational regime is at least partly **learned under representational/optimization constraints**, rather than being a fixed architecture-family property.

This is sufficient to return to selection for C2/C3, not permission to immediately scale.

### Geometry moves MLP usability but route does not shift

**KILL the current determinant hypothesis.** Do not search across arbitrary architecture/data knobs for a factor that works.

### Geometry fails to move MLP usability

**Instrument failure / STOP.** Repair is allowed only if it preserves the same independently motivated geometry intervention and is bounded; unrestricted manipulation search requires fresh selection.

### Attribution methods disagree on route direction

Treat the route construct as unstable. **KILL/HOLD** before any natural-model expansion. Do not convert the paper into a generic attribution-metric comparison without re-selection.

## Resolution and feasibility

This pilot is intentionally cheap relative to full-LLM training:

- shallow/small synthetic Transformers;
- same public factual-recall family as the theory/constructive literature;
- multiple random seeds are expected;
- no model-zoo inference or billion-parameter training is required for E01.

The mother and first-stage effect are expected to be large enough for this controlled regime: prior work reports large changes in MLP capacity/usability under embedding-geometry manipulation. Therefore the pilot passes the L19 resolution gate.

## Main-level growth path if E01 passes

E01 alone is not a Main paper. The intended paper-scale progression is:

1. **C1:** controlled geometry causally selects a factual-recall route;
2. **C2:** test whether the same geometry/usability quantity predicts natural pretrained-model regime differences without model-family handwaving;
3. **C3:** manipulate the quantity during controlled pretraining or a matched factual-learning trajectory and show a regime switch / boundary condition;
4. optional consequence: show that localization/editing assumptions transfer differently across regimes.

The desired final inference is a conditional computational law, not a synthetic-task curiosity:

> **Transformers can implement factual memory through multiple computations; which route emerges is selected by the usability/geometry of the candidate memory substrate.**

C2/C3 are **not authorized** by this file. E01 must pass and return to selection.

## Anti-resurrection / scope guard

L31 is not:

- another `where are facts stored?` paper;
- another knowledge-editing benchmark;
- a generic architecture sweep;
- generic post-training rerouting;
- representation/readout;
- a localization-method paper;
- a model-family comparison.

If E01 cannot causally connect a pre-specified geometry/usability manipulation to route selection, stop the route.

## Final authorization

> **PILOT-AUTHORIZED — E01 ONLY**

Authorized: small controlled factual-recall training experiment with predeclared embedding-geometry intervention, first-stage MLP-usability validation, multiple seeds, and two causal route measurements.

Not authorized: natural LLM model zoo, broad architecture/data sweeps, knowledge editing experiments, C2/C3, or full-study claims.
