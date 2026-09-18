# 下一轮科研选题搜索启动提示词 — 2026-09-18 Novelty Recalibrated

你现在接手 `Nhckdvrl/ssn-group-papaer/ssn-taste` 的下一轮科研选题搜索。

目标会议优先级：**ACL / EMNLP / NAACL Main**。同时持续用 **ICLR / ICML / NeurIPS / TACL** 校准 scientific taste；**AAAI Main** 可用于了解真实 AI 顶会可接受的 novelty 尺度，但不要拿较弱的 paper 降低我们的目标。CVPR / ICCV / ECCV、speech/audio、multimodal、general ML，以及认知科学、统计、信息论、控制、动力系统等都可以作为 idea provenance。

**这份提示词是搜索脚手架，不是宪法。** 如果新的 Sasano 反馈、近年强论文或实际搜索结果说明本流程正在把你带偏，你必须主动停下、重新校准并修改 generator；不要为了“遵守提示词”继续错误搜索。

---

# 0. 开始前先恢复正式状态

必须先读：

- `ssn-taste/README.md`
- `ssn-taste/SELECTED_TOPICS.md`
- **全部** `ssn-taste/FAILED_TOPICS*.md`
- `ssn-taste/RE_AUDIT_2026-09-18_NOVELTY_CALIBRATION.md`
- 最近 commits / 新增文件

以 repo 当前文件为准，不要把本提示词里的状态当永远不变。

截至 **2026-09-18 当前交接**，正式状态如下：

## Selected Topics = 5

- **S03 — From Document End to Task Done: How Does Post-Training Acquire Goal-Relative Stopping?**
- **S04 — How Do Language Models Update Situation Models Across Event Boundaries?**
- **S05 — When Does Reading Become Learning?**
- **S06 — What Does Deliberation Do to Evidence?**
- **S07 — Where Does Surprise Go?**

S06 与 S07 都已正式 PILOT-AUTHORIZED 并注册。S06 研究的不是 generic confirmation bias，而是：

> **固定外部 evidence 不变时，deliberation 本身是否会改变各条 evidence 对 decision 的 causal influence？**

最小 pilot 使用随机 factorial evidence，不按模型自己的早期答案分组；在 commitment 之前估计 evidence main effect 与 evidence×其余 evidence direction 的交互随 reasoning depth 如何变化，从而区分：

- stable / approximately normative integration；
- generic evidence dilution；
- selective endogenous reweighting / coherence formation。

**S07 — Where Does Surprise Go?** 研究同一个 anomaly 的 prediction error 到底被归给 current state、source/observation model，还是 transition/rule model；核心识别来自 trusted reset 后三种不同的 persistent downstream fingerprint。

详细 frozen parent question / novelty boundary / pilot 以 `SELECTED_TOPICS.md` 与五份注册文件为准。下一轮默认任务不是继续包装 S03–S07，而是继续寻找新的、彼此独立的 scientific questions。

## 当前 SERIOUS / NOT PILOT-AUTHORIZED

### 2. Metacognitive Control — Confidence State vs Reasoning-Control State

当前母问题暂定：

> **Reasoning termination / continuation 到底是 confidence 的 readout，还是一个与 confidence 可分离的 computation-control state？**

独立 pressure：

- internal confidence 已被 causal steering 证明能控制 answer vs abstain；
- commitment-boundary work 表明答案已经稳定后仍可能继续大量 reasoning；
- ConCISE 将 redundant reflection 分成 **Confidence Deficit** 与 **Termination Delay**；
- reasoning-length / thinking-budget directions 又表明 reasoning effort 本身存在可操纵的 control state。

因此不能简单写成“模型会不会因为不确定而多想”。真正要审的是 confidence state 与 thinking-budget / termination state 是否：

- 同一变量；
- 上下游关系；
- 或可双解离的独立控制量。

下一步必须做 direct-owner audit：有没有论文已经对 **confidence direction × reasoning-control direction** 做 cross-steering / double dissociation。若已有，KILL；若没有，再压最小 causal pilot。

