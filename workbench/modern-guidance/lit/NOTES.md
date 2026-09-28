# Modern guidance — literature and genealogy notes

Verified 2026-09-28. PDFs and extracted text in this folder (not committed; `*.pdf`, `*.txt` ignored).
Genesis tags: **[DOC]** = stated by the authors; **[REC]** = our reconstruction. A reconstruction is a
training exercise, not a claim about the authors' history.

---

## 1. Lineage map

### Parent
- **Classifier guidance** (Dhariwal & Nichol 2021): an external noisy classifier trades diversity for fidelity.
- **CFG** (Ho & Salimans 2022, arXiv 2207.12598): train the same net with condition dropout;
  `v = v_u + w (v_c - v_u)`. It is a sampling-time extrapolation, not the score of a tilted
  distribution `p(x) p(c|x)^w` once noise is added. Several 2026 theory papers (2607.19725,
  2606.24025, 2609.24287) derive the distribution the guided ODE actually samples.
- **Prediction space.** In ε/x0/v parameterisations the linear combination is the same up to a
  σ-dependent factor, **but** methods that act on a derived quantity (x0-space projection in APG,
  renoise with ε_u in CFG++) are *not* invariant: the same hyperparameter means a different
  effective guidance in another space or with another step size (see §2, CFG++ note).
- **Flow matching / rectified flow** (Lipman 2023, Liu 2023; SD3, Esser 2024): the model predicts
  `v = ε - x0`, integration is near-straight, typically 25–50 Euler steps with a resolution-dependent
  time shift (FLUX: `mu` from image sequence length). SD3 also re-evaluated the **training** design
  space (logit-normal timestep sampling), i.e. an EDM-style move on the training side.

### Method zoo — what each method actually changes
| method | acts on | per-step effect relative to CFG (Δ = v_c − v_u) | cost |
|---|---|---|---|
| CFG | magnitude | `w Δ` | 2 NFE |
| Interval guidance (Kynkäänniemi 2024) | **timestep schedule** | `w` inside a σ-window, 1 outside | ≤2 NFE |
| CFG++ (Chung 2025) | renoise with ε_u | **exactly a schedule** in flow/Euler form: `w_t = λ σ(1−σ')/(σ−σ')` ∝ 1/step size | 2 |
| CFG-Zero* (Fan 2025) | uncond rescale + zero-init | `v_u ← α v_u`, α=⟨v_c,v_u⟩/‖v_u‖²; first k steps `v=0` (skips the start of the trajectory) | 2 |
| APG (Sadat 2025) | **direction** in x0-space | drop the part of the x0-space update parallel to x0_c; reverse momentum; norm clamp | 2 |
| TCFG (Kwon 2025) | uncond direction | project v_u onto the top singular direction of [v_c; v_u] | 2 + SVD |
| Rectified-CFG++ (2025) | predictor–corrector | conditional step then guided correction | 3 |
| SAG / PAG / SEG / OSEG | **the weak prediction** | replace v_u by a prediction with perturbed/blurred attention | 3 |
| Autoguidance (Karras 2024) | the weak model | guide away from a *smaller/undertrained* model instead of v_u | 2 (needs weak model) |
| C²FG, DG-CFG, PathGuide, adversarial/IT schedules (2026) | schedule | derived or learned `w(t [, c, x])` | 2 (+aux) |
| AdaMaG, MOG, CAT, PMC-CFG (2026) | direction/magnitude | attenuate score-parallel / normal components, cap by posterior mean | 2 |
| Momentum Guidance (2026) | history | extrapolate away from an EMA of past velocities | 1 |

**Observation from the table:** most "new" prediction-level methods are some mix of (i) a per-step
effective scale along Δ and (ii) an orthogonal residual. Guidance Matters (ICLR 2026) already
decomposes updates into parallel/orthogonal-to-CFG parts, but calibrates with *one time-averaged*
scale on an independent trajectory. On-trajectory, per-step projection is the stronger causal
test and is E01 here.

