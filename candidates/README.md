# Serious Candidate Portfolio — 2026-09-14

**Target:** ACL / EMNLP / NAACL Main  
**Approved paper mainline:** **NONE**  
**Active serious candidates:** **L39 — PILOT-AUTHORIZED — E01 ONLY**; **L38 — SERIOUS CANDIDATE / identification blocker / no pilot**  
**Search state:** **BROAD SEARCH OPEN; NO SURVIVOR QUOTA**

> `PILOT-AUTHORIZED` is not an approved paper mainline. It authorizes only the explicitly bounded experiment named in the candidate package. A failed pilot must close the parent rather than trigger model/prompt/construction rescue.

## Current newly authorized candidate

### L39 — Past Is Not Always Before

Package: [L39_SEQUENCE_OF_TENSE_REANCHORING/](L39_SEQUENCE_OF_TENSE_REANCHORING/)

**Status:** `PILOT-AUTHORIZED — E01 ONLY; NOT MAINLINE`

Locked RQ:

> **Can language models re-anchor temporal meaning compositionally when surface tense morphology conflicts with the correct discourse/reference-time interpretation?**

The identifying instrument is English Sequence of Tense (SOT): a past-under-past report such as `John said that Mary was sick` can license a reading where Mary's sickness overlaps John's saying time. Embedded past therefore does not itself entail anteriority relative to the matrix attitude time.

E01 starts from Mucha, Renans & Romoli's published human SOT materials rather than a new benchmark. The pilot asks whether strong current models specifically fail to license/use the simultaneous interpretation while succeeding on explicit anteriority and ordinary temporal controls. The strongest result would be a knowledge–deployment dissociation: the model can state the SOT rule but still over-infers `PAST => BEFORE` in contextual reasoning.

Critical identification rule: **do not label an ambiguous bare SOT sentence as uniquely simultaneous.** Measure compatibility/licensing and non-entailment of anteriority.

See:
- [candidate README](L39_SEQUENCE_OF_TENSE_REANCHORING/README.md)
- [bounded E01 protocol](L39_SEQUENCE_OF_TENSE_REANCHORING/E01_PROTOCOL.md)

No E02/E03/E04 is authorized unless E01 survives and the project returns to Selection.

## Other current serious candidate

### L38 — What Does Ellipsis Reconstruct?

Package: [L38_ELLIPSIS_RECONSTRUCTION_SUBSTRATE/](L38_ELLIPSIS_RECONSTRUCTION_SUBSTRATE/)

**Status:** `SERIOUS CANDIDATE — IDENTIFICATION BLOCKER; NO PILOT AUTHORIZED`

L38 remains separate from L39. Do not use L39 authorization to start L38 experiments.

---

## Historical portfolio note

Older candidate directories are retained for provenance and reproducibility. Directory presence does not imply active authorization.

### L15 — No Result Is Not No Evidence

Null evidence as an observation-model integration problem.  
**Status:** **ARCHIVED / NO-GO — KILL K183 (2026-09-11), killed by its own bounded pilot.**  
Canonical package: [L15_NULL_EVIDENCE_OBSERVATION_MODEL/](L15_NULL_EVIDENCE_OBSERVATION_MODEL/)

Locked question:

> **For the same observed null result, does an LLM scale its world-state update with counterfactual detectability, and can it correctly represent `P(null|H)` while failing to use that quantity in `P(H|null)`?**

The expanded ownership audit explicitly covers classical absence-of-evidence work, NAACL 2025 evidence→belief, ACL 2025 Bayesian updating, JAMA negative-test posterior reasoning, 2026 selection neglect, current RAG evidence-sufficiency work, and 2026 belief-state / partial-observability methods.

The pilot answered this in the negative: with normal reasoning allowed both model families compute the detectability-conditioned posterior essentially exactly (KNI rate .003 / .014), and the direct-answer failure is general rather than null-specific. See [PILOT_REPORT.md](L15_NULL_EVIDENCE_OBSERVATION_MODEL/PILOT_REPORT.md).

The route survived only for the exact locked computation. Generic Bayesian reasoning, evidence reliability, diagnostic Bayes, selection neglect, RAG abstention, partial observability, belief-state tracking, probabilistic memory, and external filtering are not available as rescue narratives.

See:
- [README](L15_NULL_EVIDENCE_OBSERVATION_MODEL/README.md)
- [ownership audit](L15_NULL_EVIDENCE_OBSERVATION_MODEL/RELATED_WORK_AND_NOVELTY.md)
- [data/gold contract](L15_NULL_EVIDENCE_OBSERVATION_MODEL/DATA_AND_GOLD.md)
- [bounded pilot card](L15_NULL_EVIDENCE_OBSERVATION_MODEL/PILOT_CARD.md)
- [pilot report and kill decision](L15_NULL_EVIDENCE_OBSERVATION_MODEL/PILOT_REPORT.md)
- [experiment ledger](L15_NULL_EVIDENCE_OBSERVATION_MODEL/EXPERIMENTS.md)

## Archived in the 2026-09-11 reset

- **L03 — Table Value ≠ Observation Status:** NO-GO by portfolio reset / user preference and paper-priority review.
- **L06 — Study Identity Is Not Document Identity:** NO-GO; strong data but the successful-result story compresses to study grouping/publication linkage plus established evidence-synthesis principles.
- **L07 — Official Correction ≠ Current Scholarly Claim:** NO-GO; fresh ownership audit compresses the broad authoritative-supersession/current-validity principle, leaving mainly a scholarly-domain instantiation.
- **L08 — Readout-Dimension / Compression Evaluation:** NO-GO; substantial evidence preserved, but reconstructed paper identity is not grandfathered into novelty and is removed from active execution.
- **L09 — RLVR Disagreement: Erased or Suppressed?:** NO-GO; the proposed mechanism space is crowded by RLVR entropy/diversity collapse, ambiguity representation, and post-training latent-state work.
- **L10 — From Failure to Action:** NO-GO; current self-reflection/tool-error work compresses the planned diagnosis→policy→action decomposition below the desired Main-level independent contribution.
- **L12/L13:** NO-GO; retained as workflow lessons on claim mutation and novelty reset.
- **L14 — Negation of the World, or Negation of the Words?:** NO-GO before pilot; technically plausible but too narrow and insufficiently exciting/broad for the current Main-level search objective.

Historical packages remain for reproducibility; location does not imply authorization.

## Search objective

Prefer paper-shaped questions with the character of strong classic-problem modernizations:

> **a durable, immediately understandable problem → simple natural/controlled data with hard gold → a genuinely unresolved LLM-era computation → an experiment whose result is intrinsically interesting → a clear consequence for real language-model use.**

A candidate must expose a broad model computation or bias, not merely an uncovered linguistic construction.

Before any pilot, require:

1. strongest plausible successful result and what it would actually establish;
2. strongest `Prior A + B + C = our paper` compression;
3. prospective development path and fresh novelty check for the likely next paper identity;
4. clean data/gold/identification route;
5. Main-level reason to care beyond a benchmark cell;
6. explicit claim-mutation trigger: if the paper identity changes, authorization expires until re-selection.

No survivor quota.
