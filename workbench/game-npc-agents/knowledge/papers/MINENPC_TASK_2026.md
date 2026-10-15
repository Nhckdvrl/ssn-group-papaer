# MineNPC-Task（2026预印本，正文与相关附录）

主源：[论文](https://arxiv.org/html/2601.05215)。核读§3–6、附录A/B/D及E任务表，并由PDF核对validator提示；本轮未取得可执行作者仓库或复现。接收身份未核实。

**DOCUMENTED：** 真人共玩产生44高层任务、216尝试子任务，8位熟练玩家，GPT-4o单模型；作者报告71/216失败。公开Mineflayer感知/动作边界、plan预览、单轮澄清、代码review及有界repair，按状态/库存证据评判。附录有BotState、TaskModel、ValidationOutput及Validation AI Agent提示，故“machine-checkable”不自动等同全部为确定性engine flags。

**idea来源与尺度：** DOCUMENTED为从真实玩家的任务/失败和恢复过程形成可复用任务集。贡献包括真实互动压力、评估程序和观察，未做跨模型或组件消融；不能把216子任务当216独立世界。其NPC主要执行玩家任务，没有本地复现可直接代表本项目的私有作者目标与请求冲突。

**对本项目：** 真实玩家会在意资源/工具处理与恢复，印证行动路径问题具有应用意义。它的任务/日志结构可供以后跨游戏检验借鉴；本轮不因看见新框架就启动大规模移植，也不将已有的分阶段日志当我们的独立发明。整体增量仍由人物、目标取舍与实际执行的联合预测决定。

PDF资产`cache/papers/minenpc_task_2026.pdf`，SHA256 `a3237d317d1ca6980da1bb4ec72610bf2955c36b72ad1bf8dc4f248713095ff2`。
