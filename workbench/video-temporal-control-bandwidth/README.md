# Temporal Control Bandwidth in Video World Models — Workbench

**Lane:** our-taste  
**Status:** exploratory workbench — not a candidate

## Territory

Modern video generators and video world models obtain tractability by temporally compressing several raw frames into one latent frame. The same systems are increasingly asked to obey controls, actions, contacts, and camera trajectories that evolve at the original frame rate or faster.

This workbench studies the resulting representation/interface question:

> **How much fine-grained temporal control survives video-latent compression, and when does the compression grid itself become a bottleneck?**

The object is broader than one action-following benchmark and narrower than “build a better world model.” We care about temporal resolution, within-latent timing, phase/boundary sensitivity, short events, and high-frequency control under otherwise fixed pretrained systems.

No final paper RQ or method is registered.

## Why this territory exists

Several independent systems already reveal the same pressure from different directions:

- **Improved Video VAE (CVPR 2025)** shows that causal video VAEs create unequal information access and unbalanced reconstruction quality across frames within temporal groups, motivating group-causal processing.
- **VideoWorld (CVPR 2025)** deliberately removes temporal downsampling in its causal codec to preserve frame details.
- **SANA-WM (2026)** explicitly identifies a compression mismatch: one latent summarizes multiple raw frames with distinct camera poses, so it adds a fine-grained per-raw-frame Plücker branch in addition to latent-rate camera conditioning.
- **ForgeWM (2026)** notes that keyboard/mouse controls must remain aligned with temporally compressed latent chunks during causal training and rollout.
- **Mira (2026)** contains explicit implementation logic for temporal action offsets when video/action streams are downsampled; the code warns that a one-frame offset error misaligns actions and frames, and that live inference cannot always know a future within-chunk action.
- **World2Act (2026)** groups multiple frame-level actions into each video-latent window and preserves all high-frequency action variations rather than collapsing them to one action.
- **EmbodiedVAE (ECCV 2026)** argues that ordinary video-VAEs can lose motion semantics under temporal compression and therefore uses weaker temporal compression for robot motion than for background context.

These are not evidence for one predetermined answer. They are evidence that temporal compression and control resolution are repeatedly becoming load-bearing at different layers of modern video/world-model systems.

## Related-work boundary

This workbench is **not**:

- another generic action-following benchmark;
- mid-chunk action editing (e.g. ActionSplice);
- generic long-video memory/cache work;
- another VAE trained from scratch for higher PSNR;
- generic dynamic-frame-rate acceleration;
- “EmbodiedVAE but with a different compression ratio.”

The scientific target is the **behavior of fixed compression interfaces**: what temporal information/control is preserved, aliased, phase-dependent, or erased, and whether downstream models compensate for it.

## Baseline residency

Start with frozen, public artifacts.

### Tier 1 — VAE-only diagnosis

Use several public causal video VAEs/tokenizers with different temporal structures, prioritizing:
- Wan-VAE / Wan2.x;
- IV-VAE;
- Cosmos / Hunyuan-family VAE where public and practical;
- optionally a non-temporally-compressed or weakly-compressed control.

This stage requires no world-model training.

### Tier 2 — downstream video/world model diagnosis

Prefer open models where temporal action alignment is explicit:
- minWM small/open variants;
- ForgeWM checkpoints;
- Mira;
- SANA-WM for continuous camera trajectories;
- a Wan2.x-based playable/world model if its action interface is reproducible.

Do not begin by training a foundation world model.

## First analyses

These are discovery experiments, not preregistered claims.

### A. Temporal phase equivariance

Take the same clip/event and shift it by 0...k-1 raw frames relative to a VAE temporal stride k.

Measure:
- per-frame PSNR / LPIPS;
- optical-flow error;
- motion-onset timing;
- reconstruction of short contacts / object displacement;
- latent distance and decoder output as a function of phase mod k.

The key question is whether semantically identical dynamics receive systematically different treatment solely because of their position inside the compression grid.

### B. Temporal bandwidth sweep

Construct or collect motions whose temporal frequency/duration is varied while spatial content is held as constant as practical:
- smooth camera motion;
- direction reversals;
- short action pulses;
- contact / release events;
- fast object motion.

Find the regime where reconstruction or action-conditioned response degrades as event duration approaches or falls below one latent stride.

