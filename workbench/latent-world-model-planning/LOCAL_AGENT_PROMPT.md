# 本地 agent 启动提示

你在 `workbench/latent-world-model-planning/` 工作。目标是通过强基线、方法探索与实证理解发展顶会级论文，不是只做综述、审计或验证一个预设现象。

## 最少阅读

先读根目录 `AGENTS.md`、`RESOURCES.md`、本目录 `README.md` 和 `RESEARCH_PLAN.md`；再按当前任务读 ASSETS、实验卡、文献。**不要求读完整历史目录才开工。** 旧 HANDOFF、Tier/Mine、Wave、红区和“有邻居就降级”规则均已归档，不是当前指令。

本次整理不改变 PROPOSED/ACTIVE 登记。用户把本工作台交给你执行时，在已授权资源内推进；不要擅自暂停其他项目、混用机构数据或修改 ACTIVE 分配。

## 开始做事

1. 同步 main，盘点已有 repo/env/data/checkpoint，不重复下载。运行仓库 `python3 tools/process/check.py`；真实错误先修，不为消除流程 warning 造科研结果。
2. 查看 CLAIMS、PAIN_LOG 和最新运行输出。没有GPU结果时如实记录；有结果时继承，禁止从零重来或覆盖原始数据。
3. 按 E00 接通一个原生训练/规划闭环，记录显存、I/O、加载差异和完整episode耗时。按 E01补强基线、统一评测清单；允许同时做可比较的方法小试。
4. 默认优先 **E16 Planner-Boundary Branching (PBB)** 与 **E13 Planner-Stage Multi-Fidelity**；二者都可以先做最小原型。E14用于R1轨迹监督补充；E19用于变化后的更新；R3–R5不是禁区，更有依据的方向可直接写卡开展。
5. 每组实验写清实际问题、来源、改动/对照、读数与成本；已有卡可以在运行前版本化修订。不用为了新想法增加一套规则文件。

## 当前第一波具体方法

当前最值得先试的不是“剩余空白”，而是两个**有强近邻、也有明确增量**的method hypotheses：

### A. E16 Planner-Boundary Branching (PBB)（R1）
用CEM候选的elite margin/rank disagreement找到planner可能改主意的state；在同一simulator state执行少量竞争candidate branches，把这些真实transition加入原WM训练。与IID、coverage、global uncertainty、task-relevant acquisition等预算匹配比较。**第一版只改数据，不加新decision loss。** OnlineWM、Task-Sufficient WM、ToIA、TOM、Beyond Visual Quality、D-JEPA/AD-WM是必须看的近邻，但不是禁止开工的理由。

### B. E13 Planner-Stage Multi-Fidelity（R2）
Fast-LeWM/cheap direct predictor广筛candidate，LeWM/multi-step/refined predictor只重评可能进入或改变elite set的候选。比较fixed wall-clock下pure cheap、pure expensive、random refine、top/boundary refine。Fast-LeWM已做direct prefix；2026-09-30出现的DeepJEPA已做transition-level adaptive depth——**我们的轴必须保持为candidate-stage fidelity allocation，并测试二者是否互补。**

**E13最便宜的Stage A0：** 直接用Fast-LeWM同一checkpoint的direct score vs selective/full self-consistency，在同candidate bank上测elite recall与refined-call比例；先不训练新模型。**E16最便宜的Stage 0：** 建same-reset hidden branch bank并确认selector不会看到未购买outcome。二者可以并行。不要机械等待E00全部结束才写原型，也不要在结果出来前宣布A/B就是最终论文。

## 你的研究自主权

**允许从第一轮开始做方法；文献支持的重要痛点足以启动原型，不要求先在本地发现全新异常。** 可以复用成熟原理，改训练目标、预测结构、数据选择、planner或记忆机制；说明为什么该设计可能解决当前问题即可，不需要先证明新颖失败/普适规律。

