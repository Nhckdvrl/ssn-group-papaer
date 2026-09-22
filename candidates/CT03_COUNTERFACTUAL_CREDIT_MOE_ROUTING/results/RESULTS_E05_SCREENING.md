# CT03 E05 — the estimator's real operational role: candidate screening

**Run:** 2026-09-22, zero GPU. Reuses exact/proxy grids already collected on the
same tokens and the same pairs: Qwen L28/36/44 (`e036_proxy` ×
`c0_eval_base_pairs`) and OLMoE L1–L15 (`e037_olmoe_*`). `src/e05_screening.py`.

## Why this exists after the kill

CT03 was killed because `credit -> router policy` failed. That failure was
established against **two action mechanisms we invented ourselves** — binary CCD
and CPD. The parent's own action mechanism, EPO, was never tried with our
estimator. EPO samples equal-compute alternative routes, evaluates them with
**exact** downstream CE, and runs a reference-anchored, CE-gap-weighted
preference update; the parent validated it end-to-end on Qwen3-30B-A3B at L47.

So `A_delta ~ 0` falsifies **CPD's distillation mechanism**. It does not falsify
"counterfactual preferences can train a router" — the parent is a counterexample.
The untested question is the plainest one CT03 ever asked:

> can the cheap estimator replace EPO's expensive exact search — not by
> replacing the labels, but by **screening which candidates get exactly
> evaluated at all**?

This is the job the fidelity numbers actually support (ranking, recall), rather
than the job CPD asked of them (generalising a privileged gold-gradient signal
into a global linear router).

## Result: retained oracle gain when only the proxy's top-m are exactly evaluated

Mean over tokens that have a beneficial swap; 1.0 = the full 32-candidate oracle.

**Qwen3-30B-A3B**

| layer | m=1 | m=2 | **m=4** | m=8 | m=16 |
|---|---|---|---|---|---|
| L44 | 0.932 | 0.948 | **0.962** | 0.996 | 0.996 |
| L36 | 0.820 | 0.870 | **0.937** | 0.988 | 0.992 |
| L28 | 0.641 | 0.754 | 0.830 | 0.908 | 0.975 |

**OLMoE-1B-7B**

| layer | m=1 | m=2 | **m=4** | m=8 | m=16 |
|---|---|---|---|---|---|
| L15 (94%) | 0.933 | 0.941 | 0.948 | 0.980 | 0.983 |
| L13 (81%) | 0.883 | 0.920 | 0.947 | 0.988 | 0.992 |
| L10 (63%) | 0.824 | 0.877 | 0.906 | 0.979 | 0.996 |
| L7 (44%) | 0.737 | 0.820 | 0.897 | 0.974 | 0.994 |
| L4 (25%) | 0.552 | 0.657 | 0.770 | 0.890 | 0.951 |
| L1 (6%) | 0.376 | 0.494 | 0.612 | 0.764 | 0.890 |

`m = 4` costs **1/8 of the exact reruns**; `m = 8` costs 1/4.

The pre-set bar was: top-4 retaining 90%+ makes screening solid, 50% means drop
it. **Qwen L36/L44 pass (0.937, 0.962); L28 does not (0.830)** — consistent with
it having been the calibration-boundary layer throughout. OLMoE reproduces the
same depth structure: L7 and deeper pass at m=4, L1/L4 fail. Shallow layers are
not screenable, which is the operational consequence of the finite-step
estimation error E01.5 and E03.7 already localised.

## Why this is structurally unlike CPD

- the estimator only does what its measured fidelity supports — ranking and
  recall — not cross-problem generalisation into router weights;
- the **labels stay exact**, so the attribution disaster that killed CPD ("is
  the gain from counterfactual content?") cannot arise by construction;
- the action mechanism is the parent's validated one, not a new invention.

## What this does NOT establish, and the honest cost of the next step

It does **not** reopen CT03. Screening only matters if counterfactual
supervision works at non-final layers at all, and that has never been tested:
the parent trained L47 only, and our own two attempts used different objectives.
Compressing final-layer EPO alone would be "EPO but cheaper" — the parent reports
roughly 5h of router-only EPO on 2×A6000, which is not a prohibitive cost to
attack.

The gate that would have to pass first, at real GPU cost, is:

> **exact** counterfactual labels at L36/L44 + the parent's **validated** EPO
> objective — does a non-final router absorb it?

If it does not, CT03 is dead for good, and this screening curve is simply an
archived property of the estimator. If it does, screening is what makes
multi-layer counterfactual supervision affordable, and that is the paper the
project originally proposed.

**Status unchanged:** CT03 remains KILLED (`CT-KILL-20260922-1`). This file is
recorded as a property of the estimator, not as a resurrection.
