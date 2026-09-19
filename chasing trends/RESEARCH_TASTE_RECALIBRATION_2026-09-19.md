# Research Taste Recalibration — 2026-09-19

## 为什么要重写 chasing trends

上一版 `chasing trends/` 犯了一个和过去相反、但本质相同的错误：

过去是把：

> scientific question first

执行成了几乎唯一允许的论文形态。

这一次又差点把用户举的一个喜欢的例子：

> failure → diagnosis → mechanism → method → benchmark

执行成新的唯一范式。

这是错误的。

用户真正要求的不是“找某一种题”。

而是：

> **大量阅读真实优秀论文，研究 idea 到底是怎么从已有 literature 中长出来的；**
>
> **研究作者为什么能看到那个问题，nearest related work 留下了什么结构性空位，他们新加的到底是哪一层；**
>
> **最后从很多不同论文的生长史中归纳多种可复用的 question-forming / paper-growing paradigms。**

所以本目录现在的任务不是固定一个 search template，而是建立：

> **research genealogy library + problem-finding grammar**

在这套 library 足够成熟以前，不开始正式 CT01。

---

# 一、必须区分：paper shape ≠ idea genesis

一篇论文最后写出来可能都是：

1. motivation
2. method
3. experiments
4. analysis

但这并不意味着它们的 idea 是用同一种方式形成的。

两个最后结构看起来都像“分析 + 方法”的 paper，其 idea genesis 可能完全不同：

- 一个来自已有方法的具体 failure；
- 一个来自 objective 的数学分解；
- 一个来自部署 constraint；
- 一个来自 old theorem 的隐藏 assumption；
- 一个来自多个方法一直各自发展、但没人统一 design space；
- 一个来自成熟科学问题中新 explanatory decomposition；
- 一个来自现实 regime 改变，使旧结论的前提失效；
- 一个来自一个反直觉 empirical asymmetry；
- 一个来自跨领域理论提供新的可识别 quantity；
- 一个甚至只是发现社区一直 optimize 错 proxy。

因此：

> **不允许从最终论文结构反推一个机械的选题模板。**

真正应该学习的是：

> **Question ancestry。**

---

# 二、当前 deep-read 后确认的 8 种不同 genealogy

以下不是“以后只能从这八种找题”。

它们只是第一批被真实强论文证明存在的 idea-growth pattern。

---

## GENEALOGY A — 成功方法内部存在未拆开的 learning signal

### 代表：The Surprising Effectiveness of Negative Reinforcement in LLM Reasoning  
NeurIPS 2025

这个 idea 不是从：

> “RLVR 有 failure，我们来修。”

开始的。

RLVR 本身已经很成功。

真正的切口是：

> **一个成功 objective 同时包含两种本质不同的 update：提高正确样本概率，以及降低错误样本概率。社区通常把它们作为一个整体谈论，但没有真正拆开。**

于是作者做的第一步不是提算法，而是**objective decomposition**：

> RLVR = PSR + NSR

一旦拆开，就出现一个此前不可见的问题：

> 正样本 reinforcement 和负样本 reinforcement 到底分别教会模型什么？

然后才得到反直觉结果：

- PSR 提 Pass@1，却压 diversity、伤高 k；
- NSR 单独就能在整个 Pass@k spectrum 上改善，甚至逼近/超过完整 PPO/GRPO。

接着 gradient analysis 给出解释：

> NSR 主要在 suppress 已有错误路径，然后让 probability mass 按 pretrained prior 重新分配，而不是强行灌入一个具体正确 path。

最后 Weighted-REINFORCE 只是这个发现非常自然的 downstream consequence。

### 真正可以学的不是

> “以后多拆 positive / negative。”

而是：

> **社区把一个成功整体当成 atomic object 时，先检查它是不是由功能不同的 constituent operations 组成。**

这个 question 在 method 出现以前已经成立。

---

## GENEALOGY B — 真实 deployment constraint 没进入算法状态

### 代表：Aligning Tree-Search Policies with Fixed Token Budgets in Test-Time Scaling of LLMs  
ICML 2026

这个 idea 也不是 mechanism-first。

related work 已经有大量：

- test-time scaling；
- MCTS；
- PUCT；
- dynamic widening；
- verifier-guided search。

作者没有问：

> “还能不能发明一个更聪明的 tree search？”

而是看部署：

> **真实系统给每个 query 的 token budget 是固定且可变的。**

然后检查现有算法发现：

> budget 只被当作 termination condition；
> search policy 本身并不知道“还剩多少预算”。

这是一个非常具体的 structural mismatch。

于是问题自然变成：

