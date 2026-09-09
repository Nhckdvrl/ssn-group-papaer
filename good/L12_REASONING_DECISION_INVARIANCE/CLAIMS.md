# L12 Claim Ledger

**Updated:** 2026-09-09

## Current RQ

> Why does reasoning-oriented post-training make decisions dramatically more invariant to presentation, and does the self-generated long reasoning trajectory become the dominant causal controller of the final answer?

| ID | Claim | Role | Evidence | Status |
|---|---|---|---|---|
| **L12-C0** | Reasoning models are more invariant across risky-choice presentations. | Established parent, not ours | *Mind the (DH) Gap!* | Established prior |
| **L12-C1** | Think-SFT is more gain/loss- and order-consistent than sibling Instruct-SFT under the audited native-template protocol. | Behavioral substrate | L12-E01/E02 | **Supported on 3 parent prospects** |
| **L12-C2** | Frame identity remains recoverable through early/middle prompt representations after the behavioral transition. | Mechanism constraint | L12-E03 | **Supported diagnostically; not causal** |
| **L12-C3** | Complete natural Think-SFT reasoning trajectories strongly and causally control final A/B readout. | Mechanism substrate | L12-E05/E06 | **Supported; terminal-conclusion contribution unresolved** |
| **L12-C4** | Strong decision control survives removal of the terminal explicit choice/conclusion, indicating a trajectory-level takeover rather than mere final-sentence copying. | **Next load-bearing claim** | L12-E07 | **Not tested** |
| **L12-C5** | A trajectory-built pre-answer decision state causally mediates final choice and can transfer decision control under state substitution. | Main mechanism claim | L12-E08 | **Gated on C4** |

## Interpretation boundaries

- The 0.817 / 0.992 values are **frame-consistency**, not generic task accuracy.
- C2 does not imply frame information is causally used.
- C3 does not make generic trace causality novel; Thought Injection already establishes that traces can affect outputs.
- E06 weakens the cheap explanation that a short arithmetic snippet alone produces the E05 effect.
- C4 is intentionally one decisive experiment, not a control battery.
- If C4 fails, reconstruct around **late self-commitment** rather than adding rescue experiments.
- The semantic context-boundary scaffold is parked and is not part of the current C1→C2→C3 mainline.

## Training attribution

The public checkpoints are sibling branches from a common base. Current evidence supports a reasoning-oriented-vs-instruction-oriented branch contrast, not strict one-variable causal training attribution.
