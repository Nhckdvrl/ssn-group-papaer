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

## Exploratory cuts (same scores; `results/p0_explore_T7_H7.txt`, `results/p0_srcdist_T7_H7.txt`)

**Content > function is mostly reuse composition.** 92% of function-word tokens are reuses
(rep ≥ 1) vs 57% of content tokens. Within strata:

| stratum | content | function |
|---|---|---|
| rep = 0 | +0.036 [+0.027, +0.044] | −0.010 [−0.020, +0.001] (n = 98k) |
| rep = 1 | −0.010 | −0.008 |
| rep ≥ 2 | −0.021 | −0.028 |

The paper's own controlled aggregate effect (Fig. 2, bottom right) is also within ±0.002 nats.
The raw content/function contrast should not be read as an open-class / state effect.

**Novel vs reused target is the dominant axis.** At every difficulty bin, rep = 0 favours H (up to
+0.035) and rep ≥ 2 favours T (−0.11 to −0.25 on mid/hard tokens). Per domain, H wins on rep = 0
only in pg19 (+0.096) and arxiv (+0.054); elsewhere it is ≈ 0 or negative. **PG-19 is the
exception on every cut** (H better even on repeats: rep ≥ 2 +0.023). That points to a data-mix /
exposure difference, not architecture.

**Not SWA copying.** For repeated 4-grams, Δ by distance to the previous occurrence:
−0.037 (<64), −0.051 (64–512), −0.066 (0.5–2k), −0.068 (2–4k), −0.047 (4–6k, CI to −0.005),
−0.077 (6–8k, CI to +0.002). There is no recovery once the source leaves T's 4096 window, so T's
reuse advantage is not its extra 24 local-attention layers. The shared structure is the 8
full-attention layers, which in the final H run **without positional encoding (DroPE)**.

Next test (queued): the stage-1-end pair (both RoPE, before any long-context stage). If the reuse
deficit disappears there, it belongs to H's long-context recipe (DroPE), not to the mixer.

**Exposure fingerprint (line endings).** Tokens containing `\r` are −1.42 nats [−2.31, −0.05] worse
for H in Python (−0.52 LaTeX, −0.23 HTML), and CRLF files are −0.28 vs −0.08 for LF files. This is
*consistent with* materially different code/data exposure or preprocessing (the official model
card confirms a different data mix and LR schedule). It does not by itself show that CRLF was
normalised; source proportions, other preprocessing, architecture behaviour on rare formatting,
or later-stage recipe could each produce it. Signal kept, explanation deferred. CRLF is only ~3% of Python tokens, so it explains
≈ −0.008 of the −0.082 Python gap; LF-only Python is still −0.076. `\xa0` has no effect in prose.
No verbatim-memorisation signature on PG-19 (no ≥16-token near-zero runs in either model). PG-19
is uniformly H-favoured across windows (10th pct +0.036), while ccnews / wikipedia / python have
heavy negative tails (10th pct −0.14 / −0.15 / −0.30). The worst stretches are name lists,
number/unit runs and CRLF code.

## Stage-1 change-point (2026-09-28; `results/stage1_change_diag3.txt`, pg19 / wikipedia / python)

Pairs: T7s1 = Olmo-3 `stage1-step1413814`, H7s1 = Olmo-Hybrid `stage1-step1414078` (both RoPE, 8k,
before midtrain / long context; data mix and LR schedule still differ). D = final gap − stage-1 gap.

| feature | stage-1 T−H | final T−H | D |
|---|---|---|---|
| all | +0.033 | −0.022 | −0.055 |
| novel (rep 0) | +0.069 | +0.025 | −0.044 |
| rep ≥ 4 | +0.002 | −0.058 | −0.060 |
| rep ≥ 16 | −0.000 | −0.075 | −0.075 |
| open / close | +0.029 / +0.014 | −0.101 / −0.131 | −0.13 / −0.14 |
| content / function at rep 0 | +0.078 / +0.052 | +0.052 / +0.016 | −0.026 / −0.036 |
| pg19 / wikipedia / python | +0.034 / +0.048 / +0.017 | +0.052 / −0.050 / −0.082 | +0.018 / −0.098 / −0.099 |

- **At stage-1 end the published signature reproduces.** H is better everywhere, most on novel
  targets, and the advantage goes to ~0 on long repeats (Li & Merrill: "approaches zero").
- **The final-pair reuse deficit and the 5/7 domain losses arise after stage 1**, in midtraining
  and/or the long-context stage.
- **My written prior was wrong.** I expected the deficit to persist at stage 1, based on Olmo Hybrid
  Table 2 (pretrain Code / LBPP) and RULER 4k. It does not persist at the token level.
- **D is not reuse-selective.** It is a broad downward shift, only moderately larger on long repeats
  (−0.075) than on novel targets (−0.044), and strongly domain-dependent (wikipedia / python ≈
  −0.10, pg19 +0.02). At face value this looks more like a later-stage data / recipe effect than
  "DroPE breaks induction". Not yet shown.
Next: stage ladder (stage-2 end = midtrain, early stage-3, final) for both, on the same three
domains, and the difference-in-differences per stage transition.

## Stage ladder (2026-09-28; `results/stage_ladder_diag3.txt`, pg19 / wikipedia / python)

Checkpoints: S1 = stage-1 end; S2 = midtrain end (T `stage2-step47684`; H souped
`stage2-ingredient1+2-step23842`), both RoPE; S3e = `stage3-step1000` (T: **YaRN** config; H: **no
RoPE / DroPE**, `rope_theta: None`); F = released main. Gap = T − H.

**Gap path:** S1 +0.033 → S2 +0.051 → S3e +0.016 → F −0.022.

- **S1→S2 (midtraining):** the hybrid gains more, mostly on novel targets (D +0.035). No reuse
  deficit.
- **S2→S3e (switch to long context, first 1000 steps):** both models get much worse (all-token
  −0.10 T, −0.14 H), and H is hit harder on every feature. A broad disruption, not reuse-selective.
- **S3e→F (rest of the long-context stage): the reuse-selective change happens here.**
  Within-model change (> 0 = improved):

| | novel | rep ≥ 4 | rep ≥ 16 | close | python |
|---|---|---|---|---|---|
| T (YaRN) | +0.191 | +0.015 | +0.005 | +0.035 | +0.053 |
| H (DroPE) | +0.164 | **−0.041** | **−0.070** | **−0.087** | **−0.028** |

During its long-context stage the hybrid keeps improving on novel targets but gets worse on long
repeated continuations, closing delimiters and code, while T improves on all of them. The
final-pair "reuse deficit" is therefore not a stage-1 architecture property of the hybrid. It is
produced during the hybrid's DroPE long-context stage.

**What this does not yet separate:** positional treatment (DroPE vs YaRN) vs architecture × LC
stage (GDN hybrid under 64k Longmino training). Only the **Hybrid-YaRN** LC checkpoint (Table 3,
not public) cleanly isolates DroPE, and that is item 4 of the author request. A dose-response check
(mid-stage-3 checkpoints) is next, to see whether the repeat degradation grows steadily or appears
late.
