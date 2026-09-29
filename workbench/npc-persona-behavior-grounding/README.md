# NPC Persona-to-Behavior Grounding — Workbench

**Lane: our-taste. Status: exploratory workbench — not a candidate.**

## Territory

This workbench studies a game-specific question that appears once NPC persona moves beyond dialogue style into action policy:

> **When a designer supplies a natural-language persona, does its semantics causally and predictably change the NPC's game decisions, or does the system mainly produce trajectories that are distinguishable under its own persona/reward/evaluator machinery?**

The object is **behavioral grounding of persona**, not generic role-playing quality, dialogue persona consistency, or another Big-Five classifier.

A useful NPC claim must survive where the NPC is actually used: in actions, state transitions, task trade-offs, social choices, and long-run trajectories.

No final RQ or method is registered.

---

## Why this territory is worth inhabiting

### Field-level pressure

*AI for Games in the Foundation Model Era* (2026) repeatedly separates:
- what structure/control is supplied by the game;
- what the AI actually produces;
- whether an output/capability transfers to the downstream setting;
- what evidence supports the claim in the setting where the output is used.

For a behavioral NPC, a persona embedding or persona-identification score is therefore not automatically evidence that the **policy's decisions** are semantically persona-grounded.

The broader game-agent surveys also decompose role-play, memory, reasoning, perception/action, and learning rather than treating “NPC quality” as one scalar. Recent player studies further show that functional competence can dominate perceived character quality.

### Parent lineage

1. **Explicit behavioral personality RL (2024–2025).**
   OCEAN/personality is implemented through inspectable behavior/reward definitions. This is rigid, but the trait→behavior contract is explicit.

2. **Stack More Levels: How to Get General and Human-like Mario Playing (CoG 2026).**
   Runner / killer / collector playstyles are shaped through concrete game rewards, then PPO→DRAIL uses human demonstrations. Persona preservation is measured in actual game outcomes such as kill/coin behavior. Code, checkpoints, PCG levels and demonstrations are public.

3. **One Policy, Infinite NPCs / PCSP (2026).**
   A much more flexible formulation: free-form persona text is encoded once with a frozen Qwen embedding and conditions one shared PPO policy. The paper reports strong zero-shot trajectory-to-persona identification, semantic-behavioral alignment, external Melting Pot validation and UE5 deployment.

PCSP is the strongest practical starting substrate because it makes natural-language persona a direct policy input and releases unusually complete code/evaluation artifacts.

---

## The pressure exposed by the strong baseline

The current PCSP repository contains later audits that materially narrow the headline interpretation.

### 1. Internal persona traceability does not reproduce as independent behavioral advantage

The repository's independent evaluator uses only environment trajectories, not PCSP's learned persona projection, logits, or trajectory encoder.

On v3-large, across full vs no-consistency policies:

- action-only Big-Five balanced accuracy: **0.482 full vs 0.511 no-consistency**;
- paired bootstrap full-minus-no-consistency: **[-0.056, -0.002]**;
- action+state-response features: **0.556 vs 0.558**;
- most independently recoverable action-only signal is extraversion;
- conscientiousness is below chance after the held-out distribution shift.

The repository itself therefore states the defensible claim narrowly: InfoNCE is load-bearing for alignment between the learned trajectory encoder and persona projection, but the independent probe does not show a behavioral advantage.

### 2. Persona information is heavily compressed before the policy

The projection audit reports:

- raw Qwen Big-Five probe: **0.898** mean balanced accuracy;
- projected embedding: **0.799**;
- raw/projected pairwise cosine correlation: **rho = 0.404**;
- numerical rank 16 and effective rank **3.87**.

This does not prove a problem, but it provides an observable bottleneck candidate.

### 3. The consistency objective has no direct actor-head gradient path

The gradient-path audit shows:

- PPO → projection + actor + critic;
- InfoNCE consistency → projection + trajectory encoder;
- InfoNCE → **no direct actor-head path**.

Any action-policy effect from InfoNCE is indirect through the shared projection.

### 4. Persona is encoded twice: policy conditioning and environment/reward

Source inspection reveals an especially important attribution issue.

A persona record contains:
- free-form persona text / Qwen embedding;
- Big-Five labels;
- `preferred_actions`;
- `decay_modifiers`.

