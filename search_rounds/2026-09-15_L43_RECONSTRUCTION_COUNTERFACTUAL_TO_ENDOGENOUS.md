# L43 Reconstruction — Counterfactual Alternatives vs Endogenous Route Selection

**Date:** 2026-09-15  
**Decision:** keep L43, but supersede the original phenomenon-trigger E01 with `E01R`.

## Why reconstruction was necessary

The original formulation asked whether published IOI backup name movers wake up on DoubleIO / TripleIO without internal ablation.

That experiment had an undesirable gamble structure: a negative result could always be dismissed as `the chosen stressor did not trigger the backup`, leaving the mother question unresolved.

During re-audit, several strong 2026 papers also made the broader space clearer:

- CoAx: counterfactual backup discovery after primary ablation — https://arxiv.org/abs/2607.01940
- ICLR 2026 intervention divergence: causal interventions can create divergent states and activate dormant pathways — https://proceedings.iclr.cc/paper_files/paper/2026/hash/133e588e1429f9f1e25b215da145580e-Abstract-Conference.html
- The Curse of Multiple Mediators: prompt-dependent mediator effects and hidden interactions — https://arxiv.org/abs/2606.27510
- All Circuits Lead to Rome: multiple low-overlap faithful circuits can support the same behavior — https://arxiv.org/abs/2605.12671
- Many Circuits, One Mechanism: input-conditioned structural circuit differences can be phantom specialization — https://arxiv.org/abs/2606.06267
- Adaptive Circuit Behavior: IOI reuses components across DoubleIO / TripleIO and can exhibit knockout-only mechanisms — https://arxiv.org/abs/2411.16105
- Circuit Stability Characterizes LM Generalization — https://aclanthology.org/2025.acl-long.442/

These papers do **not** kill L43 when treated correctly. Their intersection exposes a missing quantity.

## Reconstructed mother question

> **When an intervention reveals an alternative circuit that can substitute for a primary route, does that alternative predict which route becomes causally load-bearing across intact input variation?**

Short form:

> **Does counterfactual substitutability predict endogenous substitution?**

This is a distinct scientific statement from all parents:

- `alternative circuits exist` does not imply the intact model switches among them;
- `circuits differ across inputs` does not imply different underlying mechanisms;
- `an intervention activates a backup` does not imply the backup is naturally used;
- `interventions can diverge` does not tell us whether a specific intervention-defined alternative corresponds to natural computation.

No exact owner was found in the audit.

## Why the intersection is a contribution rather than a three-paper mash-up

The parents define two axes that have not been connected:

1. **counterfactual axis:** which routes become useful when we perturb the network;
2. **endogenous axis:** which routes become useful when the intact input changes.

L43 asks for the transfer relation between these axes.

The paper identity is therefore not `apply method A to setting B`. It is a new question about what intervention-based mechanistic evidence means.

## E01R correction

Old E01:

> chosen stress family -> does backup wake up?

New E01R:

> measure natural primary-route engagement continuously across a fixed published input-variation family -> estimate whether CoAx counterfactual scores predict endogenous recruitment across all non-primary heads -> causally validate the top-CoAx group.

The primary head-level quantity is a rank relation between:

- `C_h`: CoAx counterfactual substitutability;
- `E_h`: within-semantic increase in intact correct-answer contribution as the primary route becomes less engaged.

A group-level matched-control ablation then tests whether the top-CoAx set becomes selectively more necessary on naturally low-primary inputs.

## Why this is exploratory

Three resolved outcomes are all scientifically useful:

- positive mapping -> interventions expose a naturally used reserve repertoire;
- precise zero -> counterfactual alternatives are reachable capacities, not predictors of intact route scheduling;
- negative / different-route mapping -> natural adaptation and intervention repair recruit systematically different mechanisms.

The only failed pilot is insufficient variation / statistical resolution.

## Current status

> **L43 — `PILOT-AUTHORIZED — E01R ONLY; NOT MAINLINE`.**

Canonical files:

- `candidates/L43_NATURAL_BACKUP_ROBUSTNESS/SELECTION.md`
- `candidates/L43_NATURAL_BACKUP_ROBUSTNESS/E01_PREREGISTRATION.md`

The directory name is legacy; the reconstructed scientific object supersedes the earlier `natural backup robustness` title.