### Modern baseline
- FLUX.2 [klein] Base 4B (undistilled, real CFG; BFL default `w=4.0`, 50 steps). Revisiting used
  `w=7, 30 steps`. SD3.5 Medium/Large and FLUX.1/2-dev are gated for our HF account (not accepted).
- Other open RF Transformers with real CFG: Z-Image (6B), Qwen-Image (20B), Lumina-Image-2, SANA.

### Recent re-evaluation
- **Guidance Matters** (Xie et al., ICLR 2026, 2602.22570): preference models (HPSv2, ImageReward,
  CLIP) reward large CFG scales even when images are visibly oversaturated; GA-Eval compares each
  method with CFG at its effective scale; most methods lose most of their win rate. Mainly SDXL;
  effective scale = time-average of ‖parallel‖/‖Δ‖.
- **Revisiting CFG methods** (Sergievskii, Turevich, Kastryulin, 2608.16786, 17 Aug 2026): eight
  methods on SD3.5-M and FLUX.2-klein-base-4B, GenEval + DPG + OneIG, paired bootstrap. No method
  consistently beats CFG; on FLUX nothing beats CFG beyond the margin. One qualitatively chosen
  config per method, 1 sample per GenEval prompt, no scale curves, no mechanism, no diversity.
  **Large unexplained deltas in their Table 5 (FLUX):** CFG++ counting 0.788→0.550, position
  0.56→0.45; CFG-Zero* counting →0.663, position →0.41. Both methods weaken *early* guidance.

### Remaining pressure (as of 2026-09-28, to be tested, not assumed)
1. The zoo is motivated by oversaturation/off-manifold artefacts at high `w`, and evaluated with
   FID/aesthetic/preference scores. Is that failure still binding for modern RF Transformers at their
   useful `w`? If not, the zoo optimises a non-binding constraint.
2. In modern models guidance is mostly buying **composition** (FLUX GenEval two-object 0.24→0.89,
   counting 0.23→0.79 without/with CFG). Which part of the trajectory and which component of the
   update buy it, and do the zoo's losses come from removing that part?
3. Interval guidance (FID) says *disable* guidance at high noise; Step-AG (2506.08351, alignment)
   says guidance in the *first* steps is enough. The two recommendations conflict because they
   optimise different metrics. The conflict is a lead, not a gap.

---

## 2. Notes on individual methods (checked in code)

- **CFG++ in flow form** (RevisitingCFGMethods `flux2_klein_base/cfgpp.py`): the guided velocity is
  `v_u + λ σ(1−σ')/(σ−σ') Δ`. With 30 shifted steps and λ=1.2, the first step has w≈1.2 and mid-trajectory
  w≈10. Doubling the step count roughly doubles w in the middle. **A fixed λ is not a fixed
  guidance strength across NFE.**
- **CFG-Zero*** zero-init sets `v=0` for the first `k` steps: the latent stays pure noise while σ
  drops, so the model is then queried off its training marginal.
- **APG** (their FLUX config): `w=12, η=0, momentum=−0.5, radius=0`. The paper table says `w=10`, the
  yaml says 12. We use the yaml.

---

## 3. Paper rewinds (research-process genealogy)

Format: Parent · Pressure · Changed premise · Earliest revealing experiment · Alternatives ruled out
· Crystallization · Method birth · Boundary · **Move to imitate**.

### R1. ResNet Strikes Back (Wightman, Touvron, Jégou 2021) [REC]
- **Parent:** ResNet-50 at ~76–77% ImageNet top-1 with the 2015 recipe, used as "the baseline" by
  every new architecture paper.
- **Pressure:** new architectures reported large gains, but trained with modern recipes (long
  schedules, strong augmentation, LAMB, BCE, mixup/cutmix) that the baseline never got.
- **Changed premise:** "the ResNet number in tables measures the architecture". It measures
  architecture × recipe.
- **Earliest revealing experiment:** train the unchanged ResNet-50 with the recipe of the newest
  competitor (DeiT-style). One run moves it to ~80%.
- **Alternatives:** test-resolution effects, evaluation crop, EMA — controlled by reporting several
  procedures (A1/A2/A3) and cost-matched variants.
