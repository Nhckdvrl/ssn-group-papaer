# Lessons from ssn-taste：旧搜题流程复盘与 chasing-trends 迁移规则

> **2026-09-19 correction.**
>
> 本文件关于旧 `ssn-taste` 的失败复盘仍然有效，但它后半部分把新路线过度收缩成“机制驱动方法论文”。这一点已经被后续纠偏。
>
> 当前 canonical taste 以：
>
> - `RESEARCH_TASTE_RECALIBRATION_2026-09-19.md`
> - `PAPER_GENEALOGY_GUIDE.md`
> - `SEARCH_GUIDE_ZH.md`
>
> 为准。
>
> 现在的目标不是优先某一种 paper shape，而是通过真实论文 genealogy 学习多种 research moves。

日期：2026-09-19

这份文件不是新的 topic ledger，也不是要否定 `ssn-taste/`。

它只回答一个问题：

> **上一轮为什么越来越难找、越来越难做；哪些纪律必须保留，哪些纪律在“机制驱动方法论文”这条新路线里应该改写？**

---

# 1. 先恢复事实：handoff 已经过时

最新 repo 的正式状态优先于聊天 handoff。

当前真正仍为 **SELECTED — PILOT-AUTHORIZED** 的只有：

- S04 — How Do Language Models Update Situation Models Across Event Boundaries?
- S05 — When Does Reading Become Learning?
- S06 — What Does Deliberation Do to Evidence?
- S07 — Where Does Surprise Go?
- S08 — Is Metacognitive Control Shared?

已经正式取消：

- S03 — From Document End to Task Done
- S09 — Same Recall, Different Stability?

这件事本身就是第一条流程教训：

> **永远恢复 repo，不要相信“上一轮总结里看起来很正式”的状态。**

---

# 2. ssn-taste 做对了什么

上一轮最值得保留的不是具体 Sxx，而是以下研究纪律。

## 2.1 Reviewer compression

一个 idea 不能靠漂亮术语保护。

必须不断问：

> reviewer 最狠地把这篇工作压成一句话，会是什么？

这条对方法论文更重要。

例如：

> “你不就是给 GRPO 加了一个 weight 吗？”

如果我们无法回答：

> “这个 weight 是由我们先验证的 failure mechanism 唯一/自然导出的，而且它在 mechanism-strength 变化时产生预期变化。”

那么方法仍然薄。

---

## 2.2 Nearest-prior deep audit

不能只搜标题。

真正危险的 prior 要读：

- introduction；
- main claim；
- method；
- decisive experiment；
- ablation；
- limitations / discussion。

在 chasing-trends 里，novelty 不再只问：

> “有没有人问过同一个 mother question？”

还必须问：

> “有没有人已经完成同一个 **failure → diagnosis → design principle → intervention** 链？”

如果别人已经诊断出同一个病因，并且用了本质相同的修法，只换 loss 名字或 benchmark，直接 kill。

---

## 2.3 Data / compute gate

上一轮越来越清楚：

> 一个 paper idea 的质量不能和“执行成本”分开评价。

如果第一轮判断生死就需要：

- 十几个模型；
- 多个 optimizer；
- 大规模 RL；
- 很多人工标注；
- 新 simulator；
- 大量 judge API；
- full pretraining；

这个题对当前项目不合适。

新路线仍然坚持：

> **先用最便宜的 diagnosis 判断核心故事是否存在，再花钱训练方法。**

---

## 2.4 Anti-resurrection

F01–F109 的价值主要是防止：

> 换个名字，又重新做一次同一个 parent。

这条规则保留。

尤其禁止：

- “旧题 + reasoning model”；
- “旧题 + GRPO”；
- “旧题 + agent”；
- “旧题 + multimodal”；
- “旧题 + 新术语”。

---

## 2.5 Identification before rhetoric

上一轮不断提醒：

> 一个漂亮 explanation，如果没有一个实验让它和其它 explanation 给出不同 prediction，就不是真正的 diagnosis。

新路线仍然要求这一点。

区别只是：

> 我们不一定要把所有 possible worlds 研究成一篇纯科学论文。

只需要把**决定 method design 的那条 distinction**识别清楚。

---

# 3. ssn-taste 为什么变得越来越痛苦

不是因为标准“太高”这么简单，而是目标函数逐渐偏向了一个非常窄的论文类型：

> **纯 scientific mother question + 多 possible worlds + 直接 identification + null/opposite 也独立 Main-sized + mechanism 只作为后续。**

这类论文当然很好。

但它对选题和执行的要求都非常苛刻。

---

## 3.1 “behavior 已知 → mechanism”被过度当成危险模式

FAILED ledger 中大量候选死于：

> parent 已经有人做；
> 我们只是 mechanism follow-up。

对纯 scientific-question search，这个警惕是合理的。

