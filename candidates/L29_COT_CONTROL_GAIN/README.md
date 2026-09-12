# L29 — Losing the Steering Gain

**Status:** **SERIOUS / PRE-PILOT — IDENTIFICATION BLOCKER — NO COMPUTE AUTHORIZED**  
**Date:** 2026-09-12  
**Target:** ACL / EMNLP / NAACL Main

## Locked research question

> **When reasoning post-training makes chain-of-thought control collapse, is the loss merely caused by longer trajectories accumulating more opportunities to violate the constraint, or does training itself weaken the local causal influence of an explicit constraint on the reasoning policy?**

If the local influence really weakens, the second-stage question is:

> **Did the constraint signal become unavailable, or is it still represented but increasingly unable to steer the continuation policy?**

The first question is load-bearing. The second is authorized only if the first establishes a genuine training-induced local-control change.

---

## Mother phenomenon

Primary mother:

- Yueh-Han Chen et al., **Reasoning Models Struggle to Control their Chains of Thought** (ICML 2026 / arXiv:2603.05706).

The phenotype is already strong enough that this project does not need to gamble on discovering it:

- CoT control is dramatically lower than final-output control across many reasoning models;
- models often explicitly notice that they are violating a CoT constraint and still continue violating it;
- controllability worsens with test-time reasoning, problem difficulty, and additional reasoning-oriented RL;
- public OLMo model-flow checkpoints expose a same-base training trajectory;
- the parent explicitly states that the mechanism behind low controllability is not well understood.

This candidate studies **why training changes control**, not whether low controllability exists.

---

## Why the broad mechanism story is not ours

The tempting broad formulation

> “the model knows the instruction but the reasoning policy ignores it”

is already too directly owned.

Tan et al., **Compliance versus Sensibility: On the Reasoning Controllability in Large Language Models** (arXiv:2604.27251), reports that conflicting reasoning instructions remain internally detectable / decodable, models favor task-appropriate reasoning patterns over compliance, and activation steering can increase compliance by up to 29%.

Fu et al., **Scaling Reasoning, Losing Control: Evaluating Instruction Following in Large Reasoning Models** (ACL 2026 Main), and ReasonIF occupy the broader reasoning-capability / instruction-adherence trade-off.

Therefore L29 is **not**:

- another “represented but unused” probe paper;
- another activation-steering paper;
- another reasoning-vs-instruction benchmark;
- another endpoint model-family comparison.

If the project drifts into any of those identities, re-select or kill.

---

## Why length correction is not the paper

CoT length is a known major confound. OpenAI system cards already report CoT-Control conditional on chain length precisely because longer trajectories are harder to control.

So this is **not** a paper about fixing the aggregate controllability metric.

The unresolved quantity is:

> **At a matched reasoning state, does the same explicit constraint have lower causal gain on the continuation policy after reasoning post-training?**

Call this quantity the **local constraint→policy control gain** for now. The name is provisional; the estimand, not the terminology, is what must be locked.

---

## Competing accounts

### Account A — Opportunity accumulation

Training mainly lengthens / expands the reasoning trajectory. Local responsiveness to a constraint remains similar, but every extra reasoning step creates another opportunity for a first violation. Global exact-control probability therefore collapses even without a changed local controller.

### Account B — Constraint-signal degradation

At the same reasoning state, the constraint becomes less available / less stably represented after training, so its causal influence on continuation falls.

### Account C — Policy-gain / attractor override

The constraint signal remains represented, but outcome-trained reasoning dynamics exert stronger policy control. The constraint therefore loses causal leverage over token/continuation selection even though it can still be decoded.

The sequence is mandatory:

> **A vs {B,C} behaviorally first → only then B vs C mechanistically.**

A probe cannot skip the first discrimination.

---

## Proposed decisive operation — not yet authorized

A future E01 should estimate the constraint’s **local causal influence at a matched state** across checkpoints from the same open OLMo training path.

Candidate structure:

1. select multiple checkpoints from one same-base OLMo RL-Zero reasoning trajectory;
2. use the same questions and constraint-compatible reasoning states/prefixes;
3. hold the reasoning state fixed by teacher forcing;
4. change only the explicit CoT constraint versus a matched neutral/control instruction;
5. measure the induced change in locally compliant next-token probability mass and a short-horizon continuation measure;
6. use pre-specified surface constraints for which local compliance is mechanically identifiable;
7. replicate the conclusion on natural pre-violation states rather than relying solely on synthetic/shared prefixes.

The target is the **causal contrast induced by the constraint**, not absolute next-token probability, benchmark accuracy, probe score, or hidden-state similarity.

---

## Identification blocker

The shared-prefix intervention can be off-distribution for later checkpoints.

If an apparent checkpoint trend is caused by forcing a state that a checkpoint would not naturally visit, then the experiment does not identify a training-induced change in control.

Before any compute, lock a construction satisfying all of the following:

- the reasoning content/state is identical across constraint and control arms;
- the prefix is valid under both arms and remains constraint-compatible;
- local compliant-token mass has an unambiguous interpretation;
- natural pre-violation states provide an active control against teacher-forcing artifacts;
- the intervention does not itself restate the answer or alter task difficulty;
- the inference still holds if aggregate sequence length is ignored entirely.

If this bridge cannot be made defensible, L29 is NO-GO.

---

## Anti-resurrection

Closest internal dead/search routes:

