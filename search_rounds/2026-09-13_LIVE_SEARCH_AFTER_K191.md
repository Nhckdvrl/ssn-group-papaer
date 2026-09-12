# 2026-09-13 — Live Search After K191

**Purpose:** persistent rolling log for the current search round so network interruption does not cause repeated rediscovery. Any seriously investigated dead route is recorded here immediately.

**Rule:** only `PILOT-AUTHORIZED` candidates are surfaced as actionable topics. `MAYBE` / `SERIOUS` / blocked ideas stay internal and are either killed or fully selected before user-facing promotion.

---

## Hook A — Final-layer hidden-state angular jump

**Status:** `DROP / OWNER COLLISION — DO NOT REDISCOVER THIS ROUND`  
**Origin:** Shibata et al., Findings EACL 2026, *Suppressing Final Layer Hidden State Jumps in Transformer Pretraining*.

Observed mother phenomenon:
- many open-weight Transformer LMs show small angular displacement through middle layers but a disproportionately large jump at/near the final layer;
- the jump grows over pretraining/checkpoints;
- jump-suppressing regularization (JREG) reduces the phenomenon and modestly improves downstream performance;
- the parent interprets the jump as possible over-reliance on final layers / under-utilization of middle layers, but does not directly establish why this late reconfiguration emerges.

Primary source: https://aclanthology.org/2026.findings-eacl.64/

### Owner assassination result

The natural mechanism question — why computation remains relatively quiet/off-readout in the body and changes abruptly near the end — is no longer open enough.

1. **Oskin 2026, *Off-Axis, On Purpose: Where a Transformer Computes Concepts and Why it Does So*** directly studies why intermediate computation is held away from the vocabulary readout and why the answer arrives late. In a controlled 12-layer Transformer, attention writes remain strongly off the unembedding/readout direction through depth; forcing attention onto the readout is 64–84x more damaging than matched random rotations, specifically through cross-token mixing. In the late phase, the FFN writes the answer on-axis by addition. This supplies a direct functional account for late representational commitment rather than merely observing late-layer specialization.
   - https://arxiv.org/abs/2608.10251
2. **Queipo-de-Llano et al., ICLR 2026, *Attention Sinks and Compression Valleys in LLMs are Two Sides of the Same Coin*** already proposes a causal/theoretical `Mix → Compress → Refine` depth organization, with late layers performing selective refinement after a compressed middle phase.
   - https://proceedings.iclr.cc/paper_files/paper/2026/hash/1734b19d9afe7d2c7f1154954eaf0d5a-Abstract-Conference.html
3. **Bhattacharya & Kolli 2026, *An Analysis of Residual-Stream Geometry Across Transformer Depth*** independently reproduces a quiet-middle / strong-late transition across six instruction-tuned models and finds Procrustes residual peaking at the final transition. It explicitly remains descriptive, but it makes the geometry itself a current named object.
   - https://arxiv.org/abs/2607.18348
4. **Guda 2026, *Geometric and Behavioral Stratification in Transformer Residual Streams*** identifies the unembedding prediction direction as a narrow privileged readout interface across 18 models and causally separates prediction-proximal from prediction-distal residual structure.
   - https://arxiv.org/abs/2608.12447

### Strongest reviewer compression

> `Shibata: final angular jump + Oskin: functional off-axis workspace / late on-axis answer writing + ICLR Mix-Compress-Refine + 2026 residual-stream geometry = your explanation.`

The exact numerical identity between Shibata's angular-jump metric and Oskin's late on-axis write is not directly proven, but establishing that bridge would mostly align two already-owned descriptions rather than create a sufficiently new model-science inference. A study that only decomposes JREG/jump into readout-aligned vs orthogonal components is therefore too close to successor mechanism work.

### Verdict

**DROP.** Do not promote `why does the final layer jump?`, `jump = late readout commitment`, or `is JREG smoothing delayed commitment?` as a new candidate unless a qualitatively different contradiction emerges. Current space is too owned for the Main bar.

---

## Hook B — Why masked diffusion tolerates repeated data while AR overfits

**Status:** `DROP / DIRECT MECHANISM OWNER — DO NOT REDISCOVER THIS ROUND`

### Origin

NeurIPS 2025, *Diffusion Beats Autoregressive in Data-Constrained Settings*, establishes a large stable contrast: under repeated limited data, autoregressive LMs saturate/overfit while masked-diffusion LMs continue benefiting from additional epochs and have a far larger data-reuse half-life.

- https://proceedings.neurips.cc/paper_files/paper/2025/hash/0f705a932553c08ebf0d1bc520b7cbc6-Abstract-Conference.html

ICLR 2026, *Dual-objective Language Models: Training Efficiency Without Overfitting*, independently reproduces the complementary AR-fast/overfit versus MD-slow/resilient regimes across 50 models and turns them into a mixed-objective training recipe.

- https://proceedings.iclr.cc/paper_files/paper/2026/hash/c5f92e7fa410b1055d8a45e86fdd1adb-Abstract-Conference.html

### Owner assassination result

