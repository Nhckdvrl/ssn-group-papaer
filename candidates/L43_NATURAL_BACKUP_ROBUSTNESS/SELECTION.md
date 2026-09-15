# L43 — Do Backup Circuits Provide Natural Robustness?

**Status:** `PILOT-AUTHORIZED — E01 ONLY; NOT MAINLINE`  
**Date:** 2026-09-15  
**Target:** ACL / EMNLP / NAACL Main  
**Calibration:** TACL / ICLR / ICML / NeurIPS

## RQ

> **Are the dormant backup circuits that repair a Transformer after artificial ablation also recruited by ordinary, answer-preserving input stress in the intact model?**

Short form:

> **Is artificial self-repair the same mechanism as natural robustness?**

This is **not** another circuit-finder paper and not another `does circuit X generalize across prompts?` paper.

The scientific object is the relationship between:

1. **intervention-induced redundancy** — backup components that become load-bearing only after a primary mechanism is artificially removed; and
2. **natural robustness** — the intact model preserving the same behavior when the input is changed in ways that preserve the correct answer.

---

# 1. Why this is a standing scientific problem

Transformer self-repair / the Hydra effect has been known for several years. The important unresolved question is not merely which component repairs which ablation. It is **why this redundancy exists and what, if anything, it is for**.

The key old pressure is unusually explicit.

Rushing & Nanda, ICML 2024, *Explorations of Self-Repair in Language Models*:

https://proceedings.mlr.press/v235/rushing24a.html

They show self-repair across model families and on the full pretraining distribution, but every self-repair event is still defined **after an internal ablation**. Their analysis finds at least two qualitatively different sources:

- final-LayerNorm rescaling, which can mechanically amplify surviving signal;
- sparse later components / Anti-Erasure behavior, which looks more like learned compensation.

Crucially, the paper explicitly warns that what first looked like intentional repair may instead be an uninteresting consequence of throwing the model off-distribution, and closes with the mystery of why self-repair occurs at all.

Therefore the standing question predates the new method:

> **Does self-repair reveal a robustness mechanism the intact network actually uses, or does it mainly reveal how a neural network reacts to an unnatural internal intervention?**

That distinction matters to both mechanistic interpretability and model science. If ablation-induced backup pathways are naturally recruited under input stress, they are part of the model's functional robustness architecture. If they are not, interpreting them as evidence of functional redundancy is much weaker.

---

# 2. Why now: the missing leverage appeared in 2026

Gong et al. 2026, *Conditional Co-Ablation: Recovering Self-Repair Backups in Transformer Circuits*:

https://arxiv.org/abs/2607.01940

introduces CoAx, which detects dormant backup components by measuring how a component's ablation effect grows after a primary circuit has already been removed.

Important facts for this project:

- on GPT-2-small IOI, CoAx recovers documented backup heads with ROC-AUC about `0.91`, versus `0.33` for ordinary single-ablation saliency;
- the discovered backup heads are genuinely dormant on the intact canonical task and become primary-like after the name-mover circuit is ablated;
- the same conditional principle generalizes to induction across multiple model families / scales;
- the released implementation is label-free, gradient-free, and costs only `O(#heads)` forward passes per seed set.

CoAx answers:

> **Which components become necessary after I break the primary circuit?**

It does **not** answer:

> **Would those same components ever become necessary if I leave the model intact and only stress the input?**

That newly separates a long-standing conceptual ambiguity into a directly testable question.

A second 2026 leverage, *Circuit Condensation* (arXiv:2608.27254), can post-train a model so that a behavior is carried by a much smaller causal graph while approximately preserving ordinary behavior and next-token distributions. This may become a useful later orthogonal intervention, but it is **not needed for E01** because changing weights creates a training confound. E01 deliberately uses a frozen model only.

---

# 3. Competing accounts

## H1 — Natural redundancy / robustness account

Backup circuits are learned alternate routes for the same computation. Artificial ablation exposes them because it is an extreme stressor, but milder ordinary input stress should recruit the same latent routes.

Prediction:

> a backup set that is nearly irrelevant on canonical intact inputs becomes causally important on answer-preserving stress inputs, even though no internal component has been removed.

Scientific consequence:

- self-repair is evidence about the model's natural robustness architecture, not only an ablation confound;
- robust behavior can be implemented by **adaptive mechanism switching**, not necessarily by a single stable circuit;
- circuit analyses that report only the canonical route can miss behaviorally relevant reserve capacity.

## H2 — Intervention-artifact account

Backup wake-up is mainly a response to the highly abnormal internal state created by ablation. The same components remain dormant when the intact model encounters ordinary input variation.

Prediction:

> natural input stress changes model performance / circuit use, but the CoAx-defined backup set does not become selectively load-bearing.

Scientific consequence:

- self-repair remains important as an **interpretability confound**, but it should not be interpreted as evidence that the model has naturally useful redundant mechanisms;
- internal ablations can create computations that the intact model never normally uses;
- claims about `the model has a backup circuit` need to distinguish counterfactual repair capacity from natural computation.

## H3 — Mixed account

Some backup pathways are true natural reserve routes while others are geometric / intervention-specific. The important object then becomes which properties distinguish the two classes.

E01 is not authorized to build a taxonomy. It only asks whether a selective natural-recruitment signal exists at all in the best-documented self-repair system.

---

# 4. Closest owners and why they do not own the claim

## 4.1 Hydra / self-repair lineage

- McGrath et al. 2023, *The Hydra Effect*.
- Rushing & Nanda, ICML 2024, *Explorations of Self-Repair in Language Models*.

They establish compensation **after internal intervention** and motivate the mystery of why it occurs. They do not test whether identified repair routes are naturally recruited by intact models under answer-preserving input stress.

