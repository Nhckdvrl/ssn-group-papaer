# L12 — Next Decisive Pilot Card

**Experiment:** L12-E07 → L12-E08 if E07 is informative  
**Status:** CONTINUE-PILOT

# E07 — Semantic-Relevance Boundary

Use the **three audited parent prospects** for route selection.

Keep the displayed options fixed. Append one of:

1. **none**
2. **redundant context** — restate one probability with the same value
3. **decision-relevant correction** — same template, but set that probability to a frozen value that flips the EV-optimal underlying choice

Cross the existing gain/loss and order conditions.

The exact edits are frozen in `configs/boundary.json`. The runner verifies that every correction flips the normative target before generation.

## Core readout

Report only the quantities needed for the scientific distinction:

- **redundant-context consistency**
- **correction-context EV accuracy**

Interpretation:

- high redundant consistency + high correction accuracy → **selective semantic abstraction**
- high redundant consistency + low correction accuracy → **context flattening / causal disengagement**
- another stable pattern → reconstruct the explanation around that pattern

Models:
- OLMo-3 Instruct-SFT
- OLMo-3 Think-SFT

This is a route-selection pilot, not the final dataset.

# E08 — Decision-State Causal Substitution

Run only if E07 gives a clear semantic-relevance pattern.

At a pre-answer point before explicit conclusion text, substitute the matched state from:
- redundant-context trajectory
- correction-context trajectory

Ask one question:

> **Does the decision state carry the relevant contextual update while discarding the redundant one?**

That causal distinction is the goal. The layer number is not.

# Runnable scaffold

- `configs/boundary.json`
- `scripts/run_boundary.py`
- `scripts/summarize_boundary.py`
- `scripts/run_boundary.sh`

No additional defensive experiments are queued before E07/E08 changes the scientific picture.
