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
