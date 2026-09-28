# L13 — Minimum Decisive Pilot

Preregistered 2026-09-11, **before** any model was run on `stimuli_v1`.

## Cheapest load-bearing uncertainty

Not "do LLMs get `before` right". It is:

> **Is event-realization commitment separable from temporal-relation computation, and
> does forcing timeline construction move it?**

## E01 — Commitment profile (behavior)

- Items: all 200 (`stimuli_v1`), paired within base.
- Probes: P1 (strict, 6 permutations) and P2 (likelihood, 5 options).
- Task order: `fact_first`.
- Models: 4 checkpoints spanning ≥3 families (see `ENVIRONMENT.md`).
- Primary quantities, per model, bootstrapped over the 40 bases (10k resamples, 95% CI):
  - `commit(c)` = mean P1 probability mass on `YES` in condition `c`;
  - `neutral_gap` = `commit(before_neutral) − commit(nontemporal_neutral)`;
  - `veridicality_gap` = `commit(after) − commit(before_neutral)`;
  - `update_asymmetry` = `|commit(before_confirm) − commit(before_neutral)| −
    |commit(before_neutral) − commit(before_cancel)|`;
  - P1/P2 dissociation on `before_neutral`.

## E02 — Timeline-induced actualization (the decisive manipulation)

Same items, same P1 probe, `timeline_first` vs `fact_first`.

- Primary quantity: `timeline_effect(c) = commit_timeline(c) − commit_fact(c)`, paired
  by base, with `before_neutral` as the target condition and `after` /
  `nontemporal_neutral` as controls (a genuine coupling effect should be concentrated on
  the unresolved temporal condition, not a uniform shift).

Run E02 only after E01 completes; both are cheap enough to run in one session.

## Preregistered interpretation

| pattern | reading |
|---|---|
| `neutral_gap` ≫ 0 and `timeline_effect(before_neutral)` ≥ +8pp with CI excluding 0, on ≥2 families | **Account B** — timeline construction contaminates realization. Escalate to mechanism (C3). |
| `neutral_gap` ≈ 0, `timeline_effect` ≈ 0, symmetric update, on all families | **Account A** — separability. Not automatically a paper; go to the reconstruction rule below. |
| large `update_asymmetry` (cancellation harder than confirmation) without a timeline effect | partial B — commitment is premature but not caused by explicit timeline construction; reconstruct around **default realization bias**. |
| P1 near-ceiling but P2 flat across conditions | the model answers the label without representing the distinction; reconstruct around **readout vs representation**. |

## Kill rule (hard)

KILL if **all** of the following hold across all four models:

1. `commit(after) > 0.95` and `NOT_DETERMINED` is the modal P1 answer for
   `before_neutral` at ≥ 0.80;
2. `neutral_gap` 95% CI within ±3pp;
3. `|timeline_effect|` < 3pp with CI inside ±3pp for every condition;
4. `update_asymmetry` CI covers 0;
5. no cross-family heterogeneity (all CIs overlap).

That configuration means the two computations are simply separate, resolution is
symmetric, and no boundary is visible — nothing remains but a competence report, which
is a K064 resurrection. Do not rescue it with more models or more items.

## Reconstruction rule

If Account A wins but any of (2)–(5) fails, the surviving project is the **boundary**
question: where does separability break (item veridicality bias from the norming
literature, longer discourse, multi-event timelines, generation instead of scoring),
and which families break first. That is a legitimate reconstruction, not a rescue.

## Explicitly not in the pilot

Model zoo, prompt-format batteries, hidden-state probing, natural-corpus replication,
human annotation at scale. Each is authorized only by a specific downstream claim.
