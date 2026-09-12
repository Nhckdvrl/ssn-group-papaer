# 2026-09-13 — Factual-Recall Computational-Regime Search

**Target:** ACL / EMNLP / NAACL Main  
**Mode:** mechanism-first; old empirical law → modern regime; owner assassination before promotion; no survivor quota.  
**Repository state at round start:** latest visible `main` commit was `b8394a271ee9e456fc2fb10be2b17541748525b6`.

## Round result

# **1 SERIOUS lead — selection audit required; no pilot authorized**

The lead below is intentionally **not** registered as a pilot and is **not** permission to run a broad model zoo, factor sweep, or activation-patching campaign. Its surviving contribution is a causal/conditional-law question, not another localization result.

---

# SERIOUS — What Selects a Factual-Recall Computational Regime?

## RQ

> **Why do autoregressive Transformers that can recall the same kind of factual associations rely on different causal computations to do so, and what determines whether recall becomes Attention-centered or MLP-centered?**

A stronger paper-level formulation, if identification survives, is:

> **What load-bearing condition determines which factual-retrieval computation a Transformer learns?**

The target is **not** to ask where knowledge is stored in one more model. The target is to identify what makes a model settle into one computational regime rather than another.

## Concrete origin / mother phenomenon

The immediate pressure is Choe et al., EMNLP 2025 Main, *Do All Autoregressive Transformers Remember Facts the Same Way? A Cross-Architecture Analysis of Recall Mechanisms*:

- prior GPT-style factual-recall work emphasized early MLP contributions;
- across 17 autoregressive models, Choe et al. find strong cross-model differences, with Qwen-based models often showing substantial early-Attention causal contribution;
- the difference is not a single table cell: the paper runs restoration, severing and knockout-style analyses across multiple families/scales;
- importantly, the simple story is **not** `Qwen = Attention, LLaMA = MLP`: Appendix A includes within-family/scale heterogeneity (e.g. LLaMA-3.2-3B differs from LLaMA-3.1-8B), while Qwen models are more consistently Attention-centered;
- Appendix D checks several obvious static explanations—MLP hidden size, total attention-head count, MHA vs GQA, tokenizer/vocabulary size, and multi-token subjects—and none singly explains the observed localization pattern. The authors conclude that more complex interactions with training objectives / optimization dynamics remain open.

Primary source:
- Choe et al. 2025: https://aclanthology.org/2025.emnlp-main.1448/

There is also independent 2026 pressure that factual retrieval differs structurally across LLaMA and Qwen while being highly redundant/distributed:

- Hochman, Shapira & Goldberg, ACL 2026 Main, *Factual Retrieval in LLMs Is a Redundant, Distributed and Non-Contiguous Process* studies LLaMA-3.1-8B and Qwen3-8B and finds sparse/non-contiguous attribute-computation paths plus multiple functionally equivalent paths.
- This strengthens the claim that factual retrieval is not one universal localized pipeline, but it also creates a major construct-validity warning: a coarse module-localization score can reflect which redundant route an intervention exposes rather than a unique intrinsic memory site.

Primary source:
- Hochman et al. 2026: https://aclanthology.org/2026.acl-long.2168/

**Mother status:** `STRONG SINGLE PRIMARY SOURCE + INDEPENDENT STRUCTURAL SUPPORT`.

The mother is credible enough for search/selection because we are not betting the project on first discovering cross-model mechanism diversity. However, the exact binary notion `Attention-centered vs MLP-centered` still requires construct validation before compute-heavy causal claims.

## Why this matters

A large mechanistic literature has treated MLPs as key factual associative-memory components and used localization claims to motivate editing and interpretation. If different pretrained Transformers solve the same factual-recall problem through systematically different computations, then the useful scientific question is no longer simply:

> “Where is the fact?”

It becomes:

> **“What training / architectural condition makes one retrieval computation emerge rather than another?”**

A successful answer would turn a broad old mechanistic claim into a **conditional law** rather than add another model-specific exception.

## Closest work and prior endpoint

### 1. Choe et al., EMNLP 2025

Owns:
- cross-architecture factual-recall localization diversity;
- the observation that many Qwen-based models show stronger early-Attention contribution than the classical GPT-style MLP pattern;
- elimination of several simple correlates as complete explanations.

Does **not** identify:
- a load-bearing causal condition that predicts/induces the regime;
- whether architecture itself, learning dynamics/data, or intervention/path redundancy creates the apparent split;
- a controlled regime switch.

### 2. Hochman et al., ACL 2026

Owns:
- distributed, non-contiguous and redundant factual-retrieval computation;
- minimal attribute-computation paths in LLaMA and Qwen;
- evidence against a naive single-location story.

Does **not** identify:
- why different models acquire different module-level causal organizations;
- what condition changes that organization during learning.

