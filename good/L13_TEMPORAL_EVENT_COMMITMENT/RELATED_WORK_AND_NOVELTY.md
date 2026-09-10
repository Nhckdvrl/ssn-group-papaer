# L13 — Live Novelty Audit

Audit date: **2026-09-11**. This file is live; re-run the audit before any load-bearing
claim is promoted (RESEARCH_EXECUTION.md §3).

## 1. Classical parents (assets, not competitors)

- Non-veridicality of `before` vs veridicality of `after` (Anscombe; Heinämäki;
  Beaver & Condoravdi). Establishes that the distinction is real and stable for humans;
  we do not claim to discover it.
- Psycholinguistic processing of `before`/`after`: Politzer-Ahles et al. (2017),
  *"Before" and "after": Investigating the relationship between temporal connectives and
  chronological ordering using event-related potentials*, PLOS ONE 12(4):e0175199 —
  publishes critical stimuli **and item-level veridicality norming ratings**, and states
  explicitly that their `before` items were largely pragmatically veridical (mean
  ratings ≈ 4.2/5) with no anti-veridical condition. We use this as a naturalness
  reference and as evidence that item-level veridicality bias is a real, measurable
  nuisance variable — **not** as our benchmark.
- Richer Event Description annotation guidelines: hypothetical/generic events must not
  be placed on the actual timeline. This is the applied statement of our concern.

## 2. Nearest modern neighbours and what they own

| work | owns | does not own |
|---|---|---|
| *Are Large Language Models Temporally Grounded?* (2024) | ordering, duration, self-consistency of **given** events | whether a temporal relation licenses believing a relatum exists |
| Temporal-mechanism work on before/after ordering (attention heads / temporal tokens, 2026) | internal machinery of **ordering** | realization commitment as a separate quantity, and its coupling to ordering |
| MAVEN-FACT (Findings EMNLP 2024) | large-scale event factuality labels; LLM benchmark; link to event hallucination | any manipulation of the temporal construction or of timeline-construction demand |
| TReMu (Findings ACL 2025) | temporal anchoring, unanswerable time questions | existence of the event |
| Belief-R (EMNLP 2024) | defeasible belief revision under new evidence in general | whether the *temporal* construction is what created the premature belief |
| Simple linguistic inferences / veridicality NLI lines | veridicality under embedding predicates | narrator-level non-veridicality from a temporal adjunct, and order/realization coupling |

## 3. Reviewer compression test

> "This is just ______."

Candidate compressions and answers:

- *"Event factuality with before/after items."* — would be accurate if we only reported
  accuracy per connective. It stops being accurate once the load-bearing evidence is
  the **task-order manipulation** (timeline-first vs realization-first on identical
  text) and the **update asymmetry**, neither of which a factuality dataset produces.
- *"Another temporal reasoning benchmark."* — we do not score ordering accuracy as an
  end; ordering is the manipulated cause, not the measured skill.
- *"Belief revision, again."* — Belief-R asks whether models revise at all. We ask
  whether the temporal construction manufactures the belief that must then be revised.

## 4. Honest novelty statement

Searches on 2026-09-11 (before/after non-veridicality × LLM; temporal clause ×
factuality × LLM; timeline construction × event realization; ACL Anthology temporal +
factuality 2025–2026) returned **no work that owns the coupling question**. This is not
a proof of global absence. Our claim is:

> the parents are mature and independently valuable; the specific question of whether
> temporal-relation computation causally contaminates event-realization commitment in
> LLMs is, as of this audit, unowned.

## 5. Weakest dimension (declared in advance)

Frontier models may handle explicit cancellation almost perfectly. Novelty therefore
must not rest on error rate. It rests on **coupling magnitude, task-order sensitivity,
update asymmetry, and cross-family heterogeneity** — quantities that remain measurable
at ceiling accuracy.