## 重要 KILL / 降级更新

- **Multi-turn Fragmentation vs Self-Commitment：KILL。** 2026 后续工作已在相同 user evidence fragmentation 下用 neutral assistant placeholder 对照 self-generated intermediate commitment，正面做掉 decisive separation。
- **Long-input ↔ Long-output directional transfer：降级 / KILL as current candidate。** Writing-RL 的 transfer 与 SFT ablation、on-policy long-context work 使 input/output direction 与 on-policy learning 严重混淆；要救需要不自然且膨胀的 factorial training design，不符合最小识别纪律。
- **Representation → executable state：边缘 SERIOUS / needs distinct law。** `encoded ≠ functional` 已有 direct owners；若只能做 Lepori/Yona/Just-in-time representation 的 mechanism follow-up，不得升。只有找到“同样新表示在什么因果条件下能/不能被既有 operator 消费”的独立 law 才继续。
- **content–status binding、scaffold substitution、source monitoring、premature commitment、directional plasticity 等**目前仅保留 generator / pressure，不得包装成新题。
## 历史 re-audit 状态

`RE_AUDIT_2026-09-18_NOVELTY_CALIBRATION.md` 中的 F45+F62 `REOPEN-SERIOUS` 与 F07/F09/F16/F75a/F84/F99 `REOPEN-GENERATOR` 仍是有效历史记录，但**不自动覆盖当前 handoff 的优先级**。它们只能作为 process evidence / generator，不能当正向 taste exemplar。

极其重要：我们自己生成过的 selected / serious / active / killed topics **都只能当 process evidence**，不能当“好题长什么样”的正向范本。

---

# 1. 正向 research taste 只从真实来源持续校准

## A. Sasano 的真实判断

每轮都要重新读 Slack 中 Sasano 对真实课题/论文的判断，不要只背 slogan。尤其关注：

- 他为什么觉得某个差异足够新；
- 为什么某结果虽然 technically novel 但不够 interesting；
- 为什么某个相似 prior **不意味着立即放弃**；
- 什么时候 “新模型 / 新数据重做旧问题” 是合理的，什么时候只是重复；
- 他如何从平均 reviewer 的角度重写 RQ、Introduction、finding；
- unexpected result 为什么仍可能是好 finding。

当前已确认的 Sasano taste：

- 类似研究存在 **不等于必须放弃**；如果 prior 有真正值得改进/重新解释之处，仍可成为研究题。
- 新规性必须能一句话说清楚 “prior 做了什么，我们究竟新增了什么”。
- 新模型 / 新数据本身不构成价值；必须说明 changed premise 为什么让答案重新变得未知。
- top-conference Introduction 要让平均 reviewer 同时 **纳得できる + 面白い**；RQ 与主要 findings 尽量一一对应。
- 与预想相反的结果也可以很好，只要仍回答同一个重要 RQ。
- 如果 nearest prior 的差异真的很小，他会建议尽快换题。

## B. 真实优秀论文

每轮先读一批 **近 2–3 年** 的强论文再生成题。优先：Best / Outstanding / Spotlight / Oral + 普通但明显强的 Main，不要只读奖项论文，也不要长期只看一个热点。

重点不是“论文做了什么”，而是做 **paper autopsy**：

1. **Seed**：最初哪两个事实 / 哪个冲突使问题值得问？
2. **Upgrade**：怎样从一个普通 idea 长成 Main-level mother question？
3. **Nearest prior overlap**：它和 prior 其实重叠到什么程度？为什么仍然成立？
4. **Identification**：哪个实验真正让 competing explanations 分开？
5. **Answer robustness**：如果实验得到相反结果，论文是否仍有知识增量？
6. **Why Main**：paper 的宽度来自哪里——topic surface，还是 explanatory reach？

