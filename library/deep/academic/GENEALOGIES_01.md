# Longitudinal Genealogies 01 — 2026-09-19

> **Status: literature / taste calibration only.**
>
> 本文件不生成候选题，不注册 CTxx，也不把下面任何历史 pattern 当成搜题模板。
>
> 目的只有一个：
>
> > **把几条成熟 research lineage 纵向展开，研究一个 field 的 basic object / unit / assumption 是怎样一代代发生变化的。**
>
> 这里的“genealogy”是基于论文公开 claim、related work、problem setup 与实验结构做的 research reconstruction。
>
> **不声称后来的作者一定是因为读到前一篇的某句 future work 才想到下一篇。**
>
> 我们关心的是：
>
> > 在后一篇出现以前，literature 已经把哪些东西变成了可见 object；  
> > 后一篇到底重新定义了什么；  
> > 为什么那个重新定义在当时有 scientific / algorithmic pressure。

---

# 0. 为什么要纵向读

孤立读一篇 paper，最容易得到这种总结：

> A 提出 X，提升 Y。

连续读一个 lineage，问题会完全不同：

> 为什么 2022 年大家把 primitive 定义成 A，  
> 到 2024 年 primitive 变成 B，  
> 2025 年又开始拆 B 内部的 C/D，  
> 2026 年反而开始研究 B 优化时损坏的另一个 quantity E？

这才接近：

> **research frontier 是怎样移动的。**

第一批选择五条：

1. RLVR learning signal
2. Test-time scaling / search policy
3. ICL mechanism
4. Diffusion fast sampling
5. Robot/VLA action representation & chunking

它们特意不属于同一种 paper type。

---

# LINEAGE 1 — RLVR：从“RL 能否激发 reasoning”到“到底什么 learning signal 在起作用”

## 1.1 Pre-lineage world

在 reasoning RL 成为热点以前，主问题更接近：

> pretrained / instruction-tuned LM 能否通过 RL 在可验证任务上继续提升？

PPO 的 actor-critic/value-model 结构成本较高。

数学 reasoning 又提供了一个特殊条件：

> outcome 很多时候可以自动验证。

这使得：

> reward 可以便宜、规模化地得到。

这里最初的 research object 主要还是：

> **trajectory / response-level policy optimization。**

---

## 1.2 DeepSeekMath / GRPO — 先解决“怎么做规模化 RL”

**DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models (2024)**

重要贡献之一是 GRPO：

> 用 group-relative reward / baseline 避开额外 value model，降低 PPO 类训练的资源负担。

在这一阶段，研究 pressure 很直接：

- 数学预训练有效；
- 可验证 reward 可用；
- PPO 很重；
- 怎样让 reasoning RL 更可扩展？

### Primitive

> sequence / rollout 的 reward 与 policy update。

### 当时还没有被充分拆开的东西

- response 里哪些 token 真正在学？
- correct 和 incorrect sample 是否作用对称？
- accuracy gain 是否损坏 uncertainty / calibration？
- reward-relative update 是否在统计上引入别的偏差？

换句话说：

> GRPO 主要回答“怎么优化”，没有必要同时回答“优化信号内部是什么”。

---

## 1.3 DeepSeek-R1 — 让“纯 RL 可以诱发 reasoning”本身成为事实

**DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning (2025)**

R1-Zero / R1 的重要影响不是只有 benchmark。

它把一个新的 empirical premise 变得很难忽略：

> 大规模 outcome-RL 不只是微调答案分布；它可以伴随更长 reasoning、自我反思、策略变化等 emergent behavior。

于是 literature 的问题开始从：

> RL 能不能用？

向：

> **RL 到底改变了什么？为什么会改变？**

移动。

这里非常值得注意：

> 一个成功 scaling result 本身会创造新的 science question。

不是因为作者“漏做了分析”。

而是因为：

> **当 effect 足够大，原来不值得研究的内部机制突然变成了重要 object。**

---

## 1.4 DAPO / large-scale RL engineering — 先把 instability 拆成可操作问题

**DAPO: An Open-Source LLM Reinforcement Learning System at Scale (2025)**

这一支更偏 scaling / training recipe：

- reward / clipping / sampling 等 practical choices；
- large-scale open RL system；
- 复现和训练稳定性。

它告诉我们：

> RLVR 的结果并不是只由“算法名字”决定。

training system / sampling / clipping / data regime 都会改变 behavior。

### 对 genealogy 的作用

这使得后续纯“PPO vs GRPO vs another acronym”的空间更拥挤。

也让真正有意思的问题开始往：

> **learning signal 的结构**

下沉。

---

## 1.5 High-Entropy Minority Tokens — sequence update 不是 homogeneous 的

**Beyond the 80/20 Rule: High-Entropy Minority Tokens Drive Effective Reinforcement Learning for LLM Reasoning (NeurIPS 2025)**

这是 lineage 里很关键的 object change。

