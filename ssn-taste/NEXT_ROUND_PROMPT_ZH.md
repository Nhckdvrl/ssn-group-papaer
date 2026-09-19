# 下一轮科研选题搜索启动提示词

你现在接手 Nhckdvrl/ssn-group-papaer/ssn-taste 的下一轮科研选题搜索。

不要先总结这份提示词。先恢复 repo，然后直接开始工作。

完整长期规范见：

- ssn-taste/SEARCH_GUIDE_ZH.md

这份文件只保存当前 handoff 与启动动作。若与 repo 最新正式状态冲突，以 repo 为准。

---

# 0. 先恢复正式状态

开始前必须读取：

- ssn-taste/README.md
- ssn-taste/SEARCH_GUIDE_ZH.md
- ssn-taste/SELECTED_TOPICS.md
- S03–S09 全部 registration
- 全部 ssn-taste/FAILED_TOPICS*.md
- ssn-taste/RE_AUDIT_2026-09-18_NOVELTY_CALIBRATION.md
- 最近 commits / 新增文件

当前正式 selected / PILOT-AUTHORIZED = 7：

- S03 — From Document End to Task Done
- S04 — How Do Language Models Update Situation Models Across Event Boundaries?
- S06 — What Does Deliberation Do to Evidence?
- S07 — Where Does Surprise Go?
- S08 — Is Metacognitive Control Shared?

不要重新审 S03–S09 是否 selected，除非找到直接 covering prior 或 pilot 触发 registration 中的 kill condition。

2026-09-19 曾短暂错误地将 S05/S09 标为 KILL；该决定已在重新核对 prior 与 recipe robustness 后撤销。repo 最新 registration/SELECTED_TOPICS 为准。

非常重要：

> S03–S09 以及所有历史 killed Sxx 都不是正向 taste exemplar。

包括所有历史 S/L/F/Unring/selected/serious/failed topic，都只能用于 process evidence、dedup、防复活和资产复用。

当前没有需要继承的正式半成品 candidate。

---

# 1. 会议与 taste

优先：

- ACL Main
- EMNLP Main
- NAACL Main

持续用：

- TACL
- ICLR
- ICML
- NeurIPS

校准 scientific taste。

CVPR / ICCV / ECCV、image/video generation、multimodal、speech/audio、robotics、general ML、optimization、cognitive science/neuroscience、statistics、information theory、control、dynamical systems、statistical physics 都可以作为 idea provenance。

但跨领域只迁移：

> scientific pressure / conflict / competing explanations / identification logic / directed asymmetry / regime change / paper-growth pattern。

不要机械搬术语。

---

# 2. 正向 taste 来源

只用两类主要来源：

## A. Sasano 的真实判断

持续读 Slack / 学生课题反馈，特别关注：

- 什么让他觉得面白い；
- 哪些差异只是先行研究との差太小；
- 怎样重写 RQ；
- 怎样预判普通 reviewer；
- unexpected result 为什么也可以有 value；
- mechanism 什么时候必要、什么时候不必要；
- changed premise 什么时候真的让旧问题重新未知。

稳定原则：

> simple puzzle → clear scientific object → natural competing explanations → controlled discrimination。

但不要把它变成机械 checklist。

## B. 真实强论文

每轮读几篇不同 lineage 的 ACL/EMNLP/NAACL Main，以及 ICLR/ICML/NeurIPS/TACL。

做 paper autopsy：

1. mother question；
2. pre-existing scientific pressure；
3. competing worlds；
4. decisive experiment；
5. opposite result 是否仍有 value；
6. seed 怎样长成 Main story；
7. 与 nearest prior 重叠多少，为什么仍有 novelty。

Interpretability 特别学习 Zhao / Cho：

> representation → transformation/computation → component/pathway → causal intervention → optional controllability。

学的是 explanatory decomposition，不是 head/vector/circuit 模板。

---

# 3. 当前最重要的找题方式

不要 brainstorm 一堆标题。

先找：

> unresolved / conflicting / unclear scientific component。

重点搜：

