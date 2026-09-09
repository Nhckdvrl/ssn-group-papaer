# Current Research State — 2026-09-09

**Target:** NAACL Main  
**Approved paper mainline:** NONE  
**Killed ledger:** through K181  
**Next kill ID:** K182

> Current status only.  
> Search rules → **RESEARCH_TOPIC_SEARCH.md**  
> Candidate gates → **RESEARCH_TOPIC_SELECTION.md**  
> Execution rules → **RESEARCH_EXECUTION.md**

---

# Current phase

# **RESEARCH EXECUTION — broad search paused**

Do not reopen broad topic search unless the user explicitly asks or decisive evidence destroys enough of the active portfolio to justify replacement search.

Current execution priority:

1. **L10 — From Failure to Action** — **A / PILOT-AUTHORIZED / Rank 1**
2. **L12 — Reasoning-Induced Invariance / Trajectory Takeover** — **A / CONTINUE-PILOT / Rank 2**
3. **L08 — Low-Dimensional Readout Preserves Knowledge but Breaks Reasoning** — **HOLD / strong backup / Rank 3**

**L11 is KILL / K181.**  
**Approved paper mainline remains NONE.**

---

# Rank 1 — L10

> **Why can an LLM remember that an action failed yet repeat the same action? Where does failure experience stop becoming future action?**

The parent failure/inhibition gap is robust and independently corroborated.

Immediate work:

> untouched-history stage decomposition → matched stage completion on actual action.

Runnable scaffold:

`good/L10_FROM_FAILURE_TO_ACTION/scripts/run_pilot.sh`

---

# Rank 2 — L12

## Current question

> **When reasoning training makes decisions almost invariant to framing/presentation, does the model's own long reasoning trajectory take over causal control of the final answer?**

Established locally:

- Instruct-SFT frame consistency ≈ **0.817**
- Think-SFT ≈ **0.992**
- difference ≈ **+0.175**, CI **[0.025, 0.367]**
- frame identity remains recoverable early/mid;
- complete natural trace strongly controls final readout;
- short arithmetic snippets do not explain the large trace effect.

### Next decisive experiment

**L12-E07 — Conclusion-Stripped Trajectory Takeover**

Ask whether natural reasoning still strongly controls A/B readout after removing its terminal explicit choice/conclusion.

Runnable scaffold:

`good/L12_REASONING_DECISION_INVARIANCE/scripts/run_trajectory_takeover.sh`

If E07 succeeds:

→ **L12-E08 — pre-answer decision-state causal substitution**

If E07 collapses:

→ reconstruct around **late self-commitment**; do not add rescue controls.

The older semantic context-boundary scaffold is parked, not a prerequisite.

---

# Rank 3 — L08

Still alive as a strong backup. Its final-readout truncation → teacher-forced vs free-running corridor remains natural, but the parent anomaly is less independently established than L10/L12.

---

# L11 — KILL / K181

The parent-compatible micro-pilot is unstable across seeds and prompt-bootstrap intervals cross zero. The natural why-space is also crowded.

Do not rescue L11.

---

# Active portfolio

| ID | Topic | Current status | Canonical package |
|---|---|---|---|
| **L03** | Table Value ≠ Observation Status | PILOT-AUTHORIZED, lower priority | good/L03_TYPED_OBSERVATION/ |
| **L06** | Study Identity Is Not Document Identity | SERIOUS / PILOT-READY | candidates/L06_STUDY_IDENTITY/ |
| **L07** | Official Correction ≠ Current Scholarly Claim | SERIOUS / DATA AUDIT FIRST | candidates/L07_OFFICIAL_CORRECTION/ |
| **L08** | Low-Dimensional Readout Preserves Knowledge but Breaks Reasoning | HOLD / strong backup / Rank 3 | candidates/L08_READOUT_DIMENSION/ |
| **L09** | RLVR Disagreement: Erased or Suppressed? | SERIOUS | candidates/L09_RLVR_DISAGREEMENT/ |
| **L10** | From Failure to Action | PILOT-AUTHORIZED / Rank 1 | good/L10_FROM_FAILURE_TO_ACTION/ |
| **L12** | Reasoning-Induced Invariance / Trajectory Takeover | CONTINUE-PILOT / Rank 2 | good/L12_REASONING_DECISION_INVARIANCE/ |

L11 historical artifacts remain under `good/L11_TASK_GRADIENT_PRESSURE/`, but it is not active.

---

# Reopen-search rule

Resume topic search only when the user explicitly requests it, decisive pilots kill enough active routes, or new literature destroys a load-bearing identity.
