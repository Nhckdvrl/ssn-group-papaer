# 可解释性与表征分析（Interpretability / representation）

**范围：** 机制可解释性与表征分析：SAE/转码器/电路、探针与干预、steering、模型差分、跨模型表征、训练中的机制形成。
**更新：** 2026-09-30（按题材重组；内容从 `KEY_PAPERS.md`、`TERRITORY_BANK.md`、`deep/` 迁移或索引而来，未改写）。

## 1. 热度（`tools/venue_corpus`，顶会 main 接收数；ICLR 括号内为切片接收率 / 全会基准）

正则：`mechanistic interpretab|sparse auto[- ]?encoders?|\bSAEs?\b|steering vectors?|activation steering|linear probes?`（粗筛，数字是量级参考）

| NeurIPS2024 | ICLR2025 | ICML2025 | NeurIPS2025 | ICLR2026 | ICML2026 | ACL2025 | EMNLP2025 | ACL2026 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 10 | 33（34% / 基准 32%） | 40 | 50 | 89（31% / 基准 27%） | 105 | 16 | 31 | 39 |

## 2. Territory 笔记（原 `TERRITORY_BANK.md`）

### T06 — Mechanistic interpretability / model science

**Why keep inhabiting it**

The frontier has moved beyond “find another neuron/head”. By 2025–2026, major pressure sits on the **validity of mechanistic evidence itself**: what the causal mediator is, whether an explanation is identified or merely one convenient decomposition, whether interventions reflect natural computation, and whether an interpretation provides actionable information beyond cheaper behavioral/logit baselines.

**Recurring assumptions worth auditing**

- neuron / SAE feature / circuit edge is the right causal unit;
- readable or linearly decodable representation = naturally used representation;
- higher IIA / attribution score = better mechanistic explanation;
- a more expressive alignment map is always better;
- one SAE dictionary is a canonical feature inventory;
- structurally different circuits imply different mechanisms;
- successful steering proves the steered direction is the natural mechanism;
- a narrow model organism is representative of broad post-training;
- internal interpretability has comparative advantage over black-box/logit/activation-difference baselines.

**Natural observations**

- mediator complexity vs held-out intervention generalization;
- negative-control success/failure (random/wrong-task models, shuffled variables);
- cross-seed / cross-method explanation stability;
- structural difference vs functional interchangeability;
- intervention naturality / off-manifold effects;
- proxy metric vs practical/actionable outcome;
- internal model-diff signals vs simple output/logit differences;
- explanation transfer across prompts, distributions, checkpoints, and model pairs.

**Baseline / observation first**

Start from MIB / causal abstraction / SAEBench / established model-diffing harnesses. Reproduce strong simple baselines and negative controls before proposing a new mediator, SAE, circuit algorithm, or steering method.

**High-risk failure modes**

- behavior anomaly → synthetic task → probe/SAE/DAS → “mechanism”;
- another SAE/probe/lens without changing a scientific inference;
- using only one toy or narrow fine-tune and generalizing to LLM mechanisms;
- treating a flexible analysis pipeline's fit as evidence that the model itself implements the proposed abstraction.

**Deep map:** `INTERPRETABILITY_LANDSCAPE_2026.md`（本目录）  
**Tool map:** `INTERPRETABILITY_TOOLING_2026.md`（本目录）  
**Anchors:** MI01–MI05 plus MIB, SAEBench, causal abstraction, Non-Linear Representation Dilemma, 2026 SAE consistency / model-diffing work.

## 3. 关键论文与本目录文件

- [`INTERPRETABILITY_LANDSCAPE_2026.md`](INTERPRETABILITY_LANDSCAPE_2026.md)
- [`INTERPRETABILITY_TOOLING_2026.md`](INTERPRETABILITY_TOOLING_2026.md)
- **[MODEL_DIFFING_MEASUREMENT.md](MODEL_DIFFING_MEASUREMENT.md)** — 将原 desk-only workbench 的实验设计、强基线、证据效度与研究谱系凝练成可复用的知识卡（2026-10-09）。
- [`KEY_PAPERS.md`](KEY_PAPERS.md)

## 4. 深读材料：`library/deep/` 中与本题材相关的章节

- [`deep/academic/GENEALOGIES_01.md`](../../deep/academic/GENEALOGIES_01.md)
  - LINEAGE 3 — ICL Mechanism：一个极拥挤问题如何连续改变 explanatory primitive
- [`deep/academic/GENEALOGIES_04.md`](../../deep/academic/GENEALOGIES_04.md)
  - LINEAGE 17 — CoT Faithfulness：从“CoT看起来合理吗”到“到底要用什么 intervention定义 faithful”
