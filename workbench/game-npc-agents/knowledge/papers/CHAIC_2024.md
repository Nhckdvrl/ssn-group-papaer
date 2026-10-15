# Constrained Human-AI Cooperation（CHAIC）

NeurIPS2024 Datasets and Benchmarks。[正文v3](https://arxiv.org/html/2411.01796v3) · [正式PDF](https://openreview.net/pdf?id=2vs1fIAy3X)。2026-10-15核读§3–5/Table2、AppendixB/C与E.3；未复现或审计作者代码。

**DOCUMENTED：** 从可达高度、移动、力量等个体身体限制出发，测试伙伴目标推断与具身协作。受限伙伴为规则策略，助手用LLM/VLM决策；AppendixB明确低层导航执行用A*等模块。Table2有无助手、规则、随机、基础模型与oracle；§5.3单列目标推断、动作和协作失败。AppendixE保留RL/SmartHelp负结果。

**定位判断：** 身体可行性、合作成功及计划—动作接口已有直接先例。这里的助手以帮伙伴完成任务为目标；我们的NPC保留作者自有任务，问题是社会请求相对于该任务的方向及前提如何共同改变人物行为。E70不能把“前提步骤会影响合作”当独占新颖性。增量应是同NPC/目标/物品配对中的具体可预测关系；也不能把底层执行器不同的系统差直接叫人格失效。

不新增CHAIC复现，不把视觉感知/导航困难混入当前LIGHT的完整符号观测问题。
