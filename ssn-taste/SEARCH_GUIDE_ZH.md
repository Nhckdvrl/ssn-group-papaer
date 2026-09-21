# ssn-taste 科研选题搜索指南（Canonical）

最后系统整理：2026-09-19

这份文件是 ssn-taste 的长期找题规范。它描述“怎么找题”，不保存某一轮临时候选。
当前正式选题状态以 README.md、SELECTED_TOPICS.md、各 Sxx registration 和最新 commits 为准。

---

# 1. 目标

优先目标会议：

- ACL Main
- EMNLP Main
- NAACL Main

持续用以下会议校准 scientific taste、问题宽度和 mechanism depth：

- TACL
- ICLR
- ICML
- NeurIPS

可以广泛从以下领域获取 idea provenance：

- CVPR / ICCV / ECCV
- image / video generation
- multimodal
- speech / audio
- robotics
- general ML / optimization
- cognitive science / neuroscience
- statistics / information theory
- control / dynamical systems / statistical physics

但跨领域迁移的对象必须是：

> scientific pressure、矛盾、competing explanations、identification logic、directed asymmetry、regime change、paper-growth pattern。

禁止机械迁移名词：

> “人类有 X，所以问 LLM 有没有 X”
> “CV 有 Y，所以把 Y 换成 language”
> “控制论里叫 Z，所以给旧现象换个 Z 的名字”

---

# 2. Repo 真相源与文件职责

每次新一轮开始，先恢复 repo，不能相信旧 prompt 或聊天摘要永远最新。

必须读取：

1. README.md
2. SELECTED_TOPICS.md
3. 全部当前 selected topic registration
4. 全部 FAILED_TOPICS*.md
5. RE_AUDIT_2026-09-18_NOVELTY_CALIBRATION.md
6. 最近 commits / handoff

优先级：

> 最新 repo 正式文件 > 历史 handoff > 旧聊天状态。

各文件职责：

- README.md：当前正式状态与目录索引。
- SEARCH_GUIDE_ZH.md：长期 canonical 搜题规范。
- NEXT_ROUND_PROMPT_ZH.md：下一轮 agent 的短 handoff，只保存当前状态与启动动作。
- SELECTED_TOPICS.md：只有已经 PILOT-AUTHORIZED 的题。
- Sxx_*.md：冻结该题的 mother question、novelty boundary、pilot、kill condition。
- FAILED_TOPICS*.md：防重复、防复活、学习失败模式；不是 taste exemplar。
- RE_AUDIT_2026-09-18_NOVELTY_CALIBRATION.md：历史 novelty 纠偏记录；不是 active candidate list。

当前自己生成过的任何题——无论 selected、serious、active、failed、S/L/F/Unring——都只能作为：

- process evidence；
- dedup / anti-resurrection evidence；
- 实验资产复用来源；
- 搜索失败诊断。

绝不能把它们当“好题应该长这样”的正向 taste exemplar。

---

# 3. 正向 scientific taste 只来自真实外部来源

## 3.1 Sasano 的真实判断

每轮都应该重新抽样 Sasano 对真实学生课题/论文的反馈，而不是把几句 slogan 永久固化。

目前最稳定的判断模式：

- Sato 型：简单直观的 puzzle → 清楚 scientific object → 自然 competing explanations → controlled experiment 区分。
- Guo 型：如果和 prior 的区别只是新模型、新语言、新数据、新条件，通常 novelty 不够。
- Hamdi 型：Introduction 要让普通 reviewer 同时“納得できる + 面白い”；RQ 与主要 findings 对齐；unexpected result 完全可以成为好结果。
- changed-premise 型：旧问题可以重做，但必须指出哪个 premise 真的变了，以及为什么旧答案不能直接推出新答案。
- Yano / Youchi 型：相似 prior 不自动 kill；如果缺失 control 或 structural defect 会改变原论文解释，successor work 可以成立。
- mechanism 不是必选项：一个 clean behavioral / learning law 也可以 Main-sized。
- technically fancy 不等于 mother question 有价值。

## 3.2 强论文 calibration

每轮至少抽样几篇近年的强 ACL / EMNLP / NAACL Main，并用 ICLR / ICML / NeurIPS / TACL 做补充。
Best / Outstanding 用来学习 taste 上限，不是最低门槛；普通但明显强的 Main 更适合校准正常 novelty 尺度。

