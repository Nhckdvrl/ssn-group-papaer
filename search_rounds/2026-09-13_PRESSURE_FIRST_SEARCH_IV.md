# 2026-09-13 — Pressure-First Search IV

Continuation of the pressure-first rolling logs. This file starts with a semantic/pragmatic route that initially looked substantially stronger than a competence benchmark, but was killed by a direct same-estimand owner.

---

## Hook P12 — When a model accepts a false presupposition, does it merely accommodate it conversationally or actually update the truth state used by later reasoning?

**Status:** `DROP / DIRECT SAME-ESTIMAND 2026 OWNER`

### Pressure

Recent work establishes three relevant facts:

1. LLM behavior is sensitive to presupposition projection and discourse/pragmatic conditions.
2. Stronger explicit reasoning does not reliably make presupposition judgments more human-like or make false presuppositions consistently challenged.
3. ACL 2026 frames many failures to challenge harmful/false premises as excessive **accommodation** rather than simply missing factual knowledge.

That creates a scientifically meaningful distinction from pragmatics:

> **Accepting a proposition for the current discourse is not the same thing as believing/encoding it as true.**

The initially attractive RQ was therefore:

> **When an LLM goes along with a false presupposition, does it only accommodate the proposition at the conversational-policy level, or does the proposition actually cross the model's internal contextual-truth boundary and contaminate later inference?**

Unlike a generic presupposition-competence test, this would have separated discourse policy from internal epistemic state.

### Why it dies

August-2026 work *Language Models Encode the Contextual Truth of Propositions* already identifies almost exactly this distinction. It reports a linearly represented contextual-truth quantity, demonstrates causal steering, and explicitly separates cases where a model outwardly accommodates/agrees with a false proposition while retaining an internal false representation from cases where interaction pushes the internal truth representation across the decision boundary. The latter shift is reported more often when the model explicitly restates a false claim than when it merely agrees implicitly.

Combined with ACL-2026 evidence that at-issueness, linguistic encoding, and source reliability systematically affect whether models challenge a premise, the attractive `accommodation ≠ internal truth update` estimand is no longer open.

### Reviewer compression

> `ACL-2026: false-premise failures are pragmatically conditioned accommodation + Aug-2026 contextual-truth work directly separates outward accommodation from internal truth-state shift and causally steers that state = proposed paper.`

### Anti-resurrection

Do not reopen as:

- `accommodation vs belief update`;
- `false presupposition contaminates later reasoning`;
- `explicit restatement vs implicit agreement changes belief`;
- `does the model really believe a premise it accepts?`;
- generic source-reliability / epistemic-vigilance variants.

A future route would need a different computational quantity not already captured by contextual truth representation and policy-vs-state separation.

---

No new `PILOT-AUTHORIZED` topic is produced by this log.
