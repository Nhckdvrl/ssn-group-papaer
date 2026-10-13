# E05：游戏 NPC 行为学习基线与评价构念准入（2026-10-13）

- **状态：** VOID / superseded（2026-10-14 用户要求取消此旧“共享NPC行为训练”入口的执行优先级；从未运行，非实验证伪）。
- **类型：** REPRO / MEASUREMENT 建设；不预设新方法或论文想要看到的失败。
- **对应：** Trainable, Designer-Controllable Game NPCs territory；D1–D4。无新的 C##、P##，旧 E03/E04 已撤主优先级。
- **问题：** 能否在开放的真实 NPC 行为任务中，在可负担的本地训练成本下，复现已发表系统的行动、角色行为和任务表现，并验证哪些行为评价能反映可执行后果而非内部训练指标？
- **来源与执行前检查：** 首查 PCSP research/Mini-Inzoi v3 数据、license、模型/pretrained checkpoint、scripts/run_pcsp_v3.py、独立 action behavior evaluation；查 ccb/agent-sandbox LLM高层原生NPC回合与动作合法性作为**可选补充，不称其顶会 baseline**。完整上游 git SHA + 数据/模型哈希和测试环境，在 GPU 前冻结；不从零做 Unreal 大项目。
- **读数：** 任务回报/失败、NPC真实 action/state、行动分布与状态条件差异、内部对齐与独立行为 evaluator 的差异、不同角色/情境/伙伴、训练样本/设计成本、端到端 CPU steps/s、GPUh、p50/p95 latency、模型参数与VRAM。报告最强预先定义的行为真值及其适用边界；不能仅用 kNN persona retrieval 或 LLM自评代替玩家可见行为。
- **对照：** 作者完整 policy 与核心消融（尤其 no-consistency）、简单 rule/BT、基本单-policy PPO、预算匹配条件化 PPO；其它 BC/偏好/LLM controller 只有天然可用的示范/真实标签与性能门槛过了再决定。每个对照的实际训练数据/teacher成本等额计入。
- **阳性对照：** 环境 reset/step 与合法/非法 action；至少一套脚本/可复算NPC状态行为能达到任务正效应；评价器能在强制区分的两种实际行为策略上检测差异，且不会将同等成功/合理差异机械罚分。
- **噪声地板 + MIE：** 尚未测。先用环境重复、政策不同 seed、动作策略等价/不同的人工构造**仅作测量正负对照**；正式统计规模按自然环境与效果方差确定，不拿两个 toy scene 发表。
- **混杂审计：** style shaping 本身对 reward 的直接影响、训练内部 probe vs 独立行为 probe、参考人格词汇泄漏、训练/测试角色分拆、观察特权、不同策略训练样本量、GPU/CPU瓶颈、model API/teacher额外成本、角色/世界/玩家权威分离。
- **决策表：** 基线可复现但独立行为指标和内部对齐矛盾→核查行为真值/指标效度/数据来源，然后决定是否存在更广泛控制学习问题；强基线原设定很好但跨合法环境/不同设计条件失败→定位训练条件和行为规格，再选择最少关键试验；所有行为很稳定→不要造难题，寻找其它公认重要NPC压力；开放系统不是游戏 NPC 或缺行动因果→不继续用它冒充核心 substrate，转有可执行行为的另一开放游戏；先决基本能力/CPU IO无法通过→修环境或按资源换底座而非宣称方法失效。
- **GPU 预算：** 0 付费 API；未测速不填 GPUh；优先 CPU engine+少量单卡 PPO/推理 profile，再判断扩 n/seed，跨节点独立实验而非DDP。**实际 GPUh = 0，本轮未运行。**

## 当前结果
无。已知 PCSP 作者自己报告独立 probe 不支持 InfoNCE 对外部行为的显著优势，这是**源论文/代码公开结果，不是我们复现**。E05 是接下来进行实际驻留的运行前计划。


## 2026-10-14 后续决策
该卡是此前用户授权下的具体运行前草案；用户现在明确否决其作为整个 Game NPC workbench 的默认主线。本实验**没有被执行**，不含真实GPU/模型结果，故归档为 VOID/superseded 而不是负结果。保留原问题、设计、决策表作为过程资产；下一研究入口在 [knowledge/DOMAIN_ATLAS](../knowledge/DOMAIN_ATLAS.md) 与 [EXPLORATION_ENTRY](../EXPLORATION_ENTRY.md)。
