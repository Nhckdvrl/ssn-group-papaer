# 2026-09-13 — Continued Search After L31 II

Continuation of `2026-09-13_CONTINUED_SEARCH_AFTER_L31.md`. Same persistence rule: log every nontrivial killed lead immediately; only report a topic to the user after full SEARCH+SELECT reaches `PILOT-AUTHORIZED — named bounded E01`.

## N. Parallel Attention+MLP as the root cause of small-Pythia late saturation — DROP

**Scientific object:** Why do small Pythia models become worse late in pretraining while closely matched small language models do not? Is Pythia's hardware-motivated parallel Attention+MLP block the load-bearing trigger, rather than an intrinsic softmax/output-rank capacity wall?

**Mother / same-quantity pressure:**
- COLM 2024 establishes late-training loss degradation / saturation in small Pythia models.
- PolyPythias (ICLR 2025) provides nine additional seeds across 14M–410M and reports highly consistent training dynamics across seeds/sizes; ICML 2026 explicitly cites Pythia/PolyPythias saturation for <=160M.
- ICML 2026 Spotlight `Disentangling Geometry, Performance, and Training in Language Models` trains an OLMo-14M that exactly matches Pythia-14M and states that the **sole architectural difference is sequential attention instead of Pythia's parallel variant**. Pythia shows late loss degradation and abrupt rank collapse; matched OLMo does not. The authors explicitly conjecture that parallel attention may contribute, while leaving the root cause open.
- PaLM previously reported a small-scale quality penalty for parallel Attention+MLP that shrinks/disappears at larger scale, giving independent architecture pressure rather than a Pythia-only observation.

**Closest mechanistic owners:**
- Aug-2026 `Feed-Forward Steering in Transformer Residual Dynamics` develops an attention-as-aggregation / FFN-as-local-steering account and defines a sequential-to-parallel defect. It shows that low-defect sequential layers can be parallelized with small loss while high-defect layers degrade sharply.
- Mar-2026 `Half the Nonlinearity Is Wasted` finds strong architecture dependence between sequential GPT-2 and parallel Pythia MLP behavior and explicitly discusses the sequential-vs-parallel trade-off.

**Tempting missing inference:** A causal training intervention could try to show that removing same-layer Attention→MLP dependence causes the late small-model failure, perhaps with a scale boundary and a growing FFN-steering/commutator defect.

**Strongest reviewer compression:**
> `Kulkarni et al.: matched Pythia-14M saturates while the otherwise matched sequential OLMo-14M does not, and parallel attention is explicitly proposed as the cause` + `Mudarisov et al.: we already know what computation is lost when a sequential block is parallelized and have a defect predicting its quality cost` + `PaLM / later architecture sweeps: parallel blocks already have a small-scale quality penalty` = `you confirmed an already strongly implied explanation`.

**Why this fails the successful-result test:**
Even a perfect same-code parallel-vs-sequential training result would mostly upgrade Kulkarni's near-controlled observation/conjecture to a cleaner causal replication. The likely mechanism—loss of current-layer attention-conditioned FFN steering—is already supplied by the Aug-2026 dynamics work. The exact late-training intervention is missing, but the strongest expected answer is substantially implied by the closest components.

**Identification / pilot problem:**
A cheap checkpoint surgery (switching a trained parallel Pythia checkpoint to sequential) changes the computation off the training manifold; positive rescue could be transient architectural perturbation, while a null would not rule out an architecture-induced training path. A clean from-scratch parallel-vs-sequential training comparison is identifiable, but ICML-2026 has already run almost that exact matched comparison. Thus the cleaner the experiment becomes, the more it collapses into a replication/confirmation of the closest owner.

**Verdict:** `DROP / DO NOT REGISTER AS L32`.

**Anti-resurrection:** do not reopen as `parallel residual causes saturation`, `same-layer Attention→MLP steering prevents saturation`, `commutator defect predicts Pythia saturation`, `serializing Pythia rescues late loss`, or another parallel-vs-sequential small-model sweep unless a qualitatively different stable quantity and inference appears.

## O. Diffusion objective as implicit regularization under repeated data — DROP

**Scientific object:** Why do masked-diffusion language models tolerate repeated finite data better than standard autoregressive models? Is random masking itself the load-bearing anti-overfitting mechanism?

**Mother:** 2025 `Diffusion Beats Autoregressive in Data-Constrained Settings` reports that masked diffusion models substantially outperform AR models under repeated-data / compute-rich training and interprets the advantage as implicit data augmentation from varied mask patterns/prediction tasks.

