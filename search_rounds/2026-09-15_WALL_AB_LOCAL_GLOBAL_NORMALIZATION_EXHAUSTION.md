# WALL-AB — Local vs Global Normalization / Label Bias

Date: 2026-09-15
Status: EXHAUSTED AS A CURRENT GENERATOR

## Mother question
Does step-wise local normalization impose a structural defect on sequence models that global normalization removes, and if modern high-capacity autoregressive models appear to work well anyway, which premise of the classic label-bias argument has changed?

## Old lineage and crucial qualification
Classic locally normalized structured models exhibit label bias. Andor et al. (ACL 2016) showed a strict expressivity advantage for globally normalized transition models under the incremental scoring assumptions used in their proof.

Goyal, Dyer, and Berg-Kirkpatrick (NAACL 2019) already supplied the key modern qualification: with sufficiently expressive neural parameterizations that can condition on the whole input, locally and globally normalized conditional sequence models can be equivalent in the distributions they represent. Remaining practical advantages of global normalization then depend on search/training conditions rather than a universal representational impossibility.

## Modern direct ownership
- NeurIPS 2022 GNAT directly uses global normalization to address label bias in streaming ASR, where future-input restrictions make the old issue structurally relevant.
- EMNLP Findings 2024 compares locally and globally normalized decoding distributions for text generation.
- EMNLP Findings 2025 develops a thermodynamic account of local-normalization distortion in top-k/nucleus/temperature decoding.

## Verdict
The attractive story "an old theorem says local normalization is defective, yet LLMs work, so what changed?" is not an unowned contradiction. The theorem's assumptions and modern high-capacity qualification were worked out years ago, and the remaining decoding/streaming manifestations are active programs.

## Anti-resurrection
Do not revive as:
- label bias in LLMs;
- globally normalized LLMs;
- energy reranking as a scientific fix for autoregressive local normalization;
- length bias as generic evidence of label bias;
- scaling up the Andor/Goyal comparison;
- local-vs-global decoding quality comparisons.

A reopening would require a distinct old prediction that remains violated after conditioning-capacity and search assumptions are matched.
