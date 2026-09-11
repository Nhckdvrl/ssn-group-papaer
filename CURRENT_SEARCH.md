# Current Research State — 2026-09-11

**Target:** ACL / EMNLP / NAACL Main  
**Approved paper mainline:** **NONE**  
**Active serious candidates:** **NONE**  
**Current phase:** **BROAD SEARCH OPEN — no candidate carries experiment authorization**  
**Killed ledger:** through **K183** — **Next kill ID: K184**

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

# Most recent kill — L15 (K183)

## No Result Is Not No Evidence — ARCHIVED / NO-GO, 2026-09-11

Canonical package: `candidates/L15_NULL_EVIDENCE_OBSERVATION_MODEL/` (no authorization).

The locked RQ was:

> **For the same observed null result, does an LLM scale its world-state update with counterfactual detectability, and can it correctly represent `P(null|H)` while failing to use that quantity in `P(H|null)`?**

Its own bounded E01/E02 pilot answered no. With normal reasoning allowed, both model
families track the detectability-conditioned posterior essentially exactly (Spearman
.989 / .945, compression ratio .985 / .929, KNI rate .003 / .014, obs-known rate 1.000).
The direct-answer failure is not null-specific: the `f=0` positive counterpart and the
bare arithmetic control fail by the same margin, while prior-only is exact.

E03 was never run — it was conditional on an integration gap that does not exist.

**The forbidden fallback is recorded explicitly:** "LLMs need explicit reasoning to use
observation models" is a different paper identity, was never selected, and compresses
into generic chain-of-thought / Bayesian-elicitation / reasoning-and-calibration work.
It survives as a historical observation, not as a route.

Full record: `candidates/L15_NULL_EVIDENCE_OBSERVATION_MODEL/PILOT_REPORT.md` and
`failed/KILLED_LEDGER.md` K183.

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