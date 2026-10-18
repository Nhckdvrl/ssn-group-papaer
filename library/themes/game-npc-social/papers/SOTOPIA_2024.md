# SOTOPIA: Interactive Evaluation for Social Intelligence in Language Agents

规范记录：`sotopia_2024`；ICLR 2024。实际版本：Official ICLR proceedings PDF, 45 pages。

**实际阅读范围：** 完整正文 pp.1–9；任务与评价全部文字协议/人类招募和校准附录 A–G pp.18–31；界面截图仅按正文所述查看，长对话例库 pp.33–45未逐篇通读

[原文](https://proceedings.iclr.cc/paper_files/paper/2024/file/b3075b88e583a0e98d8b24338a613060-Paper-Conference.pdf) · [发表／主源信息](https://proceedings.iclr.cc/paper_files/paper/2024/hash/b3075b88e583a0e98d8b24338a613060-Abstract-Conference.html)

**来源与范围：** 2024；ICLR 2024；Official ICLR proceedings PDF, 45 pages。完整正文 pp.1–9；任务与评价全部文字协议/人类招募和校准附录 A–G pp.18–31；界面截图仅按正文所述查看，长对话例库 pp.33–45未逐篇通读。[SOTOPIA: Interactive Evaluation for Social Intelligence in Language Agents](https://proceedings.iclr.cc/paper_files/paper/2024/file/b3075b88e583a0e98d8b24338a613060-Paper-Conference.pdf)。阅读标记：new_full_read。

Sotopia把角色、关系、秘密和私有社会目标交叉组合，90个社会情境、40人物，每情境5人物对得到450任务；4模型彼此配对。最多20轮，语言、非言语、物理行动均是文本类型，状态转移只是追加历史，并没有独立物理世界执行器。七维评价把目标、可信度、关系、信息获取、秘密、规范、财富分开，是从“说得像”走向互动社会目标的重要谱系；不过秘密/规范默认只罚不奖，不能直接当所有虚构角色的价值函数。

GPT-4-0613在全体目标均分7.62，高于GPT-3.5的6.45；提示采用简单角色/场景/历史，CoT/ReAct明确留待未来。Hard是从450任务按模型表现选20个难项，人机40、人人20段；GPT-4与人的目标分4.85，对方人类5.95，人人6.15。不能由这套经过难例筛选的2023模型证据推当前商业模型一般失败。伙伴能力会改变同一个代理表现，互动评价必须报告对手/同伴分布。

人类校准正文称约200段，附录明确222段（180模型间、42含人类），每段2评者，235申请者筛43人。七维合并五档κ=.503，可信度与关系仅.200/.161；GPT-4与人类对模型目标评分相关.71，对模型秘密仅.22，人类行为的多个维度进一步下降。因此“LLM已可全面评价社会智能”超出证据。贡献是可扩展、具私有信息的社会互动测试与多维审视；开放处是跨长时段的关系/目标变化、环境裁决与玩家意义，不能把口头协商结果直接当完整游戏后果。

## 与最近邻的距离

此表是当前比较视角，包含后来工作；不把它们均视作本文发表时的基线。

| 近邻 | 方法、对象或证据的区别 |
|---|---|
| [SOTOPIA-π: Interactive Learning of Socially Intelligent Language Agents](SOTOPIA_PI_2024.md) | π沿用环境/评判器做交互学习，新增训练分布会改变自动分数与人评的对应。 |
| [Agent Sociodrama: Social-Dynamics-Guided Persona Recasting for LLM Agent Teams](../../../../workbench/game-npc-agents/knowledge/papers/AGENT_SOCIODRAMA_2026.md) | Sociodrama显式更新关系和情绪并优化团队人格，Sotopia主要提供私有目标互动评测。 |
| [Generative agent-based modeling with actions grounded in physical, social, or digital space using Concordia](CONCORDIA_2023.md) | Concordia由GM裁定世界后果，Sotopia的文本物理动作并无独立执行器。 |