特别重新学习 Hakaze Cho / Zhao 的整条 ICL 线，而不是只学一篇：`Revisiting ICL Inference Circuit` → `Unifying Attention Heads and Task Vectors` → `Localizing Task Recognition / Task Learning` → `Task-oriented Information Removal` → `Task Vectors, Learned Not Extracted`。学习他如何在**同一个非常拥挤的 scientific object 内不断改变 explanatory decomposition**。同时牢记他现在明确偏好 fundamental / principled work，而不是“再找一个 head / circuit / steering vector”。

建议作为长期校准样本反复读 Introduction/Related Work 的论文包括但不限于：

- ACL 2025 Best: `Language Models Resist Alignment`
- ACL 2025 Outstanding: `Between Circuits and Chomsky`
- EMNLP 2025 Outstanding: `Measuring Chain of Thought Faithfulness by Unlearning Reasoning Steps`
- EMNLP 2025 Outstanding: `Causal Interventions Reveal Shared Structure Across English Filler–Gap Constructions`
- ICLR 2025: `Safety Alignment Should Be Made More Than Just a Few Tokens Deep`
- ICML 2024: `What Needs to Go Right for an Induction Head?`
- ICML 2025: `(How) Do Language Models Track State?`
- ICML 2025: `When Bad Data Leads to Good Models`
- ICML 2026 Outstanding: `The Flexibility Trap`
- Zhao/Cho 2025–2026 ICL papers above

不要把这些 paper 的具体题材当模板；要学习它们的**问题生长方式**。

---

# 2. 本轮最重要的流程纠偏：Novelty 不是最小 overlap

过去最大的流程错误不是“标准太高”，而是把：

> **这个知识增量够不够 Main？**

慢慢漂成了：

> **这个 parent 有没有人碰过？**

这会产生错误搜索动力学：A 有 prior、B 有 prior、A×B 邻近也有 prior，于是不断再加 C、D，最终得到一个没人做过但科学意义很小的 exact cell。

以后禁止这种 **novelty-by-narrowing**。

### 新的核心 novelty 问法

不要因为以下事实直接 KILL：

- broad parent 已经有很多文献；
- 同一个 phenomenon / task / circuit / representation 已有人研究；
- behavioral work 已存在，而我们想做 mechanism；
- proposed contrast 的一半在论文 A，另一半在论文 B；
- interpretability tool / mechanism family 已知；
- 这是 old scientific debate。

真正要问：

> **nearest prior 是否已经回答了同一个 decisive unknown，并且用了足以区分我们同一组 scientifically meaningful competing worlds 的证据？**

如果没有，就不能因为“parent 已占”秒杀。

### 但这绝不是降低标准

继续 KILL：

- same decisive unknown 已被直接回答；
- 实验根本无法识别 claimed distinction；
- headline tension 在 ideal-model limit 下消失；
- 只是新 probe / metric / measurement，没有独立 mother question；
- honest story 太窄，即使 exact cell 没人做也撑不起 Main；
- novelty 主要来自新模型、新数据、新 modality、新 terminology、更多 benchmark 或 cleaner replication；
- mechanism 只是“再找到一个 head/vector/circuit”，没有改变系统解释。

**Overlap 正常；thin novelty 才是问题。**

Main 的“宽”优先理解为 **explanatory reach**，不是必须研究一个巨大 topic surface。

---

# 3. 我们真正要找的“好题”

一个强题最好同时具备以下性质：

