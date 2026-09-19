# Selected Topics — chasing trends

Started: 2026-09-19

This file contains only formal chasing-trends candidates that have survived the current genealogy-first audit and are **PILOT-AUTHORIZED**.

Admission is deliberately strict:

- the topic must grow from a real literature pressure rather than a template;
- dangerous nearest priors must be read deeply enough to establish an honest ownership boundary;
- data / compute / recipe / engineering feasibility are part of topic quality;
- the first pilot must be cheap and discriminative;
- formal candidates do not remain in a vague SERIOUS/HOLD state: after audit they are either PILOT-AUTHORIZED or KILL.

---

## CT01 — Relevant but Invalid: When Should Reasoning Models Forget Their Own Thoughts?

**Status:** PILOT-AUTHORIZED  
**Registered:** 2026-09-19  
**Detailed registration:** `CT01_RELEVANT_BUT_INVALID.md`

### Mother question

When a later turn changes an upstream premise used by a model's own prior reasoning, does preserving that prior private reasoning causally impede belief revision—even when the old reasoning remains topically relevant and the visible conversation is held fixed?

### Scientific pressure

Modern reasoning APIs now expose historical private reasoning as persistent cross-turn state. Nearby work gives apparently conflicting operational advice: retained thinking can improve multi-turn continuation/tool use, while multi-turn models can also become stuck on earlier commitments and assistant-side history can create context pollution.

Existing history-selection work mainly asks whether old content is relevant/useful. CT01 asks whether **relevance is sufficient for reusing an already executed computation** when a later premise invalidates dependencies used by that computation.

### Minimum identification

For the same visible dialogue, compare private reasoning history:

- DROP;
- PRESERVE exact native Turn-1 reasoning;
- LENGTH CONTROL with unrelated matched reasoning.

Cross this with:

- CONTINUE: old reasoning remains valid;
- REVISE: a minimal new premise invalidates an upstream dependency.

The mother statistic is the **PRESERVE × VALIDITY interaction**.

The strongest result is a sign reversal:

> preserving reasoning helps valid continuation but hurts revision after dependency invalidation.

### Kill boundary

Kill if the effect is explained by generic extra-context/length pollution, disappears when visible history is held fixed, requires artificially wrong old reasoning, fails across two model families, or does not produce a validity-conditioned interaction.

Do not rescue with a larger benchmark, learned context router, agent environment, LLM judge, or more model families.

---

**Current selected topic count = 1.**
