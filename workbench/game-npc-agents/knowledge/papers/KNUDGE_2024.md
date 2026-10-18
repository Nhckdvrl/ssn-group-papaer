# Ontologically Faithful Generation of Non-Player Character Dialogues

规范记录：`NPC-PA22`；EMNLP 2024, pp.9212–9242。实际版本：ACL Anthology Version of Record, 31 pages。

**实际阅读范围：** 全文正文 §1–8、Limitations/Ethics、Tables 1–6；附录 A–L 方法文字、Algorithm1、Tables7–8及关键任务/人物/评价和修订提示/树样例。未逐字读全部重复长提示和所有巨大树节点，非全部附录逐图审查。

[原文](https://aclanthology.org/2024.emnlp-main.520.pdf) · [发表／主源信息](https://aclanthology.org/2024.emnlp-main.520.pdf)

**规范来源：** [Ontologically Faithful Generation of Non-Player Character Dialogues](https://aclanthology.org/2024.emnlp-main.520.pdf)。发表/阅读版本：ACL Anthology Version of Record, 31 pages。

**来源与阅读。** Nathaniel Weir 等，EMNLP 2024，pp.9212–9242，ACL Anthology 正式 PDF。通读正文 §1–8、Limitations/Ethics、Tables 1–6；补读附录 A–L 的方法文字、结构验证 Algorithm 1、Tables 7–8、评价/修订提示及关键任务、人物、生成树样例。未逐字遍读全部重复长提示与所有大型树节点，也未做图像级版面审查。库已有 KNUDGE 卡，本次属**既有条目新全文阅读与证据加深**。

**任务与来源。** 从获授权的 The Outer Worlds 游戏文件提取全部 45 支线任务、159 棵对话图、约 4.7K 话轮，再以玩家 wiki 补人物/世界、进入和离开对话时的任务说明，人工标注话轮支持事实。平均 29 节点、1,322 约束 token，按任务 60/10/30 切分。它面向**作者生成/补全对话树**，而非实时自主角色。抽取时先只走无状态条件边，再人工补相关条件边，不能说保留原游戏完整技能/状态执行逻辑。新增 2 个专业作者写的未见任务产生 8 项测试，对既有 8 项作补充；仍是同一游戏设定，不能等同多个独立游戏。

**方法与证据。** T5-large、GPT-3 text-davinci-003 用历史/世界/任务生成下一句；GPT-4-turbo 与 Vicuna-13B-16k 生成整图，采用 BM25 例子、知识选择 KS、先补 lore 再以脚本检查断边/不可达/长单链/角色出边等，最多 5 轮修订。下一句人工评价每模型 100 项，完整参与标注的人数未清楚报告。全知识普通 ICL 在连贯/不矛盾上为 3.88/3.97，KS 为 3.78/3.85；KS 增加知识重叠但并无全面人评优势。31 节点 skeleton 的 16 项人评也整体偏好普通 ICL。端到端 Table 6 主要由 GPT-4 评，图级连贯性与人不相关，故只公布相关的 lore/任务/game-effect 三项；相关约 .30/.47/.47，不能笼统宣称强裁判可靠。

**关键限制与用处。** “Effect on the Game”是读生成树后判断文字是否达成要求，**没有独立引擎执行和玩家实测**。附录 Table 8 的 16 对话专家比较显示，完整修订法对普通 ICL 的 lore 胜/负 12.5/6.2%、任务 25/0%、game effect 25/18.8%，但内容建议 25/43.8%、吸引力 0/25%，并非所有质量单调改善。人物档案正确事实（Tucker 已成年）过早暴露还会破坏叙事，说明“事实真”与“此刻应该说”不同。KS、树修订和图结构检查是合理强基线组件；开发可用性仍需真实作者编辑成本及整局玩法验证。附录所谓百万美元成本是人数×外部薪资×工期估算，非访谈/公司实测，不能拿来当已验证节约空间。

## 与最近邻的距离

此表是当前比较视角，包含后来工作；不把它们均视作本文发表时的基线。

| 近邻 | 方法、对象或证据的区别 |
|---|---|
| [A Framework for Exploring Player Perceptions of LLM-Generated Dialogue in Commercial Video Games](../../../../library/themes/game-npc-social/papers/DISCO_PERCEPTIONS2023.md) | 两者专业RPG语料与人工比较，后者追问原作玩家文风偏好。 |
| [Personalized Quest and Dialogue Generation in Role-Playing Games: A Knowledge Graph- and Language Model-based Approach](../../../../library/themes/game-npc-social/papers/PERSONALIZED_QUEST2023.md) | 早期KG任务介绍明确分结构和生成语言，本研究推进到复杂对话图。 |
| [StoryAssembler: An Engine for Generating Dynamic Choice-Driven Narratives](../../../../library/themes/game-npc-social/papers/STORYASSEMBLER2019.md) | 运行时片段规划/作者调试先例可补本研究尚未验证的开发流程。 |

## 官方资产与历史核查范围

[ACL正式发表页](https://aclanthology.org/2024.emnlp-main.520/) · [官方代码与数据](https://github.com/nweir127/KNUDGE)

作者README提供任务数据、专业作者新任务、数据对象接口与事实数据处理脚本。许可证、数据重建、原始quest／dialogue／support对齐仍需专门核查；本次论文阅读不替代完整资产审计。 历史核查细节与固定文件身份见[此前规范卡](https://github.com/Nhckdvrl/ssn-group-papaer/blob/c3af2a785368632ebcce5bc8cfce8994ecc56eb3/workbench/game-npc-agents/knowledge/papers/KNUDGE_2024.md)。