> 一个 fixed-budget search policy 为什么在 90% budget remaining 和 5% budget remaining 时还应该做相同的 exploration / widening 决策？

BG-MCTS 后面的 wide-to-deep schedule 几乎从问题定义里直接出来。

### 真正的 genealogy

> mature method
> → inspect actual deployment contract
> → find an important variable treated only externally, not as policy state
> → turn it into conditioning variable
> → derive behavior change.

这类题不需要“内部机制”才能成立。

---

## GENEALOGY C — fragmented methods → unified design space → find dominant bottleneck

### 代表：Analyzing and Improving Training-Free Fast Sampling of Text-to-Image Diffusion Models  
ECCV 2026

这个 paper 最值得学习的不是 TORS 本身。

在它之前：

- fast ODE solver；
- timestep scheduling；
- feature caching；

都有大量工作。

如果机械 follow related work，会变成：

> 再设计一种 solver / cache / schedule。

作者做的是反方向：

> **先把三个分支统一成一个 design space。**

在 matched setting 下拆成：

- solver；
- outer schedule；
- inner schedule；
- cache object；
- feature predictor。

然后系统问：

> 到底哪个 component 真正决定 few-step quality？

结果不是“每个都重要”，而是发现：

> outer schedule 的影响最大；
> early sampling stage 更值得计算；
> 一些看起来 fancy 的 cache/solver 改进反而作用有限或 model-dependent。

这一步才把 search space 从：

> “五个地方都可以创新”

收缩成：

> “应该解释和优化 outer schedule”。

再进一步用 sampling trajectory geometry（curvature + torsion）长出 TORS。

### 真正的 genealogy

> literature fragmentation
> → common coordinate system
> → component attribution
> → dominant factor
> → deeper theory/geometry
> → method.

这和“看到一个 failure 再修”完全不是一回事。

---

## GENEALOGY D — final failure 已知，但 attribution unit 错了

### 代表 1：Reasoning Fails Where Step Flow Breaks  
ACL 2026

已有大量 work 知道：

- long CoT 会错；
- attention / saliency 能分析 token；
- test-time scaling 可以补性能。

作者真正看到的问题是：

> **现有 attribution unit 是 token，但 reasoning 的 natural unit 是 step。**

也就是说，gap 不是“没有 interpretability signal”，而是：

> signal 的粒度与 scientific object 不匹配。

Step-Saliency 首先是一种重新选择分析坐标系：

> token→token  
> 变成  
> step→step across depth。

新的坐标系才让 Shallow Lock-in / Deep Decay 变得可见。

StepFlow 是后续 consequence。

### 代表 2：Dissecting Failure Dynamics in Large Language Model Reasoning  
ACL 2026

这里的切口又不同。

社区已经知道 reasoning failure 和 test-time scaling。

作者问的是：

> **错误到底均匀积累，还是有 failure onset？**

于是把 trajectory 从最终正确/错误重新分解成：

> valid prefix → first invalid transition → post-onset evolution。

结果发现：

- >85% failure onset 在前 30%；
- 43.5% 错误 trajectory 只有一个 invalid segment；
- onset 后往往还会生成很长、局部 coherent 的错误尾巴；
- 同一 state 的 alternative continuation 仍可能正确。

于是“多想一点”被改写成：

> **在关键 transition 处换 branch。**

### 真正可以学的

> 一个现象可能已经被研究很多年，但 community 选择的 **analysis unit / event boundary / causal coordinate** 仍可能太粗。

换 unit 本身可以打开新问题。

---

## GENEALOGY E — mature object，不换现象，换 explanatory decomposition

### 代表：Mechanism of Task-oriented Information Removal in In-context Learning  
ICLR 2026

ICL mechanism 已经是极拥挤领域。

prior 已有很多解释：

- induction / copying；
- function vectors；
- task vectors；
- Bayesian / implicit learning；
- attention head analyses；
- representation shifts。

如果 novelty 标准是：

> “ICL mechanism 已经有人做”

这篇论文根本不应该存在。

它真正的新东西不是“再找一个 head”。

作者换掉了 decomposition：

> few-shot demos 未必主要是在“写入/增加 task information”；
>
> 它也可能是在从一个本来包含多任务可能性的 entangled representation 中**选择性删除 task-irrelevant information**。

这是 explanatory direction 的翻转：

> addition → removal。

作者先证明：

- zero-shot state 里多个 task-relevant alternatives 共存；
- 人工 low-rank removal 可以把模型推向特定 task；
- few-shot ICL 的 state evolution 与这种 selective removal 对应；
- 再定位 Denoising Heads；
- 最后 ablate computation。

