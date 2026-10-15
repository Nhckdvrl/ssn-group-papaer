# Persona Dynamics / PANDA（ACL 2025 Main）

[ACL论文页](https://aclanthology.org/2025.acl-long.1515/)，[正文v2](https://arxiv.org/html/2504.06868v2)，[作者仓库](https://github.com/pull-ups/PANDA)。本轮核读§2.3、§4.2、§5.2–5.3/Table6–8、Appendix F.3，作者README；代码实现未逐行核验，未复现训练。

**作者事实：** 在DRRN动作价值上加入情境—动作人格分类器的分数，考察Jiminy Cricket中的任务表现。Table6把奖励动作及价值分开，Table7报告训练前后人格动作分布；Table8用GPT-4判断25游戏walkthrough的特质倾向，以解释某些特质为何更利于通关。附录分析人格数据的动词/名词分布。README给出GPT-2动作候选器、Flan-T5-XL分类器和运行路径。

**Idea来源与最近邻距离：** 该文已将成功任务需要的行为与人物特质兼容性联系起来。“人物会促进某类任务动作”不能单独占据新颖性。E69在同一角色/物品/请求者上改变指定任务，以原生目标和接收者事件测交互，弥补跨游戏构成差异；该交互仍不单独识别词汇启动。人格分类分数不是我们的行为评价，避免用同一个分类器既引导又证明效应。没有据这篇近邻关闭I04或另开RL复现。