读论文时不只问“做了什么”，而要做 paper autopsy：

1. Mother question 是什么？
2. 在 method / benchmark 出现以前，为什么这个问题就值得问？
3. 原本有哪些 scientific pressures / contradictions？
4. 有哪些真正不同的 possible worlds？
5. 哪个 experiment 真正把它们分开？
6. 如果结果反过来，paper 还成立吗？
7. 它怎样从一个 seed 长成 Main-sized story？
8. 它和 nearest prior 实际重叠了多少？为什么 overlap 没有杀掉它？

重点学习 Zhao / Cho 一类 mechanistic work 的出题方式：

> 同一个很拥挤的 scientific object 可以连续做很多篇，只要 explanatory decomposition 真正改变。

不要学习成：

> “再找一个 head / vector / subspace / circuit”。

---

# 4. 用户真正想要的题

优先偏好：

- mechanistic interpretability / LLM science
- learning / post-training
- reasoning / inference
- architecture / inductive bias
- generation
- understanding
- 简单但根本的问题
- 形成过程 / learning dynamics
- internal computation / functional architecture
- 可以用小而直接的 experiment 识别的问题

不偏好：

- benchmark / dataset 作为主贡献
- evaluator / metric validity
- RAG
- data-centric work
- model-zoo
- 大规模人工造数据
- complicated linguistics
- “新模型重新测老现象”
- RL / agents / RLVR 仅仅因为热门
- method stacking
- 工程刷分
- 一个已知现象后面机械接 mechanism

简单语义、受控 synthetic micro-world 可以使用，但必须只是 identification instrument，不得变成论文主体。

---

# 5. 好 mother question 的最低形态

好的问题通常满足：

- 一句话普通 reviewer 能懂。
- 在知道答案以前就值得问。
- 删除所有 model / benchmark / method 名称以后仍然成立。
- 至少有 2–3 个 qualitatively different possible worlds。
- 不同世界成立会改变我们如何理解 learning / computation / representation / generation / understanding。
- 有一个相对直接的 experiment 能明显压缩 explanation space。
- 结果不依赖“effect 必须显著且方向符合我们猜测”才能写 paper。
- Main-size 来自 explanatory reach，而不是实验数量。

核心 sanity check：

> 去掉所有专有名词后，这篇论文告诉我们关于模型学习、理解、生成、推理或内部计算的什么新事实？

如果答案只是：

> “在 dataset D 上 method M 比 baseline 高 X 分”

直接淘汰。

---

# 6. Novelty：Main-level knowledge delta，不是零 overlap

AI/NLP 论文不要求数学意义上的完全无交叉，也不要求把所有可能 confound 消灭到绝对严谨。

正常 Main paper 与 prior 有大量 overlap 很常见。

真正应该问：

> nearest prior 是否已经回答了同一个 decisive unknown，并且已经用足够的 evidence 区分了我们关心的同一组 possible worlds？

不要因为以下理由自动 kill：

- broad parent 已有人做；
- behavior 已有人观察；
- 相关 mechanism tool 已有人用；
- 一个世界在 paper A 出现、另一个世界在 paper B 出现；
- 同一 scientific object 很拥挤；
- 论文作者在 future work 里提过类似方向。

真正的 kill：

- same decisive unknown 已经被直接回答；
- reviewer 一句话就能用已有论文的核心 finding 原封不动描述我们的贡献；
- novelty 主要是新模型 / 新数据 / 新语言 / 新 modality / 新名词；
- 只是 cleaner replication；
- 只是 paper A × paper B 的交集；
- 为逃 prior 不断把题切成更小 exact cell；
- honesty 之后的 mother question 太窄，不够 Main；
- experiment 无法识别主解释；
- story 实际是 benchmark / evaluation / method comparison。

Reviewer compression 必须写出来：

> Prior 已经知道 X。
> 但 Y 仍然未知，因为 Z。
> 我们的实验第一次区分 A / B / C。

如果这三句写不清楚，继续审，不要靠 rhetoric 硬升。

---

# 7. 不要过度严谨到把题杀死

过去一个明显 drift 是：

> 一发现 prior overlap 或一个潜在 confound，就继续把题压窄，直到只剩没人研究的小缝。

