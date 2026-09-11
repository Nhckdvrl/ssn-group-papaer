# 2026-09-12 — Continued Topic Search

**Target:** ACL / EMNLP / NAACL Main  
**Rule:** anti-resurrection first; no survivor quota.

## Killed in this round

### Temporal forgetting → latent survival via relearning

**RQ:** When a factual association is learned, later forgotten during pretraining, and then encountered again, does faster relearning show that the original knowledge survived in a latent form?

**Why we cannot do it:** Pretraining-time factual acquisition and forgetting are already a direct NeurIPS 2024 scientific object. Relearning / savings / reversibility is also an established diagnostic in adjacent memory, continual-learning and unlearning work. The natural paper compresses to applying a familiar persistence diagnostic to an already-owned forgetting phenomenon rather than opening a new Main-level parent question.

**Decision:** KILL CURRENT FORM.

### Own-answer persistence vs generic anchoring

**RQ:** When an LLM remains stuck on a previous wrong answer across turns, is the persistence specifically caused by treating the answer as its own prior commitment rather than merely seeing the same candidate in context?

**Why we cannot do it:** 2026 work on self-attribution / choice-supportive bias already performs the decisive own-answer-versus-other-model attribution intervention and finds the self-specific persistence effect. Recent work on prior assistant history further crowds the broader context-pollution story.

**Decision:** KILL / DIRECT COLLISION.

## Serious lead retained — L19

### What Does an LLM Learn From a Rewarded Trajectory?

**RQ:** When a fixed pretrained LLM sees a multi-step attempt followed by scalar reward, does its next policy preferentially update the actions that causally earned the outcome, or mainly treat the whole rewarded trajectory as a good/bad demonstration?

**Why this is not K021 by default:** K021 was retrospective causal credit attribution — which past step caused the observed outcome. L19's estimand is the **future in-context policy change** of a fixed-weight model after reward exposure. Executed replay is only independent causal gold for local action quality, not the paper endpoint.

**Scientific pressure:**
- *Reward Is Enough* (ICLR 2026) shows aggregate inference-time improvement from response/reward history and argues for emergent ICRL, including learning from failure experience.
- *Self-Generated In-Context Examples Improve LLM Agents* (NeurIPS 2025) shows that whole successful trajectories alone can substantially improve future behavior, so aggregate improvement does not identify local credit assignment.
- *Credit Without Ground Truth* (arXiv 2026-08) shows that common step-credit signals can fail against executed-replay causal contribution, making the local-credit question substantive rather than automatic.

**Reviewer compression to defeat:** “K021 / step-credit auditing, but in ICRL.”

**Current verdict:** **SERIOUS / PRE-PILOT — NO COMPUTE AUTHORIZED.**

Before promotion, the candidate must survive one final exact-operation audit and show that a clean matched trajectory-conflict design can be constructed in an existing environment without author-defined causal labels.
