# Paper Genealogy Guide

这份文件回答：

> **一篇真正优秀的论文，到底该怎么读，才能学到“它的问题是怎么被看到的”，而不是只记住它最后用了什么方法？**

---

# 1. 第一原则：不要从 final method 读论文

最常见的错误阅读方式：

> Paper A 提出 Method M，解决 Task T，提升 X%。

这种阅读对复现工程有用，对找题几乎没用。

真正要恢复的是：

> **在 Method M 出现以前，作者面对的 literature 长什么样？**
>
> **为什么这个问题并没有被已有论文自然解决？**
>
> **作者做了哪个 conceptual move，才让新 question 变得可见？**

所以 paper autopsy 的单位不是：

> method

而是：

> **question genealogy**。

---

# 2. 一篇 core paper 至少要读哪些部分

不能只看 abstract。

最低要求：

## A. Introduction

要找：

- 作者如何描述 field 的 dominant story；
- 哪些 prior 被当成主要成功路线；
- 哪个 gap 被认为真正阻碍 progress；
- 第一段和最后一段之间，scientific object 是否发生了变化。

## B. Related Work

不是为了查重。

要画：

- parent lineage；
- sibling lineages；
- competing decompositions；
- saturated axes；
- 哪些 prior 看起来“已经很像”。

最重要问题：

> **为什么这些相似 prior 没把这篇压死？**

## C. Problem setup / formalism

这里常常藏着真正的新意。

检查：

- 作者新增了哪个 state variable；
- 把什么 quantity 从外部 condition 变成了模型内部变量；
- 把什么 monolithic object 拆成多个 component；
- 换了哪个 analysis unit；
- 哪个以前固定的东西现在允许变化；
- 哪个平均量被改成 conditional / local / trajectory-level quantity。

## D. First decisive experiment / theorem

不是 main benchmark table。

找：

> **哪一个结果一旦成立，整篇 paper 才真正有理由继续？**

这往往是：

- decomposition 后的 asymmetry；
- matched control；
- phase transition；
- invariant correlation；
- failure onset；
- theorem 改变旧结论；
- dominant component attribution。

## E. Method derivation

问：

> 如果我只知道前面的 finding，能不能大致猜出 method 应该长什么样？

如果完全猜不到：

> method 很可能是后来拼上的。

如果 method 几乎自然推出：

> 这个 paper 的 intellectual chain 很强。

## F. Ablation / boundary / bad case

最有价值的不一定是“去掉 module 掉多少”。

更重要：

- 哪些 regime method 不该有效；
- 哪类 error 不在 scope；
- nearest alternative explanation 是否真的被排；
- gain 是否只是更多 compute。

## G. Limitations / Discussion

看作者自己承认：

- claim 到哪里停止；
- 哪个 causal link 仍是 suggestive；
- 哪个 assumption 未验证。

这些经常就是 lineage 下一篇真正可能长出来的地方。

但：

> **future work 不是自动的 candidate generator。**

---

# 3. 必须向下追 immediate parents

对每篇 core paper，不要只读它自己。

至少找 3–8 个 immediate parent / sibling。

定义：

> 如果没有这篇新 paper，reviewer 最可能用哪几篇来回答“这不是早就有人做了吗？”

对每个 parent，只回答三个问题：

1. 它真正 claim 了什么？
2. 它固定了什么？
3. 它没有区分什么？

然后画成：

```
Parent A: solved X under assumption P
Parent B: solved Y with object O
Parent C: observed phenomenon F but used coarse measurement M

                 ↓ new paper changes one load-bearing thing

New paper: asks Z
```

---

# 4. Saturated axis audit

一个领域不是“有人做过”或“没人做过”二元状态。

要问：

> **它在哪些轴上已经卷烂了？**

例：

test-time scaling 里可能已经卷：

- more samples；
- better verifier；
- deeper tree；
- self-consistency；
- adaptive compute。

但没人认真把：

> **remaining deployment budget**

放进 policy state。

所以 BG-MCTS 的 opening 不在“tree search 还没人做”。

而在：

> **大家都在同一组 axis 上优化，却把一个真实 control variable 留在算法外面。**

以后每个 literature map 都要写：

### Saturated axes

已经有很多 paper 的方向。

### Frozen axes

几乎所有 paper 默认固定的东西。

### Coupled quantities

总是一起变化、没人拆开的量。

### Missing relation

两个成熟 literature 间没有解释清楚的关系。

---

# 5. 观察 paper 中的“坐标变换”

强论文经常做的不是：

> 在旧坐标系里测得更准。

而是：

> **换了一个更能暴露问题的坐标。**

目前看到的例子：

### Object decomposition

RLVR  
→ PSR / NSR

### Policy-state augmentation

budget  
→ 从 stopping condition 变成 policy state

### Unit change

token saliency  
→ step-to-step flow

### Event change

wrong trajectory  
→ first invalid transition + post-onset dynamics

### Process direction change

information addition  
→ information removal

### Asymptotic premise change

fixed depth  
→ minimally growing depth

### Evidence-regime change

biased / adversarial CoT  
→ natural prompts

### Property change

merge score / magnitude  
→ directional consistency

### Design-space change

solver/cache/schedule 分散 methods  
→ unified component space

找题时真正值得问：

> **当前领域的坐标系是不是把重要结构平均掉了？**

---

# 6. 如何判断 idea 是“长出来的”还是“拼出来的”

## 长出来

