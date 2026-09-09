# L12 — Related Work and Paper-Level Novelty

**Candidate:** Reasoning-Induced Invariance  
**Freshness:** 2026-09-09

Novelty is paper-level. Framing, reasoning, context sensitivity, traces, and patching are populated areas; none is novel by itself.

---

# 1. Mind the (DH) Gap! — direct parent

ACL 2026 Outstanding  
<https://aclanthology.org/2026.acl-long.479/>

Owns:
- reasoning-vs-conversational risky-choice behavioral differences;
- gain/loss/order/explanation/description-history effects;
- association with mathematical reasoning training.

L12 cannot claim the behavioral phenomenon. It begins at:
> **what transformation makes the reasoning-oriented branch invariant?**

---

# 2. Framing Matters

2026  
<https://arxiv.org/abs/2605.28188>

Owns fact-preserving framing sensitivity as an internal/mechanistic object and representation-level interventions.

Therefore “where is framing represented?” or “can framing activations be patched?” is not enough.

L12 must preserve the **reasoning-induced transformation** and its semantic boundary.

---

# 3. Reasoning traces and answer readout

ACL 2026 thought-injection work already establishes that changing reasoning traces can causally change outputs.

Findings of ACL 2026 **How Do Answer Tokens Read Reasoning Traces?** studies answer-to-reasoning attention/self-reading:
<https://aclanthology.org/2026.findings-acl.1507/>

Therefore L12 cannot own:
- generic trace causality;
- generic answer-token reading;
- “the final answer depends on the CoT.”

These are tools/constraints, not the paper identity.

---

# 4. Reasoning and context robustness/control

ACL 2026 **Scaling Reasoning, Losing Control** shows reasoning improvements can trade off with instruction control.

CoNLL 2026 **Sense and Sensitivity** independently reports that enabling reasoning improves robustness to irrelevant prompt features:
<https://aclanthology.org/2026.conll-main.4/>

September 2026 **Untangling the Mechanisms of Misleading Context in Medical Question Answering** shows different misleading cues can enter reasoning through different temporal mechanisms:
<https://arxiv.org/abs/2609.02754>

These raise the bar for any generic “reasoning ignores context” story.

They do **not** answer:
> **does reasoning-oriented post-training selectively ignore semantically irrelevant variation while preserving sensitivity to decision-relevant information?**

---

# 5. What can still be ours

The surviving full identity is:

1. externally established + independently reproduced reasoning-induced invariance;
2. distinguish **selective semantic abstraction** from **broader causal disengagement/context flattening**;
3. use matched irrelevant vs decision-relevant changes with objective decision truth;
4. localize the constructed decision state causally, not by probe alone;
5. identify whether deliberation mediates the selective boundary;
6. derive a consequence for how “reasoning-induced rationality” should be interpreted.

---

# 6. Reviewer compression

### “Mind the DH Gap + probes”
Fatal if L12 stops at decodability.

### “Mind the DH Gap + thought injection”
Fatal if E05 is the main mechanism result.

### “Framing Matters on reasoning models”
Fatal if training-regime transformation and semantic boundary disappear.

### “How answer tokens read CoT”
Fatal if the contribution becomes generic pre-answer/readout localization.

### “Scaling Reasoning, Losing Control”
Dangerous if context disengagement is shown only as instruction neglect rather than a matched semantic-relevance boundary.

---

# 7. Why-space verdict

**PASS, but guarded.**

The natural remaining question is still broad without naming a layer or method:

> **Why does reasoning-oriented post-training make decisions invariant to presentation, and is that invariance selective for meaning-preserving changes?**

The E07 boundary experiment is also a novelty defense: it prevents collapse into generic framing + trace causality.

Refresh after E07/E08 or any narrative reconstruction.
