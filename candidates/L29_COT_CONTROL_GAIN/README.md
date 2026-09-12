# L29 — Losing the Steering Gain

**Status:** **RECONSTRUCT-AUTHORIZED — ONE FINAL INSTRUMENT AUDIT (2026-09-13)**
**Date:** 2026-09-13
**Target:** ACL / EMNLP / NAACL Main

## Locked research question

> **When reasoning post-training makes chain-of-thought control collapse, is the loss merely caused by longer trajectories accumulating more opportunities to violate the constraint, or does training itself weaken the local causal influence of an explicit constraint on the reasoning policy?**

If the local influence really weakens, the second-stage question is:

> **Did the constraint signal become unavailable, or is it still represented but increasingly unable to steer the continuation policy?**

The first question is load-bearing. The second is **not authorized yet**; it becomes eligible for re-selection only if E01 establishes a genuine training-induced local-control change.

---

## Mother phenomenon

Primary mother:

- Yueh-Han Chen et al., **Reasoning Models Struggle to Control their Chains of Thought** (ICML 2026 / arXiv:2603.05706).

The phenotype is strong and does not need to be rediscovered:

- CoT control is dramatically lower than final-output control across many reasoning models;
- models often notice that they are violating a CoT constraint and nevertheless continue violating it;
- controllability worsens with longer reasoning / increased test-time compute;
- on the same OLMo-3 RL-Zero training path, CoT controllability falls by more than an order of magnitude as RLVR training proceeds;
- the trend is also observed before/after reasoning training across multiple open model families;
- output controllability falls much less than CoT controllability;
- the parent explicitly states that the mechanism behind low controllability is not well understood.

The paper itself already treats reasoning length as a major confound. This candidate therefore studies **why training changes control after separating local responsiveness from cumulative opportunities to fail**.

---

## Why the broad mechanism story is not ours

The broad formulation

> “the model knows the instruction but the reasoning policy ignores it”

is already directly owned.

Tan et al., **Compliance versus Sensibility: On the Reasoning Controllability in Large Language Models** (arXiv:2604.27251), shows that conflicting reasoning instructions remain internally detectable / decodable, models favor task-appropriate reasoning patterns over compliance, and activation steering can increase compliance.

Fu et al., **Scaling Reasoning, Losing Control: Evaluating Instruction Following in Large Reasoning Models** (ACL 2026 Main), and **ReasonIF** occupy the broader reasoning-capability / instruction-adherence trade-off.

Therefore L29 is **not**:

- another represented-but-unused probe paper;
- another activation-steering paper;
- another reasoning-vs-instruction benchmark;
- another endpoint model-family comparison;
- another “repeat the instruction near the answer” method paper.

If the project drifts into any of those identities, re-select or kill.

---

## Important 2026 neighbor: bringing the constraint closer is already owned

MathIF (ACL 2026 Main) explicitly tests a recency/distance account: after a long CoT it appends `Wait` and repeats the original constraint near the final answer. Compliance improves on all three tested reasoning models, although problem-solving accuracy can fall.

This is **not** our novelty. It is useful prior evidence that contextual distance is a serious competing explanation.

L29 instead asks a training-dynamics question MathIF does not answer:

> **Along the same reasoning-RL trajectory, does the instantaneous causal gain of a fresh constraint itself collapse, or does the model remain locally steerable while only accumulating more opportunities to violate the constraint?**

A recent RLVR neighbor, **Verifier-Induced Support Reshaping in On-Policy Optimization** (arXiv:2608.00220), shows that verifier training can reshape the support of later instruction-following behaviors. This increases the importance of measuring the *local intervention effect* directly rather than inferring it from endpoint pass rates, but it does not establish the CoT constraint→continuation gain studied here.

---

## Competing accounts

### Account A — Opportunity / distance accumulation

Training lengthens or expands reasoning. The original constraint becomes more distant and every extra step creates another opportunity for the first violation. However, **at a currently reachable reasoning state, a fresh or otherwise locally available constraint should retain roughly similar causal leverage over the next part of the trajectory**.

Global exact-control probability can therefore collapse even if the local controller has not weakened.

