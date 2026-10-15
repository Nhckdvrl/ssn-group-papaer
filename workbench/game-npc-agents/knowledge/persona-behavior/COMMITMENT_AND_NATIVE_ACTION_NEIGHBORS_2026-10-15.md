# 新近邻补充：承诺、策略机会与原生行动（2026-10-15）

新检索和venue corpus用于校准问题空间，不作territory/idea去留判决。E59/E60是围绕已有角色矛盾的竞争解释实验，不能只凭“多步”“承诺”命名新贡献。

## Commitment To Cooperation With Self-Negotiated Contracts

- **来源：** [arXiv全文](https://arxiv.org/html/2607.22750)、[PDF](https://arxiv.org/pdf/2607.22750)；PDF页眉标Published as a conference paper at COLM 2026。作者Tim Wyse、Kaitlin Bustos、Yulia Volkova、Max Kleiman-Weiner。缓存 `~/.cache/game-npc-research/papers/self_negotiated_contracts.pdf/.txt`，PDF SHA256 `8dd45c0a5a1beb81cdf99766515aa6aa0337fe794820c04d01627950e55ef6dc`。
- **本次读取：** 正文环境/支付/合同/结果，Table1；附录C.3.2/C.4/C.5/C.6、Table9–11；D生成、E复现、G.1–3真实提示。不是只读摘要。合同示例其余小节与作者代码待进一步阅读。
- **论文事实：** CT-Bench是4×4空间博弈，玩家跨颜色格支付chip，按到达与剩余chip获得分数。Pay-for-Partner覆盖承诺非绑定，未来实际移动时对方可以不提供chip；不是单步矩阵。80个board、三依赖类型、六模型；主结果每board/config一次，GPT4.1附录5次×80×4共1600局重复。
- **已有机制与读数：** self-negotiated contracts三种表示；Prog-Trading/Points按结构化约定自动转账，NL-Trading由Qwen235B解释后同样执行，失败/缺货有处罚。各agent明确自利最大化，提供本人/对手best path及缺chip；因此动作选择与寻路能力分开。未来履行、互惠、依赖结构和first-mover效应已有ownership，不能称我们首次发现。
- **关键结果：** No-Contract平均normalized joint return .77，Prog-Trading .89；Mutually Dependent里NL与程序化合同虽覆盖相近tile，后续交易量不同。Table11异模型承诺履行和发起顺序差异；作者已有“自然语言合同过度锚定并抑制补充交易”的解释。Judge C.4核1155个approved move发现3个false positive；并非全部reject也校验的完整confusion matrix。
- **源码事实：** 论文E指向[匿名作者仓库](https://anonymous.4open.science/r/colored_trails-70A4)。web工具README不可访问；此处未读代码、未复现，不把论文描述冒充源代码审计。
- **解释/竞争解释：** 强制执行和惩罚改变commitment device，不能把“contract更有效”全当persona/自主守约改善。不同模型承诺差也可能受prompt/能力/互惠推理影响。游戏玩家明确自利与LIGHT人物含关系/道德/长期动机是不同构念。
- **与当前工作的距离：** 解释NPC人物信息如何改变采纳、取舍和手段仍可探索；“延迟承诺+资源依赖+实际执行”本身不新。E57持有与伙伴依赖线索不能包成首次依赖影响社会策略；E60普通明确未来句的作用也要与已知具体行动锚点定位。

## Persona Dynamics / PANDA

- **来源：** [ACL2025 Main](https://aclanthology.org/2025.acl-long.1515/)、[全文PDF](https://aclanthology.org/2025.acl-long.1515.pdf)。缓存 `papers/panda_acl2025.pdf/.txt`，SHA256 `1472f38b2e5947108ce6d737e5e05eaf8e7da934863e2a8f32bd625a8889ae4c`。正文§2–3、§5.2–5.4、§6部分及附录B/Table11–12已读；其余数据生成/完整结果附录待读。
- **论文事实：** DRRN action value上叠加性格classifier的高/中/低输出，16个高低人格配置，25个Jiminy Cricket文字冒险。Classifier用GPT4生成约120k性格数据，FlanT5XL训练；policy shaping weight2、8并行env、每start15000步。该classifier也用于主要人物动作比例评价，walkthrough另用GPT4标性格。原游戏score、访问位置、reward动作与内部trait比例均有报告。
- **解释：** 既有工作已展示人格适应能改变游戏动作和探索，不能把C02本身称新发现。其人格对动作标签映射及classifier塑形不是自然NPC的自身目标/社会互动，内部对齐与独立任务score要分开。
- **执行边界：** 本轮只精读，不恢复或训练PANDA/PCSP小模型RL，不重复奖励/分类器QA。官方代码 `pull-ups/PANDA` 未在本次审计读取，未称复现。

## 当前问题保持开放

NCP-Bench正文/代码此前已精读，见 `knowledge/papers/NCP_BENCH_2026.md`；其model审查叙事约束与native物理引擎不同，但长期承诺保存已有强结果。CDT、Story Shapes、Persona Circuits、Persona Vectors、PMBench/PASB/DREAM等ownership同样保留，不能因换成三阶段名称重新宣称首次。

有价值的剩余问题应从实际矛盾收敛：同一人物在相同社交承诺下是否仍选择不同目标；表现一致是否因合理协调/委托；知识与使用、语义模态和执行机会分别影响什么。E60全200图正在给出实体对照；后续内部干预需明确检验一个行为解释，不能只给向量夹角起机制名字。
