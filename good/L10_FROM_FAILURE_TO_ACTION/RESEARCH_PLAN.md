# L10 — Research Plan

**Goal:** locate the failure→action bottleneck before scaling.

# Phase 0 — Artifact audit

Completed for route selection:
- ImplicitMemBench upstream pinned at `927413bf3f5389bb47c94c2a0ba987e435b101b8`;
- 10 Conditioned API Aversion items selected as the cleanest strict two-action substrate;
- Tool Use with Side-Effects deferred because many items admit multiple valid actions.

Run `scripts/fetch_parent_data.sh` and preserve provenance/hashes before execution.

# L10-E01 — Untouched-History Stage Decomposition

- 10 released items;
- pinned Qwen2.5-7B-Instruct;
- greedy first-action decoding;
- native chat template;
- independent M/C/P/A0 forks.

Report M/C/P accuracy, A0 good-action/bad-repeat rates, strict validity, and item-level **P correct + A0 bad repeat**.

No hidden-state probe.

# L10-E02 — Matched Stage Completion

From H compare A0 raw, A1 outcome reminder, A2 causal binding, A3 negative prohibition, A4 positive replacement.

Interpret only through paired changes in **actual first action**:
- A1 rescues → retention;
- A2 adds rescue → attribution;
- A4 needed after correct P → policy/action bottleneck;
- A4 ≫ A3 → negative-specification boundary.

Questionnaire accuracy alone cannot establish a causal stage.

# After leverage

Only after E01/E02:
1. confirm on a second open family;
2. add a success-experience control if needed;
3. add interference only if retention is implicated;
4. formalize natural interactive validation with objective action schemas.

The side-effect family can return after its action space is formalized.

# Kill / reconstruct

RECONSTRUCT when another stage/boundary wins.

KILL/demote when source mapping fails, strict action identity is invalid, no stage/completion has leverage, effects reduce to known explicit-negative-instruction behavior, natural validation breaks the diagnosis, or new literature compresses the full chain.

# Main-level shape

> established failure behavior → stage-wise localization → targeted causal completion → meaningful boundary → natural validation → consequence for experience/memory design.
