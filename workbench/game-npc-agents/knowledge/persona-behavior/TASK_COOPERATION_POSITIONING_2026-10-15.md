# 任务保留与合作：E63/E64的近邻定位

用户报告后要求超越“Agreeable更愿意给物品”，停止新增细标签与无回路patch。当前大问题仍是NPC怎样同时形成角色选择、维持自身目标并响应社会互动，不钦定“自毁”故事。

| 近邻 | 已拥有的具体认识 | 当前可检验的增量入口 |
|---|---|---|
| [FAccT2026 Identity Overrides Incentives](../papers/IDENTITY_OVERRIDES_INCENTIVES_2026.md) | persona×收益显式化交互；附录已有收益优先、人格只影响风格的控制 | 原生物品依赖、顺序、可恢复路径与真实对方行动，而非重复人格压倒收益 |
| [Persona-Guided TOD](../papers/PERSONA_GUIDED_TASK_DIALOGUE_2026.md) | 人格适应与服务grounding取舍，明确schema/数据库约束 | NPC有自己的目标，任务与合作分别由实体事件读出 |
| [Price of Agreement](../papers/PRICE_OF_AGREEMENT_2026.md) | 用户偏好/记忆注入造成任务准确性损失，过滤与训练对照 | 把请求的采纳落实到资产归属与后续合法恢复，不把给予当错误答案 |
| [ACL2026 DebtBench](../papers/DEBTBENCH_ACL2026.md) | 协议达成高却过度让步；经济理性与体验分开 | 协议后真实行动、对手响应及合作后受损的路径，需要实测而非换场景 |
| [EMNLP2026 MASCOT](../papers/MASCOT_EMNLP2026.md) | 两级persona对齐/Director训练与社会贡献，含独立人评 | 实体任务与私人利益不由对话贡献分数替代；不照搬两级训练 |
| [SidConArena](../papers/SIDCONARENA_2026.md) / [KDD2025 MMOAgent](../papers/MMOAGENT_KDD2025.md) | 真实多步经济、礼貌与谈判能力差、画像/劳动成本与交易制度 | NPC私有作者目标与实际履约路径；价格表/目标事件不能自动替代全部效用 |
| CT-Bench / Dragon / LIGHT | 长期资源承诺、策略互动、以对话影响真实动作 | 不能声称首次多步承诺；聚焦哪些可操纵条件预测保任务的合作 |

**Compression risk：** “人设—效用冲突”“友善导致让步”“加目标优先提示改善”各自都容易压缩成已有结论。E63普通规则是竞争解释控制；若它解释数据，就如实接受。E64仅9独立图的发现性pilot，不能用调用数替代独立情境。

**查询记录：** `python3 tools/venue_corpus/query.py nearest 'NPC personality social compliance instrumental goals costly resource negotiation task preservation'`；命中包括PRISMA、冲突对话对齐、FAIRGAMER、Richelieu等，词面分数不是科学判决。最新主源检索另找到EMNLP2026 MASCOT与ACL2026 DebtBench；实际阅读正文/关键附录范围在各论文卡逐项列出，代码阅读与训练复现不混写。

**正在检验：** E63同人物/请求者，原目标资产与另一真实资产，none/明确任务优先/资产保护，三模型三seed；E64原生互持物品、私有目标、真实交换/偷取/攻击。得到实际成功失败后才收敛机制；不从attention权重或口头理由直接推断因果回路。

## 完整结果前已改变的定位

E63明确任务优先在32B恢复原任务，同时保留另一物品合作的角色差；资产保护包在Gemma反而增加未推进终点和可行计划未采纳。E64两Qwen完整，普通check在27B提高双向Give，firm的跨模型check交互33.3pp [11.1,59.3]；agreeable交互区间跨0，资源取得交互亦未明确。以上不等于发现统一预训练回路。

测量层次需要明确：E63的200任务主要是原子Give/equip/consume，目标对象依赖不等于完整工具利益链；同资产的后续回报、作者长期目标尚未都具备实体flag。E64的9个源get/steal配对和33图CPU原Give来源也不自动等于真实自利交易。下一增量需要让可操纵因素预测实际回报/后续任务，而非仅换一个词汇描述同一交付效应。新颖性保持定位，人决定方向状态。