Mini-Inzoi v3 then uses persona metadata directly:
- preferred action: **+0.5 reward**;
- action-style / Big-Five cosine: **0.3-weight style reward**;
- social reward depends on Big-Five compatibility;
- decay modifiers change need dynamics.

Thus training correlates two persona channels:

> **language persona → policy conditioning**

and

> **structured persona → reward / environment dynamics**

Observed persona-specific trajectories can therefore reflect both. Existing headline evaluation does not by itself identify how much causal behavioral control comes from the language-conditioned policy channel.

This is not being treated as a paper claim yet. It is the first thing the workbench should try to falsify.

---

## Ownership boundaries

Already active / owned; do not repackage:

- better persona prompting for dialogue;
- static or dynamic persona consistency in LLM role-play;
- memory for role-playing characters;
- generic “persona vs task utility” trade-off;
- Big-Five dialogue classification;
- “natural-language persona should condition an NPC”;
- one shared policy for many NPCs;
- trajectory-to-persona identification;
- explicit OCEAN reward shaping by itself.

The workbench is only interesting if **semantic persona control of game behavior** behaves differently from these existing proxies.

---

## Strong executable substrate

Primary baseline:

**yoosunghong/pcsp**
- https://github.com/yoosunghong/pcsp
- https://arxiv.org/abs/2605.23652

Useful assets already present:
- Mini-Inzoi v1/v2/v3/v3-large environments;
- 300/500-persona datasets;
- Qwen persona embeddings;
- full / no-consistency and other ablation pipelines;
- independent behavior evaluator;
- persona-projection audit;
- attributable-gradient audit;
- Melting Pot experiments;
- UE5 bridge and telemetry.

Secondary behavioral comparator:

**carrotoxic/mario-personas**
- https://github.com/carrotoxic/mario-personas

Use it as a conceptual/control baseline for explicit action-grounded playstyles, not as proof that PCSP is wrong.

---

## Baseline residency

Do not invent a new loss at entry.

### B0 — Reproduce the repository's own current evidence

1. pin the PCSP repository commit used for the workbench;
2. run environment/unit tests;
3. regenerate or verify the committed independent-behavior metrics;
4. reproduce full vs no-consistency rollouts from existing checkpoints where available;
5. reproduce the persona-projection and gradient-path audits;
6. confirm action/reward semantics from source rather than paper prose.

If the current repo results are not reproducible, stop and resolve the baseline first.

### B1 — Fixed-state persona intervention

Hold fixed:
- policy weights;
- exact observation/state;
- random seed where sampling is used.

Change only the persona embedding supplied to the policy.

For the same state (s), evaluate:

[
pi(a mid s, e_{p_1}) quad 	ext{vs} quad pi(a mid s, e_{p_2})
]

Do this before rolling the environment forward.

This directly asks whether the learned policy is causally sensitive to persona at the decision surface.

Measure:
- logit/action-distribution delta;
- JS/KL/TV distance;
- top-action flips;
- semantic action-group shifts;
- sensitivity by trait axis and state type.

A large difference is not automatically good: direction and semantic relevance matter.

### B2 — Cross the two persona channels

Construct a 2×2-style counterfactual:

- policy embedding (p), environment persona config (p);
- policy embedding (q), environment config (p);
- policy embedding (p), environment config (q);
- policy embedding (q), environment config (q).

Use matched initial state/seeds.

Separate:
- **one-step action choice**, before persona-specific environment dynamics can diverge;
- **multi-step behavior**, where decay/reward/dynamics can accumulate.

This is the key attribution test.

### B3 — Neutral-environment evaluation

At evaluation time, neutralize persona-specific environment channels:
- common decay modifiers;
- no preferred-action bonus;
- no Big-Five style reward;
- common/neutral social reward.

Then vary only the policy persona embedding.

Do not retrain first.

Question:
> does the already-trained policy still express semantically meaningful persona differences when the environment is no longer helping manufacture them?

### B4 — Semantic intervention controls

Use three perturbation classes:

1. **Paraphrase:** same persona meaning, changed wording/language realization.
2. **Semantic opposite / axis edit:** minimally alter one behavioral trait while holding occupation/age/rest fixed.
3. **Nuisance edit:** occupation/age/name/style changes that should not dominate the claimed personality behavior.

Desired scientific object is not high sensitivity. It is a sensible combination of:
- invariance to irrelevant rewrites;
- sensitivity to behaviorally meaningful changes.

