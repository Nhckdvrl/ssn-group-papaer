# CT03 — Counterfactual Credit for MoE Routing

**Status:** ❌ **CANCELLED / KILLED AFTER PILOT — 2026-09-22**

> Killed as a Main-level **method** topic. The estimator half survived every test;
> the step from credit to router policy did not. Two distillation formulations
> (binary CCD, then KL-regularised CPD) failed to establish any credit-specific
> improvement, and ordinary router-only CE adaptation matched or exceeded CPD on
> route quality. Kill record: `FAILED_TOPICS.md` (`CT-KILL-20260922-1`);
> full evidence: `candidates/CT03_COUNTERFACTUAL_CREDIT_MOE_ROUTING/`.
> **Do not reopen with a nonlinear router, on-policy/actionable credit, a
> second-order estimator, more data, a second model family, or EPO/RoMA
> baselines.** Registration kept below as provenance.

**Original status:** PILOT-AUTHORIZED  
**Registered:** 2026-09-19  
**Primary target:** ICLR / ICML / NeurIPS; ACL/EMNLP Main is plausible if the final story centers language reasoning.  
**Core mode:** method-first after a diagnostic proxy-validation pilot.  
**Resource envelope:** designed for 4×/8× RTX PRO 6000 96GB; no from-scratch MoE pretraining required.

---

# 1. Mother question

Modern sparse MoE routers receive task-loss feedback mainly through the experts that were actually executed. On hard tokens, recent counterfactual analysis shows that the standard route can be far from the best equal-compute route available inside the same frozen model.

CT03 asks:

> **Can we give a pretrained MoE router useful token-level credit for unexecuted experts without explicitly rerunning the downstream network for many alternative routes?**

The methodological target is not generic differentiable routing. It is a scalable approximation to **counterfactual route utility** that can supervise multi-layer router adaptation while preserving ordinary sparse Top-K inference.

---

# 2. Why now

## 2.1 The routing blind spot is now empirically visible

**When Are Experts Misrouted? Counterfactual Routing Analysis in Mixture-of-Experts Language Models** (Yoon et al., 2026) directly compares the default route with sampled equal-compute alternatives in pretrained MoE LLMs.

It reports that:

- standard routing is well aligned on already-confident tokens;
- on ambiguous / fragile reasoning tokens, route scores become weakly aligned with actual next-token utility;
- lower-loss equal-compute routes often already exist inside the frozen model;
- a minimal final-layer router-only update can move AIME/HMMT pass@K.

The paper's own formal diagnosis is important:

> standard task loss evaluates the executed route; unexecuted experts receive no token-level counterfactual task signal.

Its EPO update samples multiple alternative routes, executes them, observes their losses, and trains only the final-layer router. The authors explicitly frame this as an existence probe rather than a complete routing-improvement method, and point to efficient counterfactual-aware training as an open next step.

## 2.2 Existing solutions address adjacent but different objects

Nearby work already owns several broad ideas:

- **ERL (EMNLP 2025 Findings):** random routing perturbations + task-performance advantage + RL;
- **MoE-GRPO (CVPR 2026):** expert routing as an RL exploration problem in VLMs;
- **ProbMoE (ICML 2026):** probabilistic differentiable exact-k routing;
- **ERC (ICLR 2026):** router–expert capability coupling via an auxiliary loss;
- **AdapMoE:** Taylor/Fisher sensitivity for deciding whether extra expert activation is needed;
- **CoR (ACL 2026):** inference-time counterfactual expert impact / virtual ablation for factuality;
- **TGR-MoE (2026):** teacher-guided supervision to stabilize sparse routing.

Therefore CT03 does **not** claim first counterfactual routing, first gradient routing, or first router supervision.

The remaining opening is narrower and methodological:

> **replace expensive route-level counterfactual execution with a cheap local credit estimator for unexecuted experts, then use that estimator to train pretrained routers across multiple layers.**

---

# 3. Proposed method object

Consider one MoE layer and one token. The standard route activates expert set (S) and produces MoE output (h). Suppose candidate expert (j\notin S) replaces selected expert (i\in S).

Exact counterfactual utility would require forming the alternative route and rerunning the remaining network to obtain:

[
\Delta L_{i\rightarrow j}
=
L(h^{i\rightarrow j})-L(h).
]

CT03 tests whether a first-order local approximation is predictive enough:

[
\widehat{\Delta L}_{i\rightarrow j}
\approx
\nabla_h L^	op
\left(h^{i\rightarrow j}-h\right).
]

Operationally:

1. run the normal sparse forward;
2. obtain downstream gradients with one normal backward pass;
3. for a small candidate set of unexecuted experts, compute only their local expert outputs;
4. estimate their counterfactual marginal utility using the cached local gradient;
5. distill these utilities into the router with a pairwise/listwise preference objective;
6. at inference, discard the estimator and use ordinary Top-K routing.

The key efficiency hypothesis is:

> **local expert forwards + one shared downstream backward can approximate many expensive full rerouting evaluations.**

