# CT03 FG0 — Does teacher-forced counterfactual utility have free-generation consequence?

**Status:** FROZEN 2026-09-20, before any run. Nothing is trained.
**Target:** amendment kill-bar condition 3, the only one with no instrument.

---

## 1. The existential risk being tested

Every CT03 number so far — E01, E01.5, E02, C0, E03.1/.5/.6/.7 — is defined on
**teacher-forced gold trajectories**. The utility `u_ij = -ΔL(i→j)` is a change
in the loss of reproducing a gold continuation that the model did not write.

If routing choices that look better under teacher forcing do not help the model's
**own free continuation**, then the entire training target is a gold-path
artefact and no amount of CPD engineering can rescue it. That is a larger risk
than any loss-function choice, and it is testable now, without v1.

## 2. Why a causal branch, not a correlation

The tempting cheap version — "does a problem's aggregate route headroom predict
its solve rate?" — is confounded by difficulty, solution length and gold CE, and
would not license a causal reading. Worse, once generation diverges from the gold
path there is no position correspondence to correlate against.

FG0.1 therefore intervenes exactly once and then lets the model run:

```
fix gold prefix y_<=t ,  do( route at (layer l, position t) = r ) ,
then restore ordinary routing and free-generate to the end
```

measuring `P(correct final answer | gold prefix, do(route))`. Everything after
`t` uses the unmodified router, so any difference is attributable to that single
routing decision.

## 3. Arms

- **BASE** — the model's own top-8 at `t`.
- **PROXY-BEST** — the equal-compute one-swap maximising `û_ij`, i.e. the choice
  CT03's cheap credit would actually make.
- **EXACT-BEST** — the one-swap maximising the exact `-ΔL`, on a subset. This is
  the oracle ceiling and the one that decides the kill bar: if *exact* better
  routing does not help free generation, the object itself is the problem, not
  our estimator.

## 4. Token selection — and the control that keeps it honest

Selecting only high-headroom tokens would produce a selection-conditioned
result. Each problem contributes **two** positions:

- one **high** proxy-headroom token;
- one **matched low**-headroom token, matched on relative position within the
  solution and on base CE.

Both restricted to the first 70% of the solution, so the intervention is not
sitting on the answer itself.

The informative quantity is the **difference of treatment effects**:

```
Δ_high = P(correct | PROXY-BEST, high) - P(correct | BASE, high)
Δ_low  = P(correct | PROXY-BEST, low)  - P(correct | BASE, low)
```

A real consequential-decision story predicts `Δ_high > Δ_low ≈ 0`. A uniform
shift across both is far weaker evidence and probably a generic perturbation
effect — the same lesson the shuffled-label control taught in C0.

## 5. Layer

Qwen3-30B-A3B **L44** first (potential fidelity ρ = 0.979, the layer where the
credit is most trustworthy). If the signal exists anywhere it should exist here;
if it does not exist at L44, testing L36 first would only have been slower. L36
is added only if L44 shows an effect.

## 6. Outcomes

Primary: **final-answer correctness** by boxed-answer extraction and normalised
string match. Single-token interventions give a sparse outcome signal, so also
recorded, as diagnostics that cannot substitute for it:

- short-horizon gold logprob after the intervention;
- whether and where the continuation diverges from BASE;
- paired solve rate over seeds where sampling is used.

Improving gold likelihood while not improving free continuation is a **negative**
result, not a partial success.

## 7. Data — locked, and disjoint from everything downstream

`EleutherAI/hendrycks_math` **train** split. MATH-500 is drawn from the MATH
*test* split, so the pools are disjoint by construction; problem text is
additionally deduplicated against MATH-500. The selected problem ids are written
to `results/fg0_devpool.json` before the first run and **never enter CPD
training**. AIME/HMMT are not touched.

Note for the record: MATH-500 can no longer be described as untouched. C0 drew
its training pool and its 16 held-out problems from it, and the metrics and
controls of E03.1/.5/.6 were developed on it. It remains reportable as a
development-influenced evaluation; the locked confirmatory sets are AIME/HMMT.

## 8. Numerics

The outcome is a discrete correctness bit, so generation may run in bf16. The
**proxy ranking** must not silently degrade with it: before the main run, the
bf16 argmax over the 32 candidates is compared against the fp32 argmax on a
subsample, and the agreement rate is reported. EXACT-BEST requires fp32 replay
and is run separately on its subset.

## 9. Pre-registered reading

- `Δ_high > Δ_low`, with EXACT-BEST ≥ PROXY-BEST: the counterfactual object has
  genuine generation consequence, and CPD is worth training.
- `Δ_high ≈ Δ_low ≈ 0` **while EXACT-BEST also does nothing**: kill-bar
  condition 3 fires. The object is a teacher-forcing artefact. Do not respond by
  adding metrics.
- EXACT-BEST helps but PROXY-BEST does not: the object is real and the estimator
  is too weak at this operating point — an estimator problem, not an object
  problem.
- Uniform improvement on both high and low: suspect a generic perturbation
  effect and test it as such before claiming anything.