- **Crystallization:** once one recipe run closes most of the gap, "architecture gains" become
  "recipe gains" by default.
- **Method birth:** no method; the contribution *is* the baseline plus the lesson.
- **Boundary:** not a new model, but a re-attribution that changes how later tables are read.
- **Move:** before crediting a guidance method, give CFG the same tuning budget (scale × steps ×
  schedule) the method got. *E01/E02 here.*

### R2. EDM — Elucidating the Design Space (Karras et al. 2022) [REC + DOC]
- **Parent:** DDPM, DDIM, VP/VE SDE, iDDPM — each a bundle of entangled choices (noise schedule,
  scaling, parameterisation, sampler, loss weighting).
- **Pressure:** improvements could not be attributed; "theory-driven" formulations hid arbitrary choices.
- **Changed premise:** the choices are separable; each formulation is a point in one design space
  (σ(t), s(t), preconditioning, sampler).
- **Earliest experiment:** re-express existing models in one common framework and swap only the
  sampler (Heun, time steps) on fixed pretrained networks — large FID/NFE gains with no retraining.
- **Alternatives:** separated sampling from training: first improve samplers on *fixed* networks,
  then improve training.
- **Crystallization:** when single-axis swaps on fixed networks produce big deltas, the design
  space is the object.
- **Method birth:** the final recipe is the recombination of best choices on each axis.
- **Boundary:** not "a new sampler": a decomposition that makes other methods' gains legible.
- **Move:** express every guidance method as (per-step effective scale along Δ) + (orthogonal
  residual) + (weak-prediction choice) and swap axes on the **same** trajectories.

### R3. FAST action tokenisation (Pertsch et al. 2025) [REC]
- **Parent:** autoregressive VLAs with per-dimension, per-timestep binning (RT-2/OpenVLA).
- **Pressure:** at high control frequency and on dexterous tasks, AR VLAs fail to learn or are
  far behind diffusion/flow policies.
- **Changed premise:** the bottleneck is the action *representation*, not model capacity: at
  high frequency consecutive tokens are almost copies, so next-token loss carries little signal.
- **Earliest experiment:** vary control frequency on a simple interpolation task with naive
  tokens; the AR model degrades as frequency rises, while the task stays easy.
- **Alternatives:** larger model / more data do not fix it; the degradation tracks frequency.
- **Crystallization:** failure scales with redundancy between tokens → compress before tokenising.
- **Method birth:** DCT + BPE compression — the minimal response to measured redundancy.
- **Boundary:** a representation bottleneck localised by a controlled sweep, not a bigger policy.
- **Move:** look for a *regime variable* (here: model generation, prompt compositionality, NFE)
  along which the old method's premise stops holding.

### R4. Applying guidance in a limited interval (Kynkäänniemi et al., NeurIPS 2024) [REC]
- **Parent:** constant-w CFG, known to trade diversity for quality.
- **Pressure:** FID-optimal w is small; larger w looks better but distribution metrics worsen.
- **Changed premise:** guidance does not need to be equally useful at all noise levels.
- **Earliest experiment:** enable guidance only in a window [σ_lo, σ_hi] and sweep the window;
  FID as a function of window.
- **Alternatives:** schedules (linear/cosine ramps) — the paper compares and keeps the interval.
- **Crystallization:** guidance at high noise is harmful (pulls samples to a few modes); at low noise it is useless.
- **Method birth:** a hard interval — the simplest instrument that attacks the localised effect.
- **Boundary:** localisation in time, established by a sweep, not a derivation.
- **Move:** timestep localisation via window sweeps. **Caveat for us:** the conclusion was drawn
  with FID on class-conditional/SDXL models; for composition the high-noise stage may be exactly
  where guidance is needed. The metric decided the "bottleneck".

### R5. Autoguidance — guiding a diffusion model with a bad version of itself (Karras et al., NeurIPS 2024) [REC + DOC]
- **Parent:** CFG, which improves both prompt alignment and image quality.
- **Pressure:** CFG's quality gain comes with diversity loss; nobody knew *why* CFG improves quality at all.
- **Changed premise:** CFG entangles two effects — (a) condition alignment and (b) a quality
  improvement that arises because the unconditional model is a *worse* model making errors
  correlated with the conditional one.
