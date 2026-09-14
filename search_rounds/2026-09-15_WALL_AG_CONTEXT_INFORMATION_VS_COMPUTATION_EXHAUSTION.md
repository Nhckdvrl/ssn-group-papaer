# WALL-AG — Longer context: more information or more computation?

Date: 2026-09-15
Status: EXHAUSTED / DIRECT PROGRAM EXISTS

## Mother question
Increasing a decoder transformer's context length changes two resources at once: it can add task-relevant information, but it also adds hidden-state slots and attention-mediated computational workspace. Are apparent long-context gains information gains or computational gains?

## Direct-owner audit
This distinction is already the core of the pause/filler-token program.

- ICLR 2024 *Think Before You Speak* explicitly motivates pause tokens as allowing a model to manipulate more hidden vectors before committing to an output, isolating extra computation from added semantic evidence.
- Pfau, Merrill & Bowman (2024), *Let's Think Dot by Dot*, uses semantically meaningless filler tokens to show transformers can solve algorithmic tasks they cannot solve without the extra tokens, and gives a computational-complexity characterization of when filler positions add expressive power.
- 2025–2026 follow-up work studies filler-token computation in frontier LMs and causally decodes/composes computations across otherwise content-free positions.

Thus the clean decisive intervention—hold semantic information fixed while adding token positions/computational workspace—already defines an active research program.

## Verdict
No L-series. Recasting filler/pause effects as a long-context information-vs-compute decomposition would be setting transfer.

## Anti-resurrection
No:
- filler tokens inside long-context benchmarks;
- 'same information, more tokens' as a new control;
- context length as hidden computational workspace without a genuinely distinct old theory;
- long-context gains attributed to compute by reusing pause-token logic.
