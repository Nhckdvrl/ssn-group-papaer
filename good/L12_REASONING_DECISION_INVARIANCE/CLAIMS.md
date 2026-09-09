# L12 Claim Ledger

**Updated:** 2026-09-09

## Current RQ

> Why does reasoning-oriented post-training make decisions dramatically more invariant to presentation, and does the self-generated long reasoning trajectory take over causal control of the final answer?

| ID | Claim | Role | Evidence | Status |
|---|---|---|---|---|
| **L12-C0** | Reasoning models are more invariant across risky-choice presentations. | Established parent, not ours | *Mind the (DH) Gap!* | Established prior |
| **L12-C1** | Think-SFT is more gain/loss- and order-consistent than sibling Instruct-SFT under the audited native-template protocol. | Behavioral substrate | E01/E02 | **Supported on 3 parent prospects** |
| **L12-C2** | Frame identity remains recoverable through early/middle prompt representations after the behavioral transition. | Mechanism constraint | E03 | **Supported diagnostically; not causal** |
| **L12-C3** | Complete natural Think-SFT reasoning trajectories strongly and causally control final A/B readout; short answer-free arithmetic snippets do not reproduce the effect. | Mechanism substrate | E05/E06 | **Supported** |
| **L12-C4** | Decision control survives removal of the terminal explicit choice/conclusion, indicating distributed trajectory takeover rather than only late self-commitment. | **Next load-bearing claim** | E07 | **Not tested** |
| **L12-C5** | A trajectory-built pre-answer hidden state causally transfers decision control under matched state substitution. | Main mechanism claim | E08 | **Gated on C4** |

## Interpretation discipline

- 0.817 / 0.992 are **frame-consistency**, not generic accuracy.
- C2 rules against simple erasure language; decodability alone does not prove causal use.
- C3 is not by itself novel: generic CoT/trace causality is already occupied.
- C4 asks whether the causal controller is distributed through the natural trajectory or concentrated in the final self-commitment.
- C5 asks whether the trajectory has built an internal state that directly carries decision control.
- If C4 fails, reconstruct around late self-commitment rather than adding defensive experiments.

## Training attribution

The released OLMo checkpoints are sibling branches from a common base. Current evidence supports a reasoning-oriented-vs-instruction-oriented branch contrast, not strict one-variable causal attribution to a single training operation.
