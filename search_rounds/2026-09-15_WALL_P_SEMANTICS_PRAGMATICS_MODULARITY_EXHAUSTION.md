# 2026-09-15 — WALL-P / Semantics–Pragmatics Computational Modularity

**Parent standing problem:** IP08 — semantics + context + pragmatic goals  
**Mode:** classic theory dispute → processing evidence → modern connectionist reformulation → identification / owner audit  
**Outcome:** **CURRENT DESCENDANT EXHAUSTED — NO NEW L-SERIES — NO PILOT**

# 1. Mother scientific problem

> **Does utterance interpretation pass through a reusable, context-independent semantic representation that pragmatic inference subsequently enriches, or are semantic and pragmatic constraints integrated into one context-sensitive computation without a separable semantic bottleneck?**

This is an old semantics/pragmatics dispute, not an LLM benchmark question.

A modular / semantic-first lineage treats linguistic decoding as producing a semantic or logical form which is then supplied to pragmatic inference. Relevance-theoretic accounts such as Carston's explicitly distinguish decoding from inferential enrichment.

A competing contextualist / parallel-processing lineage argues that contextual information can participate immediately and that literal/minimal and enriched interpretations need not be serial stages. Controlled psycholinguistic experiments in the early 2000s explicitly compared minimal-first and parallel-enrichment processing accounts.

Recent Christopher Potts talks make the deeper connectionist version explicit: if semantics and pragmatics had developed from a connectionist rather than symbolic starting point, the sharp semantics/pragmatics distinction itself might disappear.

# 2. Why this initially looked promising

The theories disagree at the level of computational architecture rather than benchmark accuracy.

A strict semantic-bottleneck view appears to predict a context-stable semantic variable which is reused across pragmatic contexts and then transformed by context-sensitive inference.

An integrated semprag view predicts that contextual constraints enter the meaning computation itself, so no single context-independent intermediate should be both necessary and sufficient across pragmatic regimes.

Both answers would matter for theories of learned meaning representation.

# 3. Direct current evidence already approaches the obvious mechanistic experiment

EACL 2026, *Tug-of-war between idioms' figurative and literal interpretations in LLMs*, uses causal tracing/activation patching to study competing literal and figurative interpretations. It reports that disambiguating context is used from the earliest layers, while literal and figurative readings later travel through competing pathways.

Source: https://aclanthology.org/2026.eacl-long.135/

EMNLP 2024 pragmatic-evaluation work also analyzes layerwise pragmatic representation, and ACL 2026 work on deferred semantic drift uses causal interventions to trace context-dependent reinterpretation.

Sources:
- https://aclanthology.org/2024.emnlp-main.1258/
- https://aclanthology.org/2026.findings-acl.57/

These papers do not settle the general semantics/pragmatics theory. They do show that `take one semantic/pragmatic phenomenon and causally trace literal vs contextual interpretations` is already an active experimental program.

# 4. The decisive problem is identification, not lack of theory

The old theories disagree about computational dependency / processing organization.

Three tempting neural tests fail:

## 4.1 Layer order is not processing time

Finding literal information at layer L and context-enriched information at layer L+k cannot establish a serial semantic→pragmatic cognitive architecture. Transformer depth is not a licensed proxy for online human processing time, and contextual information is available throughout the forward computation.

## 4.2 Decodability does not establish a semantic bottleneck

A context-invariant semantic representation may be linearly decodable even if the model never uses it as an autonomous intermediate. This is the generic IP01/WALL-A problem.

## 4.3 Patching inherits the causal-abstraction problem

Cross-context activation transfer appears attractive: hold literal content fixed, swap pragmatic context, and test whether a common semantic variable transfers.

But the interpretation requires exactly the assumptions already recorded under WALL-A: alignment of the high-level variable, intervention semantics, domain validity, and avoidance of off-manifold/divergent states.

Without an independently justified intervention, a successful patch shows that a representation can drive the behavior under the edit, not that natural computation contains a modular semantic bottleneck.

# 5. Reviewer compression

The strongest current realization compresses to:

> `classic semantic-first vs contextualist/parallel-processing debate + modern causal tracing on another semantic/pragmatic phenomenon`.

That is precisely the prohibited `old linguistic theory × mechanistic interpretability` generator.

Behavior-only tests are weaker: semantic-first and integrated accounts can generally be tuned to produce the same final interpretation, so final-answer accuracy does not discriminate their computational commitments.

# 6. Decision

**WALL-P / this IP08 descendant is exhausted under current identifying leverage.**

The mother dispute remains important. Reopen only if a new operation makes semantic-first and integrated accounts give opposite predictions on the same externally defined causal quantity without treating layer order, probe accuracy, or generic activation patching as the identifying bridge.

Do not regenerate scalar implicature / presupposition / metaphor / idiom × mechanistic tracing as a new parent.

No L-series is created.