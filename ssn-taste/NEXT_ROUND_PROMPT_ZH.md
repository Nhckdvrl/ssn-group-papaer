# 下一轮 Sasano-Taste 科研选题搜索启动提示词

当前日期：2026-09-16。

你现在接手 `Nhckdvrl/ssn-group-papaer/ssn-taste` 的下一轮 NLP/LLM 科研选题搜索。

目标会议：**ACL / EMNLP / NAACL Main**。辅助校准：**TACL / ICLR / ICML / NeurIPS**。EACL / AACL / Findings / workshop / arXiv 可以用于查重、nearest-prior、collision，但不能作为主要正向 taste。

**当前正式 selected topic = 0。** S01 和 S02 均已取消注册。允许这一轮最终仍然是 0；绝不能为了留下题而降标准。

---

# 0. 这一轮最重要的新纠偏：不要再找“评测题”

用户明确不要以以下内容为主贡献的题：

- benchmark construction；
- 新 evaluation set / challenge set；
- metric validity / metric comparison；
- robustness benchmark；
- “方法 A/B/C 在 perturbation X 下谁更稳”；
- 大量 synthetic data construction 后比较现有方法；
- 主要结果是一张 leaderboard / accuracy/F1/correlation/robustness table；
- 高层 framing 看起来像科学问题，但真正实验落地只是“造测试集 + 跑模型 + 比指标”。

**Evaluation 可以作为实验工具，但不能成为 paper 的 scientific object。**

优先找真正的探究型 scientific question：研究语言、模型、学习、训练、表示、生成行为、交互、资源分配或现实语言过程本身的规律，而不是研究“现有方法测得准不准”。

上一轮 C2/S02 是必须记住的反例：

> “AI rewrite 是否制造虚假 semantic change”听起来像 changed-premise scientific question，但真正落地后需要 synthetic rewrite data、semantic-preservation validation、LSC method comparison 和 robustness metrics；现实数据又缺 ground truth。于是 scientific framing 高于 actual experimental object，最终退化为 evaluation paper。

以后这种题必须在注册前就杀掉。

---

# 1. Sasano taste 是生成 prior，不是事后 filter

不要先随便生成技术 gap，再拿“Sasano fit”去包装。**从问题产生的第一步就按照 Sasano 的思考方式。**

已确认的核心锚点：

- **Sato：最强正例。** 人人能理解的自然 puzzle → 明确未知 scientific object → 几个自然竞争解释 → controlled experiment 区分。学习的是思考方式，不是机械复制“来源分析”。
- **Guo：最强负例。** Sasano 明确指出「先行研究との差が小さい」。旧问题 + 新模型、新语言、新数据、新 condition 通常不够。
- **Hamdi：** 从普通 reviewer 视角，Introduction 必须“纳得 + 有意思”；RQ 与 finding 清晰对应；unexpected finding 也可以成立；机制不是硬要求。
- **Utami：** 真正的现实技术/社会变化可以创造新问题，但必须是一个明确 changed premise 导致一个清楚、可研究的语言/行为后果，不是泛泛“LLM 改变语言”。
- **Kisako / Tsukagoshi：** 两种成熟操作围绕同一个自然 quantity/resource 形成系统 trade-off 或 interaction，可以是好科学问题；不必强求深机制。
- **Oshika：** 成熟 workflow 中一个必要的独立中间 decision 如果长期由 human/gold/oracle 给定，可以成为 Main-sized scientific object。
- **Youchi / Yano：** 类似 prior 并不自动杀题；但必须存在 load-bearing structural defect，修复后改变 inference、研究对象或能力，而不是“我们做得更完整”。

每个候选在深入前先写 3–5 句：

> **如果 Sasano 自己从现象/问题出发，他为什么会自然问出这个 RQ？**

如果写出来像：

> “Paper X 做了 A，但没测 B，所以我们测 B”

默认是跑偏。

---

