# L12 — Research Plan

**Goal:** explain why reasoning-oriented post-training produces presentation-invariant decisions.

# Completed

- parent artifact audit;
- sibling Instruct-SFT vs Think-SFT behavioral reproduction;
- frame decodability diagnostic;
- invalid `</think>` stopping test;
- natural reasoning-prefix causal readout test;
- answer-free arithmetic-prefix test.

These establish the substrate but do not explain the mechanism.

# L12-E07 — Semantic-Relevance Boundary

Keep the original option lines fixed.

Add matched contextual notes:

- **redundant:** a probability is rechecked and remains unchanged;
- **correction:** the same kind of note updates the probability enough to flip the EV-optimal action.

This directly asks whether Think-SFT distinguishes context that merely accompanies a problem from context that changes the decision-relevant state.

Use only the two audited sibling branches.

Primary quantities:

1. redundant-context consistency;
2. correction EV accuracy.

Outcomes:

- high on both → **selective semantic abstraction**;
- high redundant consistency but low correction accuracy → **context flattening / causal disengagement**;
- another pattern → reconstruct the explanation.

The three prospects are a route-selection pilot. If the boundary is real, expand it later to a small natural controlled set.

# L12-E08 — Decision-State Causal Test

Run only after E07 gives a stable boundary.

Use matched redundant/correction contexts and intervene on the pre-answer internal state before explicit conclusion text.

Question:

> **Does the state carry decision-relevant contextual information while discarding irrelevant variation?**

The contribution is the causal distinction, not a layer number.

# Main-level shape

> reasoning-induced invariance  
> → semantic-relevance boundary  
> → causal explanation of decision-state construction  
> → consequence for how we interpret reasoning-model rationality
