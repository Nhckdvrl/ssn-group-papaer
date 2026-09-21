# CT03 — Counterfactual Credit for MoE Routing

**Status:** `CPD v1 training in progress` (2026-09-21) · **Opened:** 2026-09-20
**Topic authority:** `chasing trends/topics/CT03_COUNTERFACTUAL_CREDIT_MOE_ROUTING.md`

## The object

A sparse MoE router only ever receives task-loss feedback through the experts it
actually executed. Nearby unexecuted experts get no token-level task signal. The
parent diagnostic (*When Are Experts Misrouted?*) shows a better equal-compute
route often already exists inside the frozen model on fragile reasoning tokens,
and buys that knowledge by **executing** sampled alternative routes.

CT03 asks whether the same signal can be had for almost nothing, and then turned
into a better router:

```
u_hat_ij = -grad_h L^T (h^{i->j} - h)      cheap credit, one shared backward
z_hat    = Project(u_hat)                  router-representable expert potential
q*       ∝ p_0 exp(beta z_hat)             conservative policy improvement
```

Inference stays ordinary Top-K.

## Where it stands

| stage | question | outcome |
|---|---|---|
| **E01** | is the local estimate faithful? | **yes** — rho 0.698 overall; router's own score ~0. `RESULTS.md` |
| **E01.5** | why is it weak in shallow layers? | tail dispersion at full swap, not curvature. `RESULTS_E015.md` |
| **E02** | does it survive a second family? | **yes** on Qwen3-30B-A3B, incl. renormalised routing; onset is model-specific. `RESULTS_E02.md` |
| **C0** | can binary pairwise credit train a router? | **largely no** — margin-collapse shortcut; metric B invalid. `RESULTS_E03_C0.md` |
| **E03.1** | on fixed support, what really happened? | no utility alignment; route gain real but tail-driven. `RESULTS_E031.md` |
| **E03.5/.6/.7** | can a scalar router even represent the utility? | **yes** (R² .87–.999); shallow limit is estimation, not interaction. `RESULTS_E035.md`, `RESULTS_E036_E037.md` |
| **FG0.1** | does a one-off reroute change free generation? | decision-local, TV .043, **no persistence** — motivates distilling into the router. `RESULTS_FG0.md` |
| **CPD v1** | does distilled credit beat controls? | **running** — `docs/CPD_V1_DESIGN.md` |

## Method state

Trained: `gate` matrices at **L36 and L44** of Qwen3-30B-A3B (524k params);
everything else frozen. L28 excluded (potential fidelity 0.703, at the
estimator's calibration boundary); L47 excluded (the parent already owns
final-layer adaptation).

Target is **exactly mass-preserving** on `U = S ∪ C`: gauge-invariant in `z`,
experts outside `U` stay at their base probability, and `sum_U q* = sum_U p_0`
exactly — so no gain can come from inflating candidate mass or flattening the
router. Trust region `beta_l` is set per layer so the median `KL(q*||p_0)` hits
one global budget `delta`, chosen by a training-free ladder under a rule frozen
in code (`delta = 0.002`; 24%/16% of tokens change route, ~1.1 experts each).

Three arms, identical data/order/token selection/optimiser/steps:
**Router-CE**, **KL-constrained Shuffled-CPD**, **CPD**.

## Layout

```
docs/     E01_DESIGN, E015_DESIGN, E02_STAGEB_DESIGN, E03_C0_DESIGN (+amendment),
          E035/E031 notes, FG0_DESIGN, CPD_V1_DESIGN   -- all frozen before their run
src/      e01_*  estimator validity + cost
          e015_* alpha sweep;  e02_*  cross-family;  e03*  C0 training + repaired eval
          e035/e036/e037  integrability, proxy-vs-exact potential, gap decomposition
          fg0_*  free-generation causal branch;  cpd_*  CPD v1;  run_cpd_v1.sh driver
results/  RESULTS*.md per stage, reports, locked pools, router checkpoints
```

## Reproduction

```
PY=/home/xiang/miniconda3/envs/verl-clean/bin/python
CUDA_VISIBLE_DEVICES=0,1 bash src/run_cpd_v1.sh     # ladder -> smoke -> 3 arms -> free-gen
$PY src/cpd_report.py ladder|train|freegen
```

float32 sharded over 2 cards throughout. bf16 is rejected deliberately: deep-layer
exact effects reach 1e-4 and bf16 can round two near-identical routes to the same
value, producing `dL = 0` silently.

## Data hygiene

- Training: 600 MATH **train** problems (`results/cpd_trainpool.json`).
- Free-generation dev: 120 locked problems (`results/fg0_devpool.json`), disjoint
  from both, never trained on.
- **MATH-500 is no longer untouched** — C0 drew its pool and held-out set from it
  and E03.1/.5/.6 metrics were developed on it. It stays reportable only as
  development-influenced evaluation. AIME/HMMT remain locked and untouched.

## Standing requirements (earned, not stylistic)

Every one of these exists because something went wrong without it:

- the **shuffled-label/potential control is permanent** — in C0 it was the only
  thing that stopped "route regret fell, the method works", which was wrong;
- **fixed support** for any before/after mechanistic metric — C0's A/B/D
  compared different tokens around different routes;
- **medians and win-rates beside every mean** — E03.1's effect is tail-driven and
  the mean alone overstated every cell;
- **per-problem values kept** for paired bootstrap intervals;
- validity checks run *before* headline numbers — they have caught a CE off-by-one,
  a frozen-parameter no-graph backward, a baseline on a different numeric path,
  and three device-placement bugs on the sharded model.
