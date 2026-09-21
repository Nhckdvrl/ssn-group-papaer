# ssn-taste 科研选题搜索指南（Canonical）

最后系统重构：2026-09-21

这份文件是 `ssn-taste/` **唯一长期方法论来源**。

本子仓库只有一个核心目的：

> **找到一个 Sasano 会认为清楚、重要、值得知道，且具有 ACL / EMNLP / NAACL Main 潜力、现在又能被直接攻击的科学问题。**

不是为了制造 Sxx，不是为了把某个 seed 救活，也不是为了证明“我们能找到 novelty”。

优先级：

> **Sasano 的真实研究判断 > ACL / EMNLP / NAACL / TACL 强论文的问题形成方式 > 其他顶会/跨领域启发 > 同门题材分布。**

同门研究只说明实验室允许做什么，是弱证据；**不能当正向 taste exemplar**。  
历史 selected / failed / Sxx / Fxx 也只用于状态恢复、去重和失败学习，不能定义下一题应该长什么样。

---

# 0. 开局只恢复最小状态

每轮开始只读：

1. `README.md`
2. `SELECTED_TOPICS.md`
3. 当前 selected registrations（只为避免重复）
4. 本文件
5. 最近 commits

然后做新鲜校准：

- 2–4 条 Sasano 最近、与“有趣 / 意外 / novelty / 是否值得继续”直接相关的 Slack feedback；
- 4–8 篇近期强 ACL / EMNLP / NAACL / TACL Main papers，至少跨 2–3 个不同 lineage；
- 必要时补 ICLR / ICML / NeurIPS / CV / multimodal / cognition / statistics 等作为外部压力。

**不要开局顺序读完全部 `FAILED_TOPICS*.md`。**

过去这么做会让 agent 被 F01–F109 的术语与负例锚死，只能在历史题目的 negative space 里继续变体。

Failed ledgers 改成：

> **锁定 seed 后，按关键词 / parent / mechanism 定向搜索，做 anti-resurrection。**

---

# 1. 过去为什么长期找不到足够好的题

问题不是“门槛太高”，而是 generator 经常从错误的地方开始。

## 1.1 从漂亮结构开始，而不是从 scientific pressure 开始

过去大量 seed 来自：

- A ≠ B；
- shared vs separate；
- encoded vs used；
- state vs operator；
- invariance / commutativity；
- prototype vs exemplar；
- 某个 architecture paradox；
- 某个经典 cognitive effect；
- 某个看起来必要的 latent computation。

这些结构可以成为实验形式，但**不是 idea provenance**。

结果通常是：先设计了一个很漂亮的实验，nearest-prior 一查才发现 mother question 早被占了，只剩一个 exact cell。

### 修正

先找：

> **社区现在有什么重要理解是不稳的？哪条 load-bearing assumption 没被验证？哪两个已知事实不能被一个简单解释统一？**

只有 pressure 成立后，才允许使用 A/B contrast。

---

## 1.2 “赌一个新现象”是最危险的模式

错误模式：

> 也许 LLM 会出现一个神奇现象 → 先跑看看 → 有了再解释 why。

如果现象不存在，整题归零；如果存在，漂亮现象往往已经被原作者或紧邻工作继续做到 why / boundary / mechanism。

### Anti-Anomaly-Gambling Rule

优先只接受以下母问题：

1. 已有长期未决理论分歧，新模型第一次允许更干净 intervention；
2. 社区广泛依赖的 premise / proxy / metric 尚未真正验证；
3. 两个独立、已成立的结果彼此冲突，需要区分解释；
4. changed regime 使旧结论的前提失效；
5. 一个结构性 identification problem 本身就存在，不依赖先观察新 anomaly。

如果第一步只是“看看这个现象有没有”，默认不进入 pilot。

---

## 1.3 “别人发现现象，我们补 why”通常已经太晚

最近反复撞死的共同叫法、curse of knowledge、entity tracking、interference、belief revision、probability coherence、evidence dependence 等都说明：

> **一个现象一旦漂亮到值得追，作者往往已经顺手做 decisive contrast。**

只有在以下条件同时成立时才允许追 why：

- why 本身早于该现象就是一个重要科学问题；
- nearest prior 没有回答 same decisive unknown；
- 我们回答的是独立 mother question，而不是“再加机制”。

否则直接 KILL。

---

## 1.4 “经典心理学 / 语言学问题 + LLM”不是 novelty

