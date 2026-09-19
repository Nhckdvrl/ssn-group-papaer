# Literature Map — 2026-09-19

目的：

> **记录这一轮 breadth scan 看到了哪些 field structure，防止后续只在一个热点里越搜越窄。**

说明：

- 这里大量使用 PaperNotes 做高吞吐 discovery。
- 数量是 PaperNotes 当前索引/分类规模，只用于感受 field density，不作为官方统计。
- 这里的 paper title 不等于 positive exemplar。
- 真正进入 taste / candidate 的 paper 必须回原文 deep-read。

---

# 1. 当前 breadth coverage

这一轮至少覆盖了以下 pool：

## ACL 2026
- LLM Reasoning：约 82 篇
- Interpretability：约 63 篇
- Agent：约 82 篇
- Multimodal VLM：约 82 篇
- Audio/Speech：约 70 篇

## ACL 2025
- LLM Reasoning：约 54 篇
- Agent：约 55 篇
- VLM Reasoning：约 18 篇
- LLM Other：数百篇

## ICLR 2026
- LLM Reasoning：约 241 篇
- Interpretability：约 196 篇
- 大量 RL / generation / theory / multimodal

## ICML 2026
- LLM Reasoning：约 78 篇
- Optimization/Theory：约 88 篇
- Interpretability：约 90+
- Pretraining / RL / multimodal / generation 均有较大 pool

## NeurIPS 2025
- LLM Reasoning：约 82 篇
- Optimization/Theory：约 126 篇
- Pretraining：约 51 篇
- Interpretability：约 80 篇
- Image Generation：约 221 篇

## AAAI 2026
- LLM Reasoning：约 37 篇
- 另有 optimization / multimodal / generation 等

## CVPR 2026
- Image Generation：约 490 篇
- Multimodal VLM：约 400+
- Optimization/Theory：约 22 篇
- LLM Reasoning：约 16 篇

## ECCV 2026
- Image Generation：当前 PaperNotes 分类约 137 篇
- Video / VLM / Robotics / 3D 另有大量 work

这一步的目的不是凑“读了多少篇”。

而是建立：

> **哪里已经极度拥挤，哪里在快速改变 primitive，哪里可能有值得追的 genealogy。**

---

# 2. Reasoning / RL：已经不只是“怎么让模型多想”

2024–2026 的明显变化：

早期主问题：

> CoT / self-consistency / search 能不能提高 reasoning？

现在已经细化成多条 lineage：

### A. Compute quantity
- more samples
- longer reasoning
- test-time scaling

### B. Compute allocation
- adaptive rollout
- difficulty-aware sampling
- budget-aware tree search
- selective branching

### C. Credit assignment
- outcome vs process reward
- high-entropy / branching tokens
- positive vs negative samples
- hierarchical planning tokens

### D. Failure dynamics
- earliest wrong step
- critical transitions
- drift
- information-flow decay

### E. Objective pathology
- calibration mismatch
- entropy collapse
- relative objective bias
- group-relative advantage artifacts

### F. Faithfulness / monitoring
- CoT correctness vs causal faithfulness
- internal uncertainty vs verbalized reasoning

### 这一 lineage 的启示

如果以后还做 reasoning：

> “reasoning 更强”不是问题。

必须知道自己接在哪条 lineage 上，以及这条 lineage 最近已经把 primitive 推到哪一层。

---

# 3. Test-time scaling：object 从“更多 compute”变成“compute policy”

值得连续追：

- self-consistency
- verifier selection
- tree search
- process scoring
- adaptive search
- fixed-budget policy
- critical-transition repair

目前看到一个重要 research progression：

> **amount of compute**
>
> → **allocation of compute**
>
> → **state-dependent policy for compute**
>
> → **failure-triggered intervention**

这不是一个 candidate。

它是一条 lineage 发展的例子：

> field 的基本 object 会自己升级。

后续找题不能站在旧 object 上重复问。

---

# 4. RLVR：从 algorithm competition 开始转向 learning-signal science

高价值 paper 越来越不是：

> PPO vs GRPO vs new acronym。

而是问：

- correct / incorrect sample 分别做什么？
- 哪些 token 真正承载 policy change？
- entropy 变化来自哪里？
- group-relative baseline 的 statistical consequence 是什么？
- calibration 和 accuracy 为什么可能分离？
- strong pretrained prior 在 RL 中扮演什么角色？

代表阅读：

