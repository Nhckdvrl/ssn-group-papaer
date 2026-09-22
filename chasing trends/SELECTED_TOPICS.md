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

## CT04 — What Moves During Hybrid Adaptation? State-Dynamics Drift in Recurrent–Attention LMs

**Status:** PILOT-AUTHORIZED — exploratory identification program  
**Registered:** 2026-09-19; reframed 2026-09-20  
**Detailed registration:** `topics/CT04_HYBRID_ADAPTATION_STATE_DYNAMICS.md`

### Mother question

When a pretrained hybrid recurrent–attention LM is adapted, **what actually moves**: recurrent transition dynamics, recurrent-state operating point, attention↔recurrence functional allocation, operation-local memory behavior, or only generic representations?

### Scientific pressure

Current results do not line up under one simple explanation. Component-specific LoRA can be destructive on the recurrent path of sequential Qwen3.5 yet constructive on parallel Falcon-H1; state/S0 tuning can adapt recurrent computation strongly without changing the weights; causal cache interventions show attention KV and recurrent state carry different functions; and separate hybrid work shows post-training can locally damage a memory-routing mechanism.

CT04 treats these as an identification problem rather than presupposing which operation is brittle.

### Identification program

Use matched adaptation plus base/adapted **state × weights × channel** crosses to measure:

- recurrent-state trajectory / retention-horizon drift;
- whether changed behavior travels with state or transition parameters;
- attention-KV vs recurrent-state causal contribution before/after adaptation;
- sequential vs parallel topology;
- pure-Transformer controls for generic drift.

Different outcomes imply different method families: dynamics anchoring, state recentering, channel-balanced adaptation, or operation-aware PEFT.

### Continuation boundary

Do not stop because one predicted sign fails. Stop/reframe only if matched experiments reveal no stable causal structure beyond recipe noise or generic drift, or if a direct prior already performs the same decomposition and method.

--

**Current selected topic count = 1.**