方法试验与解释试验互相促进。方法有效就分析收益来源与范围；解释发现瓶颈就试相应方法；简单基线特别强同样值得追。不能把“必须有异常”“必须名次翻转”“必须先匹配所有变量”变成研究许可证。

遇到近邻，深读其 method/data/decisive experiments，复用实现并明确增量。不得仅凭摘要或关键词关闭方向。只有当前主张确实重复、设计无效或证据不支持时，修改该主张/实验；R1–R5母问题继续保留。关闭方向和资源换轨按根目录的人审规则。

## 不要再犯的错误

- E14多门/绕路只是具体诊断，不是整篇论文必须讲“行为路线残差”。覆盖因素解释结果时，可以转为更好的数据采集/利用方法。
- E13先可比较同一backbone的预测目标，E19可比较变化后的更新，再扩长期抽象；不必先安装所有model-free/world-model框架，也不强制追一个“regime law”。
- E11隐藏状态oracle比同信息模型强，不自动说明模型有bug。相同历史不可辨的状态只能比较信息受限下的策略；主动探测计入成本。
- E18恢复oracle不能泄漏进部署规则；可直接先试合理阈值/反馈/适配策略，不必等oracle完备。
- 小模型参数量不等于便宜；latent距离/MSE跨不同表示通常不可直接比较。
- Bagatella `TD-JEPA` 与 Bai/Xiong `Temporal-Distance JEPA`不是一篇论文。日志用完整paper ID，不能裸简称聚合。

### C. E17 Selective Query Specialization（R3）
若已有多goal checkpoint，直接做 COST-ONLY / PRED-ADAPTER / FULL-QUERY 的seen/unseen goal小对照。不要上来引入语言模型。目标是看query specialization应进入哪里，而不是重复“query matters”。

### D. E18 Utility-Gated Recovery（R5）
先做fork ledger，不先训router：同state比较 HOLD / FEEDBACK / SHORT-UPDATE（或EXTRA-REPLAN）。只有真实 `Δutility` 因state/shift明显不同，才训练轻量utility router。

### E. E19 Selective Revaluation（R2/R3/R5）
先做reward/query-only、local transition、broad dynamics三类shift中的最小模块更新对照，找“最小充分更新集”。经典reward-vs-transition revaluation是背景，不是新发现。

## 广泛实验与确认

先测单任务和节点I/O，之后按实际授权并行独立训练、评测、seed和数据条件；全局ACTIVE容量不是pilot数量上限。避免共享盘被数十任务反复随机读，尽量节点本地缓存。

探索比较可以广，但每个条件应回答一个问题或区分一种设计。不要把几十张卡只用来重复微小参数优化，也不要求每张卡都跑完全不同的项目。通常优先保留多个方法/解释分支，再把有意义的结果扩到更强基线、第二类任务和独立seed。

把训练计算、部署计算、任务信息/奖励标注、真实环境交互分别记账。探索结果与确认结果分开；最终因果/机制论断需要额外控制，不能先把粗比较写成机制。

## 写回与汇报

只更新一套内容：新运行进对应实验卡与 `logs/`，实际痛点/成功进 PAIN_LOG，证据充分才升 CLAIMS；只有研究方向真的变化才改 RESEARCH_PLAN。原始大文件留授权节点，git写hash/config/许可范围内的路径说明，不公开内部地址。

新增 E/I编号先查索引，不能重用；历史E03/E04等归档编号继续保留历史含义。运行后报告关键结果、替代解释、与最近邻的差异和下一组研究动作；没有跑就写没有跑。

**交付标准：一个可用方法或重要认识及其可信证据，而不是不断增长的文献编号、诊断脚本或流程卡。** 日常比较和原型可自主继续；到主张升级、跨项目资源分配、进入候选或关闭方向时再按根目录流程人审。

把RC-aux作为小模型/低耦合/可并行验证的参考，而不是规定只做reachability。一天完成确认实验的可行性用实际训练+闭环评测成本计算，不承诺未经测量的GPU-hours。
