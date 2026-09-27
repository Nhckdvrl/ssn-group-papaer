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

## 2026-09-28 — Pile architecture-only triplet results (`results/pile_profiles_all.txt`, `results/pile_placebo_gate.txt`)

Models (same Pile data, NeoX tokenizer, 2k windows, 7 domains): PPT = Transformer++ 2.7B, PPH =
Mamba-2-Attention 2.7B (hybrid), PPR = Mamba-2 2.7B. Controls: Pythia 1.4B→2.8B (scale), Pythia-2.8B
step71000→final (training), Mamba-2 1.3B→2.7B (scale). (PY28_36k was invalid, see P0_LAUNCH; re-queued.)

**1. Three-way.** All-token gaps: T−H +0.027, R−H +0.038, T−R −0.012.
- Novel targets (rep 0): T−H +0.053, R−H +0.055, T−R −0.001. **T ≈ R on novel targets; H beats both
  by ≈ 0.05.**
- Reused targets: R worse than T (rep ≥ 2: −0.015; content|rep ≥ 1: −0.044), H ≈ slightly better than T.
- So H > max(T, R) holds, and it is concentrated on novel targets, where neither parent has an
  advantage over the other.

**2. The H−T token profile has the shape of a generic improvement.** Profile / all-token gap:

| | T→H (arch) | Pythia 1.4→2.8B | Pythia 71k→final | Mamba-2 1.3→2.7B |
|---|---|---|---|---|
| novel | 1.99 | 2.02 | 2.01 | 2.03 |
| rep 1 | 1.00 | 1.01 | 1.00 | 1.02 |
| rep ≥ 2 | 0.32 | 0.29 | 0.30 | 0.27 |
| rep ≥ 4 | 0.13 | 0.13 | 0.12 | 0.13 |
| content|rep0 | 2.16 | 2.38 | 2.30 | 2.33 |
| function|rep0 | 1.17 | 0.98 | 1.00 | 1.13 |

On an architecture-only comparison, "novel > repeat → 0, content > function" is what any lower-loss
model shows (scale, training progress, architecture). **It cannot be read as a recurrent / state
signature.** The OLMo stage-1 pair has the same shape (novel / all ≈ 2.1). The only architecture
contrast whose profile is *not* generic-shaped is **T vs R** (novel ≈ 0, reuse negative), i.e. the
known Zoology recall gap. Brackets are relatively larger in T→H (open 0.90, close 1.09 of all) than in
the controls (0.5–0.7); a small, unexplained deviation.

**3. Pre-registered reuse gate: H-gate rejected, H-within supported.** Novel targets, T→H: Δ = +0.053
= gate +0.0025 + within +0.051 (every domain: gate ≤ 0.005). IN targets: +0.016 = +0.004 + +0.013.
Gate calibration is nearly identical across models (mean P(IN) 0.711 vs 0.712, reliability near
diagonal). Pythia scale: novel +0.181 = gate +0.008 + within +0.173. The architecture gap is about
*which* token, not about betting on the prefix, and in that respect it again looks like scale.

**4. The token-level placebo regression is uninformative.** corr(d_HT, d_TT) = +0.02 at token level
(per-token noise dominates), so α ≈ 0.02 and the residual ≈ the raw gap. The informative placebo is
the profile-shape comparison (2). A seed noise floor (PolyPythias) is still to be computed at GPU
scale; the CPU pilots cover only 60 windows.

**What this changes.** Per-token *type* profiles do not discriminate architectures: they measure
"how much better", not "better at what". What survives and is architecture-specific:
(i) the T vs R recall gap (old, Zoology);
(ii) the aggregate super-additivity H > max(T, R) on novel targets (≈ +0.05 with T ≈ R);
(iii) on OLMo, a reuse / closure / code degradation produced during the hybrid's DroPE long-context
stage (P0_RESULTS, stage ladder).
None is named or registered. The next question has to use a tool other than token-type profiles,
e.g. counterfactual context interventions on the same targets.