### 真正的 genealogy

> crowded object
> → audit what all current explanations implicitly treat as the primitive operation
> → propose an orthogonal/deeper decomposition
> → build measurements specifically distinguishing the new decomposition
> → causal localization.

所以：

> **“parent 很拥挤”与“没有新问题”完全不是一回事。**

---

## GENEALOGY F — old conclusion depends on a hidden asymptotic / structural premise

### 代表：A Little Depth Goes a Long Way  
NeurIPS 2025

已有理论指出：

> fixed-depth Transformers 对某些 sequential reasoning 问题有表达限制。

机械 follow-up 可能是：

> 再证明一个 impossibility。

作者反而检查 theorem 的 premise：

> prior 通常把 depth 当作与 input length 无关的 constant；
> 但实际模型的最大 context length 是 bounded 的。

于是问题被改写：

> 如果 depth 只需要随 context length 极慢增长，会发生什么？

结论：

> Θ(log n) depth 已经能跨过 fixed-depth 的一些表达障碍，而且在 width / CoT scaling 对比中更高效。

这里没有“bug”，也没有“机制→方法”。

idea 来自：

> **检查一个强结论到底依赖哪个 load-bearing idealization。**

### 可迁移原则

读理论 paper 时，不只问：

> theorem 证明了什么？

要问：

> **它为了得到这个结论，固定了什么？取了什么极限？默认了什么不随规模变化？**

改变一个真正 load-bearing premise，老问题会重新变成新问题。

---

## GENEALOGY G — prior phenomenon 只在一个 artificial regime 成立

### 代表：Chain-of-Thought Reasoning in the Wild Is Not Always Faithful  
ICML 2026

CoT unfaithfulness 不是新现象。

prior 已经用：

- injected hints；
- explicit bias；
- adversarial manipulations；

证明 CoT 不总忠实。

如果只看关键词 overlap，这题应当直接被杀。

但作者看到的是：

> **我们真正关心的是正常使用时能否把 CoT 当作可信 monitor；而 prior 主要证明的是人为加入 bias 后会不忠实。**

所以 load-bearing premise 是：

> unfaithfulness 是否依赖 external bias injection？

作者把 intervention 去掉，转而寻找 natural prompt 中可检测的不忠实：

- logical inverse questions 出现 post-hoc rationalization；
- hard math 中出现 illogical shortcut。

### 真正 genealogy

> known phenomenon
> → inspect whether evidence only exists in a distorted/artificial regime
> → ask whether the claimed practical interpretation survives when distortion removed.

这不是“old problem + new model”。

是：

> **old evidence does not identify the real-world quantity people are using the result to talk about。**

---

## GENEALOGY H — identify an invariant/property that explains success across a mature method family

### 代表：DC-Merge: Improving Model Merging with Directional Consistency  
CVPR 2026

model merging 已有很多方法分别处理：

- sign conflict；
- magnitude；
- task interference；
- low-rank structure。

作者不是再加一个 heuristic。

他们问：

> **无论你怎么 merge，究竟什么 property 被保留下来时 task ability 才能保住？**

然后用 SVD 把 task vector 拆成 knowledge directions + singular-value energy，观察到：

> performance 更依赖 directional geometry 是否保持，而不是 energy 本身精确保持。

于是定义 DirSim，再指出两个破坏它的来源：

- energy imbalance 让弱但重要方向被淹没；
- parameter-space geometric inconsistency 让方向被扭曲。

后面的 smoothing + shared orthogonal projection 都是为了维护这个 property。

### 真正 genealogy

> many heuristics solve same engineering problem
> → search for a common success invariant
> → show invariant predicts performance
> → diagnose why existing methods violate it
> → design method to preserve it.

这种路子特别适合跨领域迁移。

---

# 三、这八类之间最重要的共同点

不是：

> 都有 mechanism。

而是：

> **它们都先改变了“应该把什么当成问题”的坐标系。**

Negative Reinforcement：
> RLVR → PSR / NSR

BG-MCTS：
> token budget → termination condition / policy state

TORS：
> isolated acceleration tricks → unified design space

StepFlow：
> token attribution → step-flow attribution

GUARD：
> incorrect trajectory → failure onset transition

Cho：
> information addition → information removal

A Little Depth：
> fixed-depth impossibility → minimally growing depth

CoT faithfulness：
> adversarial unfaithfulness → natural unfaithfulness

DC-Merge：
> merge heuristic → preserved geometric property

真正的高价值 move 往往发生在**方法提出以前**：

> **重新定义 scientific / algorithmic object。**

---