过去 gradient 是 token-level 算的，但 conceptually 仍经常把整个 response 当成一个统一对象。

这篇从 token entropy 看 update，发现：

> reasoning trajectory 中只有少部分 high-entropy token 承担真正的 branching / decision leverage。

低 entropy token 很多只是：

> 已经决定路径后的 continuation。

而只针对这些高 entropy / forking tokens 更新，可以保持甚至提升效果。

### Question-forming move

不是：

> “我们发明一个 token weighting trick。”

而是先问：

> **一个获得 sequence-level reward 的 trajectory，内部各 token 的 learning importance 真的是同质的吗？**

### Primitive change

```
rewarded sequence
→ heterogeneous token decisions
→ a minority of branching tokens
```

### 新的 consequence

一旦这个结果成立：

> full-sequence update 就不再是“自然默认”，而是一个需要解释的 design choice。

---

## 1.6 Negative Reinforcement — correct / incorrect rollout 不是对称 signal

**The Surprising Effectiveness of Negative Reinforcement in LLM Reasoning (NeurIPS 2025)**

这里又换了一个分解轴。

RLVR 通常把：

- correct rollout 提高概率；
- incorrect rollout 降低概率；

作为同一个 binary reward objective 的两面。

作者把它显式拆成：

- Positive Sample Reinforcement (PSR)
- Negative Sample Reinforcement (NSR)

然后分别训练。

决定性的不是最后 W-REINFORCE。

而是出现了强 asymmetry：

- PSR 可以提高 Pass@1，却压缩多样性、伤更高 k；
- NSR 单独就能在广泛 Pass@k 上改善；
- gradient analysis 指向：NSR 更像 suppress 已有错误，再让 probability mass 按 pretrained prior 重新分配。

### Primitive change

```
binary reward
→ positive update + negative update
→ two learning operations with different behavioral effects
```

### 为什么它能在 GRPO 已经很热门后仍有新意

因为它没有再问：

> 哪个 RL algorithm 更好？

而问：

> **我们一直称为“RLVR signal”的东西到底是不是一个 atomic signal？**

---

## 1.7 GSPO — reward unit 与 optimization unit 的错位

**Group Sequence Policy Optimization (2025)**

另一条分支不是 entropy，也不是正负样本。

它抓：

> reward 是 sequence-level；
> 但一些优化量/importance ratio 的处理长期保留 token-level结构。

于是把优化 unit 对齐到 sequence。

### 这里学到什么

当一个 field 从别的算法传统继承技术组件时：

> **历史留下的 computational unit 不一定与当前 task/reward 的 semantic unit 对齐。**

这和 high-entropy token paper 看似相反：

- 一个说不要把 token 当同质；
- 一个说某些 policy-ratio design 应该升到 sequence。

并不矛盾。

它们说明：

> **不同数学对象需要不同的 natural unit。**

这也是为什么不能把“更细粒度”当固定创新方向。

---

## 1.8 CAPO — accuracy 提升不等于 objective 没损坏别的 quantity

**Calibration-Aware Policy Optimization for Reasoning LLMs (ACL 2026)**

到了这里，问题再次移动。

已有 RLVR 很强。

但如果 reasoning model 被用于：

- confidence-based selection；
- routing；
- abstention；
- downstream decision；

那么 calibration 也是 operationally important。

论文观察到：

> GRPO 可以提高 accuracy，同时让 relative calibration / AUC 变差。

然后不是停在 empirical trade-off，而是进一步问：

> 为什么 group-reward advantage 对 calibration 不一致？

理论分析把问题归到：

> uncertainty-agnostic advantage 与 calibration objective 的 gradient mismatch。

CAPO 才从这里长出。

### Primitive change

```
optimize correctness
→ correctness + uncertainty relation
→ objective consistency with the downstream quantity
```

---

## 1.9 这条 lineage 真正发生了什么

不能简单写成：

> GRPO → token weighting → better RL。

更接近：

```
Can scalable verifiable RL work?
        ↓
large effects establish RLVR as a real capability-changing process
        ↓
recipe/stability problems become visible
        ↓
"the RL signal" stops being atomic
        ↓
Which tokens carry decision leverage?
Which signs of feedback play different roles?
Which optimization unit matches the reward?
Which side quantities are silently distorted?
```

frontier 从：

> **algorithm name**

逐渐移动到：

> **learning signal structure / optimization semantics。**

---

## 1.10 已经开始 saturated 的轴

至少截至当前 literature：

- “高 entropy token 更重要”
- generic entropy preservation
- correct/incorrect sample reweighting
- another GRPO clipping variant
- simply adding process reward
- generic difficulty-aware sampling

都已经非常危险。

---

## 1.11 机械复制会犯什么错

错误迁移：

> “那我们找另一个 token score 做 weighting。”

或者：

> “那我们再拆一种 positive/negative subgroup。”

这只是复制 surface。

真正值得学的是：

