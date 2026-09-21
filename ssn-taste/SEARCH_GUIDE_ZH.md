# ssn-taste 科研选题搜索指南（Canonical）

最后系统整理：2026-09-21

这份文件只回答一个问题：

> **怎样找到真正值得投入时间、符合 Sasano 审美、并有 ACL/EMNLP/NAACL/ICML/ICLR/NeurIPS Main 潜力的研究问题？**

它不是固定流水线，也不是 checklist。下一轮 agent 必须像研究者一样判断；如果发现流程本身正在把搜索带偏，可以主动停止、重新读论文和 Slack、换 lineage、重构问题。

当前 topic 状态以 `README.md`、`SELECTED_TOPICS.md`、各 registration、`FAILED_TOPICS*.md` 和最新 commits 为准。

---

# 0. 最高优先级：先找“值得知道的问题”，再找 novelty 和实验

整个搜索最重要的顺序是：

> **重要/有意思的未知 → 真实 scientific pressure → 新 knowledge → 可直接攻击 → 执行现实**

不要反过来：

> 先发现一个 literature 空格 / 一个 vector / 一个 benchmark cell → 再想办法解释为什么重要。

一个候选最先必须过两问：

### A. 30 秒 reviewer test

不用 mechanism 名词、不用 benchmark 名词，能不能让一个普通 AI/NLP reviewer 在 30 秒内明白：

> **为什么这个问题值得知道？**

Sasano 的真实反馈反复强调：top conference 的 Introduction 要让平均 reviewer **納得できる + 面白い**。Reviewer 不会替作者挖掘“哪里有意思”。

### B. Consequence test

假设两个主要 possible worlds 分别成立：

> **我们对模型的 learning / reasoning / generation / representation / architecture 的什么重要理解会改变？**

如果答案只是：

- “说明内部 architecture 不一样”
- “说明 A 和 B 是两个不同 representation”
- “说明这个 vector 有因果作用”
- “说明 effect 在这个 setting 存在”

通常不够。

S08 的失败是重要教训：shared-vs-separate control 可以 technically clean，但如果 strongest finding 仍只是局部架构差异，scientific consequence 太弱。

---

# 1. 好题的五个核心锚点

不要把下面五条当打分表；它们是优先级很高的研究判断。

## 1. Important question

问题在知道答案前就值得问，而且答案不是只对一个 niche setup 有意义。

优秀顶会工作经常具备以下一种压力：

- 挑战一个社区广泛接受但未真正验证的 premise；
- 两个现象/结果无法被同一个简单解释同时解释；
- 一个能力看似成功，但可能由完全不同的 computation 实现；
- 一个“优势/灵活性/改进”可能反而允许模型绕过真正重要的 computation；
- 社区把两个量当成同一个，但它们若分离会改变重要结论；
- 训练与部署、指标与真实对象、endpoint 与 formation 之间存在结构性错位；
- 一个经典问题以前无法 intervention，现在出现了新的 attack。

**注意：** “A ≠ B”“shared vs separate”“encoded vs used”只是可能的结构，不是 idea generator。本身没有 importance。

## 2. Real scientific pressure

题目必须从真实世界中的矛盾、失败、假设或 unexplained pattern 长出来。

优先来源：

- 多篇强论文之间无法统一解释的结果；
- 作者真正依赖但没有验证的 load-bearing assumption；
- strong negative / counter-intuitive evidence；
- changed premise：旧解释成立所依赖的条件已经改变；
- 一个成熟问题突然获得新的可干预性。

弱来源：

- 最近 paper 的 future work；
- “这个 exact cell 好像没人测”；
- “换新模型再测一次”；
- “behavior 已知，所以再做 mechanism”。

Remove-trigger-paper test：

> 删除启发你的那篇 paper，这个问题还能否从其他独立 pressure 自然出现？

不能的话，通常太像 follow-up。

## 3. Real knowledge delta

允许与 prior 大量 overlap。Main novelty 不是“没人说过这些词”。

必须能写：

> **Prior 已经知道 X；但 Y 仍然未知，因为 Z；我们第一次能区分 A/B/C。**

真正 kill 的是：

- nearest prior 已经回答 same decisive unknown；
- difference 只是 model / language / dataset / modality / condition；
- cleaner replication；
- paper A × paper B 的机械交集；
- 为躲 prior 把问题切到一个没人关心的小格子。

Sasano 的 Guo 案例是硬提醒：

> 如果和先行研究差太小，应及时見切り，换题，而不是继续包装。

## 4. A direct attack already exists

Hamming 式原则：

> 重要问题不仅要重要，还必须现在有一个 reasonable attack。

在注册前，应已经能描述一个小而直接的 decisive experiment。

好的 pilot：

- 直接操纵 scientific variable；
- 主要 possible worlds 给出不同 prediction；
- 第一轮就在回答 science。

危险 pilot：

- 先看看现象存不存在；
- 先看看能不能找到一个 probe/vector；
- 先验证自己发明的 measurement；
- 需要大量 engineering 才知道 question 是否 measurable。