### Account B — Constraint-signal degradation

At the same externally matched reasoning history, the constraint becomes less available / less stably represented after training, so its causal influence on continuation falls.

### Account C — Policy-gain / attractor override

The constraint signal remains available, but the outcome-trained reasoning policy exerts stronger competing control. The constraint therefore loses causal leverage over continuation even when freshly supplied.

Mandatory sequence:

> **A vs {B,C} behaviorally first → only then B vs C mechanistically.**

No probe or activation analysis may skip E01.

---

# E01 — AUTHORIZED BOUNDED PILOT

E01 contains **two mandatory identification legs**. Neither leg alone licenses the Main-level inference.

The purpose is only to answer:

> **Does reasoning post-training reduce local constraint→policy causal gain beyond the known length/opportunity effect?**

No hidden-state mechanism work, new training, steering method, benchmark construction, or model-zoo expansion is authorized.

## E01A — Common-support same-history control gain

### Core idea

Compare checkpoints on the **same observable reasoning history**, but do not assume arbitrary teacher-forced prefixes are valid states.

1. Use one same-base OLMo-3.1 7B RL-Zero reasoning trajectory with multiple public RL checkpoints.
2. Use the same frozen questions and CoT-control constraints across checkpoints.
3. Generate a pool of constraint-compatible prefixes from natural rollouts.
4. Score every candidate prefix under **every checkpoint × prompt arm**.
5. Retain only a preregistered **common-support set**: prefixes whose per-token NLL / likelihood lies inside the normal range of natural prefixes for every compared checkpoint and for both the constraint and matched-neutral prompt. Exact cutoffs must be frozen before outcome analysis.
6. On each retained identical text history, evaluate two prompt arms:
   - the real CoT constraint;
   - a length/format-matched neutral instruction that does not impose the constraint.
7. Measure the induced shift in mechanically defined local compliance probability / short-horizon violation risk.

### Estimand

For checkpoint `c` and matched observable history `h`:

`G(c,h) = local_compliance(c, constraint, h) - local_compliance(c, neutral, h)`

The training quantity is the change in `G` across RL checkpoints, not raw compliance.

### Why this closes the old blocker

The old design required arbitrary teacher-forced shared prefixes and could therefore mistake checkpoint-specific OOD behavior for reduced control.

The revised design makes **overlap/common support an explicit inclusion criterion**. A prefix that later checkpoints assign abnormally low likelihood is not allowed into the matched-state causal comparison.

The “same state” claim is intentionally narrowed to **same observable text history on common support**. We do not claim hidden states are identical; changes in the internal state induced by changed weights are exactly part of the training effect under study.

## E01B — Natural-state constraint-refresh gain

E01B is an active control against any remaining teacher-forcing/common-support artifact.

For each checkpoint separately:

1. start from the normal prompt containing the CoT constraint;
2. let that checkpoint generate its **own natural trajectory**;
3. at preregistered positions while the trajectory remains constraint-compatible, fork the exact natural prefix;
4. append either:
   - a concise repetition of the original constraint, or
   - a token/format-matched neutral reminder;
5. measure the next `H` tokens / next reasoning segment with a mechanically checkable violation metric.

Primary horizons and insertion positions must be fixed before looking at the checkpoint trend. A no-reminder baseline may be recorded, but the load-bearing comparison is constraint-refresh minus neutral-refresh.

### Estimand

`R(c) = E[future_compliance | fresh constraint reminder, natural state] - E[future_compliance | neutral reminder, same natural state]`

This intervention uses states that the checkpoint itself actually visited. It therefore does not require cross-checkpoint teacher forcing.

### Why MathIF does not own E01B

MathIF already shows that bringing an instruction closer can improve obedience. L29 does **not** claim this intervention as new.

The new quantity is the **training curve of the intervention effect** on CoT continuation under a same-base reasoning-RL trajectory. MathIF does not establish whether this instantaneous steering gain is preserved or progressively lost during reasoning post-training.

---

## Constraint families and measurement

