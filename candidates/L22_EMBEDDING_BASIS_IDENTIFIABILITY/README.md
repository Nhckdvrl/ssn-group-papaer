# L22 — Bad Dimensions or Bad Directions?

**Status:** **SERIOUS / PRE-PILOT — NO COMPUTE AUTHORIZED**  
**Date:** 2026-09-12  
**Target:** ACL / EMNLP / NAACL Main

## Locked research question

> **When modern NLP work says that some text-embedding dimensions are harmful or query-specifically important, are those claims properties of the learned representation itself, or artifacts of the arbitrary coordinate basis used to write the same embedding geometry?**

Plain version:

> Dense text retrieval usually depends on cosine similarity or dot products. If every query and document embedding is multiplied by the same orthogonal matrix, full-dimensional retrieval is unchanged exactly. But the meaning of “dimension 37” changes completely. If published conclusions about harmful / important dimensions disappear or reverse under such behavior-preserving rotations, then the scientific object is not an identifiable dimension; it is a direction, subspace, or regularization effect.

The paper is **not** “rotation changes interpretability,” which is old. The modern scientific object is:

> **which current NLP claims about text-embedding dimensions survive the symmetries of the function the embedding is used to compute?**

## Why this question is live

Several independent lines now collide without already resolving this question.

1. **Random dimension removal is surprisingly robust.** Takeshita et al. (EMNLP 2025 Main, People’s Choice) find that randomly removing up to 50% of dimensions from six modern text encoders causes only minor degradation across retrieval and classification. Their proposed explanation is that many uniformly distributed individual dimensions are *degrading*: removing them can improve performance.
2. **Dense retrieval increasingly treats coordinates as query-specific units.** DIME (SIGIR 2024) and its 2025–2026 follow-ups assign importance to individual embedding coordinates and select query-specific coordinate subsets; newer supervised methods likewise learn per-dimension importance distributions.
3. **Redundancy / intrinsic-dimensionality work gives a different, largely basis-invariant explanation.** Tsukagoshi & Sasano (Findings ACL 2025) show very strong post-hoc compressibility of prompt-based text embeddings and relate it to intrinsic dimensionality and isotropy, especially for classification and clustering.
4. **The basis problem is classically real but has not been applied to these modern claims.** Earlier word-embedding / representation-interpretability work shows that orthogonal transformations can redistribute single-dimension interpretability while preserving embedding structure; neural-network interpretability work similarly warns that neuron-level explanations can depend on basis.
5. **High-dimensional retrieval has a basis-invariant null explanation.** Random-projection / Johnson–Lindenstrauss theory can preserve pairwise geometry and ranking with far fewer dimensions under suitable margins. Thus random coordinate truncation robustness does not by itself imply that positive and negative coordinate contributions cancel in a scientifically privileged basis.
6. **Recent quantization work shows the opposite outcome is plausible.** Coordinate heterogeneity can sometimes be functionally useful, while random rotation can either destroy exploitable axis structure or improve quantization by isotropizing it. Therefore the native text-embedding basis may or may not be privileged; this is an empirical question, not a mathematical tautology.

## Symmetry / identifiability fact

For embeddings `x,y` and any orthogonal matrix `Q`:

```text
(Qx)^T(Qy) = x^T y
||Qx|| = ||x||
cos(Qx,Qy) = cos(x,y)
||Qx-Qy||_2 = ||x-y||_2
```

Therefore a simultaneous orthogonal rotation of all query/document embeddings leaves full-dimensional dot-product / cosine retrieval exactly unchanged.

But a coordinate mask `M = diag(m)` after rotation corresponds in the original basis to

```text
Q^T M Q
```

which is generally a dense projector rather than deletion of the original coordinates.

So the full retrieval function is basis-invariant while “dimension importance” need not be.

## Nearest neighbors and ownership fence

### Takeshita et al. 2025 — random dimension removal

Owns:
- the robust 50%-removal phenomenon;
- individual-coordinate attribution in the native basis;
- the claim that many uniformly distributed dimensions are degrading;
- PCA and standard truncation comparisons.

Does **not** test whether the degrading-dimension explanation survives behavior-preserving changes of basis.

### DIME / RDIME / adaptive dimension selection

Owns:
- query-specific coordinate importance;
- coordinate pruning / masking as a retrieval improvement;
- formalizations of coordinate selection as denoising / risk minimization.

Does **not** establish that the native coordinate system is privileged, or test whether the same scientific conclusions survive orthogonal reparameterization.

### Tsukagoshi & Sasano 2025

Owns:
- strong compressibility of prompt-based embeddings;
- intrinsic dimensionality / isotropy analyses across tasks.

Important positive-control role:

> intrinsic dimensionality, singular spectrum and many isotropy quantities are much closer to basis-invariant objects. L22 should not claim that all embedding analyses are invalid; it asks which conclusions are identifiable and which are coordinate artifacts.