把 prototype/exemplar、cue competition、common ground、reference frame、antonymy、coercion 等搬到 LLM，通常只是：

> **old question + new model**

经典问题只有在现代模型带来**新的 identification opportunity**时才值得做。

正确形式：

> 过去 A/B 两种解释在人类数据中纠缠；现在可在同一个 artificial agent 内只改变一个变量，第一次真正区分 A/B。

错误形式：

> “人类有 X，LLM 有没有 X？”

---

## 1.5 强论文曾经被主要用来查重，而不是生成科学问题

这会把搜索变成法律检索。

以后每篇强论文只做 5 行 autopsy：

1. **Pressure**：为什么问题在实验前就值得问？
2. **Load-bearing assumption**：社区默认了什么？
3. **Knowledge at stake**：哪个理解可能被改写？
4. **Decisive attack**：作者用什么最小 contrast？
5. **Growth lesson**：普通 observation 是怎样长成 Main-level question 的？

只迁移问题形成方式，不复制题材。

---

## 1.6 追热门线会天然降低 novelty

2025–2026 的 reasoning / agent / RL / uncertainty / evidence integration / latent planning 更新极快。

热门题不是禁区，但默认降权。优先寻找：

- undercrowded 的基础问题；
- generation / learning / representation 的基本规律；
- discourse / cognition / multilingual / multimodal 中**无需大量专业背景即可理解**的问题；
- 旧问题的新 identification，而不是热点新术语。

尤其避免为了追热点而进入 RL / agent / latent reasoning / MoE 等拥挤 lineage。

---

## 1.7 大 mother question 与实际实验经常不匹配

S05 是典型：母问题漂亮，但能执行的实验只回答很窄的 causal cell。

注册前必须问：

> **这个最小实验真的在回答标题里的 mother question 吗？**

如果实验只能支持标题的 10%，不要靠 rhetoric 放大。

---

# 2. Sasano taste：只保留真实、稳定的判断

不要把 Sasano taste 简化成“喜欢语言学”或“喜欢 interpretability”。

## 2.1 Reviewer 第一遍必须看懂为什么有意思

Sasano 明确强调：top conference 的平均 reviewer 不会替作者找亮点。

因此：

> **一句话讲不清的问题，默认危险。**

如果理解问题必须先学五个语言学术语、一个复杂 formalism、或一套内部机制，优先不做。

这也符合当前搜索偏好：**即使某种复杂语言学题很 Sasano，也应谨慎，除非它能被压缩成普通 reviewer 一听就懂的科学问题。**

---

## 2.2 “意外”值钱，但不是“奇怪”值钱

真正值钱的是：

> **结果迫使我们修改一个 live belief / explanation / assumption。**

“找到一个 representation”“两个内部状态不同”“某 head 有因果作用”通常不够惊讶。

---

## 2.3 技术上新，不等于 scientific contribution 强

机制可以深化一个已经重要的问题，但不能拯救一个本身无聊的 mother question。

正确顺序：

> important question → behavior / law → representation / computation → component → causal intervention

错误顺序：

> probe / SAE / head / vector → 再反向发明 mother question。

---

## 2.4 Novelty 太小时要敢于立即见切り

如果 honest reviewer compression 只是：

- 新模型；
- 新语言；
- 新 modality；
- cleaner replication；
- 已知现象的 why；
- 已知机制的一格变体；

就停止，不要因为已经投入时间继续救。

---

# 3. ACL / EMNLP / NAACL 是主要 idea source，但学的是“出题动作”

重点寻找以下问题形成方式，而不是固定题型。

## 3.1 挑战默认 premise

社区默认：

> X 更灵活 / 更多 / 更强 → 应该更好

强论文可能问：

> 这个“优势”是否允许模型绕过真正关键 computation？

---

## 3.2 拆开被默认等价的量

不是为了机械做 A ≠ B，而是因为社区正在用 A 代表 B，并据此得出重要结论。

只有当分离会改变一个现有解释时才值得做。

---

## 3.3 找 training / evaluation / deployment 的结构错位

例如：

- 单轮训练 vs 多轮使用；
- endpoint performance vs formation process；
- proxy metric vs 真正对象；
- controlled benchmark success vs realistic decision process。

重点是**结构性错位**，不是再造一个 benchmark。

---

## 3.4 找 changed premise

旧结论依赖某个条件；现代模型/训练范式已经改变该条件。

