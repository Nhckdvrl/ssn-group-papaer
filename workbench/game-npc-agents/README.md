# Game NPC Agents — 游戏中的自主非玩家角色

**状态：PROPOSED；用户选定本轮优先矿区 A：人物设定、真实利益与战略行为的关系。** 全局ACTIVE状态不变；安全、人格漂移、社会互动和游戏经济仍开放。允许结果显示Persona对真实行动很有效。

**执行：E74进行中，E70–E73全部完成，暂缓论文正文。** 最新入口为[执行前提与请求报告](PROGRESS_REPORT_2026-10-15_REQUEST_PRECONDITIONS.md)；此前见[E69同图任务报告](PROGRESS_REPORT_2026-10-15_MATCHED_TASKS.md)、[E67/E68报告](PROGRESS_REPORT_2026-10-15_RULE_EXECUTION.md)、[E65/E66报告](PROGRESS_REPORT_2026-10-15_CONSTRAINT_PROBES.md)、[E63/E64报告](PROGRESS_REPORT_2026-10-15_POST_REVIEW.md)、[E50–62报告](PROGRESS_REPORT_2026-10-15.md)、[10月14日报告](PROGRESS_REPORT_2026-10-14.md)。当前[I04](ideas/I04-commitment-conflict-stage-arbitration.md)、[原生结果综合](knowledge/persona-behavior/NATIVE_ROLE_RESULTS_2026-10-15.md)。PCSP／MeltingPot小模型RL及其后续诊断停止追加；禁止1200帧全图漫游、只改conversation的总体人格实验、无实体完成判定的任务研究。全部历史证据保留。

## 当前研究动作

- **E74进行中：** 全117作者Give图、两人物三seed两模型，独立物理后果预测＋自产预测/原生真值同格式替换后实际执行；不将预测当内部信念。819原生反事实/1404输入CPU核对通过，固定首世界成本profile先行。定位见[当日近邻校准](knowledge/persona-behavior/BELIEF_CHOICE_POSITIONING_2026-10-16.md)，[实验卡](experiments/E74-physical-consequence-prediction-and-choice.md)。

- **E70–E73完成：** 同117原作者Give图、两模型/三seed，23868分支/125126本地调用/2解析失败（保留）/12.847GPUh，峰值8卡、0API。32B冲突下人物原任务效应ready −6.84pp、equipped +5.41pp；普通机制事实恢复大部分交付，单纯priority无同等恢复。E71无人索要亦有前提困难，请求方向可促进/妨碍原任务。
- **固定对话后的信息控制：** E72对称扩展A/B命令候选，E73保留原生菜单、预先统一给真实引擎操作事实，均大幅恢复。E73冲突下原任务F/A：Gemma56.4/70.7%、32B77.8/80.1%；人物差仍有联合去向差异，不能直接推成私人效用权重。C06限定L2，I04 PROMISING；所有模型job完成，无新增队列。见[报告与复算入口](PROGRESS_REPORT_2026-10-15_REQUEST_PRECONDITIONS.md)。

- **E69完成：** 112同图任务配对＋3个源案例，2760主分支/144适应性控制/27519新增调用，2.828GPUh、0API，GPU已释放。任务人物交互Gemma +4.17pp [0.00,8.33]、32B +6.25 [2.08,10.71]；Duty-Give约98%–99%完成且保留接收者A，未跨模型出现完整正负反转。补共同窗口没有新增顺序完成；单句机制知识在32B恢复5/36双事件，Gemma0/36但17条真实卸下。不将三个案例当总体机制、不把goal交互当动词回路。C04/C05仍限定L2，I04 PROMISING。

中心问题：面对具体请求、自身目标、角色规范、社会关系和游戏状态，人物设定怎样影响NPC的选择与实际后果？按用户最新纠偏，先横向研究LIGHT、E42与校园轨迹的成功/失败矛盾。阶段渠道与完成状态是诊断线索，不是钦定论文故事；依据实证发展解释和方法，不先规定GRPO／steering／新损失，也不用自设通过比例判科学价值。

- **E67/E68完成：** 15108新执行/51631本地调用/6.556GPUh（含中断），GPU已释放。E67执行规则恢复在E68独立41装备图复现：固定asset上游换generic执行，Gemma F/A原goal +27.6/+36.6pp，32B +8.9/+13.0pp。60个其他物品图人物交付差+10.0/+38.3pp、同轨迹both亦增加；Gemma任务约81%–82%，32B约99%。32B纯否定未复现强阻挡/降低交付的统一分流。C04/C05 L2，见[预测完整读数](results/E68_prediction_readout.md)与[混杂核对](knowledge/persona-behavior/EXECUTION_RULE_CLAIM_AUDIT_2026-10-15.md)；0API，不追加盲网格。

