# Longitudinal Genealogies 02 — Pretraining, SFT, Distillation, Architecture

> **Status: literature / taste calibration only.**
>
> 本文件继续做纵向 lineage reconstruction，不生成 CTxx，不把任何 pattern 直接转成候选题。
>
> 本轮特别补上一批上一版明显偏少的方向：
>
> - pretraining / scaling / data mixture；
> - SFT 对 knowledge 的作用；
> - knowledge / CoT distillation；
> - architecture / inductive bias / recurrent depth。
>
> 这些方向的重要性在于：它们可以检验我们从 reasoning-RL 中归纳出来的 intuition 是否真的一般化，还是只适用于当前热点。

---

# 0. Genealogy evidence discipline

从这份文件开始，所有 lineage relation 分三档：

### [DIRECT]
后一篇明确引用 / 定位前一篇，并把它视为 parent/problem context。

### [FIELD]
两篇属于公开 literature 中可确认的同一 problem family，但不声称作者的 idea 是直接由前一篇产生。

### [RECONSTRUCTED]
为了理解 frontier movement 做的事后 conceptual reconstruction。只允许说：

> 在后一篇出现以前，field 已经拥有这些 objects / assumptions，因此后一篇改变了某个坐标。

不允许说：

> 作者“就是因为”某篇论文才想到它。

这是为了避免 hindsight storytelling。

---

# LINEAGE 6 — Pretraining Scaling：从 N/D/Compute 的光滑规律，到 data composition / repetition / capacity allocation

## 6.1 Kaplan-style scaling laws — 先把“scale”本身变成可预测对象 [FIELD]

**Scaling Laws for Neural Language Models (2020)**

这一代工作的关键，不是简单说：

> 大模型更好。

而是把：

- model size (N)
- dataset size (D)
- compute (C)

与 language-model loss 的关系变成经验幂律。

这件事改变了 field 的 planning object：

> 训练预算不再只是“能训多大就训多大”，而可以问 compute-optimal allocation。

### 当时默认的 abstraction

dataset 主要被表示成：

> **多少 token。**

数据内部：

- domain composition；
- document quality；
- duplication；
- knowledge density；
- curriculum；

在 scaling-law 主坐标里都被大量压缩掉。

这不是说早期作者“不知道数据质量”。

而是：

> scaling law 的 scientific object 为了可建模，主动把复杂数据压成了 (D)。

---

## 6.2 Chinchilla — scaling law 没死，compute allocation 被重估 [DIRECT/FIELD]

**Training Compute-Optimal Large Language Models (2022)**

Kaplan-style结论推动了：

> 让 model 很大、token 相对较少。

Chinchilla 用更系统的 model/data scale sweep 重新估计 compute-optimal front，得到：

> 在其实验 regime 下，model size 与 training tokens 应更接近平衡扩展。

### 这里真正值得学的 research move

它不是：

> “Scaling law 不对。”

而是：

> **一个已被广泛采用的 empirical law 可能因为 experimental grid 覆盖不足，而把最优资源分配方向估偏。**

换句话说：

```
scaling law
→ used for planning
→ therefore errors in fitted regime become operationally important
→ broader controlled sweep can change recommended allocation
```

### 但对我们的 execution 是负面范例

这种 work 需要：

- 大量 model scale；
- 大量 token budget；
- dense sweep；

不是适合我们当前 compute 的题型。

它的价值主要在：

> **如何挑战一个已经 institutionalized 的 empirical rule。**

不是：

> 我们也去重新拟合一次 scaling law。

---

## 6.3 Data-mixture optimization — (D) 不再是一个 scalar [FIELD]

随着 pretraining corpus 越来越异质，新的现实 pressure 变强：

> 相同 token 数的不同 domain mixture，训练结果可以完全不同。

于是 data mixture 从：

> preprocessing choice

逐渐升格成：

> **optimization variable。**

DoReMi 一类工作把 domain reweighting显式化；到 **Scaling Laws for Optimal Data Mixtures (NeurIPS 2025)**，更进一步把传统 scaling-law 的对象从：

```
L(N, D)
```

扩成：

```
L(N, D, h)
```

其中 (h) 是 domain weight vector。

论文尝试用少量小规模 runs：

> 预测更大 scale、未见 mixture 下的 loss 与 optimal mixture。

### Primitive change

