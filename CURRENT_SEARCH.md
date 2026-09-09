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
2. **L12 — Reasoning-Induced Invariance** — **A / CONTINUE-PILOT / Rank 2**
3. **L08 — Low-Dimensional Readout Preserves Knowledge but Breaks Reasoning** — **HOLD / strong backup / Rank 3**

**L11 is KILL / K181.**  
**Approved paper mainline remains NONE.**

---

# Why the priority changed

## L10 — Rank 1

> **Why can an LLM remember that an action failed yet repeat the same action? Where does failure experience stop becoming future action?**

The parent failure/inhibition gap is unusually robust: ACL 2026 ImplicitMemBench evaluates 17 models and reports inhibition 17.6% versus preference 75.0%, with public artifacts. ACL 2026 Fission-GRPO independently reports repetitive invalid tool calls after execution errors.

Immediate work: **untouched-history stage decomposition → matched stage completion on actual action.**

## L12 — Rank 2

> **Does reasoning-oriented post-training learn which contextual changes are semantically irrelevant, or does it more broadly disconnect context from decisions?**

Own pilot establishes a usable sibling-branch contrast: Instruct-SFT frame consistency ≈ 0.817, Think-SFT ≈ 0.992, difference ≈ +0.175 with CI excluding zero.

Next:
1. **relevant-vs-irrelevant context boundary**;
2. then **conclusion-free decision-state causal substitution**.

## L08 — Rank 3

Still alive as a strong backup. Its final-readout truncation → teacher-forced vs free-running corridor remains natural, but the parent anomaly is less independently established than L10/L12.

## L11 — KILL / K181

The parent-compatible micro-pilot is unstable across seeds and all prompt-bootstrap intervals cross zero. The surrounding optimization/learning-progress/gradient-geometry literature also crowds the natural why-space. Preserving novelty would require technical compression and another phenomenon gamble.

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
| **L12** | Reasoning-Induced Invariance | CONTINUE-PILOT / Rank 2 | good/L12_REASONING_DECISION_INVARIANCE/ |

L11 historical artifacts remain under `good/L11_TASK_GRADIENT_PRESSURE/`, but it is not active.

---

# Reopen-search rule

Resume topic search only when the user explicitly requests it, decisive pilots kill enough active routes, or new literature destroys a load-bearing identity.