**Owner class:** mother-problem owner, not exact owner.

## 4.2 Conditional Co-Ablation (2026)

CoAx identifies dormant backups under conditional internal ablation, validates their causal role in repair, and uses them for better knockout / pruning.

It does not test natural input stress without primary ablation.

**Owner class:** leverage paper / adjacent owner, not exact owner.

## 4.3 Adaptive Circuit Behavior and Generalization (Nainani et al., 2024)

https://arxiv.org/abs/2411.16105

This paper is especially important because it shows that IOI prompt variants can alter how the circuit behaves, and it discovers `S2 Hacking`, a mechanism that exists in the **knockout circuit but not in the full model**. That is direct evidence that internal interventions can create apparently adaptive mechanisms that are not how the intact model solves the task.

It studies circuit reuse / added edges across DoubleIO and TripleIO. It does not ask whether **published dormant backup name movers** become naturally load-bearing, and it predates the scalable CoAx backup-identification tool.

**Owner class:** strong adjacent lineage; strengthens the identification need rather than owning L43.

## 4.4 Circuit Stability Characterizes Language Model Generalization (ACL 2025)

https://arxiv.org/abs/2505.24731

Studies whether a model applies consistent circuits across input families and relates circuit stability to generalization.

It does not distinguish canonical primary routes from conditional backup routes or test whether ablation-induced backups support natural robustness.

**Owner class:** adjacent mother problem.

## 4.5 Formal / certified circuit robustness (ICLR 2026 and related work)

Recent verification work certifies that extracted circuits preserve behavior over bounded input domains or that circuit extraction is stable to perturbations. This concerns robustness of an **explanation / circuit**. L43 asks whether a specific redundancy discovered only under internal damage is part of the **model's natural computation**.

**Owner class:** adjacent methodology.

### Novelty verdict

`PLAUSIBLE INDEPENDENT SCIENTIFIC CLAIM — NO EXACT OWNER FOUND AS OF 2026-09-15`.

The dangerous compression is:

> `People already know circuits change across prompts and self-repair exists; just combine the two.`

What that compression misses is the load-bearing distinction:

> **The exact components called “backups” are defined by an intervention that may itself manufacture their role. The project asks whether that counterfactual role predicts causal necessity in an intact model under natural stress.**

Neither parent entails the answer.

---

# 5. Why this is not a bet on a lucky phenomenon

Both directions are scientifically meaningful.

### If backup recruitment is positive

We obtain a functional interpretation of self-repair: artificial intervention exposes reserve mechanisms that intact models also recruit when their ordinary computation is stressed.

### If backup recruitment is precisely absent

We answer the original Rushing–Nanda ambiguity in the other direction: at least for the canonical system, the celebrated backup circuit is a counterfactual repair route rather than a natural robustness mechanism.

A weak / noisy intermediate result is the bad outcome. E01 is designed to distinguish a material positive effect from a well-resolved near-null.

---

# 6. Why E01 uses GPT-2-small IOI

This is not because IOI itself is the desired paper identity. It is the strongest instrument.

GPT-2-small IOI has:

- the best-documented primary circuit;
- eight published backup name-mover heads;
- a published CoAx recovery benchmark;
- published answer-preserving prompt variants (DoubleIO / TripleIO) that stress the canonical algorithm;
- cheap exact interventions over all 144 attention heads.

That combination gives E01 unusually strong ground truth and low cost.

If E01 passes, the paper **must** move beyond one GPT-2 IOI case. Induction across multiple released models is the natural E02 route because CoAx already demonstrates scalable backup discovery there.

---

# 7. Best-case paper identity

The paper is not:

> `a better IOI analysis`.

It is:

> **A scientific test of whether redundancy revealed by mechanistic interventions corresponds to redundancy used by intact neural networks.**

A strong full result would establish one of two claims:

1. **Natural-redundancy result:** the same dormant components exposed by internal failure are selectively recruited by ordinary behavior-preserving stress across behaviors / models.
2. **Intervention-artifact result:** even highly validated backup circuits remain dormant under natural stress, separating counterfactual repair capacity from the mechanisms that support ordinary generalization.

Either would change how `backup circuit`, `self-repair`, `circuit completeness`, and ablation-based causal evidence should be interpreted.

---

# 8. Feasibility

Very high for E01.

The CoAx reference implementation is public and the IOI reproduction runs in seconds to minutes on a single GPU (or minutes on CPU). The proposed E01 uses GPT-2-small, a few hundred prompts per condition, frozen weights, and head-level ablations only.

Expected compute is negligible relative to the user's available hardware.

No training, SAE fitting, new benchmark construction, or model-zoo sweep is authorized.

---

# 9. Selection verdict

| criterion | verdict |
|---|---|
| Independent importance | **PASS** — why self-repair exists / what backup circuits mean is an old MI problem |
| Scientific consequence | **PASS** — separates natural robustness from intervention response |
| Genuine uncertainty | **PASS** — learned redundancy and off-distribution-artifact accounts both have direct support |
| Why now | **PASS** — CoAx makes dormant backups identifiable and transferable across models |
| Decisive attack | **PASS for E01** — intact stress + frozen backup set + causal backup ablation |
| Exact owner | **NO EXACT OWNER FOUND** |
| Feasibility | **VERY HIGH** |
| Best-case Main identity | **PLAUSIBLE**, contingent on expansion beyond IOI after E01 |

## Decision

> **L43 — PILOT-AUTHORIZED — E01 ONLY; NOT MAINLINE.**

Authorization is bounded by `E01_PREREGISTRATION.md`.

Do not start broad model scaling, SAE analysis, Circuit Condensation training, or a generic robustness benchmark before E01 resolves the basic construct.