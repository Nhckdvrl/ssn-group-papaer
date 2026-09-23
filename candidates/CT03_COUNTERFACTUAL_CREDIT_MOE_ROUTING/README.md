# CT03 — Counterfactual Credit for MoE Routing

**Status:** ❌ **KILLED / CLOSED — 2026-09-23** · **Opened:** 2026-09-20
**Kill record:** `chasing trends/topics/FAILED_TOPICS.md` (`CT-KILL-20260922-1`)
**Final scientific archive:** `FINAL_POSTMORTEM.md`

> Killed as a Main-level **method** topic. The estimator survived every test it
> was given; the step from credit to router policy never closed. Two distillation
> formulations failed to establish credit-specific improvement, and ordinary
> router-only CE adaptation matched or beat CPD on route quality. **Do not reopen
> with a nonlinear router, on-policy/actionable credit, a second-order estimator,
> more data, a second model family, or EPO/RoMA baselines** — those grow branches
> around a claim whose centre has no supporting evidence.
>
> **What stands** (independent of the method, reusable): the cheap estimator and
> its cross-family validity, the depth-calibration curve, the interaction-vs-
> estimation decomposition, and the finding that a one-off reroute is
> decision-local but not state-persistent.
>
> **What failed:** `credit -> router policy -> deployed action`. CPD did not
> establish a credit-specific effect; exact EPO moved route metrics without
> downstream gain; final frozen-target probes showed preference success can be
> strongly decoupled from actual Top-K adoption. See `FINAL_POSTMORTEM.md`.
>
> **2026-09-23 update — the kill is now more thorough, not less.** The
> narrow reopening (cheap screening for the parent's exact EPO) is also closed:
> E11 shows the objective those labels feed can be driven to 94.7% preference
> accuracy while the router's executed Top-8 moves *away* from the preferred
> route, with 80.8% of executed experts in neither route. Making exact labels
> cheaper only buys a cheaper way to optimise an objective that does not command
> the deployed decision. See `results/RESULTS_E11_CORRECTED_L47.md`.
>
> E08's screening result stands as an asset (32 exact reruns -> 2, retaining
> 94-98% of oracle gain); it is about proxy ranking of exact utilities and is
> untouched by any of this. The phenomenon E11 uncovered is registered
> separately as **CT04**, not as a CT03 rescue:
> `../CT04_ROUTE_PREFERENCE_DECISION_CONSISTENCY/SELECTION.md`.
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
| **CPD v1** | does distilled credit beat controls? | **no credit-specific gain established** — controls matched/exceeded it |

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


## Final closure

CT03 is closed. E08–E10 and the final frozen-target probes were post-kill audits, not a revival. Their final role is diagnostic: the estimator/screening side survives, but the information-to-action chain does not. In the strongest frozen-target probe, parent-style preference training reached high preference accuracy while the executed Top-8 moved largely outside both compared routes; the canonical interpretation, caveats, and anti-resurrection rules are in `FINAL_POSTMORTEM.md`.

**Do not run further CT03 GPU experiments or convert the route-preference mismatch into a new numbered topic without a separate question-formation and novelty audit.**