Use only pre-existing CoT-Control-style constraints with mechanically verifiable local behavior. Prioritize surface constraints for which short-horizon compliance has an unambiguous checker, e.g. case/style and selected information-suppression/addition families.

Before outcome analysis, freeze:

- the exact constraint families;
- prompt wording;
- common-support threshold;
- insertion positions / progress bins;
- short-horizon length(s);
- local compliance / violation checker;
- question subset;
- checkpoint subset;
- primary aggregation over questions rather than tokens.

Do not scan constraints and report the family with the best sign.

---

## Required triangulation / interpretation

### KEEP / RE-SELECT only if E01A and E01B agree

The intended positive signature is:

1. common-support same-history `G(c,h)` decreases materially with reasoning RL; **and**
2. natural-state refresh gain `R(c)` also decreases materially with reasoning RL.

Together these rule down both obvious alternatives:

- `E01A` rules down simple longer-trajectory opportunity accumulation at a matched external history;
- `E01B` rules down the claim that the matched-prefix result is merely teacher-forcing/OOD behavior.

Only this joint result authorizes a new selection pass for B-vs-C localization.

### KILL — local gain is stable

If E01A and E01B show roughly stable local gain while global controllability collapses, the opportunity/distance account wins for the present paper identity.

This is scientifically useful, but length/distance is already known and MathIF already shows that bringing constraints closer helps. Therefore **kill L29 as a Main paper** rather than publishing a fallback deconfounding study.

### KILL / RECONSTRUCT — only E01A falls

If common-support matched histories show lower gain but natural-state refresh does not, treat the result as a possible intervention-support artifact. The current training-induced local-controller claim is not established.

### KILL CURRENT CLAIM / NEW-CANDIDATE REQUIRED — only E01B falls

If natural-state refresh weakens but same-history gain is stable, the effect is better explained by training shifting models into less recoverable / more committed state distributions, not by reduced local gain at the same history. That may motivate a different future RQ, but it is **not L29** and must restart selection.

### KILL / HOLD — tiny or unresolved effect

If the checkpoint difference in the paired causal contrast is too small to resolve cheaply, stop. Do not enlarge the project into parent-scale stochastic sampling and do not rescue it with hidden-state statistics.

---

## External ownership and strongest reviewer compression

Primary owner stack:

1. **CoT-Control** — owns the phenotype, RL/test-time-compute/length trends, and open mechanism question.
2. **MathIF** — owns the reasoning/instruction trade-off and the result that moving a constraint closer can recover obedience.
3. **Compliance versus Sensibility** — owns static reasoning-prior-over-instruction behavior, internal encoding, and activation steering.
4. **ReasonIF** — owns reasoning-level instruction adherence and training-based improvement.
5. **Verifier-Induced Support Reshaping** — owns a related RLVR phenomenon where current-objective optimization reshapes later rewardable instruction-following support.

Strongest reviewer compression:

> **“CoT-Control already shows RL and length reduce controllability; MathIF already repeats constraints near the answer; Compliance-vs-Sensibility already shows reasoning priors override encoded instructions. This is those papers plus checkpointed logits.”**

The contribution survives only if E01 establishes the statement none of those works establishes:

> **Across a same-base reasoning-RL trajectory, the causal effect of the same explicit constraint on the next part of reasoning changes even after controlling both trajectory opportunity and intervention support; or, conversely, the effect remains stable and the training-induced global collapse can be attributed to accumulated opportunity/distance rather than a weakened local controller.**

The positive branch is the Main-level route. The stable-gain branch kills the paper because its substantive explanation is already too close to known distance/length effects.

Fresh 2026-09-12 owner search did not locate a paper that measures this same-base **training curve of local CoT constraint→continuation gain** with a common-support / natural-state intervention.

---

## Successful-result chain

Required chain:

> same-base RL checkpoints + common-support same-history intervention  
> + natural-state constraint-refresh intervention  
> → paired estimate of local constraint→policy causal gain  
> → gain falls with reasoning post-training beyond length/opportunity and OOD artifacts  
> → reasoning training changed the controller itself rather than only exposing the controller for longer  
> → only then: localize signal degradation vs intact-signal / policy-attractor override  
> → conditional account of when stronger reasoning becomes less steerable.

