# Game NPC Agents — 游戏中的自主非玩家角色

**状态：PROPOSED；用户选定本轮优先矿区 A：人物设定、真实利益与战略行为的关系。** 全局ACTIVE状态不变；安全、人格漂移、社会互动和游戏经济仍开放。允许结果显示Persona对真实行动很有效。

**执行：2026-10-14用户已明确恢复，并下达科研审计与冻结指令。** 历史入口为 [进度报告](PROGRESS_REPORT_2026-10-14.md)；当前推进 [I04承诺冲突裁决](ideas/I04-commitment-conflict-stage-arbitration.md) 与 [E50决策快照](experiments/E50-commitment-decision-snapshots.md)。PCSP／MeltingPot小模型RL及其后续诊断停止追加；禁止1200帧全图漫游、只改conversation的总体人格实验、无实体完成判定的任务研究。全部历史证据保留。

## 当前研究动作

中心问题：面对具体请求、自身目标、角色规范、社会关系和游戏状态，人物设定怎样影响NPC的选择与实际后果？按用户最新纠偏，先横向研究LIGHT、E42与校园轨迹的成功/失败矛盾。阶段渠道与完成状态是诊断线索，不是钦定论文故事；依据实证发展解释和方法，不先规定GRPO／steering／新损失，也不用自设通过比例判科学价值。

- **跨环境矛盾：** 既有轨迹已拉通，见 [归因表](knowledge/persona-behavior/CROSS_ENVIRONMENT_CONTRADICTIONS_2026-10-15.md)。E42具体偏好提示提高收益但降低初始人设动作差；E22鸟自己台词改变原目标物品绑定。接下来区分目标可用性、绑定、优先级竞争与执行能力，而不是给仓库做QA。

- **原生决策切片：** E50 已得到 360 个不同 LIGHT source graph，各有原任务／请求的两条原生实体终点；40 pilot、200 confirm、120 reserve 固定拆分。32B 完成 40 图×三 seed 的一致人设实验，共 1680 分支／3183 调用。agreeable−firm 的实际请求转移差在完整渠道为 +13.3pp，图簇95%[4.2,23.3]；人设在真实行动上有效。
- **阶段与渠道：** 32B 的单 seed 2×2 阶段干预已完成；固定下游人设，conversation 人设的请求转移效应约 +15pp，固定 conversation 的下游合并效应约 +2.5pp。完整渠道低于 agenda-only；agreeable 渠道交互 −11.7pp，95%[−20.8,−2.5]。当前检查的是承诺如何传递及被重新裁决。
- **白盒与决定性下一实验：** 27B／32B 三阶段 residual 与统一 action 读出都已实测。32B conv–exec 方向 cos 从 .140 变为 .712，说明原输出粒度会大幅影响“耗散”解释。E51 已运行：固定计划、承诺、实体状态，仅改 pending/completed，再交叉原任务提醒与真实状态提示，区分完成状态误记和目标显著性。
- **数据：** 用户指定 Step5 用于数据构造／质检；仅 Step Plan，固定 step-5-preview。200 confirm 图的自然请求另存 v2，盲检不展示行为结果。NPC 决策和实体评价均本地，密钥不入 Git。最新认识见 [阶段裁决记录](knowledge/persona-behavior/STAGE_ARBITRATION_2026-10-15.md)。

以下是已封存的基线背景，历史过程见进度报告；不按旧“下一步”恢复执行。

- **原生NPC闭环：** ActionCastle／LIGHT已恢复。E35原三人校园世界三个自然episode各1200帧，129/129/166本地27B调用、5/5/8对话；首episode完整cassette独立回放一致。正向目标对应与地点/计划异常均保留，新增承诺超出episode边界的不记失败。E42两强模型与具体偏好提醒全部240个原生200cycle episodes完成，48000本地决策，无随机fallback。
- **PCSP完整预算：** E34正确编码、原作者300轮预算，三seed×Full／No全部完成（4608万原生transitions）。300轮Full局部人物利益响应三seed更强，完整游戏收益三seed较低。E41四种普通覆盖／绑定对照×三seed全300轮完成（9216万新增transitions），所有30／100／300阶段保留；结果不支持用一个方向概括全部收益，亦不包装成独立“利益控制”新题。
- **功能测量（冻结）：** E37／E39 分开测等义变化、属性编辑与原生收益方向，60000动作累计reward完成重建。按用户指令停止追加训练或诊断。
- **独立战略环境：** E38恢复原MeltingPot2.4.0／DMLab2D1.0.0；26次默认/强/正确编码训练与360完整原生episode均完成。正确码Full−No团队return−12.54、五seed簇95%[−38.52,13.43]，内部读取38.1%/6.9%，不同层次分别解释。PHASE5源码稀疏检出遗漏已纠正，作者独立读出路径完成数值审计。
- **自然角色测量（历史）：** E45–49 完成并在2026-10-14暂停收尾。E49复用三条自然历史，不将24后缀当24独立场景；校园讲课／画图文字不作实体完成判定。用户随后已恢复并要求关键决策切片重构。

[实验卡](experiments/) · [结果与校对](results/README.md) · [当前日志](logs/2026-10-15.md) · [I04阶段裁决](ideas/I04-commitment-conflict-stage-arbitration.md) · [主张账本](CLAIMS.md)。C02／C03 是有范围的 pilot 科学主张，下一步以独立 200 图与机制对照检验。

## 阅读与执行入口

[LOCAL_AGENT_START](LOCAL_AGENT_START.md) · [EXPLORATION_ENTRY](EXPLORATION_ENTRY.md) · [领域地图](knowledge/DOMAIN_ATLAS.md) · [人格—行为知识](knowledge/persona-behavior/) · [源代码审计](knowledge/persona-behavior/SOURCE_AUDIT_2026-10-14.md) · [强近邻定位](knowledge/persona-behavior/RELATED_WORK.md)。源代码事实、我们的解释与未排除的竞争解释分别记录。

不自动恢复已撤出的E00／E02–E05，不建立第二套工作台。优先原作者人物／目标／合法动作与实际后果；自述表达、特定场景意图和执行策略分开；抽象标签不对应唯一正确动作。

## 资产位置与重建

完整轨迹、checkpoint、模型输入输出保存在`/home/xiang/.cache/game-npc-research/runs/`，不进Git；E35完整三人轨迹在`e35_original_cast/`。模型复用HuggingFace缓存；上游源码在同缓存`sources/`，版本与hash见各结果manifest。原PCSP主pin5420f7b与MeltingPot隔离分支4fbbffa分别保留，不改运行中源码。

环境优先现有Conda／venv：NPC／Mini-Inzoi用fgvd＋deps overlay，MeltingPot用lightwam＋项目隔离overlay。用户已授权七节点全部GPU；07:00 Asia/Tokyo起本项目最多8卡，不干扰其他任务。核心链路零付费API，不允许SDK云端fallback。依据实际计算特点使用GPU；先原生完整episode再扩大。
