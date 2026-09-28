# L15 — Bounded Pilot Card

**Date:** 2026-09-11  
**Authorization:** E01–E03 only  
**Mainline:** NOT APPROVED

## Locked question

> **For the same null observation, does the model use counterfactual detectability in its world-state update, and can it know `P(null|H)` while failing to integrate that quantity into `P(H|null)`?**

No experiment may broaden the question without returning to selection.

## Models

Start with two capable open model families. A third family is allowed only if model heterogeneity determines the decision.

Do not run a model zoo before re-selection.

## E01 — same-null detectability curve

Construct matched items over:

- `p ∈ {.2,.5,.8}`;
- `s ∈ {.05,.25,.50,.75,.95}`;
- `f=0`;
- four natural frames.

For every item, the visible outcome is the same: **no detection / no record / negative test / no matching result**.

Measure:

1. posterior absolute error;
2. Spearman correlation between model posterior and gold posterior across sensitivity levels;
3. monotonicity violations;
4. slope/range compression relative to gold.

Critical question:

> Does the model's posterior materially respond to detectability when surface evidence is unchanged?

## E02 — competence vs integration

For each E01 item ask separately:

1. `P(null|H)`;
2. `P(H|null)`.

Primary signature: **Known-but-Not-Integrated (KNI)** from `DATA_AND_GOLD.md`.

A strong result requires more than generic Bayes error. Preferred outcome:

> observation-likelihood estimate is correct, while posterior update remains materially wrong or insensitive to detectability.

## E03 — predeclared computation intervention

Only if E02 shows an integration gap:

- ask the model to compute/state `P(null|H)` first;
- feed that value into the posterior question;
- compare against baseline on identical items.

Interpretation:

- recovery supports a missing-use / integration explanation;
- no recovery weakens it and triggers re-selection or kill.

This is a diagnostic intervention, not a novel prompting method.

## Required controls

- positive-result counterpart;
- direct arithmetic Bayes control;
- prior-only baseline;
- multiple null-wording paraphrases;
- handed-likelihood control (`P(null|H)` explicitly supplied);
- no hidden domain priors.

## Primary success condition

At least one capable family must show a stable, replicated pattern that cannot be compressed to generic arithmetic error, preferably:

> **high P1 accuracy + substantial P2 error / detectability compression**, across at least two non-medical frames.

A mere statistical significance with tiny effect is not enough.

## Kill conditions

Kill immediately if:

- capable models track the detectability-conditioned posterior well across frames;
- failures disappear under direct arithmetic controls and therefore reduce to generic probability arithmetic;
- P1 and P2 fail together, leaving no observation-model/integration distinction;
- the interesting effect appears only in the medical frame;
- the only remaining story is generic Bayes, generic evidence reliability, partial observability, RAG abstention, or belief-state tracking;
- a direct current owner of the locked computation is found.

## Mandatory re-selection trigger

After E01–E03, stop.

Before any agent/RAG/tool extension, write the observed one-line paper takeaway and compare it against the locked one. If RQ, estimand, mechanism, central claim, or reviewer compression has materially changed, perform a fresh novelty/data/identification/Main-level audit first.

**Evidence survives mutation; authorization does not.**