> **一个规模化成功算法出现以后，不要默认它论文里的 optimization object 就是 natural scientific object。**

但到底该怎么拆：

> 必须来自该领域自己的 pressure。

---

# LINEAGE 2 — Test-Time Scaling：从“多采样”到“何时、哪里、以什么 policy 花 compute”

## 2.1 Self-Consistency — 先打破 single greedy path

**Self-Consistency Improves Chain of Thought Reasoning in Language Models (2022)**

CoT 原本常见 decoding：

> 生成一条 reasoning chain → 得 answer。

Self-consistency 做的 conceptual move 很简单却重要：

> reasoning 问题往往存在多条有效路径；
> 一条 greedy trajectory 不应该等于模型的全部 reasoning capacity。

因此：

> sample multiple chains → marginalize / vote answers。

### Primitive change

```
one deterministic reasoning path
→ distribution over reasoning paths
```

从这里开始，test-time compute 有了明确对象：

> **多花 sampling compute 能换 performance。**

---

## 2.2 Tree of Thoughts — sampling distribution 还不够，要显式 search state

**Tree of Thoughts: Deliberate Problem Solving with Large Language Models (2023)**

如果 self-consistency 是：

> 多条完整路径最后投票，

ToT 则把生成过程重新表示成：

> coherent thought state + branching + evaluation + backtracking。

### Primitive change

```
independent full trajectories
→ explicit intermediate search states
```

于是 compute 不再只是：

> “多生成几份答案”。

开始变成：

> **search policy。**

---

## 2.3 Process supervision — final answer score 太晚

**Let's Verify Step by Step (2023)**

和 search lineage 相互作用的一条重要 evaluator branch：

> outcome reward 只告诉最终对错；
> process reward 可以评价中间 reasoning step。

这使得：

> search 不必等到整条路径结束才能得到 signal。

### Primitive change

```
final outcome
→ intermediate process quality
```

它不是 search algorithm 本身。

但它改变了 search 可获得的信息结构。

这类“相邻 lineage 提供新 measurement，然后另一 lineage 的 algorithm space 扩大”非常常见。

---

## 2.4 Compute-optimal test-time scaling — “更多 compute”开始失效为问题定义

**Scaling LLM Test-Time Compute Optimally Can Be More Effective than Scaling Model Parameters (2024)**

当 sampling/search 已经证明有效后，一个现实问题出现：

> 不是所有 prompt 都值得同样多的 inference compute。

论文比较不同 test-time scaling 策略，并强调：

> 方法收益依赖 problem difficulty。

于是：

> fixed best-of-N

变成：

> **difficulty-conditional compute allocation。**

### Primitive change

```
test-time compute amount
→ policy for allocating compute across problems
```

这是非常重要的 frontier shift。

因为从这一刻起：

> “多想一点有没有用”

已经不是最好的问题。

更自然的是：

> **什么状态下应该多想？**

---

## 2.5 BG-MCTS — per-query budget 不能只当 stop condition

**Aligning Tree-Search Policies with Fixed Token Budgets in Test-Time Scaling of LLMs (2026)**

上一阶段已经在问：

> 哪个 problem 分配多少 compute？

BG-MCTS 把问题再推进一层：

> 一个 query 的总 token budget 确定以后，
> search policy 在预算早期和预算将尽时为什么还应该一样？

标准 MCTS 通常：

> budget 用完 → stop。

但 remaining budget 并没有成为真正的 policy state。

作者因此让 search policy 对 remaining budget 敏感：

- early：更广；
- late：更深、更倾向完成。

### Primitive change

```
allocate a budget to the query
→ condition the within-query policy on remaining budget
```

这说明：

> **global allocation problem 和 within-trajectory control problem 是两层不同对象。**

---

## 2.6 GUARD — 即使有 budget policy，也不代表每个 trajectory location 都同样值得 branch

**Dissecting Failure Dynamics in Large Language Model Reasoning (ACL 2026)**

再往下：

> 一个错误 reasoning trajectory 不是从头到尾均匀“变坏”。

作者定位：

> first invalid transition / failure onset。

发现很多失败：

- 在较早阶段出现关键错误；
- 后面仍然可以局部 coherent 地继续很久；
- 同一 state 的 alternative continuation 可能成功；
- critical transition 常伴随 entropy / branching signal。

于是 intervention 从：

> 增加整条 trajectory 的 compute

变成：

> **只在高 leverage transition 做 branch / redirect。**

### Primitive change

```
problem-level difficulty
→ budget state
→ trajectory-local failure opportunity
```

---

## 2.7 这条 lineage 的真正 progression

```
greedy one-path inference
→ sample a distribution of paths
→ explicit intermediate search states
→ intermediate evaluators
→ allocate compute by problem difficulty
→ adapt search to remaining budget
→ intervene at locally high-leverage transitions
```

这里不是“越细越好”。

而是：

