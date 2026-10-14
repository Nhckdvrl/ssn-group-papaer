# Game NPC Agents — 游戏中的自主非玩家角色

**状态：PROPOSED；用户选定本轮优先矿区 A：人物设定、真实利益与战略行为的关系。** 全局ACTIVE状态不变；安全、人格漂移、社会互动和游戏经济仍开放。允许结果显示Persona对真实行动很有效。

**执行：用户已恢复，并要求2026-10-15继续按大问题探索。** 历史入口为 [进度报告](PROGRESS_REPORT_2026-10-14.md)；当前推进 [I04人物设定与决策](ideas/I04-commitment-conflict-stage-arbitration.md)、[E54自然文本标注](experiments/E54-natural-dialogue-data-labels.md) 、[E55独立原生确认](experiments/E55-independent-native-role-confirmation.md) 与 [E57原任务互动](experiments/E57-native-private-goal-interaction.md)。PCSP／MeltingPot小模型RL及其后续诊断停止追加；禁止1200帧全图漫游、只改conversation的总体人格实验、无实体完成判定的任务研究。全部历史证据保留。

## 当前研究动作

中心问题：面对具体请求、自身目标、角色规范、社会关系和游戏状态，人物设定怎样影响NPC的选择与实际后果？按用户最新纠偏，先横向研究LIGHT、E42与校园轨迹的成功/失败矛盾。阶段渠道与完成状态是诊断线索，不是钦定论文故事；依据实证发展解释和方法，不先规定GRPO／steering／新损失，也不用自设通过比例判科学价值。

- **跨环境矛盾：** 既有轨迹已拉通，见 [归因表](knowledge/persona-behavior/CROSS_ENVIRONMENT_CONTRADICTIONS_2026-10-15.md)。E42具体偏好提示提高收益但降低初始人设动作差；E22鸟自己台词改变原目标物品绑定。接下来区分目标可用性、绑定、优先级竞争与执行能力，而不是给仓库做QA。

- **原生决策切片：** E50得到360个不同LIGHT图，40 pilot／200 confirm／120 reserve固定。三模型各1680完整分支；完整渠道agreeable−firm的实际请求转移差：32B +13.3pp [4.2,23.3]、27B +5.0pp [0,10.8]、Gemma +9.2pp [3.3,16.7]。人设在真实行动上有效。
- **阶段与渠道：** 32B 的单 seed 2×2 阶段干预已完成；固定下游人设，conversation 人设的请求转移效应约 +15pp，固定 conversation 的下游合并效应约 +2.5pp。完整渠道低于 agenda-only；agreeable 渠道交互 −11.7pp，95%[−20.8,−2.5]。当前检查的是承诺如何传递及被重新裁决。
- **机制诊断：** 三阶段白盒没有共同单调耗散；E52单一鸟案例中，32B自己台词worm→nut使eat从6/32到27/32，31层词位patch为21/32、sham6/32。E53的32B直接决策40图×三seed已完成：原人物差+11.7pp [4.2,20.0]，不同任务执行状态记录可放大或压平人物差；E54检查这些语义在自然文本中多常见，E55以普通一句事实指令为强对照。
- **独立确认与解释：** 200新世界×三seed，32B/Gemma各5600完整分支；实际请求人物差+13.7pp [9.7,17.8]/+6.7pp [4.3,9.3]。E56阶段结束一句恢复大量原目标行动，接受普通指令范围解释；数值与下一步见 [综合结果](knowledge/persona-behavior/NATIVE_ROLE_RESULTS_2026-10-15.md)。E57已启动39原世界的双私有目标/动态伙伴/不可逆消费，两强模型全部三seed。
- **数据与近邻：** Step5完成200 confirm自然请求构造；盲检不展示行为结果，澄清盲检185保留／14复核／1拒绝，全部200为主表；[派生请求与QC](results/E55_natural_requests.jsonl)已公开。E54全部720文本盲标注完成。NPC和实体评价均本地；Step仅Plan做数据，密钥不入Git。已核读 [五篇机制近邻](knowledge/persona-behavior/MECHANISTIC_NEIGHBORS_2026-10-15.md)，人格信号竞争、情境加权和角色信念分离均已有owner。

