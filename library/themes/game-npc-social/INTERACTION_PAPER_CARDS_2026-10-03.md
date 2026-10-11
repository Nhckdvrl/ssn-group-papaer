# 交互与伙伴适应：定向精读卡（2026-10-03）

本轮推进 **territory 搜索**，无实验、无新主张升级。精读来源为论文正文、方法、实验、局限与关键附录；未把自动摘要当全文。`DOCUMENTED` 指论文明确写出的动机，`RECONSTRUCTED` 指我们的研究路径重建，后者不当作者传记。主会状态回原始会议页面核对；Findings / EACL 不进入校准。

## 1. Collab-Overcooked — EMNLP 2025 main

- 原文：[正式论文](https://aclanthology.org/2025.emnlp-main.249/)、[全文 PDF](https://aclanthology.org/2025.emnlp-main.249.pdf)；[代码](https://github.com/YusaeMeow/Collab-Overcooked)。另读 [arXiv v2 全文](https://arxiv.org/html/2502.20073v2)：该版 **11 模型**，正式版 **13 模型**；不得混用版本数字。正式主文前半与 arXiv 全文/附录读完，正式版新增两模型主表未逐格复核。
- **形态：** 可执行 benchmark + 过程测量 + 失败分析。
- **旧压力 / 改前提：** 旧协作环境中，单个 agent 有时足以完成任务；最终成功率不能说明协作发生在哪。作者用资源隔离、非对称任务知识使双方确实需要互相依赖。
- **idea 来源（DOCUMENTED）：** Introduction 与 Table 1 明确列“缺乏协作必要性、仅端到端指标、缺细粒度诊断”三个问题。**RECONSTRUCTED：** 先把“合作”变成环境不可绕开的依赖，再在可枚举成功轨迹上设计读数，而非先发明一个多 agent 框架。
- **最近邻距离：** Overcooked-AI / ProAgent 提供游戏与 agent 接口；CuisineWorld / VillagerBench 主要终局得分；RocoBench 已有协作但任务少。这里的实质变化是协作依赖和轨迹读数，不只是换厨房皮肤。
- **方法与证据：** 30 任务、6 档复杂度、两角色；TES 对齐参考行动轨迹并惩罚冗余，ITES 测单步进展，分启动协作 IC 与响应 RC。v2 每任务 10 次，Qwen2.5 7/14/32/72B、Llama3.1 8/70B 等；另有人类上限与注意力干预。注意力解释不是我们已经复现的事实。
- **读者应注意：** TES 依赖参考轨迹覆盖度；有效但不同的策略是否被罚，需要独立审计。任务层级、行动长度、上下文负担同时变化，不能直接把难度效应归为“协作本质能力”。小模型原文已有低档失败，不应只选 7B 后宣布协作不存在。
- **可迁移动作：** 用环境控制建立必要的依赖；把失败定位为请求、回应、行动三个接口；成功轨迹和简单 oracle 都是测量阳性对照。
- **本地可行性：** README 明确 vLLM；`src/main.py` 实际有 `--local_server_api`（默认 localhost:8000/v1）、`--model_dirname` 与开源模型分支。Python 3.8 / MPI 旧依赖需要适配，**已核查代码接口，尚未安装或运行**。客观动作/终局指标无须 LLM judge。

## 2. LVLMs and Humans Ground Differently in Referential Communication — ACL 2026 main

- 原文：[会议页](https://aclanthology.org/2026.acl-long.410/)、[v3 全文](https://arxiv.org/html/2601.19792v3)、[代码/语料](https://github.com/peterzeng/lvlms-referential-game)。精读 §2–7 与局限、后续控制；最终 ACL PDF 是 27 页，未逐字比对 arXiv v3 与最终版。
- **形态：** 成熟心理语言学构念 + 有行动结果的受控人机实验。
- **旧压力 / 改前提：** 既有 reference game 常让 speaker 一次描述、listener 一次选图。双方不能真澄清/修复，测到的可能是离线解码。本文开放多轮对话并交叉 director/matcher 角色。
- **idea 来源（DOCUMENTED）：** Clark–Wilkes-Gibbs、Brennan–Clark 的共同知识/概念契约研究；PhotoBook、Hawkins、Hua 的反复指称研究。**RECONSTRUCTED：** 保留旧任务的可测性，补上原评测删掉的互动与角色，观察双方共同完成的过程。
- **最近邻距离：** PhotoBook/AI-AI 工作偏语料或同类配对；Hua–Artzi 2024 有重复指称但缺自由多轮；RIFTS 从自然日志提 grounding acts，但没有共同可验证物理目标。本文的 2×2 人/AI 角色设计带来解释力。
- **证据：** 89 对 × 4 轮 = 356 对话（HH 32、HA 22、AH 17、AA 18）；每轮 12 篮子，matcher 另有 4 干扰项。主模型 GPT-5.2，后续 Gemini/Claude 和 reasoning、prompt、ordering controls。读数同时看正确率、字数/回合、词汇沿用，图报告 95% CI。
- **关键审计：** 高词汇重复可以来自机械复述，不能独立证明共同知识；原文承认 basket 顺序错误也促成掉分。主模型非本地；referring-expression 提取调用 GPT-5，虽有人校验 F1=0.86，仍非无 judge 管线。研究把互动成本和任务结果分开，优于只看“自然度”。
- **可迁移动作：** 交叉配对以区分谁在承担修复；共同状态保持与视觉识别分别做阳性对照；解释先排除顺序/接口混杂。不得只换 Qwen 再复述同一结论。
- **对我们：** 现成自然对话可先分析；local VLM 进入完整任务前须过单轮识别、顺序跟踪与短游戏门槛。低成本可用文本/已知对象 ID 作为控制，但最终视觉/人机主张不能仅靠该控制成立。

## 3. Success and Cost Elicit Convention Formation for Efficient Communication — ACL 2026 main

- 原文：[会议页](https://aclanthology.org/2026.acl-long.1946/)、[全文 v1](https://arxiv.org/html/2510.24023v1)、[代码](https://github.com/saujasv/learning-conventions)。精读 §1–5、Appendix A/C/E；方法数字按 v1 记录，会议版摘要的 improvement 数字有变化，不混写为精确复现目标。
- **形态：** 对旧测量痛点的小训练修复 + 人类行为验证。
- **旧压力 / 改前提：** 人会逐渐用更短、双方理解的称呼；模型在“说正确”上不错，却常持续啰嗦。不能把“指令要求短一点”与“学会对该伙伴形成惯例”视为同一件事。
- **idea 来源（DOCUMENTED）：** Grice/RSA 的沟通效用、Hawkins 的重复游戏、Hua–Artzi 的模型不适应观察、偏好优化。**RECONSTRUCTED：** 将 success 与 cost 拆开而不是堆 reward，取相同历史下最短且成功的 utterance 构造 pair，直接问两种压力分别教会什么。
- **最近邻距离：** Hawkins 在线改权重；Hua 2025 从人类剧本/指称链训练；本文以模拟游戏产生偏好，无须新增真人重复对话。不是首次模型惯例形成，也不是首次语言长度正则。
- **方法/证据：** Gemma-3-12B 为主、Pixtral 扩展；COCO 与 tangram。每游戏 4 图、20 trials、每次采 4 句；COCO 500 游戏、tangram 400；LoRA r=32、IPO 3 epoch、4 GPU。真人与模拟 listener、success-only / cost-only / combined 对照；完整真人游戏 126 COCO、120 tangram，另人类 speaker 基线。
- **值得学：** 同时看成功、消息长度、word novelty、真人响应时间，才支持“效率”与可理解性；cost-only 短不等于可用。主要结果并非只刷一项综合分。
- **局限/资产：** 整段历史都装得进上下文；一次一句的 reference-game 结构仍较简单。tangram 先做视觉 encoder 适配，不能误称完全没有人类描述数据。README 有模拟/训练配置，但本轮未确认公开 trained adapters；因此**可做本地基础测量，不把复现最终强 checkpoint 宣称为已解决**。
- **对我们：** 可借成熟任务与开源 12B 管线，以 frozen models 做建设，后续再决定小训练；“成功+成本训练出简短惯例”已有 claim owner，不能当新题。全文的“单次指称”“总历史可见”是边界，不是自动 paper idea。

## 4. Bayesian Partner Modelling enables Adaptive Replanning for LLM Coordination — arXiv 2026-08

- 原文：[全文](https://arxiv.org/html/2608.18490v1)、[状态页](https://arxiv.org/abs/2608.18490)。**主会接收未核实**，作为强预印本近邻；精读 §3–6 与实验控制，不据摘要猜方法。
- **形态：** 可定位的执行失败 + training-free belief/control 干预。
- **旧压力 / 改前提：** hierarchical agent 已看出队友换了活，自己仍把旧技能做完；简单频繁 replanning 又贵。论文不把伙伴 posterior 只塞进 prompt，而让它决定是否打断当前技能。
- **idea 来源（DOCUMENTED）：** ProAgent、Hypothetical Minds 与 Bayesian inverse planning；全文明确对比“posterior 当上下文”与“posterior 当控制信号”。**RECONSTRUCTED：** 从持续旧行动这个可见痛点反推决策调用时机，而非追求更精细的文字 ToM 推理。
- **距离：** 对 ProAgent 加 online belief/control；对 Hypothetical Minds 改成低成本技能 posterior；对 GAMMA/TALENTS 不声称全面超过 RL。belief–action gap、按矛盾选择性重规划已有 owner。
- **证据：** 3 layout、12 偏好伙伴分 3 组、每组每 layout 4 partner × 5 seed；GPT-4o/5.2；奖励、技能识别、互补技能、重复技能与 replanning 数。Open 的 gap 0.41→0.20 是原文报告；它不是我们新发现。Full / no-prompt / no-replan / no-belief 分解，以及 periodic、completion、LLM-trigger 对照较关键。
- **限制：** 有限手工技能、likelihood 以自身控制器近似队友；紧耦合 Forced Coordination 仍弱，RL 往往更强。某些互补技能标签由人定义，不能忽略。公开代码/可本地替换端点本轮未确认，不把它选为唯一 D1 入口。
- **对我们：** 伙伴适应可从公开策略池开始；应把 perception、partner inference、分工、动作触发拆清。仅换小模型重做 belief/action 二分，会被此文压缩。

## 5. Navigating Rifts in Human–LLM Grounding — ACL 2025 main（补充精读）

- [会议页](https://aclanthology.org/2025.acl-long.1016/)、[全文](https://arxiv.org/html/2503.13975v1)、[代码](https://github.com/microsoft/rifts)。精读 taxonomy、§4–6、limitations、forecaster/标注附录。
- **形态与来源：** 从 WildChat / Bing Chat / MultiWOZ 的实际修复负担出发，引入 grounding acts 分类，再用前向 forecaster 构造难例；不是先捏一个悖论。
- **证据：** RIFTS 1,740 任务；Llama3.1-8B forecaster macro AUROC 0.61（few-shot GPT-4o-mini 0.51）；分类器经 30 对话/108 条消息人工校验，macro F1 0.75。原文表中 Llama8B + GROUND 54.48±2.45 对 24.22±3.49；区间定义应按正式版核实后再用于复现。
- **最近邻/边界：** 延续其 NAACL2024 grounding-gap 工作，扩到行为预测与干预；Bing 与 MultiWOZ 任务分布不同，不能将观察比率直接解释为模型与人的能力因果差。RIFTS 经 forecaster 挑选且依赖 WildChat 模型，不代表所有真实交互。
- **可迁移动作：** 用自然数据先定义痛点，再在可执行任务验证后果。只比较澄清次数或做 prompt 恢复不能当能力证据；后续需要 task success 与可校验的 user burden。

## Paper rewind 记录：读出研究动作，尚不生成具体题目

遮住方法时，Collab-Overcooked 的合理第一步是检查任务能否单人完成、请求是否真改变伙伴动作、参考轨迹是否漏掉等价解；Success+Cost 的第一步是把成功率、长度、重复度、理解速度分别画出来；BayesBeliefAgent 的第一步是对齐“看见队友变化—改 belief—真正改行动”的时刻。三者共同说明：**可操作的压力来自系统怎样工作，而不是概念上可以怎样二分。** 以上是我们的研究动作重建，未运行其中任何测量。
