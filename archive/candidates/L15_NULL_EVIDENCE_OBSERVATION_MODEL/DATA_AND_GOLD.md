# L15 — Data and Gold Contract

**Date:** 2026-09-11  
**Status:** frozen for bounded pilot

## 1. Analytic gold

Let:

- `H`: target exists / hypothesis is true;
- `p = P(H)`: prior;
- `D`: detector/search returns a positive hit;
- `s = P(D|H)`: sensitivity / recall / detection probability when the target exists;
- `f = P(D|¬H)`: false-positive rate;
- `N = ¬D`: null observation.

Then:

`P(H|N) = p(1-s) / [p(1-s) + (1-p)(1-f)]`.

Gold is computed programmatically. No evaluated model supplies labels or judgments.

The first pilot uses `f=0` for the cleanest identification. A nonzero-false-positive robustness slice is allowed only after the primary result and may not rescue a null result.

## 2. Primary grid

- priors `p ∈ {0.2, 0.5, 0.8}`;
- sensitivities `s ∈ {0.05, 0.25, 0.50, 0.75, 0.95}`;
- identical visible outcome: **no detection**.

At `p=.5, f=0`:

| sensitivity | gold posterior after no detection |
|---:|---:|
| .05 | .4872 |
| .25 | .4286 |
| .50 | .3333 |
| .75 | .2000 |
| .95 | .0476 |

This creates a large normative dynamic range without changing the observed surface result.

## 3. Matched natural frames

Use at least four domains with the same parameterized structure:

1. camera / access monitoring;
2. database or document search;
3. diagnostic test;
4. system monitoring / logging.

Example:

> Before checking, there was a 50% chance Alice entered the building. If Alice entered, this camera records her 95% of the time. The camera produced no record of Alice. What is the probability Alice entered?

Avoid hidden domain priors: every required probability is explicit in the item.

The medical frame is a transfer condition, not the paper identity; prior diagnostic-Bayes work already exists.

## 4. Three matched probes

### P1 — observation-model competence

> Suppose `H` were true. What is the probability that the procedure would nevertheless return no detection?

Gold: `1-s` when `f` is irrelevant under `H`.

### P2 — posterior integration

> Given prior `p` and the no-detection result, what is `P(H|N)`?

Gold: analytic Bayes equation above.

### P3 — qualitative downstream decision

The item states an explicit threshold, e.g. continue investigating iff posterior `> .20`. This tests whether posterior mis-updating changes action without requiring an LLM judge.

P1/P2 are primary; P3 is secondary.

## 5. Load-bearing dissociation

Define:

- `Err_obs = |predicted P(N|H) - gold P(N|H)|`;
- `Err_post = |predicted P(H|N) - gold P(H|N)|`.

Pre-register **Known-but-Not-Integrated (KNI)** items as:

- `Err_obs ≤ .05`, and
- `Err_post ≥ .10`.

Primary KNI statistic:

`KNI rate = P(Err_post ≥ .10 | Err_obs ≤ .05)`.

A high KNI rate is the preferred signature because it separates observation-model knowledge from its use in belief updating.

## 6. Controls

Required controls:

- positive-detection counterpart;
- explicit Bayes arithmetic form with the same numbers;
- wording paraphrases for `no detection`;
- monotonic-order scoring independent of exact numeric calibration;
- prior-only baseline;
- matched item in which `P(N|H)` is explicitly handed to the model, testing integration after eliminating observation-likelihood computation.

The project dies if apparent failure is explained by generic arithmetic or probability-format errors.

## 7. Data-generation policy

Main pilot items are programmatic templates plus human review. LLMs may not generate the load-bearing data or gold.

Naturalness review checks only wording and whether all needed assumptions are explicit; it does not determine mathematical labels.

## 8. No post-hoc expansion

Do not add extra domains, model families, hidden-state probes, RAG agents, or complex POMDP environments to rescue a weak E01/E02 result.

Any new data regime that changes the central computation requires re-selection.