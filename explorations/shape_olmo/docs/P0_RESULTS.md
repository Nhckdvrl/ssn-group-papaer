# P0 — token-level T vs H on the final 7B pair (2026-09-28)

Models: `Olmo-3-1025-7B` main (a81bae42, scored with transformers 4.57.6) vs `Olmo-Hybrid-7B` main
(4f1cc566, transformers 5.12.1, fla kernels). 7 domains, ~0.6–1.1M tokens each, 8192-token packed
windows (`results/data_manifest.json`). Δ = NLL_T − NLL_H (> 0: hybrid better). CIs are
window-cluster bootstrap. Raw output: `results/p0_T7_H7.txt`, `.json`.

## Pipeline checks before reading any number
- Olmo-3 under transformers 5.x: NLL rises with position (1.99 → 5.23 nats/token, first vs last
  512) because YaRN is applied to the sliding layers. Scored with 4.57.6 instead (see
  `logs/P0_LAUNCH.md`).
- Hybrid: no position blow-up. The scorer equals plain `forward()`. Padded-vocab mass ~1e-7.
  fla kernels and the torch path give identical NLL.
- The tagger is noisy (Brown n-gram backoff; unknown words → NN).

## Result
| domain | Δ | 95% CI |
|---|---|---|
| pg19 | +0.052 | [+0.048, +0.055] |
| ccnews | −0.062 | [−0.075, −0.050] |
| wikipedia | −0.050 | [−0.064, −0.036] |
| arxiv | +0.005 | [−0.011, +0.018] |
| python | −0.082 | [−0.107, −0.059] |
| html | −0.041 | [−0.054, −0.029] |
| latex | −0.043 | [−0.066, −0.022] |

- Reproduces (ordering): content +0.007 > function −0.016 (paper 0.038 > 0.024). Open − close
  gap positive in 5/7 domains (pg19 +0.097, ccnews +0.057, python +0.039, latex +0.053; wikipedia
  −0.062).
- Does **not** reproduce (level): on 5/7 domains the hybrid has *higher* NLL.
- **Reuse carries the deficit.** Non-repeated targets (rep = 0): Δ = +0.018 [+0.011, +0.025].
  Repeated n-gram targets: Δ = −0.042 (n≥1) … −0.050 (n≥5) … −0.060 (n≥16), monotone. The paper
  reports the advantage "approaching zero" on repeats; here it turns clearly negative.
- **No SWA-window effect.** Δ is ≈ 0 for positions 0–1k and ≈ −0.03 beyond 1k, **flat across
  4096** ([1024, 4096): −0.033; [4096, 8191): −0.032). T's local-window truncation does not
  show up.

## Open explanations for the level discrepancy (not yet tested)
1. **Long-context stage:** the final hybrid uses DroPE (no positional encoding in attention); the
   final T uses YaRN. Losing positional information plausibly weakens induction / copying.
   → Test: stage-1-end pair (both RoPE, downloading).
2. **Data mix:** the hybrid's stage-1 data is the Olmo 3 32B mix; the eval domains may favour one
   mix.
3. **Their inference stack** is unspecified (HF version, OLMo-core); the Olmo-3 YaRN trap shows
   how much it can matter.
4. Our eval data differs (sources and repetitiveness), but the rep = 0 / rep ≥ n split holds
   within domains pooled; to check per domain.
