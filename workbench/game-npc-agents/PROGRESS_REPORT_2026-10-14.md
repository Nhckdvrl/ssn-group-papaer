# Game NPC Agent 矿区A进度报告｜2026-10-14

**结论：已完成强近邻定位、核心源码审计、多个原生游戏闭环及完整预算基线，进入真实角色选择的机制诊断；尚未形成独立验证的新顶会级idea。** 人物设定能够影响真实行动，也有行为稳定的情况；现有证据不支持把研究概括为“Persona必然失效”。用户要求本轮分析后暂停实验，不自动启动后续任务，研究线与idea不关闭。

报告日期按北京时间；游戏内08:00–11:20是模拟时钟。完整结果及实施纠正均在现有workbench内可追溯。

## 1. 从哪里入手，为什么这样推进

本轮开始先同步GitHub `main` 至 `9242c4b8`，阅读根AGENTS、RESOURCES、EXECUTION与现有workbench，继续使用原knowledge／experiments／results／logs，未恢复E00/E02–E05、未建第二套工作台。科研提交目前只在本地，未推送GitHub。

研究中心一直应是：**NPC面对具体请求、自身目标、角色规范、社会关系和可见状态，怎样形成选择，并通过合法动作产生游戏后果？** 曾使用的“利益控制”术语不清楚，已撤回并改正I03标题。PCSP手写奖励是基线诊断对象，不能将提高这个分数独立包装成新题。

推进顺序是：先核前人最强结果和代码 → CPU核引擎／parser／重试 → 单条本地完整episode → 恢复强模型与原预算训练 → 分开测表达、具体意图、实际执行 → 审阅真实异常与成功 → 做能区分竞争解释的控制。30轮只用于观察形成过程，随后已补齐300轮；不挑最好checkpoint、不筛种子，不用自设通过比例判科研价值。

## 2. 顶会与强近邻对齐到了哪里

| 强近邻 | 已核范围 | 对我们最关键的限制 |
|---|---|---|
| [The Personality Illusion，ICML2026](knowledge/papers/THE_PERSONALITY_ILLUSION_2026.md) | 正文、主表、关键附录与代码／数据入口；未复算全文统计 | 自述与行为失配、persona注入效应已有直接研究；不能重发现gap |
| [Rethinking Psychometric Evaluation](knowledge/papers/RETHINKING_PSYCHOMETRIC_2026.md) | 正文、提示／结果附录、Likert／行为runner；未本地复现论文数字 | 粒度、同／跨会话、priming已被研究；NeurIPS main身份尚未独立确认 |
| [The Story Shapes the Agent](knowledge/papers/STORY_SHAPES_AGENT_2026.md) | 正文、关键附录／表格、动作词／长度／强指令等消融；明确代码URL待核 | 叙事先验影响行动、persona在特定叙事内有效都已有；换RPG外壳不是增量 |
| [Persona Vectors in Games](knowledge/papers/PERSONA_VECTORS_GAMES_2026.md) | 正文、关键附录、生成／steering／judge代码入口 | 利他、宽恕、对他人的预期与策略steering已有；可解码不等于干预有效 |
| [PCSP](knowledge/papers/PCSP_2026.md) | 训练、奖励、split、梯度、独立行为评价及本地全预算；UE完整实现未复现 | 作者自己已披露内部对齐不等于独立Big Five行为效度；不能冒领其负结果 |

LIGHT／How to Motivate Your Dragon／CDT／KNUDGE的角色、动机、对话—动作和数据谱系已追踪；本地恢复了LIGHT原生目标事件，未完整复现Dragon原RL配方。另已读CRPO/ICML2026、HAMLET/ICLR2026、CoSER/ICML2025、UGST/TACL2026、Goal-Directedness/ICML2026、Dialogue is the Plan/ACL2026等强邻近工作。逐篇阅读边界在 [论文卡](knowledge/papers/) 与 [定位表](knowledge/persona-behavior/RELATED_WORK.md)，不能把它们一概说成“全部代码复现”。DPC匿名代码返回401；CoSER代码等仍有阅读债。

尤其已有：私有目标／公开剧情冲突、动机提示、角色与任务分开训练、动态状态追踪、对话形成共同承诺、goal/belief/plan分层与因果patch。当前探索须在具体NPC选择上获得进一步证据，不能只换术语。

