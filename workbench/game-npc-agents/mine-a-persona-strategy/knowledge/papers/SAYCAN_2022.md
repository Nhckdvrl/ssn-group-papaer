# SayCan — Do As I Can, Not As I Say: Grounding Language in Robotic Affordances（2022）

证据：正文与关键附录、作者公开示例代码；CoRL 2022，正式收录于PMLR 205:287–318（2023出版）。未复现机器人实验。

主源：[正式会议页](https://proceedings.mlr.press/v205/ichter23a.html)、[正文](https://arxiv.org/html/2204.01691)、[作者项目](https://say-can.github.io/)、[作者代码](https://github.com/google-research/google-research/tree/master/saycan)。

1. **论文形态：** 系统＋受控消融，连接语言规划与具身技能。
2. **背景与压力：** LLM 能建议语言上合理、机器人实际上做不了的行动；低层技能本身又缺少复杂指令理解。
3. **改变的前提：** 不直接执行语言生成的计划，而将每项技能“对目标有用”的语言评分与当前状态下可执行性评分结合，再逐步选择。
4. **Idea 来源：** DOCUMENTED：将已有技能作为语言模型的实体能力接口，结合两类评分。RECONSTRUCTED：让“想做什么”与“能做什么”的错误在可观测接口上分别暴露，便于解释与改进。
5. **最近邻距离：** 与 BC-Z/MT-Opt 等低层技能、直接 LLM 计划和纯文本具身规划相比，增加状态 affordance 对技能选择的约束；不是我们首次提出的层次区分。
6. **实际已读与实验：** §3/算法1、§4–5、表1–3、Appendix D.1–D.2/E.1/E.3/E.6。101 条指令、7 任务族；PaLM 计划/执行成功率 84%/74%，真实厨房 81%/60%。比较 No VF、Generative、BC NL/USE，并比较不同语言模型。种子总口径与整项 GPU 成本本轮未核对。
7. **证据与负例：** 计划与执行由三名人评多数判定；长程有提前终止，affordance 有误判。新增抽屉任务计划 100% 而执行仅 33%，说明好计划不自动等于技能执行成功。公开桌面 notebook 使用检测式 affordance，不能等同主文真实机器人训练系统。
8. **可迁移研究动作：** 同时检查目标选择、路径是否有效和物理执行；用实际初态与能力变化检验解释，保留计划正确但执行失败的负例。
9. **对整体 NPC 研究：** 继承既有层次工具。我们的 NPC 有自身目标、人设与可拒绝/协商的社会请求，外部请求不是唯一指定目标；整体增量在于测清人设怎样影响目标采用与必要行动，并预测前提变化何时改变最终人物效应。无需为使用现成分层思想而逐组件缩小主张。

源码核读：`SayCan-Robot-Pick-Place.ipynb` 的 `affordance_scoring`、`combined_scores` 与 Runner；SHA256 `5f1b975f43197af538867e6cb1864a2fea354fe4540668e8be20c37e682d626c`。缓存位于 `/home/xiang/.cache/game-npc-research/sources/progress-selection-2026-10-16/`，未运行 notebook/API。