> **compute control 的 state representation 越来越接近真正决定 marginal value 的变量。**

---

## 2.8 Research pressure 是怎样一代代产生的

Self-consistency 成功以后：

> compute 成为资源。

ToT/verification 成功以后：

> compute 不只可以“多”，还可以“搜索”。

search 成功以后：

> uniform allocation 成为浪费。

adaptive allocation 成功以后：

> within-query policy 仍然可能是 budget-blind。

budget-aware policy 成功以后：

> 仍然可能在错误的 trajectory location 花 compute。

也就是说：

> **每一代 solution 都把一个以前不可问的问题变成下一代可以问的问题。**

---

## 2.9 机械复制会犯什么错

不要得到：

> “下一篇一定是更细粒度 allocation。”

这很危险。

更应学习：

> **当 field 开始 optimization under resource constraints 时，必须持续检查“marginal value of compute”到底由哪个 state variable 决定。**

如果没有新的真实 state variable：

> 再切更细只是人为复杂化。

---

# LINEAGE 3 — ICL Mechanism：一个极拥挤问题如何连续改变 explanatory primitive

## 3.1 In-Context Learning and Induction Heads — capability ↔ circuit emergence

**Olsson et al. (2022)**

ICL 最开始可以只是 behavioral observation：

> context 中给几个 pattern，模型后续预测会利用这些 pattern。

这篇的重要 move 是把：

> training 中 ICL capability 的 phase change

与：

> induction-head circuit 的 emergence

联系起来。

尤其在小型 attention-only models 中给出较强 mechanistic evidence。

### Primitive

```
behavioral ICL
→ learned circuit capable of pattern completion / induction
```

重要的是：

> ICL 从 capability-level phenomenon 变成了可以定位的 internal computation。

---

## 3.2 Task Recognition vs Task Learning — 先问“ICL”是不是一个东西

**What In-Context Learning "Learns" In-Context: Disentangling Task Recognition and Task Learning (2023)**

这条 lineage 不沿 circuit 往下。

而是先在 behavior/function level 拆：

- Task Recognition：
  demos 帮模型识别一个 pretraining 中已经存在的 task；
- Task Learning：
  demos 真的让模型在 context 中建立新的 input-output mapping。

### Primitive change

```
ICL as one phenomenon
→ recognition of stored task + learning a new task
```

这特别重要，因为：

> 如果不先拆 capability，后面的 “ICL mechanism” 很可能把两种完全不同的 computation 混在一起。

---

## 3.3 Task Vectors — demonstrations 能否被压缩成一个 task representation

**In-Context Learning Creates Task Vectors (2023)**

这里研究对象又换了：

> 不是只问哪个 head 做 copying，也不是只问 behavior 分几类。

而是问：

> demos 对后续 query 的 effect 是否能被一个 compact representation 压缩？

如果能：

> 从 demonstrations 计算出的 task vector 可以注入别的 query/context 中并恢复 task behavior。

### Primitive change

```
set of demonstrations
→ compact task representation
```

这给后续 work 一个新的 object：

> **task representation 本身。**

---

## 3.4 Function Vectors — representation 不必每次由 context 新创建

**Function Vectors in Large Language Models (ICLR 2024)**

Function Vectors 与 task-vector family 看起来很近。

真正重要的区别是：

> 一些 function-like representations 可以是模型内部已经存在的 causal directions，并由少数 attention heads transport / compose，而不只是 demos 临时“写出来”的 summary。

论文用 causal interventions 验证这些 vector 对 function execution 的作用。

### Primitive change

```
context creates a task summary
→ model contains endogenous causal function representations
```

这一步使问题从：

> demos 如何编码 task？

拓展成：

> 模型内部本来存着哪些可调用 computation？

---

## 3.5 Task-vector structure / limitation — 有 vector 不代表它能表示任意 task

后续研究开始问：

- task vectors 为什么能工作？
- 它们是不是线性组合？
- 哪种 mapping 超出这种 representation 的能力？
- representation rank / structure 有什么 boundary？

### lineage signal

一旦一个 object 被证明存在：

> 下一阶段很自然会从 existence 转向 structure / expressivity / boundary。

但不是所有 object 都值得这么追。

前提是：

> 这个 object 真正承担了前一阶段的 explanation。

---

## 3.6 Task-Oriented Information Removal — explanation 的方向被反过来

**Mechanism of Task-oriented Information Removal in In-context Learning (ICLR 2026)**

这是当前最值得研究 taste 的一跳。

到了这时：

- induction heads 已有；
- task/function vectors 已有；
- representation steering 已有；
- causal heads 已有；
- task recognition/task learning 已拆过。

如果用关键词 novelty：

> “ICL internal representation”早就拥挤死了。

论文却从另一个 explanatory decomposition 切入：

> zero-shot hidden state 可能已经同时携带多个 potential-task 的 information；
> few-shot examples 的关键作用不一定是“把目标 task 写进去”，
> 也可能是**选择性删除 task-irrelevant information**。

