# L43 — Do Counterfactual Alternatives Predict Endogenous Route Selection?

**Status:** `PILOT-AUTHORIZED — E01R ONLY; NOT MAINLINE`  
**Date reconstructed:** 2026-09-15  
**Target:** ACL / EMNLP / NAACL Main  
**Calibration:** TACL / ICLR / ICML / NeurIPS

> Directory name is legacy from the original formulation. The scientific object below supersedes the earlier `natural backup robustness` framing.

## RQ

> **When a mechanistic intervention reveals an alternative circuit that can substitute for a primary route, does that alternative predict which route becomes causally load-bearing across ordinary input variation in the intact model?**

Short form:

> **Does counterfactual substitutability predict endogenous substitution?**

This is no longer the narrower question `do DoubleIO / TripleIO wake up the published backup heads?`.

The scientific object is the relationship between two notions that current mechanistic-interpretability papers often leave implicit:

1. **counterfactual alternatives** — components / circuits that become sufficient or necessary only after an internal intervention changes the model state;
2. **endogenous route selection** — components / circuits that become more or less load-bearing across intact forward passes as the input changes while the target behavior is preserved.

A model can possess many counterfactually sufficient routes without ever naturally switching among them. Conversely, an intervention-defined backup may reveal a genuine reserve route that the intact network recruits whenever the primary computation is naturally weak. Existing work establishes both sides separately but does not identify their mapping.

---

# 1. Why this is an important standing problem

Mechanistic interpretability studies trained networks largely through interventions. The interpretation usually goes beyond the literal statement `the network can behave this way after I perturb it`: researchers use interventions to infer the computation of the **unperturbed model**.

That inference is exactly what becomes questionable when redundancy and non-unique circuits exist.

The durable scientific question is therefore:

> **When does a counterfactual mechanism exposed by intervention correspond to computation the intact model actually uses?**

This matters independently of CoAx, IOI, or any specific circuit finder. It determines what we are entitled to mean by terms such as `backup circuit`, `alternative mechanism`, `redundancy`, and `circuit completeness`.

---

# 2. Why now: four recent results make the question identifiable

## A. Conditional Co-Ablation (CoAx, 2026)

https://arxiv.org/abs/2607.01940

CoAx makes **counterfactual substitutability measurable**. It identifies components whose causal importance rises after a primary circuit is removed. On GPT-2-small IOI it recovers the documented backup name movers with ROC-AUC about `0.91` versus `0.33` for ordinary first-order saliency, and the method transfers to induction across multiple architectures.

But CoAx deliberately asks:

> once the primary is removed, which units become necessary?

It does not ask whether the same units become necessary on any intact input.

The paper additionally reports that IOI backup discovery is robust across prompt templates, but the wake-up event is still defined **under primary ablation**.

## B. Intervention divergence (ICLR 2026)

*Addressing divergent representations from causal interventions on neural networks* shows that common MI interventions can move representations away from the model's natural distribution. Critically, it distinguishes harmless divergence from **pernicious divergence that activates hidden network pathways and dormant behavioral changes**.

This creates a live alternative interpretation of self-repair:

> a backup exposed after ablation may be a real counterfactual capability yet not be a route used by the natural model.

The paper studies when intervention states diverge and how to regularize them; it does not map intervention-exposed alternatives to endogenous route use.

## C. Multiple valid circuits (ICML 2026)

*All Circuits Lead to Rome* shows that the same task can be supported by multiple sparse, faithful, complete and low-overlap circuits. This rejects the assumption that one behavior has one canonical subgraph.

But `many sufficient circuits exist` does not imply:

> the intact model schedules different circuits on different inputs.

Alternative circuit existence and endogenous circuit selection are different scientific claims.

## D. Input variation can change discovered circuits without changing mechanism (TMLR 2026)

*Many Circuits, One Mechanism* shows the converse danger: input-conditioned structural differences can be **phantom specialization**. Circuits extracted from different input-frequency bands can look different while remaining functionally interchangeable and sharing one underlying computation.

Therefore neither of these inferences is safe:

- `different circuit structure -> different natural mechanism`;
- `alternative circuit under intervention -> naturally used backup`.

Together these results make the missing quantity unusually clear.

---

# 3. Closest owner map

## CoAx / self-repair lineage

Owns conditional backup discovery and causal repair **after internal damage**.

Does not test whether CoAx score predicts endogenous variation in causal necessity on intact inputs.

**Class:** leverage paper / mother-problem owner.

## ICLR 2026 intervention-divergence

Owns the general warning that interventions can activate dormant pathways that are not faithful to the natural state.

Does not study known alternative circuits, route selection across natural inputs, or whether counterfactual backup scores predict intact-state mechanism variation.

**Class:** adjacent foundational owner.

## The Curse of Multiple Mediators (2026)

Shows that mediator effects contain interaction terms, can be prompt-dependent, and that first-order component rankings can miss conditional mechanisms.

This establishes that causal importance can vary with context. It does not ask whether **the direction of that natural variation is predicted by counterfactual substitutability measured under an internal intervention**.

**Class:** strong adjacent causal-methodology owner.

## Adaptive Circuit Behavior and Generalization (Nainani et al.)

Shows that the GPT-2 IOI circuit largely reuses components across DoubleIO / TripleIO and adds input edges; it also discovers S2 Hacking and demonstrates that knockout circuits can exhibit behavior not present in the full model.

