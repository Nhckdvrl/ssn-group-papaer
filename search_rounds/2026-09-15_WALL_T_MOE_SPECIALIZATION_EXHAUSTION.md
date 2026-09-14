# 2026-09-15 — WALL-T / Why Does Sparse Mixture-of-Experts Work?

**Mode:** classic load-bearing explanation → modern sparse-MoE regime → specialization/redundancy pressure → decisive routing-factorization owner audit  
**Outcome:** **EXHAUSTED AS A CURRENT TOPIC GENERATOR — NO NEW L-SERIES — NO PILOT**

# 1. Mother scientific problem

> **Why does conditional expert computation improve learning efficiency: because a router discovers functionally distinct subtasks and sends each input to a specialized expert, or because sparse/stable partitioning creates more effective parameter capacity even when the partition itself is arbitrary?**

This question predates modern LLMs.

Jacobs, Jordan, Nowlan & Hinton (1991), *Adaptive Mixtures of Local Experts*, motivate the architecture by interference reduction: when a problem contains distinct subtasks, a gating network allocates cases to separate experts so that weight changes for one subset do not interfere with others. Their learning procedure demonstrably divides a vowel-discrimination problem into appropriate subtasks.

Primary source:
- https://www.cs.toronto.edu/~hinton/absps/jjnh91.pdf

The load-bearing classical story is therefore:

> heterogeneous task → learned allocation → expert specialization → reduced interference / easier local problems.

# 2. Modern regime changes the premise

Shazeer et al. (ICLR 2017) revive MoE primarily as **conditional computation**: increase total parameter capacity dramatically while activating only a small fraction per example.

Source:
- https://arxiv.org/abs/1701.06538

Contemporary sparse-MoE LLMs often discuss specialization, but empirical work repeatedly finds weaker or stranger specialization than the intuitive domain-expert picture:

- ST-MoE and Mixtral analyses find mostly lexical/syntactic routing patterns rather than clean topic/domain experts;
- frozen/random routers can be surprisingly competitive;
- experts can be pruned/merged substantially in some regimes;
- 2026 analyses report domain-invariant core expert coalitions rather than clean domain partitions.

DeepSeekMoE 2024 explicitly motivates architectural changes by reducing redundancy and pursuing stronger expert specialization, showing that specialization remains a load-bearing design story even in modern systems.

# 3. The strongest residual

The best theory-level question was:

> **Does modern sparse-MoE gain require learned input-dependent specialization, or is a persistent but arbitrary partition sufficient because experts co-adapt to whichever subsets they consistently receive?**

A decisive factorization seemed possible with matched total parameters, active parameters, training FLOPs and expert load:

1. learned routing;
2. frozen random routing — arbitrary but persistent input→expert relationship;
3. routing re-randomized every iteration — sparsity/capacity without persistent partition;
4. active-parameter-matched dense control.

This gives interpretable quantities:

- `adaptive-routing surplus = learned − frozen`;
- `persistent-partition surplus = frozen − rerandomized`;
- `sparse-capacity surplus = rerandomized − dense`.

This was initially the strongest descendant because it does not require defining semantic specialization post hoc.

# 4. Direct owners already perform the decisive factorization

## 4.1 Hash Layers — fixed arbitrary routing can match learned routing

Roller et al., NeurIPS 2021, *Hash Layers for Large Sparse Models*, replace learned routing by a fixed hash from token identity to experts and find the method competitive with or better than Switch/BASE routing on language modeling, dialogue and fine-tuning. Random/balanced local hashes work particularly well.

Source:
- https://proceedings.neurips.cc/paper/2021/hash/92bf5e6240737e0326ea59846a83e076-Abstract.html

This already shows that a learned semantic routing policy is not necessary for sparse-model gains.

## 4.2 THOR — stochastic routing can also work

Zuo et al., ICLR 2022, *Taming Sparsely Activated Transformer with Stochastic Experts*, explicitly find that standard gates do not outperform random routing in their translation experiments. THOR randomly selects experts during training and inference, adding consistency regularization to stabilize predictions.

Their pre-THOR analysis also directly removes the trained Switch gate and replaces it with random assignment; performance changes little in that setting.

Source:
- https://arxiv.org/abs/2110.04260

THOR is not a clean pure-sparsity test because its final method adds consistency regularization, but it already occupies the claim that adaptive routing is not universally necessary.

## 4.3 StableMoE — assignment persistence itself matters

Dai et al., ACL 2022, *StableMoE*, identify `routing fluctuation`: the same input changes target expert during training even though only one expert will be used at inference. They argue this harms sample efficiency, learn a cohesive assignment, then freeze it; stable routing improves convergence and performance.

Source:
- https://aclanthology.org/2022.acl-long.489/

This directly elevates **temporal stability of token→expert assignment** to a causal design variable.

## 4.4 The exact frozen-vs-rerandomized experiment already exists

Fan, Messmer & Jaggi (2024), *Towards an Empirical Understanding of MoE Design Choices*, perform essentially the exact discriminating experiment proposed above.

They compare:

- **Learned** router;
- **Frozen** router: router parameters frozen at initialization, so assignment is arbitrary but persistent/adaptable through embeddings;
- **Random** router: router reinitialized randomly at every iteration, destroying persistent assignment.

Results:

- Multilingual token routing: Frozen 9.810, Learned 9.907, Random 11.752 validation perplexity.
- OpenWebText token routing: Frozen 22.687, Learned 22.632, Random 26.879.

Thus learned and frozen routing are nearly indistinguishable, while iteration-wise rerandomization is much worse.

Source:
- https://arxiv.org/abs/2402.13089

This is almost exactly the residual's decisive quantity:

> arbitrary persistent partition retains the gain; fluctuating arbitrary routing does not.

The paper also matches active/total-parameter dense baselines and explicitly frames contemporary MoEs as scaling expressiveness rather than the original 1991 specialization objective.

# 5. Later work makes the program denser, not emptier

- SMoE-Dropout uses a randomly initialized frozen router.
- HyperRouter (EMNLP 2023) explicitly positions itself between fixed-random and trainable routers.
- RMoE (ICLR 2025) improves learned routing by sharing cross-layer routing information.
- current routing-consistency work continues to target fluctuation/stability.
- 2026 studies of random routing, shared expert pools, routing absorption and apparent specialization continue the same question at larger scales.

Representative sources:
- https://aclanthology.org/2023.emnlp-main.351/
- https://proceedings.iclr.cc/paper_files/paper/2025/hash/250a6c6a7a7216f5dec1364e9a93abf4-Abstract-Conference.html

# 6. Reviewer compression

Any current realization compresses to one of:

- `Hash Layers / frozen-router results, scaled up`;
- `StableMoE routing fluctuation + a cleaner random control`;
- `Fan et al. 2024 learned/frozen/rerandomized factorization on larger models`;
- `THOR/SMoE-Dropout revisited without consistency regularization`;
- another semantic-specialization analysis.

The exact scientific inference we wanted — learned routing is not required, but persistent assignment is valuable — is already directly supported by prior work. Scaling it to modern models could be useful engineering evidence but would not be an independent Main-level scientific question under the current standard.

# 7. Decision

**WALL-T exhausted as a current topic generator.**

Keep the durable scientific update:

> **The original MoE specialization story is not the only explanation of modern sparse-expert gains. Stable arbitrary partition/co-adaptation can recover much of learned-routing performance, while routing fluctuation can be harmful.**

But that update is prior work, not our candidate.

Do not regenerate learned-vs-random router comparisons, expert-specialization atlases, larger-scale hash-routing tests, routing-stability ablations, or `why MoE works` by merely combining these known results.

No L-series is created.