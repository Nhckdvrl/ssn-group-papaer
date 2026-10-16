# Game NPC Agents — 游戏中的自主非玩家角色

**当前执行暂停（2026-10-16用户决定）。** E85及此前已启动实验全部结束，自有worker/GPU释放，无待运行队列。当前只整理文档；恢复须用户明确指令。工作台PROPOSED、I04 PROMISING、C01–C06既有等级保持，论文正文暂缓。

**先读[整个项目的整体进度报告：从最初接手到E85](PROJECT_PROGRESS_REPORT_2026-10-16.md)。** 报告按研究问题组织全部阶段：为什么选实验、结果怎样改变判断、两次局部化与纠偏、对原始NPC问题的推进、未解决问题、成本及全部79张现存实验卡索引。[E85分报告](PROGRESS_REPORT_2026-10-16_PARTNER_PERFORMANCE.md)保留本轮完整设计与结果，不能代替整体报告。

## 中心问题

有自身身份和目的的NPC，面对玩家提出的合作办法、实际履约和条件变化，怎样形成、修订或拒绝方案，并以合法行动产生有意义的游戏后果？当前优先矿区A：人物设定、真实利益与战略行为；安全、人格漂移、社会互动和游戏经济仍开放。

## 当前已有的认识

- **人物确实影响真实行动。** E55独立200图、三seed、三个模型的实际请求交付差为6.7–13.7pp；完整角色立场并非纯Big Five，“友善更愿给物”是可靠起点。
- **当前任务与人物差异可以共存。** C04包含独立其他物品图确认；任务完成率依模型/任务变化，不是人格与完整效用数学独立。
- **任务分数混合推进与用途。** E70–E77显示必要动作更多、请求交付更多和自身任务得分可以不同向；C06限定L2，没有统一两模块守恒机制。
- **普通系统已有真实合作能力。** E81–E85有交换、条件借用、继续帮助、拒绝和返还；仍需理解这些行动能否持续服务本人目的，而非只跟随近期话语或物品。

这些认识、被推翻的解释及证据范围见[整体报告§4–12](PROJECT_PROGRESS_REPORT_2026-10-16.md)、[CLAIMS](CLAIMS.md)。新颖性按整体认识/方法判断，不要求每个组件首创，不以自设bar自动关闭idea。

## 最近完成：从双方目的到玩家实际行动

| 实验 | 当前结果与范围 |
|---|---|
| [E81](experiments/E81-authored-cooperation-and-partner-response.md) | 双方作者任务126图/504局，普通系统可真实交付、取得及替代帮助。 |
| [E82](experiments/E82-minecraft-original-cooperation-baseline.md)／[E83](experiments/E83-npc-quest-receipt-and-reward-baseline.md) | 原Minecraft CPU多步见证；单角色两条本地模型重建路径，最终交换但有提前/重复奖励，亦能拒借。未作跨游戏总体确认。 |
| [E84](experiments/E84-independent-goals-and-alternative-cooperation.md) | 32原任务对/23图、128局；实际交换、条件借用、继续求药、拒绝及未落实方案同时保留。 |
| [E85](experiments/E85-partner-performance-and-revision.md) | 18自然前史/9图、576分支；真实转移未统一增加GiveY；同首回应后Qwen新返还+30.56pp [19.44,40.74]。216事实问答不稳定，不当内部信念。 |

尚未解决的是：同一目的下，玩家用合法替代办法实现前提、或原方案真正失效时，NPC能否理解新贡献、保持目的并落实新办法。这里只保存未解关系，没有新实验队列或预定方法。

## 分阶段原始报告

- [10月14日：E07–E49](PROGRESS_REPORT_2026-10-14.md)：原生闭环、PCSP、校园；历史状态按当时阅读。
- [E50–E62](PROGRESS_REPORT_2026-10-15.md)：一致人设、独立确认、普通解释与白盒正负结果。
- [E63/E64](PROGRESS_REPORT_2026-10-15_POST_REVIEW.md)、[E65/E66](PROGRESS_REPORT_2026-10-15_CONSTRAINT_PROBES.md)、[E67/E68](PROGRESS_REPORT_2026-10-15_RULE_EXECUTION.md)、[E69](PROGRESS_REPORT_2026-10-15_MATCHED_TASKS.md)：任务/合作、规则与实体后果、独立图及任务类型。
- [E70–E80连续报告](PROGRESS_REPORT_2026-10-15_REQUEST_PRECONDITIONS.md)、[E74–E76分报告](PROGRESS_REPORT_2026-10-16.md)：前提、用途与强执行基线。
- [E85分报告](PROGRESS_REPORT_2026-10-16_PARTNER_PERFORMANCE.md)：玩家实际转移、声称、后续补交与修订。

## 明确冻结的旧执行

PCSP/MeltingPot小模型RL及追加诊断、校园1200帧漫游、局部修改冒称总体persona、无实体flag履约、Step细语义打标和无回路假说的patch网格，均不自动恢复。E43原小MLP卡未运行；LLM白盒见E50/E52/E62。E00/E02–E05已撤出当前目录；E78/E79没有实际实验结果。冻结执行不等于关闭整个研究领域或修改idea状态。

## 入口、资产与资源边界

[AGENTS](AGENTS.md) · [LOCAL_AGENT_START](LOCAL_AGENT_START.md) · [EXPLORATION_ENTRY](EXPLORATION_ENTRY.md) · [主张账本](CLAIMS.md) · [idea现状](ideas/README.md) · [痛点](PAIN_LOG.md) · [领域地图](knowledge/DOMAIN_ATLAS.md) · [知识索引](knowledge/README.md) · [结果索引](results/README.md) · [最新日志](logs/2026-10-16.md)。

完整raw、模型/权重、世界状态在`/home/xiang/.cache/game-npc-research/`，不进Git；各实验卡/manifest给源数据、模型与driver pin、启动/退出成本和复算脚本。GitHub轻量结果不等于raw已异地备份。成本按整体报告分段列，没有编造全历史精确总账。

恢复后优先复用现有Conda/venv与模型缓存，先核节点实际空闲、不干扰其他任务；独立单卡/单节点优先，白天最多8卡。NPC/伙伴/教师/实体裁判核心链路本地、零付费推理API；另获授权的Step5仅作数据且限定Token Plan端点。当前暂停，不据资源授权自动启动。