作者进一步：

- 构造 low-rank removal/filter；
- 观察 few-shot representation 的变化；
- 定位 Denoising Heads；
- causal ablation 检验。

### Primitive change

```
context adds / writes the task
→ context filters an already entangled representation
```

这个 move 的价值不在“又找到一种 head”。

而在：

> **把 computation direction 从 addition 改成 selection/removal。**

---

## 3.7 这条 lineage 给“拥挤方向”一个更细的理解

错误判断：

> ICL mechanism 有太多人做，所以没有空间。

更好的判断：

> 当前有哪些 explanatory coordinates 已经 saturated？

例如：

- “再找一个 causal head”可能 saturated；
- “再找一个 task vector”可能 saturated；
- “再证明 ICL 有 representation”可能 saturated。

但：

> **existing explanations 是否共享某个没被检查的 process assumption？**

仍可能 open。

---

## 3.8 需要警惕的 retrospective illusion

现在把这些 paper 连起来，很容易写成：

> induction head → task vector → function vector → removal

仿佛历史必然如此。

不是。

这些工作有多条并行 parent：

- behavioral ICL theory；
- mechanistic interpretability；
- task arithmetic / steering；
- representation probing；
- meta-learning / Bayesian interpretations。

正确学习方式不是背一条线。

而是看：

> **每篇为什么在当时 existing explanation space 中还有一块真正不同的 explanatory degree of freedom。**

---

## 3.9 机械复制会犯什么错

最危险：

> 找任何 capability，然后问“是不是 information removal”。

这是纯 analogy。

真正可迁移的是：

> **当一个 field 的主解释长期使用同一个 directional metaphor（write/add/encode/route）时，检查它是否只是一个未验证的 decomposition。**

但必须有该 field 独立证据。

---

# LINEAGE 4 — Diffusion Fast Sampling：从 solver competition 到 design-space attribution，再到局部 compute allocation

## 4.1 Pre-lineage world

Diffusion / ODE sampling 的显著问题：

> 高质量生成需要很多 denoising / solver steps。

早期快速采样的大量 work 自然围绕：

- better numerical solver；
- higher-order integration；
- fewer function evaluations。

primitive 主要是：

> **如何更准确地走同一条 continuous trajectory。**

---

## 4.2 Optimized Time Steps — solver 固定以后，time grid 本身也是 algorithm

**Accelerating Diffusion Sampling with Optimized Time Steps (CVPR 2024)**

当 solver 已经很强以后，另一个长期默认浮现：

> timestep 往往按手工/uniform/固定 schedule 选择。

论文把：

> solver 给定时，在哪些 times 调用它

变成 optimization object。

### Primitive change

```
which solver?
→ where along time should a fixed solver spend its evaluations?
```

这很像 resource allocation，但不能简单迁成 LLM token budget。

它来自 diffusion ODE 的具体 trajectory error。

---

## 4.3 Schedule on the Fly — global schedule 仍假设所有 sample 一样

**Schedule On the Fly: Diffusion Time Prediction for Faster and Better Image Generation (CVPR 2025)**

固定优化 schedule 仍然有一个 assumption：

> 所有 prompt / current latent 共享一套时间步。

下一步因此变成：

> 根据当前 state 预测 next time / noise level。

### Primitive change

```
globally optimized time schedule
→ sample/state-conditioned schedule
```

这里 success 本身又暴露：

> “time schedule”不是一个静态 hyperparameter，而可以是 policy。

---

## 4.4 TORS — 当 solver / schedule / cache 都发展起来，真正缺的是 attribution

**Analyzing and Improving Training-Free Fast Sampling of Text-to-Image Diffusion Models (ECCV 2026)**

到 2026，一个更成熟的问题出现：

fast sampling 已经有多个平行 branch：

- solver；
- outer timestep schedule；
- inner scheduling；
- feature caching；
- feature prediction。

如果继续在任何一个 branch 内发 trick：

> 很难知道整个 fast-sampling design space 里真正的 bottleneck 是谁。

论文因此先做：

> unified / matched decomposition。

在统一 compute budget 下比较 components，发现 outer sampling schedule 是最关键因素之一。

只有在这一步之后，才进一步研究：

> 为什么 schedule 应该非均匀？

并用 trajectory geometry：

- curvature；
- torsion；
- total rotation；

推导 TORS。

### Primitive change

```
multiple isolated acceleration methods
→ one common design space
→ component attribution
→ dominant component
→ geometric principle for that component
```

这篇最值得学的恰恰是：

> **先缩小“哪里值得创新”的空间，再创新。**

---

## 4.5 Denoising, Fast and Slow — temporal allocation之后，spatial uniformity 也成为 assumption

**Denoising, Fast and Slow: Difficulty-Aware Adaptive Sampling for Image Generation (CVPR 2026)**

过去 adaptive sampling 主要沿：

