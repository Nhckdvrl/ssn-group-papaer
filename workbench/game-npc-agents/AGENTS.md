# Game NPC 科研 Agent 指南｜开放领域、自主发现、绝不先锁结论

继承根 AGENTS、workbench/EXECUTION。**2026-10-14 用户再次纠正：NPC领域不仅是目标/旧计划，也不仅是训练可控政策；安全、人格漂移、游戏经济、多NPC攻击与社会效应必须正式纳入。** 不能用旧 README 或实验卡重新锁死领域。PROPOSED状态/ACTIVE名额仅由用户变动。

## 2026-10-14 用户新决定：先进入矿区 A

用户明确选择 **Persona 与游戏中的真实利益/战略行动** 为当前探索焦点。**先读 [LOCAL_AGENT_START.md](LOCAL_AGENT_START.md) → [knowledge/persona-behavior/RELATED_WORK.md](knowledge/persona-behavior/RELATED_WORK.md) → [CODE_AUDIT.md](knowledge/persona-behavior/CODE_AUDIT.md) → [EXPLORATION_ENTRY.md](EXPLORATION_ENTRY.md) → [E06](experiments/E06-persona-strategy-baseline.md)**，然后回到 [DOMAIN_ATLAS](knowledge/DOMAIN_ATLAS.md) 和相关领域。不得忽略 ICML2026 *Personality Illusion*、2026 *Rethinking Psychometric*、*Story Shapes the Agent*、PCSP 已有的研究。全域 NPC 安全/经济/记忆方向保留，A 的用户授权仅限当前科研探索，非永久缩小整个 workbench。

## 每次接手优先阅读

**2026-10-16用户新增要求：每次启动实验前，必须判断是否在局部优化、追逐局部现象。** 在实验卡写明：它回答原始中心问题的哪一部分、不同结果会改变什么研究判断、为什么不是上一例的提示/接口/指标微调；同时写最实际的局部化风险及如何从完整结果识别。扩大N、换模型/任务或增加条件本身不算研究价值。判断服务研究选择，不新增人为通过bar、不替人关闭idea，也不把必要的强基线驻留包装机制贡献。

**2026-10-16最新E85已完成：** 全E84资格18前史/10任务对/9图、两模型两seed576逻辑分支/216独立事实问答；13,452已记录本地calls/2.04614占卡GPUh、0API，四worker已退出，2782统计字段独立一致。真转移未统一增加GiveY；同一首回应后撤回使Qwen后续新GiveX +30.56pp [19.44,40.74]，Gemma −7.41 [−20.37,0]。响应玩家会后来真补Give，Drop/Put也可释放可用资源；读真实时序与原目的，不用交换率概括人格/利益。两字段事实问答不一致，未被当行动信念。原状态兼容修复、全部失败/cost/cache lineage保留，最终outcome仅四recover目录；下方E85运行中/历史0队列说明按时间读。下一对象是原生多步任务中原手段/合法替代/手段失效后的目标保持与方案修订，先选真实任务，不机械新提示/训练或状态升级；I04/C06/全局状态保持，正文暂缓。

**2026-10-16当前已获用户明确推进授权：** [E81](experiments/E81-authored-cooperation-and-partner-response.md)全126双作者原图/504逻辑episode完成（16611本地calls/3.45956GPUh）；[E82](experiments/E82-minecraft-original-cooperation-baseline.md)原Minecraft资源交接→书架制作CPU链已完成；[E83](experiments/E83-npc-quest-receipt-and-reward-baseline.md)原paper-role归还/奖励重建切片2完整episode/16本地请求及独立物理读回完成。两路径最终交换但提前奖励/重复结清，P1也能拒借；单角色不当总体机制。[E84](experiments/E84-independent-goals-and-alternative-cooperation.md)全32对/23图×两seed×两模型128完整episode完成，4224本地calls/0.75834完整占卡GPUh，全部输入/typed事件/全世界重放PASS，0云/Step/API；本轮server/GPU已全部释放。普通32B已能实际帮忙后有条件借刀、连续响应求药，Gemma也有真实帮助与合理拒借。读[完整方案和后续](results/E84_grounded_plans_POST_HOC.json)，不将原Steal/Put标签或双向Give当合作/完整利益；未送达的choice.utterance不当对话承诺。当前0新队列，先根据玩家真实行动/改方案会改变什么判断作下一次立项检查；不围几例提示优化、不预定方法或擅改I04/C06状态。