但对于 method paper，这个规则不能照搬。

如果：

1. behavior/failure 已知；
2. **真正导致 failure 的 operative mechanism 仍不清楚**；
3. 不同 mechanism 对修法给出不同 prediction；
4. 我们的 diagnosis 直接产生一个有效新方法；

那么 mechanism follow-up 完全可以是非常好的论文。

关键不是：

> “现象是不是第一次被发现？”

而是：

> **“我们是不是第一次把这个失败变成了一个可操作的设计原则？”**

---

## 3.2 “方法不能成为贡献主体”执行得过头

旧 guide 的 sanity check 很强：

> 去掉 model / benchmark / method 名以后，还剩什么科学事实？

但 chasing-trends 不应该要求 method 被删掉以后论文仍完整成立。

这里更合适的 sanity check 是：

> **去掉方法名以后，能否说清楚它修复了什么具体 failure；去掉 diagnosis 以后，方法是否失去设计依据？**

理想关系是：

> diagnosis 与 method 互相支撑。

不是纯 science + 后贴一个 trick，
也不是 trick + 后贴一个解释。

---

## 3.3 “opposite/null outcome 也必须是一篇论文”不适合方法路线

纯科学问题最好做到：

> A/B/C 哪个世界都产生知识。

方法论文不必强求。

方法论文天然允许更强的 asymmetric risk：

> diagnosis 如果不成立，或者修法不涨点，这个 project 可以死。

真正重要的是控制试错成本：

> **不要在昂贵训练之后才发现核心 diagnosis 不成立。**

因此新的原则是：

> 允许 positive-result dependence；
> 但必须用 cheap diagnosis / proxy pilot 把风险前置。

---

## 3.4 对 benchmark 的排斥也过度了

旧路线非常怕：

> 最后变成 score table。

这是正确警告。

但 benchmark 本身不是问题。

对于 method paper：

> **标准 benchmark 是证明方法具有实际价值的必要闭环。**

新的区分是：

- benchmark 作为 **contribution** → 不喜欢；
- benchmark 作为 **validation** → 必须认真做。

我们不要造新 leaderboard。

但提出方法以后，应该在社区接受的 benchmark、强 baseline、合理 compute budget 下证明它有效。

---

# 4. S03 真正教会我们的东西

S03 最终不是因为“结果不好”而死。

真正的问题是：

> 它试图解释从 pretraining 到 post-training 的 stopping capability 如何形成，但“post-training stage”不是一个干净的 causal variable。

它实际捆绑：

- data mixture；
- serialization；
- optimizer；
- training budget；
- synthetic-data generation；
- SFT / preference optimization；
- model-family-specific interfaces。

actual pilot 中，合理的 budget / model family 改变就会让 developmental story 改写。

继续下去只能：

> 再加 recipe；
> 再加 checkpoint；
> 再加 family；
> 再解释一次。

最后变成：

> **一条 training biography，而不是一个稳定机制。**

### 对 chasing-trends 的迁移规则

training / post-training 不是不能做。

但尽量选：

- **同一 run 内可定义的 failure quantity**；
- 可在 token/sample/trajectory/step level 测量；
- intervention 可以局部打开/关闭；
- method 只改变一个清楚的 learning signal；
- 一个 standard recipe 就能完成核心 causal comparison。

例如：

> “哪些 token 的 policy gradient 真正决定 reasoning branch？”

比：

> “模型的 reasoning ability 在整个后训练生命周期如何形成？”

更适合方法路线。

---

# 5. S09 真正教会我们的东西

S09 的母问题很有吸引力：

> 相同当前 recall 的 memory，是否因为 learning history 不同而具有不同 stability？

问题在于：

> “memory age/history”本身就是 optimization path 的产物。

它无法自然和以下因素分离：

- acquisition time；
- intervening gradients；
- spacing；
- recency；
- dose；
- parameter state；
- optimizer。

即使 mirrored schedule / common refresh 能改善 within-recipe control，也不能让“age”变成 recipe-invariant quantity。

### 对 chasing-trends 的迁移规则

不要把：

> **训练历史的摘要标签**

当成方法设计的核心 observable。

优先使用：

- current uncertainty；
- current entropy；
- current reward variance；
- gradient magnitude；
- step saliency；
- policy/reference divergence；
- rollout success distribution；
- verifier disagreement；
- token-level advantage；
- trajectory branching / collapse；
- compute utilization；
- train–test distribution mismatch；

这类可以**在当前状态直接测量**的量。

它们更容易变成 adaptive algorithm。

---

# 6. FAILED_TOPICS F01–F109 的共同死法

大量旧候选并不是一个个独立失败，而是集中在几个模式。

## A. Parent 已被回答

典型：

- uncertainty retained but unreadable；
- message/role serialization；
- prompt-side learning；
- fine-tuning feature reuse；
- circuit composability；
- information-seeking agents。