- 多篇可信 paper 的结果不能被一个简单解释同时解释；
- 社区默认相同的两个 quantity 其实可能不同；
- A→B 与 B↛A 的 directed asymmetry；
- changed premise 让旧解释失效；
- endpoint 已知但 formation dynamics 存在独立 puzzle；
- 同样 behavior 可能由不同 computation 完成；
- constraint / flexibility 改变 learned algorithm；
- mature workflow 中隐藏的 oracle / intermediate decision；
- 旧科学争论因为新 intervention 第一次变得可识别。

然后才升级成：

> 一个 natural mother question + A/B/C possible worlds + decisive experiment。

不要靠纯推理凭空发明 anomaly。大量读相关论文，尤其找 open、冲突、悬而未决、不清楚的组件。

---

# 4. Novelty 标准

AI/NLP Main 不要求零 overlap，也不要求数学意义上的绝对严谨。

不要因为 broad parent 有 prior 就 kill。

真正问：

> nearest prior 是否已经回答同一个 decisive unknown，并区分了我们同一组 competing worlds？

正常 overlap 完全允许。

但以下仍然 kill：

- same decisive unknown 已被 direct owner 回答；
- reviewer 可以用已有 paper 的核心 finding 原封不动描述我们的贡献；
- 新模型 / 新数据 / 新语言 / 新 modality；
- cleaner replication；
- paper A × paper B 的交集；
- cross-domain 换名词；
- 为躲 prior 把自然问题切成 tiny exact cell；
- honest mother question 太窄；
- experiment 无法识别；
- 论文实际变成 benchmark/evaluation。

必须能写：

> Prior 知道 X；Y 仍未知，因为 Z；我们的 experiment 区分 A/B/C。

Future work 本身不是自动 kill。
如果问题还有多条独立 scientific pressure，可以成立。
如果只是照着作者“下一步做这个”执行一个 cell，通常不够。

---

# 5. 用户偏好 / 禁区

优先：

- mechanistic interpretability / LLM science
- learning / post-training
- reasoning / inference
- architecture / inductive bias
- generation
- understanding
- training dynamics
- simple but fundamental questions

不喜欢：

- benchmark
- dataset
- RAG
- evaluator / metric
- data-centric
- model-zoo
- complicated linguistics
- 大量人工造数据
- 热点套热点
- RL/agent/RLVR 追潮流
- “新模型再测一次”
- behavior 已知后机械接 mechanism

small controlled synthetic micro-world 可以作为 identification instrument，但不能成为 benchmark 主体。

---

# 6. Mechanism discipline

不要 mechanism-first。

错误：

> 先找一个 probe / SAE / head / vector / circuit，再找故事。

正确：

> mother question 先成立。
> behavior / learning law 先明确。
> mechanism 只在它能解释这个 law 时进入。

如果做 mechanism，按 Zhao/Cho 方向：

> representation structure
> → transformation / computation
> → component / pathway
> → causal intervention。

不是每一层都必须做。
probe/decodability 本身不是结论。

---

# 7. Experiment-grounding

锁定 seed 后马上问：

- 数据从哪里来？
- 操纵的 scientific quantity 是什么？
- 主结果是什么形状？
- 删除 benchmark/method/metric 名称后还学到什么？
- main figure 是 causal law / learning curve / dissociation，还是 score table？
- ground truth 是否现实？
- pilot 是否便宜？

禁止 actual work 退化成：

> method × dataset × perturbation × score。

训练题可以先用小模型/toy pilot 判生死，但完整 claim 必须考虑 realistic scale validity；不要从 toy 直接宣称 universal LLM law，也不要一开始跑 model zoo。

---

## 7.5 Training-dynamics recipe gate

S03 的执行失败与 S05/S09 re-audit 增加一条硬门槛：

> **不要只问 training-dynamics 问题是否可控；先问它是否有理由存在一个 recipe-stable answer。**

对任何 learning / post-training / memorization / acquisition 题，在 PILOT-AUTHORIZED 前必须判断：

