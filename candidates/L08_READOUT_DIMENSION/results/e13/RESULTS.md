# E13 — self-state refresh: the load-bearing experiment  `2026-09-14`

Reproduce: `$PY scripts/analyze_e13.py`.

## Result

```
Delta_refresh = [Y_T(state) - Y_T(placebo)] - [Y_0(state) - Y_0(placebo)]
              = +0.0000   [-0.102, +0.102]      quant:4, n = 112 shared items
```

| arm | n | state | placebo | state - placebo | 95% CI |
|---|---|---|---|---|---|
| full precision | 101 | 0.7723 | 0.7723 | **+0.0000** | [-0.050, +0.050] |
| quant 4-bit | 112 | 0.2946 | 0.2768 | **+0.0179** | [-0.045, +0.080] |
| readout keep=0.75 | **3** | — | — | — | not estimable |

Instrument check: the null-injection arm scores 0.3214, above both injected arms.
Injecting anything at all costs ~0.03-0.04 regardless of the number, symmetrically
across arms, so the contrast is unaffected.

## Verdict: the preregistered kill rule fires

`E13_PREREGISTRATION.md` §7: *if, on at least one parameter-locus compression plus the
readout anchor, `Delta_refresh` is not significantly positive, the mechanistic Main
route is KILLED.*

`Delta_refresh` is not significantly positive. **The mechanistic Main route is killed.**

## The readout anchor could not be tested at all

Self-state refresh requires the model to have produced the correct intermediate state
itself. Eligible trajectories with enough correct calculator annotations and remaining
downstream computation:

| intervention | eligible / 500 |
|---|---|
| full precision | 101 (20%) |
| quant 4-bit | 112 (22%) |
| **prune 40%** | **11 (2%)** |
| **readout keep=0.75** | **3 (0.6%)** |
| **readout keep=0.5** | **0 (0%)** |

The readout-locus interventions destroy exactly the structured intermediate states the
design needs. Weakening the truncation to keep 75% of dimensions did not recover them.
The kill rule's "parameter compression **plus** readout anchor" could therefore only be
evaluated on the parameter half, and that half is null.

## Why the null is informative rather than merely underpowered

For the same model and the same items, the two interventions differ by more than an
order of magnitude:

| manipulation | effect on quant 4-bit |
|---|---|
| replace the whole prefix with the correct trajectory (E12 reference clamp) | **+0.2595** [0.191, 0.326] |
| re-emit the one already-correct state the next step consumes | **+0.0179** [-0.045, 0.080] |

So the mediation is **not** the model losing track of a state it had already computed.
It is that the compressed model writes a wrong chain and the wrong chain produces a
wrong answer. That is ordinary error propagation, with a model perturbation in place of
sampling noise as the trigger.

**Power, stated honestly.** The CI half-width on `Delta_refresh` is ~0.10, so effects
above ~0.10 are excluded and smaller ones are not. n = 112 is what the eligibility
criterion yields on 500 items; reaching n ~ 500 would need ~2200 items per cell. That
is a reasonable thing to want and it does not change the verdict, because the mechanism
being tested predicted a rescue comparable to the clamp's +0.26, not one below 0.10.

## What this leaves

| claim | status |
|---|---|
| C1 protocol effect | OWNED (Wen et al.; Song et al.) |
| C2a trajectory mediation | **SUPPORTED**, but the instrument is owned (Exposure Bias vs Self-Recovery, EMNLP 2021) and the residual is null |
| C2b state re-grounding | **REJECTED** |
| C3 consequence | depends on C2b; not reachable |

No quantity separates this work from the exposure-bias literature or from RAC/AYOT,
which own both the phenomenon and a fix for it. **Main-level novelty is gone.**