Failure modes:

- checkpoint trend in raw compliance only → insufficient;
- length-normalized endpoint score only → insufficient;
- “repeating instructions helps” → already owned / insufficient;
- probe decodability → insufficient;
- activation transplant → insufficient by itself;
- unrelated model-family comparison → not a training intervention.

---

## Resolution / feasibility

This remains intentionally unlike L19.

- **Training:** none for E01.
- **Models:** public OLMo-3/3.1 7B RL-Zero reasoning checkpoints; Ai2 explicitly releases RL-Zero series/checkpoints for scientific study.
- **Primary E01 quantities:** paired logit/probability or short-horizon causal contrasts, reducing stochastic evaluation noise.
- **Independent units:** questions / prefix states; tokens are not treated as independent replicates.
- **Mother-effect scale:** the published aggregate CoT controllability decline over RL is order-of-magnitude, not a marginal sub-noise phenotype.
- **Pilot compute:** expected to be single-digit GPU-hours to low tens of GPU-hours depending on number of checkpoints / natural continuations; no new model training.
- **Dry-run:** a small no-claim variance/support audit is allowed solely to freeze the MDE and common-support threshold before the main E01 analysis.
- **Stop rule:** if common support is too small or the causal-gain shift is only ~1 pp / requires large rollout budgets to resolve, stop rather than scale.

---

## Main-level growth path — NOT AUTHORIZED YET

If and only if E01A+E01B jointly show a real training-induced local-gain decline, re-run selection before doing any of the following:

1. **Mechanistic localization:** constraint-signal degradation vs intact signal with reduced policy leverage.
2. **Training-stage boundary:** Base/SFT/DPO/RL or RL-Zero domain paths where scientifically matched.
3. **Prediction:** whether local gain predicts late-reminder recoverability, constraint persistence, or CoT-vs-output controllability divergence.
4. **Scope:** second open model flow only if required by the eventual claim.

No part of this list is authorized by the current pilot verdict.

---

## Current verdict

The bounded E01 audit was completed on 2026-09-13. Shared/common-support and
checkpoint-natural comparisons were feasible, but the exact-word suppression
intervention failed the early-gain validity gate. An initially apparent 6.25 pp decline
was caused by a neutral suffix that retrieved the original rule. Target-matched,
structural, and target-free anaphoric controls did not yield robust positive early
control gain. See `notes/E01_PILOT_REPORT.md` for the complete result chain.

```yaml
natural_question: PASS
mother_phenomenon: PASS_STRONG
replication_risk: LOW
broad_parent_novelty: FAIL_ALREADY_OWNED
narrow_training_causal_quantity: PLAUSIBLE_INDEPENDENT_CONTRIBUTION
closest_owner_density: HIGH
causal_estimand: LOCKED_FOR_E01
old_identification_blocker: COMMON_SUPPORT_FEASIBLE
current_identification_blocker: FINAL_BALANCED_BINARY_INSTRUMENT_GATE
successful_result_test: PASS_ONLY_IF_E01A_AND_E01B_AGREE
outcome_identity: LOCKED_WITH_KILL_ON_STABLE_GAIN_OR_DISAGREEMENT
resolution_risk: SECONDARY_TO_INSTRUMENT_INVALIDITY
training_cost: NONE_FOR_E01
pilot: E01R_EARLY_INSTRUMENT_DEVELOPMENT_ONLY
verdict: RECONSTRUCT_AUTHORIZED_ONE_FINAL_AUDIT
```

# **RECONSTRUCT-AUTHORIZED — ONE FINAL INSTRUMENT AUDIT**

The paper mainline remains **not approved**. E01R may run one early-checkpoint
instrument-development gate using fresh balanced-binary local control. Persistent
suppression is permanently closed. If both case and tag families pass the frozen gate,
E01R-A/B may proceed on untouched questions; otherwise L29 is killed without another
reconstruction. Hidden-state mechanism, steering, new training, and broader model
sweeps remain unauthorized. See `notes/E01R_DESIGN.md`.