**2026-10-16用户再次质疑研究尺度：** 已承认E80仍沿用同类物品索要，应用审计没有充分改变实验优先级。先读README“当前证据与研究判断”。不要将“用途采纳/执行/修订”再细分就视为科学推进；后续证据围绕NPC自身目的、玩家不同合作办法与真实后果的关系判断价值，已有可靠执行与测量作为底座。不新增同类提示/动作分解队列，不凭相关工作关闭idea或擅改状态；正文仍暂缓。本次复盘0新增模型/GPU/API调用。

**2026-10-16最新完成：** E80固定200原held源图、两trait/三seed/两执行器/两模型共4800episode全部完成，37642本地调用/3.61979观测GPUh/峰8卡/0API，fvcrc20/21全部本轮槽释放。读[E70–E80连续报告](PROGRESS_REPORT_2026-10-15_REQUEST_PRECONDITIONS.md)与[E80卡](experiments/E80-responsive-player-and-grounded-execution.md)。主全图A−F Give+10.50/+12.83pp，绑定goal−9.00/−12.50pp；技能首共同前提实现显著恢复而总体goal仅+.17/+.50pp，不能直接归为潜在能力。原子goal不等于作者全部目的；支付/腾手等合法替代行动已出现。0新增队列，不机械E81或刷提示。首完整记录优先的恢复/原生歧义、prefix不合格对及计数修正公开；原raw和所有失败保留。C06 L2/I04 PROMISING/全局PROPOSED不变，正文暂缓。E78/E79是旧未来引用非漏失运行。

**2026-10-16最新完成：** E77全102图/两模型/三seed/4896逻辑记录完成，1224旧对角＋3672新增分支，17375新本地调用/2.15314观测GPUh/0解析/API，worker及GPU已释放，不重复启动。[E70–E77连续报告](PROGRESS_REPORT_2026-10-15_REQUEST_PRECONDITIONS.md)已追加完整结果与新应用审计。非Give推进差更随C来源变化，当前trait仍改变用途；Gemma Give固定C仍有直接推进效应，明确终局没有统一修复所有目标，不改写为二模块定律或能力等价。原事件/物理消费并报、全部失败保留。C06 L2/I04 PROMISING不变。

用户新的应用审计仅供参考：完成当前E77后先把真实玩法、强现有规则/可靠技能与玩家证据纳入判断，不机械续开E78–80。先读PLAYABLE_NPC_APPLICATION_AUDIT与PLAYER_VALUE_EVIDENCE两笔记；研究整体novelty与中心问题保留，分析不必强行变方法/人评。下一项数据应解释玩家提出、回应或改变条件后NPC的选择和兑现，而非再调Get/Remove提示；暂无新实验队列、训练或新平台，论文仍暂缓。

**2026-10-16前轮（历史）：** 先看[完整报告](PROGRESS_REPORT_2026-10-16.md)。E74–E76全部完成：29125调用/8928新增物理分支/2808预测/208不同源图/3.83553观测GPUh、0API，所有本轮worker退出。人物同时影响推进与用途；E76固定C后非Give Gemma任务交互−21.51pp[−37.63,−6.45]、32B0[−11.83,11.83]。I04 PROMISING、C06 L2、正文暂缓；下一项区分目标/等待价值与已选目标实现，不自动启动提示/patch网格。novelty按整体问题与证据链判断，不要求每组件无人做过。已精读七篇近邻，未启动新平台移植。

**最新完成（2026-10-15）：** 先读[E70–E73完整报告](PROGRESS_REPORT_2026-10-15_REQUEST_PRECONDITIONS.md)。117源作者Give图、23868分支/125126新本地调用/2解析失败保留/12.847GPUh；峰值8卡，0API/训练/patch。相同任务下32B人物效应随ready/equipped换向；固定本人对话，扩展候选或预先给真实引擎操作信息均恢复大量交付，E73后仍需结合向A/向B/未交的联合分布解释人物作用。C06限定L2，I04 PROMISING、全局PROPOSED；正文暂缓。全部worker已完成，无新增队列，不自动扫提示、训练或恢复旧线。下列“最新”段落按历史阅读。

