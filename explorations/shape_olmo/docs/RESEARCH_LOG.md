# ShapeLab research log (running; newest at bottom)

## 2026-09-28 — state of understanding after P0 and the literature pass

1. The published token-level "hybrid signature" (Li & Merrill 2606.20936) comes from a 7B pair that differs
   in data mix, LR schedule, heads and long-context recipe, not only in the mixer. On our data the final
   Olmo-Hybrid is *worse* on 5/7 domains. The dominant axis is **novel vs reused target**: H better on novel
   (+0.018), worse on reuse, growing with n (−0.04 → −0.06). Content > function is mostly reuse
   composition.
2. "Attention wins on reused tokens" is Zoology's result (Arora et al., ICLR 2024: 82% of the gated-conv
   vs attention Pile gap is on AR hits). Not new.
3. A public **architecture-only triplet** exists: state-spaces Transformer++ / Mamba-2 / Mamba-2-Attention
   2.7B, same Pile data, 300B tokens, NeoX tokenizer, 2k context (Mamba-2 paper §9.2.3, Table 3). A second
   one at 8B / 3.5T: NVIDIA gpt3-8b-multi-3.5t-base / mamba2-8b-3t-4k / mamba2-hybrid-8b-3t-4k (Megatron
   format). The same Pile data also underlies Pythia (143 checkpoints, PolyPythias seeds), Mamba-1 and
   Mamba-2 size ladders: same-architecture **scale**, **training-progress** and **seed** controls.

## Hypothesis registered before any in-prefix-mass data (the reuse gate)

For every model, next-token loss splits exactly:
  nll = −log P(class) − log P(token | class),  class ∈ {IN: target type already in visible prefix, OUT}.
**H-gate:** the novel-vs-reuse architecture signature is mostly in the *gate*. Attention-rich models bet
more mass on in-prefix types (win on IN, lose on OUT); recurrent/hybrid models bet less.
Predictions if true:
  (a) On OUT targets, Δ_gate carries most of Δ (|Δ_gate| > |Δ_within|), with the same sign as Δ.
  (b) Mean P(IN | OUT target) is higher for the attention-rich model.
  (c) Same-architecture scale/progress changes move gate and within-class terms together; an
      architecture swap moves them in opposite directions.
**H-within (alternative):** the gap sits within class: which novel token (semantic / state, Li & Merrill)
and which in-context token (retrieval precision, Zoology). Then (a) fails.
Either outcome is informative. Noise floor for any profile claim: token-level differences between
PolyPythias seeds of the same size.

## Queue (blocked: all fvcrc cards held by other users' jobs; 11 / 21 unreachable)
- T7s1 / H7s1 (OLMo stage-1 end) with lpin/lpout → stage change-point + gate on the OLMo pair.
- Pile triplet 2.7B (T++ / Mamba-2 / Mamba-2-Attn) + Mamba-2 1.3B + Pythia-1.4B/2.8B (+ steps 36k, 71k)
  on 2k NeoX windows, with lpin/lpout.