### Classical rotation / basis-dependence work

Owns:
- the general fact that single-coordinate / single-neuron interpretation can change under orthogonal rotation;
- methods that rotate embeddings to improve interpretability while preserving global geometry.

Does **not** own the 2024–2026 NLP consequence:

> whether modern claims about harmful dimensions, query-specific important dimensions, and the mechanism behind dimension-removal robustness survive the symmetries of modern dense text retrieval.

Identity fence:

> **L22 lives at modern NLP conclusion identifiability under a function-preserving symmetry, not at the generic statement that coordinates depend on basis.**

If the paper becomes only “orthogonal rotations change per-dimension attribution,” kill it as an old interpretability sanity check.

## Competing accounts

### A — coordinate artifact / geometric account

The native axes have little privileged scientific status. Published coordinate identities and coordinate-level harmfulness change strongly under rotations that leave full embedding behavior exactly unchanged.

Predictions:
- identities/rankings of “degrading dimensions” are unstable across harmless rotations;
- selective removal of native-basis bad coordinates is not uniquely stronger than appropriately matched subspace operations in rotated bases;
- DIME-style gains can be recovered in many bases, but the selected coordinates do not correspond across them;
- random-removal curves are largely explained by low intrinsic dimension / margin-preserving random-subspace geometry.

Interpretation:

> the real object is harmful/helpful **directions or subspaces**, not named embedding dimensions; coordinate-level explanations overstate what the representation identifies.

### B — privileged learned basis

Despite a rotation-invariant downstream geometry, training produces unusually useful axis alignment in the native basis.

Predictions:
- native-basis harmful / important-coordinate interventions systematically outperform the same procedures after Haar-random rotations;
- coordinate importance is more sparse/stable/transferable in the native basis;
- this advantage replicates across models trained with similar embedding objectives and is not explained only by variance heterogeneity.

Interpretation:

> modern text encoders spontaneously learn a privileged coordinate system, giving a substantive foundation to coordinate-level dimension selection. Explaining how this basis emerges becomes a new representation-learning question.

### C — basis-stable aggregate structure, basis-unstable identities

The exact dimensions are arbitrary, but every basis exposes a similar *amount* of harmful/helpful directional mass.

Predictions:
- dimension identities rotate away;
- distributions of deletion effects remain stable;
- basis-invariant subspace / spectral quantities predict the aggregate phenomenon.

Interpretation:

> current “dimension” language is too literal, but the underlying phenomenon is real and admits a cleaner basis-invariant formulation.

All three outcomes answer the same RQ. Do not rename the project after seeing the result.

## Data / gold / workload

No author-defined semantic gold is required.

Primary external gold:
- standard retrieval qrels (e.g. BEIR / TREC-style datasets used by DIME work);
- MTEB classification labels as a secondary domain;
- published model embeddings / reproducible embedding encoders.

The decisive manipulation is deterministic linear algebra. No RL, fine-tuning or pretraining is required for the first study.

Expected cost:

> encode once, cache embeddings, apply orthogonal transforms/masks offline, recompute similarities/rankings.

This is intentionally cheap relative to the project’s recent RL/training candidates.

## Proposed bounded E01 — NOT YET AUTHORIZED

E01 should be authorized only after the final source-level audit below is closed.

### E01-A — reproduction

On one standard dense retriever + one prompt-based embedding model:
- reproduce full-dimensional retrieval;
- reproduce random 25/50% deletion curves;
- reproduce a native-basis coordinate attribution / DIME-style improvement.

### E01-B — exact equivalence sanity check

Sample several Haar-random orthogonal matrices `Q`.

For every `Q` verify numerically that full-space:
- dot products / cosine similarities;
- ranking;
- retrieval metric

are unchanged up to floating-point tolerance.

Failure here is an implementation bug, not a result.

### E01-C — symmetry audit

In each rotated basis re-run:
- single-coordinate deletion effects;
- ranking of harmful/helpful coordinates;
- random 50% coordinate removal;
- selective removal of native/rotated “bad” coordinates;
- one DIME/oracle-DIME style coordinate-selection procedure.

Primary quantities:
- stability of scientific conclusions across behavior-equivalent bases;
- native-basis advantage over the distribution of random rotations;
- whether aggregate deletion-effect distributions are basis-stable even when coordinate identities are not.

### E01-D — geometric positive controls

Compare against:
- random subspace / Gaussian or orthogonal projection;
- intrinsic-dimensionality / spectral quantities;
- retrieval margin or neighborhood-preservation diagnostics where feasible.

Matryoshka-style models may serve as a **positive control for an intentionally privileged coordinate order**, not as the primary model family.

## E01 gate

### Keep condition 1 — substantive basis dependence

If a harmless rotation leaves the base system identical but materially changes one or more published substantive conclusions — e.g. whether many coordinates are harmful, how much selective coordinate removal helps, or whether DIME exposes stable query-specific components — then:

> **KEEP / RE-SELECT.**

The paper must quantify how much of the modern dimension literature is basis-identifiable, not stop at one model/dataset.

### Keep condition 2 — privileged native basis

If the native basis consistently stands out against random rotations on preregistered metrics while base behavior is exactly invariant:

> **KEEP / RE-SELECT.**

This is a stronger scientific result than a simple invariance critique: training has created axis-aligned structure not required by the downstream function.

### Kill condition

Kill if:
- only coordinate identities change but all substantive conclusions/gains stay effectively identical;
- the result reduces to a generic old “rotations change interpretability” demonstration;
- DIME / degrading-dimension claims are explicitly basis-conditional already and no broader scientific conclusion changes;
- practical differences are tiny and no model/task boundary yields a principled account.

Do not rescue by inventing a new interpretability metric after a null substantive result.

## Main-level development path if E01 survives

### C1 — identifiability audit

Establish which current claims about text-embedding dimensions are invariant / non-invariant under function-preserving rotations across models/tasks.

### C2 — why some models have privileged axes

Characterize boundaries across:
- ordinary contrastive embeddings;
- prompt-based embeddings;
- Matryoshka / explicitly nested representations;
- retrieval vs classification / STS.

Use intrinsic dimension, spectrum, coordinate heterogeneity and training objective as candidate explanatory factors; do not overclaim mechanism from correlation.

### C3 — reformulate the object

Show whether coordinate methods should be interpreted as:
- basis-specific regularization;
- directional/subspace selection;
- or genuinely learned axis-aligned semantics.

A lightweight basis-invariant or basis-aware diagnostic may be proposed only after C1/C2 establish the scientific need.

## Reviewer compression test

Strongest attack:

> “This is Network Dissection / old word-embedding rotation invariance applied to a new embedding paper.”

Required answer:

> The classical symmetry fact is conceded, not claimed as novelty. The contribution is that a substantial 2024–2026 NLP literature now draws substantive conclusions from coordinate-level pruning/importance while the deployed dense-retrieval function is orthogonally invariant. L22 tests whether those *current NLP conclusions* survive function-preserving reparameterizations, and whether the native text-embedding basis is empirically privileged. Either answer changes how dimension-pruning results should be interpreted.

If experiments cannot support that stronger answer, kill.

## Current blockers before pilot authorization

1. Finish source-level check for any text-embedding / dense-retrieval paper that already runs a random-rotation basis sanity test on DIME / harmful-dimension claims.
2. Verify at least one modern DIME implementation can be reproduced without major infrastructure reconstruction.
3. Freeze the distinction between **basis-invariant scientific quantities** (full similarity geometry, spectrum/intrinsic dimension) and **basis-dependent quantities** (coordinate attribution/masks) before looking at results.
4. Predeclare what magnitude counts as a *substantive conclusion change* rather than merely different coordinate labels.

## Current verdict

```yaml
natural_question: PASS
simple_example: PASS
multi_line_support: PASS
anti_resurrection: PASS_NO_MATCH_IN_MAIN_OR_INTERPRETABILITY_LEDGER
external_exact_owner: NOT_FOUND_YET_STRONG_GENERAL_NEIGHBORS
new_estimand: PASS_MODERN_NLP_CONCLUSION_IDENTIFIABILITY_UNDER_FUNCTION_PRESERVING_SYMMETRY
data_gold: PASS_EXISTING_QRELS_LABELS
pilot_cost: VERY_LOW_OFFLINE_LINEAR_ALGEBRA
outcome_robustness: PASS_A_B_C
reviewer_compression_risk: HIGH_BUT_EXPLICITLY_FENCED
full_study_burden: LOW_TO_MODERATE
pilot: NOT_AUTHORIZED
verdict: SERIOUS_PRE_PILOT
```

## High-confidence references

- Takeshita et al. 2025, EMNLP Main / People’s Choice: *Randomly Removing 50% of Dimensions in Text Embeddings has Minimal Impact on Retrieval and Classification Tasks*.
- Tsukagoshi & Sasano 2025, Findings ACL: *Redundancy, Isotropy, and Intrinsic Dimensionality of Prompt-based Text Embeddings*.
- Faggioli et al. 2024, SIGIR: *Dimension Importance Estimation for Dense Information Retrieval* and later DIME follow-ups.
- Campagnano et al. 2025, SIGIR: *Unveiling DIME: Reproducibility, Generalizability, and Formal Analysis of Dimension Importance Estimation for Dense Retrieval*.
- Wu et al. 2026, ACL: *Learning to Select: Query-Aware Adaptive Dimension Selection for Dense Retrieval*.
- Luan et al. 2021, TACL: *Sparse, Dense, and Attentional Representations for Text Retrieval* (random-projection / JL retrieval analysis).
- Classical rotation / embedding-interpretability work is treated as a conceded theoretical neighbor, not novelty.