### 3. Lv et al. 2024, *Interpreting Key Mechanisms of Factual Recall...*

Owns a GPT/OPT/LLaMA-style pipeline in which attention extracts topic information and MLPs transform/redirect it toward the correct answer.

Does not explain the later cross-model regime diversity.

Source: https://arxiv.org/abs/2403.19521

### 4. Ravfogel et al. 2026, *Geometric Factual Recall in Transformers*

In a controlled setting, challenges the interpretation of an MLP as a literal associative key-value store and shows a different geometric memorization solution in which embeddings carry relational structure and an MLP acts as a selector.

This is important pressure against an over-literal `MLP = memory bank` story, but it does not own the natural-pretraining question of what determines Attention-centered versus MLP-centered factual retrieval across modern LMs.

Source: https://arxiv.org/abs/2605.12426

### 5. Zucchet et al. 2025, *How do language models learn facts?*

Uses controlled factual learning to study training dynamics and finds phases associated with attention-circuit formation followed by precise factual learning. It establishes that training dynamics can matter for factual computation, but does not explain the natural-model regime split.

Source: https://arxiv.org/abs/2503.21676

## Prior endpoint

The current literature permits the reader to conclude:

> factual recall is more distributed/redundant than a single MLP-memory story, and different autoregressive Transformers can place causal burden on different modules/paths.

It does **not** yet permit:

> **given a model/training regime, predict which factual-retrieval computation will emerge—or causally change that regime while holding the task/factual objective fixed.**

That is the missing inference.

## Candidate accounts

These are deliberately broad at SEARCH/early-SELECT stage. Do not multiply them into many factor hypotheses after seeing results.

### Account A — Architecture-induced regime

A structural design choice changes the computational economics of factual retrieval; under matched learning conditions, changing that architecture is sufficient to shift causal reliance between Attention and MLP.

The important version is **not** one of Choe's already-negative one-factor correlations. It would need a pre-specified structural quantity with a mechanistic reason to alter where subject/relation information can be bound/transformed.

### Account B — Learning-induced regime

The apparent family/architecture association is incidental. Fixed architecture can acquire different retrieval regimes under different training/data/optimization conditions; the learned representation geometry and learning trajectory determine causal routing.

### Account C — No stable intrinsic module regime

`Attention-centered` versus `MLP-centered` is partly a property of the intervention/localization protocol in a computation with multiple redundant paths. Under path-aware or orthogonal causal measurements, the binary regime distinction is not stable enough to support a causal determinant story.

C is a legitimate kill outcome, not a rescue narrative.

## Possible discriminator

The decisive operation should eventually be a **controlled cross that can cause or predict a regime change**, not a model-zoo correlation.

A scientifically valid path would have two stages:

1. **Construct-validity gate:** establish that the same facts/models have a stable causal-regime classification under at least two intervention families that stress different failure modes of localization (e.g. module-output ablation/knockout versus a path-aware/restoration-style criterion), with direct behavior as the endpoint. If the classification is protocol-fragile, kill the proposed scientific object.
2. **Only after that**, compare a small number of pre-specified architecture-vs-learning manipulations capable of separating A from B. The strongest evidence would be a controlled manipulation that **switches or predictably shifts** the causal regime while factual competence/objective is matched closely enough for interpretation.

Do **not** authorize unrestricted searches over architecture knobs, data mixtures, prompts, checkpoints or localization metrics until one yields a convenient sign.

## L29 first-stage lesson applied

L29 failed because the proposed causal instrument had almost no valid leverage at the reference state. The analogous first gate here is:

> **Does our operational definition of a factual-recall regime have material, directionally interpretable, protocol-stable causal leverage on factual output?**

If `Attention-centered` / `MLP-centered` is only a fragile ranking of small attribution scores, later causal comparisons are unidentified.

This gate must precede any expensive controlled-training program.

## Reviewer compression

Strongest attack:

> **“This is just Choe et al. 2025's cross-architecture Attention-vs-MLP observation + Hochman et al. 2026's distributed factual paths + better causal tracing / architecture ablations.”**

If the proposed study merely:
- runs more models;
- reports Attention/MLP ratios;
- adds activation patching;
- sweeps obvious architecture hyperparameters;
- correlates the pattern with model family;

then that compression wins and the route should be killed.

## Why the lead currently survives compression

`Choe + Hochman` still does **not** imply the central answer:

> **what load-bearing condition makes one factual-retrieval computation emerge instead of another?**

Nor does it provide a controlled switch that changes the regime under matched factual learning.

That remainder is a real scientific inference rather than a missing benchmark cell. It would revise the old factual-memory mechanism into a conditional computational law.

## Successful-result test

The strongest acceptable headline is **not**:

> “Qwen uses more Attention than LLaMA.”

It must look like:

> **“Factual retrieval has multiple stable computational regimes, and which regime emerges is determined by condition X; changing X causally switches retrieval from one route to another while preserving the factual objective.”**

or, if Account C wins:

> **“The apparent Attention-vs-MLP regime split is not an intrinsic model property: once redundant retrieval paths are measured in a protocol-robust way, the classical localization distinction collapses.”**

The second outcome is only Main-worthy if the construct failure is broad, causal and consequential for factual-mechanism/editing conclusions—not if one metric merely disagrees with another.

## Outcome interpretation

- **A wins:** a pre-specified architecture condition causally shifts the regime under matched training. This yields a conditional architecture→computation law.
- **B wins:** fixed architecture changes regime under a pre-specified training/data condition, showing the observed family split is learned rather than structurally forced.
- **A×B interaction:** potentially the most informative result if predicted in advance; architecture changes which learning condition favors a route.
- **C wins / construct gate fails:** kill the `regime-selection` paper identity unless the failure itself invalidates a broad consequential mechanistic inference under a pre-specified test. Do not mutate into a generic localization-metric paper.
- **No controlled factor moves the regime:** do not factor-fish. Return to SEARCH/SELECT.

## Anti-resurrection

This is **not**:
- the killed generic representation/readout route;
- the killed generic post-training rerouting route;
- the killed MoE routing-frequency/causal-utility route;
- another knowledge-editing benchmark;
- another “which layer stores facts?” localization study.

Its only acceptable identity is **cause/condition of computational-regime formation for the same factual-recall function**.

## Main-level growth path

If the construct and causal determinant survive:

1. establish a protocol-robust cross-model mother phenomenon;
2. causally isolate the condition selecting the regime;
3. show the conditional law predicts held-out natural pretrained models / training trajectories;
4. test one consequential implication (e.g. whether an editing/localization assumption transfers only within a regime), without turning the paper into an editing-method paper.

This is a plausible paper-scale path, but it is not authorized yet.

## Current blocker

# **BLOCKER: PRE-SPECIFY A LOAD-BEARING CAUSAL AXIS WITHOUT FACTOR FISHING, AND VALIDATE THE REGIME CONSTRUCT AGAINST REDUNDANT-PATH ARTIFACTS.**

Choe already tried several obvious static factors and found none sufficient. We must not convert that negative appendix into an unlimited search for any correlating architecture detail.

Before pilot authorization, selection must identify:
- one or at most a very small number of scientifically motivated causal axes;
- why each should alter the relevant computation;
- a matched manipulation that can distinguish architecture-induced from learning-induced regime formation;
- a regime metric whose causal interpretation survives redundancy/path compensation.

## Verdict

# **SERIOUS — SELECTION AUDIT REQUIRED; NO COMPUTE AUTHORIZED**

The question is natural and consequential, the mother phenomenon is credible, direct owner search did not find a 2026 paper that already identifies the determinant, and the strongest reviewer compression leaves a substantial missing causal inference.

However, the route should be killed before compute if the only feasible next step is an open-ended factor sweep or if the Attention-vs-MLP classification is not stable under orthogonal causal measurements.

---

# Other hooks assassinated in this round

These are recorded only to prevent rediscovery; none is a candidate.

## Position/context geometry — DROP

Position bias / position-dependent behavior has already been directly mechanized by ICLR/ICML 2025 and later structural analyses. A new position intervention would be another cell, not a new parent.

## Beam-search inverse test-time scaling — DROP

2026 work directly explains wider beam / more search hurting through scorer noise and overestimation bias. The attractive `more compute hurts` phenomenon already has a named causal account.

## LM-head gradient bottleneck — DROP

A March 2026 work argued the LM head suppresses 95–99% of gradients and may be a harmful bottleneck; by August 2026 a direct backward-only causal intervention explicitly tests whether that bottleneck is harmful. The decisive question is already owned.

## Weight tying / input-output gradient conflict — DROP

Findings ACL 2026 directly studies output-gradient dominance under weight tying and causal input-gradient scaling. Old empirical recommendation + modern mechanism is already occupied.

## Induction-head / function-vector mechanism switching — DROP

By ICML 2025 / ICLR 2026, work already asks which heads implement ICL, how function-vector and induction-head roles differ with scale/training, and how mechanisms transition. Too mature.

## Multi-token prediction as planning mechanism — DROP

2026 work directly analyzes why MTP changes planning/reverse-reasoning behavior and supplies theory/mechanism. No open parent here.

---

# Round conclusion

This round produced **one candidate worth spending further selection effort on**, not one candidate ready to run.

The key distinction to preserve is:

> **Prior work owns cross-model factual-recall mechanism diversity. The only surviving paper identity is to identify the load-bearing condition that selects a computational regime—or decisively show that the supposed regime is not a stable causal object.**

Do not dilute this into a localization survey.