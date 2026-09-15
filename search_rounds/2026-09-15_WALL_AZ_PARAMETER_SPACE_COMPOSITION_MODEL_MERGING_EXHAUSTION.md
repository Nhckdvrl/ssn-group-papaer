# WALL-AZ — Why can pretrained neural models be composed in parameter space?

Date: 2026-09-15  
Status: **EXHAUSTED / DIRECT THEORY PROGRAM EXISTS**  
Mode: problem-first lineage + regime-change + owner audit  
Candidate generation: **OFF**

## Mother question

Neural-network parameters are not intrinsically named scientific coordinates. Hidden units can be permuted, rescaled, or otherwise reparameterized while preserving function, and independently trained solutions can occupy different parts of a non-convex loss landscape. Why, then, can fine-tuned foundation models so often be averaged, added/subtracted as task vectors, or merged directly in raw parameter space without first solving a full representation-alignment problem?

This is a real long-lived scientific problem. It is not `how to build a better model merger`.

## Old intellectual ancestry

The pre-foundation-model premise was that raw coordinates of separately trained neural networks are generally not directly comparable because of symmetry and optimization non-identifiability.

Relevant ancestry includes:

- loss-landscape and mode-connectivity work showing that apparently distinct optima can be connected by low-loss curves;
- permutation-symmetry work arguing that much apparent separation between solutions can disappear after re-basing hidden units;
- Git Re-Basin-style results showing that independently trained networks can sometimes be aligned by permutation before interpolation.

The old load-bearing premise was therefore approximately:

> independently learned parameter vectors do not share a canonical coordinate semantics merely because the architectures match.

## Foundation-model regime change

Large pretrained models create a qualitatively different regime: many downstream models begin from the **same pretrained checkpoint** and move only through fine-tuning/post-training.

This partially breaks the old premise. Fine-tunes inherit a common coordinate system and often remain close enough to the pretrained solution that raw arithmetic can retain functional meaning.

The phenomenon is strong and reproducible:

- **Model Soups** (ICML 2022) showed that averaging independently fine-tuned models from a shared pretrained initialization often improves accuracy/robustness and explicitly connected this to the models occupying a common low-error basin.
- **Editing Models with Task Arithmetic** (ICLR 2023) made vector addition/subtraction of fine-tuning deltas a direct object of study.

So WALL-AZ passes the regime-change gate at the level of the mother problem.

## Mature explanation map

Unfortunately, the explanatory space is no longer empty. Several distinct but compatible programs already attack exactly why parameter arithmetic works and when it fails.

### 1. Shared basin / local geometry

Shared initialization can keep fine-tunes inside a region where interpolation remains low-loss. This is already explicit in Model Soups and the broader mode-connectivity literature.

### 2. Symmetry alignment / re-basing

Permutation symmetry explains why separately trained networks may need coordinate alignment before arithmetic. Git Re-Basin and follow-up work make this an explicit mechanism rather than an unasked caveat.

More importantly for a tempting residual, **Update Your Transformer to the Latest Release: Re-Basin of Task Vectors** (ICML 2025) already attacks task-vector transport across different pretrained backbones by learning a re-basing/alignment. Thus `shared base vs different base` is not an unowned identification axis.

### 3. Local linearization / tangent-space explanations

**Task Arithmetic in the Tangent Space** (NeurIPS 2023) relates successful task arithmetic to the local linearized/NTK regime and to localization of task effects in pretrained-model eigendirections. It directly asks why weight disentanglement can emerge from pretraining and why tangent-space arithmetic can reduce interference.

### 4. Sparse / partially disjoint task supports and interference

TIES-style work identifies redundant changes and sign disagreement as a source of destructive interference. **Localizing Task Information for Improved Model Merging** (ICML 2024) goes further by showing that much task information can be localized to sparse, partly non-overlapping parameter subsets and by distinguishing helpful, selfish, and catastrophic parameters.

### 5. Gradient / multitask-learning interpretation

