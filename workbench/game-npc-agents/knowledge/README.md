# 游戏 NPC Agent 专属知识库｜2026-10-13 用户第二次领域校准

**研究对象只有游戏世界中非玩家控制角色**，不是单独通关的 game-playing agents / 仅靠 prompt 模仿人物的聊天机器人。研究 game NPC 的训练、角色可控行动、多角色行为、与玩家互动和真正的部署成本；高级 LLM 可供训练/低频决策，快策略可由其它政策执行。

## 当前读取入口
1. **[NATIVE_GAME_NPC_FRONTIER.md](NATIVE_GAME_NPC_FRONTIER.md)**：EA、PCSP、UBCL、Human-Like tactical bots、MultiGAIL、KRAFTON、NeurIPS2026、世界模型 NPC 的论文/源码证据、会议身份与真正创新所有权。
2. **[METHOD_TERRITORIES.md](METHOD_TERRITORIES.md)**：围绕 designer feedback、共享策略与行为修复、LLM→可执行政策学习、真实玩家适应的探索空间。
3. [POSITIONING.md](POSITIONING.md)：强最近邻和不能再次主张 novelty 的项目。
4. [EXPLORATION_ENTRY](../EXPLORATION_ENTRY.md)、[BASELINES](../BASELINES.md)、[LOCAL_FIRST](../LOCAL_FIRST.md)、[E05](../experiments/E05-native-npc-baseline-gate.md)：零API与本地研究执行。
5. [PROBLEM_GENEALOGY](PROBLEM_GENEALOGY.md) / [RESEARCH_CALIBRATION](RESEARCH_CALIBRATION.md) / [INDUSTRY_EVIDENCE](INDUSTRY_EVIDENCE.md)：领域历史、转折研究动作、产品说明；仍可引用，但不能覆写当前游戏 NPC 定义。

## 旧路线保留但降级
[GOAL_CONTROL_REVIEW](GOAL_CONTROL_REVIEW.md)、[FRONTIER_CHECK](FRONTIER_CHECK.md) 仍包含此前 goal-vs-plan、LLM narration、RPA / 竞争解释文献。它们是**潜在子问题/邻接研究**，用户明确拒绝将其独占 workbench；旧 E03/E04 从未运行，不是反证。CPDC 是历史源码/比赛，不再争夺科研主轴。

## 阅读等级与证据记录
P0 只题名；P1 原文摘要；P2 指定正文/源码片段；P3 正文＋关键附录/代码重要路径系统审阅；P4 本地结果复现。新文件单篇逐项标实际读到的内容，不允许把论文库的条数当精读结果。
论文正文中作者的主张/数字、可公开核验的代码、我们自己的解释/猜想，必须分别注明；“训练分数高”不能自动等于玩家认为自然；“游戏角色行为”不能简单由聊天 judge给真值。持续查近邻，不为了新的损失函数找动机。
