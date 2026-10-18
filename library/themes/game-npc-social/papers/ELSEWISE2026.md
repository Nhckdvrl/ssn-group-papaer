# Elsewise: Authoring Open-Ended Interactive Narrative with Possibility Space Visualization

规范记录：`NPC-PA15`；UIST 2026 listed by author; no final publisher DOI verified in this reading。实际版本：arXiv 2601.15295v2, 2026-09-09; author-listed UIST version。

**实际阅读范围：** 全文正文 §1–9、附录 A、图表文字、玩家模拟人设/故事主题；外部画布材料未读。

[原文](https://arxiv.org/pdf/2601.15295v2) · [发表／主源信息](https://ywang485.github.io/)

**规范来源：** [Elsewise: Authoring Open-Ended Interactive Narrative with Possibility Space Visualization](https://arxiv.org/pdf/2601.15295v2)。发表/阅读版本：arXiv 2601.15295v2, 2026-09-09; author-listed UIST version。

**阅读身份与范围：**新读 arXiv 2601.15295v2（2026-09-09），全部正文 §1–9、Appendix A 图注、玩家代理类型和题材表；单独补充画布未读。https://arxiv.org/pdf/2601.15295v2 。作者主页列 UIST 2026，但此 PDF 未给正式会议 DOI，记录为已核查的 v2 作者稿，不能称已读正式会录。

**贡献与比较：**将不同游戏经历中、同一时步且在作者选定维度取值相同的状态捆绑成图；可按自定或 Claude-3.5-Sonnet 归纳的语义维度比较，关联两维、过滤、对比改稿前后。依旧用自然语言世界和条件/效果规则控制 LLM 游戏主持人。12 人均至少中等 GenAI 经验，其中 6 位有公开互动作品；顺序平衡，比较可视化工具与相同叙事控制规则但以自行试玩为主的界面。每故事限一场景四角色，每次三条模拟轨迹、各五轮。实验中全部轨迹来自模型玩家，并无真实外部玩家数据。

**实际结果与限制：**作者预期故事的信心中位数 6 对 3.5（p=.031），创意探索与表达较好；控制感 6 对 4 的 p=.052 未达常用阈值。Elsewise 平均看到 54.4 轮，基线 17.2 轮，故不宜把模拟批量浏览与图形本身的作用分开归因。维度提取算法未独立评价；相同时步不等于相同叙事进度，分类可能偏离作者含义；“想买这游戏”的语义桶也不能视为购买行为证据。

**横向认识：**承接 StoryAssembler 的状态与路径可视化，把显式变量扩展为可由作者命名的语义维度，适合发现提示改动如何影响故事分布。它降低的是创作者观察不确定空间的困难，尚不证明玩家体验或稳定控制提升。代理玩家可提供反例灵感，不能替代真人；部分 killer 档被安全过滤停用也使覆盖进一步受限。论文中自称无限 agency 的表述，应由后文作者对实际 agency 两条件均中位数 4 的谨慎结果约束。

## 与最近邻的距离

此表是当前比较视角，包含后来工作；不把它们均视作本文发表时的基线。

| 近邻 | 方法、对象或证据的区别 |
|---|---|
| [StoryAssembler: An Engine for Generating Dynamic Choice-Driven Narratives](STORYASSEMBLER2019.md) | 两者可视化分支调试，后者搜索明确片段状态，本研究显示模型模拟的语义状态。 |
| [Orchid-Creator: An Authoring Tool Supporting LLM-Driven Interactive Narrative Creation](ORCHID_CREATOR2026.md) | 后者有长期艺术家和展览观众，本研究没有独立真人玩家。 |
| [Player-Driven Emergence in LLM-Driven Game Narrative](PLAYER_EMERGENCE2024.md) | 后者从真实玩家策略发现未预想路线，可与本研究模拟玩家覆盖互补。 |