## 3. 代码级审计得到什么

**PCSP源码事实。** 人物文本经冻结embedding与可学习投影进入共享actor/critic；PPO和diversity直接塑造策略。Mini-Inzoi的InfoNCE通过共享投影可能间接改变策略，离散rollout没有直接反传到actor；MeltingPot PHASE5则有独立GRU／head读出路径，不能混成一个损失拓扑。`preferred_actions`、Big Five风格与需求／social项已写进环境奖励，一些行为由奖励直接定义。

400训练角色只有20种属性配置×20职业；held100是另外五种联合原型×20职业。没有ID／全文重复，不等于每个属性组合或职业都独立。作者内部retrieval与独立动作／状态特征probe测的是不同层次。

**agent-sandbox源码事实。** 人物、目标、历史经不同组件进入LLM；合法动作由原parser执行，失败可能重试或fallback。计划、反思、对话后outcome与计划修订都是真实本地LLM调用，非用脚本代替模型选择。会话结束后，关系记忆及高importance意图记忆先写入，再尝试修改agenda；显式修订可影响何时结束当前活动。逐帧日志记录原始输入输出、parser调用、位置与world delta。

**解释与未排除因素。** parser合法不等于第一次模型选择正确，计划字段不等于实体任务完成，内部角色可读性不等于正确利益取舍。源码中的硬编码／fallback主要改变结果解释范围，本身不是科学创新。完整审计及历史纠正见 [SOURCE_AUDIT](knowledge/persona-behavior/SOURCE_AUDIT_2026-10-14.md)、各E##结果和 [CLAIMS](CLAIMS.md)。

## 4. 实际做了哪些实验

| 实验组 | 已实际完成 | 主要读数／认识 |
|---|---|---|
| E07–E12：ActionCastle与接口 | CPU正负控制、本地模型episode、现代模型和原生tool loop | E12首次合法动作48/133→92/135可由普通强接口解释；不是人格失效新机制 |
| E11/E14：LIGHT自然任务 | 36个原生episode；266/273动作合法，36/36作者goal事件执行 | 目标event不是所有长期人物利益成功；源场景／人物／合法动作可回放 |
| E15：意图—行动抽样校准 | 1152本地调用，独立支线与A/A噪声比较 | ΔJS均值−0.01125，图簇95%[−0.03103,0.01020]；不能从两次不同抽样直接讲gap |
| E16/E20/E21：双角色资源与对话 | E21 36局，78/78物理、102/102speech合法，310本地调用 | 每局一次消费／两个角色机会；对话与动作调度影响解释，不是所有角色目标都完成 |
| E22：公开归属／物理访问 | 704调用、规则事实与物品绑定控制 | 不支持此前权限投射解释；原目标物品提醒使放worm9/32→1/32，负向字段资格失败已降级 |
| E13/E17–E19：PCSP公开政策与读出 | 原政策闭环、冻结政策读出、三种子／独立行为测量 | 可读取身份、实际策略变化、身体状态信息必须分开 |
| E23–E28：编码／短形成控制 | 原500编码复现、正确pool、梯度路径、普通语义和坐标对照 | 原pool有480行取padding位置；修正是已有算法的工程恢复。坐标补偿无明确效用收益 |
| E29/E30/E35：原生生成式NPC | 真实健康／饮用任务准入，本地planner/reflector；三角色三自然局各1200帧 | E35分别129/129/166调用、5/5/8自然对话；成功、失败和未观察承诺均保留 |
| E34：PCSP完整强基线 | 三种子×Full/No，六次300轮，4608万transitions | 所有30/100/300阶段保留；Full局部C响应更强，完整native收益三种子较低 |
| E36/E37/E39/E40：功能／状态控制 | 三阶段、三种子、120属性编辑、三个状态银行、身份对照；E40 540局 | 60000动作reward重建零误差；方向／状态／身体反馈并存，没有统一修复方向 |
| E38：独立MeltingPot | 26次默认／强／正确编码训练，360个完整七角色episode | 正确编码Full−No团队收益−12.54，五种子簇95%[−38.52,13.43]；内部读出和外部结果分开 |
| E41：普通覆盖／绑定全预算 | 四条件×三种子，12次300轮，每次768万，共9216万transitions | 表面扩充、匹配C干预、仅输入、仅真实目标；所有阶段和反方向结果保留 |
| E42：强本地LLM参考 | 两Qwen模型×两提示×两伙伴政策，240个200cycle原生局 | 48000本地决策、0随机fallback；具体偏好信息常改善两目标，不能把DD直接叫偏好实现 |
| E44–E48：自然角色机制诊断 | 时钟／责任、人物／信息四格、真实计划进度、宽发言预算、显式agenda消融 | 见下一节；均保留完整1200帧和独立回放 |
| E49：跨两其他角色 | 六原生处境×四条件，24条完整1200帧后缀，1173新增调用 | 全24条独立回放通过；详见下节的处境差异与协议限制 |