```
data amount
→ data amount + structured composition
```

这里不是简单：

> “data quality matters”。

真正变化是：

> **composition 被纳入可外推的 scaling object。**

---

## 6.4 Phase transitions — mixture 不一定只是平滑地改变 loss [FIELD]

**Data Mixing Can Induce Phase Transitions in Knowledge Acquisition (NeurIPS 2025)**

这是这条 lineage 中非常值得 taste calibration 的反向结果。

如果已经相信：

> mixture weight (h) 可以平滑地进入 scaling law，

一个自然但未必正确的 intuition 是：

> mixture 改一点，knowledge acquisition 也平滑地改一点。

这篇 controlled study 发现：

- knowledge-dense data 单独训练时可以比较平滑；
- 与 web data 混合后，随着 model size / mixing ratio 变化，某类知识 acquisition 可以突然跨过 critical point；
- 低于某个 mixing ratio，几乎学不到；超过以后快速增长；
- 作者用 capacity allocation / knapsack-like picture 解释 discontinuity。

### Primitive change

```
data mixture as a smooth performance knob
→ data mixture as a capacity-allocation problem with regime changes
```

### 为什么这比“又一个 data mixing method”更值得学

它攻击的不是某个 optimizer。

而是：

> **把 global validation loss 的平滑 scaling，和特定 knowledge 的 acquisition dynamics 区分开。**

也就是：

> average metric 可以很 smooth，
> internal capability allocation 却可能是 discontinuous。

这是一种非常普遍、但不能机械复制的 scientific warning。

---

## 6.5 Repetition — “unique token count”也不是完整 data quantity [FIELD]

**Datasets, Documents, and Repetitions: The Practicalities of Unequal Data Quality (NeurIPS 2025)**

高质量 filtering 带来一个现实矛盾：

> 数据更干净，但可用 unique data 变少。

过去很容易把重复理解成：

> 数据不够时的次优妥协 / overfitting risk。

这篇系统研究：

- filtered dataset；
- larger noisy superset；
- repeated epochs；
- document-level repeat count；
- training recipe interaction。

它得到的经验结论之一是：

> 合适 recipe 下，重复高质量过滤数据若干 epoch，可以优于一次扫过大得多的 superset；document 也不应该都具有相同 repeat count。

### Primitive change

```
D = number of seen tokens / unique corpus size
→ exposure count is itself structured by document quality
```

这进一步打碎：

> “更多独立 token 永远是同一种资源”

的 abstraction。

---

## 6.6 Hyperparameter scaling — recipe 也开始进入 scaling object [FIELD]

**Power Lines: Scaling Laws for Weight Decay and Batch Size in LLM Pre-training (NeurIPS 2025)**

这类工作把：

- weight decay；
- batch size；
- learning rate timescale；

也写进随着 (N,D) 变化的规律。

例如论文报告：

> optimal AdamW timescale 与 tokens-per-parameter ratio (D/N) 呈系统关系；
> optimal / critical batch size 更强依赖 (D) 而不是简单依赖 (N)。

### lineage signal

传统 scaling law 一开始想用很少维度描述训练。

随着 field 成熟：

> 被早期 abstraction 当成“recipe details”的变量，一个个升级成 scaling coordinate。

这说明一个 empirical law 的发展经常不是：

> law A → law B 把 A 推翻。

而是：

> **law A 的 residual structure 逐渐被解释成 previously marginalized variables。**

---

## 6.7 这条 lineage 的整体 movement

```
scale can be summarized by N / D / compute
→ compute-optimal N:D allocation is itself empirical
→ D is heterogeneous: domain mixture matters
→ mixture can be modeled as a vector h
→ capability acquisition under mixtures can become discontinuous
→ exposure/repetition is another data coordinate
→ optimizer hyperparameters themselves scale with N,D
```

### 一个重要 lesson

> **“scale”从来不是天然 scalar。**

field 一开始必须压缩问题才能建立规律；
后续工作常常做的不是否定规律，而是：

> 找到哪个被压缩掉的 structured variable 已经大到不能再忽略。

---

## 6.8 为什么这条线不适合直接变成我们的 candidate generator

危险做法：

> “找另一个变量加进 scaling law。”

这会立刻变成：

- huge sweep；
- expensive pretraining；
- model zoo；
- curve fitting；
- data-centric。