要避免。

要求控制的是：

> 会改变核心 scientific interpretation 的 load-bearing confound。

不要求：

- 每个 surface factor 都完全 orthogonal；
- 每个 possible mechanism 都一次性排完；
- pilot 阶段就达到 theorem-like identification；
- 一个 Main story 必须和所有论文零交集。

小实验只需要让主要 possible worlds 给出不同 prediction，并让 reviewer 相信主解释空间真的被压缩。

如果为了消除一个次要 confound，需要把 4-arm design 膨胀成 20-arm factorial、造很不自然的环境、或引入大量 auxiliary assumptions，应重新判断：

> 这个题是不是本来就不可识别，还是我们在追求不必要的完美？

---

# 8. 最有效的 idea generator：先找 scientific pressure，不先想标题

当前最重要的搜索方式：

> 先找 unresolved / conflicting / unclear component，再升级成实验问题。

不是：

> 先 brainstorm 30 个漂亮标题，再给每个找 novelty gap。

## 8.1 多论文冲突 / open component

优先找：

- Paper A 的结果支持解释 X；
- Paper B 在另一个 setting 下更像解释 Y；
- Paper C 出现 X/Y 都解释不好的结果；
- 社区知道这些结果，但没有把隐藏变量 H 单独拿出来识别。

然后问：

> 有没有一个更底层的 quantity / relation / control state，使这些结果成为不同 regime 下的自然表现？

## 8.2 默认被当成同一个量，其实可能不同

非常高价值：

- endpoint performance 与 future learnability
- accessibility 与 stability
- representation 与 causal deployment
- confidence 与 control
- reading / use / writing
- quality 与 memorization
- local success 与 global computation

重点不在这些具体例子，而在结构：

> 社区用一个 observable 代理两个不同 scientific quantities。

## 8.3 Directed asymmetry

如果观察到：

> A → B，但 B ↛ A

不要停在 transfer score。

问：

> 这种方向性是否说明 A 包含 B 的 prerequisite computation / control relation / richer state？

但必须排除简单 training-procedure confound；如果要靠巨大 factorial 才能救，kill。

## 8.4 Changed premise

旧 failure 常被解释为 architecture/objective/premise P。

如果新系统真正移除了 P，但 failure 仍存在：

> 原解释空间必须重开。

前提是“premise 真改变”，不是“模型更新了一代”。

## 8.5 Endpoint → formation dynamics

如果 endpoint mechanism 已知，但形成过程存在独立 puzzle：

> 哪个 intermediate state / learning pressure / transient computation 让 final mechanism 成为可学习？

不要做无压力的 checkpoint archaeology。

## 8.6 Same behavior, different computation

相同成功行为可以由不同算法、不同 internal route 完成。

好问题不是：

> probe 能不能 decode？

而是：

> 什么决定模型选择哪种 computation？这些 computation 在 transfer / intervention / failure 下有什么不同？

## 8.7 Constraint / flexibility changes computation

值得问的不是 generic regularization。

而是：

> 一个 constraint 是否迫使模型采用 qualitatively different algorithm？
> 一个看似有利的 flexibility 是否反而允许模型绕过 globally decisive computation？

## 8.8 Hidden decision / hidden oracle

成熟 workflow 中如果存在一个必须由人工/gold/oracle 做出的中间判断，而模型/理论从未把它当 scientific object：

> 那个决定本身可能就是问题。

## 8.9 旧科学争论获得新的 identification

认知科学、统计、控制等旧问题可以借现代模型获得新的干预能力。

但贡献必须是：

> competing theories 以前不可区分，现在第一次可区分。

不是：

> “LLM 是否也有人类现象 X？”

---

# 9. 高风险 generator：默认禁止

以下模式除非有非常强的独立 pressure，否则默认不追：

1. Recent paper X → “为什么会这样？”
2. Recent paper X → future work 原句。
3. Behavior 已知 → 再找 mechanism。
4. Probe / SAE / head / vector / patching 先行。
5. “encoded ≠ used” 这种 generic slogan，没有独立行为 puzzle。
6. Architecture micro-puzzle：很 elegant，但答案不影响更大理解。
7. Cross-domain terminology transfer。
8. 新模型 / 新语言 / 新 benchmark 重新测老问题。
9. Benchmark / robustness / metric / evaluator 主导。
10. 大 synthetic dataset 只为了获得 ground truth。
11. 只看 reasoning / RL / agents，因为论文最多最好搜。
12. 复杂语言学细节，需要半页才能解释 why care。
13. 只用 strong papers 当 kill database。
14. 为了躲 prior 把自然问题拆成越来越窄的小格子。
15. 为了救一个题不断加 training arms / controls，最后实验比 mother question 复杂得多。

