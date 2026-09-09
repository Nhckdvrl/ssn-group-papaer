# L12 — Related Work and Open Scientific Space

**Freshness:** 2026-09-09

# 1. Established starting point

**Mind the (DH) Gap!** (ACL 2026 Outstanding) owns the broad behavioral observation: reasoning-oriented models are much more invariant across several risky-choice presentations.

L12 starts from that phenomenon rather than trying to rediscover it.

# 2. Nearby mechanism work

**Framing Matters** studies internal framing sensitivity and representation-level intervention.

ACL 2026 work on reasoning traces shows that reasoning trajectories can causally affect final answers, and **How Do Answer Tokens Read Reasoning Traces?** studies how answer tokens integrate those traces.

Other recent work shows reasoning can change sensitivity to irrelevant or misleading context.

So the interesting question is no longer whether framing is represented or whether reasoning influences readout.

# 3. Open scientific question

> **When reasoning-oriented post-training makes behavior invariant, has the model learned which contextual variation is irrelevant, or has context more generally lost influence over the decision?**

E07 tests that distinction directly:

- redundant context should not matter;
- corrective context should matter.

E08, only if needed, asks how that semantic distinction is carried in the decision state.

# 4. Paper identity

A strong L12 paper has the shape:

> established reasoning-induced invariance  
> → semantic-relevance boundary  
> → causal explanation of decision-state construction  
> → consequence for how we interpret reasoning-model rationality

The interpretability method is supporting machinery, not the identity.

# 5. Current novelty judgment

The why-space remains open because existing work does not yet answer whether reasoning-induced invariance is **selective semantic abstraction** or **broader causal disengagement**.

Refresh after E07/E08 if the central explanation changes.
