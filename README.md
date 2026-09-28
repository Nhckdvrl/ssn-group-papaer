# SSN Group Paper — Current Research State

**Last reset:** 2026-09-28  
**This README is the only global source of truth for current authorization.**

The repository has accumulated many historical candidates, pilots, search rounds, and failed lineages. Directory names such as `candidates/` or `good/`, and old status text inside historical packages, **do not authorize current work**.

## Current state

| track / object | current status | meaning |
|---|---|---|
| Global paper mainline | **NONE** | no project is currently approved as a paper mainline |
| `ssn-taste/` | **SEARCH / TERRITORY MODE; selected = 0** | Sasano-taste search has no current candidate |
| `chasing trends/` | **TERRITORY MODE; selected = 0** | hybrid-adaptation work is a territory, not a candidate |
| `AI4Quant/` | **TERRITORY MODE; selected = 0** | the two former "selected" ideas are hypotheses/territories until an empirical observation earns promotion |
| `observations/ROUTE_PREFERENCE_DECISION_CONSISTENCY.md` | **OBSERVATION** | strong empirical result; not yet an independent paper candidate |
| `explorations/shape_olmo/` | **PAUSED EXPLORATION / KNOWLEDGE ASSET** | useful empirical knowledge, no registered RQ |
| `failed/` | **HISTORICAL ANTI-RESURRECTION** | durable kill evidence only |
| `candidates/`, `good/` | **HISTORICAL EXECUTION PACKAGES** | retained for reproducibility; not current authorization |

## The research process

The repository no longer treats a paper-shaped question as the default unit of search.

> **TERRITORY → STRONG BASELINE → EXPLORATION → STABLE OBSERVATION → CANDIDATE → CONFIRMATION → MECHANISM / METHOD → PAPER**

### 1. Territory

A territory is a scientific object worth learning deeply: a model family, training process, failure surface, architecture, or mature scientific problem.

At this stage it is normal to:
- read lineages and code;
- reproduce strong baselines;
- inspect checkpoints and failure slices;
- run exploratory ablations;
- change hypotheses freely.

At this stage do **not** create a paper title, candidate ID, mother question, "both outcomes are interesting" story, or Main-level growth plan.

The only investment question is:

> Are we becoming materially more knowledgeable about this object?

### 2. Observation

An observation is a concrete pattern we have actually seen.

Before it can support a candidate, require:
- it is not a one-off point;
- it survives a fresh seed, natural subset, or matched setting when feasible;
- a simple baseline / parser / prompt / generic-capability explanation does not already account for it;
- the observation is stated independently of the hoped-for paper story.

An investment threshold is not the same as a scientific null. Record both separately.

### 3. Candidate

A candidate is earned only when a stable observation or independently strong empirical pressure forces a worthwhile scientific question.

A candidate must have:
- an important belief or assumption that the observation changes;
- a nearest-prior boundary that is not merely a new model/dataset/cell;
- a feasible confirmation experiment with enough resolution;
- a natural path to a substantial contribution without rescuing the story after each result.

Only here should the repository create a candidate ID and freeze a claim.

### 4. Mechanism / method

For method-shaped work, never infer a method from a successful diagnostic.

Require the full chain:

> **Failure → Bottleneck → Controllable action → Downstream outcome**

Each arrow needs independent evidence. CT03 is the canonical warning: a high-quality counterfactual routing signal did not imply that the supervision objective controlled the Top-K decision actually executed.

## Discovery vs confirmation

**Discovery** is allowed to be exploratory. Look at curves, slices, stages, failure gradients, simple explanations, and counterexamples.

**Confirmation** begins only after a claim exists. Then freeze the metric, held-out set, controls, stopping rule, and statistical test.

Do not use a preregistered continuation threshold to decide whether an empirical effect "exists"; use it only to decide whether the project deserves more investment.

## Failure-derived rules that survive the cleanup

1. **Conceptual distinction is not empirical pressure.** `A ≠ B` is not a paper until a real system forces the distinction.
2. **Prior A + Prior B is usually not a new parent question.** Most historical kills were ownership/crowding failures.
3. **Gold must equal the claimed estimand.** A high-quality label can still measure the wrong quantity.
4. **Simple controls come before elaborate interpretation.** Object-specific failures often collapse to generic capability or evaluator failures.
5. **Training phenomena must be stable enough to be scientific objects.** If reasonable budget/family/recipe changes rewrite the explanation, avoid turning one trajectory into a law.
6. **Mother phenomenon and identifying intervention must coexist in the same feasible regime.**
7. **Synthetic tasks diagnose; they should not simultaneously create the phenomenon, define the construct, provide the gold, and justify the interpretation.**
8. **A healthy project gets simpler as evidence accumulates.** If every repair adds another conditional branch, stop.
9. **Cheap E01 is an efficiency property, not a topic-quality criterion.**
10. **Failure should accumulate expertise, not only anti-resurrection entries.**

## Reading order for future agents

1. Read this file.
2. Before broad web search, check `library/README.md` → `TERRITORY_BANK.md` → relevant anchor papers/blogs.
3. Enter exactly one track and read that track's `README.md` and canonical guide, if present.
4. Read the relevant experiment/territory/observation package.
5. Consult `failed/` or track-specific failed ledgers only for targeted anti-resurrection.

Do **not** start by trawling historical candidate directories or old search scratch.

## Repository policy

- No new `search_rounds/`-style process dumps.
- No duplicate "current state" documents.
- No candidate ID before candidate status is actually earned.
- A claim mutation does not inherit authorization: if the scientific identity changes, return to Observation / Candidate evaluation before more compute.
- Historical raw results, code, tests, and reproducibility assets are preserved.
- If current status conflicts with an old package, **this README wins**.