---

# 10. Zhao / Cho-style mechanistic interpretability 规范

Mechanism 是回答问题的工具，不是问题来源。

正确顺序：

> natural puzzle / behavioral or learning law
> → representation structure
> → transformation / computation
> → implementing component / pathway
> → causal intervention
> → optional controllability

不是每篇都必须做到所有层级。

最重要的是：

- representation 不是终点；
- decodability 不是 causality；
- component localization 只有在 higher-level computation 清楚后才有意义；
- 不要从 neuron/head/vector 开始，再反向发明 mother question；
- 如果一个行为 law 已经 Main-sized，机制可以后置，不要硬加。

从 Zhao/Cho 真正要学的是：

> 在拥挤领域中改变 explanatory decomposition，而不是换 interpretability tool。

---

# 11. Experiment-grounding：题目必须落到真实实验对象

在 candidate 进入深审后，立即回答：

1. 数据从哪里来？
2. scientific variable 真正是什么？
3. manipulation / observation 是不是直接作用在这个 variable 上？
4. 主 figure 会长什么样？
5. 删除 benchmark / metric / method 名以后，结果还剩什么？
6. 论文的语法主语是 model / learning / computation / representation / behavior / process，还是 dataset / benchmark / method？
7. 需要多少人工构造？
8. pilot 是否能在合理 GPU 时间内给 go/no-go？

允许：

- small controlled micro-world；
- synthetic aliases；
- factorial stimuli；
- minimal intervention；

前提是它们是 identification instruments。

不允许：

- 造一个大 synthetic benchmark，然后论文变成 leaderboard；
- 大规模 annotation 才能知道 ground truth；
- 主结果只是 method × dataset × perturbation × score。


## 11.1 Data Path Gate

数据路径本身是选题生死条件，不是后续工程细节。

优先级：

1. **现成公开数据 + 原生 ground truth**；
2. **小规模程序化 controlled stimuli，答案可解析计算**；
3. **少量自动生成 + 人工 spot-check**；
4. **需要大量人工标注 / LLM judge / 专门造 benchmark** —— 强烈负面，通常 KILL。

在 PILOT-AUTHORIZED 前必须回答：

- 核心实验是否能在 **不超过几百个 controlled items** 或一个现成公开数据集上判生死？
- ground truth 是否可以直接从构造规则/原数据得到，而不是靠另一个 LLM judge？
- synthetic data 是不是只负责 identification，而不是现象本身？
- 如果删掉 synthetic generator，是否有自然数据/已有文献说明同一 scientific pressure 确实存在？
- 是否需要人工标注 hidden state、reasoning quality、semantic faithfulness 等难标变量？如果需要，优先 KILL 或换设计。
- 数据构造是否偷偷把 hypothesis 写进模板里，例如只有某一 condition 出现特定 lexical cue？
- 如果 pilot 成功，是否能用一个现成自然数据集做最小 ecological validation，而不是再造第二个大数据集？

硬规则：

> **如果为了让现象可测，必须造一个越来越复杂的数据生成器，那么很可能 generator 已经成为真正的 contribution。此时应优先 KILL，而不是把它包装成 scientific instrument。**

用户偏好下尤其避免：

- 大规模人工 annotation；
- judge-model 作为主要 ground truth；
- benchmark construction；
- 需要大量领域知识的数据清洗；
- 只有一个 synthetic micro-world 能成立、离开该 world 就无法表达的 claim。

允许的小 synthetic instrument 必须满足：

> 程序化、便宜、可审计、答案解析可得、surface 可随机化、规模小、并且不作为论文卖点。

---

# 11.5 Training-dynamics recipe gate

S03 的真实执行经验增加一条硬门槛：

> **不要把一个 arbitrary training point 当成 learning law。**

但 recipe dependence 本身不是自动 kill。AI/NLP 论文不要求对所有 optimizer、LR、budget、model family 都给出 theorem-like invariance。真正要防的是：

