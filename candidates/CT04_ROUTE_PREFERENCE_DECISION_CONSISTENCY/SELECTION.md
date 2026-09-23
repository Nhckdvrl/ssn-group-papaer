# CT04 — Are route-preference objectives decision-consistent with the Top-K a sparse MoE actually executes?

**Status:** `PILOT-AUTHORIZED — GATES 1-3 ONLY; NOT MAINLINE`
**Date:** 2026-09-23
**Predecessor:** `CT03_COUNTERFACTUAL_CREDIT_MOE_ROUTING` — **stays KILLED**, and
the evidence below makes its revival less warranted, not more.
**Parent:** arXiv 2605.07260, spec verified verbatim in
`../CT03_COUNTERFACTUAL_CREDIT_MOE_ROUTING/docs/PARENT_EPO_VERIFIED.md`.

## RQ

> **When counterfactual route preferences supervise a pretrained MoE router,
> does satisfying the preference objective make the router execute the preferred
> route?**

One sentence of phenomenon:

> **A router can satisfy 94.7% of exact counterfactual route preferences while
> moving its executed Top-8 farther from the preferred route than before
> training — and 80.8% of the experts it ends up executing belong to neither the
> preferred nor the rejected route.**

## Why the mother question changed

CT03 asked *can counterfactual routing credit be estimated cheaply* — answered
yes, repeatedly, and killed because `credit → router policy` never closed. CT04
asks a different question that the E11 data forced open: not whether the labels
are cheap or correct, but whether **the objective that consumes them targets the
decision the model actually makes.** The supervision here is exact, not
estimated; cheapness is not part of the claim.

This matters for CT03's disposition. E08's screening result (32 exact reruns →
2, retaining 94-98% of oracle gain) is a real asset and stays, but it cannot be
a paper's centre any more: making exact labels cheaper only buys a cheaper way
to optimise an objective that does not command the deployed decision. CT03 is
**more** dead than before, not less.

## The evidence in hand (from E11, all committed)

Same frozen targets, same linear gate, same data; only the objective differs.

| objective | pref_acc | **ov** (base 3.77/8) | adopt | ‖ΔW‖/‖W₀‖ |
|---|---|---|---|---|
| parent preference | **0.947** | **1.05** | 0.000 | 0.659 |
| execution-aligned (Top-K margin) | 0.726 | **5.45** ↑ | 0.101 | 2.387 |

Composition of every executed expert slot after training (zero-GPU
decomposition, `src/e11_decompose.py`):

| gate | in r⁺ only | in r⁻ only | both | **NEITHER** |
|---|---|---|---|---|
| W₀ | 0.000 | 0.528 | 0.472 | **0.000** |
| parent preference, lr 3e-4 | 0.081 | 0.064 | 0.047 | **0.808** |

The textbook counterexample — `z(r⁺)=5, z(r⁻)=4, z(outside)=10` — is not
hypothetical here. It is what the trained router does.

Controls already run and committed: matched-norm random perturbation (the move
is directed, 4-15× larger than noise, and aimed away from r⁺); positive-only SFT
(kills the "it only suppresses r⁻" story); router-peakedness audit (**my
prediction, measured wrong, not used**); train/test superposition (no
generalisation gap); frozen targets (not a moving-target artifact).

## Three corrections to how this must be stated

1. **The execution-aligned objective is not an oracle.** It uses only `r⁺` — the
   same supervision EPO consumes — and no `Δ`, no `r⁻`. An earlier comment in
   `e11_epo.py` called it an oracle probe; that was wrong and is fixed. It is a
   deployable alternative objective, which makes the contrast a *method*
   contrast rather than a capacity probe.
2. **It does not "recover adoption."** ov 3.77 → 5.45 is a large move toward
   `r⁺`, but exact adoption reaches only 0.101 and the gate drifts 2.39× its own
   norm. Any comparison must be **drift-matched**, or the two arms are not
   comparable. This is Gate 2's first requirement.
3. **The headline 0.947 comes from the frozen-target probe**, 12 epochs — not
   from the parent's own online recipe, where pref_acc reached 0.572 in one
   epoch. The phenomenon appears in both, but the number quoted must carry its
   regime.

## Nearest prior — verified, not assumed

Checked on 2026-09-23, because two topics in this repo have died on nearest
prior.

- **Yang & Koyejo, ICML 2020, *On the Consistency of Top-k Surrogate Losses***
  (https://proceedings.mlr.press/v119/yang20f.html). Defines top-k calibration
  as necessary and sufficient for consistency and shows **hinge-like top-k
  surrogates are not top-k calibrated**. So "surrogate ranking ≠ Top-K decision"
  is old, and — importantly — this bears on our *fix*: the execution-aligned
  loss in `e11_epo.py` is a hinge. Gate 1 must not present it as principled
  until that is confronted.
- **Cai et al., ACL Findings 2025, KPO** (https://aclanthology.org/2025.findings-acl.250/,
  arXiv 2506.00441). Extends DPO's Plackett-Luce to top-K rankings, motivated by
  exactly the observation that ordinary preference objectives do not target the
  top-K a user sees. Closest methodological neighbour.
- **Kool et al., ICML 2019, Gumbel-Top-k / Plackett-Luce**: Gumbel-top-k is
  sampling without replacement, so `Π_{e∈S} p_e` is *not* the law of the sampled
  route. The parent states openly that the factorized form is a chosen
  surrogate, so this is a calibration question about their surrogate, **not an
  error in their paper**, and must never be written as one.

**Therefore the claim is NOT** "we discovered Top-K surrogate inconsistency."
**It is**: counterfactual preference optimization of a pretrained MoE router can
optimise its stated preference while anti-optimising the executed expert set,
which explains why better route supervision need not become better routing. No
located work covers that object.

## Gates

**Gate 1 — nail the object. Near-zero GPU.**
Separate the three quantities: factorized subset score, the true Gumbel-Top-K /
Plackett-Luce law, and the deterministic Top-K execution condition
`min_{e∈r⁺} z_e > max_{j∉r⁺} z_j`. Give the minimal counterexample, and pair it
with the measured decomposition above. Confront the Yang & Koyejo result about
hinge surrogates.

**Gate 2 — matched objective comparison, drift-matched.**
Same frozen `r⁺`, same init, same gate; parent preference vs positive-only vs
execution-aligned, compared at **equal ‖ΔW‖**, not equal epochs. Headline is
`pref_acc / ov / adoption / realized exact route utility` — never training loss.
Mostly built; the drift matching is the missing piece.

**Gate 3 — one replication, and one only.**
A second MoE with different routing cardinality (GPT-OSS-20B overlaps the
parent; OLMoE is already validated in this repo as cross-family). Question:
Qwen 128/8 accident, or general to combinatorial routing objectives?
**If Gate 3 fails, KILL CT04 immediately. Do not repair it.**

**Gate 4 — downstream, only if 1-3 pass.**
parent EPO vs execution-aligned, on realized route utility first and generation
second. AIME/HMMT pass@K is final validation, **not** the live-or-die criterion,
and is not touched before then. Reason: E11 shows a preference objective can
change generation wholesale *without* executing the supervised route, so a
benchmark delta obtained now has an attribution problem by construction.

## Standing prohibition

The failure that killed CT03 was assuming a clean first half implies the second
half. The phenomenon here is clean. That is not evidence that the fix works.
Gate 2 and Gate 3 exist to stop exactly that inference.
