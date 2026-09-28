# CT03 CPD v1 — trust-region calibration (ladder)

**Run:** 2026-09-21, Qwen3-30B-A3B fp32, 12 calibration trajectories = 192 tokens
at L36/L44. Training-free. `src/cpd_v1.py` (`--steps 0`), `results/cpd_calib.json`.

## Rule (frozen in code before the run)

> smallest `delta` whose top-8 change fraction is in **[0.15, 0.35]** on **both**
> layers, with mean experts changed per token **<= 1.0**.

The bounds encode C0's lesson: wholesale rerouting (3–5 of 8 experts) is the
generic-perturbation regime that produced a credit-independent effect there. CPD
should look like a small, directed correction. The script exits with an error if
no rung qualifies, rather than falling back to a default.

## Result: `delta = 0.002`

| delta | layer | beta | changed_frac | mean_chg | chg given chg |
|---|---|---|---|---|---|
| 0.001 | L36 | 1.0088 | 0.146 ✗ | 0.146 | 1.00 |
| 0.001 | L44 | 0.7424 | 0.104 ✗ | 0.104 | 1.00 |
| **0.002** | **L36** | **1.4172** | **0.240** ✓ | **0.281** ✓ | 1.17 |
| **0.002** | **L44** | **1.0514** | **0.156** ✓ | **0.167** ✓ | 1.07 |
| 0.003 | L36 | 1.7313 | 0.292 | 0.385 | 1.32 |
| 0.006 | L36 | 2.4719 | 0.396 ✗ | 0.562 | 1.42 |
| 0.01 | L36 | 3.1861 | 0.458 ✗ | 0.677 | 1.48 |
| 0.05 | L36 | 7.3935 | 0.750 | 1.844 | 2.46 |
| 0.2 | L36 | 17.1292 | 0.906 | 3.438 | 3.79 |

`delta = 0.002` is the first rung where both layers enter the window; at 0.001
both fall below it. About a quarter of tokens change route, and when they do they
change **~1.1 experts** — the intended regime.

## Two things this run corrected

**The grid was wrong, not the rule.** The first ladder used `{0.01 … 0.2}` and
*no* rung qualified: even its smallest rung already had L36 at 0.458. The grid
was an arbitrary guess with nothing guaranteeing it covered this router's trust
region; the rule was left untouched and the grid extended downward. An
extrapolation from the first table predicted `delta ≈ 0.006`, which the real
measurement refutes (L36 = 0.396 there) — which is why the decision was left to
the rule rather than to the estimate.

**The failure had to be made inspectable.** The first version raised its error
*before* writing the report, destroying the very data the rule exists to expose.
The ladder is now persisted first.

## A fact worth keeping

The same KL budget buys very different behavioural change at the two layers —
0.240 vs 0.156 at `delta = 0.002`, and 0.906 vs 0.854 even at 0.2. L36 is
consistently easier to move. So **equal KL is not equal intervention strength
across layers**, which is the same shape as E02's finding that the calibration
onset is model-specific. Nothing is changed on account of it here; if CPD works,
it is real evidence about how a layer-wise trust region should be set.