> competing-world 的**定性结论**只能靠挑某个训练点成立，而稍微改变一个合理 recipe 就可能反转。

对任何 learning / post-training / memorization / acquisition 题，在 PILOT-AUTHORIZED 前判断：

1. decisive comparison 能否尽量放在同一个 model / optimizer state 内，或至少用 mirrored / counterbalanced history 减少不可比性？
2. recipe 是 nuisance/control，还是 mother question 本身就在做 industrial recipe archaeology？
3. 是否可以用 **1 个主 recipe + 1 个便宜确认条件**（第二 training dose / adaptive optimizer / seed block）检查 qualitative conclusion，而不是一开始跑大矩阵？
4. 如果确认条件只改变 effect size，题通常仍可保留；如果 A/B/C world assignment 直接翻转，则优先 KILL。
5. 为了让故事成立，是否必须扩张成 optimizer × LR × dose × model-family sweep？如果是，KILL。

真实 lesson：

- **S03:** 最终 KILL。真实 pilot 已证明 single-budget / single-family developmental reading 极易制造假 law，且 budget/family 改变了 qualitative story。不要靠继续加 recipe 救。
- **S05:** 允许做，因为 response relevance 可以在同一 SFT run 中 matched intervention；但若 persistent trace 只在明显 overfitting 后出现，立即 KILL。
- **S09:** 最终 KILL。核心变量 memory age / learning history 本身就是 optimizer path 的复合产物；即使 mirrored history + same-final-checkpoint update 能改善 within-recipe control，也不能避免 positive result 立即要求大 recipe matrix。

优先保留：

> 同一训练状态内的 causal intervention、matched within-run contrast、或经过小规模 robustness check 仍保持 qualitative conclusion 的 learning law。

优先淘汰：

> industrial recipe biography、只能靠单个 checkpoint/budget 讲故事、或必须大规模 recipe matrix 才知道结论方向的题。

---

# 12. Training / post-training 题的 scale discipline

小模型、toy data 可以用于 pilot。

但如果最终 scientific claim 是关于真实 LLM training dynamics：

> 不能只凭一个极小 toy regime 就宣布 universal law。

在升成完整 project 前至少要问：

- effect 是否在更 realistic 的 model/data/step regime 仍然存在？
- toy world 的关键 causal structure 是否对应真实训练过程？
- 是否存在 scale reversal？
- claim 是否应该收窄为该 regime 下的 law？

不要一开始做 model zoo。
先用最便宜 pilot 判生死，再做最少量 scale validation。

---

# 13. 从头到尾的标准工作流

## Phase 0 — Restore

读 repo 正式状态、selected registrations、failed ledger、re-audit、最新 commits。

目的：

- 不重复做已经杀过的题；
- 不把旧临时状态当当前状态；
- 不把 selected 当 taste exemplar。

## Phase 1 — Fresh taste calibration

每轮重新读：

- Sasano 真实 feedback；
- 3–6 篇近年强论文；
- 至少 2–3 个不同 lineage；
- 必要时加入 CV / generation / cognition / stats / control 等来源。

对至少两篇做：

> Seed → Pressure → Competing worlds → Decisive experiment → Why Main。

## Phase 2 — Pressure mining

先记录 scientific pressures，不起标题。

例如：

- 两篇可信论文结论互相顶；
- 两个 quantity 被默认等同；
- 一个 operation 每天都用但 learning semantics 不清楚；
- 旧解释依赖的 premise 已改变；
- 一个 behavior 可以由不同算法完成；
- 一个 global label 遮蔽 local causal structure；
- 一个 hidden decision 一直由 oracle 提供。

## Phase 3 — Seed formation

把 pressure 升级成一句自然 mother question。

此时必须能写：

- why care；
- A / B / C worlds；
- 哪个 observable/intervention 会让 worlds 给出不同 prediction。

如果只能写：

> effect 大 / effect 小 / 没 effect

还不是好 competing worlds。

## Phase 4 — Lock one seed

不要 dump 十几个半成品。

一旦一个 seed 看起来有潜力：

> 锁住它，审到明确 YES / NO，再换题。

这会显著减少漂亮标题堆积和浅搜。

## Phase 5 — Nearest-prior deep audit

