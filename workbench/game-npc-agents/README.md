# Game NPC Agents｜目标可以坚持，计划必须能改

**状态：PROPOSED；2026-10-13 用户要求完成选题准备并选定探索切口。已选择本工作台的探索优先级，不改变全局 ACTIVE 分配。**

## 已选定的探索切口

> **玩家改变游戏局势后，NPC 能否坚持自己的目标，同时放弃失效的手段，并在目标已经实现时停止旧行动？**

研究的是 **NPC 的目标承诺与计划适应是否真正分离**。不是人格提示/工具调用竞赛，不是再做一个通用记忆模块，也不是预先宣称存在“稳定性—灵活性权衡”。目前选定的是值得驻留的研究问题，不是已经验证的新发现或论文标题。

同一角色、同一动机、同一段实际经历，在游戏状态处建立配对分支：局势不变；玩家正常互动但不影响目标；旧路线失效而原目标仍可达；玩家已经实现该目标。看角色的真实后续行动，而非仅看它怎样解释自己。合法替代路径不罚，不把完成目标等同于照搬原示范。

## 当前唯一执行入口

| 文件 | 作用 |
|---|---|
| [EXPLORATION_ENTRY.md](EXPLORATION_ENTRY.md) | **选题决定、具体研究对象、竞争解释、什么结果值得继续** |
| [knowledge/GOAL_CONTROL_REVIEW.md](knowledge/GOAL_CONTROL_REVIEW.md) | LIGHT/Dragon、行为控制、goal drift、goal-directedness、重规划与新近顶会的研究谱系 |
| [knowledge/FRONTIER_CHECK.md](knowledge/FRONTIER_CHECK.md) | NeurIPS 2026 等定向补查；正文范围、track 与未获取来源明确分开 |
| [BASELINES.md](BASELINES.md) / [LOCAL_FIRST.md](LOCAL_FIRST.md) | 固定上游代码、自然数据来源、完整本地实验链与成本 |
| [experiments/E03-native-goal-entry.md](experiments/E03-native-goal-entry.md) | **PLANNED**：自然角色任务与最小强基线测量 |
| [experiments/E04-goal-plan-interventions.md](experiments/E04-goal-plan-interventions.md) | **PLANNED**：在真实线索基础上区分目标、状态和旧计划的作用 |
| [knowledge/README.md](knowledge/README.md) | 本工作台内部知识库；旧方向材料仍可追溯 |
| [logs/2026-10-13-selection.md](logs/2026-10-13-selection.md) | 本轮做了什么、未做什么及证据边界 |

## 为什么选这里

角色拥有自己的动机而不只是服从玩家，是 LIGHT/Dragon 的原生研究对象；设计者控制行为而不只最大化任务奖励，是 Direct Behavior Specification 的问题。游戏开发中的 GOAP、Ubisoft Teammates 和 KRAFTON 又都要求角色面对新局势作适当选择。学术与行业依据及边界见新综述，不用产品宣传证明模型效果。

**已有工作很多，不能冒领：** Goal Drift 已研究工具性目标切换与模式延续；Everitt 等已区分任务能力与目标导向；Arghal 等已研究无用钥匙与内部地图/计划；Bayesian Partner Modelling 已研究推断正确却继续旧技能；经典 GOAP 更早已分离目标和计划。因此“NPC 会忘目标”“加状态表”“有时应该重规划”不构成新贡献。

我们要从实际 NPC 交互中寻找能解释、预测这些不同失误的条件；若只复现上述认识，或简单强对照已覆盖全部现象，不包装为新 idea。

## 首选底座与边界

首选 **LIGHT 引擎 + 原有自然角色动机/任务**，不是从头造世界。代码固定为 `71a06cae8573048b1af41507ac52fe33b650fab3`。经典短任务保留本来的长度，局势变化用合法玩家事件实现。先研究目标含义和完成条件足够明确的自然任务；无法无歧义形式化的角色动机不硬打成错误标签。

E03 必须验证数据、目标、事件与当前引擎确实对齐。官方 demo 只用于运行测试，不替代自然评测；`projects/quests` 也不等于 Dragon 完整复现包。若资产恢复成本不合理，换支持同一科学问题的公开底座，而非改回 CPDC 或另开通用多智能体提分项目。

## 资源与实际进度

核心实验默认 **零付费推理 API**。NPC 为本地开放权重，世界与主要评分为引擎，玩家干预先用合法脚本事件；自然交互扩展才增加独立本地伙伴。教师、记忆、裁判都不得偷偷调用云端。多 GPU 用于独立场景、模型和确认种子，不跨节点同步训练。

**本轮完成：** 定向论文/近邻核查、选题决定、固定代码与来源核验、自然数据方案、强对照与预算方案。**未完成：** LIGHT 原生安装与任务恢复、模型推理、论文成绩复现、玩家研究；尚无新的科学主张。数据归档下载在当前环境受阻，具体源与待验证状态见 BASELINES，不虚构数据已读或 GPU 已跑。

CPDC 保持历史材料；E02 仍 VOID/superseded。旧 E01 的源码检查不是 NPC 行为证据。后续允许根据实测改变具体假设，但不机械展开旧的六方向列表。