**最新工作（2026-10-15）：** [E69](experiments/E69-matched-task-and-motivation-window.md)2760主分支＋144适应性控制全部完成，先读[同图任务报告](PROGRESS_REPORT_2026-10-15_MATCHED_TASKS.md)。112图人物×任务交互成立但完整正负反转未跨模型成立，职责Give约98%–99%且接收者保留；3世界补窗仍无双事件，机制事实在32B恢复5/36双事件、Gemma0/36但17条卸下。27519新调用/2.828GPUh/0API，job和watcher均退出。C04/C05仍限定L2，I04 PROMISING；正文仍暂缓，不因外部审计自动定词汇神经机制或封账。原始图、失败与所有seed保留。

**最新用户决定与完成状态（2026-10-15）：** 授权的[E67真实执行交叉](experiments/E67-stage-rule-physical-cross-swap.md)与[E68独立世界预测](experiments/E68-clean-reserve-rule-predictions.md)已全部完成，先读[本轮完整报告](PROGRESS_REPORT_2026-10-15_RULE_EXECUTION.md)。15108分支/51631本地调用/6.556GPUh，0API，worker均退出。执行规则恢复跨两模型、独立41装备图复现；60其他物品图保留人物合作差，但Gemma任务水平约81%–82%。统一三向分流未成立，32B纯否定未降低请求Give。C04/C05 L2、I04 PROMISING、全局PROPOSED；论文仍暂缓，不自动追加措辞网格或训练。

**2026-10-15进度报告后用户再审计：** 不把Agreeable比Firm多给物品本身当独立贡献。停止新增Step语义细分/时态标注；禁止没有具体回路假说的单层patch网格。本轮固定任务为[I04](ideas/I04-commitment-conflict-stage-arbitration.md)的[E63任务资产与明确规则](experiments/E63-native-dependency-and-explicit-priority.md)、[E64双角色有代价谈判](experiments/E64-native-reciprocal-goal-negotiation.md)，收尾后见[复审报告](PROGRESS_REPORT_2026-10-15_POST_REVIEW.md)。E58第二句是一般责任表态，不是明确排他规则；“迎合式自毁/预训练先验绕过推理”只是待检验解释。原子goal、资产持有与完整私人利益分开，交付后恢复路径与敌对角色的攻击后果保留，不改世界使结论成立。

**2026-10-15用户再次纠偏：** 双信道/TCE/SFR方案过早收窄成特定架构，不能作为钦定故事。围绕“人物设定、自身目标与社交互动怎样共同决定真实行动”，先拉通已有LIGHT/E42/校园成功失败；用可检验隐藏变量解释矛盾，再精确反事实和LLM内部干预。PCSP小MLP与旧E43不再启动；LLM白盒已在E50/E52实际执行。Step5明确只用于数据构造、质检及文本标注，固定Token Plan端点，禁止让它替我们写科研审计。最新工作见I04、E50–60及当前日志；当前结果汇总为knowledge/persona-behavior/NATIVE_ROLE_RESULTS_2026-10-15.md。

**最新用户决定覆盖下方历史暂停：** 2026-10-14用户明确说“继续”，恢复矿区A，按用户科研审计重构。冻结PCSP/MeltingPot小模型RL（不得追加seed），停止全图1200帧漫游和无实体flag的履约任务；总体persona效应采用全阶段一致人设，阶段交叉仅作为明确标注的机制干预。优先≥200个独立源场景的短决策切片、本地LLM跨阶段白盒和免费opencode盲检。研究主线/ACTIVE分配不自动改变。

**2026-10-14执行更新：** 用户要求本轮分析结束后暂停新增实验。先读 [进度报告](PROGRESS_REPORT_2026-10-14.md) 和最新结果；除本轮已启动任务的收尾／核对外，不自动启动实验，等待用户恢复指令。E07–E49已有真实本地执行，旧“当前尚未运行”不代表现状；E06仅统领设计，E43与E42额外对照未执行。暂停算力不等于关闭研究线，idea与全局状态不擅改。
依照上面 A 的入口，结合 [knowledge/README.md](knowledge/README.md)、BASELINES、LOCAL_FIRST、最新 logs 与 CLAIMS/PAIN_LOG 阅读；原论文与源码优先于历史旧“current”说明。