- Beyond the 80/20 Rule
- The Surprising Effectiveness of Negative Reinforcement
- Calibration-Aware Policy Optimization
- Emergent Hierarchical Reasoning through RL

### 对我们很重要的一点

这类 paper 的 method 往往非常小。

intellectual novelty 在：

> **把“RL 有效”拆成一个更有解释力的 learning object。**

---

# 5. ICL / mechanistic interpretability：拥挤 object 仍然可以长新 paper

ICL 已经存在：

- induction heads
- task vectors
- function vectors
- implicit Bayesian / gradient-descent views
- causal heads
- representation analyses
- steering

但 ICLR 2026 的 Information Removal 仍能成立。

这说明：

> novelty 不是“有没有研究 ICL mechanism”。

而是：

> **当前 explanatory decomposition 是否已经穷尽。**

后续 interpretability 阅读需要特别追：

> 同一 object 连续几代 paper 是如何改变 primitive 的。

而不是搜：

> “还有哪个 capability 没找 circuit”。

---

# 6. Theory：最值得学的是 assumption audit

NeurIPS 2025 的 A Little Depth Goes a Long Way 是很好的例子：

prior：
> fixed-depth Transformer 有 expressivity limitation。

new move：
> 实际 context 有上界；为什么 depth 一定要作为 absolute constant？

这不是：

> “旧 theorem 再加强一点”。

而是：

> **重新检查 theorem 的 asymptotic regime。**

以后读：

- architecture theory
- optimization theory
- scaling law
- representation theory

必须单独记录：

> theorem/claim 依赖的 load-bearing assumptions。

---

# 7. Empirical phenomenon：旧现象可以因为 evidence regime 不对而重开

CoT faithfulness：

prior 已经知道：

> prompt 中人为塞 bias/hint 时，CoT 可以不忠实。

new move：

> 现实中大家真正想知道的是 natural use 时 CoT 是否可信。

这提醒：

> “已有 paper 观察 X”不等于 “X 的实际 interpretation 已经确定”。

要审：

- evidence 是 natural 还是 adversarial；
- task 是 toy 还是 deployment-relevant；
- measurement 是否改变行为；
- observation 是否依赖 intervention 本身。

---

# 8. Diffusion / image generation：非常适合学“方法是怎样从分析长出来的”

这个领域 method paper 极多，但也因此特别适合看：

> 哪些 paper 只是 module innovation，
> 哪些 paper 真正重构了问题。

当前值得深追的几个 lineage：

## Fast sampling
- higher-order solver
- timestep schedule
- feature cache
- unified design-space analyses
- geometry-aware schedules
- adaptive compute

TORS 特别值得学：

> 它先问“真正 bottleneck 是谁”，再发明 method。

## One/few-step generation
- distillation
- consistency / flow
- target redesign
- guidance conditioning
- trajectory geometry

Improved Mean Flows 这类 paper 值得继续深读：

> 原方法哪些 default design choice 其实是 bottleneck？

## Reward alignment
- preference optimization
- reward hacking
- diversity collapse
- reward geometry / robustness

这里很容易和 LLM alignment 形成真正结构迁移。

---

# 9. Model merging：从 heuristic zoo 到 property-first

CVPR 2026 optimization pool 里：

- covariance estimation
- bias-aware routing
- directional consistency
- singular-space methods

DC-Merge 值得读的原因不是它 SOTA。

而是它试图把：

> “哪种 merge trick 好”

提升成：

> **“task capability 保留下来的必要/关键 property 是什么？”**

这类：

> method family → success invariant

是一个高价值 genealogy。

---

# 10. Optimization：别只看 optimizer name

ICML 2026 / NeurIPS 2025 optimization pool 里，大量论文表面是：

> 新 optimizer / convergence rate。

真正值得跨领域学的是：

- fixed hyperparameter 的 bias–variance conflict
- stability boundary
- stochastic vs deterministic dynamics
- implicit regularization
- saddle / sharpness behavior
- constraint handling
- bilevel coupling

例如 SAM stability work：

> 不只问“SAM 为什么泛化好”，而是分析某个动力学 regime 下 SAM 甚至更容易被 saddle 吸引，然后解释 momentum / batch size 的作用。

这种：

> popular algorithm → unexpected dynamical implication → hidden real source of success

非常值得继续深追。

---

# 11. Benchmark / evaluator papers：即使我们不想做，也不能不读

例如：