It does not test CoAx-defined backups as a class, nor the counterfactual-to-endogenous mapping.

**Class:** strong adjacent behavior owner.

## Circuit Stability Characterizes LM Generalization (ACL 2025)

Relates consistency of circuits across inputs to generalization.

It does not distinguish counterfactual alternative routes from naturally selected routes.

**Class:** adjacent mother problem.

## All Circuits Lead to Rome / Many Circuits, One Mechanism

The first establishes non-unique faithful circuits; the second shows apparent input-specific circuit structure may be functionally non-specific.

Neither asks which alternative route is **actually more causally load-bearing on a given intact input**, nor whether intervention-defined alternatives predict this allocation.

**Class:** adjacent foundational owners.

### Novelty verdict

> **NO EXACT OWNER FOUND as of 2026-09-15.**

The new estimand is not `circuit overlap`, `prompt-dependent attribution`, `backup discovery`, or `intervention OOD` individually. It is:

> **transfer from counterfactual substitutability to endogenous route selection.**

That claim is not entailed by any parent result and can plausibly go either way.

---

# 4. Why the reconstructed question is exploratory rather than phenomenon-gambling

The original E01 depended too heavily on a chosen perturbation family (DoubleIO / TripleIO) happening to wake the published backups. A null could always be attacked as `wrong stressor`.

E01R removes that dependence.

It does **not** ask whether one hand-picked prompt family triggers a backup.

Instead it estimates a relationship over a predeclared family of intact input variants:

> as the primary route's engagement varies naturally from input to input, do the heads that score as counterfactual substitutes under CoAx systematically become more engaged / necessary?

The primary object is a **continuous mapping across heads and inputs**, not a single positive phenomenon.

Three outcomes are all informative:

1. **positive transfer:** CoAx alternatives predict endogenous substitution;
2. **precise zero:** counterfactual alternatives are available but do not predict intact route selection;
3. **systematic negative / mismatch:** intervention-exposed routes and natural adaptive routes are different objects.

Only an unresolved wide interval / insufficient natural variation is a pilot failure.

---

# 5. Scientific consequence

## If counterfactual -> endogenous transfer is positive

- `backup circuit` has a functional interpretation beyond repair after artificial damage;
- conditional interventions can reveal a model's reserve computational repertoire;
- robust behavior may involve adaptive load sharing among alternative routes;
- non-canonical circuits are not merely equivalent explanations — some alternatives are differentially recruited across inputs.

## If transfer is precisely absent

- intervention-discovered alternatives are better described as **counterfactual capacities** rather than natural mechanisms;
- mechanistic explanations must distinguish `can implement after intervention` from `is used by the intact model`;
- self-repair and alternative-circuit results become evidence about reachable computation, not automatically about natural route scheduling.

## If structurally different circuits are naturally interchangeable without selective recruitment

This would connect directly to the `phantom specialization` result: mechanistic structure can vary or admit alternatives without corresponding to input-conditioned algorithm switching.

All directions change how causal MI evidence should be interpreted.

---

# 6. Why IOI is still the E01R instrument

GPT-2-small IOI remains the cleanest first test because it uniquely combines:

- documented primary name movers;
- documented backup name movers;
- CoAx's strongest labeled counterfactual-backup benchmark;
- published Base / DoubleIO / TripleIO variants with ABBA/BABA template families;
- known cases where circuit behavior adapts while core components are reused;
- negligible compute.

IOI is the **instrument**, not the intended paper identity.

If E01R is resolved, a full-paper path must move to an independent redundant computation such as induction, where CoAx already supplies cross-model counterfactual alternatives.

---

# 7. Best-case paper identity

Not:

> `CoAx on harder IOI prompts`.

Not:

> `another circuit stability metric`.

The best-case identity is:

> **Counterfactual alternatives are not the same thing as endogenous mechanisms: when does an intervention-discovered alternative route predict the route an intact neural network actually uses?**

A strong paper would introduce only the minimum measurement machinery needed to answer that scientific question, then establish the relation (or dissociation) across at least two behaviors and multiple models.

---

# 8. Feasibility

E01R is extremely cheap:

- frozen GPT-2-small;
- released CoAx implementation;
- released / published IOI prompt-template families;
- intact forward statistics plus head / head-set ablations;
- no training, SAE fitting, benchmark construction, or model zoo.

Expected compute is far below one GPU-day.

---

# 9. Selection verdict

| criterion | verdict |
|---|---|
| Independent importance | **PASS** — concerns the meaning of intervention-based mechanisms |
| Scientific consequence | **PASS** — separates natural computation from counterfactual capacity |
| Genuine uncertainty | **PASS** — recent literature supports both correspondence and divergence |
| Why now | **PASS** — CoAx + intervention-divergence + non-unique-circuit results make the mapping measurable |
| Exploratory vs gamble | **PASS AFTER REDESIGN** — continuous relation, no single stressor must succeed |
| Exact owner | **NO EXACT OWNER FOUND** |
| Feasibility | **VERY HIGH** |
| Main-level growth path | **PLAUSIBLE**, requires independent behavior/model evidence after E01R |

## Decision

> **L43 remains alive, but the old E01 authorization is superseded. `PILOT-AUTHORIZED — E01R ONLY; NOT MAINLINE`.**

The only authorized experiment is the reconstructed protocol in `E01_PREREGISTRATION.md`.