这恰好踩我们的 execution risk。

真正值得学习的是：

> **识别一个 dominant abstraction 在什么 regime 开始失效。**

是否需要 giant sweep：

> 是另一个 gate，不能因为科学问题漂亮就忽略。

---

# LINEAGE 7 — SFT：从“教会模型怎么回答”到“它到底怎样修改已有 knowledge”

## 7.1 Instruction tuning / LIMA — SFT 最初的强故事是行为适配，而不是写入世界知识 [FIELD]

instruction tuning 成功后，一个越来越强的经验是：

> pretrained model 已经拥有很多 capability / knowledge；
> SFT 可以用远少于 pretraining 的数据显著改变它“怎样使用这些能力”。

**LIMA: Less Is More for Alignment (2023)** 是一个极端而有影响力的表达：

> 约一千条精心选择的 example 就可以得到很强的 instruction-following behavior。

它强化了一个 worldview：

```
pretraining = knowledge / broad capability
SFT = response style / instruction use / alignment
```

这个 worldview 很有用，但也很粗。

---

## 7.2 New-knowledge fine-tuning — “SFT 能不能把新事实写进去？”开始被单独问 [FIELD]

**Does Fine-Tuning LLMs on New Knowledge Encourage Hallucinations? (EMNLP 2024)**

如果 SFT 只是：

> “给 input-output pair，模型学会它”，

那训练数据里的：

- pretrained-known facts；
- truly new facts；

似乎只是不同内容。

这篇 controlled work 把两者分开，发现：

> new knowledge 相比与 pretrained knowledge 一致的数据，学得更慢；
> 当新知识最终被学进去时，模型在原有知识上的 hallucination tendency 也会上升。

### Primitive change

```
SFT example
→ example relative to the model's pre-existing knowledge state
```

这一步非常关键。

从此以后：

> dataset item 不再只由文本内容定义。

它还有一个 model-relative property：

> **模型训练前到底掌握多少。**

这与传统 data quality 完全不同。

---

## 7.3 Token/parameter dynamics — 从“哪些数据伤 knowledge”下沉到“哪些 updates 在伤” [DIRECT/FIELD]

**Analyzing the Effects of Supervised Fine-Tuning on Model Knowledge from Token and Parameter Levels (EMNLP 2025 Main)**

前面的 phenomenon 已经足够制造下一问：

> 为什么更多 SFT data 反而可能让 closed-book knowledge 更差？

论文在 5 个 LLaMA-2/3 family models 上做 CBQA，报告：

- 1,920 SFT samples 某些设置下可比 240 samples 低最多约 14%；
- training data 的 knowledge mastery 改变可带来 >12% 波动；
- token-level KL 呈现与 data amount / mastery 相关的 dynamics；
- parameter-level restoration 显示大量 update 并不贡献于 knowledge enhancement；论文报告可高达约 90%。

### Question-forming move

不是：

> “SFT 会 forgetting，做 anti-forgetting。”

而是先把 SFT effect 从：

```
dataset → final accuracy
```

改成：

```
dataset relative to current knowledge
→ token distribution change
→ parameter update decomposition
→ knowledge behavior
```

### 为什么这个 paper 比泛泛的 catastrophic forgetting 更 sharp

它不是只比较：

> before vs after。

而是试图识别：

> **SFT update 中哪些部分真的和 knowledge enhancement 有关。**

这让 method 可能从 observation 长出来，而不是先加 regularizer。

---

## 7.4 Massive SFT sweeps — 一个非常重要的 contrast case [FIELD]

2025 也出现使用 **1,000+ fine-tuned models** 的大规模 SFT empirical study，系统研究：

- data volume；
- model；
- dataset；
- perplexity；
- layer change；

与 downstream performance 的关系。

这类论文对 field map 很有价值，因为它可以：

> 从大量 runs 中找稳定规律。

但它是我们的**负面 execution archetype**：

> 科学上可能有信息量，
> 但如果一条 question 只有靠 1000 个模型 sweep 才有说服力，
> 对我们就是极高风险。

### 重要区别

> **strong paper ≠ suitable project for us。**

我们学习它提供了哪些 variables / regularities。

不学习：

> 它的 compute shape。

---

## 7.5 SFT lineage 当前真正变了什么