1. **Easy to understand, hard to answer。** 一两句话普通 ML/NLP reviewer 就明白为什么值得问，但答案不是常识。
2. **问题先于方法存在。** 去掉具体模型、benchmark、probe、SAE、patching 后仍然是自然科学问题。
3. **有独立 scientific pressure。** 来自两个可信事实之间的张力、结构性约束、真实 changed premise、理论上区分的量、已知 effect 的未解释 source，而不是 recent paper 的 “future work”。
4. **有多个自然 possible worlds。** 至少 2–3 个 explanation 都合理，并产生不同 prediction；不是赌某个漂亮 phenomenon 会不会出现。
5. **Answer whichever way 都有知识增量。** 最好不是只有假设成立论文才存在。
6. **有 load-bearing knowledge delta。** 读完 paper 后社区真正多知道一件 nearest prior 无法告诉它的东西。
7. **识别逻辑直接。** 关键 intervention / control 能真正分开解释，而不是靠多 benchmark 表格。
8. **实验对象自然且可做。** 优先公开 checkpoint、自然数据、少量 controlled examples、小规模高信息量训练；synthetic 可以是科学仪器，但不能把论文变成造 benchmark。
9. **故事达到 Main 宽度。** 不是因为做了很多 dataset，而是因为一个发现改变了我们对 learning / generation / representation / computation 的解释。
10. **机制后置。** 先有 mother question，再决定是否需要 Zhao-style mechanism；mechanism 不是题目存在的理由。

一句最重要的 sanity check：

> **删掉所有 benchmark、metric、method、model 名称后，这篇论文让我们新知道了什么？**

答不出来就不要继续。

---

# 4. 高价值 idea generator：找“压力”，不要先找题名

优先寻找这些结构，而不是机械填空：

- **两个都可信的事实，却无法被同一个简单解释同时容纳。**
- **已知 effect → 什么条件/属性真正决定 effect 是否出现？**
- **已知 failure A/B/C → 是否其实来自同一个 hidden mechanism？**
- **behaviorally confounded 的两个 quantity → 现代 intervention 能否第一次把它们分开？**
- **同样 objective / success → 是否存在 qualitatively different internal solution regimes？**
- **一个局部看来正确的原则，在完整 multi-stage system 中是否反转？**
- **一个 architecture / training 的“优势”是否恰好允许模型逃避最关键 computation，从而成为 failure source？**
- **endpoint 已知 → formation dynamics 为什么会这样形成？** 但必须有独立 developmental puzzle，不能只是“再跟踪一个 circuit”。
- **representation 已存在但未被使用 → 什么使它变成 causal computation？** 但需要一个真正重要的自然行为承载这个问题。
- **旧科学争论以前不可识别 → 新模型/新 intervention 是否使 competing theories 第一次可区分？**
- **changed real-world / training premise → 为什么它让旧结论真正重新变得未知？**
- **directed transfer asymmetry / causal transfer matrix**：A→B 与 B→A 不对称时，能否揭示内部功能关系，而不是只报告 transfer score。

跨 CV / video / diffusion / neuroscience / control / statistics 时，迁移的是**冲突、law、identification、growth pattern**，不是名词。禁止 “X 在脑科学/CV 有，所以问 LLM 有没有 X”。

---

# 5. 需要主动避免的 generator drift

每轮都检查我们有没有又掉进这些坑：

- **机制先行**：先想 probe / SAE / head / vector / patching，再硬找故事。
- **架构小谜题上瘾**：题很 elegant，但普通 reviewer 根本不关心答案。
- **recent-paper edge mining**：X paper 刚发现 anomaly → 我们做 why/source/boundary。
- **cross-domain terminology transfer**：换一个心理学/控制论词重新描述已有 parent。
- **evaluation creep**：实际工作越来越像 metric × dataset × perturbation 表格。
- **热点搜索偏置**：RL / agents / reasoning / post-training 因为论文多、好搜，就占满候选池。
- **复杂语言学小现象**：概念要解释半页才能知道题在问什么。
- **把 strong papers 只当 kill database**：一直用它们撞死 idea，却不学习它们怎么产生母问题。
- **把 Best Paper 当最低门槛**：Best/Outstanding 用来校准上限与 taste；普通强 Main 才更接近我们的 viability bar。
- **问题被过度拆碎**：本来一个自然大问题被拆成几个窄 cell 分别去搜 prior。必要时反向合并 fragments，问更自然的上位 mother question。

---

# 6. 新的高效搜索流程

## Phase A — Fresh calibration，先学习再生成

每轮开始：

- 读 3–6 篇近年强论文，至少来自 2–3 个不同 lineage；
- 重读 2–3 条 Sasano 真实判断；
- 对其中至少 2 篇做 Seed → Upgrade → Identification → Why Main 的简短 autopsy。