至少读最危险 prior 的：

- abstract
- introduction
- related work
- actual claim
- core experiment / intervention

问：

1. reviewer 会把我们压成什么 parent？
2. prior 真正回答的 decisive unknown 是什么？
3. 它是否已经区分我们的 A/B/C？
4. 我们新增的是新 knowledge sentence，还是只换 setting？
5. 如果有 overlap，为什么 changed question 仍值得知道？
6. remove-trigger-paper：删掉启发我们的那篇 paper，这个问题是否仍从其他 pressure 自然产生？

Future work 不是自动 kill。
只有当我们本质上只是在执行作者已经定义好的下一个 cell，且没有独立 pressure，才算弱 follow-up。

## Phase 6 — Identification audit

只控制 load-bearing confounds。

要求：

- major worlds 有不同 prediction；
- intervention 和 scientific quantity 的联系清楚；
- 不靠 post-hoc grouping / cherry picking；
- 不把 outcome 变量和 treatment 混在一起；
- 不为了完美 identification 让实验爆炸。

如果核心 confound 只能靠一个极其不自然的大 factorial 消除：

> 直接考虑 KILL。

## Phase 7 — Experiment / data audit

确认：

- 数据现实；
- pilot 便宜；
- ground truth 可得；
- 主结果不是 evaluation table；
- synthetic 部分是 instrument，不是贡献主体。

## Phase 8 — Main story audit

用普通 reviewer 语言回答：

> 为什么现在需要知道这个？
> prior 已经知道什么？
> 我们到底新增哪一句 knowledge？
> A/B/C 任一结果为什么都重要？
> 一篇 Main 的宽度从哪里来？

Main-size 来自 explanatory reach，不来自：

- 模型数量；
- benchmark 数；
- ablation 数；
- 图表数量。

## Phase 9 — Binary decision

对于一个已经锁定并完成 deep audit 的 seed，只允许：

### PILOT-AUTHORIZED

必须同时满足：

- mother question natural + important；
- reviewer-level novelty 清楚；
- same decisive unknown 未被 prior 做掉；
- A/B/C worlds 有科学差异；
- minimum experiment 能直接区分主要 worlds；
- 无 load-bearing identifiability blocker；
- 数据/算力现实；
- 非 evaluation-centric；
- opposite/null result 仍有 knowledge gain；
- novelty sentence 一两句可说清。

### KILL

任一情况成立即可：

- same decisive unknown 已被 direct owner 回答；
- honest mother question 太窄；
- novelty 只靠 setting / terminology / model；
- experiment 无法识别；
- 数据路径不现实；
- story 最终是 evaluation；
- 只有预期方向成立才有论文；
- 为救题需要实验爆炸；
- reviewer compression 后就是成熟 parent 的一个普通 cell。

不再把“SERIOUS”作为需要交给用户或长期留在 repo 的结果状态。

内部搜索过程中当然可以暂时觉得某个 seed serious，但：

> 一旦锁定审题，本轮必须继续审到 PILOT-AUTHORIZED 或 KILL。

不要半途把未完成候选扔给用户让用户自己判断做不做。

## Phase 10 — Register or log

如果 PILOT-AUTHORIZED：

- 新建 Sxx registration；
- 更新 SELECTED_TOPICS.md；
- 更新 README.md；
- 更新 NEXT_ROUND_PROMPT_ZH.md；
- 冻结 parent question / novelty sentence / pilot / kill conditions。

如果 KILL：

- 写入 FAILED_TOPICS ledger；
- 记录真正 kill reason；
- 记录 covering paper / growth lesson；
- 禁止之后只换标题复活。

---

# 14. Binary decision 输出格式

每个完成审计的 candidate，用户最终只应收到两种结果。

## 如果升

必须给：

- Mother question
- Scientific pressure
- Competing worlds
- Nearest prior
- Reviewer compression
- Knowledge delta / novelty sentence
- Identification logic
- Minimum pilot
- Outcome A/B/C 各自意义
- Main-size 原因
- Kill conditions after pilot
- 若机制题：Zhao-style mechanism path

然后明确：

> PILOT-AUTHORIZED / registered as Sxx

## 如果杀

必须给：

