# Current Research State — 2026-09-11

**Target:** ACL / EMNLP / NAACL Main  
**Approved paper mainline:** **NONE**  
**Active serious candidates:** **L14 only**  
**Current phase:** **BROAD SEARCH OPEN + L14 ONE BOUNDED PILOT AUTHORIZED**

---

## Portfolio reset

The previous active portfolio has been archived. Existing code, data, and results are preserved for reproducibility, but none carries current experiment authorization.

Archived in this reset:

- **L03 — Table Value ≠ Observation Status**
- **L06 — Study Identity Is Not Document Identity**
- **L07 — Official Correction ≠ Current Scholarly Claim**
- **L08 — Readout-Dimension / Compression Evaluation**
- **L09 — RLVR Disagreement: Erased or Suppressed?**
- **L10 — From Failure to Action**
- **L12 — Reasoning-Induced Invariance / Trajectory Takeover**
- **L13 — Temporal Order ≠ Event Realization**

L02, L04, and L11 were already historical / killed routes.

The decisive workflow lesson remains:

> **A topic is not selected once. We continuously select the paper we are actually writing. Evidence survives claim mutation; authorization does not.**

---

# Current serious candidate — L14

## Negation of the World, or Negation of the Words?

Canonical package: `candidates/L14_METALINGUISTIC_NEGATION/`

### Plain example

> **The movie wasn't good — it was excellent.**

The speaker rejects *good* as an inadequate description while still committing to a world state at least as strong as *good*.

Contrast:

> **The movie wasn't good — it was terrible.**

Here `not` genuinely negates the world-state proposition.

### Current RQ

> **Does an LLM select what semantic level `not` targets before applying polarity, or do models/negation-focused interventions over-apply world-state reversal when the target is metalinguistic?**

### Fresh pre-pilot audit result

**PASS FOR ONE BOUNDED KILL-ORIENTED PILOT.** Not mainline-approved.

The strongest modern compression was explicitly checked:

> **EMNLP 2025 Negation Blindness + Findings EMNLP 2025 negation-attention prompting + classical metalinguistic-negation stimuli.**

The surviving independent question is whether the established drive for stronger ordinary-negation sensitivity is actually monotonic once negation can target a linguistic representation instead of a proposition.

Two fresh boundaries are locked:

1. **Artificial Epanorthosis (Boggia 2026)** shows that LLMs overproduce/miscalibrate corrective `Not X. Y` rhetoric. This is an LLM-specific motivation/production anomaly, not our claimed comprehension result.
2. **ImplicatureX (Spinoso-Di Piano et al. 2026)** owns implicature recognition/cancellation. Scalar `some→all` cases are diagnostic only and cannot carry or rescue L14.

### Authorized pilot only

After human stimulus audit, run:

- **E01:** paired DN/MN world-state target-selection profile on 40–60 bases with positive/paraphrase controls;
- **E02:** apply the pre-existing warning-based negation intervention from Barreto & Jana (2025) to the exact same items and measure paired `ΔDN` and `ΔMN`.

The strongest prospective signal is:

> **ordinary descriptive-negation accuracy improves while metalinguistic accuracy worsens**, showing that increased cue sensitivity trades negation blindness for over-negation.

Only if E01/E02 survive may the project return to selection for possible E03:

- pre-context versus post-correction to distinguish polarity-first repair from context-sensitive target selection.

No hidden-state scan/model zoo is authorized before that decision.

### Kill rule

Archive if capable models are essentially ceiling; warning produces no meaningful DN/MN differential and there is no independent target-selection structure; controls explain the effect; the signal is scalar-only; human readings/gold are unstable; or a direct current owner appears.

See:
- `candidates/L14_METALINGUISTIC_NEGATION/README.md`
- `candidates/L14_METALINGUISTIC_NEGATION/RELATED_WORK_AND_NOVELTY.md`
- `candidates/L14_METALINGUISTIC_NEGATION/DATA_AND_GOLD.md`
- `candidates/L14_METALINGUISTIC_NEGATION/PILOT_CARD.md`

---

# Search objective

The preferred new topic style remains:

> **durable and immediately understandable problem → simple natural/controlled data with hard gold → genuinely unresolved LLM-era question → interesting decisive experiment → broader consequence for actual NLP/LLM behavior.**

The ideal question should be understandable from one example, but should not reduce to “does the model know a textbook linguistic distinction?”

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