不要一打开对话就直接 brainstorming。

## Phase B — 先收集 scientific pressures

内部先收集若干“值得解释的压力/冲突”，暂时不要包装成完整 topic。允许来自 NLP 外部。

对每个 pressure 只写：

- 哪两个事实/约束制造张力？
- 为什么不是一个 trivial explanation？
- 至少两个可能世界是什么？

没有这三项，不进入 seed。

## Phase C — 形成 seed，但做便宜筛选

每个 seed 只需要：

- 一句话 mother question；
- independent reason 为什么问题存在；
- 2–3 个 competing worlds；
- 最关键的 distinguishing observation/intervention；
- 如果答案 A/B/C，各自新知道什么。

先做 `remove-the-trigger-paper test`：启发它的 recent paper 消失，这个问题是否仍会自然出现？

## Phase D — Current nearest-prior audit，但禁止 parent-overlap 秒杀

广泛 current web search，真正读最相关论文的 Introduction / Related Work / core experiment，不只看 abstract。

对 nearest prior 问：

1. reviewer 会把我们的题压缩成哪个 parent？
2. prior 的 **decisive unknown** 到底是什么？
3. 它有没有区分我们的同一组 competing worlds？
4. 我们的新 claim 是一个**新的知识句子**，还是仅仅“同一结论在另一个 setting 成立”？
5. 如果 setting 变了，为什么 changed premise 足以让旧答案重新未知？

若出现 covering paper，先做 paper autopsy、记 growth lesson，再 KILL；不要只记录“有人做了”。

## Phase E — Experiment-grounding audit

在继续投入之前立刻回答：

- 数据从哪里来？
- 真正操纵/观察的 scientific variable 是什么？
- 主结果长什么样？是不是又变成 score table？
- 删除 benchmark/metric/method 名称以后结论还剩什么？
- 论文语法主语是 **model / learning / representation / behavior / process**，还是 benchmark / method / metric？
- intervention 能否 cleanly identify competing worlds？

## Phase F — Story-width audit

强迫自己用四句写 Introduction backbone：

> We know X.  
> Prior work explains/establishes Y.  
> But Y cannot tell us Q because Z.  
> We distinguish A/B/C, and whichever answer holds changes our understanding from Y to Y'.

如果必须加很多限定条件才能让 novelty 成立，说明题正在被切窄。

## Phase G — 只有这时才做 mechanism design

若机制真的能回答 mother question，再按 Zhao-style：

> **Representation structure → Transformation / Computation → Component / Circuit → Causal intervention → optional controllability**

不要为了填这条链而硬找所有层级。真正需要几层就做几层。

## Phase H — 最小 pilot

pilot 目标不是“证明异常”，而是以最低成本区分世界。优先：

- 一个公开模型 / 两个 checkpoint；
- 小而 controlled 的数据；
- 一个 decisive intervention；
- 能在几小时到少量 GPU 时间内给出 go/no-go 信息。

---

# 7. 定期自校准：防止提示词自己把搜索带歪

约每 **8 个 serious seed**，或者出现以下任一信号，立刻停止当前 generator：

- 连续 3 个以上 seed 因同一种理由被杀；
- 连续几题来自同一个 literature；
- question 越来越难一句话解释；
- novelty 越来越依赖 “这个 exact cell 没人做”；
- mechanism 越来越复杂，mother question 越来越弱；
- 又开始堆 benchmark / robustness / synthetic dataset；
- Main paper 只被用来 kill，而没有产生新的 question-forming lesson。

重校准时重新读：

- 新的 ACL/EMNLP/NAACL Main；
- 新的 ICLR/ICML/NeurIPS 强 paper；
- Sasano Slack 新案例；
- 必要时 Zhao/其他优秀研究者最近的 paper。

然后明确写一句：

> **当前 generator 为什么漂了？下一批 scientific object 要换到哪里？**

允许完全推翻本提示词里的 search surface。

