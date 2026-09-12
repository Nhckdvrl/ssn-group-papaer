# L22 — Bad Dimensions or Bad Directions?

**Status:** **PILOT-AUTHORIZED — E01 SYMMETRY AUDIT ONLY**  
**Date:** 2026-09-12  
**Target:** ACL / EMNLP / NAACL Main

## Locked research question

> **When modern NLP work says that some text-embedding dimensions are harmful or query-specifically important, are those claims properties of the learned representation itself, or artifacts of the coordinate basis used to write an equivalent embedding geometry?**

Plain version:

> Dense retrieval usually uses cosine similarity or dot products. Multiplying every query and document embedding by the same orthogonal matrix leaves the full retrieval system unchanged, while completely redefining what “dimension 37” means. Which current claims about harmful / important embedding dimensions survive that function-preserving symmetry?

This is **not** a paper whose novelty is “rotations change interpretability.” That fact is classical. The scientific object is the **identifiability of substantive 2024–2026 NLP conclusions about embedding dimensions**.

## Why the question is live

Independent literature lines now make coordinate-level claims scientifically consequential:

1. **Random dimension removal:** Takeshita et al. (EMNLP 2025 Main / People’s Choice) report little degradation after removing up to half of embedding dimensions and explain the effect partly through many distributed *degrading dimensions*.
2. **Query-specific dimension importance:** DIME (SIGIR 2024), its SIGIR 2025 reproducibility/formal analysis, and 2026 adaptive-dimension work explicitly select individual coordinates as query-specific retrieval units.
3. **Redundancy / intrinsic dimension:** Tsukagoshi & Sasano (Findings ACL 2025) show strong compressibility and relate it to largely basis-invariant geometric quantities such as intrinsic dimensionality/isotropy.
4. **Classical symmetry warning:** word-embedding and neural-interpretability work already shows that single-coordinate interpretation can be redistributed by orthogonal rotation while preserving global geometry.
5. **Geometric null:** random-projection / Johnson–Lindenstrauss results show that high-dimensional retrieval geometry can remain useful under severe dimension reduction without implying a privileged native coordinate system.

Fresh source-level search did **not** find a dense-text-retrieval paper that applies a random orthogonal basis sanity check to modern DIME / harmful-dimension claims.

## Exact symmetry

For embeddings `x,y` and orthogonal `Q`:

```text
(Qx)^T(Qy) = x^T y
||Qx|| = ||x||
cos(Qx,Qy) = cos(x,y)
||Qx-Qy||_2 = ||x-y||_2
```

Thus simultaneous rotation preserves the full retrieval function exactly.

But deleting coordinates after rotation corresponds in the original basis to

```text
Q^T diag(m) Q
```

which is generally a dense projection, not deletion of the original coordinates.

## Competing accounts

### A — coordinate artifact / geometric account

Native axes are not privileged. Harmful/important coordinate identities and coordinate-level explanations vary strongly across behavior-equivalent rotations.

Scientific consequence:

> the identifiable objects are directions/subspaces or regularization effects, not named dimensions.

### B — privileged learned basis

Native coordinates systematically yield sparser, stronger or more transferable importance/degradation effects than random rotations, despite identical full-dimensional retrieval.

Scientific consequence:

> training has produced a privileged coordinate system not required by the downstream similarity function, giving coordinate-level methods a substantive basis.

### C — basis-stable aggregate, basis-unstable identities

Exact dimensions rotate away, but the amount/distribution of harmful/helpful directional mass remains stable.

Scientific consequence:

> the phenomenon is real, but “dimension” is too literal; a basis-invariant directional/subspace formulation is required.

All three answer the same RQ. Do not rename the paper after seeing the result.

## Data / workload

Natural external gold already exists:
- BEIR / TREC-style qrels used by dense retrieval work;
- MTEB labels for secondary classification checks.

E01 requires no training, RL or new annotation. Encode/cache once, then use offline linear algebra and reranking.

## E01 — authorized bounded pilot

### E01-A — reproduce the owned phenomena

On one standard dense retriever and one prompt-based embedding model:
- full-dimensional retrieval;
- random 25% / 50% coordinate deletion;
- native-basis single-coordinate deletion effects;
- one reproducible DIME/oracle-DIME style coordinate-selection result.

If these cannot be reproduced, stop and audit implementation rather than switching models until one works.

### E01-B — exact equivalence check

Sample preregistered Haar-random orthogonal matrices `Q` and verify that full-dimensional similarities, rankings and retrieval metrics are unchanged up to floating-point tolerance.

Failure is an implementation bug, not a scientific result.

### E01-C — symmetry audit

