# Persona Dynamics / PANDA（ACL 2025 Main）

[ACL论文页](https://aclanthology.org/2025.acl-long.1515/)，[正文v2](https://arxiv.org/html/2504.06868v2)，[作者仓库](https://github.com/pull-ups/PANDA)。本轮核读§2.3、§4.2、§5.2–5.3/Table6–8、Appendix F.3，作者README；代码实现未逐行核验，未复现训练。

**作者事实：** 在DRRN动作价值上加入情境—动作人格分类器的分数，考察Jiminy Cricket中的任务表现。Table6把奖励动作及价值分开，Table7报告训练前后人格动作分布；Table8用GPT-4判断25游戏walkthrough的特质倾向，以解释某些特质为何更利于通关。附录分析人格数据的动词/名词分布。README给出GPT-2动作候选器、Flan-T5-XL分类器和运行路径。

**Idea来源与最近邻距离：** 该文已将成功任务需要的行为与人物特质兼容性联系起来。“人物会促进某类任务动作”不能单独占据新颖性。E69在同一角色/物品/请求者上改变指定任务，以原生目标和接收者事件测交互，弥补跨游戏构成差异；该交互仍不单独识别词汇启动。人格分类分数不是我们的行为评价，避免用同一个分类器既引导又证明效应。没有据这篇近邻关闭I04或另开RL复现。

## 2026-10-16 增读作者源码

实际读到 `jiminy-cricket/drrn/drrn.py` 的 update/act、`model.py` 的 forward/act、`conditioning_model.py` 的人格分类分支：网络将分类条件信号用于候选动作价值修饰，随后采样；训练更新也调用条件化 forward。源代码事实支持其“人格引导真实序贯行动”的实现范围，未训练、未逐行审计整个系统，不重新开 RL 复现。

**对主问题的启发：** 已有人物引导探索、奖励动作及任务得分的研究，足以作为强参照；我们的完整问题仍是有自身作者目标的 NPC 怎样在社会请求与物理前提下采用目标、推进必要动作、分配资源。应解释同目标人物效应随情境变化并预测真实后果，而非把单个动作或人格分类分数当独立贡献，也无需要求整条证据链的每个工具前所未有。

只读缓存：`/home/xiang/.cache/game-npc-research/sources/progress-selection-2026-10-16/`。三文件 SHA256：`drrn.py` `1a18b80b21c072bd1e4dc999dad3711810dd57faeb25b286983b262516f81330`；`model.py` `f23f4f9e72fcb68adf1f7bdc7d8bf48c2a7ec0254803669a241f9474cb6c15b3`；`conditioning_model.py` `55f5161c56d6039f8875ec3d41661988aef40c6ffbb297b189882b5560c7f77d`。论文版本增读为 [v4 HTML](https://arxiv.org/html/2504.06868)，正文§2.3/§4/§5与表3–8，并核对附录B的训练配置；没有把代码阅读当作新科学结果。