- `search_rounds/2026-09-12_CONTINUED_SEARCH_II.md` — **Reasoning strength vs validity gate**. Not the same: that route asked whether stronger reasoning weakens the decision to attempt/abstain; L29 asks whether post-training changes causal prompt→reasoning-policy influence under an explicit constraint.
- same round — generic **generation destroys an already-good decision structure** / latent→policy gaps. Not the same only because L29 has a specific stable training transition, same-base checkpoints, and a pre-defined causal quantity. If reduced to endpoint representation/readout, it becomes a duplicate neighborhood and should die.

No existing K-ID or candidate with the exact CoT-control-gain quantity was found in the repository search. This does not waive external owner search.

---

## Closest external owners and reviewer compression

Primary owner stack:

1. **CoT-Control** — establishes the phenotype, the RL/test-time-compute/length trends, and the open mechanism question.
2. **Compliance versus Sensibility** — establishes static reasoning-prior-over-instruction behavior, internal encoding, and activation-level steering.
3. **MathIF / ReasonIF** — establish the modern reasoning-versus-instruction-adherence tension.
4. OpenAI system-card reporting — already conditions controllability on CoT length, so simple deconfounding is not new.

Strongest reviewer compression:

> **“CoT-Control already shows RL and longer reasoning reduce control; Compliance-vs-Sensibility already shows instructions are encoded but internal reasoning priors win; MathIF/ReasonIF already show the trade-off. This is those papers plus checkpointed logit/activation analysis.”**

The paper survives that compression only if it establishes a new training-causal statement:

> **Holding the current reasoning state fixed, reasoning post-training changes how strongly an explicit constraint causally controls the continuation policy, separating a training-induced controller change from mere longer exposure to failure opportunities.**

No current owner located in the 2026 search directly establishes that quantity across a same-base training trajectory.

---

## Successful-result chain

Required chain:

> same-state constraint intervention across matched checkpoints  
> → estimated local constraint→policy causal gain  
> → gain changes systematically with reasoning post-training, beyond trajectory length  
> → reasoning training changed the controller itself rather than only the duration of exposure  
> → causal localization distinguishes signal degradation from intact-signal / policy-override dynamics  
> → a conditional account of when stronger reasoning becomes less steerable.

Failure modes:

- checkpoint trend in raw compliance only → insufficient;
- probe decodability changes → insufficient;
- activation transplant changes behavior → insufficient by itself;
- aggregate length-normalized benchmark result → insufficient;
- unrelated model-family comparison → not a training intervention.

---

## Pre-result outcome interpretations

### Outcome A — local control gain is stable

Supports the opportunity-accumulation account. Because length confounding is already known and operationally handled in system-card reporting, this result likely **kills L29 as a Main paper** rather than creating a fallback “length explains everything” paper.

### Outcome B — local control gain clearly falls with training

Supports a real training-induced controller change and authorizes the pre-registered B-vs-C localization stage.

### Outcome C — gain changes only for a pre-specified constraint family / RL domain

Potentially meaningful only if the conditioning axis is motivated and locked before E01. Otherwise re-select; do not invent a heterogeneity paper post hoc.

### Outcome D — effect is tiny / unresolved

Kill or HOLD on resolution. Do not rescue with a hidden-state statistic.

---

## Resolution / feasibility

This candidate was deliberately designed to avoid repeating L19.

- **Training:** none required for the first discriminator.
- **Models:** public 7B OLMo same-base training checkpoints.
- **Primary E01 metric:** logit/probability causal contrast, allowing deterministic paired measurement before stochastic rollouts.
- **Independent units:** questions / matched question-prefix states, not tokens treated as independent replicates.
- **Expected scale:** parent endpoint controllability shifts are large, often order-of-magnitude, so the route does not start from a sub-noise mother effect.
- **Pilot scale:** hundreds of states across a few checkpoints should be enough to discover whether the local effect is substantial; expected inference cost is single-digit GPU-hours on the available hardware.
- **Kill threshold:** if the estimated matched-state gain shift is only at the ~1 percentage-point scale or otherwise requires parent-scale stochastic sampling to distinguish from noise, stop rather than enlarge compute.

Exact MDE must be computed from a small no-claim dry-run / variance estimate before any authorized pilot.

---

## Main-level growth path if C1 survives

1. **Training effect:** local constraint→policy gain falls across reasoning post-training even at a matched state.
2. **Mechanistic localization:** signal degradation vs intact signal with reduced causal policy gain.
3. **Training boundary:** identify which stage/domain changes the controller using OLMo Base / SFT / DPO / RL and RL-Zero domain paths where comparable.
4. **Prediction / consequence:** use control gain to predict late-reminder / steering recoverability and the gap between native reasoning control and more externalized/output control.
5. **Scope:** replicate the core inference on a second open model flow only if required for the claim; do not replace same-base causality with model-family breadth.

---

## Current verdict

```yaml
natural_question: PASS
mother_phenomenon: PASS_STRONG
replication_risk: LOW
broad_parent_novelty: FAIL_ALREADY_OWNED
narrow_training_causal_quantity: PLAUSIBLE_INDEPENDENT_CONTRIBUTION
closest_owner_density: HIGH
causal_estimand: DEFINED_IN_PRINCIPLE_NOT_YET_LOCKED_OPERATIONALLY
primary_blocker: MATCHED_STATE_INTERVENTION_MUST_NOT_BE_A_TEACHER_FORCING_OOD_ARTIFACT
successful_result_test: PASS_IF_BLOCKER_CLOSED
outcome_identity: LOCKED_WITH_KILL_ON_STABLE_GAIN
resolution_risk: LOW_TO_MODERATE
training_cost: NONE_FOR_FIRST_DISCRIMINATOR
pilot: NOT_AUTHORIZED
verdict: SERIOUS_PRE_PILOT
```

**Next action:** close the matched-state identification bridge on paper, then re-run selection. Do not run E01 yet.