> time / sample

变化。

但一张图内部：

> 不同 patch 的 denoising difficulty 并不相同。

于是问：

> 为什么每个空间区域都必须经历同样 timestep / compute？

不过这里出现一个非常关键的 negative：

> 直接让不同 patch 处于不同噪声时间，会产生训练时过于 informative、推理时不存在的 state mismatch。

所以方法不是简单“per-patch adaptive timestep”。

而必须先解决：

> **local adaptation 引入的 support / train-inference mismatch。**

### Primitive change

```
global temporal schedule
→ spatially heterogeneous local difficulty
→ constrained local adaptation under valid state support
```

这里特别能说明：

> 好 method 往往不是看到 heterogeneity 就 adaptive。

真正 paper-sized 的部分常常是：

> **为什么 naive adaptive idea 本身不成立。**

---

## 4.6 Cache branch — acceleration 的另一个 state space

同时期 caching line 也从：

> fixed local cache interval

走向：

> path-dependent/global cache planning。

这说明成熟 field 常出现：

> 同一个 efficiency goal，被不同 state representation 切成完全不同的 optimization problems。

所以：

> 不能只看“都是加速”就把它们当一个 method family。

---

## 4.7 这条 lineage 的关键历史变化

```
better integrator
→ better location of function evaluations
→ instance-conditioned time policy
→ multiple acceleration branches become hard to compare
→ unified attribution identifies dominant component
→ trajectory geometry explains schedule
→ local/spatial heterogeneity creates a new axis
```

这和 RL test-time scaling 有结构相似：

> uniform resource → adaptive allocation。

但 underlying object 完全不同：

- LLM：reasoning branch / verifier / token budget；
- diffusion：ODE trajectory / noise schedule / spatial noise state。

真正可迁移的是：

> **问清楚 heterogeneity 的 physical/statistical source。**

而不是复制“adaptive”。

---

## 4.8 机械复制会犯什么错

错误：

> “既然 diffusion 可以 adaptive schedule，我们给 LLM 也 adaptive schedule。”

太浅。

正确学习：

> 当成熟方法 family 有多个独立 acceleration axes 时，
> 先问是否缺 matched design-space attribution；
> 当统一方案已出现，再问 dominant component 有没有更自然的 state/geometry。

是否适用于另一个领域：

> 必须由那个领域自己的 structure 决定。

---

# LINEAGE 5 — Robotics / VLA：成功的 action abstraction 怎样不断制造下一代问题

这条 lineage 很重要，因为它让我们离开 NLP/reasoning 的局部语言。

---

## 5.1 ACT — 单步 imitation 的 horizon 本身就是问题

**Learning Fine-Grained Bimanual Manipulation with Low-Cost Hardware / Action Chunking with Transformers (2023)**

fine-grained manipulation 里，behavior cloning 有经典问题：

> 小的 prediction error 会通过 closed-loop execution 累积成 compounding error。

常见解法如：

- DAgger / on-policy correction；
- synthetic perturbation / recovery data；

在高维、人类示范、真实机器人中往往代价很高。

ACT 的核心 move：

> 不再一步预测一个 action，而是一次预测未来一段 action chunk。

这样：

- effective decision horizon 缩短；
- temporally correlated human behavior 可以作为 sequence 被建模；
- overlapping chunks 再做 temporal ensembling 提升 smoothness。

### Primitive change

```
one observation → one action
→ one observation → short action trajectory
```

这是一个非常典型的例子：

> **改变 prediction unit 本身，就能改变 learning problem 的 effective horizon。**

---

## 5.2 RT-2 — web semantics 与 robot action 原本属于两个接口

**RT-2: Vision-Language-Action Models Transfer Web Knowledge to Robotic Control (CoRL 2023)**

另一条 pressure：

> VLM 有大量 internet semantic knowledge；
> robot policy 有低层 action data；
> 两者原本训练接口不同。

RT-2 做了一个看似简单、实际很 consequential 的 representation move：

> 把 robot actions 表示成 text-like tokens，
> 与 vision-language data 共同 autoregressive 训练。

### Primitive change

```
language prediction + separate robot controller
→ shared token prediction interface including actions
```

这样做的真正意义不是：

> “把 action 变成文字。”

而是：

> **把两种数据放进同一个 sequence-model training objective。**

这使 pretrained VLM knowledge 能直接进入 action generation。

---

## 5.3 OpenVLA / Octo — 一旦 VLA 成立，下一层 pressure 是 scale / openness / heterogeneity

后续 generalist policies 开始面对：

- 不同 embodiment；
- 不同 sensor；
- 不同 action dimension；
- 大规模 robot dataset；
- efficient finetuning；
- 开源可复现。

OpenVLA 的重要性很大程度是：

> open / scalable VLA recipe 与 fine-tuning accessibility。

Octo 更明确处理：

> generalist policy 怎样兼容 heterogeneous observation/action spaces 并快速适配。