E43白盒方向诊断和E42额外规则知情对照仅登记／准备，**未运行**；暂停后不会自动启动。大权重和raw轨迹不进Git，统计结果见 [results索引](results/README.md)。各组episode、transition和frame不是可相加的独立样本量。

## 5. 最重要的结果，及它们支持到哪里

### 训练基线：人物信息有真实作用，整体游戏表现还受其他因素影响

E34在300轮时，Full−No原生平均收益逐种子为 **−20.94、−5.06、−7.61**；同状态同幅度的C利益方向，Full在三种子及三个状态银行更强。这两条证据并存：不能说persona只有读出，也不能用局部方向替代长期收益。只有三个训练种子，报告逐种子结果，不推人口性结论。[原始结果](results/E34_checkpoint_0300.json)

E38正确编码的内部retrieval为 **38.07%／6.93%**，团队收益差 **−12.54 [−38.52,13.43]**。区间跨零意味着本次跨种子方向不确定，不作为“没有价值”的淘汰bar。作者PHASE5独立读出路径已数值核对，不能把retrieval上升直接称策略改善。[原始结果](results/E38_native_policy_360_episodes.json)

E41在300轮相对原No的收益变化：surface **[+2.29,−8.28,+0.88]**；matched **[+3.20,−0.89,+4.19]**；input-only **[+0.21,−1.66,+6.64]**；goal-only **[−5.13,−1.84,+0.71]**。普通覆盖与绑定没有统一排序，不强造新loss，也不挑某一seed／阶段作为答案。[全部四格与阶段](results/E41_complete_factorial_all_stages.json)

### 自然角色：表达、承诺、计划与行动之间存在可核查的多条路径

E45三个固定自然episode的角色／责任四格全部完成：10条新后缀、704新增调用；加两条E44复用格共12格／820次后缀调用。修改的是教授conversation阶段的一处描述，planner／执行器和历史仍保留原人设，不能称完整人格改变。不同处境方向不同，不符合“reserved必然少帮助”的简单故事。原输入重复中，两局位置／活动1200帧相同，一局为1095/1200；后续随机分化必须保留。[完整结果](results/E45_complete_persona_context_factorial.json)

E46加入真实计划执行位置后，两角色条件都进入原讲座活动；original形成两次即时新教学承诺，reserved形成一次11:00预定承诺。原教授speak解析失败2/0次；E47把其两路预算128→512，变为 **0/0**，两即时对一预定的区别仍在。预算也改变具体内容和后缀，因此只排除了部分协议解释，不证明深层人格机制。[E46](results/E46_complete_grounded_progress.json)、[E47](results/E47_complete_dialogue_budget.json)

E48保留真实对话、关系及意图记忆，只阻止教授conversation显式修订。original仍说出即时承诺，但新增活动不再出现；reserved仍起步去Williams，因为原agenda已包含那里。这说明 **“动作符合承诺”不能单独识别承诺的因果作用**。这是单case和已有程序渠道的诊断，不是首次提出对话进入计划。[E48完整消融](results/E48_complete_plan_update_ablation.json)

### E49：跨角色本轮结果

**24/24条完成并独立零模型重放1200帧完全一致，1173次新增本地调用、8852个新后缀帧。** 复用的是三条自然历史，不是24个独立自然样本。两个角色用了不同描述对照：Diego `creative→conventional`，Sofia `friendly→reserved`；只作用于conversation，旧历史和其他组件保留原人设。[完整结果](results/E49_complete_cross_role_commitments.json)、[24条回放证明](results/E49_all_24_independent_replay.json)

