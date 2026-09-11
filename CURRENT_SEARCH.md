# Current Research State — 2026-09-11

**Target:** ACL / EMNLP / NAACL Main  
**Approved paper mainline:** **NONE**  
**Active serious candidates:** **L15 only**  
**Current phase:** **BROAD SEARCH OPEN + L15 ONE BOUNDED PILOT AUTHORIZED**  
**Killed ledger:** through **K182** — **Next kill ID: K183**

---

## Portfolio reset

The previous active portfolio has been archived. Existing code, data, and results are preserved for reproducibility, but none carries current experiment authorization.

Archived in / before this reset:

- **L03 — Table Value ≠ Observation Status**
- **L06 — Study Identity Is Not Document Identity**
- **L07 — Official Correction ≠ Current Scholarly Claim**
- **L08 — Readout-Dimension / Compression Evaluation**
- **L09 — RLVR Disagreement: Erased or Suppressed?**
- **L10 — From Failure to Action**
- **L12 — Reasoning-Induced Invariance / Trajectory Takeover**
- **L13 — Temporal Order ≠ Event Realization**
- **L14 — Negation of the World, or Negation of the Words?** — archived before pilot because the likely strongest contribution was too narrow / insufficiently exciting for the current Main-level search objective.

L02, L04, and L11 were already historical / killed routes.

The decisive workflow lesson remains:

> **A topic is not selected once. We continuously select the paper we are actually writing. Evidence survives claim mutation; authorization does not.**

---

# Current serious candidate — L15

## No Result Is Not No Evidence

Canonical package: `candidates/L15_NULL_EVIDENCE_OBSERVATION_MODEL/`

### Plain example

> Camera A detects 99% of people who enter an airport. Camera B detects only 5%. Both return: **"Alice was not detected."**

The same null observation should be strong evidence against Alice's presence under A and almost uninformative under B.

### Locked RQ

> **For the same observed null result, does an LLM scale its world-state update with counterfactual detectability, and can it correctly represent `P(null|H)` while failing to use that quantity in `P(H|null)`?**

### Expanded ownership audit

**REGISTERED / PASS FOR ONE BOUNDED KILL-ORIENTED PILOT. Not mainline-approved.**

The audit explicitly includes:

- Hsu et al. 2017 classical absence-of-evidence work;
- NAACL 2025 **From Evidence to Belief**;
- ACL 2025 **Enough Coin Flips Can Make LLMs Act Bayesian**;
- JAMA 2023 LLM post-test probability after negative diagnostic results;
- Deng & Yan 2026 selection neglect / WYSIATI;
- 2026 Belief-State Engine, Belief-Based World Models, Belief Memory, T3/AREW;
- current RAG evidence-sufficiency / over-searching work.

These prior works own the broad neighborhood. L15 is authorized only for the exact five-part object:

1. identical null observation;
2. isolated detectability manipulation;
3. matched explicit `P(null|H)` probe;
4. separate `P(H|null)` probe;
5. competence–integration dissociation as the central target.

If development drops this identity and becomes generic Bayes, evidence reliability, medical diagnostic reasoning, selection neglect, RAG abstention, partial observability, or belief-state tracking, authorization expires immediately.

### Authorized pilot only

- **E01:** same-null detectability curve;
- **E02:** observation-likelihood competence versus posterior integration;
- **E03:** only if E02 reveals integration failure, make the observation likelihood explicit before the posterior update.

No agent/RAG/tool extension, hidden-state scan, model zoo, probabilistic-memory method, or external Bayesian filter is authorized before re-selection.

### Preferred signal

> **The model correctly knows how likely the observation process was to miss the target, yet fails to use that knowledge when deciding whether the target exists.**

### Kill rule

Archive if capable models already track the detectability-conditioned posterior; residual errors reduce to generic arithmetic/base-rate failure; observation-likelihood and posterior probes fail together; or the surviving story collapses into a neighboring already-owned claim.

See:
- `candidates/L15_NULL_EVIDENCE_OBSERVATION_MODEL/README.md`
- `candidates/L15_NULL_EVIDENCE_OBSERVATION_MODEL/RELATED_WORK_AND_NOVELTY.md`
- `candidates/L15_NULL_EVIDENCE_OBSERVATION_MODEL/DATA_AND_GOLD.md`
- `candidates/L15_NULL_EVIDENCE_OBSERVATION_MODEL/PILOT_CARD.md`

---

# Search objective

Prefer questions with this shape:

> **durable and immediately understandable problem → simple natural/controlled data with hard gold → genuinely unresolved LLM-era computation → result interesting enough to matter by itself → broader consequence for actual NLP/LLM behavior.**

The ideal question should be understandable from one example and should expose a broad model computation or bias, not merely an uncovered linguistic construction.

Classic parents are assets, not novelty failures. The novelty burden is on the **modern scientific question, inference, and development path**.

---

# Pre-pilot requirement for every new serious candidate

Before any compute authorization, record:

1. one-sentence RQ + plain example;
2. strongest plausible successful result and what it establishes;
3. prospective paper identity after the first result;
4. strongest current `Prior A + B + C = our paper` compression and surviving contribution;
5. development-path novelty for the likely next claim;
6. data/gold/identification with truth independent of the evaluated model;
7. Main-level progression beyond the first effect;
8. explicit stop condition.

---

# Durable workflow rule

`SEARCH → SELECT → PILOT → RE-SELECT CURRENT PAPER IDENTITY → DEVELOP → RE-SELECT → PAPER / ARCHIVE`

Claim mutation requires return to selection, not merely a wording update to related work.