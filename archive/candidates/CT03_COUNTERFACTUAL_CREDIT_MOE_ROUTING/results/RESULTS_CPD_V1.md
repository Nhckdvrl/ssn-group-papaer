# CT03 CPD v1 — free-generation result

**Run:** 2026-09-21, `fvcrc20:0,1`, Qwen3-30B-A3B fp32 · three arms × 400 steps on
600 MATH-train problems · greedy free generation on the **120 locked FG0
problems**, never trained on, disjoint from MATH-500.
**Design:** `docs/CPD_V1_DESIGN.md` (frozen, amended 2026-09-21 before training).

## Verdict: outcome **D** of the pre-registered tree

> *CPD helps free generation but Router-CE helps equally* → the novelty burden
> moves to sample efficiency / generalisation / route quality, and stronger
> baselines (EPO, RoMA) are required.

| arm | acc | vs base | same_as_base | first_div | KL(shared) | ovl L36 | ovl L44 |
|---|---|---|---|---|---|---|---|
| base | 0.475 | — | 1.000 | 412.2 | 0 | 1.000 | 1.000 |
| router_ce | 0.517 | +0.042 | 0.000 | 23.6 | 3.48e−2 | 0.698 | 0.578 |
| shuffled | 0.500 | +0.025 | 0.083 | 112.5 | 2.24e−3 | 0.803 | 0.667 |
| **cpd** | **0.533** | **+0.058** | 0.008 | 38.8 | 1.68e−2 | 0.735 | 0.615 |

Paired bootstrap, 10k resamples, on the same 120 problems:

| contrast | diff | 95% CI | |
|---|---|---|---|
| cpd − base | **+0.0583** | [+0.0167, +0.1083] | **significant** |
| cpd − shuffled | +0.0333 | [−0.0083, +0.0833] | not significant |
| cpd − router_ce | +0.0167 | [−0.0333, +0.0667] | not significant |

## What this does and does not establish

**Does:** CPD produces a statistically significant gain in *real free
generation* over the base model, on problems never trained on, with ordinary
Top-K inference and no test-time overhead. This is the first time in CT03 that
the chain reaches an end-task outcome rather than a teacher-forced proxy.

**Does not:** show that the counterfactual *content* is what produced it.
Shuffled-CPD also gains +2.5 and Router-CE gains +4.2; neither contrast
separates. The credit-specific claim is unsupported at this scale.

## A gap in the control that this run exposed

The three arms are **not equal-strength interventions after training**, even
though the per-token training targets were exactly KL-matched (max residual
2.4e−7, verified at every step):

- router_ce moved furthest (route overlap 0.698/0.578, shared-prefix KL 3.5e−2,
  first divergence at token 23.6);
- shuffled moved least (0.803/0.667, KL 2.2e−3, first divergence at 112.5);
- cpd sits between them.

Shuffled's realised shared-prefix KL is an **order of magnitude** below CPD's. So
"cpd − shuffled = +3.3, not significant" is confounded: it could be content, it
could be that the shuffled router simply ended up in a weaker place. The design
matched the *target* KL per token; it did not match the *resulting* policy
displacement. That is a real hole in the control, stated rather than explained
away, and any follow-up must close it — e.g. by matching realised route overlap
or realised shared-prefix KL, or by training shuffled longer to the same
displacement.

## Training summary

| arm | steps | loss | drift L36 / L44 |
|---|---|---|---|
| cpd | 400 | 0.0262 → 0.0244 | 0.092 / 0.136 |
| shuffled | 400 | 0.0201 → 0.0142 | 0.073 / 0.115 |
| router_ce | 400 | 1.4047 → 1.2275 | 0.109 / 0.161 |

CPD's own loss is essentially flat across training while shuffled's falls
further. The two losses are different functions (different targets at matched
KL), so the values are not directly comparable — unlike C0, where both arms
optimised the identical functional form and the comparison was meaningful. No
inference is drawn from it.

Router-CE's ordinary CE falls by 0.177 nats, confirming that router-only
post-training is a genuinely strong baseline — which is why it was in the design
(RoMA, ICLR 2026, already owns "router-only post-training helps").

## Next, per the D branch

Not more loss variants. The open question is whether counterfactual credit buys
anything *over* ordinary router adaptation:

1. close the realised-strength gap in the shuffled control;
2. sample efficiency — does CPD reach Router-CE's gain in fewer trajectories?
3. route quality on fixed support (`V_route`, `A_fixed`) — CPD learns the
   potential explicitly, so if `A_fixed` does not move, the mechanism claim
   fails regardless of accuracy;
4. only then, stronger baselines (EPO, RoMA) and a second model family.

Item 3 is the cheapest and the most diagnostic, and the fixed-support instrument
from E03.1 already exists.