The obvious unresolved question `why does MD reuse data better?` is already substantially answered by the NeurIPS mother itself. It interprets randomized masking as implicit data augmentation over a richer distribution of conditional prediction tasks / token orderings, unlike AR's fixed left-to-right factorization, and performs a direct intervention: augmenting AR training with multiple token orderings systematically lowers validation loss and delays overfitting; with enough orderings it approaches MD behavior.

The same paper explicitly frames the complementary downside: order diversity reduces specialization and therefore training compute efficiency, while fixed AR order gives dense repeated reinforcement of one task. The ICLR 2026 dual-objective paper then exploits exactly this complementarity.

### Strongest reviewer compression

> `NeurIPS 2025 already observes the overfitting gap, proposes task/order diversity as the mechanism, and intervenes on AR order diversity; ICLR 2026 operationalizes the same explanation with a mixed objective.`

A follow-up about generic gradient diversity, memorization, or representation differences would therefore be mechanism refinement inside an already centralized explanation, not a sufficiently new parent.

### Verdict

**DROP.** Do not reopen as `why is diffusion resistant to repetition?`, `objective diversity prevents memorization`, or `AR fixed factorization causes overfitting` without a qualitatively different empirical contradiction to the existing order-diversity account.

---

## Hook C — Why the same reasoning data is more valuable in pretraining than SFT

**Status:** `DROP / COST-BRIDGE FAILURE — DO NOT REDISCOVER THIS ROUND`

### Origin

ICLR 2026, *Front-Loading Reasoning: The Synergy between Pretraining and Post-Training Data*, reports a strong training-stage asymmetry using 8B models pretrained from scratch on roughly 1T tokens:
- front-loading reasoning data creates a large advantage that later SFT cannot catch up to;
- pretraining benefits especially from diversity/scale while SFT is more sensitive to quality;
- some high-quality pretraining data has little immediate effect but becomes valuable only after SFT;
- scaling mixed-quality SFT can wash out earlier gains.

- https://proceedings.iclr.cc/paper_files/paper/2026/hash/82eac7050fb44b662062ac64aa6637c3-Abstract-Conference.html

### Why it is attractive

The question `why can the same broad reasoning supervision have different value depending on when it is introduced?` is natural and the mother effect is real. The latent-effect result is especially mechanism-shaped: pretraining can alter later learnability without an equally large immediate behavioral gain.

### Selection failure

The decisive quantity is inherently a training-trajectory / stage interaction. A credible causal mechanism study must re-control at least the stage of exposure, token budget, surrounding data distribution, optimizer trajectory, and subsequent SFT. The mother itself is established at an 8B / ~1T-token controlled-pretraining scale.

A cheap pilot on a tiny model/toy reasoning distribution would at best establish that stage interactions *can* occur; it would not identify the mechanism behind the natural mother. Conversely, reproducing the relevant stage contrast at a scale where the mother is known to hold is a substantial pretraining program, not a bounded E01 under the current project budget.

This is analogous to the L19 lesson: the scientific gap may remain interesting, but the discriminating effect cannot be cleanly tied to the mother within an affordable pilot. Narrowing to one synthetic stage effect would change the paper identity.

### Strongest reviewer/feasibility compression

> `Front-Loading Reasoning already establishes the phase-dependent law; a small-model study would be a toy explanation, while a faithful mechanistic re-run requires full controlled pretraining.`

### Verdict

**DROP for current project.** Do not reopen as `pretraining creates latent reasoning potential`, `why diversity early / quality late`, or `why SFT cannot catch up` unless a later paper supplies a cheap natural instrument/checkpoint resource that makes the stage interaction identifiable without reproducing large-scale pretraining.

---

## Hook D — Fewer unique data can train faster under repetition

**Status:** `DROP / DIRECT MECHANISM OWNER — DO NOT REDISCOVER THIS ROUND`

### Origin

ICML 2026 / arXiv 2605.20314, *Less Data, Faster Training: Repeating Smaller Datasets Speeds Up Learning via Sampling Biases*, reports the counterintuitive law that under repeated-data training, using fewer unique examples can accelerate optimization/learning.

### Owner assassination result

The paper itself does not leave the obvious mechanism question open. It traces the effect to sampling biases induced by smaller repeated datasets, links those biases to layer-wise norm growth / effective relative learning rates, and uses random-label and parameter/learning-rate interventions to reduce the speed gap. Thus `why does less unique data sometimes train faster?` is already the paper's central explanatory contribution rather than an unexplained side anomaly.

### Strongest reviewer compression

> `The mother already owns the anomaly, the norm/effective-step mechanism, and causal interventions on the proposed pathway.`

### Verdict

**DROP.** Do not reopen as `repetition changes optimization geometry`, `sampling bias accelerates learning`, or a generic norm-growth mechanism without an independent contradiction to the published account.

---

## Hook E — Distilled pretraining improves generation diversity while harming ICL

**Status:** `DROP / PARENT CENTRALIZED — DO NOT REDISCOVER THIS ROUND`

### Origin

ICLR 2026, *Distilled Pretraining: A Modern Lens of Data, In-Context Learning and Test-Time Scaling*, reports a stable trade-off under distilled pretraining: weaker induction / in-context-learning behavior alongside improved generation diversity / pass@k / test-time-scaling characteristics, including comparisons under matched data regimes.