```
SFT changes behavior
→ small curated data can strongly align output
→ but examples differ by whether the model already knows their content
→ new knowledge has different learning / hallucination behavior
→ more SFT can damage knowledge
→ inspect token and parameter update dynamics
```

这条线逐渐把：

> “SFT dataset”

改写成：

> **supervision relative to a model's current state。**

这是后面 distillation lineage 也会再次出现的东西。

---

## 7.6 对我们自己的 warning

用户之前 S03 的失败已经说明：

> training dynamics 很容易变成 training biography。

这条 literature 并没有取消这个风险。

反而强化了：

> 如果问题依赖“第几 checkpoint / 第几阶段学会什么”，
> 必须知道 recipe 是否是 causal variable。

因此：

### 可学习
- model-relative data state；
- local update diagnostic；
- pre/post controlled comparison；
- selective parameter/token update。

### 高风险
- 从 pretraining 到 SFT 到 RL 的宏观“成长史”；
- model family × recipe × budget 的大矩阵；
- 只在一个 recipe 下描述漂亮 trajectory。

---

# LINEAGE 8 — Distillation：从“更强 teacher”到“teacher signal 必须对 student 可学习”

## 8.1 Classical KD — teacher distribution 比 hard label 携带更多 structure [FIELD]

knowledge distillation 的经典 picture：

> teacher soft distribution 含有 class/task structure；
> student 学 teacher，而不只是学 hard label。

进入 autoregressive LM 后，问题更复杂：

- sequence 很长；
- token distribution 极高维；
- teacher/student capacity gap 大；
- student 自己的 generation distribution 会偏离 teacher-forced prefix。

于是：

> “把 teacher 变得更强”

不再保证：

> “student 得到更好监督”。

---

## 8.2 MiniLLM — divergence direction 本身改变 student 看到的学习压力 [FIELD]

**MiniLLM: Knowledge Distillation of Large Language Models (2023)**

标准 KD 常最小化：

> teacher → student 的 forward KL。

在生成式 LM 里，作者强调 forward KL 容易迫使 student：

> 覆盖 teacher distribution 的大量低概率区域。

MiniLLM 转向 reverse-KL-style objective，并结合优化技巧，让 student 更聚焦 teacher 的高概率 modes。

### Primitive change

```
teacher distribution is the target
→ how the student is geometrically penalized relative to that distribution matters
```

也就是说：

> 同一个 teacher 不是唯一 supervision object；
> **divergence 定义了什么叫“学 teacher”。**

---

## 8.3 Capacity gap — teacher performance 不是 supervision quality 的 scalar [FIELD]

**Towards the Law of Capacity Gap in Distilling Language Models (ACL 2025 Main)**

distillation 一个经典但反直觉 phenomenon：

> 更大的 teacher 不一定产生更好的 student。

论文系统研究不同 teacher/student scale，报告：

> 存在 optimal teacher；
> 在其小模型 study 中，optimal teacher scale 与 student scale 呈近线性关系，并尝试外推到 7B 级别。

### Primitive change

```
teacher quality = teacher benchmark accuracy
→ teacher suitability = teacher capability relative to student capacity
```

这是一个很有价值的 shift：

> **supervision quality 是关系属性，不是 teacher 自身的单变量属性。**

---

## 8.4 CoT distillation — “正确 reasoning trace”也可能不是可学习 trace [FIELD]

reasoning model 兴起以后，最自然的 distillation idea 是：

> 让强 teacher 生成 CoT，student imitation。

但随后大量 work 开始遇到同一个压力：

- teacher reasoning 太长；
- strategy 超出 student capability；
- trace 中大量 token 并不是关键；
- teacher-forced trajectory 与 student rollout 分布不同。

于是问题从：

> teacher 有没有高质量 reasoning？

转成：

> **student 能不能从这种 reasoning 学。**

---

## 8.5 Key-step distillation — 全 trace 不是同质 supervision [FIELD]

**Capture the Key in Reasoning... EDIT (ACL 2025 Main)** 一类工作指出：

> student 往往模仿 reasoning 的表面形式，而不是最关键的转折步骤。

论文通过 mistake-driven / key-step identification，把关注点从：

```
whole teacher CoT
```

改成：

```
high-leverage reasoning steps for the student
```

这与 RLVR high-entropy token paper 在 surface 上很像：

> 都在 sparse attribution。

