# Modern Guidance Under Strong Baselines — Workbench

**Lane: our-taste. Status: exploratory workbench — not a candidate.**

## 进度页（中文，随每次里程碑更新）

**最后更新：2026-09-28**

### 现在在做什么
- 基线驻留（baseline residency）：在 FLUX.2 [klein] Base 4B（整流流 Transformer，真 CFG，未蒸馏）上搭了自己的可插拔采样器，逐步记录条件/无条件速度的几何量。
- E01（运行中）：GenEval 分层 120 条 × 2 种子 × 16 种配置。内容：CFG 强度扫描、Revisiting 论文四种方法（CFG++ / CFG-Zero* / APG / TCFG）原设置、以及"每步只保留沿 CFG 方向分量"的投影消融。
- 评测：官方 GenEval（新建 `mg-eval` 环境，mmdet3 适配）、PickScore / HPSv2.1 / LAION 美学 / CLIP / 饱和度 / DINOv2 多样性、Qwen3-VL 问答裁判（DPG）。

### 目前的实证事实（都还只是单模型、小样本）
1. FLUX.2-klein 在 1024² 下的时间偏移让 30 步中 20 步落在 σ>0.8；最后约 5 步才从 σ=0.57 走到 0。"前几步"≠"低 σ"。
2. 条件/无条件速度余弦 0.99–0.999；两者之差 ‖Δ‖ 只占 ‖v‖ 的 4–15%，并随去噪单调变小。
3. CFG++ 在整流流 Euler 采样器里**严格等价**于一条强度曲线 `w_t = λσ(1−σ')/(σ−σ')`：λ=1.2 时两端 1.2、中段峰值 9.6；强度随步长反比变化（同一 λ 换步数就换了强度）。
4. APG（w=12, 动量 −0.5）的更新里，正交于 CFG 方向的分量是 ‖Δ‖ 的 3.5–5 倍；无动量时 APG = CFG_w − (w−1)·(Δ 在 x0_c 方向上的投影)。

### 尚未被授权的东西
- 没有候选题，没有方法。上面的"早期引导决定计数/位置"只是待检验的假设。

---

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
