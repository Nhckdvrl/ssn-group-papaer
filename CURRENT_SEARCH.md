# Current Research State — 2026-09-09

**Target:** NAACL Main  
**Approved paper mainline:** NONE  
**Killed ledger:** through K180  
**Next kill ID:** K181

> This file records **current status only**. It is not a workflow manual and should not accumulate historical search rules.  
> Search rules: **RESEARCH_TOPIC_SEARCH.md**  
> Candidate gates: **RESEARCH_TOPIC_SELECTION.md**  
> Execution rules: **RESEARCH_EXECUTION.md**

---

# Current phase

The earlier six-topic search target was completed. The user explicitly reopened broad search on 2026-09-09 and requested **two additional topics that are genuinely worth advancing**.

That search round is now complete.

Two new candidates survived current literature assassination, paper-level novelty review, data/identification review, reviewer-compression testing, outcome-robustness review, and Main-level calibration:

- **L11 — Task Gradient ≠ Learning Pressure**
- **L12 — Reasoning Training: Canonicalization or Policy Override?**

Both are registered in **good/** as **PILOT-AUTHORIZED**.

Broad search can pause again unless the user reopens it or decisive pilots kill enough of the portfolio to justify another search round.

**Approved paper mainline remains NONE.**

The previously selected execution priority remains:

# **L08 as the first execution priority**

unless the user explicitly changes priority.

---

# Current eight-topic portfolio

| ID | Topic | Status | Canonical package | Immediate decisive work |
|---|---|---|---|---|
| **L03** | Table Value ≠ Observation Status | **PILOT-AUTHORIZED** | good/L03_TYPED_OBSERVATION/ | cross-provider typed-observation pilot |
| **L06** | Study Identity Is Not Document Identity | **SERIOUS / PILOT-READY** | candidates/L06_STUDY_IDENTITY/ | oracle / flat / wrong-split / wrong-merge with papers fixed |
| **L07** | Official Correction ≠ Current Scholarly Claim | **SERIOUS / DATA AUDIT FIRST** | candidates/L07_OFFICIAL_CORRECTION/ | proposition-level old→new correction-yield audit before GPU |
| **L08** | Low-Dimensional Readout Preserves Knowledge but Breaks Reasoning | **SERIOUS / CURRENT PRIORITY** | candidates/L08_READOUT_DIMENSION/ | parent reproduction + teacher-forced vs free-running + long-generation control |
| **L09** | RLVR Disagreement: Erased or Suppressed? | **SERIOUS** | candidates/L09_RLVR_DISAGREEMENT/ | secure matched pre/post RLVR pair + causal recovery test |
| **L10** | Success Teaches, Failure Doesn't? | **SERIOUS** | candidates/L10_SUCCESS_FAILURE_ASYMMETRY/ | matched success/failure stage decomposition |
| **L11** | Task Gradient ≠ Learning Pressure | **PILOT-AUTHORIZED** | good/L11_TASK_GRADIENT_PRESSURE/ | reproduce one gradient/gain paradox and decompose optimization loudness |
| **L12** | Reasoning Training: Canonicalization or Policy Override? | **PILOT-AUTHORIZED** | good/L12_REASONING_DECISION_INVARIANCE/ | reproduce same-family training-induced decision invariance and choose decisive mechanism split |

Eight active candidates do **not** mean eight approved projects.

---

# Newly registered candidates

## L12 — Reasoning Training: Canonicalization or Policy Override?

Established parent:
> ACL 2026 Outstanding work reports that reasoning-oriented models become substantially less sensitive to several equivalent risky-choice presentations and points toward reasoning-oriented training as an important differentiator.

Our question:
> **Does reasoning post-training genuinely canonicalize different presentations into a shared decision representation, or does framing/context information remain internally available but lose control over the final policy?**

Current open mechanism families:
- representational canonicalization;
- policy/readout override;
- inference-time deliberation;
- arithmetic-specialization boundary;
- another stronger mechanism if the pilot reveals one.

The candidate is deliberately **not locked to one interpretability method**.

Main-level requirement:
> established behavioral anomaly → independent mechanism question → decisive evidence → meaningful boundary/consequence → reinterpretation of reasoning-induced decision invariance.

## L11 — Task Gradient ≠ Learning Pressure

Established parent:
> EACL 2026 reports large task-specific gradient imbalance during multi-task RL post-training, including cases where gradient magnitude does not track learning gain and simple reward/advantage/length explanations are insufficient.

Our question:
> **What makes one natural language/reasoning task optimization-loud, and does raw parameter-gradient magnitude actually measure comparable learning pressure across tasks?**

Current open mechanism families:
- per-example/token sensitivity;
- within-response cancellation;
- across-example update coherence;
- parameter-space vs function-space miscalibration;
- another stronger source if discovered.

The candidate is deliberately **not locked to GradNorm, gradient surgery, Fisher, or any single decomposition**.

Main-level requirement:
> established gradient/gain paradox → explanatory mechanism or measurement correction → decisive validation → consequence for multi-task LLM post-training.

---

# Package philosophy for L11/L12

The new candidate packages intentionally separate:

## Hard constraints
- natural and important RQ;
- established parent phenomenon;
- credible identification;
- paper-level novelty;
- outcome robustness;
- explicit reviewer-compression boundary;
- continuous ACL/EMNLP/NAACL Main calibration.

## Open research space
- exact probe/patching/gradient metric;
- exact model family after the first reproducible lineage;
- which account ultimately wins;
- precise section/claim ordering;
- whether the final paper becomes mechanism-first, measurement-first, boundary-first, or another stronger reconstruction.

Candidate documents should guide research, not force the data into a prewritten paper.

---

# Current mechanism-candidate ranking

The portfolio is not a strict permanent ranking.

At current paper-design confidence:

- **L12** — especially strong natural mechanism question anchored in an ACL 2026 Outstanding parent.
- **L11** — strong optimization/measurement question with more crowded related work but a surviving paper-level corridor.
- **L08** — still one of the cleanest established-anomaly mechanism corridors and remains the currently selected execution priority.
- **L10/L09** — strong mechanism questions with narrower/crowded neighborhoods.

Do not treat this ordering as protection from pilot results.

---

# Recent dead routes

- **L02 / K175:** gold ≠ estimand; DNI/INI did not identify concrete filler support.
- **L05 / K176:** adaptive information-seeking story compressed by close causal/adaptive-search work.
- **L04 / K180:** remaining realization-cardinality story too outcome-fragile and narrow.
- **Temporal Forgetting revival:** old Lost Skill vs Lost Entry route remains dead because cue/prefix interventions do not identify retained competence; 2026 follow-up literature further crowds access-vs-execution and robust-regression explanations.

For all older killed parents, use **failed/KILLED_LEDGER.md**.

---

# Reopen search only when needed

Resume broad topic search when:
- the user explicitly requests more topics;
- decisive pilots kill enough candidates that replacement search is useful;
- a newly discovered literature collision invalidates a major part of the portfolio.

When reopened, follow:
1. **RESEARCH_TOPIC_SEARCH.md**
2. **TOPIC_SEARCH_PLAYBOOK.md**
3. formal candidate audit in **RESEARCH_TOPIC_SELECTION.md**

Do not use this status file as a source of search philosophy.