但 genealogy 不同：

- RLVR：rewarded rollout 的 credit assignment；
- distillation：teacher supervision 的 learnability / instructional relevance。

不能因为 method 都“selective weighting”就视为同题。

---

## 8.6 Curriculum distillation — teacher trace 的复杂度也应该 relative to student state [FIELD]

**Teach Small Models to Reason by Curriculum Distillation (EMNLP 2025 Main)**

这类工作观察到一个具体 asymmetry：

- 显式复杂 reasoning trace：信息多，但小 student 未必能直接吸收；
- 简短 answer / implicit supervision：容易学，但可能不够建立 reasoning procedure。

因此构造 staged curriculum：

> 先让 student 建立内部 problem-solving capability，再逐步外化复杂 reasoning。

### Primitive change

```
one fixed teacher target
→ supervision should evolve with student capability
```

这里的核心不是“curriculum 很好”。

而是：

> **teacher target 的最优形态取决于 student training state。**

---

## 8.7 Student-trajectory distillation — teacher-forced data 与 student inference state 不同 [FIELD]

**CoTD-PO / SWITCH 等 2025 work**

另一条 pressure：

> teacher-generated CoT 全部来自 teacher state distribution；
> 但 student 部署时访问的是自己产生的 prefix。

这和 imitation learning 经典 covariate shift 很接近：

```
teacher trajectory distribution
≠ student rollout distribution
```

于是方法开始：

- 采 student trajectories；
- 让 teacher 只在必要时 intervention；
- 对 student mistakes / uncertain state 提供 targeted correction。

### Primitive change

```
distill teacher outputs
→ distill teacher knowledge on states the student actually visits
```

---

## 8.8 Distillation lineage 的真正 movement

```
teacher is better, so imitate teacher
→ divergence defines what imitation means
→ stronger teacher can be worse for smaller student
→ full CoT contains heterogeneous instructional value
→ supervision complexity should match student capacity
→ teacher-forced trajectories mismatch student rollout states
→ teacher quality becomes a student-relative / state-relative quantity
```

这条线对选题 taste 很有价值：

> 很多 training paper 的 opening 不来自“teacher 还不够强”，
> 而来自 **supervision 与 learner 的关系被过度简化。**

---

## 8.9 当前已经很拥挤的 surface

截至 2025–2026：

- generic “teacher CoT 太复杂”；
- generic “select key steps”；
- generic “student-generated trajectory”；
- generic “curriculum distillation”；
- “larger teacher not always better”；

都已经不能当 novelty。

真正下一问必须：

> 把 student-relative learning pressure 定义得更具体。

---

# LINEAGE 9 — Architecture / Inductive Bias：不是“换 backbone”，而是问 architecture 把什么 computation 变得自然

## 9.1 Universal Transformer — recurrence 作为 iterative-computation bias [FIELD]

**Universal Transformers (2018/2019)**

标准 Transformer：

> 每一层参数不同，固定 depth 前馈通过。

Universal Transformer：

> 在 depth 维度重复一个 recurrent transition，并可结合 adaptive computation time。

它的核心 research intuition不是：

> 参数共享省参数。

而是：

> 某些 algorithmic / sequential computation 天然是 iterative；
> recurrence 把这种 iterative refinement 写进 architecture。

### Primitive change

```
depth = stack of distinct functions
→ depth = repeated application of a transition
```

这给 architecture 一个 computation-level inductive bias。

---

## 9.2 Looped Transformers — “重复层”能不能真正执行 algorithm [FIELD]

**Looped Transformers as Programmable Computers (ICML 2023)**、  
**Looped Transformers are Better at Learning Learning Algorithms (2023)**

这类 work 把 recurrent/looping 进一步理论化：

> 一个固定 transformer block 被重复应用，可以实现 iterative algorithms / programmable computation。

这一步的价值是：

> 把 recurrence 从 architecture aesthetic 变成 expressivity/computation object。

### 但要注意

很多结果：

- synthetic；
- algorithmic；
- theoretical construction；

与现代 7B/70B LM 的实际训练不是一回事。

这类 paper 对我们最有价值的是：

> **提供理论 pressure / distinction。**

不是：

> 直接把 toy theorem 当 LLM empirical claim。

---

## 9.3 Recurrent Depth — reasoning 热点改变 recurrence 的意义 [FIELD]

