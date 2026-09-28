# L13 — Paper outline (draft 1, 2026-09-11)

**Working title:** Extraction Makes It Real: LLMs Judge Unrealized Events Correctly and
Then Extract Them as Events

(Earlier title "Ghost Events on the Timeline" named the wrong mechanism; E16 shows the
ordering demand is not required.)

**Venue target:** NAACL / ACL / EMNLP Main. Long paper, empirical/analysis.

---

## Hook (Figure 1)

> *Before Maya submitted the application, the portal closed.*

Ask the model whether the passage guarantees that Maya submitted: Gemma-3-12B answers
*not determined* (0.86). Ask the same model for a timeline of the same sentence and it
writes `Maya submitted the application.` (0.93), and then answers *yes* (+0.33).

Figure 1: two panels on the same sentence — the direct judgement (correct) and the
emitted timeline (wrong) — plus the `Before X, Y` / `Y never happened` self-contradictory
timeline from Llama.

## Contribution claims

1. **A dissociation.** LLMs represent the non-veridicality of `before` when asked
   directly, and discard it when they emit an event structure. Direct
   `NOT DETERMINED` 0.59–0.86 vs plain-timeline instantiation 0.45–1.00, against a
   matched non-temporal control at ~0.10 that human(-author) ratings confirm is matched
   on pragmatic expectation (2.38 vs 2.42 on 1–5).
2. **The structure causes a belief change.** On identical text and an identical probe,
   emitting a timeline raises realization commitment by +0.075 to +0.332 across 9
   checkpoints and 4 families, against a form-matched paraphrase-first control; the
   effect is ~0 on the non-temporal passage. A non-generative ordering demand produces
   nothing (≤0.07), so the effect lives at the point of emitting the structure.
3. **Reasoning perfects the order and completes the error.** Qwen3-8B with thinking:
   emitted chronological order 0.34 → 1.00 correct, instantiation of the unresolved
   event 0.45 → 1.00. Across models the two quantities are independent (Llama: order
   0.15 / instantiation 0.98). This is the title claim, measured.
4. **It is not plausibility, not scale-fragile, and not prompt-fixable.** No monotone
   dependence on item pragmatic bias; instantiation *rises* from Qwen3-8B (0.45) to
   Qwen3-14B (0.98) and 32B (1.00) with the control flat at 0.10; an explicit
   prohibition, an explicit three-state schema and a status-first pipeline all fail on
   the unresolved case while the same interventions nearly eliminate the
   explicitly-negated case (0.35–0.90 → 0.00–0.08).
5. **Scope, stated precisely.** The failure is confined to the case where
   non-veridicality is carried by **nothing but the temporal connective**. The same
   proposition with the same open status, marked aspectually
   (*"was about to … when …"*), is kept off the timeline (0.150 in all three models);
   marked modally (*"before X could Y"*) likewise (0.025–0.250), in constructed and in
   natural text alike. A hand-adjudicated prevalence sample puts the affected
   construction at ~13% of natural `before`-clauses.

## Section plan

| § | content | evidence |
|---|---|---|
| 1 | Introduction, Figure 1, contributions | — |
| 2 | Background: `before`/`after` (non)veridicality; event factuality; temporal reasoning; why RED forbids hypothetical events on the actual timeline | `RELATED_WORK_AND_NOVELTY.md` |
| 3 | Materials: 40 bases × 5 conditions; minimal pairs; the two controls; gold and its audit | `DATA_AND_GOLD.md`, `data/GOLD_AUDIT_v1.md` |
| 4 | Measurement: permutation-controlled label scoring; the ghost-node adjudication rule and its validation | `src/scoring.py`, `src/ghost_detect.py` |
| 5 | The dissociation (C1 rejected, C5 supported) | E01, E04 |
| 6 | Structure changes belief (C2), and requires emission (E05) | E02, E05 |
| 7 | Reasoning: order up, realization down | E09 |
| 8 | What it is not: plausibility (E11), scale (E07), schema (E06) | E06, E07, E11 |
| 9 | What can and cannot be repaired (E10) | E10 |
| 10 | Scope and prevalence in natural text (E08) | E08 |
| 11 | Implications for timeline/event-graph extraction, temporal QA, agent state | — |
| 12 | Limitations | below |

## Limitations to state in the paper

1. English only; one construction (`before`-clauses); 40 base scenarios.
2. Gold and the natural-set adjudication are **author** judgements with a written,
   blinded protocol and published raw responses — not independent annotation. This is
   the one item that must be closed before submission.
3. Instantiation is scored by a validated rule (159/160 against hand adjudication) that
   under-counts; all rates are lower bounds.
4. The mechanism is characterised at the level of emitted structure. E05 rules out a
   representation-level coupling that needs no generation; it does not localise where in
   generation the collapse happens.
5. `yes_leaning` has only 4 items, so the moderation result rests on the
   no_leaning/neutral contrast and the ceiling models.

## Work required before submission

1. **Independent annotation** of `before_neutral` gold, the naturalness ratings, and a
   sample of ghost-node judgements. Blocking.
2. Two or three more families for the headline table (Mistral-Small-24B and Phi-4-mini
   are in the local cache), and closed-weight API models if the budget allows.
3. More connectives (`until`, `by the time`, `in time to`). E12 already establishes the
   marked/unmarked boundary with `about_to` and `before X could Y`; this extends it.
4. One realistic downstream task (timeline extraction → temporal QA) so §11 rests on
   measurement rather than argument.
5. Figures: F1 hook; F2 direct-vs-structure dissociation across models; F3 scale ladder;
   F4 order-vs-instantiation scatter; F5 intervention ladder (plain → prohibition →
   schema → status-first) split by `unresolved` vs `not-realized`.
