# Persona Dynamics: Unveiling the Impact of Personality Traits on Agents in Text-Based Games

规范记录：`panda_2025`；ACL 2025 Main, 31360–31394。实际版本：ACL Anthology published PDF, 35 pages。

**实际阅读范围：** 完整正文 pp.1–10；附录 A–D 的数据/训练/统计/人类轨迹协议 pp.13–16、E–F pp.22；全25游戏结果及旧基线 Table 14/15/18、全部GPT-4提示 Table 21 pp.28–29；其余图例附录仅定位未逐页通读

[原文](https://aclanthology.org/2025.acl-long.1515.pdf) · [发表／主源信息](https://aclanthology.org/2025.acl-long.1515/)

**来源与范围：** 2025；ACL 2025 Main, 31360–31394；ACL Anthology published PDF, 35 pages。完整正文 pp.1–10；附录 A–D 的数据/训练/统计/人类轨迹协议 pp.13–16、E–F pp.22；全25游戏结果及旧基线 Table 14/15/18、全部GPT-4提示 Table 21 pp.28–29；其余图例附录仅定位未逐页通读。[Persona Dynamics: Unveiling the Impact of Personality Traits on Agents in Text-Based Games](https://aclanthology.org/2025.acl-long.1515.pdf)。阅读标记：first_full_body_after_existing_partial_card。

PANDA把单一人格倾向分类器的−1/0/1分数加到DRRN动作价值，比较大五与黑暗三联征的16个高低倾向版本。分类器由GPT-4生成12万行为样本微调Flan-T5-XL；这把人格表达连接到可执行文本游戏动作和分数，但代理扮演玩家角色，并非多个有社会关系的NPC。25个Jiminy Cricket游戏、每条件3种子，主表只选另外10款绝大部分回合零分之外的15款，报告最后50回合。开放性高/无人格/低的15游戏均分为6.5/5.6/4.4，Zork1分析显示探索轨迹和稀有地点访问变化；这是人格偏置与任务探索的关系，不能直接推广为所有人格的玩家价值。

关键证据边界：全部25游戏旧系统对照见表18，但NAIL/CALM/CMPS/GALAD分数取既有论文，并非同轮重跑；文内分类器“98.59%”与表2实际跨集均值82.50不一致，不引用前者。最优通关路径的人格由只输入动作的GPT-4提示判定；引导与部分评估共用分类器，不能视作独立心理效度验证。附录D.8明确人类数据仅3人各玩10款，15游戏各2条、每条100动作、给合法候选，人格标注交叉进行。高精神病态28.8%动作一致率不等于人类有该人格或玩家喜欢该NPC。Q值行动审计也不是完整新策略运行。领域贡献是检验角色倾向如何改变真实环境中的取舍与探索，同时提示人格稳定、任务能力与心理标签效度必须分别评价。

## 与最近邻的距离

此表是当前比较视角，包含后来工作；不把它们均视作本文发表时的基线。

| 近邻 | 方法、对象或证据的区别 |
|---|---|
| [Deriving Character Logic from Storyline as Codified Decision Trees](CDT_2026.md) | PANDA以人格分类器修正任务Q值，CDT从原作行为抽取条件人物规则。 |
| [Beyond Static Persona Consistency: Dynamic Persona Coherence in LLM Role-Playing](DYNAMIC_PERSONA_COHERENCE_2026.md) | DPC研究累计状态的文本表达，PANDA研究固定性格方向如何改变交互小说行动。 |
| [Agent Sociodrama: Social-Dynamics-Guided Persona Recasting for LLM Agent Teams](AGENT_SOCIODRAMA_2026.md) | Sociodrama重选团队人格配置，PANDA固定目标人物特征来改变单个游戏代理策略。 |

## 官方资产与历史核查范围

[PANDA作者仓库](https://github.com/pull-ups/PANDA)

此前卡已有drrn.py、model.py、conditioning_model.py指定分支的定向阅读和文件SHA，未训练或全面审计。README链接动作候选器、人格分类器和Zork 1示例，不能据此宣称25款游戏和全部训练资产均完整验证。 历史核查细节与固定文件身份见[此前规范卡](https://github.com/Nhckdvrl/ssn-group-papaer/blob/c3af2a785368632ebcce5bc8cfce8994ecc56eb3/workbench/game-npc-agents/knowledge/papers/PERSONA_DYNAMICS_ACL2025.md)。