### B5 — Trait-relevant state slices

Avoid global trajectory classification as the only readout.

Ask whether persona effects appear **where a trait has an affordance to matter**.

Examples grounded in the existing action ontology:
- social opportunity vs no nearby agents;
- work need / available work affordance;
- leisure/rest alternatives;
- exploration/novelty choices;
- cooperative vs selfish action opportunities where supported.

Do not invent a new synthetic benchmark at the beginning. Use existing environment states and interventions.

### B6 — Task-pressure sweep

Increase urgency / depleted needs / task reward pressure and measure whether persona-conditioned behavior:
- remains stable;
- becomes selectively suppressed only when rational;
- collapses immediately to the same high-reward policy.

This can distinguish “persona as real policy preference” from “persona as weak decoration that disappears under task pressure.”

---

## First decision ladder

### Outcome A — embedding swaps cause strong, semantically correct, state-appropriate action changes

The strong baseline survives.

Do **not** invent a method. Narrow the concern and likely stop this workbench unless another robust failure appears.

### Outcome B — trajectory identity is strong, but fixed-state embedding swaps barely affect action choice

Then persona traceability is not equivalent to persona control. Investigate what channel creates the traceability before proposing any fix.

### Outcome C — embedding changes actions strongly, but directions are arbitrary / nuisance-sensitive

Then the bottleneck is semantic grounding, not sensitivity.

### Outcome D — persona effects exist only while persona-coded reward/dynamics are active

Then the environment may be doing more of the behavioral work than the natural-language conditioning.

### Outcome E — one or two traits work while others collapse

Do not average them into one “persona score.” Determine whether the action ontology/environment affords each trait, or whether the learned projection selectively discards dimensions.

### Outcome F — behavior is grounded but collapses only under task pressure

Then the scientifically useful object may become the competence/persona Pareto boundary and how a policy should arbitrate contextually.

---

## Method permission

**No new method at entry.**

A method is allowed only after evidence supports:

> proxy/behavior mismatch  
> → attributable bottleneck  
> → controllable action surface  
> → minimal intervention  
> → better independent behavior without sacrificing task competence

Possible intervention families are intentionally not registered. Do not pre-commit to:
- another contrastive loss;
- a new persona encoder;
- trait reward shaping;
- a learned evaluator;
- a router / mixture-of-personas;
- human feedback.

If a simple evaluation correction dissolves the issue, stop.

---

## Feasibility

The first gates are cheap:

- no foundation-model training;
- existing persona embeddings;
- small discrete-action environments;
- existing full/no-consistency policies and evaluation code/results;
- fixed-state action-logit analyses are inference-only;
- environment/reward neutralization is a small code intervention;
- later PPO retraining, if justified, is tiny relative to LLM/VLA training.

The user's available GPU resources are more than sufficient for the baseline scale; GPU cost should not be the research bottleneck.

---

## Major risks / kill conditions

Stop or downgrade if:

- the published/current PCSP checkpoints or metrics cannot be reproduced;
- the apparent mismatch is only a bug in the independent probe;
- counterfactual persona swaps reveal strong semantic control and no meaningful failure remains;
- all interesting effects depend on Big-Five labels / hand-coded action semantics and do not generalize beyond the toy ontology;
- a nearest prior is found that already disentangles language persona conditioning from persona-coded environment/reward with causal action interventions;
- solving the problem requires large-scale human annotation before a basic behavioral signal exists;
- the workbench degenerates into “design a better persona metric” without changing our understanding of NPC policy behavior.

Also remember that PCSP is currently a frontier/preprint artifact rather than a field-standard benchmark. Its exceptional openness makes it a good workbench substrate, but the scientific object must eventually survive beyond one implementation.

---

## Why this fits our taste

This territory begins from a strong runnable baseline rather than an invented module.

Its current shape is:

> **successful method + strong internal metric**  
> → **independent readout disagrees**  
> → **source audit reveals entangled persona channels**  
> → **cheap causal intervention can re-attribute the behavior**  
> → only then, if needed, a minimal method may emerge.

That is exactly the desired baseline-first / exploration-first research process.

---

## Paper identity

None.

The workbench may end after the first counterfactual audit. It earns promotion only if a simple, externally meaningful behavioral regularity survives strong controls and leads to a clearer problem than “persona consistency.”