---

# 4. Exact novelty boundary

## Not the contribution

- “Top-K routing is imperfect.”
- “MoE routers need better supervision.”
- “Use gradients for routing.”
- “Explore alternative experts.”
- “Counterfactual expert impact matters.”
- “Use Taylor sensitivity.”
- “Fine-tune only routers.”

All already have close prior art.

## Intended core claim

> **For pretrained MoE LLMs, the expensive loss effect of replacing a routed expert can be predicted sufficiently well from local expert-output perturbations and shared downstream gradients. This converts sparse partial-feedback routing into scalable approximate counterfactual credit, enabling multi-layer router adaptation with no inference-time overhead.**

The paper lives or dies on whether this approximation is accurate enough to improve real routing and downstream reasoning.

---

# 5. Dangerous nearest priors

## 5.1 When Are Experts Misrouted? — strongest parent

Owns:

- the counterfactual routing-quality diagnostic;
- fragile-token routing regret;
- sampled equal-compute route evaluation;
- final-layer EPO existence probe.

Does not currently own:

- a cheap surrogate for alternative-route loss;
- multi-layer scalable router adaptation;
- one-backward credit for many local route alternatives;
- strong benchmark improvement method.

If a revised version adds exactly this class of efficient surrogate, CT03 is KILL or must be reframed.

## 5.2 ERL — EMNLP 2025 Findings

Owns route exploration and performance-gap RL.

Difference:

> ERL obtains supervision by executing perturbed routing paths. CT03's question is whether unexecuted expert credit can be estimated locally enough to avoid repeated downstream route execution.

## 5.3 ProbMoE — ICML 2026

Owns differentiable probabilistic exact-k routing.

Difference:

> ProbMoE redesigns the routing distribution/gradient estimator. CT03 retains a pretrained Top-K MoE and supplies task-grounded counterfactual utility targets for router adaptation.

## 5.4 ERC — ICLR 2026

Owns expert-router coupling using expert proxy activations.

Difference:

> ERC encourages structural alignment between expert identity and router embeddings; it does not estimate token-specific downstream loss change for an unexecuted expert.

## 5.5 AdapMoE

Owns Taylor/Fisher sensitivity as a routing/computation tool.

Difference:

> Taylor approximation itself is not novelty. CT03 uses a local downstream influence estimate specifically to recover **which currently unexecuted expert should replace a selected expert** and validates it against exact equal-compute route regret.

## 5.6 CoR — ACL 2026

Owns training-free counterfactual expert impact for hallucination mitigation using virtual ablation.

Difference:

> CoR is inference-time expert redistribution guided by offline causal analysis. CT03 uses counterfactual credit as a **training signal**, with standard routing retained at inference.

## 5.7 Gradient-based expert pruning / upcycling

Recent pruning/upcycling work uses first-/higher-order expert-importance estimates.

Difference:

> global expert deletion/duplication importance is not token-conditional route credit. However, if their estimators transfer directly and already solve token-wise expert replacement, novelty collapses.

---

# 6. Minimum pilot

The pilot is not “train the whole method”.

It first asks whether the cheap estimator is faithful enough to justify the paper.

## 6.1 Models

Stage A — cheap proxy validation:

- OLMoE-1B-7B and/or DeepSeek-V2-Lite.

Stage B — main realistic model if Stage A survives:

- Qwen3-30B-A3B.

Optional replication:

- GPT-OSS-20B.

No from-scratch pretraining.

## 6.2 Data

Use existing verifiable reasoning trajectories.

Primary:

- MATH / Numina-style verified math trajectories;
- AIME/HMMT held out strictly for evaluation.

Optional breadth after survival:

- GPQA;
- code with executable tests.

Do not build a new dataset.

## 6.3 Exact-vs-proxy calibration experiment

For sampled hard tokens at several MoE layers:

1. execute standard route;
2. choose a small candidate pool of near-boundary / plausible unselected experts;
3. compute exact alternative-route loss by true downstream rerun;
4. compute first-order local credit from the standard pass;
5. compare:
   - Spearman/Kendall correlation;
   - best-alternative top-1/top-k recall;
   - sign agreement on beneficial replacements;
   - calibration versus token difficulty/layer/depth;
   - speed / FLOPs / wall-clock ratio.

This is the decisive experiment.

## 6.4 Hard success bar for continuing

Continue only if the proxy:

- predicts exact route utility materially above router-score and random baselines;
- retrieves beneficial alternatives reliably on fragile/hard tokens;
- remains useful beyond the final MoE layer;
- achieves a large reduction in supervision cost relative to explicit rerouting;
- does not work only in one narrow layer/model.

---

# 7. Method path if pilot survives

A minimal full method can be:

## Candidate generation

Do **not** evaluate all experts.

Use a cheap pool such as:

- router top-(k+m);
- high-score boundary experts;
- optionally an expert-similarity / historical-utility candidate.

## Local counterfactual credit

For candidate replacement (i\rightarrow j), estimate:

[
\hat u_{ij}
=
-\nabla_h L^	op \Delta h_{ij}.
]

Potential refinements only if required by evidence:

- gradient normalization;
- second-order diagonal correction;
- uncertainty filter;
- layer-specific temperature.

Do not add these by default.

## Router objective

Train only routers initially with:

- pairwise preference;
- listwise ranking;
- or soft utility distillation.

Add a conservative anchor to the pretrained router to avoid route collapse.

## Inference

Standard deterministic Top-K.

No test-time search, virtual ablation, or extra expert activation.

---

# 8. Benchmark plan

Primary method-result benchmarks:

- AIME 2024/2025;
- HMMT 2025;
- MATH held-out / comparable math suite.

After method stability:

- GPQA / science reasoning;
- one code benchmark with executable evaluation.

Main comparisons:

- original pretrained router;
- router-only SFT on the same trajectories;
- EPO-style sampled route preference where feasible;
- ERL-style alternative-route exploration if reproducible;
- ProbMoE / other differentiable routing only when compatible with pretrained-model adaptation;
- simple router-confidence / entropy hard-token baselines.

Report both Pass@1 and Pass@K. A method that moves only enormous-K oracle diversity but not practical accuracy is insufficient.

---

# 9. Resource audit

The research is intentionally post-training rather than pretraining.

Qwen3-30B-A3B:

- total weights are large but fit the local 96GB-GPU class with appropriate sharding / precision;
- only a small fraction of parameters are active per token;
- routers are tiny relative to the backbone;
- experts/backbone can remain frozen.

4× PRO 6000 is sufficient for pilot and router-only training; 8× gives comfortable parallelism for exact-counterfactual calibration and benchmark generation.

The expensive operation is not parameter optimization but alternative-route evaluation. The entire point of CT03 is to remove most of that cost.

---

# 10. Hard kill conditions

KILL CT03 if any is true:

- first-order local credit has weak correlation / top-k recall against exact alternative-route loss;
- it only works at the final MoE layer where EPO-style rerouting is already cheap;
- exact rerouting cost is already small enough that the surrogate has no practical advantage;
- router-score / entropy / expert-output norm predicts the same alternatives equally well;
- router-only adaptation using the proxy does not improve real downstream benchmarks;
- gains require dense evaluation of a large fraction of experts, destroying sparse-training efficiency;
- a direct paper is found that already performs token-wise unexecuted-expert downstream-gradient credit and multi-layer router training;
- the story collapses into a generic Taylor pruning / expert-importance method.

Do not rescue by:

- adding many handcrafted losses;
- using a giant benchmark matrix;
- full-model fine-tuning before router-only evidence;
- creating a new dataset;
- moving to proprietary-scale pretraining.

---

# 11. Reviewer compression test

## “This is just EPO but cheaper.”

Partly, and that is acceptable only if the **methodological difference is substantive**:

> EPO obtains labels by full alternative route execution and is demonstrated only as a final-layer existence probe; CT03 proposes an estimator that shares one downstream backward across many candidate alternatives and makes multi-layer counterfactual router training practical.

The paper must quantify the efficiency/faithfulness frontier, not only final accuracy.

## “This is just Taylor sensitivity.”

Then the paper fails unless it establishes the specific new object:

> **credit to an unexecuted replacement expert, calibrated against exact equal-compute route regret, used to improve pretrained multi-layer MoE routing.**

## “Why not use ProbMoE?”

Because the setting is different:

> post-hoc adaptation of strong pretrained sparse MoEs, preserving their architecture and inference path, rather than redesigning the router and retraining the MoE under a probabilistic routing formulation.

---

# 12. Expected paper narrative

A plausible paper arc is:

1. pretrained MoE routers have a task-relevant partial-feedback blind spot;
2. exact counterfactual route supervision fixes the signal but is expensive;
3. downstream gradients already contain reusable local information about route perturbations;
4. a local counterfactual credit estimator predicts exact route utility;
5. distilling that credit into multiple pretrained routers improves reasoning;
6. inference remains ordinary sparse Top-K.

This is a method paper with analysis in service of the method, not an analysis paper looking for a benchmark afterward.

---

# 13. Expected main claim

The strongest version:

> **Counterfactual route utility in pretrained MoE LLMs can be approximated locally from expert-output perturbations and shared downstream gradients, enabling efficient multi-layer router adaptation that recovers misallocated expert capacity and improves reasoning without inference-time overhead.**

---

# 14. Verdict

> **PILOT-AUTHORIZED**

Reason:

- the routing failure is real and independently documented;
- recent methods leave a clear efficiency gap between route-level exploration and scalable token-level counterfactual supervision;
- the proposed distinction is method-level rather than keyword-level;
- the decisive pilot is cheap and falsifiable;
- no from-scratch pretraining is required;
- the final system can preserve standard sparse inference;
- benchmark upside is direct and measurable.

First task:

> **validate the local counterfactual credit estimator against exact alternative-route loss before training any router.**
