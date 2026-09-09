# L12 Claim Ledger

**Updated:** 2026-09-09

## Current RQ

When reasoning-oriented post-training makes fact-equivalent presentations behaviorally invariant, does the model learn which variation is semantically irrelevant, or does contextual information more broadly lose causal control over decisions?

| ID | Claim | Role | Evidence | Status |
|---|---|---|---|---|
| **L12-C0** | Reasoning models are more invariant across risky-choice presentations. | Established parent, not ours | Mind the (DH) Gap! | Established prior |
| **L12-C1** | Think-SFT is more gain/loss- and order-invariant than sibling Instruct-SFT under the audited native-template protocol. | Behavioral gate | L12-E01/E02 | **Supported on 3 parent prospects** |
| **L12-C2** | Frame identity remains recoverable through early/middle prompt representations after behavioral invariance emerges. | Diagnostic routing | L12-E03 | **Supported diagnostically; not causal** |
| **L12-C3** | Complete natural reasoning trajectories causally control the Think-SFT final choice readout. | Mechanism component | L12-E05/E06 | **Supported with content-specificity limitation** |
| **L12-C4** | Reasoning-induced invariance reflects selective semantic abstraction, causal disengagement/context flattening, deliberative reconstruction, or another discriminable transformation. | Core scientific question | L12-E07/E08 | **Unresolved** |
| **L12-C5** | The reasoning-oriented branch treats meaning-preserving and decision-changing context differently in a way that explains its behavioral invariance. | Boundary / paper-identity claim | L12-E07 then E08 | **Not tested** |

## Interpretation boundaries

- C2 does **not** imply frame information is causally used.
- C3 does **not** make generic thought/trace causality novel.
- E04 (`</think>`) is invalid evidence.
- E06 weakens a simple arithmetic-snippet explanation.
- C4/C5 must not be reduced to a particular layer or patching method.

## Training attribution

The public checkpoints are sibling branches from a common OLMo base and use native templates. Current evidence supports a reasoning-oriented-vs-instruction-oriented branch contrast, not strict one-variable causal training attribution.
