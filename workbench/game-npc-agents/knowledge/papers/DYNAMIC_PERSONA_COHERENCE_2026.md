# Beyond Static Persona Consistency: Dynamic Persona Coherence in LLM Role-Playing

规范记录：`dynamic_persona_2026`；ACL 2026 Main，28942–28956（ACL Anthology正式PDF）。实际版本：ACL Anthology 2026.acl-long.1336，15页。

**实际阅读范围：** 完整正文第1–8页及附录A–F第10–15页；包含全部人物、状态、评分、基线、完整结果与跨评判器/语言/超参协议；参考文献选择性核对

[原文](https://aclanthology.org/2026.acl-long.1336.pdf) · [发表／主源信息](https://aclanthology.org/2026.acl-long.1336/)

**来源与范围：** 2026；ACL 2026 Main，28942–28956（ACL Anthology正式PDF）；ACL Anthology 2026.acl-long.1336，15页。完整正文第1–8页及附录A–F第10–15页；包含全部人物、状态、评分、基线、完整结果与跨评判器/语言/超参协议；参考文献选择性核对。[Beyond Static Persona Consistency: Dynamic Persona Coherence in LLM Role-Playing](https://aclanthology.org/2026.acl-long.1336.pdf)。阅读标记：first_full_body_after_existing_partial_card。

**问题与机制。** 区分恒定身份与可以累积改变的心理状态，反对把人物一致性等同于每次情绪不变。L固定天生/习得特征及当前处境；S为情绪效价，Mmeaning为意义感，Mstrain为压力适应能力，三个0–10标量按GPT-4o评事件的增量累积截断。PCC分别核身份与状态表达并取较低分；低于.6重写，达到.85的案例入PCR，按场景与状态检索改写参考。其价值是给角色变化明确接口；EMA、FAtiMA等经典早已有稳定倾向影响动态评估与应对的机制，不能把全部人格动态建模史写成静态提示。

**证据与最重要的基线条件。** 五个人设×GPT-4o/Claude-3.5/DeepSeek-V3.2，宣称每配置5种子、100–150轮。Vanilla不是带完整对话的普通商业角色：附录A明写每次只给L、当前事件、固定中性S/M，完全不保留历史响应或状态演化。Ours事件流回放给所有基线，未测各方法自由演化的匹配分布。PCC平均.7254→状态累计.8902→加改写.9195，84.9%报告增益来自补状态；不能推断强模型获得相同历史/累计摘要后仍需完整P3。

**评价局限与数值澄清。** GPT-4o兼状态估计和评价，重写也针对同PCC；Claude复评15配置、DeepSeek仅2人物，同意排序未替代人类心理合理性/玩家体验。无真人参与。PCC对不表现某特征的neutral仅.25，可能鼓励每句显露性格。式5为min(L,(S+M)/2)，但表1/3 Lisa-GPT4o基线.6876大于S/M .6751，Alex-DeepSeek .7278大于.6577；同批样本的均值应保留该不等式，不能以四舍五入解释，需作者澄清汇总。正文2,185 generation tasks与15配置×5种子×100–150轮的计数关系也未交代。跨语言仅2人物×1模型×2种子，λ敏感性仅单配置单种子，不能声称普遍鲁棒。

**领域位置。** 这是一套文本人物压力/情绪轨迹生成与修复系统，没有可执行游戏世界、关系网络或玩家改变制度的结果。真正有意义的开放问题是何种事件历史应改变何种心理变量，如何体现恢复、矛盾情绪、人物成长，以及这些状态是否因果性地影响持续选择。当前夹逼到模型自定心理量表的高分，只证明指定表达控制的一部分。

## 与最近邻的距离

此表是当前比较视角，包含后来工作；不把它们均视作本文发表时的基线。

| 近邻 | 方法、对象或证据的区别 |
|---|---|
| [EMA: A process model of appraisal dynamics](../../../../library/themes/game-npc-social/papers/EMA_2009.md) | EMA已有随事件和应对变化的情绪过程，DPC新增的是LLM场景下身份/状态分评与修复。 |
| [FAtiMA Modular: Towards an Agent Architecture with a Generic Appraisal Framework](../../../../library/themes/game-npc-social/papers/FATIMA_MODULAR_2014.md) | FAtiMA展示情绪模块与动机/ToM的组合，DPC只实例化少数心理标量和表达约束。 |
| [Agent Sociodrama: Social-Dynamics-Guided Persona Recasting for LLM Agent Teams](AGENT_SOCIODRAMA_2026.md) | Sociodrama把动态情绪放入多角色关系与团队选角，DPC主要是单人物压力轨迹。 |


## 2026-10-22矿区D复读与规范入口合并

本轮再次阅读主文§1–6与附录A/B/D/E相关段落，确认身份L固定、状态累计及普通基线缺少完整历史等判断；没有新复现。本卡是本论文唯一正文权威卡，`library/themes/game-npc-social/papers/DYNAMIC_PERSONA_COHERENCE_2026.md`仅保留兼容导航，避免两份阅读记录分叉。对D的意义是状态/表达控制谱系，不据组件先例收窄整个角色经历学习问题。
