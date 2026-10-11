# E01 interim read — epoch 1, one seed per arm

**Date:** 2026-09-13, ~04:42. **Status: NOT the estimand.** This is a go/no-go
read taken while the 12 matched runs were still training, to avoid committing
11 hours before knowing whether the effect is resolvable at all.

Each arm contributes a *different* training seed (P=0, D_rt=0, D_mask=1, S=2),
because the launcher interleaves arms across GPUs to avoid confounding arm with
device. So arm differences here are confounded with seed. No contrast below is
a valid estimate of `Delta_pair`, `Delta_wrong` or `Delta_corr`.

All four evaluations ran on fvcrc13 A100s, greedy, IFEval 541 prompts, official
verifier.

## Numbers

| arm | seed | strict prompt | strict instr | median chars | unique responses |
|---|---|---|---|---|---|
| P | 0 | 20.33 | 30.70 | 766 | 535/541 |
| D_mask | 1 | 19.41 | 29.26 | 808 | ~541/541 |
| D_rt | 0 | 16.27 | 25.42 | 502 | 536/541 |
| S | 2 | 10.54 | 22.18 | 63 | **5/541** |

| contrast | strict prompt | strict instr |
|---|---|---|
| `Delta_corr` P − S | +9.80 | +8.51 |
| `Delta_pair` P − D_mask | **+0.93** | **+1.44** |
| `Delta_wrong` D_mask − S | +8.87 | +7.08 |
| construct D_mask − D_rt | +3.14 | +3.84 |

## What this changes

**The D_mask arm earned its place.** Against the literature's own control
(D_rt), `P - D_rt` is +4.07 pp, which looks like a pairing surplus of roughly
the size An et al. report for IT−RT. But `D_mask - D_rt = +3.14 pp`, so most of
that gap is the RT *serialisation* — no prompt tokens, response starting at a
different absolute position — and not the correspondence. Against the
budget- and position-matched control, `Delta_pair` collapses to ~+0.9 pp.

Had E01 been run with the README's original three arms (D = RT), a ~3 pp
serialisation artifact would have been reported as pairing surplus.

**The S arm collapses; the D arms do not.** S emits 5 distinct strings across
541 prompts at a median of 63 characters, while D_mask — which has *no*
correspondence at all — writes 808-character varied responses. So the collapse
is not caused by the absence of correspondence. It is caused by training that
actively decorrelates the instruction from the response.

This is mathematically unsurprising: under `P_X (x) P_Y` the optimal conditional
is the response marginal, and greedy decoding from a marginal is degenerate. But
it means `Delta_corr` is partly measuring *collapse vs no collapse* rather than a
graded ability difference, and it must not be reported as a clean capability gap.

**Provisional pattern: `P ~ D_mask > S`** — the outcome-map cell where the
pretrained map plus marginal adaptation largely suffices and wrong pairing
damages it, i.e. correct pairing's role is preservation rather than teaching.

## What is not yet established

- `Delta_pair = +0.93 pp` is almost certainly inside seed noise with n=1 seed
  per arm and seeds not matched. **`P ~ D_mask` is not claimable yet**; under
  the frozen resolution rule this is exactly `HOLD — UNDER-RESOLVED` territory
  until the 3-seed runs land.
- Epoch 1 only (808 steps). An et al. train 10 epochs; longer training could
  grow `Delta_pair`.
- A hardware check worth recording: the same S adapter scored 10.91/21.46 on
  Blackwell and 10.54/22.18 on A100 under identical greedy decoding. That
  ~0.4–0.7 pp drift is the same order as the effect we need to resolve, which is
  why **all** evaluation was moved to one device class.

## Next

The 12 matched runs continue to epoch 3; every adapter is then evaluated on the
A100 nodes and summarised with prompt-clustered, seed-resampled intervals. The
decisive number is `Delta_pair` with a real CI. If it is tight around zero, the
paper's claim changes from "what pairing teaches" to "what pairing prevents",
which is a stronger and less intuitive claim — and, per the workflow, a claim
mutation that requires re-selection rather than a rewrite.
