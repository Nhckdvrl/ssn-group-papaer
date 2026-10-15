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

## E65/E66前的定位补充

最新检索增加[NegaAlign](../papers/NEGAALIGN_2026.md)（2026-10-08预印本，VLA否定约束、真实执行、语义/视觉干预）和[AgentIF](../papers/AGENTIF_NEURIPS2025.md)（NeurIPS2025 D&B，条件/工具约束组合）。本地venue nearest亦返回Persona Dynamics、CoopEval、Constrained Human-AI Cooperation等，列表只作定位。本轮不自动开新环境复现；E65要分辨限制范围/明确许可，E66要测真实动作字段的竞争。普遍否定困难、条件指令困难与保留任务能力已有ownership；当前增量须由NPC实际决策的可检验预测支撑。


## E67/E68运行中再次核对
直接重读NegaAlign §3.1 Eq.(1)和§4.1：其成功本就定义为任务完成与约束满足同时成立。因此审计中“该类工作只研究违反禁令”过于狭窄，不能靠守禁令却任务失败宣称独占新问题。AgentIF §3.4也先判断条件触发，已有复杂条件作用的评价。源链接沿用上表论文卡，未新增复现。

本轮研究动作是固定原生世界、全链一致persona及具体上游输出，交叉上游/执行规则，分别测首次防卫、重复拒绝和实体任务；再让预先写定的方向预测109个本地未探索世界。它检验可操纵的阶段条件和行为路径，不预设词汇启动或威胁注意力为真。即使asset→generic恢复成功，也只识别所测试规则包的执行因果效应；词频、长度、逻辑范围与社会焦点尚不是被各自随机化的因素。是否继续拆词须由实际成功/失败模式提供问题，而不是为了封堵所有假想质疑新增网格。

本轮venue-corpus查询（运行中、主张升级前）：`nearest "game NPC personality task preservation rule framing action execution plan causal intervention cooperation"`。主要返回CaPo、Persona Dynamics、FAIRGAMER、Tracing the Persona Circuit和ThinkAct；作为已有定位的增量检查，不以词面rank作选题判决。NegaAlign与AgentIF正文再次核对，任务完成与约束满足的双指标及条件触发均已有直接先例。

另核[Agent GPA v2](../papers/AGENT_GPA_2026.md)的阶段定义、数据/裁判协议、Table1–4与效率裁判附录：目标—计划—行动分解、计划质量与遵循分离、重复错误循环均已有明确先例。本轮可推进的是具体阶段干预对原生行为的预测，不能把换阶段标签或统计计划/行动不一致写成独占贡献。没有为这一近邻新开复现或追加GPU实验。

## E69前的定位

venue nearest以`persona task action congruence character motivation assigned task physical game actions task completion`查询，返回Persona Dynamics等。[PANDA/ACL2025](../papers/PERSONA_DYNAMICS_ACL2025.md)§5.3已经用成功walkthrough的特质倾向解释任务表现，Table6–8已有奖励动作与人物动作分布。因此“特质与任务动作兼容”本身有直接先例。E69的具体增量待同图任务干预与接收者/动作族真实事件检验，不能仅给假说起trait-verb名称。[Dragon](../papers/HOW_TO_MOTIVATE_DRAGON_2021.md)的动机—timeline框架也早已存在；旧原子goal成功即结束的观察窗没有覆盖其后交付，E69对此做共同窗口实测。近邻用于定位，不输出自动科学去留判决。