For each basis, rerun:
- single-coordinate deletion effects;
- harmful/helpful coordinate ranking;
- random 50% coordinate removal;
- selective removal of the most harmful coordinates;
- one DIME/oracle-DIME style selector.

Primary questions:
1. Does the **native basis** stand out relative to the distribution of random rotations?
2. Do published substantive conclusions survive even when coordinate identities do not?
3. Are aggregate effects better predicted by basis-invariant geometry than by native coordinate attribution?

### E01-D — positive controls

Compare against:
- random orthogonal / Gaussian subspace projections;
- spectral / intrinsic-dimensionality quantities;
- retrieval margins / neighborhood preservation where feasible;
- a Matryoshka-style representation as a positive control where coordinate order is intentionally privileged.

## Predeclared substantive-change gate

Changing only coordinate names is **not enough**.

A result counts as substantive only if at least one preregistered paper-level conclusion changes relative to random rotations, such as:

- the **performance gain** from removing estimated harmful coordinates: native-basis gain lies outside the central 95% of the preregistered Haar-rotation distribution;
- the **DIME/oracle-DIME gain at a fixed coordinate budget**: native-basis gain lies outside the central 95% of rotated-basis results, or the original “query-specific important coordinates” interpretation fails because equally strong coordinate sets appear under arbitrary rotations;
- the claimed **prevalence/sign structure of degrading dimensions** changes enough that the qualitative explanation “many native dimensions are individually harmful and their removal explains truncation robustness” is not preserved.

Exact thresholds and metrics must be frozen in the E01 config before model outputs are inspected. No post-hoc threshold tuning.

## E01 decision

**KEEP / RE-SELECT** if either:
- harmless rotations materially change substantive modern coordinate-level conclusions; or
- the native basis reproducibly stands out against random rotations, revealing an unexpected privileged-axis structure.

**KILL** if:
- only coordinate identities change while all substantive gains/conclusions remain effectively the same;
- the result reduces to the classical statement that coordinate attribution is basis-dependent;
- effects are tiny and no principled model/task boundary emerges.

Do not rescue a null result by inventing a new interpretability metric.

## Reviewer compression test

Strongest attack:

> “Old rotation/basis invariance, applied to a new embedding paper.”

Required answer:

> The symmetry fact is conceded. The contribution is a direct identifiability audit of a current NLP literature that draws substantive retrieval/compression conclusions from coordinate-level pruning and importance, even though the deployed full-dimensional function is orthogonally invariant. Either a failure or a surprising survival of those claims changes how that literature should be interpreted.

If E01 cannot support this stronger answer, kill.

## Identity fence

L22 is not:
- old L08 compression/readout continued under a new name;
- generic neuron/feature basis dependence;
- another random-projection paper;
- a new embedding compression method.

Historical L08 code/results may be inherited as evidence or infrastructure only; they confer no novelty or authorization.

## Current verdict

```yaml
natural_question: PASS
multi_line_support: PASS
anti_resurrection: PASS_NO_MATCH_TO_L08_OR_INTERPRETABILITY_LEDGER
exact_external_owner: NOT_FOUND_AFTER_FRESH_SEARCH
new_estimand: PASS_MODERN_NLP_CONCLUSION_IDENTIFIABILITY_UNDER_FUNCTION_PRESERVING_SYMMETRY
data_gold: PASS_EXISTING_QRELS_LABELS
pilot_cost: VERY_LOW_OFFLINE_LINEAR_ALGEBRA
outcome_robustness: PASS_A_B_C
reviewer_compression_risk: HIGH_BUT_TESTABLE
full_study_burden: LOW_TO_MODERATE
pilot: E01_ONLY
verdict: PILOT_AUTHORIZED
```

## Key references

- Takeshita et al. 2025, EMNLP Main / People’s Choice: *Randomly Removing 50% of Dimensions in Text Embeddings has Minimal Impact on Retrieval and Classification Tasks*.
- Tsukagoshi & Sasano 2025, Findings ACL: *Redundancy, Isotropy, and Intrinsic Dimensionality of Prompt-based Text Embeddings*.
- Faggioli et al. 2024, SIGIR: *Dimension Importance Estimation for Dense Information Retrieval*.
- Campagnano et al. 2025, SIGIR: *Unveiling DIME: Reproducibility, Generalizability, and Formal Analysis of Dimension Importance Estimation for Dense Retrieval*.
- Wu et al. 2026, ACL: *Learning to Select: Query-Aware Adaptive Dimension Selection for Dense Retrieval*.
- Classical rotation/basis-dependence work is a conceded theoretical neighbor, not novelty.
