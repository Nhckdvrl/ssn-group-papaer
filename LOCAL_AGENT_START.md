# Local Agent Start — Current Execution Handoff

**Date:** 2026-09-09  
**Target:** NAACL Main  
**Approved paper mainline:** NONE

# Priority

1. **L10 — From Failure to Action**  
   `good/L10_FROM_FAILURE_TO_ACTION/`
2. **L12 — Reasoning-Induced Invariance / Trajectory Takeover**  
   `good/L12_REASONING_DECISION_INVARIANCE/`
3. **L08 — strong backup**

**L11 is KILL / K181.**

Do not reopen topic search unless explicitly requested.

# Execution rule

Read `RESEARCH_EXECUTION.md` and the selected canonical package first.

Keep:

> claim → experiment → config/code → raw result → conclusion

Most importantly:

> **Do not add experiments merely because a reviewer might ask for them.**

Run an experiment only when it can distinguish live scientific accounts, change a load-bearing claim, or determine GO / RECONSTRUCT / KILL.

# L10 now

Run exactly:

1. **E01 — untouched-history stage decomposition**
2. **E02 — matched stage completion on actual action**

Command:

`good/L10_FROM_FAILURE_TO_ACTION/scripts/run_pilot.sh`

The pinned upstream Conditioned API Aversion source has exactly **10 items** and the current manifest maps all ten.

Nothing else is queued before those results.

# L12 now

The current scientific question is:

> **After reasoning-oriented post-training makes decisions almost invariant to framing, does the model’s own long reasoning trajectory take over causal control of the final answer?**

Current evidence already supports:

- Think-SFT frame consistency ≈ **0.992** vs Instruct-SFT ≈ **0.817**;
- frame identity remains represented early/mid;
- complete natural trajectories exert very large causal control on A/B readout;
- short answer-free arithmetic snippets do not reproduce that effect.

Run next:

1. **E07 — Conclusion-Stripped Trajectory Takeover**

   `good/L12_REASONING_DECISION_INVARIANCE/scripts/run_trajectory_takeover.sh`

   Question: does the remaining long trajectory still control the answer after the terminal explicit choice/conclusion is removed?

2. **E08 — Pre-Answer Decision-State Causal Substitution**

   Run **only if E07 supports trajectory-level control**:

   `good/L12_REASONING_DECISION_INVARIANCE/scripts/run_state_substitution.sh`

   Question: can a matched opposite-frame pre-answer hidden state transfer decision control without appending donor reasoning text?

There is **no active semantic-boundary branch**. Do not recreate it for novelty defense.

# Stop discipline

Avoid:

- model zoos;
- broad benchmark expansion;
- semantic-boundary / irrelevant-context batteries;
- extra “reviewer may ask” controls;
- hidden-state experiments without a load-bearing mechanism question.

For L12, the positive mechanism chain is:

> behavioral invariance → preserved input information → trajectory takeover → trajectory-built decision state.