**Scaling up Test-Time Compute with Latent Reasoning: A Recurrent Depth Approach (NeurIPS 2025)**

到了 reasoning/test-time compute 时代，同一个 recurrence primitive 被重新解释：

过去：

> recurrence = parameter sharing / iterative inductive bias。

现在：

> recurrence = **latent test-time compute axis**。

论文训练 3.5B model、约 800B tokens，让 recurrent block 在 inference 时可以迭代更多次：

> 不通过生成更多 reasoning tokens，也能增加 computation depth。

### Primitive change

```
test-time compute = generate more tokens
→ test-time compute = run more latent recurrent depth
```

### 为什么这是真 changed-premise，而不是老 architecture 重做

因为 modern reasoning systems 已经让：

> “inference compute 是可以 scale 的资源”

成为主问题。

这个 deployment/usage regime 给旧 recurrence 一个新的 scientific role。

---

## 9.4 但它是非常重要的 execution counterexample

从 taste 看：

> 很漂亮。

从我们能不能做看：

> 非常危险。

因为 proof-of-concept 本身：

- 3.5B；
- 800B training tokens；
- from-scratch architecture training。

所以必须把两个判断永远分开：

### Intellectual taste
高价值。

### Project suitability
低，除非能找到无需 from-scratch training 的 local question。

这条 discipline 对未来搜题非常重要。

---

## 9.5 A Little Depth Goes a Long Way — 另一条 architecture theory 不需要发明新 module [FIELD]

**A Little Depth Goes a Long Way (NeurIPS 2025)**

另一支并不发明 recurrent model。

它看已有理论：

> fixed-depth Transformer 对一些 sequential problems 有 expressivity limitation。

然后检查：

> fixed-depth 到底有多 load-bearing？

结果表明：

> 让 depth 只增长到 (Theta(log n))，就足以跨过一些 fixed-depth barrier，并且比单纯增加 width 或 CoT 更高效。

### Question-forming move

```
architecture limitation theorem
→ inspect asymptotic assumption
→ identify minimal relaxation needed to change the result
```

这类 work 提醒：

> architecture research 不一定要“提出一个新 architecture”。

一篇很强的 architecture paper 可以只做：

> **重新确定旧结论的边界。**

---

## 9.6 Body Transformer — modality / embodiment 使 vanilla Transformer 的 permutation-friendly bias 不再自然 [FIELD]

**Body Transformer: Leveraging Robot Embodiment for Policy Learning (CoRL 2024 / PMLR 2025)**

Transformer 在 text/vision 很通用。

但机器人 observation/action 并不是任意 token bag：

> body 本身有固定 graph of sensors and actuators。

vanilla full attention 没显式使用这个结构。

BoT 将 embodiment graph 作为 masked-attention inductive bias。

### Primitive change

```
tokens are generic positions
→ tokens correspond to physically structured body parts
```

### 这里最值得学的

不是：

> “给 Transformer 加 graph mask。”

而是：

> **跨域迁移 architecture 时，通用性可能来自丢弃了源域不需要的结构；目标域如果有非常强的物理结构，这个“通用”反而是一种 information loss。**

---

## 9.7 LieRE / positional encoding — inherited geometry 可以在新模态变成 constraint [FIELD]

**LieRE / Lie-group Rotary Position Embedding (ICML 2025 line)**

RoPE 在 language sequence 中非常成功。

但它把 position interaction编码进特定低维旋转结构。

进入：

- images；
- 3D；
- higher-dimensional spatial coordinates；

以后，原有二维/成对旋转结构可能太僵硬。

LieRE 一类 work 使用更一般的 skew-symmetric/Lie-group rotations 学空间变换。

### Genealogy lesson

```
successful positional encoding in source modality
→ reused as default in new modality
→ target geometry exposes representational constraint
→ generalize the transformation family
```

这和 FAST 的 action tokenization 有结构相似：

> inherited interface works long enough to become default，
> 新 modality/statistics 才让 hidden assumption 暴露。

---

## 9.8 Architecture lineage 的共同点不是“inductive bias”

如果机械归纳：

> “加入正确 inductive bias 就好。”

太空。

真正看下来有至少四种完全不同来源：

1. **Computation structure**  
   iterative algorithm → recurrence.