**Direct owners / successors:**
- ICLR 2026 `Dual-objective Language Models: Training Efficiency Without Overfitting` explicitly frames masked diffusion as more resistant to overfitting, sweeps 50 models under different data-repetition levels, and combines AR + masked-diffusion objectives to obtain AR learning speed plus diffusion-style regularization.
- Jun-2026 `Data-Constrained Language Model Pretraining: Improved Regularization and Scaling Laws` directly isolates random masking as **Masked-Input Regularization (MIR)** added to a standard AR objective and shows gains across 72M–1.4B under repeated data.
- The same 2026 work also equalizes weight decay and finds that strong AR regularization can close much of the previously reported AR–diffusion gap, showing that part of the apparent objective advantage was a regularization mismatch rather than a unique diffusion mechanism.
- Jun-2026 `Data Augmentations for Data-Constrained Language Model Pretraining` independently shows token corruption / random replacement and other augmentations delay AR overfitting.

**Reviewer compression:** `Diffusion Beats AR under repeated data + dual-objective overfitting paper + MIR isolates masking + strong weight decay closes gap = objective-as-regularizer mechanism already centralized`.

**Kill reason:** the natural mechanism question—whether random masking / diversified prediction acts as implicit regularization under data reuse—has already been directly isolated and causally exploited. A new mask rate, corruption scheme, or AR/diffusion comparison would be method variation.

**Anti-resurrection:** do not reopen as `why diffusion resists repeated-data overfitting`, `masking is implicit augmentation`, `add a diffusion auxiliary objective to AR`, or `AR vs diffusion data-efficiency gap` unless a distinct unexplained scientific quantity appears.

## P. Formal/synthetic pre-pretraining transfers inductive bias into natural-language learning — DROP current parent

**Scientific object:** Why can a short synthetic/formal pre-pretraining phase make later natural-language pretraining substantially more token-efficient, sometimes outperforming an equal amount of natural text?

**Mother:** ACL 2025 Outstanding `Between Circuits and Chomsky` reports ~33% token savings in a 1B regime, better linguistic generalization, and persistence of attention heads learned during formal-language PPT.

**Successors / direct ownership expansion:**
- ACL 2026 `Language Acquisition Device in Large Language Models` directly challenges the earlier `hierarchical + circuit-theoretically learnable` explanation and identifies **functional landmarks / dependency-resolution accessibility** as a key driver.
- May-2026 `Synthetic Pre-Pre-Training Improves Language Model Robustness to Noisy Pre-Training Data` shows PPT changes later optimization so models gradually downweight corrupted-token interactions, providing another direct mechanistic account.
- Aug-2026 `Logic Before Language` scales PPT to a 100B-token regime and connects it to persistent representational reorganization and compressibility.
- Aug-2026 `Instability of LLM Pre-Pretraining` reports strong setup/seed dependence across natural languages, making the phenotype itself conditional rather than an untouched stable anomaly.

**Reviewer compression:** `ACL-2025 PPT + ACL-2026 dependency-accessibility condition + 2026 optimization/geometry mechanisms + instability study = why/how PPT transfers is already a research line`.

**Kill reason:** the attractive broad question has already fractured into direct explanatory successors. A new formal language, syntax family, or attention-head analysis would be a cell, and the area drifts toward linguistic-inductive-bias experiments that are not current search priority.

**Anti-resurrection:** do not reopen as `why formal data beats equal natural data`, `which formal grammar transfers`, `PPT learns useful circuits`, dependency accessibility, PPT robustness, or seed-sensitive PPT unless a qualitatively new non-linguistic scientific quantity emerges.

## Q. Worse pretraining loss but better downstream fine-tuning because of stronger weight decay — DROP

**Scientific object:** Why can a base LM that is objectively worse by pretraining validation loss become better after downstream fine-tuning?

**Owner:** Feb-2026 `Weight Decay Improves Language Model Plasticity` directly establishes this trade-off across Llama-2/OLMo-2 pretraining regimes and then studies mechanisms: stronger weight decay yields more linearly separable representations, regularizes attention matrices and reduces pretraining overfit. The paper explicitly argues that pretraining-loss-optimal hyperparameters can be plasticity-suboptimal.

**Related prior:** language-model plasticity has been an explicit object since NeurIPS 2023 `Improving Language Plasticity via Pretraining with Active Forgetting`; broader plasticity-loss mechanisms are also mature in continual-learning literature.

**Reviewer compression:** `plasticity pretraining literature + weight-decay paper already owns the counterintuitive trade-off and its first mechanisms`.

**Kill reason:** the anomaly and its natural hyperparameter mechanism are already centralized. Asking which of linear separability / attention regularization / overfit is most causal would be a single-paper mechanism continuation without independent repeated pressure, while generic post-training plasticity is already a recently killed project neighborhood.

**Anti-resurrection:** do not reopen as `worse base, better fine-tune`, pretraining-loss vs adaptability, weight-decay plasticity, or generic `pretraining commits the model too much`.

---

_Continue search from here; append later killed leads in this file or a numbered continuation if the file becomes too large._
