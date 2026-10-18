# SOTOPIA-π: Interactive Learning of Socially Intelligent Language Agents

规范记录：`sotopia_pi_2024`；ACL 2024 Main, 12912–12940。实际版本：Official ACL Anthology PDF, 29 pages。

**实际阅读范围：** 完整正文 pp.1–9；完整数值/训练采样/筛选/版本/检查点协议 A–B pp.13–17；人类评价C全文（图版除外）pp.17–23；D–G额外案例与MMLU逐学科图未通读

[原文](https://aclanthology.org/2024.acl-long.698.pdf) · [发表／主源信息](https://aclanthology.org/2024.acl-long.698/)

**来源与范围：** 2024；ACL 2024 Main, 12912–12940；Official ACL Anthology PDF, 29 pages。完整正文 pp.1–9；完整数值/训练采样/筛选/版本/检查点协议 A–B pp.13–17；人类评价C全文（图版除外）pp.17–23；D–G额外案例与MMLU逐学科图未通读。[SOTOPIA-π: Interactive Learning of Socially Intelligent Language Agents](https://aclanthology.org/2024.acl-long.698.pdf)。阅读标记：new_full_read。

Sotopia-π以GPT-4轨迹行为克隆，再用自己交互中评分较高的轨迹做自我强化，实际更新为筛选后监督微调，而非在线逐步RL。生成462个新社会任务，训练每轮抽100任务×10人物对；BC保留每任务/每方前2和过局部/总体阈值样本，SR取前20%。底模Mistral-7B、专家GPT-4-0613、测试伙伴固定GPT-3.5-0613；测试90情境180点，另14难情境140点、人类只评其中28点。训练任务与测试不重合，但复用40人物。

最重要结果同时包含可学性与评价漂移：全任务GPT-4目标分BC+SR与专家同为7.62；在人评28点，BC+SR目标4.29、专家5.25、底模2.89。自动—人类差由底模.36扩大到BC+SR1.42，人评相关从专家.86降到BC+SR.58。因此“7B达到GPT-4社会智能”仅在特定LLM评价下成立。人评总分、关系、可信度及规范较底模改善，但目标差配对检验p=.059，不宜把该维度写成确定显著。30名外部加4名内部评者、每点2人，约20%高分歧点重标，须连同其过滤机制理解一致性。

安全结论只来自一个防伤害情境、每模型/角色9例；BC和SR单独甚至产生更多毒性词，不能泛化整体训练自动更安全。BC+SR的MMLU48.57接近底模49.21，SR单独43.46；这不是所有能力无遗忘的证据。领域认识是多轮社会行为能由互动数据改善，伙伴受益亦随之变化，但训练所用社会评判必须独立复核；进一步接到长期关系、制度和可执行世界仍需其他机制与评价。

## 与最近邻的距离

此表是当前比较视角，包含后来工作；不把它们均视作本文发表时的基线。

| 近邻 | 方法、对象或证据的区别 |
|---|---|
| [SOTOPIA: Interactive Evaluation for Social Intelligence in Language Agents](SOTOPIA_2024.md) | 从评价框架推进到专家示范与奖励筛选的SFT，不能把评判器同分当人类同等。 |
| [Persona Dynamics: Unveiling the Impact of Personality Traits on Agents in Text-Based Games](../../../../workbench/game-npc-agents/knowledge/papers/PERSONA_DYNAMICS_ACL2025.md) | PANDA用人格分类器引导任务学习；π用社交目标分筛选对话，均需防止训练与评价闭环。 |
| [Deriving Character Logic from Storyline as Codified Decision Trees](../../../../workbench/game-npc-agents/knowledge/papers/CDT_2026.md) | CDT把行为证据做成显式规则而非主要更新扮演模型参数。 |