前一节结果自然制造下一节问题。

例如：

> 拆 PSR/NSR
> → 发现 NSR 特别强
> → gradient 分析为什么
> → upweight NSR

或者：

> 统一 sampling design space
> → schedule 最重要
> → uniform schedule 在 early stage 不够密
> → trajectory geometry
> → TORS

每一步都有必要性。

## 拼出来

常见形态：

> 发现 A
> → 加一个 B module
> → 再加 C loss
> → 再做 D curriculum
> → benchmark 涨了

但 B/C/D 任意替换都说得通。

这类 work 即使能中，也不应该作为我们主要 taste。

---

# 7. 同一 paper 应该做 counterfactual reading

问：

> 如果作者第一个关键实验得到相反结果，paper 会往哪里长？

这不是要求所有结果都能发。

而是判断：

> **问题到底先于 answer，还是整个故事只是围绕一个 lucky effect 拼的？**

例如 Negative Reinforcement：

如果 NSR 很弱而 PSR 独占作用：

> “RLVR 两类 signal 扮演不同角色”仍然是合理 question，只是 method direction 会不同。

TORS：

如果 unified design-space study 发现 solver 而不是 schedule 是 dominant：

> paper 仍然可以沿 solver bottleneck 长。

BG-MCTS：

如果 budget-awareness 完全不改善：

> deployment mismatch question 仍可回答为“standard policy 自然 robust”，但 method story 会死。

这个 distinction 很重要：

> **question robustness ≠ method robustness。**

---

# 8. 同一 lineage 必须纵向读，不只横向抽样

只看 20 篇彼此无关的论文，会得到 20 个漂亮 story，但学不到 research progression。

必须选几条 lineage，连续追 3–8 篇。

例如未来可以追：

## Reasoning RL lineage

- vanilla RLVR / PPO / GRPO
- outcome-reward mechanism analyses
- entropy / token-level credit
- positive-negative decomposition
- calibration / advantage bias
- selective / hierarchical update

问：

> 每一篇把 primitive 从什么换成什么？

## Test-time scaling lineage

- self-consistency
- verifier-based selection
- tree search
- process reward / MCTS
- adaptive compute
- budget-aware search
- failure-onset repair

问：

> research object 怎样从“more compute”变成“where/how to spend compute”？

## ICL mechanism lineage

- induction / meta-learning
- task vectors / function vectors
- causal heads
- task-conditioned representation
- information removal

问：

> explanation space 是怎样一步步改写的？

## Diffusion fast sampling lineage

- solver
- timestep scheduling
- feature caching
- unified design space
- geometry-aware schedule

问：

> 为什么某一轮开始从“新 trick”转向“先比较 design components”？

---

# 9. 不同 paper type 要学不同东西

## Method paper

主要学：

> method 为什么是自然 consequence？

## Mechanistic paper

主要学：

> explanatory decomposition 为什么 prior 没有？

## Theory paper

主要学：

> theorem 的 assumption audit 与 regime selection。

## Empirical phenomenon paper

主要学：

> 为什么 prior evidence 不能回答真实问题？

## Benchmark / dataset paper

即使不想做 benchmark，也可学：

> field 到底因为缺什么 observation 才无法推进？

但不要机械变成 dataset idea。

## Negative / limits paper

主要学：

> 哪个被默认相信的 inference 被打断？

## Systems paper

学：

> real operational constraint 如何产生新 algorithmic object。

---

# 10. Paper genealogy card 模板

以后每篇 core paper 建卡：

## Identity
- title
- venue/year
- lineage
- paper type

## Pre-paper state
- field already knew
- dominant method/explanation
- saturated axes

## Immediate parents
- P1
- P2
- P3
- ...

## Hidden opening
- frozen assumption
- conflated quantity
- wrong unit
- missing relation
- unexplained asymmetry
- real-world regime not covered
- other

## Question-forming move
一句话。

## First decisive evidence
一句话。

## Growth chain
```
seed
→ observation/theorem
→ new object
→ next question
→ method/analysis
→ validation
```

## Why related work did not cover it
必须具体写。

## Reviewer compression
最危险的一句话。

## Why compression is incomplete
必须基于 evidence，不靠 rhetoric。

## Transferable grammar
抽象层。

## Surface to NOT copy
具体名词/方法/数据。

---

# 11. Breadth scan 的正确角色

Breadth scan 不需要每篇全文。

可以用 PaperNotes 快速扫描数百篇，目的只有：

- 建 field map；
- 看哪些关键词/方法突然密集；
- 发现 repeated assumptions；
- 找 sibling clusters；
- 找值得 deep-read 的核心 paper。

但不能：

> 用 PaperNotes 摘要直接判断 novelty。

真正到 candidate collision audit：

> 回原文。

---

# 12. 最终训练目标

不是背：

> “强论文有 8 种范式。”

而是学会面对一个新领域时，自动问：

> 这个领域最近两年把什么 object 当成基本单位？
>
> 哪些 axes 已经被扫完？
>
> 哪个 quantity 一直被当成 proxy？
>
> 哪些 variables 被默认绑在一起？
>
> 哪个 deployment / architecture / training premise 已经变了？
>
> 哪几篇 paper 的结果其实无法被一个简单 story 同时解释？
>
> 最近最强论文是沿着 related work 的哪条缝长出来，而不是从空白处凭空冒出来？

当这些问题变成自然习惯，才算真正建立科研选题 taste。