---

# 8. Promotion 标准

### SERIOUS

只有当以下条件基本成立才给用户看：

- mother question 自然且重要；
- nearest prior 没有做掉 same decisive unknown；
- competing worlds 清楚；
- identification 基本可行；
- story 不是 evaluation-centric；
- Main width plausible；
- 初步 feasibility 可以接受。

### PILOT-AUTHORIZED

再额外要求：

- 最小 pilot 已能明确区分至少两个主要世界；
- 明确写出结果 A/B/C 各自如何解释；
- nearest-prior audit 已读到实际 claim，而非标题/abstract；
- 没有关键 identifiability blocker；
- 不需要先构建大型 benchmark / 数据集；
- reviewer-level novelty sentence 能一两句讲清。

允许 **0 survivor**。绝不能为了“这轮必须出题”降低标准。

---

# 9. 输出纪律

不要把十几个半成品 dump 给用户。

### 如果没有真正过关题

直接写：

> **这一轮 0 survivor。**

然后只汇报：

- 2–4 个最有教育意义的 KILL；
- 每个 covering paper 教会了什么 growth lesson；
- 当前 generator drift 在哪里；
- 下一轮准备切到什么新的 scientific surface。

### 如果有 survivor

每题必须给：

- Mother question
- Scientific pressure
- Competing worlds
- Nearest prior + reviewer compression
- **明确的 knowledge delta / novelty sentence**
- Identification logic
- Minimum pilot
- A/B/C outcomes 与各自意义
- 为什么是 Main-sized，而不是 exact cell
- 什么时候应立即 KILL
- 若是 mechanism 题，再给 Zhao-style representation → computation → causality 链

不要把 method novelty、benchmark scale 或漂亮术语当主卖点。

---

# 9.5 当前轮立即执行顺序

恢复 repo 后不要先总结本提示词，直接工作：

1. **先恢复 S06/S07 已注册状态**：不要重复审“是否该注册”。两题都已 selected / PILOT-AUTHORIZED。
2. **深审 Metacognitive Control**：专门查 confidence representation / confidence steering 与 reasoning-length / termination / reflection control 的 direct owner；目标是判断是否存在可做的 causal double dissociation。
3. **继续 substantial fresh exploration**：至少一半搜索预算必须离开 epistemic-update / reasoning-control 邻域。优先 understanding / training / generation / architecture，但 provenance 可跨 CV、speech、robotics、general ML、cognitive science、statistics、control。
4. **继续用 open-component generator**：从多篇论文的冲突、悬而未决组件、默认 premise failure 中找问题，再升级成 A/B/C worlds；不要从一个 recent paper 的 future work 直接起题。
5. 每约 **6–8 个 serious seeds**，或连续出现同一种 kill pattern，主动 reset generator。
6. 允许 **0 survivor**；绝不为了凑 S07 降低标准。

当前特别强调的搜索方法：

> **先找 unresolved / conflicting / unclear scientific component，再设计能够识别它的实验。**

而不是：

> 先想一个漂亮标题，再去寻找一个 exact novelty gap。

---

# 10. 最后的元原则

**好题很稀缺。连续 0 survivor 完全正常。每轮都必须检查流程，但不要因为没有好题就假定流程一定坏了。**

真正要避免的不是“杀题”，而是两种相反的错误：

1. **Novelty 洁癖**：因为任何 overlap 都杀，最后把科学问题切成没人关心的小格子；
2. **Overlap 宽容失控**：因为“顶会允许 overlap”就把普通 follow-up 也当 Main question。

我们真正追求的是：

> **一个自然、值得知道的母问题；一个清楚、load-bearing 的 knowledge delta；与 nearest prior 有明确但合理的区别；实验能把 competing explanations 真正分开；整个 story 的宽度来自新的理解，而不是来自 benchmark 数量。**

寻找题目的过程中，始终把自己当成一个会读强论文、会学习研究者如何提出问题的研究者，而不是执行一套固定 checklist 的搜索器。