S08 的另一个失败教训：

> 如果第一轮主要是在赌“latent construct / causal handle 能不能抽出来”，而不是区分 scientific worlds，这个题风险很高。

## 5. Execution must remain subordinate to the question

数据、recipe、模型、tool 都应该是 instrument，不应吞掉 mother question。

优先：

- 现成公开数据 + 原生 ground truth；
- 几十到几百个程序化 controlled stimuli，答案解析可得；
- inference-only / same-run causal contrast；
- 一两个便宜 robustness checks。

危险：

- 大规模人工 annotation；
- LLM judge 是主要 ground truth；
- synthetic generator 越做越复杂；
- model zoo；
- optimizer × LR × dose × family 大矩阵；
- 为救一个题不断增加 arms / controls。

如果 harness 的复杂度增长速度快于 scientific insight，优先 KILL。

---

# 2. Sasano taste：真正需要牢牢记住的四件事

不要把 Sasano taste 简化成“喜欢 interpretability”。

### ① 普通 reviewer 必须一眼看到为什么有意思

研究不是让 reviewer 努力挖亮点。

问题、动机、实验、finding 应能顺着读下来；RQ 与核心 findings 应直接对应。

### ② “意外”有价值，但不是必须方向正确

与预期相反的结果完全可以很好。

关键是：

> unexpected result 是否改变一个真实解释 / assumption？

不是“只要结果不一样就有价值”。

### ③ 内部差异不自动等于 main contribution

Sasano 明确评价过：

> 输出相似、内部理解不同很有意思，能深化对模型行为的理解；但未必能成为论文主要结果。

所以 mechanism 必须服务于更大的 scientific question，不能靠“内部不一样”自动升级 significance。

### ④ 对小 novelty 要敢于放弃

如果 honest reviewer compression 后只是已有工作的一个小 extension，就换题。

不要因为已经投入很多搜索时间就继续救。

---

# 3. 从强论文学习“问题怎样长出来”，不要复制题型

每轮必须持续重新校准，不要只读与当前 seed 最邻近的 literature。

近年强工作反复体现的不是某种固定模板，而是：

- **The Flexibility Trap (ICML 2026 Outstanding):** 挑战“arbitrary-order flexibility 是优势”这个主流 premise；优势本身允许模型绕过高不确定度、真正决定解法的 token。
- **LLMs Get Lost in Multi-Turn Conversation (ICLR 2026 Outstanding):** 从 training/deployment 的结构错位出发，而不是从一个 benchmark gap 出发。
- **Transformers are Inherently Succinct (ICLR 2026 Outstanding):** committee 直接强调 strong conceptual message；好的题可以是给一个熟悉对象提供新的解释视角。
- **How much can language models memorize? (ICML 2026 HM):** 价值来自重新分解一个重要概念，而不只是多测 memorization。
- **强 negative-result work:** 推翻“某训练方法真的创造了新能力”等基础假设时，null/negative 本身可以很重要。
- **强 dynamics work:** 当 endpoint quality 与 memorization / transfer / controllability 等真正不同的时间尺度或 quantity 分离时，区别之所以重要，是因为它改变了我们对训练过程的理解，而不是因为“A ≠ B”形式漂亮。

奖项论文只是 taste 上限，不是模板，也不是最低标准。要同时阅读普通但明显强的 Main papers，校准现实的 novelty 和实验规模。

---

# 4. 下一轮真正的 idea search 方法

不要 brainstorm 30 个题名。

先维护一个小型 **Important Pressure Portfolio**：

> 大约 5–10 个你认为“如果能回答会真的改变理解”的 unresolved pressures。

每个 pressure 只写三句话：

- 社区现在相信/观察到了什么？
- 哪一点不协调、未解释或 premise 可疑？
- 为什么现在可能有新的 attack？

来源要分散：

- ACL / EMNLP / NAACL / TACL；
- ICLR / ICML / NeurIPS；
- CV / multimodal / generation / speech / robotics；
- cognition / neuroscience / statistics / information theory / control 等。

跨领域只迁移：

> question structure、scientific pressure、identification logic。

不要搬术语。

当某个 pressure 同时出现：

> **重要 + 未解 + 有新 attack**

再锁一个 seed，深审到底。

---

# 5. 深审时才启用这些风险 Gate

搜索早期不要让下面的 gates 压死 creativity；候选锁定后必须严格执行。

## Significance Gate

问：

> 最强 possible finding 写成一句普通话，真的重要吗？

如果 reviewer 会回答“所以呢？”，KILL。

## Novelty Gate

读最危险 prior 的 abstract / intro / related work / actual experiment。

不是关键词查重，而是 same decisive unknown audit。

## Identification Gate

主要 worlds 必须能被一个相对直接的 intervention 区分。

不要追求 theorem-like 完美控制；只处理会改变核心 interpretation 的 confound。

## Construct Gate

核心变量最好直接 observable / manipulable。

如果必须先发明一个 probe/vector/latent score 才能开始问问题，风险高。

## Data Path Gate

优先顺序：

