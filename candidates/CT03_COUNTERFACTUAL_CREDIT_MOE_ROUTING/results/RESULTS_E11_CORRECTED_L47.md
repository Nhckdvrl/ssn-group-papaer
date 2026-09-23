# E11 — the corrected EPO gate at L47

Design frozen in `docs/E11_DESIGN.md` before the run. Parent's `r⁻` (the route
the current router actually executes), parent's skip rule (`CE(r*) < CE(r⁻)`),
parent's recipe (lr 3e-4, β 0.1, batch 16, 1 epoch), parent's dynamic hard-token
rule (current CE > 0.1). 600 MATH-train problems × 96 uniformly sampled solution
tokens = 52,508 tokens; 478 problems train / 120 held out, disjoint, FG0 held
apart. L47 so that a patch changes CE at that position only.

**Pre-registered outcome rule: if a correct objective with a parent-ish recipe
and a parent-ish metric fails to reproduce at L47, stop.** It failed. What
follows is why, which is more than the rule asked for.

## The primary reading

`ov` — how many of `r⁺`'s 8 experts the router actually executes after training —
is the metric E09/E10 never had. Its baseline is 3.77/8, because `r⁺` is a
Gumbel sample from the router's own pool and already shares most of the top-8.

| run | objective | pref_acc | adopt | **ov** (from 3.77) | changed | ‖ΔW‖/‖W₀‖ |
|---|---|---|---|---|---|---|
| online, lr 3e-4 | pref | 0.572 | 0.000 | ~1.8 | 7.04 | 0.419 |
| online, lr 3e-5 | pref | 0.423 | 0.000 | 1.80 | 5.93 | 0.113 |
| online, lr 3e-5 | sft | 0.179 | 0.000 | 1.98 | 5.88 | 0.177 |
| **fixed targets** | **pref** | **0.947** | **0.000** | **1.05** | **7.71** | 0.659 |
| **fixed targets** | **rank (oracle)** | 0.726 | 0.101 | **5.45** | 3.41 | 2.387 |
| matched-norm noise @0.42 | — | 0.000 | 0.000 | 3.68 | 1.39 | 0.420 |

Route value rises in every trained arm (+0.15 to +0.17, CI clear of zero), and
it is the one number that does. Its median is **negative** (−1e-4) and its win
rate (0.29) barely clears the 0.237 floor that pure fp noise produces at W = W₀.
The mean is a heavy tail.

## The mechanism

Read the last two rows together. They use the same frozen targets and differ
only in what is optimised.

- The **parent's preference objective is essentially perfectly satisfiable**:
  pref_acc 0.947. And at that optimum the router's executed route has moved
  **maximally away** from `r⁺` — 7.71 of 8 experts changed, ov down to 1.05.
- The **rank oracle**, which optimises the top-k condition directly, raises ov
  3.77 → 5.45 and adoption 0 → 0.101, still climbing at epoch 12.

So a linear gate *can* be moved toward `r⁺`. Capacity is not the obstacle. The
obstacle is that

    logπ(S | x) = Σ_{e∈S} log p(e | x)

compares two *fixed* 8-subsets and says nothing about which subset is on top.
Ranking `r⁺` above `r⁻` is a set comparison; executing `r⁺` is an argmax
condition. The cheapest way to satisfy the first is to crush `r⁻`'s experts —
and since 120 other experts are waiting underneath, the top-8 relocates to
experts in **neither** set. Hence pref_acc → 0.947 with ov → 1.05.

This also explains E09/E10 without appeal to "the oracle signal has no
downstream value": route value up, preference accuracy up, adoption never, and
generation changed everywhere while accuracy stayed flat.

## Controls, and two explanations of mine that they killed

1. **Matched-norm random perturbation.** Two arms with 4× different drift landed
   at the same changed≈5.9, which looked like diffusion. It is not: a random ΔW
   at ratio 0.42 gives changed 1.39 and leaves ov at 3.68. The trained move is
   directed, 4–15× larger, and aimed away from `r⁺`.
2. **SFT control** (no `r⁻` term at all) behaves the same. This **killed** my
   first explanation, that the gradient simply rides the degenerate "push `r⁻`
   down" direction.
3. **Router peakedness.** I predicted the −K·logsumexp term flips the sign for
   confident experts (p > 1/K). Measured against the cache: the net coefficient
   1 − K·p_e is positive at every rank, +0.070 at rank 1, and only 31.5% of
   tokens have top-1 > 1/8. **Wrong, not written up.**
4. **Train vs test.** Superimposed throughout (final ov 1.89 vs 1.86), so none
   of this is a generalisation gap.
5. **Moving target.** Freezing the targets does not rescue it — the fixed-target
   pref row is the worst ov of all.

## What this does not say

The parent reports gains. This says their objective, as specified, is
satisfiable without adoption at L47 on this model — not that their result is
wrong. Their scale, their all-layer training, or a recipe detail may keep the
degenerate direction off the path. Settling that needs their code, not more
runs here.

`pass@K` was **not** run. With 5.8/8 experts changed it could only have measured
how badly this particular run damaged the router, at a cost of hours; the
mechanism probes above cost ten minutes each and answer the actual question.
AIME/HMMT untouched.

## Status

E08's screening result (`R_2` ≥ 0.94 at L36, 0.976 at L44) stands and is
independent of all of this — it is a statement about proxy ranking of exact
utilities, not about any training objective. The EPO training line stops here,
per the pre-registered rule.