2. **Asymptotic theory**  
   fixed depth assumption → minimal growing depth.

3. **Physical structure**  
   robot body graph → structured attention.

4. **Modality geometry**  
   1D language position encoding → higher-dimensional spatial transformation.

### 所以 architecture idea 必须回答

> **为什么这个 structure 在 task/data/physics 中是客观存在的？**

而不是：

> “我觉得这个 module 更有 inductive bias。”

---

# 10. 四条 lineage 放在一起后的交叉观察

---

## 10.1 “更好的 training signal”越来越是相对概念

Pretraining：

> data mixture 的好坏相对 model scale/capacity。

SFT：

> example 的作用相对模型已经掌握的知识。

Distillation：

> teacher 的好坏相对 student capacity / rollout state。

Architecture：

> inductive bias 的好坏相对数据/模态真正的 structure。

所以一句：

> “X 是 high-quality supervision”

往往是不完整的。

需要问：

> **对谁？在什么 state？在哪个 scale/regime？**

---

## 10.2 平均 metric 会隐藏 allocation problem

- global LM loss 隐藏某类 knowledge acquisition phase transition；
- final SFT accuracy 隐藏 token/parameter update 的异质性；
- teacher accuracy 隐藏 student learnability；
- Transformer benchmark average 隐藏某种 task 所需 computation structure。

这不是要求以后专门找：

> “平均量不够”。

只是说明：

> 一个 metric 一旦进入 field 的标准语言，必须持续检查它压掉了哪些 structured variables。

---

## 10.3 旧解决方案进入新 regime 后，常见的不是“失效”，而是含义改变

Universal Transformer 的 recurrence：

> 原本是 iterative inductive bias；
> reasoning era 变成 test-time latent compute。

SFT：

> 原本是 instruction behavior adaptation；
> 新知识训练使它同时成为 knowledge-modification operator。

Scaling law：

> 原本是 planning empirical law；
> data mixture / repetition 使它变成 structured resource-allocation model。

### Taste lesson

> **changed premise 不只是“以前方法效果下降”。**
>
> 更有意思的情况经常是：
>
> > 同一个 object 在新 regime 下承担了新的 causal / operational role。

---

# 11. 当前 saturation / warning ledger

## Pretraining
高风险：
- 又一个 data-mixture optimizer；
- 再拟合一组 scaling coefficients；
- 大 model zoo 才能建立 claim；
- data curation 本身成为主体。

## SFT
高风险：
- generic catastrophic forgetting；
- “更多 SFT 不一定更好”；
- checkpoint biography；
- recipe-dependent developmental story。

## Distillation
高风险：
- teacher too complex；
- select key steps；
- generic curriculum；
- stronger teacher not always better；
- student trajectory mismatch。

这些在 2025 已经形成密集 cluster。

## Architecture
高风险：
- 新 module + benchmark gain；
- from-scratch pretraining 才能验证；
- toy expressivity theorem 无现实 bridge；
- “加 recurrence / memory / graph / state”但没有客观 structural pressure。

---

# 12. 对下一轮 literature reading 的影响

这轮之后，我们不应该把 training/post-training 简化成：

> loss / data / optimizer 三个地方找 gap。

更好的 reading questions：

### Pretraining
- 当前 scaling abstraction 把哪些 structured variable压成 scalar？
- 哪些平均规律与 capability-specific dynamics冲突？

### SFT
- supervision 对模型当前 state 的作用是什么？
- behavior adaptation 与 knowledge modification 是同一个 process 吗？

### Distillation
- supervision 的“信息量”与“可学习性”如何区分？
- teacher/student relation是否被当成单边 teacher-quality 问题？

### Architecture
- task 的真实 computation/geometry/physics structure是什么？
- 当前通用 architecture 丢掉这个 structure 是 feature 还是 bug？
- 要证明 architecture idea，必须 from-scratch 训练吗？

---

# 13. 当前状态

这批 lineage 加厚了第一份 `LONGITUDINAL_GENEALOGIES_01` 中偏少的 training / architecture部分。

仍然：

> **不形成 topic seed。**

下一份继续：

- multimodal/VLM；
- speech/audio/full-duplex；
- negative/limits；
- optimization dynamics；

并单独建立：

> **contrast / anti-pattern library**

防止把所有 accepted paper 的 story 都事后美化成“漂亮 genealogy”。
