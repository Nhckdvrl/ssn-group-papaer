# Intentional Deception as Controllable Capability in LLM Agents — 2026

- 主源<https://arxiv.org/html/2603.07848v1>；PDF SHA8ef3149450ac782ab71d677afb0914e4a9488eb921eec1839f69fdb6cbeba14a。本轮读§3模块、§4环境/评价、§5.4–5.6表4–6、§6.4限制及附录A/B轨迹例。
- **DOCUMENTED：** 图导航文本RPG，9alignment×4motivation共36profile，Llama3.1-8B target，Marco-o1分选动作/措辞两阶段。攻击阶段给真实profile，不能把结果当未知profile推断鲁棒性。40完整序列/profile/condition。主success是alignment-appropriate score≥.80，辅助follow与bigram echo；misdirection/动机差异及“真话也可影响策略”已是该文。
- **主张边界：** 作者说每location的profile期望行为由构造确定，Wanderlust/Speed与Safety/Wealth互反；这不是自然NPC私有利益的唯一行为gold。它们是否真在每个场景相反不确定，不能沿用到真实人物；正文承认生态效度限制。
- **代码：** 正文明确withhold full implementation，接受后受限分享；本轮没有作者源码或完整data，不能冒称重跑原engine。不是推定它只做dialogue：正文有图状态/路径/动作序列。
- **我们的解释/竞争解释：** 属性条件下操纵/公开发言与策略不同已经有人研究。echo关联支持措辞摄入，但对因果作用/utility harm仍需要独立干预；泛化到真实游戏NPC且实际世界利益受损未核。A矿区可以用author goals/native后果校准，不能把这本身自动当创新。