### C. Action-within-stride perturbation

For an action-conditioned world model, preserve total action magnitude but move the same action pulse to different raw-frame positions inside one latent interval.

Compare generated:
- response latency;
- displacement / camera trajectory;
- direction;
- object interaction outcome;
- counterfactual separation between action pairs.

This directly tests whether the system respects within-latent timing or only a coarse aggregated action.

### D. Alignment implementation audit

Reproduce the exact action-to-latent alignment rules used by public systems (offsets, padding, first-frame handling, grouping, interpolation).

Then perturb only the alignment by ±1 raw frame or by alternative within-window aggregation.

Large changes are useful gradients: they reveal how load-bearing the interface is.

### E. Compensation test

A VAE-level artifact is not automatically a world-model artifact.

For each stable VAE phenomenon, test whether the downstream DiT/world model compensates for it. If the full model is invariant even when the VAE is not, the VAE observation alone is insufficient.

## Information-gain outcomes

Useful outcomes include:

- **No phase/bandwidth effect after strong controls:** kill the central hypothesis; downstream models compensate well.
- **VAE effect exists but disappears downstream:** keep as tokenizer knowledge, not a paper candidate.
- **Effect survives across multiple VAEs/models:** temporal discretization is a real system-level object.
- **Only high-frequency/contact events fail:** the relevant object becomes task-dependent temporal bandwidth, not generic VAE quality.
- **Action encoding fixes VAE limitations:** study what information the conditioning pathway restores.
- **Different systems fail at different temporal phases:** architecture/alignment choices, not nominal compression ratio alone, are load-bearing.

## Method permission

No new module at the beginning.

Only after a stable bottleneck survives multiple baselines may we test a minimal intervention, for example:
- phase-randomized training/augmentation;
- phase-aware action conditioning;
- preserving sub-stride controls instead of pooling;
- adaptive temporal rate only around high-information events;
- overlap / boundary averaging;
- a small fine-timescale branch while keeping the backbone frozen.

A method must follow:

> failure → localized temporal bottleneck → controllable interface → outcome

## Compute fit

The workbench is intentionally scoped to one machine.

- VAE-only analysis: typically 1 GPU.
- Frozen world-model inference/diagnostics: 1–4 GPUs depending on backbone/resolution.
- Prefer 1B–5B open backbones for repeated sweeps.
- Small adapters / conditioning layers / LoRA are acceptable on 4×A100 80GB or 4×RTX PRO 6000 96GB.
- No experiment may require cross-node training.
- Full from-scratch video/world-model pretraining is out of scope.

## Kill conditions

Stop or sharply narrow if:

1. the apparent phase effect is only the already-known first-frame reconstruction imbalance from causal VAEs;
2. results disappear under correct padding/alignment and sufficiently strong baselines;
3. only one proprietary/single architecture exhibits the effect;
4. ActionSplice / SANA-WM / EmbodiedVAE or another nearest prior already owns the same scientific conclusion, not merely an adjacent fix;
5. demonstrating downstream consequences requires foundation-model-scale retraining;
6. the project degenerates into a tokenizer leaderboard.

## Anchor artifacts / nearest prior

- Improved Video VAE for Latent Video Diffusion Model (CVPR 2025): https://openaccess.thecvf.com/content/CVPR2025/html/Wu_Improved_Video_VAE_for_Latent_Video_Diffusion_Model_CVPR_2025_paper.html
- VideoWorld (CVPR 2025): https://openaccess.thecvf.com/content/CVPR2025/html/Ren_VideoWorld_Exploring_Knowledge_Learning_from_Unlabeled_Videos_CVPR_2025_paper.html
- SANA-WM (2026): https://arxiv.org/abs/2605.15178
- ForgeWM: https://github.com/asdfo123/ForgeWM
- Mira: https://github.com/mira-wm/mira
- World2Act (2026)
- EmbodiedVAE (ECCV 2026): https://arxiv.org/abs/2608.02990
- ActionSplice (2026), nearest boundary/editing control: https://arxiv.org/abs/2609.08230
- DLFR-VAE / DLFR-Gen, nearest adaptive temporal-rate lineage.

## Paper identity

None yet.

The workbench is successful if baseline residency produces a stable, simple empirical object that changes our understanding of how temporal compression interacts with controllable video generation/world modeling. It is allowed to end with no candidate.