### genealogy lesson

成功 paradigm 一旦建立：

> 下一代不一定马上挑战它的“理论”。

很多工作会先：

> 把 paradigm 做成 infrastructure / scalable system。

这类 paper 对 field 也很重要，但 question-forming sharpness可能不同。

所以不能把：

> impact

与：

> 我们要学习的 research taste

完全等同。

---

## 5.4 FAST — “actions as tokens”成功以后，tokenization 本身成为 bottleneck

**FAST: Efficient Action Tokenization for Vision-Language-Action Models (2025)**

这是这条 lineage 里最值得当前 taste 学习的一篇。

RT-2 / OpenVLA 风格 VLA 已经建立：

> action 可以像 language token 一样 autoregressive predict。

但高频 dexterous control 暴露出一个 representation pathology：

> 相邻连续 action 极强相关。

如果直接逐维、逐时刻离散化：

- token sequence 很长；
- adjacent token highly predictable；
- next-token loss 很容易通过近似复制局部值下降；
- model 可以陷入一个“loss 很好看，但并没有学好 long-range action structure”的局部解。

于是 FAST 没有先改 backbone。

它先问：

> **把 continuous control signal 直接当 text-like token stream，是不是就错在 representation entropy structure？**

解决方案从 signal compression 出发：

> 用 DCT 把平滑的 action sequence 转到 frequency space，再做量化/tokenization；再配合 compression/token vocabulary 设计。

### Primitive change

```
action is tokenizable
→ but what representation makes action tokens learnable?
```

这一步非常值得学，因为它展示：

> 一个曾经 enabling 的 abstraction，可以在新的 regime 下变成 bottleneck。

RT-2 的 token interface：

> 让 VLM → control 成为可能。

FAST 的问题：

> 当 control 频率/灵巧度提高时，这个 interface 的统计结构还合适吗？

---

## 5.5 Diffusion Policy 是一个重要 sibling，而不是“FAST 的前一步”

**Diffusion Policy (2023)**

它面对 multimodal continuous action distribution 时，没有走：

> discrete autoregressive action tokens。

而是把 policy 表示成：

> conditional diffusion over actions / action sequence。

### genealogy 价值

这提醒我们：

> field 中同一个 pressure 可以产生完全不同的 representation branch。

如果只追 VLA tokenization lineage，会误以为：

> action 一定应该 tokenized。

但 Diffusion Policy 表明：

> continuous generative policy 是另一种 answer。

因此 FAST 的 novelty 不能写成：

> “continuous action 以前没人处理。”

而应该放在更窄、正确的 parent：

> **autoregressive VLA action representation。**

这是 nearest-prior discipline 的一个很好例子。

---

## 5.6 Action chunking 成功以后，新部署 regime 又让 chunking 自己成为问题

到 ICLR 2026 左右，一批工作开始明确研究：

- inference latency；
- asynchronous observation/action；
- action chunk overlap；
- inter-chunk discontinuity；
- reactivity loss；
- stale observation。

ACT 中 action chunking 原本解决：

> horizon / compounding error。

但当模型越来越大、推理越来越慢：

> chunk execution 与下一次 inference 并不同步。

于是成功 abstraction 带来新问题：

> **chunk 保证 temporal coherence，但降低 feedback reactivity；异步推理提高 throughput，却可能用 stale state 产生 chunk mismatch。**

一些工作因此做：

- masked/corrected action chunk；
- lightweight correction head；
- latest-observation conditioning；
- 显式区分 inference delay 与 execution horizon；
- 重新审 action-space abstraction 与 chunk horizon 的耦合。

### Primitive change

```
chunk as a cure for horizon
→ chunk as an object with its own latency/reactivity tradeoff
```

这是非常好的“success creates next problem”案例。

---

## 5.7 Robotics lineage 的 progression

```
single-step BC suffers long effective horizon
→ action chunk changes prediction unit
→ VLA turns actions into shared sequence-model tokens
→ VLA scaling makes action representation increasingly central
→ high-frequency/dexterous control exposes token correlation pathology
→ FAST redesigns representation through compression
→ larger/slower inference exposes chunk latency/reactivity mismatch
→ asynchronous correction / action-space design becomes a new object
```

这不是简单线性因果史。

但它清楚展示：

> **当 architecture、control frequency、latency regime 改变时，过去的“solution”会变成新的 assumption。**

---

## 5.8 为什么这条 lineage 对我们特别有用

它打破了一个 LLM-only 偏见：

> “科研问题主要来自 loss / representation / reasoning failure。”

robotics 里问题经常来自：

- closed-loop dynamics；
- control frequency；
- sensor/action timing；
- physical continuity；
- inference latency；
- action representation；
- embodiment heterogeneity。

这些不是 benchmark artifact。

它们是：

> **系统与现实交互后产生的 structural pressure。**

---

## 5.9 机械迁移会犯什么错

