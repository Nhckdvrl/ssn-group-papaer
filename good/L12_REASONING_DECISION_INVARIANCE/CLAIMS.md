# L12 Claim Ledger

**Updated:** 2026-09-09

## Current RQ

When reasoning-oriented SFT makes equivalent risky choices behaviorally invariant, are the presentations internally canonicalized, or does frame information survive while its influence on choice is overridden?

## Claims

| ID | Claim | Role | Nearest owner | Evidence | Status |
|---|---|---|---|---|---|
| L12-C0 | Reasoning models are more invariant across risky-choice presentations. | Established parent, not ours | Ge et al. (2026) | Parent paper/data | Established prior |
| L12-C1 | Think-SFT is more gain/loss- and order-invariant than its sibling Instruct-SFT under a matched direct-choice protocol. | Behavioral gate | Ge et al. report the parent behavior | L12-E01/E02 | Supported on the three published prospects; direct difference CI excludes zero |
| L12-C2 | Frame identity remains recoverable at prompt end after behavioral invariance emerges. | Diagnostic routing claim | Framing Matters and general probing work | L12-E03 | Early/middle-layer recovery is strong; final-layer result equals its small-sample null threshold |
| L12-C3 | The complete generated trajectory causally controls the Think-SFT final choice readout. | Mechanism component | General thought-injection work owns trace causality, not this decision transition | L12-E05/E06 | Natural trace effect supported; answer-free arithmetic-content account not identified |
| L12-C4 | Reasoning-induced invariance is primarily static canonicalization, policy override, or inference-time deliberation. | Load-bearing account distinction | No current paper owns the full branch-to-decision chain | L12-E02-E05 plus next boundary/intervention | Deliberation strengthened; A versus B remains unresolved |

L12-C2 is explicitly not a mechanism claim. L12-C3 concerns trajectory-to-readout causality, not the causal use of the original frame representation. E06 prevents attributing E05 to arithmetic content alone. The failed end-of-think intervention cannot identify either claim.

## Checkpoint Identification

The public branches are siblings from `allenai/Olmo-3-1025-7B`:

- `allenai/Olmo-3-7B-Instruct-SFT`
- `allenai/Olmo-3-7B-Think-SFT`

The ACL paper appendix contains a sentence claiming Instruct-SFT was initialized from Think-SFT. Official model cards contradict it and list the common base. This project uses base-to-branch deltas and does not repeat the sequential-transition claim.