Recent theory explicitly relates task vectors to optimization updates. **On Task Vectors and Gradients** (2026) shows the one-step/one-epoch relationship exactly and develops higher-order approximations for longer fine-tuning, reframing task-vector addition as an approximation to combined gradient-based learning rather than a mysterious algebra of semantic directions.

### 6. Dedicated theory of merging and transport

2025–2026 work increasingly treats mergeability, task-vector subspaces, interference, and transport as a theory program in their own right. This is no longer a field where methods exist but the scientific `why` has been left untouched.

## SAME-QUANTITY pressure

The natural quantity is something like:

> functional loss / task performance after a specified arithmetic operation on matched model deltas.

The problem is not absence of competing predictions. The problem is that the major explanatory variables above are already the explicit objects of direct owners:

- common basin / geometric proximity;
- permutation alignment;
- local linearity;
- gradient equivalence;
- overlap and conflict of task supports;
- distance from the shared base;
- cross-backbone transport after re-basing.

A new project would almost inevitably ask which already-proposed explanation better predicts mergeability in another regime.

## Residuals audited and rejected

### Residual A — Why does shared initialization matter?

Already compressed by shared-basin/local-linearization/gradient explanations. Measuring distance from initialization or training trajectory does not create a new scientific axis.

### Residual B — Is mergeability caused by low-rank/sparse task directions?

Directly inside task-localization, low-rank task-vector, and interference literatures. It also collides with earlier repository walls on low-rank adaptation and specialization.

### Residual C — Can task vectors transfer across base checkpoints?

Directly owned by ICML 2025 re-basing/transport work.

### Residual D — Which theory predicts when arithmetic will fail?

Scientifically useful, but reviewer-compresses to a comparative/theory-consolidation study inside an already active model-merging theory program. It is not a residual question prior work could not naturally formulate.

### Residual E — Why are LLMs more mergeable than independently trained small networks?

Without a new invariant quantity, this reduces to the already-known regime difference: shared pretrained initialization plus local downstream updates. Changing scale/model family does not reopen the parent.

## Reviewer compression

The harsh compression is:

> “Model merging/task arithmetic already has shared-basin, symmetry/re-basing, tangent-space, gradient, sparsity/localization, and interference explanations. This paper compares or refines those explanations on another set of models.”

I do not see a remainder that survives this compression without changing the metric, architecture, or merger.

## Verdict

**WALL-AZ EXHAUSTED. No L-series. No K-series allocation.**

The mother problem is excellent and the foundation-model regime genuinely changes an old assumption. It still fails as our project source because the modern regime change has already generated a dense first-order theory program.

### Anti-resurrection

Do not reopen as:

- `why model soups work` on another model family;
- task-vector linearity vs nonlinearity;
- sparse/low-rank task directions;
- mergeability predicted by parameter distance;
- same-base vs different-base task-vector transfer;
- re-basing plus task arithmetic;
- another empirical comparison of merging methods;
- another probe of where task information lives.

A reopening would require a genuinely different old scientific claim whose inference depends on parameter comparability and for which foundation-model weight composition creates a **new identifying operation**, not merely another mergeability predictor.

## Core references

- Garipov et al. (NeurIPS 2018), *Loss Surfaces, Mode Connectivity, and Fast Ensembling of DNNs*.
- Entezari et al. (2021), permutation invariance / linear mode connectivity conjecture.
- Ainsworth et al. (2022), *Git Re-Basin: Merging Models modulo Permutation Symmetries*.
- Wortsman et al. (ICML 2022), *Model Soups*.
- Ilharco et al. (ICLR 2023), *Editing Models with Task Arithmetic*.
- Ortiz-Jimenez et al. (NeurIPS 2023), *Task Arithmetic in the Tangent Space*.
- Yadav et al. (NeurIPS 2023), TIES-Merging.
- Tang et al. (ICML 2024), *Localizing Task Information for Improved Model Merging*.
- ICML 2025, *Update Your Transformer to the Latest Release: Re-Basin of Task Vectors*.
- 2026, *On Task Vectors and Gradients*.
