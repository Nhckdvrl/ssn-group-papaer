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

## CT03 — Counterfactual Credit for MoE Routing

**Status:** PILOT-AUTHORIZED  
**Registered:** 2026-09-19  
**Detailed registration:** `topics/CT03_COUNTERFACTUAL_CREDIT_MOE_ROUTING.md`

### Mother question

Can a pretrained sparse MoE router receive useful token-level credit for **unexecuted experts** without explicitly rerunning the downstream model for many alternative routes?

### Method thesis

Use one standard forward/backward pass plus a small number of local candidate-expert forwards to estimate the loss effect of replacing a routed expert:

[
\widehat{\Delta L}_{i\rightarrow j}
\approx
\nabla_h L^\top (h^{i\rightarrow j}-h).
]

Distill this approximate counterfactual utility into the routers, while retaining ordinary Top-K inference.

### Minimum identification

Before training the full method, calibrate the local estimator against exact alternative-route loss on hard reasoning tokens and multiple MoE layers. Continue only if it predicts beneficial replacements substantially better than router score / random baselines and yields a large supervision-cost reduction.

### Kill boundary

Kill if the estimator has weak exact-counterfactual fidelity, works only in the final layer, loses its efficiency after candidate expansion, or router-only adaptation fails to improve real reasoning benchmarks.

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

**Current selected topic count = 2.**