# 四、以后读 related work，不能再问“谁没做过这个格子”

每篇 core paper 都要画 lineage：

## 1. Parent problem

这个大问题什么时候开始被提出？

## 2. Dominant decomposition

近几年 community 默认怎样拆这个问题？

## 3. Nearest siblings

和这篇最像的 3–8 篇，不是关键词最像，而是 reviewer 最可能引用的。

## 4. Saturated axis

related work 已经沿哪些轴做得很多？

例如：

- more compute；
- better scorer；
- more data；
- new optimizer；
- finer probe；
- another benchmark。

这些通常不是我们应该继续挖的轴。

## 5. Unexamined assumption

大家有哪些东西一直固定不动？

## 6. Missing relation

两个成熟子 literature 之间是否存在没有解释清楚的关系？

## 7. Changed premise

新模型 / 新 inference / 新 training regime 到底改变了什么 load-bearing premise？

## 8. New coordinate

这篇优秀论文最终把什么旧 object 换成了更有解释力的 object？

---

# 五、深读论文的强制输出，不再是“12 个模板问题”

以后每篇真正用于 taste calibration 的 core paper，至少输出一张 genealogy card：

### Paper

标题 / venue / year

### One-sentence result

它最后做成了什么。

### Pre-paper world

假设这篇论文还不存在，community 已经知道什么？

### Immediate parents

3–8 篇/类最危险 prior 分别解决了什么？

### What looked “done”

为什么一个浅阅读者会觉得这个方向已经没什么新东西？

### Hidden opening

作者真正抓住了什么尚未被当作 object 的东西？

### Question-forming move

是 decomposition / assumption audit / regime change / unit change / invariant / contradiction / constraint / design-space unification / 其他？

### First decisive experiment

哪一个最小实验第一次让新 question 获得 empirical support？

### Paper-growth step

从这个 seed 到完整 Main paper，后面加的实验分别承担什么逻辑职责？

### Relation to method

method 是：
- mother contribution；
- consequence；
- validation；
- none。

### Counterfactual

如果核心结果反过来，这个项目还能怎么写？如果不能，为什么仍值得做？

### Reviewer compression

最危险的一句话压缩是什么？作者为什么没有被压死？

### Transferable grammar

真正可迁移的是哪一个问题形成动作？

### Non-transferable surface

哪些名词 / method / benchmark 绝对不该机械复制？

---

# 六、下一阶段的阅读规模

正式找题前，应该先完成两层阅读：

## Breadth scan

用 PaperNotes / conference pages 建图：

- ACL / EMNLP / NAACL
- ICLR / ICML / NeurIPS
- AAAI
- CVPR / ICCV / ECCV
- 必要时 robotics / speech / multimodal / optimization

每个重点 lineage 先扫几十篇的：

- title；
- abstract；
- related cluster；
- method shape；
- citation neighborhood。

目标不是“读懂”。

目标是：

> **看到 field 在沿哪些轴拥挤地移动。**

## Deep genealogy

至少挑 12–20 篇不同 lineage 的 core papers。

每篇真正读：

- Introduction
- Related Work
- problem setup
- decisive experiment / theorem
- method derivation
- main ablation
- limitations/discussion

并向下追 immediate parents。

真正目标是：

> **知道这个 idea 在论文出现之前，站在作者的位置为什么可能被看见。**

---

# 七、停止使用固定的“好题公式”

以下任何一句都不能再成为 search generator 本身：

- 找一个 failure 再修；
- 找一个 mechanism；
- 找两个 quantity separation；
- 找一个 changed premise；
- 找一个 asymmetry；
- 找一个 train-test mismatch；
- 找一个 hidden oracle；
- 找一个 invariant。

这些都只是：

> **已经观察到的 research moves。**

以后必须：

> literature → pressure → question

而不是：

> template → 找一个能填进去的例子。

---

# 八、当前状态

这一轮现在仍然是：

> **TASTE RECALIBRATION / LITERATURE STUDY**

不是 topic search。

不注册 CT01。

下一步应该继续扩大 genealogy library，尤其补：

- EMNLP / NAACL 的普通强 Main；
- ICML / ICLR 非 reasoning 的 training / optimization work；
- CVPR / ECCV 的 generation / multimodal；
- 至少几篇“没有提出新方法但问题非常漂亮”的 paper；
- 至少几篇“方法很强但 scientific story 很弱”的 contrast paper；
- 至少几条同一 lineage 连续 3–5 篇的 genealogy，而不是孤立 paper。

只有在这一步足够厚以后，才应该重新问：

> 我们自己下一题从哪里长出来。
