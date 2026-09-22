# E11 — Corrected EPO gate at L47 (validity repair, not a rescue)

**Frozen 2026-09-22, before any E11 run.** Supersedes the E09/E10 objective.

## Why this exists

E09/E10 did not reproduce the parent's EPO action mechanism. The E10 write-up
drew a conclusion from that ("the oracle yields no downstream gain") which has
been retracted. E11 repairs the gate. It is a validity repair: the thing that
was supposed to license 第四关 was not correctly executed, so 第四关 does not
run and no conclusion about non-final EPO stands until this is fixed.

## The correction that matters: `r-`

**Parent.** `r-` is the route the CURRENT router actually executes — its top-k.
Sample `G` alternative routes from the current router; let
`r* = argmin_r CE(r)`. **Emit a gradient only if `CE(r*) < CE(r-)`**; otherwise
the token is skipped. Then `r+ = r*`.

    Delta  = CE(r-) - CE(r+)                                  > 0 by construction
    margin = [logpi_theta(r+) - logpi_ref(r+)]
           - [logpi_theta(r-) - logpi_ref(r-)]
    loss   = -Delta * log sigmoid(beta * margin)

This is policy improvement from the deployed action: *you took this route, here
is a better one, move toward it.*

**What E09/E10 did instead.** `r+` = best sampled route, `r-` = **worst**
sampled route. That constrains only `best_sampled > worst_sampled`, a comparison
the deployed route need not participate in at all. A router can satisfy it by
rearranging the whole expert-score landscape without its own top-k ever becoming
the improved route — which fits 4/8 experts changed, preference accuracy
collapsing 0.550 → 0.505 while route value climbed, and greedy accuracy not
moving, far better than "counterfactual supervision has no value".

`logpi(S|x) = sum_{e in S} log p(e|x)` is **the parent's own definition** of
route log-probability. The E09/E10 docs calling it my surrogate were wrong.

## Recipe: stay near the parent

| | parent | E10 (wrong) | E11 |
|---|---|---|---|
| lr | 3e-4 | 1e-3 | **3e-4** |
| beta | 0.1 | 1.0 | **0.1** |
| batch | 16 | 1 | **16** |
| epochs | 1 | 4 | **1** |
| data | 2269 trajectories | 146 problems | **600 MATH-train problems** |
| hard tokens | dynamic, current CE > 0.1 | 6 permanently fixed per problem | **dynamic, current CE > 0.1** |

Dynamic token selection is why the expert bank is **not** cached this time: at
16KB per token (x, resid, target, base CE) a pool of tens of thousands of tokens
is affordable, and expert outputs are computed on demand from the loaded model.
Caching the bank would have forced a small, permanently fixed token set — which
is exactly the deviation being repaired.

## Metrics — three of ours, one of the parent's

Ours, kept because they are informative:

1. **Route value** `V = CE(base router's route) - CE(trained router's route)`,
   exact, paired bootstrap over held-out problems.
2. **Improved-route adoption**: the share of held-out tokens where the trained
   router's own top-k *is* the `r+` that was identified for that token. This is
   the most direct test of the mechanism and E09/E10 never measured it.
3. **Preference accuracy** on a fixed support from the reference router, with
   `r-` = the reference router's own top-k. Its floor is **structurally 0**, not
   0.5: the router's top-k maximises `sum log p` over k-subsets by construction,
   so at init `logpi(r+) < logpi(r-)` for every token. Rising off that floor is
   the router genuinely moving preference onto the better route. Reported with
   the floor stated, never as if 0.5 were the baseline.
4. **Experts changed per token**, as a rewriting-vs-surgery diagnostic.

The parent's, because ours cannot substitute for it:

5. **Sampled pass@K** on the 120 locked FG0 problems, T=0.6, top-p 0.95,
   n samples per problem, K = 1, 2, 4, 8, 16, (32). Base vs corrected, identical
   decoding. The parent never claims a greedy pass@1 gain — its headline is a
   pass@K shift it calls small and treats as a minimal existence check. Greedy
   accuracy 0.475 → 0.475 with 99.2% of completions changed says the
   distribution moved; one deterministic trajectory per problem cannot say which
   way it moved under sampling.

Greedy FG0 accuracy is still reported, now as a secondary.

Generation for pass@K runs in bf16 for both arms identically, stated here
because it differs from the fp32 used everywhere exactness is load-bearing.
pass@K uses the unbiased estimator `1 - C(n-c, k)/C(n, k)`.

## Pre-registered outcome rule

L47 is the cheap layer where the parent already showed the mechanism works, so
this is a reproduction check, not a discovery run. The four things that must
hold:

1. preference accuracy rises off its structural floor and does **not** collapse
   back during training the way E10's did;
2. experts changed per token stays well below the 4/8 wholesale rewriting E10
   produced;
3. held-out route value still improves;
4. sampled pass@K shows a shift in the parent's direction.

> **If a correct objective, a parent-ish recipe and a parent-ish metric still
> fail to reproduce at L47, stop.** That would establish that this harness does
> not reproduce parent actionability, and neither corrected L36 nor
> screened-EPO would have a basis to continue.

If L47 reproduces, run corrected L36 changing **only the layer**. If L36 then
shows route value rising with pass@K flat, that is the real negative result for
non-final counterfactual routing, and it can be stated as one.

No AIME/HMMT. Those stay a confirmatory set and are not spent on a gate.

## What E11 does not touch

E08 stands: the proxy screens full EPO-style Gumbel routes (R_2 = 0.938 / 0.976
at L36 / L44). The estimator is not under investigation here. The open question
is whether a **correct** EPO update turns exact route improvement into
downstream gain.