- manipulated scientific quantity 是否能在同一个 model/optimizer state 内直接 intervention；
- recipe 是 nuisance/control，还是它本身定义了现象；
- 合理改变 training dose / LR / optimizer 是否可能让 A/B/C world 判定直接换号；
- 如果结果只在一个 arbitrary optimization point 成立，是否仍是重要 scientific fact；
- 为了证明不是 recipe artifact，是否会被迫扩张成 optimizer × LR × dose × model zoo。

若最后一项答案是“会”，优先 KILL。

S03 的负面 lesson：single-budget / single-family training conclusions 极易制造假 law；parameter-locus 或 structural facts 往往比 developmental biography 更稳定。

S05/S09 已重新审计并保留；recipe gate 用于设计便宜的 robustness check，而不是因存在 optimizer/dose interaction 就自动 kill。

# 8. 工作纪律：一次只审一个强 seed

不要 dump 10–30 个半成品。

流程：

1. 广搜 scientific pressure。
2. 找到一个最强 seed。
3. 锁定。
4. nearest-prior deep audit。
5. identification audit。
6. experiment/data audit。
7. Main-story audit。
8. 继续审到明确 YES / NO。

用户不需要“SERIOUS / 也许可以”这种半成品答案。

对于一个已锁定的 seed，本轮最终只允许：

## PILOT-AUTHORIZED

或

## KILL

内部当然可以暂时觉得某个 seed 有潜力，但不要把 unresolved SERIOUS 长期留给用户或 repo。

允许 0 survivor。

---

# 9. PILOT-AUTHORIZED 门槛

必须同时满足：

- natural + important mother question；
- independent scientific pressure；
- reviewer-level novelty 清楚；
- same decisive unknown 没被 prior 做掉；
- 至少 2–3 个 qualitatively different worlds；
- minimum experiment 能区分主要 worlds；
- 无 load-bearing identifiability blocker；
- 数据 / 算力现实；
- 非 benchmark/evaluation-centric；
- opposite/null outcome 仍有 knowledge gain；
- novelty sentence 一两句讲清；
- Main width 来自 explanatory reach，而非实验数量。

如果为了救题需要不断加 arms / controls，实验复杂度远大于问题本身：

> KILL。

---

# 10. KILL 时不要浪费失败

每个 kill 要记录：

- mother question；
- nearest covering prior；
- 真正 kill reason；
- 是 same-unknown、identifiability、width、data、evaluation 还是 experiment explosion；
- covering paper 教会了什么 question-growth lesson。

不要只写“有人做过”。

FAILED ledger 的目的不是建墓地，而是防止下一轮：

> 换标题 → 重新走同一条死路。

---

# 11. Drift reset

一旦出现以下迹象，停止当前 generator：

- 连续多个 seed 同一种死法；
- 连续题都来自 reasoning/RL/agent 等单一热点；
- question 越来越难一句话解释；
- novelty 越来越靠 exact gap；
- mechanism 越来越复杂而 mother question 越来越薄；
- benchmark/synthetic/robustness 比重上升；
- strong papers 只用于 kill；
- 为保候选不断实验膨胀。

Reset：

- 换 lineage；
- 重新读 Sasano；
- 重新读普通强 Main；
- 重新找 scientific pressure，而不是降低标准。

---

# 12. 下一轮立即执行

当前没有 active seed 要继承。

所以：

1. 恢复 repo。
2. fresh calibration。
3. 从多个 lineage 广泛寻找 open/conflict/unclear components。
4. 优先 understanding / training / generation / reasoning / architecture / interpretability，但不要固定 quota。
5. 一旦出现最强 seed，停止 idea dumping，锁住深审。
6. 最终只给 PILOT-AUTHORIZED 或 KILL。
7. 若 PILOT-AUTHORIZED，使用下一个未占用编号注册；若没有，明确 0 survivor。

最终目标：

> 找到一个在知道答案以前就值得问的问题；无论主要结果落在哪个 plausible world，都真正改变我们对语言模型学习、理解、生成、推理或内部计算的认识。

不要为了 S10 降标准。
