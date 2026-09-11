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

### Incorrect-CoT distillation → what information actually transfers?

**RQ:** If a student can improve even when distilled reasoning traces are partly wrong, what useful information is really being transferred by the trace?

**Why we cannot do it:** 2026 work already directly separates final-answer gains from step-level reasoning quality and studies causal importance / sufficiency of reasoning content. The natural mechanism story compresses into the crowded reasoning-faithfulness / rationale-quality / CoT-distillation parent rather than a new scientific object.

**Decision:** KILL CURRENT FORM.

### Truthful evidence montage → why does stronger reasoning become easier to mislead?

**RQ:** Why can stronger reasoning make models more vulnerable to a selectively assembled set of individually true evidence fragments?

**Why we cannot do it:** The obvious explanatory routes collapse into already-killed parents: K025 selection/sampling-mechanism neglect and K010 dependent/repeated evidence aggregation. The mother paper itself already frames the failure as narrative overfitting. A mechanism follow-up would therefore refine an occupied explanation space rather than establish a new parent question.

**Decision:** DUPLICATE / KILL CURRENT FORM — do not assign a new K ID.

### Ambiguity recognition ≠ value of clarification

**RQ:** Can an agent distinguish “the instruction is ambiguous” from “the ambiguity is important enough that asking one clarification question is better than acting now”?

**Why we cannot do it:** ACL 2026 *Value of Information: A Framework for Human–Agent Communication* directly formalizes clarify-versus-commit as expected task utility versus communication cost. 2026 structured-uncertainty / EVPI work further owns the tool-argument version of when to ask, what to ask, and when to stop. The exact decision-theoretic parent is already occupied.

**Decision:** KILL / DIRECT COLLISION.

### L20 — What Does an LLM Learn From a Rewarded Trajectory?

**RQ:** When a fixed pretrained LLM sees a multi-step attempt followed by scalar reward, does its next policy preferentially update the actions that causally earned the outcome, or mainly treat the whole rewarded trajectory as a good/bad demonstration?

**Why we cannot do it:** The future-policy-shift estimand is genuinely different from retrospective step scoring, but the surviving novelty is narrow relative to ICRL, successful-trajectory reuse, and 2026 causal-credit work. More importantly, the successful-result test is asymmetric: a strong Main-level story mainly requires the interesting positive outcome that terminal scalar reward induces fine-grained local causal credit; coarse whole-trajectory reuse is compatible with existing ICRL/RL accounts and is a weaker contribution, while reward-independent hindsight kills the reward-mediated story. Realistic local causal gold also requires expensive executed replay / policy-supported counterfactuals, and cheap symbolic domains weaken the intended general claim and force another realistic domain anyway.

**Decision:** **KILL CURRENT FORM / NO PILOT.** Do not rescue by shrinking to a toy symbolic benchmark; that would be a new candidate requiring re-selection.
