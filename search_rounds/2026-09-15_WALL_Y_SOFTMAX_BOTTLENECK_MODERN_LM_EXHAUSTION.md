# WALL-Y — Softmax bottleneck in modern language models

Date: 2026-09-15
Status: EXHAUSTED AS STANDALONE GENERATOR

## Mother question
The standard linear LM head followed by softmax constrains the rank/geometry of contextual next-token distributions. Modern LLMs still use essentially this head. Is the classic softmax bottleneck non-binding at modern scale, or is a large hidden network forced through a fundamentally inadequate output family?

## Lineage
Yang et al. (ICLR 2018) formulated language modeling as matrix factorization and proved the softmax bottleneck. NeurIPS/ICML 2018–2019 developed higher-rank alternatives such as MoS, Mixtape, SigSoftmax, and nonlinear heads. ACL 2022 showed multi-modal next-word distributions remain unrepresentable by a single hidden-state softmax in practical GPT-style models.

## Modern direct owners
Godey et al. (2024) directly study modern LM saturation via the softmax bottleneck, measuring mismatch between target contextual-distribution rank and hidden dimension and showing saturation/degenerate latent representations for smaller hidden dimensions.

Godey & Artzi (2026), Lost in Backpropagation: The LM Head is a Gradient Bottleneck, further argues that the low-dimensional LM head is both an expressivity and optimization bottleneck; they report severe suppression of gradient components and controlled learning failures.

## Verdict
The old theorem is genuinely relevant to modern LMs, but the exact modern-regime question is already a live direct program. Do not generate an L-series by scaling the same effective-rank test or proposing another output head.

## Anti-resurrection
No:
- effective-rank-vs-model-size survey;
- 'does softmax bottleneck still matter for LLMs?';
- new LM head as primary scientific contribution;
- hidden dimension/vocabulary-size sweep;
- gradient compression through LM head as a supposedly new mechanism.
