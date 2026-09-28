# Modern Guidance Under Strong Baselines — Workbench

**Lane: our-taste. Status: exploratory workbench — not a candidate.**

## Territory

This workbench studies why many training-free diffusion guidance methods that improved older latent-diffusion / U-Net systems fail to deliver stable gains on modern rectified-flow Transformer models.

The object is **not** “invent a new CFG variant”. Start from the strongest modern baseline and treat the recent collapse of the method zoo as a scientific pressure.

## Why this territory is worth inhabiting

Two recent lines create a strong baseline-first opening:

- **Guidance Matters (ICLR 2026)** shows that common evaluation protocols can make guidance methods look better largely because of effective guidance-strength changes; after calibration, much of the apparent advantage over CFG disappears.
- **Revisiting Classifier-Free Guidance Methods in Latent Diffusion Models (Aug 2026)** reevaluates eight training-free guidance methods on open-weight rectified-flow Transformers and finds that no method consistently beats vanilla CFG across the measured criteria; several methods degrade on FLUX.2 while CFG remains cheaper and competitive.
- At the same time, 2025–2026 methods such as Rectified-CFG++, CFG-MP, CFG-Ctrl, dynamic CFG scheduling, and segmented guidance report gains in particular regimes.

This gives a useful workbench object: **which assumptions behind older guidance improvements stop holding in modern flow-based Transformers, and where?**

## Baseline residency first

1. reproduce strong CFG on at least one open modern rectified-flow model with a fixed, transparent evaluation harness;
2. reproduce a small but representative subset of recent guidance methods before scaling breadth;
3. sweep guidance strength fairly and include effective-guidance calibration where applicable;
4. measure quality, compositional alignment, diversity, latency, and extra model evaluations instead of one reward-model score;
5. establish variance over prompts / seeds so “wins” smaller than evaluation noise are not treated as phenomena.

The first milestone is a trustworthy baseline table, not a new method.

## First exploratory analyses

- **Prompt slices:** counting, spatial relations, text rendering, attribute binding, dense composition, ordinary aesthetic prompts.
- **Timestep localization:** where along the RF trajectory each method helps or hurts.
- **Geometry:** conditional–unconditional prediction gap magnitude, direction, cosine structure, and how method updates decompose into components parallel/orthogonal to vanilla CFG.
- **Architecture transfer:** compare one older U-Net baseline with one modern DiT/RF model under the same prompts to identify which gains truly fail to transfer.
- **Scale sensitivity:** test whether a method’s apparent benefit is only a disguised guidance-scale shift.
- **Failure inversion:** whenever a method hurts a slice, inspect whether disabling or attenuating it only in the harmful region recovers the loss.
- **Cost-normalized comparison:** compare quality at matched NFE / latency, not only matched sampler steps.

## Method permission

No method is allowed at the beginning.

A method becomes justified only after we have evidence for:

> old method failure → identifiable modern bottleneck → controllable stage/signal → simple intervention → robust outcome

Likely interventions, if earned, should be small: stage gating, prompt-conditioned attenuation, geometry-aware mixing, or switching between vanilla CFG and a specialized correction. Do not jump directly to a learned controller.

## What would change our understanding

Useful outcomes include:

- most methods collapse after fair guidance-strength matching → evaluation/scale confounding is the dominant story;
- failures cluster in early or late timesteps → stage-specific mismatch becomes the object;
- failures are prompt-family-specific → “universal guidance improvement” is the wrong abstraction;
- U-Net gains disappear on DiT/RF because update geometry changes → architecture transition becomes the bottleneck;
- one method remains genuinely superior after matched-strength, matched-cost evaluation → strengthen that baseline and study why before inventing anything.

## Risks / kill conditions

- If the Aug-2026 re-evaluation already contains the same mechanistic analyses needed to explain the failures, stop.
- If all differences disappear under correct hyperparameter sweeps and evaluation uncertainty, record the negative result and stop.
- If progress requires proprietary models or human evaluation at a scale we cannot support, narrow or stop.
- If the workbench degenerates into a leaderboard of guidance tricks, stop.

## Paper identity

None yet.

The intended paper shape, if one eventually emerges, is baseline → failure map → bottleneck → minimal intervention → benchmark/ablation validation. But the workbench is allowed to end with no method and no candidate.