- ProcessBench
- CoT faithfulness
- CRISP-like diagnostics
- model evaluation under systematic generalization

它们的价值是暴露：

> **community 当前 measurement 根本没测到什么。**

但我们的 taste 需要区分：

### 可学习
- measurement 改变 scientific interpretation；
- 揭示当前方法都在优化错误 quantity。

### 不想做
- 主要贡献只是多一个 dataset / leaderboard；
- method/knowledge delta 很薄。

所以 benchmark paper 可以是：

> **pressure source**

不一定是：

> **target paper shape。**

---

# 12. Agent / RAG：高密度，但当前默认不是我们的优先搜索池

ACL / ICLR / ICML 的 agent paper 已经非常多。

问题：

- environment-heavy
- tool schema / simulator / benchmark 很容易成为主体
- 多轮 RL 成本大
- evaluation 不稳定
- 很容易 engineering creep

因此当前：

> **继续读，用来学习 general research move；不因为 hot 就优先做。**

RAG 同理：

> 作为 lineage study 可以读，
> 作为下一题默认低优先。

---

# 13. Multimodal / VLM：值得当“问题结构来源”，不只当新 modality

未来重点不是：

> 把 NLP question 放图像里再测。

而是看：

- modality fusion 为什么需要新的 causal decomposition；
- visual tokens / text tokens 的 compute allocation；
- generation/understanding objectives 是否冲突；
- unified models 的 representational bottleneck；
- spatial/temporal state 是否改变 reasoning primitive；
- visual tool use 如何改变 test-time search。

这类可能给 LLM research 提供：

> 新的 identification / architecture pressure。

---

# 14. Speech / audio / robotics：目前阅读不足，必须补

当前 breadth map 还不够。

下一轮 literature calibration 需要补：

## Speech/audio
- streaming / full-duplex
- codec / semantic-acoustic factorization
- speech LM
- audio reasoning
- latency / turn-taking

## Robotics/embodied
- VLA
- action chunking
- world model
- policy distillation
- action representation
- language-to-action alignment
- closed-loop adaptation

不是为了强行迁移。

而是为了寻找：

> sequence model 在真实 closed-loop / continuous control 中暴露出的新 problem structure。

---

# 15. 下一批必须 deep-read 的 lineage

不是候选题。

只是为了补 taste blind spot。

## L1 — RLVR learning-signal lineage
连续读：
- GRPO / standard RLVR
- entropy-token work
- negative reinforcement
- calibration-aware optimization
- hierarchical credit

目标：
> 看“RL algorithm”如何逐步被重写成“learning signal decomposition”。

## L2 — test-time scaling lineage
连续读：
- self-consistency
- verifier selection
- MCTS / tree search
- adaptive compute
- budget-aware MCTS
- failure-onset repair

目标：
> 看 object 从 compute amount 到 compute policy 的升级。

## L3 — ICL mechanism lineage
连续读：
- induction
- function/task vectors
- causal heads
- information removal

目标：
> 看 crowded parent 如何通过 explanatory decomposition 持续生长。

## L4 — diffusion fast sampling lineage
连续读：
- solver
- schedule
- cache
- TORS
- adaptive sampling

目标：
> 看“方法 zoo”何时需要 unified design space。

## L5 — architecture/theory
连续读：
- fixed-depth limitation
- log-depth theory
- latent vs explicit reasoning theory
- width/depth/CoT tradeoff

目标：
> 看 changed-assumption paper 如何形成。

## L6 — representation/property-first methods
连续读：
- task arithmetic
- TIES / DARE / TSV / KnOTS 类 model merging
- DC-Merge

目标：
> 看 heuristic lineage 什么时候开始寻找 invariant。

## L7 — natural-vs-artificial evidence
连续读：
- CoT faithfulness with injected bias
- CoT monitorability
- in-the-wild faithfulness

目标：
> 看 evidence-regime critique 怎样变成新 scientific question。

---

# 16. 当前 breadth scan 的最大教训

如果只看 2026 reasoning paper，会产生错觉：

> 所有好题都是 entropy、RL、test-time scaling。

如果只看 interpretability，会产生错觉：

> 所有好题都是 representation / circuit / causal intervention。

如果只看 CV generation，会产生错觉：

> 所有好题都是把一个 engineering component 重新设计。

真正跨领域放在一起以后看到的是：

> **强 paper 的共同点不是题型。**
>
> **而是它们能识别“现有 literature 正在用哪个错误/过粗/失效的 abstraction”。**