真正的问题是：

> 旧解释还能成立吗？

---

## 3.5 找 old debate + new intervention

这是目前最值得优先寻找的类型之一。

不是“经典问题搬到 LLM”，而是：

> LLM 让过去无法区分的两种解释，现在第一次可以在同一 agent 内做 causal contrast。

---

# 4. 题材范围：宽，但不跟热点跑，也不钻晦涩语言学

本仓库不是“语言学选题库”，也不是“interpretability 选题库”。

优先搜索：

- LLM learning / post-training 的基础规律；
- inference / generation 的基本过程；
- representation / inductive bias；
- memory / updating / state / adaptation；
- multimodal / speech / generation 中容易解释的基础问题；
- cognition / discourse / multilingual 中普通 reviewer 能直接理解的问题；
- AI-mediated language / behavior 中具有清晰科学压力的问题。

可以看语言学，但**复杂语言学只能作为 scientific object 的来源，不应成为理解门槛**。

同门题材只做弱参考。  
Sasano 的明确判断和强 Main 论文的问题结构才是主要校准源。

---

# 5. 新的 generator：先建 Pressure Portfolio，不先 brainstorm 标题

维护约 **5–8 个 Important Pressures**。

每个只写四行：

1. **Current belief**：社区现在认为/依赖什么？
2. **Pressure**：哪里不协调、未验证、changed、或互相冲突？
3. **Why now**：为什么今天第一次有合理 attack？
4. **Consequence**：A/B 两种世界分别会改变什么理解？

没有这四行，不生成 seed。

Pressure 来源优先：

1. Sasano 明确评价里暴露的“什么算有趣 / 不惊讶”；
2. ACL / EMNLP / NAACL / TACL 强 Main 的 load-bearing assumption；
3. 多篇论文之间的冲突；
4. 其他领域可以迁移的 identification logic。

不要从：

- future work 句子；
- 心理学术语列表；
- architecture component 列表；
- Fxx negative-space；
- “这个 exact cell 好像没人测”

生成题。

---

# 6. Seed 形成前先做两个廉价 Gate

## 6.1 Why-care Gate

用普通话一句话回答：

> **为什么一个普通 AI/NLP reviewer 会想知道答案？**

不能使用 mechanism / benchmark 专有名词。

过不了直接丢。

## 6.2 Early-crowding Gate

在投入实验设计前，先做一次**快速 collision search**：

- exact mother question；
- 最接近 decisive contrast；
- 最近 12–18 个月；
- 特别检查最近几周 arXiv / ACL Anthology。

这里只回答：

> **这个 parent 是否已经正在被一群人正面做？**

若是，默认换 lineage，不在热门缝隙里找 exact-cell novelty。

---

# 7. 锁定一个 seed 后才做深审

## 7.1 Knowledge-delta statement

必须写：

> **Prior 已知 X；Y 仍未知，因为 Z；我们的实验区分 A / B / C。**

Kill：

- same decisive unknown 已被回答；
- difference 只是 model/data/language/modality/condition；
- cleaner replication；
- paper A × paper B；
- novelty 只靠 exact cell。

---

## 7.2 No-Anomaly-Gamble test

问：

> 如果我们预期的“漂亮现象”完全不存在，mother question 还成立吗？

如果不成立，危险。

更理想的是：

> 实验无论落到 A 或 B，都直接区分两个事先存在的 scientific worlds。

但不要自欺欺人地说“所有结果都有故事”。

Null 只有在它排除一个真实理论或重要 assumption 时才算有价值。

---

## 7.3 Direct-Attack Gate

PILOT-AUTHORIZED 前必须已经有一个小而直接的实验：

- 直接操纵 scientific variable；
- 主要 worlds 给出不同 prediction；
- 第一刀就在回答 science。

危险：

- 先找 probe/vector；
- 先造 evaluator；
- 先建 benchmark；
- 先赌 construct 是否存在；
- 先做大规模数据工程。

---

## 7.4 Execution Gate

优先：

> existing ground truth → small programmatic stimuli → 少量自动生成 + spot check

避免：

- 大人工 annotation；
- LLM judge 作为核心真值；
- model zoo；
- optimizer × LR × dose × family 矩阵；
- 为救题不断增加 controls。

训练题尤其问：

> causal variable 是 scientific variable，还是 recipe/path 的复合产物？

如果需要 recipe matrix 才知道 qualitative conclusion，KILL。

