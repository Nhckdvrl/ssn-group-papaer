# NPC Persona → Behavior Grounding

**Lane:** our-taste  
**Stage:** FROZEN / NOT ACTIVE after 2026-09-29 top-conference ceiling audit  
**Primary baseline:** `yoosunghong/pcsp` at `5420f7b4fa0fdb6110e131402af9f5386ce2d0cf`

## 0. Venue-scale audit

The causal distinction here is potentially broader than games:

> persona/conditioning information is decodable or trajectory-traceable ≠ it causally and semantically controls the policy's decisions.

However, the current evidence and planned experiments are dominated by one artifact (PCSP / Mini-Inzoi). PCSP itself already reports validation across Mini-Inzoi, Melting Pot, and UE5, while 2026 persona-policy work is expanding toward selection/realization and context-dependent persona policies.

A top-conference paper cannot be justified merely by finding a confound or weaker behavioral grounding in this one implementation.

**Decision:** freeze before further execution.

**Reopen condition:** first identify at least one independent conditioned-policy substrate (ideally outside game NPCs) where the same proxy-vs-causal-control distinction is meaningful and machine-testable. Only then may PCSP serve as one substrate in a broader study. If no second substrate exists, retain this as a useful PCSP audit rather than a paper workbench.

## 1. Why this is a game-NPC problem

Foundation-model NPC research is moving from “an NPC can talk in character” toward characters that **perceive game state, make decisions, act, cooperate, pursue goals, and remain recognizably themselves while doing so**.

For that setting, persona is not only a dialogue property. A designer may describe an NPC as social, cautious, diligent, impulsive, exploratory, selfish, cooperative, etc. If persona is meaningful for gameplay, it should affect **what the NPC actually chooses to do in relevant game states**.

This workbench therefore studies:

> **Does a natural-language NPC persona causally and semantically control game behavior, or can a system appear persona-consistent mainly because its trajectories, rewards, environment dynamics, or learned evaluator make personas easy to distinguish?**

The unit of interest is an **NPC decision in a game state**, not an isolated utterance and not a persona-classification score.

This is separate from the repository's `npc-deception-investigability/` workbench. That line studies deceptive claims as playable world state; this line studies **persona grounding in NPC action policies**.

No final RQ, method, or expected result is registered.

---

## 2. Related work and the lineage we are entering

### Field map: AI for Games in the Foundation Model Era

*AI for Games in the Foundation Model Era* (2026) is the main field-level map. Its useful lesson for NPC research is to ask:

- what state/rules/control come from the game;
- what the model actually controls;
- whether an upstream capability survives in downstream play;
- what evidence supports the claim in the setting where the NPC is actually used.

This matters because “persona is present in an embedding” and “persona changes the NPC's decisions” are different claims.

Other recent game-agent / AI-native-game surveys make the same general boundary visible: role-play, memory, reasoning, perception/action, learning, game state, and player experience are separate components. “NPC quality” is not one scalar.

### Dialogue and role-play persona

Generative Agents, CoSER/DMT-RoleBench/RMTBench, PersonaArena, PersonaEval, Memory-Driven Role-Playing and related work make dialogue/persona fidelity a mature research area.

Important consequence for us:

> **“Make NPC dialogue more persona-consistent” is not the research question here.**

Likewise, better memory or better persona prompting is not novelty by itself.

### Explicit behavioral persona

Older personality-RL work encodes OCEAN/personality through explicit game rewards and behaviors. This is restrictive, but the trait→behavior contract is inspectable.

A useful modern comparator is:

**Stack More Levels: How to Get General and Human-like Mario Playing (IEEE CoG 2026)**

- runner / killer / collector playstyles;
- persona rewards tied to concrete game outcomes;
- PPO followed by DRAIL with human demonstrations;
- public code, checkpoints, PCG levels and demonstrations.

This gives us a strong conceptual contrast:

> explicit behavioral persona = inflexible but behaviorally interpretable  
> free-form language persona = flexible, but behavioral grounding must be demonstrated

### PCSP: the primary strong baseline

**One Policy, Infinite NPCs / PCSP (2026)** is our main executable parent.

It conditions a shared PPO policy on frozen Qwen persona embeddings and reports strong persona traceability / semantic-behavior alignment, zero-shot evaluation, external validation, and UE5 deployment.

The public repository is unusually valuable because it also contains later audits that weaken a simple interpretation of the headline results.

#### Independent behavioral audit

Using a model-independent evaluator over actual trajectories:

- action-only Big-Five balanced accuracy: **0.482 full vs 0.511 no-consistency**;
- bootstrap CI for full − no-consistency: **[-0.056, -0.002]**;
- action + state-response: **0.556 vs 0.558**;
- most action-only recoverable trait signal is extraversion;
- conscientiousness falls below chance under the held-out shift.

