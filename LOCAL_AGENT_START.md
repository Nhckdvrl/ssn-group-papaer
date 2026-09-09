# Local Agent Start — Current Execution Handoff

**Date:** 2026-09-09  
**Target:** NAACL Main  
**Approved paper mainline:** NONE

# Priority

1. **L10 — From Failure to Action**  
   `good/L10_FROM_FAILURE_TO_ACTION/`
2. **L12 — Reasoning-Induced Invariance**  
   `good/L12_REASONING_DECISION_INVARIANCE/`
3. **L08 — strong backup**

**L11 is KILL / K181.**

Do not reopen topic search unless explicitly requested.

# Execution rule

Read `RESEARCH_EXECUTION.md` and the selected canonical package first.

Keep:
> claim → experiment → config/code → raw result → conclusion

Most importantly:

> **Do not add an experiment merely because a reviewer might ask for it.**

Run an experiment when it can:
- distinguish live scientific accounts;
- change a load-bearing claim;
- determine GO / RECONSTRUCT / KILL;
- establish a consequence required by the paper identity.

# L10 now

Run:
1. **E01 untouched-history stage decomposition**
2. **E02 stage completion**

Nothing else is queued before those results.

# L12 now

Run:
1. **E07 semantic-relevance boundary**
2. **E08 decision-state causal substitution**, only if E07 is informative

Nothing else is queued before those results.

Avoid model zoos, broad benchmark expansion, and defensive control batteries until a result creates a specific scientific reason for them.