> existing data → small programmatic stimuli → small auto-generated + spot check >>> manual annotation / judge / benchmark construction。

Synthetic 只能是 instrument，不能成为现象本身。

## Training Recipe Gate

对 learning/post-training 题，先问：

> causal variable 是不是训练 recipe/path 本身的复合产物？

S03 和 S09 是反例。

优先 same-run / same-state matched interventions。

如果 qualitative world 需要 optimizer × LR × dose × family sweep 才知道，KILL。

## Scale Gate

小模型/toy world 可以做 pilot，但最终 claim 若指向真实 LLM dynamics，必须有理由相信 pilot 对真实 regime 有意义。

不需要一开始 model zoo，只做最少量 scale validation。

---

# 6. “所有结果都有意义”必须收紧

这是上一轮一个容易自我欺骗的规则。

不能因为能给 A/B/C 各写一句 interpretation，就说不是 anomaly gambling。

真正要求：

> **每个主要 outcome 都必须改变一个当前 live belief、排除一个真实 explanation、或修正一个重要 assumption。**

“没有 effect”只有在社区有真实理由预期 effect、或 null 本身排除重要理论时才有意义。

否则：

> “结果怎样都能解释”

只是故事弹性，不是科学价值。

---

# 7. Mechanistic interpretability 的正确位置

Mechanism 是 explanation depth，不是 novelty tax。

正确顺序：

> important puzzle / law
> → representation
> → transformation / computation
> → pathway/component
> → causal intervention

如果 behavioral / learning law 已经足够重要，不必硬加 circuit。

尤其禁止：

> probe/SAE/head/vector 先行 → 再反向发明 mother question。

“同一行为是否由不同内部机制实现”只有在不同 mechanism 会改变更大的理论理解、transfer、failure 或 controllability 时才值得做。

---

# 8. 强制自我纠偏：不要完全服从这份指南

下一轮 agent **必须有权打断固定流程**。

出现以下任一迹象时，立即暂停当前 generator：

- 连续 2–3 个 seed 因同一种理由死；
- 候选越来越像 A≠B / shared-vs-separate 的形式套题；
- mechanism 越来越复杂，但“所以呢”越来越难回答；
- synthetic/data/controls 越来越多；
- novelty 越来越靠 exact cell；
- 只在 reasoning / RL / agents 一个热点里循环；
- strong papers 主要被用来 kill，而不是产生 scientific pressure；
- 为保住候选不断加实验。

### Calibration interrupt

暂停后重新做：

1. 读 2–4 篇**新鲜、不同 lineage**的强 Main / Outstanding 工作；
2. 读至少 1 个 Sasano 最近真实 feedback thread；
3. 不问“能抄什么题”，只写：
   - 它为什么值得问？
   - author 在解决哪个 live tension？
   - 如果结果反过来，什么理解会改变？
   - decisive attack 为什么足够简单？
4. 写一句 drift diagnosis：
   > “我们刚才为什么开始走偏？”
5. 再决定继续当前 pressure 还是换 generator。

不要机械规定每 N 个小时 reset；看到 drift 就 reset。

---

# 9. Binary decision：保留，但不要过早注册

一个 seed 锁住以后必须审到：

> **PILOT-AUTHORIZED 或 KILL**

不要把 SERIOUS/maybe 留给用户。

但也不要因为“形式上满足 A/B/C”就过早注册。

PILOT-AUTHORIZED 最终意味着：

> **这个问题本身重要；same decisive unknown 未被做掉；现在已有一个现实、直接、低成本的 attack；第一刀主要回答 science 而不是验证 instrument；数据/recipe/construct 不会自然爆炸。**

KILL 后写入 failed ledger，并记录真正 failure mode，禁止换标题复活。

允许一整轮 **0 survivor**。

---

# 10. 当前正式状态

截至 2026-09-21：

## SELECTED / PILOT-AUTHORIZED

- S04 — How Do Language Models Update Situation Models Across Event Boundaries?
- S05 — When Does Reading Become Learning?
- S06 — What Does Deliberation Do to Evidence?
- S07 — Where Does Surprise Go?

## 最近重要 KILL

- S03 — training-stage developmental story 随 budget / family / recipe 改变；属于 training biography 风险。
- S08 — shared-vs-separate control 即使干净识别，scientific consequence 仍不足；mechanistic-detail trap。
- S09 — memory age/history 本身是 optimization-path construct；需要 recipe matrix 才能解释。

这些 Sxx **都不是正向 taste exemplar**。Selected 只表示当前值得第一刀实验；Killed 只作为反面/process evidence。

---

# 11. 下一轮 agent 的最高行动原则

> **不要找“一个没被做过的实验”。找“一个值得知道、现在终于能被直接攻击的问题”。**

如果只能记住四句话：

> **先问 why care，再问 novelty。**  
> **先找 scientific pressure，不找 literature blank。**  
> **pilot 要直接回答 science，不要先赌 instrument / dataset / recipe。**  
> **持续读强论文和 Sasano feedback 校准；发现自己在套模板时立刻 reset。**