### Owner assassination result

The paper itself makes this trade-off the scientific center, connecting distillation to low- versus high-entropy token prediction, induction behavior and generation diversity, and proposes token-routing/mixture-style mitigation. Therefore an obvious `why does distillation hurt ICL but improve sampling diversity?` project would be another decomposition of a mechanism the parent already claims and tests.

### Verdict

**DROP.** Do not reopen as `distillation suppresses induction heads`, `distillation changes entropy and diversity`, or `ICL vs test-time scaling trade-off` without a new same-quantity contradiction that the existing entropy/routing account cannot explain.

---

## Hook F — Is pretraining-WD 'plasticity' actually downstream effective step size?

**Status:** `DROP / SELECTION FAILURE — DO NOT REDISCOVER THIS ROUND`

### Origin

ICML 2026, Han et al., *Weight Decay Improves Language Model Plasticity*, finds that stronger pretraining weight decay can worsen base-model loss yet improve later SFT performance across Llama/OLMo scales and tasks. The authors interpret the downstream advantage as greater pretrained-model plasticity and report representation/attention/overfitting correlates.

- https://arxiv.org/abs/2602.11137

A later August-2026 paper, *Effective Learning Rate Governs Loss Dynamics in Language Model Pretraining*, establishes a strong law in LLM pretraining: LR and parameter norm govern loss trajectories largely through `ELR = LR / ||W||`, and controlled ELR matching collapses trajectories across different norm-control methods. Pretraining weight decay itself strongly controls parameter norms.

- https://arxiv.org/abs/2608.24814

This creates an initially attractive identification question: high-pretraining-WD checkpoints have smaller norms, so under the same nominal downstream LR they can receive larger relative/angular steps. Does their apparent downstream 'plasticity' survive explicitly matching effective learning rate during fine-tuning?

### Why the trivial critique is insufficient

Han et al. already perform an extensive downstream hyperparameter robustness sweep for OLMo-2-1B-20x: four pretraining-WD checkpoints × three fine-tuning LRs × three fine-tuning WDs × three batch sizes (216 fine-tuned models), and the higher-pretraining-WD advantage remains even when selecting the best downstream hyperparameter combination per checkpoint. Therefore `they just fixed the fine-tuning LR` is not a valid novelty claim.

Public same-seed checkpoints and fine-tuning code exist, so a bounded E01 could in principle compare standard FT with an ELR-normalized/matched optimizer without repeating pretraining.

### Selection failure 1 — one-sided paper identity

The proposed experiment is not outcome-robust enough for the current bar.

- If ELR matching largely collapses/reverses the high-WD advantage, the result could revise the interpretation of the ICML-2026 mother: apparent plasticity is partly checkpoint × optimizer geometry rather than a checkpoint-only property.
- If the advantage persists under matched ELR, the result mostly says that a general ELR mechanism does not explain Han's effect, while Han already provides extensive downstream-hyperparameter robustness and representation differences. That outcome is scientifically clean but too close to a confirmation/boundary result to sustain the same paper identity.

Thus the candidate still depends heavily on one favorable mediation outcome.

### Selection failure 2 — intervention does not uniquely identify mediation

A global LR cannot equalize `LR / ||W||` across all corresponding matrices because pretraining WD changes layer/matrix norms non-uniformly. A per-matrix ELR-normalized optimizer could force matching, but that intervention changes the downstream optimizer geometry itself. If the checkpoint ranking changes, the clean inference is only that **ranking depends on optimizer coordinates**, not that the original pretraining-WD effect was causally mediated by ELR.

That distinction weakens the strongest intended claim.

### Selection failure 3 — reviewer compression is too strong

Nearby work already supplies all broad components:
- NeurIPS 2024 `Normalization and effective learning rates in reinforcement learning` directly links parameter-norm growth / ELR decay to plasticity loss and uses Normalize-and-Project as an intervention;
- NeurIPS 2024 `Why Do We Need Weight Decay in Modern Deep Learning?` argues modern weight decay primarily changes optimization dynamics rather than acting as classical regularization, including in LLM pretraining;
- ICML 2026 Han et al. establish the LLM pretraining-WD → downstream-plasticity phenotype;
- Aug-2026 ELR-collapse work establishes `LR / norm` as a strong coordinate for LLM pretraining dynamics.

Strongest compression:

> `ELR already controls plasticity in continual/RL settings + weight decay already acts through optimization/norm dynamics + Han gives the LLM plasticity phenotype + ELR collapse extends the coordinate to LLM pretraining = test ELR during SFT.`

The exact downstream experiment is not done, but the paper would risk reading as a transfer/application of a known mechanism to Han's new phenotype rather than a fresh Main-level scientific inference.

### Verdict

**DROP.** Do not reopen as `plasticity is optimizer-relative`, `match ELR across high/low pretraining-WD checkpoints`, or `parameter norm explains Han 2026` unless independent evidence first produces a stronger SAME-QUANTITY contradiction or a function-preserving/selective intervention that yields an outcome-robust new law.