## 最重要的是判断力，而不是执行清单
- **2026-10-16用户再次强调：以整体问题、叙事和证据链评估novelty，不要求每个组件前所未有。** 强近邻用于理解和定位，不能逐组件过度压缩自有主张；持续从NPC人设、自身目标与社交请求的大问题审视实验，避免缩成局部操作/提示优化。结果若能统一解释既有矛盾、加深理解或导出有用新方法，应围绕这份整体增量推进。
- 你不只是做既定 E## 的执行者：持续跨方向读论文，维护领域画像，结合新工作与真实执行重新评价优先级；用户的研究空间不是我们上一次写的某个方法名字。
- **对象必须是游戏 NPC 本身**。Player Agent通关、Chatbot roleplay、通用电子商务/银行工具agent都只是邻接。它们的能力/漏洞不能自动声称在游戏角色上已成立。
- 不能因为问题已有人做就关掉；不能因为某一方法可运行或数据便宜就强行把它当好问题。最近顶会强认识和游戏制作者/玩家关心的真实性必须一起考虑。
- 对“安全”务必先定义攻击者控制、角色/世界授权、违反什么可玩规则与真实后果，**不要把侦探成功诱供/剧情允许撒谎当作违规**。合法社会欺骗与越权攻防分开。
- 对“人格漂移”先分时间尺度与信念来源，**不要把合理人物成长当漂移**，更不能用只看语气的judge给动作系统写通用结论。
- 对“经济攻击”先明确库存/货币守恒、游戏制度与玩家策略，**不要把正常价格浮动/竞争获利自动算系统不安全**。区分交易结构、普通代理消息与游戏引擎权威。
- 对方法和RL，不先给每个分支硬插LoRA、GRPO或Memory；从强现有系统真实弱点出发，才决定分析、训练、benchmark还是系统论文。
- 精读时记录 DOCUMENTED（文中/作者公开回顾）与 RECONSTRUCTED（我们的猜想）。尤其追踪 idea 来源、方法为何自然、实验区分什么竞争解释及 related work ownership。多数论文用的是API，应独立核验是否真可本地替代。

## 实验和评价纪律
- 优先现有自然游戏、真实角色/交易系统或游戏原生动作日志。若自构对照场景，先说明它弥补了哪个真实缺口；10-20条只做流程检查，不能证明普遍现象。
- 记录 player vs NPC vs engine vs judge vs simulated partner、秘密/角色状态的作者许可、玩家可见观察；绝不让同一个自造评分器制造自己想要的阳性。
- 高信息量不是配置多：先观察自然样例和准确读数，想清楚不同结果怎样改变研究判断，再做合法反事实/统计和未见确认。确保正常玩法任务能力、攻击成功率/防御误阻、玩家体验与经济系统结果分别报告。
- 旧 E00/E02/E03/E04/E05 **从未完成游戏行为实测，已移出当前HEAD，Git历史可恢复**；不能再误启动。E06只是统领设计，具体已完成结果见后续E##；恢复后的新实验仍需先写来源、正负控制、噪声、预算、决策表和数据。流程heuristic不能当科学去留bar。
- 失败或负结果要保留；不能筛幸存seed、偷换scene/test、事后改变主指标、把“这个模型一时失败”叫科学机制。
- 更强科学主张要在多个自然环境/角色/模型/独立审计下成立；没有测试玩家，就不能声称真实玩家信任、乐趣更好。

## 资源与安全边界
整个研究默认0付费推理 API：NPC、玩家/恶意NPC、教师、记忆整理、attack search、裁判均必须本地或规则模拟，隐藏 API fallback 禁止；实习16 H20授权与学校研究室隔离。弱网络/IO，单节点训练+多独立GPU条件/种子，模拟人口规模可用CPU规则NPC再混少量本地LLM而非全人口长上下文推理。
攻防实验仅在明确授权的本地沙盒、虚构经济与测试账户中进行；不要接入实际 MMO 服务器或真实用户资产。记录所有上游代码/模型/数据hash、GPUh/CPUh/LLM token/模拟步数/失败/权限与license。

## 科学汇报
用一段结论、源文献强近邻、我们实测的数字与置信区间、仍可能的解释、下一次最有区分力的动作结束每次会话；没有 GPU 结果就写没有，不把“知识库整理多”装成实证。所有精读产物落在**当前workbench的 knowledge/**，不是外部 library。