- [`deep/industry/FRONTIER_DEEP_DIVE.md`](../../deep/industry/FRONTIER_DEEP_DIVE.md)
  - 3. OpenAI — GPT-6 Astra: CoT monitorability changed premise

## 5. 博客 / 报告（`../../sources/BLOGS_REPORTS.md`）

- B03 — Anthropic — The engineering challenges of scaling interpretability
- B04 — Anthropic Interpretability research index
- B05 — Anthropic — Open-sourcing circuit-tracing tools

## 6. 最新 arXiv 入口

- [ruizheliUOA/Awesome-Interpretability-in-Large-Language-Models](https://github.com/ruizheliUOA/Awesome-Interpretability-in-Large-Language-Models)
- [cooperleong00/Awesome-LLM-Interpretability](https://github.com/cooperleong00/Awesome-LLM-Interpretability)
- [zepingyu0512/awesome-SAE](https://github.com/zepingyu0512/awesome-SAE)
- [itsqyh/Awesome-LMMs-Mechanistic-Interpretability](https://github.com/itsqyh/Awesome-LMMs-Mechanistic-Interpretability)
- 全题材通用：`../../sources/AWESOME_LISTS.md`（awesome 列表、daily-arXiv 镜像、PaperNotes、spotlight 归档）

## 7. 本仓库相关 workbench / 历史

- **已终止的实证项目**：[mechanism-population-dynamics](../../../workbench/mechanism-population-dynamics)（2026-10-11 CLOSED；[科研结项](../../../workbench/mechanism-population-dynamics/heads/README.md)）。仅为知识与数据资产入口，不代表仍有活跃研究计划。
- **模型差分独立 workbench 已撤销**；不再将此题材误标为正在开展的项目。见 [模型差分知识卡](MODEL_DIFFING_MEASUREMENT.md)。
- [Shape/OLMo 历史架构/表征混杂审计](../architecture-memory/SHAPE_OLMO_CLOSEOUT.md)（旧 workbench 已删除）

## 论文卡（papers/，2026-11-25 为三个候选题精读全文写成）

每张卡都读了正文和附录；一篇论文只有一张卡。

### 变量绑定与实体追踪（Transformer）

- [How do Language Models Bind Entities in Context?](papers/2310.17191_feng-steinhardt-binding-ids.md)
- [Cell-Based Representation of Relational Binding in Language Models](papers/2604.19052_dai-cell-based-binding.md)
- [A retrieval conditioned rebinding circuit for dynamic entity tracking in large language models](papers/2606.08644_oh-demberg-rebinding-circuit.md)
- [How can embedding models bind concepts?](papers/2605.31503_uselis-embedding-binding.md)
- [Mixing Mechanisms: How Language Models Retrieve Bound Entities In-Context](papers/2510.06182_gur-arieh-mixing-mechanisms.md)
- [Do Language Models Track Entities Across State Changes?](papers/2605.30233_tang-entity-tracking-state-changes.md)
- [How Do Transformers Learn Variable Binding in Symbolic Programs?](papers/2505.20896_wu-variable-binding-symbolic-programs.md)

### 循环 / SSM / 混合架构里的记忆与检索

- [Mechanistic evaluation of Transformers and state space models](papers/2505.15105_arora-mechanistic-eval-ssm.md)
- [The Illusion of State in State-Space Models](papers/2404.08819_illusion-of-state-ssm.md)
- [Comparing Transformers and Hybrid Models at the Token Level](papers/2606.20936_transformer-vs-hybrid-token-level.md)
- [How Linear Attention Remembers](papers/2609.33093_how-linear-attention-remembers.md)
- [What Attention Recalls and Recurrence Controls in Hybrid Language Models](papers/2609.04434_attention-recalls-recurrence-controls.md)
- [Who Asks, Who Answers: Linear Attention Builds the Query in Hybrid Language Models](papers/2611.01909_linear-attention-builds-query.md)
- [On the Recall Scaling Laws in Mamba: A Theoretical and Mechanistic Study via Hashing](papers/2609.07681_mamba-recall-scaling-hashing.md)

### 覆写、前摄干扰与状态更新（11-25 补读）

- [Unable to Forget: Proactive Interference Reveals Working Memory Limits in LLMs Beyond Context Length](papers/2506.08184_wang-sun-proactive-interference.md)
- [When Context Changes: Understanding Update Failures in LLMs](papers/2609.38866_guo-stale-binding-cicm.md)
- [LLMs Remember First, Forget Last: Dual-Process Interference in Large Language Models](papers/2603.00270_chattaraj-ri-pi-dual-process.md)
- [A Fine-Grained Hierarchy and Benchmark for State Tracking in Language Models](papers/2611.03094_petty-statebench-hierarchy.md)
- [Gated Delta Networks: Improving Mamba2 with Delta Rule](papers/2412.06464_gated-deltanet.md)
- [Parallelizing Linear Transformers with the Delta Rule over Sequence Length](papers/2406.06484_deltanet-parallel.md)
- [Anatomy of Associative Recall in Fixed-State Recurrences: A Matched-State Decomposition, an Interference Wall, and a Curriculum That Breaks It](papers/2609.16183_boesch-recall-anatomy-interference-wall.md)
- [RWKV-7 "Goose" with Expressive Dynamic State Evolution](papers/2503.14456_rwkv7-goose.md)
- [Linear Transformers Are Secretly Fast Weight Programmers](papers/2102.11174_schlag-fast-weight-programmers.md)

### 表征流形与几何

- [When Models Manipulate Manifolds: The Geometry of a Counting Task](papers/2601.04480_gurnee-manipulate-manifolds.md)
- [Geometry of Ordinal Representations in Language Models](papers/2607.04167_bassi-ordinal-geometry.md)
- [The Shape of Beliefs: Geometry, Dynamics, and Interventions along Representation Manifolds of Language Models' Posteriors](papers/2602.02315_sarfati-shape-of-beliefs.md)
- [PersonaManifold: Revealing and Exploiting Curved Geometry in LLM Persona Representations](papers/2609.34571_personamanifold.md)
- [Manifold Steering Reveals the Shared Geometry of Neural Network Representation and Behavior](papers/2605.05115_wurgaft-manifold-steering.md)
- [Linear Probes to Bayesian Manifolds: Geometry of Arithmetic in Large Language Models](papers/2611.12998_kumar-bayesian-manifolds-arithmetic.md)
- [Symmetry in Language Statistics Shapes the Geometry of Model Representations](papers/2602.15029_karkada-symmetry-geometry.md)
- [Not All Language Model Features Are One-Dimensionally Linear](papers/2405.14860_not-all-features-one-dim-linear.md)
- [Language Models Use Trigonometry to Do Addition](papers/2502.00873_trigonometry-addition-helix.md)
- [The Origins of Representation Manifolds in Large Language Models](papers/2505.18235_origins-representation-manifolds.md)
- [Spokes, not a Ring: Revisiting the Weekday Manifold in Language Models](papers/2610.37796_spokes-not-ring-weekday.md)
- [Arithmetic in the Wild: Llama uses Base-10 Addition to Reason About Cyclic Concepts](papers/2605.01148_arithmetic-in-the-wild-cyclic.md)
- [Pre-trained Large Language Models Use Fourier Features to Compute Addition](papers/2406.03445_pretrained-llms-fourier-addition.md)
- [Hypothesis-Driven Feature Manifold Analysis in LLMs via Supervised Multi-Dimensional Scaling](papers/2510.01025_smds-feature-manifold-hypotheses.md)
- [A Geometric Invariant of Attention Predicts Head Specialization from Weights Alone](papers/2611.12206_rho-invariant-head-specialization.md)

### 跨运行 / 跨架构的普适与多样

- [The Clock and the Pizza: Two Stories in Mechanistic Explanation of Neural Networks](papers/2306.17844_clock-and-pizza.md)
- [A Toy Model of Universality: Reverse Engineering How Networks Learn Group Operations](papers/2302.03025_toy-model-universality-group.md)
- [Convergent Evolution: How Different Language Models Learn Similar Number Representations](papers/2604.20817_fu-convergent-evolution-numbers.md)
- [Language Models Learn Universal Representations of Numbers and Here's Why You Should Care](papers/2510.26285_universal-number-representations.md)
- [Global Divergence, Local Convergence: Representation Geometry in SSMs and Transformers](papers/2609.08692_ssm-transformer-representation-geometry.md)
- [Towards Universality: Studying Mechanistic Similarity Across Language Model Architectures](papers/2410.06672_towards-universality-mamba-transformer.md)
- [The Platonic Representation Hypothesis](papers/2405.07987_platonic-representation-hypothesis.md)

### 算法普适性：跨种子、家族、规模、架构（11-25 补读）

- [Mechanistic Analysis of Universality: Numerical Comparison Circuits Across Transformer Architectures](papers/2026.acl-srw.84_bhardia-numerical-comparison-circuits.md)
- [Grokking Group Multiplication with Cosets](papers/2312.06581_stander-group-multiplication-cosets.md)
- [Universal Neurons in GPT2 Language Models](papers/2401.12181_gurnee-universal-neurons-gpt2.md)
- [LLM Circuit Analyses Are Consistent Across Training and Scale](papers/2407.10827_tigges-circuits-consistent-training-scale.md)
- [Quantifying Feature Space Universality Across Large Language Models via Sparse Autoencoders](papers/2410.06981_lan-sae-feature-space-universality.md)
- [Algorithmic Phase Transitions in Language Models: A Mechanistic Case Study of Arithmetic](papers/2412.07386_sun-algorithmic-phase-transitions-arithmetic.md)
- [Open Problems in Mechanistic Interpretability](papers/2501.16496_sharkey-open-problems-mech-interp.md)
- [PolyPythias: Stability and Outliers across Fifty Language Model Pre-Training Runs](papers/2503.09543_polypythias-seed-stability.md)
- [Toward a Theory of Generalizability in LLM Mechanistic Interpretability Research](papers/2509.22831_trott-generalizability-mech-interp.md)
- [Quantifying LLM Attention-Head Stability: Implications for Circuit Universality](papers/2602.16740_bali-attention-head-seed-stability.md)
- [Transformers Converge to Invariant Algorithmic Cores](papers/2602.22600_schiffman-algorithmic-cores.md)
- [How Much Do Circuits Tell Us? Measuring the Consistency and Specificity of Language Model Circuits](papers/2605.08348_li-how-much-do-circuits-tell-us.md)
- [Polymorphism Is Rotation: Operational Mechanistic Interpretability from a Two-Layer Transformer to Pythia-70m](papers/2605.24577_mccann-polymorphism-rotation.md)
- [Many Circuits, One Mechanism: Input Variation and Evaluation Granularity in Circuit Discovery](papers/2606.06267_bayat-makou-many-circuits-one-mechanism.md)

### 状态更新：写入时还是读出时（11-25 补读）

- [Investigating the Indirect Object Identification circuit in Mamba](papers/2407.14008_ensign-ioi-circuit-mamba.md)
- [Lost with a Map: Conversational State and Behavioral Reliability in Language Models](papers/2609.33883_dokme-heck-lost-with-a-map.md)
- [Beyond State Capacity: Why Retrieval Breaks in Mamba](papers/2610.19709_yarden-beyond-state-capacity-mamba.md)

### 机制结论的跨模型推广与绑定容量（11-25 补读）

- [Tracking Equivalent Mechanistic Interpretations Across Neural Networks](papers/2603.30002_sun-toneva-interpretive-equivalence.md)
- [Differentiable Faithfulness Alignment for Cross-Model Circuit Transfer](papers/2604.24302_shao-dfa-cross-model-circuit-transfer.md)
- [In-Context Binding Capacity in Language Models](papers/2609.30634_ravulapalli-incontext-binding-capacity.md)
- [Late Attention Layers Alone Can Copy Entity Tokens, but Not Without Attending to Their Context](papers/2609.35663_he-late-layers-entity-copying.md)

### 后训练改变了读出还是计算

- [Represented but misread: Post-training changes how language models read out what they represent](papers/2611.26584_represented-but-misread.md)
- [Why Does Reinforcement Learning Generalize? A Feature-Level Mechanistic Study of Post-Training in Large Language Models](papers/2604.25011_why-rl-generalize-crosscoder.md)
- [Reasoning or Pattern Exploitation? Mechanistic Insights from RL-Trained Language Models](papers/2610.39182_reasoning-or-pattern-exploitation-tictactoe.md)
- [Interpretability without actionability: mechanistic methods cannot correct language model errors despite near-perfect internal representations](papers/2603.18353_interpretability-without-actionability.md)
- [Observable Patterns Are Not Explanations: A Causal-Geometric Analysis of Latent Reasoning Models](papers/2606.12689_observable-patterns-not-explanations-lrm.md)
- [How Do Language Models Choose Between Context and Memory?](papers/2609.00753_context-vs-memory-authority.md)
- [Many Biases, One Circuit: Post-Training Tunes a Pretrained Cue-Routing Mechanism](papers/2610.22937_many-biases-one-circuit.md)
- [Base Models Know How to Reason, Thinking Models Learn When](papers/2510.07364_base-models-know-how-to-reason.md)
- [RLVR Sharpens the Pencil, Not the Mind](papers/2611.02574_rlvr-sharpens-pencil-not-mind.md)
- [Erased, Rerouted, or Rescaled? Post-Training and the Causal Quotient of a Language Model's Belief State](papers/2610.05292_erased-rerouted-rescaled.md)