# 2. 我们到底想要什么题

一个强候选应当尽量具有这些性质：

1. **一句话就能说明为什么值得知道。** 不依赖复杂术语和 rhetoric 才显得重要。
2. **问题先于方法存在。** 换掉具体模型、metric、benchmark，母问题仍然成立。
3. **研究对象是真实 scientific object。** 例如学习规律、表示规律、行为规律、语言规律、训练规律、交互规律、资源 trade-off、现实语言过程、因果来源，而不是“evaluation performance”。
4. **探究型而非赌博型。** 至少两三种自然结果都能回答同一个 RQ，而不是只有发现 anomaly 才有 paper。
5. **但“多结果可解释”还不够。** 必须检查实际实验是不是仍然只在评测方法。C2 就是教训。
6. **novelty 看 reviewer compression。** 不看 exact keyword gap；要问 reviewer 会把它压缩到哪个 parent literature。
7. **Main-level width。** RQ 的抽象层级参考真实 ACL/EMNLP/NAACL Main Introduction，而不是越大越好、越窄越安全。
8. **数据自然、初期便宜。** 优先直接可取的现成自然数据、公开模型/checkpoint、小规模 controlled intervention；不优先大规模人工标注或 synthetic benchmark construction。
9. **硕士可执行。** 初期最好一天到几天就能跑一个 informative pilot，而不是先花一个月造数据。
10. **机制不是入场券。** descriptive/systematic finding 可以成立，只要 scientific question 本身强。

---

# 3. 绝对不要再混淆“探究型”和“评测型”

这是上一轮最关键的新教训。

**探究型：**

> 我们不知道模型/语言/训练过程本身遵循什么规律；设计干预去区分几个自然解释或刻画一个真实规律。

例如抽象结构：

- 同一能力来自 A 还是 B？
- 一个训练操作改变的是 quantity X 还是 Y？
- 两种自然 operation 在同一 resource 下如何 trade off？
- 某种 knowledge 在 representation / behavior / training dynamics 中怎样形成或转移？
- 某个现实语言过程在新技术介入后到底如何改变？

**评测型：**

> 我们不知道 method/metric/model A 在某个 test condition 下表现如何，所以造数据去测。

即使它有多个可能结果，即使结果都“有意义”，它仍然可能只是 evaluation。

### 强制的“实验落地审计”

任何候选在进入 serious pool **之前**，必须回答下面 5 个问题：

1. **数据从哪里来？** 是已有自然数据，还是我们必须大量合成/标注？
2. **实验真正改变/观测的变量是什么？** 是 scientific quantity，还是只是 benchmark condition？
3. **主结果最可能长什么样？** 如果核心是一张 `method × dataset/perturbation × score` 表，危险。
4. **如果去掉所有 metric 名称和 benchmark 名称，这篇论文还发现了什么关于语言/模型/学习的事实？** 如果答不出来，杀。
5. **论文的主语是谁？** 应优先是“language/model/training/representation/behavior/process”，而不是“metric/method/benchmark”。

这是 sanity check，不是为了制造复杂 gate；目的是提前发现“漂亮 framing，实际评测”的假科学题。

---

# 4. Idea 从哪里来：优先研究对象，而不是模板

不要机械枚举 provenance 模板。每轮先大量读真实 Main paper 的 Introduction + Related Work，学习**研究者是如何形成 question 的**。

当前比较值得继续搜索的来源：

### A. 自然 puzzle / 两个对象被模型训练目标或表面行为混在一起
例如 A 与 B 在表面高度相关，但理论上是不同 scientific quantities。要能设计一个 intervention 让 A/B 给出不同预测。重点研究模型到底学了什么，不是设计一个新 benchmark。

### B. 学习来源 / acquisition / representation formation
某种能力已经存在，但它究竟由哪类训练信号、数据结构、阶段或表示形成？必须存在自然 competing explanations，且 parent 没被直接占掉。