所以后续搜题最重要的不是：

> 找 hot keyword。

而是：

> **读懂一个 lineage 当前把什么当成 basic object，并判断这个 basic object 还对不对。**


---

# 17. Longitudinal reading progress — 2026-09-19

第一批纵向 reconstruction 已完成并写入：

> `LONGITUDINAL_GENEALOGIES_01_2026-09-19.md`

已追：

- **L1 RLVR learning signal**：DeepSeekMath/GRPO → DeepSeek-R1 / DAPO → high-entropy tokens → negative reinforcement → GSPO → CAPO。
- **L2 Test-time scaling / search policy**：Self-Consistency → Tree of Thoughts / process verification → compute-optimal allocation → budget-aware MCTS → critical-transition intervention。
- **L3 ICL mechanism**：Induction Heads → Task Recognition/Learning → Task Vectors → Function Vectors → task-vector structure/boundary → task-oriented information removal。
- **L4 Diffusion fast sampling**：solver-centric acceleration → optimized timestep schedule → state-conditioned schedule → unified design-space attribution / TORS → spatial difficulty-aware sampling。
- **L8 Robotics/VLA action representation**：single-step BC → ACT action chunking → RT-2 token interface → OpenVLA/Octo scaling → FAST action tokenization → asynchronous chunk correction / action-space audit。

第一批纵向阅读后的工作假说：

> **frontier 的移动经常表现为：一个曾经成功的 abstraction 被规模、部署、反馈或新模态推到新的 regime，随后从 solution 变成 inherited assumption。**

这只是 literature-reading hypothesis，不是 topic generator。

下一批优先补：

- pretraining / SFT / distillation；
- architecture / inductive bias；
- multimodal/VLM（非 robotics）；
- speech/audio；
- negative / limits paper lineage；
- optimization dynamics / theory。


---

# 18. Thickening pass completed — 2026-09-19

在第一批 L1–L8 基础上，本轮继续补到 **18 条纵向 lineage**。

新增深读 / reconstruction：

## G06 — Pretraining scaling / data composition
- Kaplan-style N/D/C scaling
- Chinchilla compute-optimal reallocation
- data mixture as structured variable
- scaling laws for optimal mixtures
- data-mixing phase transitions
- repetition/document exposure
- hyperparameter scaling

关键观察：
> smooth global scaling law 可以与 capability-specific discontinuity 并存。

## G07 — SFT & knowledge
- instruction tuning / LIMA worldview
- new-knowledge fine-tuning
- hallucination / knowledge modification
- token/parameter-level SFT analysis
- giant empirical sweeps as execution contrast

关键观察：
> SFT example 的作用取决于 model pre-SFT knowledge state；dataset item 有 model-relative property。

## G08 — Distillation
- standard KD
- divergence direction / MiniLLM
- capacity gap
- key-step CoT
- curriculum
- student rollout / selective teacher intervention

关键观察：
> supervision quality 不是 teacher intrinsic scalar，而越来越被写成 teacher–student–state relation。

## G09 — Architecture / inductive bias
- Universal Transformer
- looped computation
- recurrent latent depth
- minimal growing depth theory
- Body Transformer
- spatial positional inductive bias

关键观察：
> architecture novelty 更应该由真实 computation / geometry / physics structure约束，而不是 module invention。

## G10 — VLM interface / visual-token lifecycle
- modality bridge
- frozen-expert bridge
- instruction-tuned simple connector
- high-resolution token explosion
- depth/instance/token relevance
- operator-compatible compression
- dynamic video relevance
- multi-turn future-query uncertainty

关键观察：
> 2025–2026 generic visual token compression 已高度 saturated；新 setting 有意义时通常因为 compression objective 本身改变。

## G11 — Latent multimodal reasoning
- text-centric visual reasoning
- explicit visual intermediates
- latent visual tokens / implicit visual reasoning

关键观察：
> explicit→latent 已形成 cluster，不能再承担 novelty。

## G12 — Full-duplex speech
- VAD/ASR/LLM/TTS
- speech token LM
- shared clock / synchronous LLM
- direct speech-to-speech / Moshi
- internal text scaffold

关键观察：
> speech 把 real physical time / concurrency 变成 first-class modeling variable。

## G13 — Negative / limits / measurement re-attribution
- prompt calibration
- prompt-order sensitivity
- changed premise from instruction tuning
- evaluation artifact audit
- inductive-bias world-model probe

