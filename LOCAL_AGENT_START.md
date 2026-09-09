# Local Agent Start — Current Execution Handoff

**Date:** 2026-09-09  
**Target:** NAACL Main  
**Mode:** RESEARCH EXECUTION  
**Approved paper mainline:** NONE  
**Current user-selected priority:** **L08**

> Give this file to the local research agent when starting work.

The six-topic search portfolio is already complete. Do **not** generate new topics during ordinary execution.

---

# 1. Mandatory reading

Before experiments:

1. **RESEARCH_EXECUTION.md**
2. the selected candidate’s canonical package:
   - README.md
   - DATA_AND_GOLD.md
   - RELATED_WORK_AND_NOVELTY.md
   - RESEARCH_PLAN.md
   - PILOT_CARD.md

For current work, use:

> **candidates/L08_READOUT_DIMENSION/**

Do not execute from stale historical notes in CURRENT_SEARCH.md when they conflict with the canonical package.

---

# 2. Repository safety

During execution:

> **Only modify the concrete candidate directory being worked on.**

For L08, only modify:

> **candidates/L08_READOUT_DIMENSION/**

Keep inside that directory:
- source code;
- scripts;
- configs;
- data/pointers;
- results;
- claim ledger;
- experiment registry;
- environment/reproduction notes.

Do not edit root workflow files during ordinary experiment work.

Clean up disposable scripts/data after confirming they are no longer needed.

---

# 3. Current L08 scientific question

Parent result already reports the anomaly:

> severe reduction of final readout/representation dimensions preserves knowledge/extraction much better than GSM8K-style reasoning.

That phenomenon is **not our novelty**.

Our paper question is:

> **Why does the same final-readout bottleneck affect knowledge and multi-step reasoning so differently?**

Main accounts:
- **A — intrinsic local bottleneck:** each reasoning step itself needs higher-dimensional readout.
- **B — autoregressive accumulation:** local damage is small, but free-running generation compounds errors.
- **C — capability-specific geometry:** knowledge and reasoning rely on different readout/subspace structure.
- **D — length artifact:** long generation, not reasoning, explains the gap.

A hypothesis losing does not kill the question. Another account winning can be the result.

---

# 4. Minimum decisive first phase

Do not begin with a model zoo.

First phase:

1. **Exact/faithful parent reproduction**
   - confirm the reported capability asymmetry under a credible model/setup.

2. **Core comparison**
   - GSM8K or equivalent multi-step reasoning;
   - knowledge/extraction control;
   - long non-reasoning generation control.

3. **Most important mechanism split**
   - **teacher-forced reasoning**
   - vs **free-running reasoning**

Interpretation:
- teacher-forced local prediction mostly preserved + free-running collapse → supports accumulation;
- teacher-forced prediction itself collapses → supports intrinsic local readout bottleneck;
- long non-reasoning collapses similarly → length/generation explanation becomes serious;
- task-specific patterns remain after controls → geometry/boundary work becomes important.

Only after this split should the project expand into:
- reasoning-token-only truncation;
- answer-token-only truncation;
- one-step truncation then restore;
- random coordinate removal vs random projection;
- subspace transfer/geometry analysis.

---

# 5. Experiment discipline

Before every substantive run, record:
- experiment ID;
- linked claim;
- exact question;
- dataset/subset;
- model and revision;
- intervention/conditions;
- metric/statistical test;
- expected informative outcomes;
- interpretation/kill conditions.

After every run, record:
- exact command/config;
- raw result path;
- summary;
- uncertainty where relevant;
- interpretation;
- which claim changed.

Every important result must be traceable:

> **claim → experiment → config/code → data → raw result → conclusion**

---

# 6. Continuous novelty/Main-level check

Before a new load-bearing claim or major experiment:
- re-check the parent and closest follow-up literature;
- compare the planned claim with strong ACL/EMNLP/NAACL mechanistic/scientific work;
- ask whether the claim is genuinely discriminative or merely obvious;
- ask whether the project is still developing its own narrative.

Do not keep a trivial claim merely because it is easy to demonstrate.

Do not scale if the current result only supports:
> “reasoning is more sensitive than knowledge.”

That is the parent-level observation, not enough.

---

# 7. Pilot verdict

The first L08 phase should end with:

- **GO**
- **CONDITIONAL**
- **NO-GO**

Return:
1. data/intervention validity;
2. parent reproduction;
3. teacher-forcing vs free-running result;
4. long-generation control;
5. current mechanism ranking;
6. strongest reviewer compression after seeing the results;
7. exact reproducibility pointers;
8. next smallest decisive experiment.

Kill/reconstruct only when:
- reproduction fails in a way that destroys the scientific object;
- intervention lacks leverage;
- current literature already owns the resulting explanation;
- surviving result is trivial;
- no Main-level C1→C2→C3 remains.

A preferred hypothesis losing is **not** itself a kill condition.

---

# 8. Other serious candidates

The current six are:
- L03
- L06
- L07
- L08
- L09
- L10

If the user later changes priority, switch to that candidate’s canonical package and follow RESEARCH_EXECUTION.md.

Until then:

# **Start with L08.**
