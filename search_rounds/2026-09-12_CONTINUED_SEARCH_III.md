# 2026-09-12 — Continued Topic Search III

**Target:** ACL / EMNLP / NAACL Main  
**Search mode:** mechanism-first; stable phenomenon before method; no survivor quota.  
**Repository state at round start:** `main` = `442672051334a4e9119ddd6af0648b3f2aabaeb4`.

This round deliberately avoided the data / benchmark / RAG / metric / workflow generators that had dominated earlier search. The search budget went to stable reasoning anomalies, post-training transitions, representation→causal-use gaps, and strong mechanistic claims with weak direct causal identification.

## Hooks investigated and rejected

### 1. Math reasoning strength → instruction-following loss

**Hook:** Why do stronger reasoning models become worse at obeying simple instructions while solving the same problem?

**Mother:** Fu et al., *Scaling Reasoning, Losing Control: Evaluating Instruction Following in Large Reasoning Models*, ACL 2026 Main (MathIF).

**Why not as a paper identity:** the broad trade-off is already directly owned. MathIF reports degradation after reasoning-oriented SFT/RL and with longer generation, and simple instruction repetition/constraining can partially recover obedience. ReasonIF and adjacent 2026 work further occupy the general reasoning-vs-instruction-following phenotype. A generic mechanism follow-up would immediately reviewer-compress to “MathIF plus another diagnostic.”

**Verdict:** DROP broad parent. It supplied pressure for the narrower survivor below.

### 2. Earlier reasoning state had the right answer, final state lost it

**Hook:** Are final reasoning errors caused by information being erased, or by later trajectory dynamics overriding an earlier correct state?

**Mother:** ACL 2026 work on temporal sampling / forgotten reasoning reports that many final failures were solved at earlier checkpoints in the same trajectory.

**Why not:** the erased-vs-suppressed / detection-vs-repair / revision neighborhood is already dense, and the mother work itself turns earlier-state recovery into the central object. The remaining cells increasingly reduce to a particular intervention on an already-owned trajectory phenomenon.

**Verdict:** DROP.

### 3. Negative reasoning samples improve OOD generalization

**Hook:** Why can training on wrong reasoning traces improve generalization rather than merely teach errors?

**Mother:** *Learning from Mistakes: Negative Reasoning Samples Enhance Out-of-Domain Generalization*, ACL 2026 Main.

**Why not:** the parent already centralizes the explanation through diversity / optimization / inference analyses. A causal-ingredient decomposition would be an expected ablation program with nontrivial training cost, not a clearly independent scientific parent.

**Verdict:** DROP.

### 4. Reasoning enhancement amplifies tool hallucination

**Hook:** Why does stronger reasoning sometimes make a model more willing to invoke unavailable tools?

**Why not:** 2026 work already makes this exact anomaly and mechanistic analysis the focal object. It is also in a currently deprioritized tool/workflow neighborhood.

**Verdict:** DROP / direct owner.

### 5. Detecting a reasoning mistake but failing to repair it

**Hook:** Why can a model recognize its own error without correcting the continuation?

**Why not:** 2026 self-correction work already separates recognition from repair and includes internal-state / intervention analyses. The generic recognition→repair gap is too crowded.

**Verdict:** DROP.

### 6. The model knows the fact but chooses a shortcut

**Hook:** When an answer-relevant fact is available internally, what decides whether the model actually uses it rather than a popularity/order/co-occurrence shortcut?

**Why not:** recent work already makes selective factual use / shortcut choice the central explanation and shows reliability-conditioned behavior. The remainder overlaps prior representation→readout / latent→policy routes already rejected in this project.

**Verdict:** DROP.

---

# Survivor after owner search — training-induced loss of local CoT control

## Search-stage hook

> **When reasoning post-training makes a chain of thought dramatically less controllable, is the model merely reasoning for longer and accumulating more chances to violate the constraint, or has training actually weakened the constraint’s causal control over the reasoning policy?**

