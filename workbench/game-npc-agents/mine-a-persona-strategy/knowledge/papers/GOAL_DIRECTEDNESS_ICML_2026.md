# A Behavioural and Representational Evaluation of Goal-Directedness in Language Model Agents — ICML 2026

- 来源：[正式论文](https://proceedings.mlr.press/v306/arghal26a.html)，正文与关键Appendix E/F/G已读；代码[interp](https://github.com/SPAR-Telos/interp) pin `37aae261d4232e4136145dfca9b57040e48f94fa`，另有[reveng](https://github.com/SPAR-Telos/reveng)。已审token/site配置、probe准备和公开树，未运行模型或完整审reveng。
- 实验：GPT-OSS-20B、完全可见MiniGrid；五尺寸7–15×六墙密度，每格10worlds×10trajectories，温度0.7，horizon=1.5×最优路径。对照最优策略／动作分布、保难度旋转与反射、钥匙／门／隐式目标。不是人格NPC任务。
- 已有主张：行为成功不足以归因内部目标；空间belief和多步plan可解码，reasoning前后信息重组，动作与解码地图分别比较。“先测goal/belief再看actions”或简单goal probe不能当新贡献。
- Appendix F：在原/反事实最优动作不交且两边原预测均成功的条件中，agent或goal位置变更；单层7/15/23、四类token站点、双方向共456次，action均未改变；全层patch全部改变。另144次应保持动作的负控制均保持。可解码不等于窄干预有效，不能重发现distributed goal-state representations。
- 代码事实：`three_token_probes.conf`／`apply_trained_probes.conf`显式设置pre-reasoning suffix、output indices、layer15、linear/MLP、normalization／class balance／eval split；公开树未见命名patch的实现。配置含调试／旧条目，不把每个脚本参数视作最终协议。patch当前依据Appendix F，未代码独立核验。
- 我们的解释／竞争解释：完全可见、已给终点及求最优动作，识别的是state/plan表征，不直接回答社会互动如何产生新任务。简单扩到校园或“人物影响belief”仍有Persona Vectors in Games等强归属。E48/49显式agenda、意图记忆、已有计划冗余可用于定位，但普通管线本身不是创新；需要跨角色／场景可预测的剩余规律。