- **E65/E66完整结果：** 79原生wear/wield图，2370新轨迹、1896两模型动作概率上下文，1.196GPUh/15630本地生成调用，0API/训练/patch，GPU已释放。否定相对肯定式保有使实际goal F/A降低7.2/9.7pp，同时合法block增加约14pp；许可恢复取决于人设/任务/规则包。固定原计划和记忆换任务优先规则，使Gemma/32B目标命令概率提高17.6/12.6pp；直接效应记C05 L1。C04共存范围核对记L2，I04按人审PROMISING；暂缓正文。

- **E63/E64完整结果：** [E63](experiments/E63-native-dependency-and-explicit-priority.md)三模型各200原图、100其他资产配对、5400 episode收齐。一般任务优先使agreeable原goal完成32B60.8→90.0%、27B78.5→93.0%；Gemma资产规则反而76.8→52.8%。非冲突合作及可行计划采纳分开测；资产比较另对齐原goal前交付窗口，不把总交付差直接归因工具价值。196图交目标物后原任务暂时不可执行、4图有替代物，全部可合法偷回。[E64](experiments/E64-native-reciprocal-goal-negotiation.md)两Qwen各9独立图/108条，另32B通信控制54条，死亡/失败保留。全轮含profile/中断13.167GPUh、104883本地调用、0新增API/训练/内部干预，全部本轮worker退出。原子goal与完整私人利益分开，该轮未升级神经机制；最新人审认可I04为PROMISING，E65/E66已完成。

- **跨环境矛盾：** 既有轨迹已拉通，见 [归因表](knowledge/persona-behavior/CROSS_ENVIRONMENT_CONTRADICTIONS_2026-10-15.md)。E42具体偏好提示提高收益但降低初始人设动作差；E22鸟自己台词改变原目标物品绑定。接下来区分目标可用性、绑定、优先级竞争与执行能力，而不是给仓库做QA。

- **原生决策切片：** E50得到360个不同LIGHT图，40 pilot／200 confirm／120 reserve固定。三模型各1680完整分支；完整渠道agreeable−firm的实际请求转移差：32B +13.3pp [4.2,23.3]、27B +5.0pp [0,10.8]、Gemma +9.2pp [3.3,16.7]。人设在真实行动上有效。
- **阶段与渠道：** 32B 的单 seed 2×2 阶段干预已完成；固定下游人设，conversation 人设的请求转移效应约 +15pp，固定 conversation 的下游合并效应约 +2.5pp。完整渠道低于 agenda-only；agreeable 渠道交互 −11.7pp，95%[−20.8,−2.5]。当前检查的是承诺如何传递及被重新裁决。
- **机制诊断：** 三阶段白盒没有共同单调耗散；E52单一鸟案例中，32B自己台词worm→nut使eat从6/32到27/32，31层词位patch为21/32、sham6/32。27B patch与随机都28/32，机制未统一。E53三个模型全部40图×三seed完成；不同状态记录可改变人物效应，外加记录不等于自然错误频率。
- **独立确认与解释：** 三个模型各200不同confirm世界×三seed/5600完整分支；实际请求人物差32B13.7pp [9.7,17.8]、27B8.5pp [5.7,11.7]、Gemma6.7pp [4.3,9.3]。E56普通阶段结束解释大量无动作；E57两强模型39原世界动态伙伴互动，E58分量、E59同未来记录、E60/E61共2400完整原生分支均完成。E62三模型各4896原生选择/2448概率读出完成；同未来承诺的参数角色差1.47/5.88/0pp，单层donor无统一定向控制。固定动作族诊断与自由NPC行为、完整私有利益分开。
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

环境优先现有Conda／venv：NPC／Mini-Inzoi用fgvd＋deps overlay，MeltingPot用lightwam＋项目隔离overlay。用户已授权七节点全部GPU，07:00 Asia/Tokyo起最多8卡；本轮采用全时≤8，不干扰其他任务。NPC/模拟伙伴/物理判定全部本地，无SDK云fallback；用户单独授权Step5数据用途，只走Token Plan、不走现金端点。实际分项成本见本轮报告与结果账本。