| 固定处境 | 正常计划渠道的观察 | 阻止焦点conversation修订后的观察 | 当前解释范围 |
|---|---|---|---|
| Diego 3501 | original于1058起步去Meyerson；contrast于923起步去Williams | 两条件均留在Irvine | 本case路线差异与显式修订渠道有关 |
| Diego 3502 | 两描述都于967起步去Williams，三人tile轨迹相同 | 两描述仍去Williams，但1193才起步 | 承诺可以改变行动时机，目的地一致不能判无作用；原agenda下一处其实是Meyerson |
| Diego 3503 | original于995去Meyerson；contrast留Irvine，后来生成草图活动描述 | 两条件均留Irvine | 行程与原地活动文字须分开；有一条根级parser失败，保留 |
| Sofia 3501 | 本人两条件位置相同，contrast新增原地活动／计划；教授后续路径也不同 | 本人仍不移动，但活动描述可不同 | 本人位置稳定不等于全世界稳定；无实体草图flag |
| Sofia 3502 | original于877去Williams；contrast留Irvine | 两条件均留Irvine | 当前case的新行程与显式修订渠道有关 |
| Sofia 3503 | original去Kamin Gallery；contrast去Moelis Reading Room | 同样出现这两条不同路线，焦点agenda未被修订 | 不能把全部作用归为agenda；意图记忆仍是另一个入口 |

Sofia 3503中，blocked条件唯一焦点修订请求被确实阻止；原agenda剩余地点是Houston。844帧实际LLM选择却分别去Kamin／Moelis，输入中能直接看到对应的“我与教授约定……”PLAN记忆。这支持**显式计划之外仍有行动渠道**，还不能量化意图记忆、伙伴反馈与后续采样各贡献多少。该机制的意图保留已有作者代码设计，发现数据流本身不是新贡献。

协议读数也保留：焦点Diego的83次、Sofia的58次structured speak均零解析失败；**129次结构化解析失败来自19次其他角色speak与110次记忆重要性评分**，其他预算未统一扩大，协议影响未完全排除。outcome实际使用0.0温度，保留source默认。后缀所有角色合计 **146/147根级parser调用合法**，这是执行统计，非147个独立样本或实体任务成功率。发言／outcome／计划／实际位置必须一起审阅。

## 6. 负结果、作废与执行纠正

| 项目 | 已如何处理 |
|---|---|
| E22权限机制 | 正控制失败和不支持结果均保留，相关判断降级；I01仍SEED，不替人关闭 |
| E41 surface v1 | 错复用了只改held100的资产，train400未变；原结果作废，raw／权重保留，以正确v2从头完成全300轮 |
| E44事实提醒v1 | 漏了freechat fallback，两个部分分支不作统一暴露证据；保留后以独立v2完整重跑 |
| E49 CPU v1 | Diego同帧目标speak前还有原调用，frame切入过早；未跑GPU，保留失败，v2完整24条件资格后才运行 |
| E35首局旧调用上限 | 部分局1184帧保留，按原cassette精确续完至1200，不把预算截断记为NPC失败 |
| PHASE5源码审计 | 稀疏检出漏根目录曾造成不完整判断；已读取真实源码并数值核查，不能再说作者独立读出路径不存在 |
| 早期人为bar／含混术语 | 不再以跨seed比例、2×noise或“内部读出够不够高”自动舍弃idea；“利益控制”不再作为独立题目 |

## 7. 目前进度与未完成的科学工作

**工程与测量已落地，选题还未收敛。** C01仍L1基线可行性；I01/I02/I03保持SEED，没有宣称新方法、没有进入投稿候选。当前最值得继续判断的是人物描述如何影响NPC采纳具体任务、已有任务与新承诺如何改变动作时机和伙伴选择。这是有轨迹来源的研究问题，尚不能称已验证新idea。

