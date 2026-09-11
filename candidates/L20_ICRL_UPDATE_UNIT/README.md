# L20 — What Does an LLM Learn From a Rewarded Trajectory?

**Status:** **SERIOUS / PRE-PILOT — HIGH COLLISION RISK — NO COMPUTE AUTHORIZED**  
**Date:** 2026-09-12  
**Target:** ACL / EMNLP / NAACL Main

> **Priority note:** RL / agent / credit-assignment is an unusually crowded 2026 neighborhood. L20 is retained only as a high-risk lead while exact-operation ownership is unresolved. Do not prioritize it over cleaner NLP / language / measurement / mechanism candidates merely because no exact duplicate has yet been found.

## Research question

> **When a fixed pretrained LLM sees a multi-step attempt followed by scalar reward, does its next policy preferentially update the actions that causally earned the outcome, or mainly treat the whole rewarded trajectory as a good/bad demonstration?**

Plain version:

> A failed attempt can contain several good decisions before one later mistake ruins everything. A successful attempt can contain a bad but recoverable decision. After seeing only the final reward, what does the LLM actually learn for its next attempt?

The object is the **unit / rule of inference-time policy update**, not whether an LLM can verbally identify which old step was responsible.

## Scientific pressure

ICLR 2026 *Reward Is Enough: LLMs Are In-Context Reinforcement Learners* places previous responses and scalar rewards back into context and shows performance improves over repeated attempts. The paper presents reward maximization, exploration/exploitation, context dependence and reward ablations as evidence of RL-like inference-time learning.

However, aggregate improvement does not identify the update rule. NeurIPS 2025 *Self-Generated In-Context Examples Improve LLM Agents for Sequential Decision-Making Tasks* shows that simply accumulating successful full trajectories as future in-context examples can also produce large gains.

A second pressure comes from 2026 step-credit auditing: *Credit Without Ground Truth* finds that common LLM-agent step-level credit signals need not track executed-replay causal contribution. Thus local credit cannot be assumed merely because the final policy improves.

## Competing accounts

### A — Local causal / RL-like update

Reward is used together with trajectory structure to preferentially update state-actions that actually helped or hurt the outcome.

Prediction: a locally useful action embedded in an overall failed trajectory can become more preferred, while a locally harmful/recoverable action embedded in a successful trajectory need not be reinforced.

### B — Trajectory-level reward-conditioned imitation

The terminal reward mainly labels the whole trajectory as good or bad.

Prediction: actions appearing in successful trajectories are broadly favored over otherwise-better actions appearing in failed trajectories, even when executed replay says their local causal contribution has the opposite sign.

### C — Reward-independent hindsight

The model can infer which decisions were good or bad from the trajectory semantics alone; the scalar reward contributes little to localization.

Prediction: the same local preference shift appears when the scalar reward is removed or neutralized.

## Anti-resurrection fence — Not K021 because ...

K021 killed **causal credit from experience** as a retrospective attribution parent: determine which past trajectory step caused success/failure.

L20 survives only if it keeps a different estimand:

> **How does reward exposure change the fixed model's future policy at matched decision states?**

Executed replay may supply independent causal gold for whether an earlier action helped, but the measured quantity is `policy after context - policy before context`.

If the project mutates into explicit step scoring, failure localization, process-reward construction, or a new training-time credit-assignment method, it falls back into K021 / the modern credit-assignment literature and must be killed or re-selected.

## Nearest-work compression

Strongest attack:

> “This is K021 / *Credit Without Ground Truth*, but with ICRL prompting.”

Current rebuttal:

- step-credit auditing asks whether a score assigned to **past steps** agrees with causal contribution;
- L20 asks which **future actions** a fixed model upweights after observing scalar-rewarded experience;
- no weight update or explicit credit scorer is required;
- the competing whole-trajectory-imitation account makes a direct behavioral prediction about future policy.

This distinction is promising, but it must survive the final exact-operation literature audit before compute.

## Candidate decisive operation

Use an existing executable sequential environment and construct natural trajectory pairs where **trajectory outcome and local action quality conflict**.

Example structure:

1. a failed trajectory contains an early useful action, then later fails for an unrelated reason;
2. a successful trajectory contains an early harmful or unnecessary but recoverable action, then later succeeds;
3. use environment replay / policy-supported counterfactual actions to independently estimate the local causal contribution of the focal action;
4. after exposing the fixed LLM to the trajectory plus scalar reward, return it to the same or tightly matched decision state and measure the change in its action distribution / choice.

Critical controls:

- same trajectory with terminal reward removed or neutralized;
- localized/dense reward as a positive-control condition;
- matched task/state/action wording and history length;
- reproduce the mother ICRL improvement before interpreting local-update behavior.

Primary scientific unit should be task/state, not repeated samples from one prompt.

## Successful-result test

If local causal quality predicts the future policy shift beyond trajectory reward and beyond no-reward hindsight, we obtain evidence that general-purpose LLM ICRL performs nontrivial local credit assignment in context.

If whole-trajectory reward dominates despite opposite local causal quality, the result still matters: aggregate ICRL improvement can arise through reward-conditioned trajectory use without fine-grained temporal credit.

If removing the scalar reward preserves the same local shift, the reward-mediated-credit story is not supported; this may substantially weaken or kill L20 rather than trigger a fallback story.

Do **not** frame the second outcome as “not real RL.” Monte-Carlo / trajectory-return RL can itself use coarse credit. The claim is about **update granularity and computation**, not an ontological test of whether the behavior counts as RL.

## Main-paper growth if the core distinction survives

- **C1 — Update unit:** local causal action quality vs whole-trajectory reward association.
- **C2 — Boundary:** when terminal reward is enough for localization — horizon, delayed consequence, recoverability, or dense-vs-terminal feedback.
- **C3 — Consequence:** aggregate performance curves are insufficient to identify what ICRL learned; propose an evaluation that tests update-rule fidelity, then replicate across a second environment/model only as needed for the claim.

## Current blockers before pilot authorization

1. Finish exact source-level search for any 2026 work that already measures fixed-LLM **future policy change** under local-quality/trajectory-return conflict.
2. Verify an existing environment can produce enough natural conflict states with replay-derived causal labels without bespoke worlds or author judgments.
3. Confirm the mother ICRL setup can be reproduced with an accessible open model and an environment reward that is not an LLM judge.

Until all three pass: **NO COMPUTE.**
