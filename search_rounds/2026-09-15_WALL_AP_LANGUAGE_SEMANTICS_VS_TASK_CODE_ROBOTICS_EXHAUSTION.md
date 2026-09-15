# WALL-AP — Language semantics vs arbitrary task codes in robot policies

Date: 2026-09-15
Status: EXHAUSTED / DIRECT ABLATION TRADITION EXISTS

## Mother question
Language-conditioned robot/VLA policies are often said to gain semantic/compositional generalization from natural language. But language could merely serve as a high-dimensional task identifier. Would an arbitrary bijective task code work equally well if task identity, data frequency, capacity, and behavior supervision were held fixed?

## Direct-owner audit
This distinction is already explicitly tested in robot learning.

- RT-H (Belkhale et al., 2024) argues that language structure permits data sharing across semantically related low-level motions. Its RT-H-OneHot ablation replaces each language motion with an integer/one-hot class label while preserving the underlying motion categories; performance drops substantially. RT-H-Cluster additionally uses action-derived K-means clusters, separating the benefit of hierarchy from the benefit of linguistic structure.
- BC-Z (CoRL 2021) explicitly studies whether pretrained language representations transfer compositional generalization to real robot policies on held-out task/object combinations, claiming pretrained language embeddings confer generalization beyond a closed-set task interface.
- LIV compares pretrained language-image goal representations against one-hot goal conditioning in language-conditioned imitation settings.
- Recent VLA work continues to compare semantic language conditioning with task-ID embeddings.

## Verdict
No L-series. Natural-language semantics versus arbitrary task identity is already a standard causal ablation axis in language-conditioned robotics.

## Anti-resurrection
Do not revive as:
- natural language vs task IDs / integer labels / random embeddings;
- scrambled instructions with a fixed bijection;
- language semantics as a task-conditioner generalization test;
- one-hot versus pretrained text encoder on newer VLAs;
- language-motion hierarchy versus arbitrary motion classes without a genuinely different old theory.
