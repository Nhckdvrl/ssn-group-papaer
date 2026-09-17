# Failed Topics — 2026-09-17 Cross-Domain Search III

**Status:** durable kill ledger. Read together with all other `FAILED_TOPICS*` files before generating new topics. These are negative/process evidence only, never positive taste exemplars.

---

## F52 — Copy / reuse versus recomputation of an earlier intermediate structure

**Question.** When an LM later needs information or an intermediate structure that has already appeared earlier in its context, does it causally reuse/copy the earlier representation or recompute the result from a more abstract state?

**Why it looked promising.** Vision/diffusion work shows that apparently repeated computation can sometimes be predicted or reused from earlier hidden features, suggesting a general reuse-versus-recompute distinction.

**Nearest prior.** Once instantiated in a natural LM task using explicit intermediate reasoning or calculations, the problem collapses into the mature chain-of-thought faithfulness / intermediate-structure causality literature. Existing causal-mediation and intervention work already asks whether later answers genuinely depend on earlier intermediate reasoning and edits those intermediates to test causal following.

**Kill reason.** The cleanest identification requires explicit intermediate structures, at which point the reviewer-level parent is already `does the final answer causally use the stated intermediate reasoning?`. Rephrasing that dependency as copy-versus-recompute does not create an independent mother question.

**Revival condition.** A natural non-CoT task in which copy/reuse and recomputation make opposite causal predictions, without reducing to factual retrieval, induction heads, or intermediate-reasoning faithfulness.

---

## F53 — Coarse-to-fine semantic commitment in diffusion language models

**Question.** During denoising, does a diffusion LM first decide coarse semantic content (`what to say`) and only later resolve lexical/surface realization (`how to say it`), even without an explicitly imposed hierarchy?

**Why it looked promising.** Image diffusion has mature coarse-to-fine dynamics, creating a natural cross-modal question about whether language denoising self-organizes along an analogous semantic granularity axis.

**Nearest prior.** ACL 2026 Main work already studies semantic convergence/adaptive denoising in diffusion LMs. 2026 work explicitly framed as *When to Plan, When to Polish: Noise Level as a Granularity Axis for Diffusion Language Models* assigns coarse meaning commitment to high-noise stages and token refinement to low-noise stages. NeurIPS 2025 hierarchical diffusion LM work explicitly imposes semantic-scale coarse-to-fine generation.

**Kill reason.** The central parent `noise level / denoising stage corresponds to semantic granularity and coarse-to-fine commitment` is already forming rapidly. An observational study of ordinary DLMs would be an immediate follow-up, not an independently owned mother question.

**What to learn.** Obvious image→language mechanism analogies are currently high-collision because diffusion-LM research is importing them quickly.

**Revival condition.** A qualitatively different denoising computation with predictions not reducible to semantic convergence or coarse-to-fine granularity.

---

## F54 — Predictive relevance as the rule for what limited internal memory retains

**Question.** Under limited representational/memory capacity, does an LM preferentially preserve information according to future predictive usefulness rather than semantic salience or recency?

**Why it looked promising.** Information theory suggests that a compressed predictive state should retain precisely the information useful for future prediction, yielding a principled mechanism rather than an ad-hoc memory heuristic.

**Nearest prior.** Predictive-state/rate-distortion views of sequence models already study minimal prediction-relevant state. ACL 2026 work on gated differentiable working memory explicitly reframes test-time adaptation as budget-constrained memory consolidation / deciding what context is worth writing to memory. ICML 2025 hidden-state-prediction work develops measures of in-context computation/information gain.

**Kill reason.** Natural operationalizations collapse into the already active memory-selection / predictive-state literature, and easily become a memory method rather than a new scientific object.

**Revival condition.** A retention law with a qualitative prediction that cannot be summarized as predictive relevance, memory gating, or information bottleneck selection.

---

## F55 — Producibility versus reachability / steerability

**Question.** Can a generative model internally support an output/concept that its ordinary prompt/control interface cannot reliably reach, and what separates generative support from controllability?

**Nearest prior.** NeurIPS 2025 work explicitly distinguishes `producibility` from `steerability` across generative models, including LMs. ICML 2025 *Concept Reachability in Diffusion Models* distinguishes concepts available in the latent model from concepts reachable by prompting and studies reachability transitions.

**Kill reason.** The broad support-versus-control distinction is already a named, cross-modal research parent. Applying it to another LM behavior would be `existing parent + new capability`.

**Revival condition.** A different interface–representation dissociation whose causal structure is not reducible to reachability/steerability.

---

## F56 — Mechanism of negative constraints

**Question.** Why do instructions such as `do not mention X / do not do Y` sometimes increase activation or production of the forbidden content? Is the constraint represented early but overridden late, or does mentioning X itself prime the forbidden behavior?

**Nearest prior.** 2026 mechanistic work on negative-constraint failure already separates semantic priming/pressure from late-layer suppression or override and uses causal interventions.

**Kill reason.** The mechanistic parent is directly occupied; adding more negative constraints or models is an extension.

**Revival condition.** A constraint phenomenon requiring a computational primitive beyond priming versus suppression/override.

---

## F57 — Fast context memory versus slow parametric consolidation

**Question.** Do LMs naturally implement complementary fast and slow learning systems, with context acting as temporary memory and weights as slower consolidated knowledge?

**Nearest prior.** 2026 work explicitly frames LMs as learning `fast and slow`, combines contextual fast weights with slower parameters, and studies consolidation/sleep-like transfer; complementary-learning-system analogies are already active.

**Kill reason.** The two-timescale consolidation parent is already directly occupied. A new implementation or extra memory setting would be method work or a regime extension.

**Revival condition.** A distinct multi-timescale law with predictions not reducible to context-versus-weight consolidation.