不要：

> “FAST 用 DCT，所以给 LLM hidden states 也做 DCT。”

这是最差的迁移。

真正值得学：

> 一个 cross-domain representation 被借来后，要检查源域和目标域的统计结构是否真的匹配。

RT-2 借语言 token interface：

> 在 general VLA 上 enabling。

FAST 发现 high-frequency actions 的 correlation / smoothness 与 language token statistics 完全不同：

> 因而必须重新设计编码。

所以 cross-domain idea 的第二步永远应该是：

> **representation audit。**

---

# 6. 五条 lineage 放在一起后，新看到的 meta-pattern

这部分也不是 generator。

只是第一批 longitudinal reading 后的归纳。

---

## 6.1 Frontier 经常从“是否有效”移动到“有效的 object 到底是什么”

RLVR：

> does RL work  
> → which learning signals actually matter?

ICL：

> does in-context learning happen  
> → what internal computation / representation performs it?

Diffusion：

> can sampling be accelerated  
> → which component actually controls fast-sampling quality?

Robotics：

> can VLA predict actions  
> → what action representation makes that objective learnable?

### Taste lesson

一个 field 出现巨大 positive result 时：

> 不是只追更高数字。

它通常意味着：

> **一个新的 phenomenon 终于强到值得被拆解。**

---

## 6.2 “更细粒度”不是 universal direction

例：

High-Entropy Tokens：
> sequence → token subset

GUARD：
> trajectory → critical transition

但 GSPO：
> token-level ratio → sequence-level optimization unit

ACT：
> single action → action chunk

所以绝对不能归纳：

> 细粒度更好。

真正问题是：

> **哪个 unit 与你研究的 causal / optimization object 对齐？**

---

## 6.3 成功 abstraction 经常会变成下一代的 hidden assumption

- action chunking：
  从 horizon solution → latency/reactivity assumption
- action tokens：
  从 VLA enabling interface → high-frequency correlation bottleneck
- GRPO：
  从 scalable RL solution → calibration / signal-structure questions
- global diffusion schedule：
  从 optimized component → instance/spatial uniformity assumption
- task vectors：
  从 ICL explanation → “information is added”这个更深 assumption

这是纵向 reading 比横向 paper summary 更容易看到的东西。

---

## 6.4 好的 next paper 往往不是在前一篇“没做的实验”里

例如：

FAST 不是：

> OpenVLA 没测更大的 model，所以测一个更大 model。

它抓的是：

> action tokenization 在新 control regime 下改变了 learning problem。

Information Removal 不是：

> Function Vectors 少测了一个 task。

它换的是：

> context effect 的 explanatory direction。

TORS 不是：

> previous sampler 没试某个新 solver。

它先问：

> 多个 acceleration branches 到底哪个 component 重要。

### Taste lesson

> **future-work gap 往往是局部空白；Main-sized opening 更常来自重新解释 parent work 成功所依赖的 abstraction。**

---

## 6.5 Related work 的价值不只是 kill

传统 novelty search 容易：

> 找一篇很像 → kill。

纵向读以后，related work 还有两个更重要用途：

### A. Recover saturated coordinate

知道大家已经沿什么轴反复优化。

### B. Recover inherited assumptions

知道哪些东西因为每篇 paper 都继承，所以几乎没人重新命名成 research object。

真正的 opening 往往在 B。

---

# 7. 第一批 longitudinal reading 暴露出的 blind spots

还没有读够。

下一轮优先补：

1. **Pretraining / SFT / distillation lineage**
   - 不想只研究 RL。
   - 要看 data/objective/representation 在后训练之前怎样形成新问题。

2. **Architecture / inductive bias lineage**
   - 特别是 old theoretical premise 如何被现代 architecture 改写。

3. **Multimodal/VLM—not robotics only**
   - modality fusion / visual token allocation / unified generation-understanding。

4. **Speech/audio**
   - streaming、semantic/acoustic factorization、turn-taking、full-duplex。
   - 这里 latency/causality 可能产生与 text 完全不同的 scientific pressure。

5. **一个完整 negative/limits lineage**
   - 看“不提出新 method”的强论文怎样从 related work 长成 Main story。

6. **Optimization theory lineage**
   - 重点看 assumption / dynamics，不是 optimizer acronym。

---

# 8. 当前阶段结论

这一轮之后更应该避免一句话：

> “我们要找哪一种题？”

更有用的问题是：

> **一个成熟 lineage 的 primitive 最近三年是怎么移动的？**
>
> **哪一个成功 abstraction 现在开始变成 hidden assumption？**
>
> **后一代 paper 是在加东西，还是重新定义前一代到底解决了什么？**
>
> **哪个新 deployment / scale / modality / feedback regime 使旧 abstraction 不再自然？**
>
> **哪些 surface 很热，但 underlying question 已经 saturated？**

这些问题继续用于读论文。

**现在仍不生成 CT01。**
