# L12 Claim Ledger

**Updated:** 2026-09-09

## Current RQ

> Why does reasoning-oriented post-training make decisions invariant to presentation, and is that transition accompanied by a shift in causal control from the prompt to a self-generated reasoning trajectory and its pre-answer decision state?

## Major claim chain

| ID | Claim | Evidence | Current status |
|---|---|---|---|
| **L12-C0** | Reasoning models are more invariant across risky-choice presentations. | *Mind the (DH) Gap!* | **Established prior; not ours** |
| **L12-C1** | Decision-controlling information is distributed through the natural reasoning trajectory rather than reducible to its terminal explicit commitment. | E07 | **Supported on 3 parent prospects** |
| **L12-C2** | Long reasoning constructs a pre-answer decision state that causally carries trajectory control into final decoding. | E08 | **Supported on 3 parent prospects** |
| **L12-C3** | The sibling-branch invariance transition is accompanied by a reorganization of causal control: the same stripped trajectories control Think-SFT much more strongly than Instruct-SFT, while prompt-frame control is small once trajectory content is fixed. | E09 + E10 + E02 | **Supported across 36 independent decisions** |
| **L12-C4** | The same causal-control reorganization persists over a documented later checkpoint/training axis. | E12 | **Open; DPO weights unavailable locally** |

## Supporting evidence, not headline claims

| ID | Result | Role |
|---|---|---|
| **L12-S1** | Think-SFT frame consistency is 0.992 versus 0.817 for sibling Instruct-SFT. | Reproduces the behavioral substrate on the three parent prospects. |
| **L12-S2** | Frame identity remains linearly recoverable through early/middle prompt representations. | Rules against a simple information-erasure story; probe evidence is not causal use. |
| **L12-S3** | Full own/opposite trajectories produce margins +9.34/-9.07, while short arithmetic snippets do not reproduce that effect. | Routes the mechanism toward the natural trajectory rather than a generic calculation fragment. |

## Interpretation discipline

- E07 supports **distributed control plus terminal amplification**, not the stronger statement that the terminal commitment is irrelevant. Stripping retains a +2.62 margin effect over empty, while the terminal portion adds +7.05.
- E08 supports a coherent decision-state profile: transfer is negligible through layer 13, rises at 14-16, reverses the mean target margin at layer 17, and remains strong thereafter. The paper claim is not that one layer is the mechanism.
- E09 is the mechanism-phenomenon bridge. Its scientific object is branch-specific prompt-versus-trajectory control, not merely an injected-text effect.
- The released OLMo checkpoints are sibling branches from a common base. They support a training-regime-associated contrast, not strict attribution to one isolated optimization step.
- E10 uses 36 independent base decisions and E11 uses a preregistered 18-decision stratified subset. Repeated traces and layers remain within-unit observations.
- The exploratory decision-level association between the behavioral branch difference and control difference is unsupported (rho = -0.203, p = 0.243). Do not claim monotonic per-item coupling; the supported bridge is the matched branch-level reorganization replicated across units.

## Current verdict

**GO.** C1-C3 now form a coherent causal explanation with independent-decision breadth. The remaining paper-strengthening gap is C4 checkpoint/model breadth, not the core mechanism.