以下是已封存的基线背景，历史过程见进度报告；不按旧“下一步”恢复执行。

- **原生NPC闭环：** ActionCastle／LIGHT已恢复。E35原三人校园世界三个自然episode各1200帧，129/129/166本地27B调用、5/5/8对话；首episode完整cassette独立回放一致。正向目标对应与地点/计划异常均保留，新增承诺超出episode边界的不记失败。E42两强模型与具体偏好提醒全部240个原生200cycle episodes完成，48000本地决策，无随机fallback。
- **PCSP完整预算：** E34正确编码、原作者300轮预算，三seed×Full／No全部完成（4608万原生transitions）。300轮Full局部人物利益响应三seed更强，完整游戏收益三seed较低。E41四种普通覆盖／绑定对照×三seed全300轮完成（9216万新增transitions），所有30／100／300阶段保留；结果不支持用一个方向概括全部收益，亦不包装成独立“利益控制”新题。
- **功能测量（冻结）：** E37／E39 分开测等义变化、属性编辑与原生收益方向，60000动作累计reward完成重建。按用户指令停止追加训练或诊断。
- **独立战略环境：** E38恢复原MeltingPot2.4.0／DMLab2D1.0.0；26次默认/强/正确编码训练与360完整原生episode均完成。正确码Full−No团队return−12.54、五seed簇95%[−38.52,13.43]，内部读取38.1%/6.9%，不同层次分别解释。PHASE5源码稀疏检出遗漏已纠正，作者独立读出路径完成数值审计。
- **自然角色测量（历史）：** E45–49 完成并在2026-10-14暂停收尾。E49复用三条自然历史，不将24后缀当24独立场景；校园讲课／画图文字不作实体完成判定。用户随后已恢复并要求关键决策切片重构。

[实验卡](experiments/) · [结果与校对](results/README.md) · [当前日志](logs/2026-10-15.md) · [I04阶段裁决](ideas/I04-commitment-conflict-stage-arbitration.md) · [主张账本](CLAIMS.md)。C02已由独立200图确认至L2；C03保持范围明确的pilot。依据动态伙伴、原生前置条件与实体后果继续研究角色选择，不预定失效故事。

## 阅读与执行入口

[LOCAL_AGENT_START](LOCAL_AGENT_START.md) · [EXPLORATION_ENTRY](EXPLORATION_ENTRY.md) · [领域地图](knowledge/DOMAIN_ATLAS.md) · [人格—行为知识](knowledge/persona-behavior/) · [源代码审计](knowledge/persona-behavior/SOURCE_AUDIT_2026-10-14.md) · [强近邻定位](knowledge/persona-behavior/RELATED_WORK.md)。源代码事实、我们的解释与未排除的竞争解释分别记录。

不自动恢复已撤出的E00／E02–E05，不建立第二套工作台。优先原作者人物／目标／合法动作与实际后果；自述表达、特定场景意图和执行策略分开；抽象标签不对应唯一正确动作。

## 资产位置与重建

完整轨迹、checkpoint、模型输入输出保存在`/home/xiang/.cache/game-npc-research/runs/`，不进Git；E35完整三人轨迹在`e35_original_cast/`。模型复用HuggingFace缓存；上游源码在同缓存`sources/`，版本与hash见各结果manifest。原PCSP主pin5420f7b与MeltingPot隔离分支4fbbffa分别保留，不改运行中源码。

环境优先现有Conda／venv：NPC／Mini-Inzoi用fgvd＋deps overlay，MeltingPot用lightwam＋项目隔离overlay。用户已授权七节点全部GPU；07:00 Asia/Tokyo起本项目最多8卡，不干扰其他任务。核心链路零付费API，不允许SDK云端fallback。依据实际计算特点使用GPU；先原生完整episode再扩大。