主要限制：校园系统有真实行程／合法动作，却没有独立的讲座完成或草图成品flag；步行动作中的目的地不是已到达地点，avatar的x/y与引擎地点字段需分别核查。三个自然历史来自同世界，两个角色的描述对照不是统一心理构念，且分别在不同节点运行，不能平均成统一trait效应。局部描述与旧经历／其他组件的人设并不全一致；模型调用分化会改变后续采样seed；两强Qwen参考不是独立模型家族；尚无真实玩家体验研究。frame数、对话量和合法率不替代这些问题的证据。

恢复后优先级是：先核全部成功／失败轨迹及竞争解释 → 选择原作者已有、物理后果更清楚的角色任务验证预测 → 若普通强提示、明确目标或既有机制已经解释，承认并调整增量 → 只有剩余问题需要训练时才考虑SFT／LoRA／RL或内部干预。不排周计划、不提前规定GRPO，不因已有近邻自动关闭矿区。

## 8. 怎么接手、怎么查文件

1. **先读本报告与 [README](README.md)**，理解已做／未做与暂停边界。
2. **再读 [源码审计](knowledge/persona-behavior/SOURCE_AUDIT_2026-10-14.md) 和 [定位表](knowledge/persona-behavior/RELATED_WORK.md)**；需要主张核查时打开原论文，不把笔记替代全文。
3. **从一个原生case入手**：E35 seed3502教授787帧对话 → E45人物／信息四格 → E46计划进度 → E47预算 → E48显式修订 → E49其他角色。先看对话、outcome和原agenda，再看合法动作／位置；不先看一个聚合“persona分数”。
4. **查代码与资产**：当前入口见 [scripts说明](scripts/README.md)；E44/E49旧v1不是GPU入口。结果JSON只是摘要，完整模型输入输出、parser／frames／checkpoint都在缓存。

| 资产 | 位置 |
|---|---|
| 原始轨迹／checkpoint／manifest | `/home/xiang/.cache/game-npc-research/runs/`，对应E##卡的raw字段 |
| 三原局 | `runs/e35_original_cast/`、`runs/e35_natural_repeats/seed3502/`、`seed3503/` |
| 最新受控轨迹 | `runs/e44_*`至`runs/e49_*`；E49每worker内seed3501/3502/3503 |
| 源码 | `sources/agent-sandbox` pin `d7b872e396df2ef05ff8391de53e0563ca698cf3`；PCSP `5420f7b`、MeltingPot分支`4fbbffa` |
| 环境 | NPC／Mini-Inzoi：现有`fgvd`+`deps` overlay；MeltingPot：现有`lightwam`+隔离overlay |
| 模型 | 复用HuggingFace缓存，当前主要Qwen3.5-27B／Qwen3-32B，完整snapshot hash见manifest |

原生回放无需重新推理，可在CPU用`penn_branch_verify.py`或E49的`penn_cross_role_verify.py`验证已有cassette；输出必须指定新文件，不能覆盖原证据。暂停期间不启动新训练／新模型rollout。

## 9. 资源与暂停记录

核心研究链路**0付费推理API**，无SDK云fallback。GPU使用前核空闲，本轮最高同时8卡，主要fvcrc20/21各四卡；其余节点上的他人任务未停止。小MLP的CPU实测更快，按实际需要选择CPU，而非为了占卡使用GPU。详细成本逐实验记录，未编造一个全项目GPU小时总数。

**本轮24条均完成、24条独立回放均通过，八个实验worker会话均正常退出（exit0），本地项目Python进程为0、本地四GPU各仅15MiB空闲占用。** 原长期科研goal已暂停，收到暂停指令后没有启动新推理／训练；只完成原定轮次和CPU核对。

远程fvcrc20的四个原实验会话亦均exit0，全部manifest完整；即时硬件复查遇到既有SSH跳板banner超时，本机也无法解析校内域名直连。远程GPU释放按正常退出机制推断，**未获得最后一次nvidia-smi现场确认**，不把它写成已实测。详见 [暂停记录](results/EXECUTION_PAUSE_2026-10-14.json)。

E49记录的模型载入3040.95秒＋分支wall13811.95秒，合计约4.68GPU·小时，未覆盖所有初始化／退出间隙；高于原2小时粗估，实际成本保留。此次暂停实验执行，不关闭矿区A、不删除负结果，也不会从旧卡片自动恢复。