- Mother question
- 最危险 nearest prior
- 为什么 same unknown 已被做掉，或哪一个非-novelty blocker 致命
- 为什么不值得继续加 controls 救
- 从 covering paper 学到的 question-growth lesson

然后明确：

> KILL

允许：

> 这一轮 0 survivor。

---

# 15. Search drift reset

不要机械规定“必须每 N 个题 reset”，但以下情况出现时立即重校准：

- 连续多个 seed 因同一种原因死；
- 连续候选都来自同一 literature；
- 最近的问题越来越难一句话解释；
- novelty 越来越靠 exact cell；
- mechanism 越来越复杂、mother question 越来越薄；
- synthetic / benchmark / robustness 越来越多；
- RL / agent / reasoning 因为好搜而占满搜索；
- strong papers 只被用来杀题；
- 为了 prior overlap 不断把问题切细；
- 为了保住候选不断膨胀实验。

Reset 时：

1. 停止当前 generator。
2. 换至少 2–3 个 lineage。
3. 重新读 Sasano feedback。
4. 重新做强 paper autopsy。
5. 写一句：

> 当前 generator 为什么漂了？下一批 scientific pressure 去哪里找？

---

# 16. 从历史流程中已经确认的失败模式

这些是 process lessons，不是 topic list。

## 16.1 过早 brainstorm 大量标题

问题：

- 题名看起来漂亮；
- nearest prior 很浅；
- agent 容易爱上自己的 framing。

修正：

> pressure first，lock one seed，deep audit to YES/NO。

## 16.2 Parent overlap 秒杀

问题：

- AI Main 正常 overlap 被误当成 novelty failure；
- 好问题被越切越窄。

修正：

> same decisive unknown audit，而不是 same keywords / same parent audit。

## 16.3 Novelty 宽容失控

反向错误：

- “允许 overlap”变成什么 follow-up 都能活。

修正：

> 必须有 load-bearing knowledge delta，而不是 paper A 的未做实验。

## 16.4 Mechanism-first

问题：

- head/vector/subspace 很容易做；
- mother question 后补，story 很薄。

修正：

> 先 law / puzzle，再 mechanism。

## 16.5 Cross-domain 名词搬运

问题：

- 看似新，其实 old question + new terminology。

修正：

> 迁移 identification logic / tension，不迁移标签。

## 16.6 Evaluation creep

问题：

- intro 很科学；
- 实际实验变成 synthetic data + metric table。

修正：

> 早做 experiment-object audit。

## 16.7 Elegant but unidentifiable

问题：

- question 很漂亮；
- treatment 同时改变两个 load-bearing factors；
- 最终只能讲相关性。

修正：

> 最小 intervention 必须让主要 worlds 真正分叉；否则 kill。

## 16.8 Experiment explosion

问题：

- 为救一个混淆不断加 arm；
- 研究问题越来越弱，harness 越来越复杂。

修正：

> small decisive experiment 是 viability 的一部分，不只是成本问题。

## 16.9 半成品状态拖延

问题：

- 一直叫 SERIOUS；
- 用户不知道到底做不做。

修正：

> locked seed 必须 binary resolve。

---

# 17. 当前正式状态（2026-09-21）

当前 selected / PILOT-AUTHORIZED：

- S04 — How Do Language Models Update Situation Models Across Event Boundaries?
- S05 — When Does Reading Become Learning?
- S06 — What Does Deliberation Do to Evidence?
- S07 — Where Does Surprise Go?

最终 KILL：

- S03 — 真实 pilot 暴露 developmental story 随 budget / family / recipe 改变；
- S08 — shared-vs-separate metacognitive control 即使被干净识别，scientific consequence 仍偏弱；Broadening 会导致 experiment explosion；
- S09 — causal variable 本身是 optimization-history/path construct。

当前 surviving topics 必须继续遵守：

> **Scientific significance gate + Recipe Gate + Data Path Gate**

尤其新增一条 mechanistic significance lesson：

> **“A 和 B 是否共享内部机制？”不是天然重要的问题。必须先说明 shared 与 separate 两个世界分别会改变什么更大的科学理解；如果答案只是“内部架构不同”，通常不够。**

这些 selected topics：
- 不是正向 taste exemplar；
- 只代表当前值得真正投入第一刀 pilot；
- 一旦 pilot 触发各 registration 的 kill condition，应立即撤销，不因“已经 selected”而保留。