So InfoNCE is clearly important for the learned trajectory↔persona representation metric, but the current independent audit does **not** show that it improves independently observable Big-Five behavior.

#### Projection audit

The learned persona projection remains informative but heavily compresses the original text embedding:

- raw Qwen Big-Five probe: **0.898**;
- projected embedding: **0.799**;
- raw/projected cosine-geometry correlation: **rho = 0.404**;
- effective rank: **3.87**.

This is a diagnostic clue, not yet a causal explanation.

#### Gradient-path audit

The InfoNCE consistency loss updates:

- persona projection;
- trajectory encoder;

but has **no direct gradient path to the actor head**.

Any behavioral effect must therefore be mediated indirectly through the shared persona projection.

#### Source-level attribution issue: persona enters twice

PCSP's persona record contains both:

1. **language-side information**
   - free-form persona text;
   - Qwen persona embedding;

2. **game-side structured information**
   - Big-Five labels;
   - `preferred_actions`;
   - `decay_modifiers`.

Mini-Inzoi v3 directly uses the structured persona in the game:

- preferred action: **+0.5 reward**;
- action-style / Big-Five cosine: **0.3-weight style reward**;
- social reward depends on Big-Five compatibility;
- `decay_modifiers` change need dynamics.

So persona is correlated across two channels:

> **persona text → policy conditioning**

and

> **persona metadata → reward / environment dynamics**

This makes PCSP a particularly good workbench: the model is strong and open, but the causal source of persona-specific behavior is not yet cleanly isolated.

---

## 3. What we want to learn

We are **not** assuming PCSP is wrong.

The first goal is to identify what is actually load-bearing.

We want to explore:

1. **Causal sensitivity**  
   Does swapping only the persona embedding change the action distribution at the same game state?

2. **Semantic correctness**  
   If actions change, do they change in the direction implied by the persona, rather than arbitrarily?

3. **State dependence**  
   Does a trait matter specifically when the game affords that trait expression?

4. **Channel attribution**  
   How much persona-specific behavior comes from the policy embedding versus persona-specific reward/dynamics?

5. **Robustness to wording**  
   Are semantically equivalent persona descriptions behaviorally equivalent?

6. **Sensitivity to meaningful edits**  
   Do controlled persona changes alter the corresponding behavior?

7. **Nuisance sensitivity**  
   Do irrelevant edits such as occupation, age, wording, or language style alter behavior more than the intended persona semantics?

8. **Trait heterogeneity**  
   Are some dimensions genuinely grounded while others are mostly absent or not afforded by the action space?

9. **Task pressure**  
   Does persona survive meaningful gameplay pressure, or disappear as soon as reward urgency increases?

10. **Long-horizon expression**  
    Can a small one-step persona effect accumulate into recognizable long-run play, or do environment dynamics dominate?

11. **Proxy validity**  
    Which existing metrics actually predict real persona-conditioned game decisions, and which mainly measure representation traceability?

12. **Generalization beyond one toy environment**  
    If we discover a stable phenomenon in Mini-Inzoi, does the same distinction appear in an explicit behavioral-persona substrate such as Mario-personas or another NPC environment?

These are exploration axes, not twelve paper RQs.

---

## 4. Experimental plan

### Phase 0 — Baseline residency

Before adding anything new:

- clone and pin PCSP at `5420f7b4fa0fdb6110e131402af9f5386ce2d0cf`;
- document environment/package setup;
- run the repository's smoke/unit tests;
- verify the committed independent-behavior result;
- verify persona-projection audit;
- verify gradient-path audit;
- inspect the exact persona dataset, action ontology, reward terms and environment dynamics;
- record which published/current checkpoints are actually available.

If the current evidence cannot be reproduced, resolve that first.

### Phase 1 — Fixed-state persona swap

This is the first high-information experiment.

For a fixed trained policy and the **same observation** (s), replace only the persona embedding:

[
pi(a|s,e_p) quad 	ext{vs.} quad pi(a|s,e_q)
]

No environment rollout is needed initially.

Measure:

- JS / KL / total-variation distance;
- action-logit delta;
- top-action flips;
- rank changes;
- semantic action-group changes.

Run across:

- many personas;
- multiple policy seeds;
- full and no-consistency variants;
- representative naturally occurring states.

Then slice by trait axis and state type.

**Interpretation:** high sensitivity is not sufficient. The change must be semantically appropriate.

### Phase 2 — Counterfactual persona-channel crossing

Disentangle the two persona channels.

For persona pair `p, q`, evaluate combinations of:

- policy embedding `p`, environment persona `p`;
- policy embedding `q`, environment persona `p`;
- policy embedding `p`, environment persona `q`;
- policy embedding `q`, environment persona `q`.

Do this first at one step, then in matched-seed rollouts.

This separates:

- policy-conditioning effect;
- reward/dynamics effect;
- interaction between them.

### Phase 3 — Neutral-environment evaluation

At **evaluation time only**, create a neutral environment:

- common decay modifiers;
- remove preferred-action bonus;
- remove Big-Five style reward;
- neutralize persona-specific social compatibility reward where appropriate.

Do not retrain yet.

Vary only the policy persona embedding.

Question:

> Does the trained policy still express persona when the game stops directly rewarding / inducing persona-specific behavior?

### Phase 4 — Semantic persona interventions

Construct controlled persona pairs.

#### 4.1 Paraphrase invariance

Same personality meaning, different wording.

Desired behavior: small policy change.

#### 4.2 Single-trait edit

Change one behavioral dimension while keeping other content fixed.

Desired behavior: selective change in states where that dimension matters.

#### 4.3 Semantic opposite

Use clear oppositions where the existing environment has an affordance, e.g. more social ↔ less social or more planned ↔ more spontaneous.

#### 4.4 Nuisance edits

Change occupation, age, phrasing, language/register, or irrelevant biography while preserving intended behavioral traits.

Desired behavior: nuisance effect smaller than semantic persona effect.

Do not manufacture a large synthetic benchmark yet. Start with a small hand-audited intervention set.

### Phase 5 — Trait-relevant state slicing

Persona should not affect every state equally.

Use actual Mini-Inzoi states to create/collect slices such as:

- social opportunity present / absent;
- work opportunity and work need;
- rest/leisure alternatives;
- novelty/exploration opportunity;
- repeated-action vs alternative-action states;
- high vs low need pressure.

For each state family ask:

> Is the persona effect strongest where that trait can actually alter a meaningful NPC decision?

This is more important than a global persona classifier.

### Phase 6 — Task-pressure sweep

Systematically increase gameplay pressure:

- depleted needs;
- urgency;
- reward asymmetry;
- reduced availability of preferred actions;
- competing task demands.

Track:

- task reward;
- persona-sensitive action effect;
- independent behavioral readout.

Possible patterns include:
- persona survives robustly;
- persona is rationally suppressed only under high pressure;
- persona collapses immediately;
- different traits have different pressure thresholds.

### Phase 7 — Long-horizon attribution

After the one-step causal story is understood, run matched long trajectories.

Measure:

- action distributions;
- action transitions;
- state visitation;
- social interaction;
- need satisfaction;
- trajectory-level persona recoverability;
- task reward;
- divergence over time.

Compare these with the one-step policy effect.

A central question is whether long-run persona traceability comes from repeated persona-conditioned decisions or mostly from persona-specific game dynamics/rewards.

### Phase 8 — Metric audit

Compare candidate metrics against the causal/interventional results:

- PCSP internal trajectory-persona retrieval;
- independent Big-Five probe;
- fixed-state policy divergence;
- trait-relevant action effect;
- long-horizon behavioral outcomes.

Do not create a new learned metric unless the analysis proves one is needed.

### Phase 9 — Cross-substrate check

Only after a stable effect exists in PCSP.

Use Mario-personas or another open behavioral NPC/game-agent environment to test the **scientific distinction**, not to reproduce the exact architecture.

The goal is to distinguish:

> representation/proxy persona consistency

from

> state-appropriate causal behavioral persona expression.

If the phenomenon is PCSP-specific, keep the conclusion narrow.

### Phase 10 — Method only if earned

Only propose a method if we obtain:

> stable behavioral failure  
> → attributable bottleneck  
> → clear controllable action surface

Then use the smallest intervention that directly addresses the bottleneck.

No pre-commitment to a new contrastive loss, persona encoder, reward shaping, router, evaluator, or human-feedback pipeline.

---

## 5. Decision rules

### Strong-baseline outcome

If fixed-state swaps already produce strong, semantically correct, state-appropriate behavior and the effect survives neutral-environment controls:

> **PCSP passes the core concern.**

Do not force a paper.

### Proxy mismatch

If internal trajectory/persona identification is strong but fixed-state embedding changes barely alter actions:

> investigate what actually creates trajectory identity.

This would make proxy validity / behavioral grounding the central object.

### Sensitivity without semantics

If embedding swaps cause large changes but those changes do not align with persona meaning or are dominated by nuisance edits:

> the problem is semantic grounding, not insufficient sensitivity.

### Environment-dominated behavior

If persona disappears under neutral-environment evaluation:

> distinguish policy persona from persona encoded in reward/dynamics.

### Partial trait grounding

If only some traits work:

> do not average them into one persona score.

Check whether the environment/action ontology provides meaningful affordances for the missing traits before blaming the model.

### Pressure collapse

If persona is grounded only in easy states and collapses under realistic task pressure:

> study the persona–competence trade-off only after establishing this empirically.

---

## 6. What is already owned / what not to do

Do not turn this workbench into:

- another role-play/persona dialogue benchmark;
- “add long-term memory to NPCs”;
- better persona prompting;
- generic persona vs task trade-off;
- another Big-Five text classifier;
- another trajectory-identification metric;
- “use LLM embeddings to condition a shared policy”;
- explicit OCEAN reward shaping as the claimed novelty;
- a new method before the causal failure is localized.

Also do not treat PCSP's open artifact as the scientific contribution itself. It is the experimental substrate.

---

## 7. Feasibility

The first several phases are cheap:

- no LLM training;
- no VLA/world-model training;
- existing persona embeddings and policy code;
- discrete action space;
- inference-only fixed-state tests;
- small environment interventions;
- PPO retraining only if later justified.

This is intentionally a **game-NPC research problem with a fast experimental loop**, not a company-scale “make NPCs generally smarter” project.

---

## 8. Kill conditions

Stop or downgrade if:

- PCSP's current results cannot be reproduced and the discrepancy cannot be resolved;
- the independent behavioral audit is simply buggy;
- fixed-state and neutral-environment tests show strong semantic grounding with no meaningful failure;
- the entire signal is an artifact of hand-coded Big-Five/action mappings;
- relevant traits cannot be expressed by the environment/action ontology at all;
- nearest prior already performs the same causal policy-vs-environment persona disentanglement;
- useful conclusions require large human studies before a machine-measurable effect exists;
- after controls the project becomes merely “design a better persona metric.”

Negative results should still be recorded as workbench knowledge.

---

## 9. Workbench outputs

Keep this workbench simple. Do not create many process documents.

Use:

- this `README.md` as the scientific contract;
- `experiments/` for code/harness changes if/when added;
- `results/` for machine-readable outputs and concise analysis notes;
- `BASELINE.md` only if reproduction details become too large for this README.

Every experiment should record:

- exact upstream commit/checkpoint;
- intervention;
- controlled variables;
- metric/readout;
- result;
- what assumption changed;
- next experiment justified by that result.

The workbench remains exploratory until a simpler paper identity emerges.


---

## 10. Immediate execution order

Do **not** start by running every phase.

The first execution block is:

1. **P0 — Baseline audit**
   - reproduce / verify PCSP's current committed evidence;
   - pin exact code/checkpoints;
   - confirm the persona-conditioned reward/dynamics paths from source.

2. **P1 — Fixed-state embedding swap**
   - inference-only;
   - full + no-consistency policies;
   - same states, multiple persona embeddings;
   - measure raw policy-distribution changes before any rollout confound.

3. **P2 — Persona-channel crossing**
   - separate policy persona from environment persona;
   - one-step first;
   - matched long rollouts only after the one-step result is understood.

4. **P3 — Neutral-environment evaluation**
   - only if P1/P2 leave a genuine attribution question.

After each phase, update this workbench with:
- what was observed;
- which explanation became weaker/stronger;
- which next experiment is now justified.

Do not mechanically execute P4–P10 if an earlier result already kills or radically changes the question.

---

## 11. Primary references

- **AI for Games in the Foundation Model Era** (2026)  
  https://arxiv.org/abs/2609.16679
- **A Survey on Large Language Model-Based Game Agents** (ACM Computing Surveys, 2026)  
  https://arxiv.org/abs/2404.02039
- **AI-Native Games: A Survey and Roadmap** (2026)  
  https://arxiv.org/abs/2607.00527
- **Narrative and Dialogue Generation for Video-Games: A Systematic Mapping** (2026)  
  https://doi.org/10.1016/j.engappai.2026.115041
- **One Policy, Infinite NPCs / PCSP** (2026)  
  https://arxiv.org/abs/2605.23652  
  https://github.com/yoosunghong/pcsp
- **Stack More Levels: How to Get General and Human-like Mario Playing** (IEEE CoG 2026)  
  https://github.com/carrotoxic/mario-personas
- **Reinforcement Learning Methods for Emulating Personality in a Game Environment** (2025)  
  https://doi.org/10.3390/app15147894
- **Generative Agents: Interactive Simulacra of Human Behavior** (UIST 2023)  
  https://arxiv.org/abs/2304.03442

Broader NPC literature and artifact notes are maintained in:
- `library/themes/game-npc-social/GAME_NPC_LANDSCAPE.md`
- `library/KEY_PAPERS.md`
- `library/deep/open-artifacts/README.md`