关键观察：
> strongest negative paper 常常改变 failure attribution，而不只是找一个 failure。

## G14 — Optimization / SAM dynamics
- SAM
- whole-trajectory Hessian dynamics
- saddle/instability
- lookahead correction
- objective reformulation
- optimizer memory as implicit loss modification

关键观察：
> successful algorithm 的 original motivation 也可以成为 downstream scientific hypothesis，而不是永久真理。

## G15 — Multimodal pretraining objectives
- contrastive vs generative
- BLIP / CoCa unification
- BLIP-2 frozen bridge
- unified understanding-generation
- capability-asymmetry/self-supervision
- autoencoder/reconstruction relation

关键观察：
> 后期问题逐渐从“选哪种 loss”转向“不同 capabilities/objectives 之间应该满足什么 relation”。

## G16 — Speech tokenization
- neural acoustic codec
- semantic units
- SpeechTokenizer hierarchical RVQ
- Mimi streaming/low-rate constraints
- speech-LM scaling
- contextual representation / DM-Codec

关键观察：
> tokenizer 定义 downstream model 把 capacity 花在什么 variation 上。

## G17 — CoT faithfulness identification
- bias/hint intervention
- causal mediation
- model-family differences
- parametric faithfulness / unlearning
- metric diagnosticity
- natural evidence regime

关键观察：
> scientific concept 会随着 identification strategy 变化而被重新定义。

## G18 — Video / world-model dynamics
- video generation
- action-conditioned transition model
- interactive digital twin
- appearance/dynamics disentanglement
- unified action/world model
- autoregressive long-horizon state error

关键观察：
> generator 被用于 planning/interaction 后，“生成看起来合理”不再等于“world model正确”。

详细见：
- LONGITUDINAL_GENEALOGIES_02_2026-09-19.md
- LONGITUDINAL_GENEALOGIES_03_2026-09-19.md
- LONGITUDINAL_GENEALOGIES_04_2026-09-19.md
- GENEALOGY_LIBRARY_INDEX_2026-09-19.md
- CONTRAST_CASES_AND_ANTI_PATTERNS_2026-09-19.md

---

# 19. Breadth → depth balance check

这一轮没有把所有方向都“深读到一样深”。

当前 depth 大致分三层：

## Tier A — longitudinally reconstructed with multiple parents/successors
- RLVR
- test-time scaling
- ICL mechanism
- diffusion fast sampling
- VLA/action representation
- SFT/distillation
- VLM token lifecycle
- speech/full-duplex
- SAM
- CoT faithfulness

## Tier B — solid multi-paper conceptual reconstruction
- pretraining scaling/data mixture
- architecture/depth/inductive bias
- multimodal objective unification
- speech tokenization
- video/world model

## Tier C — breadth-scanned, not yet a primary taste source
- long-context
- MoE/routing
- model editing
- continual learning
- code/program synthesis
- 3D
- scientific ML

Rule：

> Tier C 不得直接拿来出候选题。
>
> 如果未来 seed 落到 Tier C，先做一轮对应 genealogy reconstruction。

---

# 20. Current literature-density warnings

截至当前 scan，特别需要警惕以下近期 cluster：

- generic GRPO variants；
- entropy/selective-token RL；
- generic test-time adaptive compute；
- visual-token compression；
- latent visual reasoning；
- unified multimodal models；
- student-aware CoT distillation；
- full-duplex speech as a label；
- generic world models；
- CoT faithfulness metrics；
- generic scaling-law fitting。

这些不是不能研究。

而是：

> **仅凭进入这些热门 cluster，本身已经没有选题信息。**

必须恢复更窄的 parent history和真实 pressure。

---

# 21. Current stopping discipline

用户明确要求：
> 不要做一批就过早“跳出来”。

因此 literature-calibration阶段的完成标准不再是：

> “找到几个漂亮 meta-pattern”。

而是至少同时有：

1. 多领域 breadth map；
2. 多条 longitudinal lineage；
3. immediate-parent reconstruction；
4. same-surface/different-genealogy comparison；
5. contrast / anti-pattern library；
6. execution-transfer audit；
7. saturation map；
8. clear blind-spot ledger。

当前已经首次具备 1–8 的基本版本。

这仍不代表：
> “现在应该立刻开始找题”。

只代表：
> 后续若进入 candidate search，已经不再只有一套单一模板作为视角。