- **Earliest experiment:** a 2-D toy distribution where the learned model's errors are visible;
  guiding with an unconditional model vs. a degraded conditional model.
- **Alternatives:** tested degradation types (capacity, training time) and showed that the
  "weakness" must be of the same kind as the main model's.
- **Crystallization:** the quality part of CFG does not need the condition at all.
- **Method birth:** guide with a smaller/less-trained conditional model — disentangles (b) from (a).
- **Boundary:** a decomposition of *what CFG does*, then a minimal instrument per component.
- **Move:** ask *what CFG buys in the modern regime* (composition vs. quality) and which
  component of the update buys each. Attention-perturbation guidance is autoguidance's cousin.

### R6. SD3 — Scaling Rectified Flow Transformers (Esser et al. 2024) [REC]
- **Parent:** rectified flow with uniform timestep sampling; LDM U-Nets.
- **Pressure:** RF formulations were attractive but underperformed tuned diffusion baselines at scale.
- **Changed premise:** the weighting over timesteps during training matters more than the
  formulation; middle timesteps are hardest and most informative.
- **Earliest experiment:** a large controlled sweep of formulation × timestep sampler at small scale,
  ranked across metrics.
- **Crystallization:** logit-normal timestep sampling wins consistently → becomes the default.
- **Move:** a broad controlled sweep over one design axis before committing — and the recognition
  that *which timesteps carry the signal* is a first-class design variable. The same may hold at
  sampling time for guidance.

### R7. Beyond the 80/20 rule — high-entropy minority tokens in RLVR (Wang et al. 2025) [REC]
- **Parent:** RLVR (GRPO/DAPO) works; the gradient is spread over all tokens.
- **Pressure:** little understanding of *which* tokens carry the learning signal.
- **Changed premise:** tokens are not equal; a small set of high-entropy "forking" tokens decides.
- **Earliest experiment:** measure token-entropy distribution of CoT; see which tokens RL changes.
- **Alternatives:** random-token masks as controls; entropy thresholds.
- **Crystallization:** restricting the policy gradient to the top-20% entropy tokens matches or
  beats full-gradient training → the signal lives there.
- **Method birth:** gradient only on forking tokens — follows directly from the measured asymmetry.
- **Move:** in a working mechanism, locate *where* the effect lives (here: which steps / which
  spatial tokens / which component of Δ), confirm with keep-only / drop-only interventions.

### R8. Does RL really incentivise reasoning beyond the base model? (Yue et al. 2025) [REC]
- **Parent:** RLVR models beat their base models on pass@1.
- **Pressure:** is RL teaching new reasoning or re-weighting existing samples?
- **Changed premise:** pass@1 hides coverage; measure pass@k at large k.
- **Earliest experiment:** plot pass@k vs k for base and RL models; curves cross.
- **Crystallization:** RL narrows coverage while improving pass@1 → re-weighting, not new capability.
- **Move:** guidance is *also* a re-weighting of the model's own distribution at inference.
  "Does CFG create compositional ability or select among seeds that already have it?" is directly
  testable by best-of-k over seeds without guidance vs. with guidance.

### R9. Guidance Matters (Xie et al., ICLR 2026) — in-territory [REC]
- **Parent:** a zoo of guidance methods each reporting wins on HPS/ImageReward/PickScore.
- **Pressure:** simply raising the CFG scale also raises those scores.
- **Changed premise:** "method beats CFG at w" is confounded by effective guidance strength.
- **Earliest experiment:** plot preference scores vs CFG w (monotone up to w=20 on SDXL).
- **Method birth:** a calibration (effective scale), a deliberately fake method (TDG) as a
  negative control, and re-ranking.
- **Boundary with us:** they own "effective-scale confound" and "parallel/orthogonal to CFG".
  They do not localise effects in time, do not test the projection causally on the same trajectory,
  do not use compositional benchmarks as the primary target, and study mostly U-Nets.
