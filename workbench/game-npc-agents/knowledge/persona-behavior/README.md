# 矿区 A：角色表达、行动意图与游戏内策略选择

**状态：CURRENT EXPLORATION，非已证实 IDEA**（2026-10-14 用户选择）。本目录只收精读、源码/数据审计与实际观察，不复制其它全域知识库。

## 研究目标
真正认识 Game NPC 中的 **Persona ↔ Intended Behavior ↔ Executed Strategic Action ↔ World Consequence**。不仅是比较两段不同语气。不同 NPC 的作者目标/任务利益、玩家关系、游戏状态不同；研究既允许发现显著断裂，也允许发现高质量上下文匹配或角色约束有效，并解释它们的边界。

## 当前入口
- [RELATED_WORK](RELATED_WORK.md)：最接近本矿区的6篇重要近邻，特别是已占位的 ICML2026/2026 的测量与叙事先验成果。
- [CODE_AUDIT](CODE_AUDIT.md)：PCSP、agent-sandbox、Generative Agents、Psychometric 两篇作者代码的已读事实；未跑不升级 P4。
- [实验卡 E06](../../experiments/E06-persona-strategy-baseline.md)：最小自然任务/真实 action gate，正负控制、决策标准。
- [当前执行说明](../../LOCAL_AGENT_START.md)：本地 Agent 接手与授权节点纪律。
- [领域全景](../DOMAIN_ATLAS.md)：A 是临时焦点，不得把工作台其它方向视为被关停。

## 三组需要被分清的变量
(1) **自述/语气**：角色语言是否体现设定；Big Five是粗粒度心理构念，未必预测某一选择。
(2) **目标与行动意图**：特定情景的许可行为、效用/义务与代价；TPB式 task-specific instrument 也可能更有意义。
(3) **可执行行动与后果**：如商人真正拒卖或低价交易、守卫真正保护/放行、队友真正分享稀缺资源；必须检查 game state change 和合理替代行动。
需要进一步分离世界叙事预设、具体行为词（anchor words）、玩家提示中的角色权威、故事原型、模型大小/服务模板、奖励中硬编码的偏好。

## 审计流程原则
先读作者真正做到的实验与强对照；优先通过可用原始数据的 re-analysis 或**原生游戏动作基线**验证测量。初步只有文本判别/同一玩法不足以支持广义“游戏NPC利益策略”主张；如缺数据，先调查而非马上生成。
严禁把模型“我是自私的”与行为被人类评分“不够自私”当作可自证的唯一 gold。机制推断须干预，先问提示/明确状态/动机提醒能否解释结果。