---

# 8. Global Reset：防止 agent 陷入局部最优

这是硬规则。

Agent 最容易犯的错误不是不会查文献，而是：

> **一旦投入某个 seed，就开始把“救活这个 seed”误认为核心目标。**

真正核心目标始终是：

> **找到最值得做的问题，而不是证明当前候选还能做。**

出现以下任一情况，立即强制退出当前局部搜索：

- 连续 2–3 个 seed 因同一种原因死亡；
- 已经开始为一个 seed 不断加 controls / variants；
- 思考内容越来越像“怎么绕过 prior”；
- novelty 越来越依赖 exact wording / exact condition；
- mechanism 越来越复杂，但 why-care 越来越难；
- 连续在同一 lineage 内搜索；
- 最近看的论文主要只用于 kill；
- 讨论超过一半在当前 seed，而不是 scientific pressure；
- agent 开始把历史规则当目的，而不是工具。

### Global Core-Goal Check

强制回答五问：

1. **我们现在的核心目的是什么？**
2. **如果立刻删除当前 seed，哪个 scientific pressure 仍然值得追？**
3. **我们是在寻找问题，还是在保护 sunk cost？**
4. **当前 lineage 为什么比另外 2–3 个 lineage 更值得继续？**
5. **最近一次 Sasano feedback / 强 Main paper 给我们的真正校准是什么？**

如果答不清：

> **停止当前 seed，重新校准。**

### Reset 动作

1. 重新读 1–2 条 Sasano 真实评价；
2. 重新读 2–4 篇不同 lineage 的强 Main；
3. 写一句 drift diagnosis：
   > “刚才为什么偏离核心目的？”
4. 重建 pressure portfolio；
5. 允许把整个 lineage 丢掉。

规范本身也不能成为局部陷阱。  
如果 guide 开始让 agent 机械执行 checklist，而不是找到更好问题，**回到核心目的，允许改变流程。**

---

# 9. 历史 failed ledger 的正确用法

Failed files 是**索引和 anti-resurrection archive**，不是开局教材。

锁定 seed 后：

1. 搜关键词；
2. 搜 parent；
3. 搜关键 mechanism / contrast；
4. 只读命中的 Fxx 周边；
5. 判断是否实质复活旧题。

不要因为“没在 Fxx 里找到同名词”就认为新。  
也不要因为“某个 broad parent 曾被 kill”就自动 kill 新问题。

判断标准始终是：

> **same decisive unknown 是否已死 / 已被 prior 拥有。**

---

# 10. 最终 Binary Decision

一个锁定 seed 必须继续到：

> **PILOT-AUTHORIZED**

或：

> **KILL**

不向用户留下 SERIOUS / maybe 半状态。

PILOT-AUTHORIZED 必须同时满足：

- 一句话 why-care 清楚；
- Sasano/Main taste 合格；
- parent 不属于明显拥挤追热点；
- same decisive unknown 未被 prior 占领；
- 不依赖先赌一个 anomaly；
- 一个小实验能直接区分主要 worlds；
- mother question 与实际实验宽度匹配；
- data / construct / recipe / scale 不会自然爆炸。

允许整轮 **0 survivor**。

---

# 11. 当前正式状态

以 `README.md` / `SELECTED_TOPICS.md` / recent commits 为准。

截至 2026-09-21，repo 当前正式 selected：

- S04 — How Do Language Models Update Situation Models Across Event Boundaries?
- S06 — What Does Deliberation Do to Evidence?
- S07 — Where Does Surprise Go?
- S10 — Does the Language We Plan to Speak Change Event Construal?

这些都**不是正向 taste exemplar**，只是当前尚未被推翻、值得第一刀实验的候选。

S03 / S05 / S08 / S09 已 KILL。

如果聊天、旧 prompt、历史 re-audit 与 repo 当前状态冲突：

> **repo 最新状态优先。**

---

# 12. 只记住最后六句话

> **核心目的不是救 seed，而是找到最值得做的问题。**  
> **Sasano 的真实判断高于同门题材。**  
> **ACL / EMNLP / NAACL 强论文要用来学习怎么形成问题，不只是查重。**  
> **先有 scientific pressure，再有 A/B experiment；不要赌新现象。**  
> **热门 lineage 默认降权，复杂语言学默认谨慎。**  
> **一旦陷入局部思考，立刻 Global Reset，重新回到 why-care。**