Mother phenomenon: Yueh-Han Chen et al., *Reasoning Models Struggle to Control their Chains of Thought* (ICML 2026 / arXiv:2603.05706).

The mother phenomenon is unusually strong for a mechanism project:
- CoT controllability is far below output controllability across 13 reasoning models;
- models often explicitly notice that they are violating the requested CoT constraint and nevertheless continue;
- controllability worsens with longer reasoning / more test-time compute, problem difficulty, and additional reasoning-oriented RL;
- the paper explicitly states that the mechanism behind low controllability is not well understood;
- open OLMo model-flow checkpoints expose training trajectories rather than only unrelated endpoint models.

## Why the obvious version is already dead

A broad question such as

> “Is the instruction absent internally, or represented but ignored by the reasoning policy?”

is **not new enough**.

Tan et al., *Compliance versus Sensibility: On the Reasoning Controllability in Large Language Models* (arXiv:2604.27251), already shows that instructed reasoning types remain decodable in middle-to-late layers, models prioritize task-appropriate internal reasoning patterns over explicit conflicting instructions, and activation steering can increase compliance by up to 29%.

Likewise, MathIF / ReasonIF already own the broader observation that stronger/longer reasoning can degrade instruction adherence.

Therefore this candidate survives only if its paper identity is the **training-transition causal quantity**, not static “represented-but-unused” diagnosis and not another activation-steering paper.

## Length is also not the novelty

OpenAI deployment system cards now explicitly state that CoT controllability is heavily confounded by CoT length and report controllability conditional on length. Therefore:

> “the aggregate metric drops because trajectories get longer”

would be a measurement correction, not a sufficient new paper, and it points back toward the low-priority evaluation neighborhood.

The open scientific remainder is instead:

> **At the same reasoning state / prefix, does the same explicit constraint exert less causal influence on the continuation policy after reasoning post-training?**

## Competing accounts

### A — Opportunity accumulation / trajectory-length account
Training does not materially weaken local constraint responsiveness. Global exact-control success falls because longer trajectories expose the model to more opportunities for a first violation.

### B — Constraint-signal degradation
At matched trajectory state, the instruction/constraint has become less available or less stably represented after training, reducing its influence on continuation.

### C — Policy-gain / attractor override
The constraint remains represented/diagnosable, but outcome-trained reasoning dynamics increasingly dominate action selection. The same constraint therefore has lower causal gain on the continuation policy.

B and C should only be distinguished after first ruling out A behaviorally. A probe alone cannot support C.

## Decisive operation under audit

The cheapest useful experiment is **not** full-trace exact success. It is a matched-state causal-sensitivity test across public checkpoints.

Candidate E01 design:
1. choose several checkpoints along one OLMo RL-Zero reasoning trajectory from the same base model;
2. use the same questions and a short constraint-compatible prefix/state;
3. teacher-force the same state into each checkpoint;
4. intervene only on the explicit CoT constraint (constraint present vs matched neutral/control wording);
5. measure the induced change in locally compliant next-token probability mass and a short continuation compliance measure;
6. repeat at multiple trajectory positions and with pre-specified surface constraints where local compliance is mechanically identifiable;
7. separately verify the same direction on natural pre-violation states so the conclusion does not rest solely on an OOD shared prefix.

The load-bearing estimand is the **local constraint→policy causal gain at a matched reasoning state**, not aggregate benchmark accuracy and not a hidden-state probe.

### Identification blocker that remains

A shared teacher-forced prefix can itself be off-distribution for later checkpoints. If the local causal contrast changes simply because the forced state is unnatural, the intended training-causal inference fails.

Before compute, the design must lock a prefix/state construction for which:
- semantic/reasoning content is identical across the intervention arms;
- the state is valid under both constraint and neutral conditions;
- natural-trace replication is available as an active control;
- the measured compliant-token set has an unambiguous local interpretation.

If this cannot be achieved without inventing a bespoke diagnostic whose meaning changes with the result, kill the route.

## Closest-owner compression

Strongest reviewer compression:

> “CoT-Control already shows RL + longer reasoning reduce control; Compliance-vs-Sensibility already shows instructions are encoded but internal reasoning priors win and steering restores compliance; MathIF/ReasonIF already show reasoning/instruction trade-offs. This is those papers plus checkpointed activation/logit analysis.”

The only substantial surviving contribution is:

> **None of those results identifies whether reasoning training changes the causal gain from an explicit constraint to the continuation policy at a fixed reasoning state, separately from increased trajectory length; nor whether any such training-induced gain loss first reflects signal loss or policy override.**

If the study cannot maintain this inference, it is not Main-level.

## Pre-result outcome interpretations

- **A: matched-state causal gain stays stable across training.** This favors opportunity accumulation / length as the main explanation. Scientifically interpretable, but because length confounding is already known and reported by system cards, this likely **kills the candidate as a paper** rather than becoming a fallback identity.
- **B: matched-state causal gain falls clearly across training.** This establishes a training-induced computation change beyond length exposure and permits the pre-registered representation-loss vs policy-gain localization program.
- **C: heterogeneous shift by a pre-specified constraint family or training domain.** Keep only if the conditioning axis is motivated before E01; otherwise re-select rather than narratively rescue.
- **Decisive null / unresolved tiny effect.** Kill or hold on resolution; do not switch to generic hidden-state statistics.

## Feasibility / resolution

This route is inference-first, not training-first.

- OLMo 3 releases fully open RL-Zero series and checkpoints from the same base model across math, code, instruction following and general chat.
- The parent’s endpoint controllability changes are very large (often order-of-magnitude), unlike L19’s small downstream transfer effect.
- A logit-based local causal contrast can be measured deterministically on hundreds of independent question-prefix units before using stochastic rollouts.
- With 7B checkpoints, the bounded audit/pilot should be single-digit GPU-hours on the available hardware, not a 100–300 GPU-hour training program.
- If the matched-state effect is below roughly the low-single-percentage-point scale and cannot be resolved cleanly on hundreds of units, the mechanism is unlikely to support the intended Main-level claim and should be stopped early.

## Main-level growth path if E01 is positive

1. **C1 — Training effect:** show that reasoning post-training weakens local constraint→policy control even at a matched reasoning state, beyond trajectory-length exposure.
2. **C2 — Localization:** distinguish constraint-signal degradation from intact-representation / reduced-policy-gain using causal restoration/corruption with active controls.
3. **C3 — Training boundary:** determine whether the change appears in SFT, preference optimization, outcome RL, or only particular RL domains using the OLMo model flow.
4. **C4 — Consequence/prediction:** test whether the estimated local control gain predicts late-reminder / steering recoverability and the native-CoT versus output/external-reasoning controllability gap.

Each claim deepens the same question; none should become an independent fallback paper if C1 fails.

## Formal selection verdict

```yaml
name: Losing the Steering Gain
class: mechanism / training-transition
mother_phenomenon: PASS_STRONG
natural_question: PASS
broad_parent_novelty: FAIL_ALREADY_OWNED
narrow_training_causal_quantity: PLAUSIBLE_INDEPENDENT_CONTRIBUTION
closest_owner_density: HIGH
anti_resurrection: PASS_NARROW_ONLY
successful_result_test: PASS_IF_MATCHED_STATE_CAUSAL_GAIN_IS_IDENTIFIED
outcome_identity_stability: PASS_WITH_PREDECLARED_KILL_ON_STABLE_GAIN
resolution: LIKELY_TRACTABLE_INFERENCE_ONLY
primary_blocker: MATCHED_STATE_INTERVENTION_MUST_NOT_BE_AN_OOD_TEACHER_FORCING_ARTIFACT
pilot: NOT_AUTHORIZED
verdict: SERIOUS_PRE_PILOT
```

Promote to a candidate record, but authorize **no compute** until the matched-state intervention / inference bridge is locked. Do not turn the route into a length-normalized benchmark paper or a generic activation-patching study.