教训：

> 热点不意味着可以无视 prior。

新路线依然必须做 same-unknown / same-fix audit。

---

## B. Mechanism 很漂亮，但没有方法压力

典型：

- represented → used；
- output-null planning；
- transformation similarity；
- gauge-invariant explanation；
- circuit bootstrap。

它们容易变成：

> probe / direction / circuit / patching 本身就是结果。

对新路线来说，除非这个机制自然推出一个可以改善系统的方法，否则优先级下降。

---

## C. Cross-domain 只迁移了名词

典型：

- blocking；
- source memory；
- multisensory common-cause；
- state vs operator；
- dual control。

教训：

> 继续允许跨领域迁移，但迁移的是**可操作的因果结构**。

例如：

> diffusion 的 train–test timestep coupling 被破坏
>
> → 启发我们去找 LLM 中“训练时被强绑定、推理时被打散”的量；

这比把 “SNR bias” 直接改名成 “reasoning SNR bias” 强得多。

---

## D. Exact-cell novelty

典型：

- 某个 EOS reset；
- 某个 API default；
- 某个 particular feature/pathway。

教训：

> method paper 可以比纯 science 更窄，但必须有 general design principle。

不是：

> “这个 case 能修。”

而是：

> “我们识别出一种 failure class，方法针对这个 class 生效。”

---

## E. Experiment explosion

过去为了排一个 confound，不断增加：

- arms；
- checkpoints；
- optimizers；
- model families；
- synthetic controls。

教训：

> chasing-trends 必须有 **method complexity budget** 和 **evidence budget**。

如果一个诊断要 20 个 control 才说得清，通常不适合这个路线。

---

# 7. 哪些旧规则原样保留

以下规则不因为“追热点”而降低：

1. **不做 old problem + new model。**
2. **不把模型名 / benchmark 名当 novelty。**
3. **不做 data/benchmark paper。**
4. **不靠大量 model-zoo 堆 story。**
5. **nearest prior 必须读深。**
6. **reviewer compression 必须过。**
7. **数据和算力必须真实可行。**
8. **如果需要 experiment explosion 才能 defend，就 kill。**
9. **结果必须能解释，不接受纯“多一个 module 涨点”。**
10. **selected / failed 的自有题都不是正向 taste exemplar。**

---

# 8. 哪些旧规则正式改写

## 旧：机制必须跟随独立 mother question

改为：

> **机制可以从重要已知 failure 出发，只要它改变 method design。**

---

## 旧：benchmark/evaluation 不是 science，因此尽量避免

改为：

> **benchmark 不做 contribution，但作为方法有效性的标准证据必须认真做。**

---

## 旧：null/opposite outcome 也应具有 Main-sized knowledge gain

改为：

> **允许 method project 有 positive-result risk，但 cheap diagnosis 必须先行。**

---

## 旧：method 名删掉后，问题仍须完全成立

改为：

> **方法必须有独立 failure pressure；而 diagnosis 必须能约束方法。**

---

## 旧：recent phenomenon → mechanism 默认高风险

改为：

> **recent phenomenon → generic mechanism 仍然高风险；**
>
> **recent failure → discriminative diagnosis → design principle → effective method 可以是高价值路径。**

---

## 旧：机制论文最好 representation → computation → pathway → causal intervention

改为：

> chasing-trends 更常见的是：
>
> **failure localization → causal/operational quantity → design principle → intervention → gain/ablation closure。**

不需要先定位 neuron/head/circuit。

---

# 9. 新旧两条路线的关系

`ssn-taste/`：

> 问一个本身就值得知道的科学问题。

`chasing trends/`：

> 在一个当前重要的方法范式里，找到一个真正的坏机制，把它变成一个有效的新设计。

没有谁更“高级”。

它们只是不同 paper archetype。

当前阶段明确优先：

> **chasing trends。**

原因不是降低标准，而是更符合：

- 用户真正感兴趣的论文；
- 更清楚的 paper structure；
- 更可控的执行路径；
- 更快的 pilot feedback；
- 更容易把分析、方法、benchmark、ablation 组织成完整 Main story。

---

# 10. 最终融合原则

新的核心不再是：

> “一定要找到一个没人回答过的纯 scientific mother question。”

也不是：

> “追最新热点，拼一个新 module。”

而是：

> **找一个热门且重要的范式里，大家真实遇到但还没有被正确修复的 failure。**
>
> **先把 failure 拆到足以约束修法。**
>
> **再做最小、最直接的方法改进。**
>
> **最后用标准 benchmark 和 mechanism-aware ablation 把因果链闭合。**

一句话：

> **Mechanism is useful when it earns the method.  
> Benchmark gains are useful when they validate the mechanism-guided method.**

这就是 `chasing trends/` 要保留的研究 taste。
