# L12 — Next Decisive Pilot Card

**Experiment:** L12-E07 → gated L12-E08  
**Status:** CONTINUE-PILOT  
**Purpose:** distinguish selective semantic abstraction from broader context disengagement before more mechanistic localization.

# Established before this card

- Think-SFT is far more gain/loss/order invariant than sibling Instruct-SFT;
- frame identity remains decodable early/mid;
- complete natural traces causally affect final readout;
- `</think>` stopping is invalid;
- answer-free arithmetic snippets do not explain the trace effect.

None is the final mechanism.

# E07a — minimum boundary test

Use the **three audited parent prospects** only for route selection.

For each prospect:
- **irrelevant/equivalent axis:** keep the audited gain/loss × order variants;
- **decision-relevant axis:** change exactly one payoff/probability field enough to flip the EV-optimal underlying choice in both gain and loss conditions.

The exact frozen edits are in `configs/boundary.json`; the runner asserts target flipping before generation.

Models:
- OLMo-3 Instruct-SFT sibling;
- OLMo-3 Think-SFT sibling.

Primary reporting:
1. equivalent frame consistency;
2. decision-relevant EV accuracy;
3. Think-minus-Instruct contrast on each dimension.

Do **not** collapse them into one headline score.

### A — selective abstraction
Think improves equivalent-presentation invariance without losing decision-relevant accuracy.

### B — context flattening
Think improves equivalent-presentation invariance but loses sensitivity to decision-changing facts.

### C — no stable boundary
Repair the boundary or reconsider the mechanism identity before patching.

The three-prospect experiment is deliberately only route selection.

# E08 — only after E07

Patch/substitute a pre-answer internal state from matched donors:
- equivalent-context donor;
- decision-changing donor;
- controls.

Use a donor point before explicit conclusion/answer text.

Success is a causal semantic-selectivity pattern, not “layer 23 matters.”

# Runnable E07a scaffold

- `configs/boundary.json`
- `scripts/run_boundary.py`
- `scripts/summarize_boundary.py`
- `scripts/run_boundary.sh`

# Stop

If E07 has no interpretable branch × semantic-relevance pattern and no better objective boundary can be constructed, HOLD/KILL before expanding interpretability work.