### C. Training operation 改变了什么
不是“新 recipe 提升多少分”，而是某个广泛使用的训练操作对学习 dynamics、generalization、representation、behavior 的系统作用是什么。最好有 matched intervention。

### D. 自然 trade-off
两个普通成熟操作服务同一目标/resource，却可能消耗或保留不同信息；研究 trade-off/interaction 的规律。不要把任意两种超参数硬配成 trade-off。

### E. Hidden oracle / missing decision
传统 NLP/LLM pipeline 里某个独立必要 decision 被默认为给定；研究这个 decision 本身，而不是做整个 pipeline benchmark。

### F. Changed premise 产生新的“现象问题”
新技术/社会实践真正改变了语言使用或学习环境，问新的语言/行为现象怎样形成。**注意：changed premise 不等于自动合法。** 如果落地只是“旧 metric 在新 distribution 上准不准”，仍然杀掉。

### G. Old scientific debate + new identifying operation
现代模型让过去无法区分的科学解释第一次可被 controlled intervention 区分。目标是解决 debate，不是“用 LLM 重跑经典 task”。

### H. Cross-lineage collision
两个成熟 literature 对同一 scientific quantity 有不同假设，交叉后产生新的预测。不是 Paper A + Paper B 拼接。

降低优先级甚至默认禁止：

- measurement validity / metric auditing 作为主线；
- benchmark gap；
- robustness under X；
- 数据 contamination 检测；
- “现有方法在新环境是否失效”；
- generic agent/tool-use reliability；
- RAG；
- 大型 data construction。

---

# 5. 搜题流程：顺序必须改对

## Phase 1 — 先校准 taste，再生成

每轮开始：

1. 回看 Sasano Slack 的真实评价与同门 project；
2. 读若干近期 ACL/EMNLP/NAACL **Main 普通强论文**，不只看 Best；
3. 重点读 Introduction + Related Work；
4. 总结它们的 RQ 来源、scientific object、nearest-prior 差异和实验形态。

Main paper 用于**正向学习“什么问题值得问”**，不是只用来查重。

## Phase 2 — 找 scientific pressure，不找 exact gap

先搜：

- 一个自然矛盾；
- 一个经典但仍未解决的 distinction；
- 两个 competing explanations；
- 一个学习/训练/表示过程中的未知 quantity；
- 一个自然 trade-off；
- 一个真正改变对象的现实 premise。

不要从：

> “没人测这个组合”

开始。

## Phase 3 — 每次只锁一个最强候选深审

不要同时养十几个半成品。一个 seed 真正有希望，就停下来：

- 广搜 nearest prior；
- 实读最近论文的 Introduction / Related Work；
- 找 parent RQ；
- 做 reviewer compression；
- 对齐 Sasano reasoning；
- 对齐真实 Main scope；
- **立即做实验落地审计。**

深审完必须明确：继续 / kill。然后才换题。

## Phase 4 — Novelty 审的是 parent，不是 exact experiment

必须回答：

- prior 已经拥有的母问题是什么？
- reviewer 会一句话怎么描述我们的工作？
- 如果去掉新模型/新语言/新 dataset/new condition，我们还剩什么？
- 是否只是“已有问题 + cleaner experiment”？

Remove-the-trigger-paper test 继续保留：

> 如果启发 idea 的那篇新论文消失，这个问题还会不会自然存在？

如果不会，通常只是 follow-up。

## Phase 5 — 在注册前才设计最小 pilot

只有前面都过了，才问最小实验。

最小 pilot 必须：

- 数据能立刻拿到；
- manipulation/observation 直接对应 RQ；
- 不需要先造 benchmark；
- 不需要大量 judge/annotation 才能定义 ground truth；
- 最好小规模就能区分解释或揭示结构。

如果此时才发现：

> “其实数据根本不好找，只能自己合成；最后就是跑若干 metric。”

