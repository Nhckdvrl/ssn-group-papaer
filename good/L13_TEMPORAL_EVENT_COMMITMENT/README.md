# L13 — Temporal Order ≠ Event Realization

**Status:** PILOT-AUTHORIZED (registered 2026-09-11) — **not** paper-mainline-approved.
**Target:** NAACL / ACL / EMNLP Main.

---

## 1. The question in one example

> *Before Maya submitted the application, the portal closed.*

Did Maya submit the application?

The passage does **not** guarantee either answer. `after` is veridical
(*After Maya submitted the application, the portal closed* entails that she submitted);
`before` is not. The subordinate event of a `before`-clause is introduced into the
discourse, placed in a temporal relation, and yet its realization remains open until
later text resolves it.

## 2. Research question

> **When a text introduces an event whose realization is not yet licensed, does an LLM
> defer commitment, or does it prematurely instantiate that event while constructing a
> timeline?**

Equivalently: are **temporal relation** and **event realization** two separable
judgments inside an LLM, or does putting an event on a timeline itself push the model
toward believing it happened?

This is deliberately *not* "can LLMs label event factuality" (see `PARENT_AUDIT.md`,
K064). The estimand is a **coupling** between two computations, measured by a
manipulation of the temporal construction and of the task that forces timeline
construction.

## 3. Two accounts

**Account A — Deferred Commitment.**
Realization status and temporal relation are represented separately. Under
`before`-neutral the model holds the subordinate event at `unresolved`, and updates
symmetrically when the discourse later confirms or cancels it. Asking for a timeline
first does not move realization judgments.

**Account B — Eager Instantiation.**
Constructing a temporal relation instantiates both relata as timeline nodes, and being
on the timeline raises the model's commitment that the event occurred. Predictions:
(i) `before`-neutral is pulled toward YES beyond what a matched non-temporal unresolved
control produces; (ii) forcing an explicit timeline before the realization probe
increases YES further; (iii) later cancellation is harder to absorb than later
confirmation (asymmetric update).

Both accounts are informative. A clean Account A win with a real separability result is
a publishable negative/boundary answer only if it is accompanied by the trajectory and
heterogeneity structure described in `PILOT_CARD.md`; see the kill rules there.

## 4. Why it matters beyond semantics

Timeline / event-graph extraction, temporal QA, narrative state tracking, and agent
world-state all consume text in which mentioned events are not realized events.
Annotation standards (e.g. Richer Event Description) explicitly forbid putting
hypothetical events on the actual timeline, because downstream systems treat timeline
membership as existence. If LLM timeline construction itself manufactures existence,
that is a systematic, mechanism-level source of event hallucination — not a quiz about
one connective.

## 5. Package map

| file | role |
|---|---|
| `PILOT_CARD.md` | minimum decisive pilot, preregistered predictions, kill rules |
| `CLAIMS.md` | claim ledger |
| `DATA_AND_GOLD.md` | stimulus contract, gold definition, validation plan |
| `RELATED_WORK_AND_NOVELTY.md` | live novelty audit + reviewer compression test |
| `PARENT_AUDIT.md` | non-resurrection argument vs K064 / K068 and neighbours |
| `EXPERIMENTS.md` | experiment registry |
| `ENVIRONMENT.md` | environment, models, exact commands |

## 6. Current verdict — HOLD (claim novelty reset, 2026-09-11)

The authorized claim was rejected by E05 and the project has since mutated twice more
(E16, E17) without a novelty reset. `CLAIM_NOVELTY_DELTA.md` performs that reset and
puts the project on **HOLD / RECONSTRUCT around the interface, not around `before`**,
with a hard stop on further evidence accumulation. Read it before running anything.

### Superseded verdict

Pilot E01 (behavioral commitment profile) and E02 (timeline-induced actualization) have
not yet been run. No claim is established.
