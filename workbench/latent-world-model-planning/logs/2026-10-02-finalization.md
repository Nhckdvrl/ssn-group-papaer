# 2026-10-02｜Latent-WM workbench finalization

## Scope

This log closes the **research-workbench construction / literature hardening** phase. It does **not** claim the paper idea is proven; GPU training and environment evaluation remain at zero.

## Final live structure

Top-level authority is deliberately small:

- README.md
- RESEARCH_PLAN.md
- LOCAL_AGENT_PROMPT.md
- ASSETS.md
- CLAIMS.md
- PAIN_LOG.md

Current unique idea cards: I07–I13.  
Current unique experiment cards: E00, E01, E11, E13, E14, E16, E17, E18, E19.  
Old 63-file pre-consolidation tree remains archived and is not an execution authority.

## Literature / idea-growth calibration

Core readings now include:
DINO-WM, PLDM, LeWM, RC-aux, Bagatella TD-JEPA, Temporal Straightening, JEPA-WMs, Fast-LeWM, DeepJEPA, OnlineWM, Task-Sufficient WM, ToIA, Beyond Visual Quality / AD-WM positioning, TOM / policy-aware model learning, FIRM-WM, SPARK, classical multi-fidelity planning, query-sufficiency work, Feedback WM / WorldAgen / CAWM, update-utility protocol, successor/revaluation background.

The live rule is explicit:

> nearest related work is a baseline / ingredient / pressure source, not an automatic reason to kill a mother problem.

## Current first-wave hypotheses

### H-A / I12 / E16 — Planner-Boundary Branching (PBB)

Question: under equal new environment-step / reset budget, should same-state counterfactual branches be acquired where the CEM candidate ordering / elite membership is fragile?

Nearest pressures:
- FIRM-WM already proves common-reset intervention data can help;
- OnlineWM already does causality-aware active branching;
- ToIA already does task-relevant information acquisition;
- SPARK already branches at critical states in LLM-agent RL;
- TOM / policy-aware simulator learning already argues model/data should focus on policy-relevant regions;
- AD-WM / D-JEPA already target candidate decision quality.

Therefore PBB does **not** claim any of those broad ideas. Its exact test is whether **candidate-selection-boundary acquisition** gives more planning gain per acquired transition than random / coverage / global uncertainty / task-relevant uncertainty, while leaving the base WM loss unchanged in the first implementation.

Targeted web search for candidate-boundary active data / same-state branch acquisition / CEM elite data selection surfaced these neighbours but no obviously identical visual-latent-WM method in this pass. This is **not an absence claim**; novelty must be rescanned if results become manuscript-critical.

### H-B / I08 / E13 — Planner-Stage Multi-Fidelity / Elite-Preserving CEM

Question: CEM evaluates hundreds of candidates, but only the elite set affects the next proposal distribution. Can cheap latent prediction score all candidates while refined prediction is spent only on candidates that may cross the elite boundary?

Nearest pressures:
- Fast-LeWM: parallel action-prefix prediction + uniform self-consistency/decomposed terminal estimate;
- DeepJEPA: adaptive transition depth at decision-critical imagined transitions;
- older robotics multi-fidelity planning: cheap/fine model combinations are not new;
- CEM itself exposes candidates / costs / elite set.

Exact first test:
Fast-LeWM **same checkpoint** direct score = cheap fidelity; decomposed/self-consistency rollout = refined fidelity. Compare CHEAP-ALL, FULL-REFINE, RANDOM-M, TOP-M, ELITE-BAND and residual-interval promotion on the same candidate banks before closed-loop evaluation.

Targeted search for latent-WM multi-fidelity CEM / elite-preserving refinement surfaced general multi-fidelity planning and adaptive-compute neighbours but no exact identical candidate-elite allocation method in this pass. Again, this is not a novelty certificate.

## Second-wave concrete lines

- E17 / I10: Selective Query Specialization.
- E18 / I11: Utility-Gated Recovery using update-vs-hold fork utility.
- E19 / I13: Selective Revaluation / minimal sufficient update set.
- E11 / I07: history / belief / active information.
- E14 / I09: trajectory supervision and planning semantics.

These are active research options, not “remaining scraps”.

## Code feasibility already checked

- stable-worldmodel CEM exposes candidates, costs, top-k indices and callbacks.
- Fast-LeWM get_cost has a direct rollout path and an optional additional decomposed/self-consistency rollout, so selective candidate refinement can be implemented without rewriting the planner.
- TwoRoom / PushT / OGBench environments expose state restoration interfaces useful for controlled branch-bank experiments, subject to replay-fidelity checks.
- Fast-LeWM official repo provides the same core planning task family as LeWM and public checkpoint pointers.
- DeepJEPA public repo was not yet a runnable release at the time of this pass; it is a direct neighbour, not a blocker.

## Immediate execution order for local agent

1. E00: measure actual environment / checkpoint / I/O / planner cost on one navigation and one manipulation task.
2. In parallel:
   - E13 Stage A0 candidate-bank audit (no new training);
   - E16 Stage 0 branch-bank construction / selector leakage check.
3. If E13 offline elite-recall trade-off is meaningful, run online CEM fixed-wall-clock pilot.
4. If E16 branch bank works, run 5–6 acquisition selectors with one exploratory training seed.
5. Put 3+ train seeds, second task family and strongest neighbour only behind a real signal.
6. Opportunistically launch E17/E18/E19 if their required checkpoints are already available.

## Status

- local GPU training: 0
- local environment evaluation: 0
- science claims: 0
- workbench status: PROPOSED
- current main after final registry update: 5d05de685587288fb3ee62eb3649fa386099d990

The workbench is now intended to be handed directly to the local agent via LOCAL_AGENT_PROMPT.md.