**立刻 kill，不要因为前面已经投入很多时间而护题。**

---

# 6. 为什么上一轮会把垃圾题当宝贝：必须避免的认知错误

### 错误 1：过度奖励“漂亮的一句话 distinction”
`X ≠ Y` 很容易听起来聪明，但一句话漂亮不代表 scientific object 强。必须看实验到底研究什么。

### 错误 2：把 changed premise 当成自动 novelty
“LLM 时代出现了新 distribution/process”不够。新 premise 必须产生一个新的 scientific phenomenon/question，而不是仅产生新的 evaluation condition。

### 错误 3：只做 parent novelty audit，没有做 experimental-object audit
C2 在 literature level 看似有独立 intersection，但一落地就变成 LSC robustness evaluation。以后 novelty audit 后必须立刻审实验形态。

### 错误 4：把“所有结果都能解释”当成探究型充分条件
这只说明不是 anomaly gambling；并不能证明它不是 benchmark/evaluation paper。

### 错误 5：为了让题看起来 Main-level，用 rhetoric 抬高 scientific object
如果实验只能支持“method A 对 perturbation X 不稳”，就不能包装成“我们研究 semantic inference 的 fundamental invariance”。Claim 必须由实际实验自然长出来。

### 错误 6：没有在早期问“数据到底在哪”
一个真正适合硕士快速做的题，数据路径应该在早期就能说清楚。需要创造复杂 ground truth 才能成立，是强烈危险信号。

---

# 7. 定期偏航审计

每认真审 8–12 个 seed，或者连续几个 seed 都来自相似方向时，暂停检查：

- 是否又从 recent paper 的 mechanism/future work 挖题？
- 是否又追 RL/agent/tool-use 热点？
- 是否又在 exact gap 里越钻越窄？
- 是否又出现 benchmark / metric / robustness / synthetic-data 主导？
- 是否数据路径越来越人工、越来越昂贵？
- 是否 Main paper 只被用来 kill，而没有用于正向学习 RQ formation？
- 是否 Sasano 的真实 reasoning 已经退化成几个口号？
- 最近的题如果删掉技术术语，普通 reviewer 还能不能一眼明白为什么值得知道？

如果同一种失败连续出现，不要继续润色 seed；**更换 idea generator / scientific object。**

---

# 8. 当前明确禁止复活

先读 `ssn-taste/FAILED_TOPICS.md` 和 `ssn-taste/SELECTED_TOPICS.md`。

特别注意：

- **S01 / F06 — optional tool default / effective action semantics：不复活。** Parent 会被 reviewer 压成 underspecified tool intent / argument completion；exact default 只是小 cell。
- **S02 / C2 — AI rewrite ≠ semantic change：不复活。** 主要问题不是“结果不确定”，而是落地后本质是 synthetic-data + LSC metric/method robustness evaluation，同时现实数据缺 clean ground truth。
- 以前 ledger 中已经 kill 的方向不要换名重生，除非发现真正改变原 kill reason 的新证据。
- Temporal Forgetting / forgotten≠erased family 继续禁止复活。

---

# 9. 下一轮的执行要求

开始后不要给我一堆半成品 idea。先广搜和校准；找到一个真正最强的 seed 后，**锁住它，深审到底，明确 kill / serious**，再换下一个。

但不要为了“深审”而强行救题。发现根本缺陷就立即杀。

每个准备汇报的 serious candidate 至少要能用非常短的话回答：

> **RQ 是什么？为什么 Sasano 会自然问？nearest parent 是什么？真正 novelty 是什么？数据在哪里？最小实验到底做什么？实验是在研究现象，还是只是评测方法？无论哪种自然结果，论文分别学到了什么？**

其中任何一项答得含糊，就还不能注册。

最终目标不是尽快凑出 selected topic，而是找到真正对齐 **Sasano + ACL/EMNLP/NAACL Main**、同时用户愿意真正投入去做的探究型 scientific question。
