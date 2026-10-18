# 游戏 NPC Agent 领域地图

更新：2026-10-18。这个地图覆盖**游戏中角色的行为、人物表现、与人的互动、叙事、社会、制作与运行**。它不是矿区A的相关工作表，也不把所有游戏AI或角色聊天模型都算作直接NPC证据。逐篇来源、实际版本、阅读范围与未读欠账见[阅读总账](READING_CATALOG.md)。

## 1. 先明确：谁在游戏里承担什么功能

NPC是产品中的角色位置，不是一种模型架构。同一个守卫可以由寻路、动画控制、行为树、效用决策、角色记忆和语言生成共同实现；同一种LLM也可能被用于扮演人物、操作玩家、编写剧情或裁决世界。混淆这些位置，会把不相干的榜单和限制搬来选题。

| 对象 | 主要服务的能力 | 合适的主要证据 |
|---|---|---|
| 对手与战斗单位 | 挑战、战术风格、运动可信度、性能和可预测性 | 实际动作与轨迹、设计规格、不同水平玩家体验、运行预算 |
| 背景人群、环境生物与生活角色 | 世界氛围、空间和生活可信度、局部响应、生态与社会活动 | 运动和空间协调、活动规律、玩家感知、与玩法的适配及运行预算 |
| 队友、同伴与任务伙伴 | 配合玩家、支持玩家计划、沟通分工、保留人物主见 | 与未见伙伴及真人互动、贡献分配、协调负担、角色和关系体验 |
| 居民、商人、剧情人物 | 生活规律、动机、知识、关系、交换、故事作用 | 人物、知识和事件一致性，玩家理解与角色体验；涉及状态改变时核查实际后果 |
| 叙述者、导演与世界裁决器 | 情节组织、规则维持、内容调度 | 作者意图、可达性与一致性、玩家选择空间、制作和调试成本 |
| 模拟玩家、通关agent与研究用社会仿真 | 测试游戏、学习控制、解释或预测行为及制度效果 | 任务泛化、与人类数据的差异、校准和外部验证；不可直接替代NPC体验 |

**角色是否可信、任务是否完成、世界是否自洽、作者是否能控制、玩家是否喜欢，是五个需要分别回答的问题。** 它们可以互相促进，也可以冲突。见[NPC合作设计综述](../../../library/themes/game-npc-social/papers/NPC_COOPERATION_REVIEW2022.md)、[互动叙事综述](../../../library/themes/game-npc-social/papers/RIEDL_BULITKO_2013.md)和[角色评价综述](../../../library/themes/game-npc-social/papers/RPA_EVALUATION_SURVEY_2025.md)。

## 2. 全领域的研究方向

这些方向是交叉坐标，不是互斥的矿区，也不产生开线决定。“覆盖较厚”表示本库有多篇正文和对照脉络，仍不表示已穷尽。

| 方向 | 游戏能力与典型研究问题 | 方法与代表证据 | 当前覆盖 |
|---|---|---|---|
| 身体动作、运动与风格 | NPC如何既完成动作又具有合适的姿态、节奏、技能和风格？ | [DeepMimic](../../../library/themes/game-npc-social/papers/PENG_2018_DEEPMIMIC.md)→[AMP](../../../library/themes/game-npc-social/papers/PENG_2021_AMP.md)→[ASE](../../../library/themes/game-npc-social/papers/PENG_2022_ASE.md)；示范、动作先验、技能空间 | 示范—动作先验—技能重用脉络较厚；当代运动生成、跨身体控制与多模态表演仍薄 |
| 感知、导航、技能与长程行动 | 如何理解局势、到达目标、组合技能，并在新地图/新规则中继续有效行动？ | [VPT](../../../library/themes/game-npc-social/papers/BAKER_2022_VPT.md)、[SIMA](../../../library/themes/game-npc-social/papers/SIMA_2024.md)/[SIMA 2](../../../library/themes/game-npc-social/papers/SIMA2_2025.md)、[BALROG](../../../library/themes/game-npc-social/papers/BALROG_2025.md)、[VideoGameBench](../../../library/themes/game-npc-social/papers/VIDEOGAMEBENCH_2026.md)；另见Voyager/JARVIS-1/Cradle历史阅读 | 游戏行动学习较厚；经典寻路、群体导航和潜行感知仍薄 |
| 对手、难度与玩家建模 | 如何给不同玩家合适挑战，保持可学习的战术、风格与公平感？ | [Dynamic Scripting](../../../library/themes/game-npc-social/papers/SPRONCK_2006_DYNAMIC_SCRIPTING.md)、[Enemy Within](../../../library/themes/game-npc-social/papers/PFAU_2020_ENEMY_WITHIN.md)、[MLMove](../../../library/themes/game-npc-social/papers/DURST_2024_MLMOVE.md) | 有传统自适应与真实轨迹；难度体验、公平性、长期玩家分布仍需扩展 |
| 人机合作与队友适应 | 如何配合不同习惯、能力、约定的玩家，并留给人参与和决策空间？ | [Human-aware coordination](../../../library/themes/game-npc-social/papers/CARROLL_2019_HUMAN_AWARE.md)→[FCP](../../../library/themes/game-npc-social/papers/STROUSE_2021_FCP.md)→[HSP](../../../library/themes/game-npc-social/papers/YU_2023_HSP.md)→[CooT](../../../library/themes/game-npc-social/papers/WANG_2026_COOT.md)及[ICRL4AHT](../../../library/themes/game-npc-social/papers/JING_2026_ICRL4AHT.md)；[CoELA](../../../library/themes/game-npc-social/papers/ZHANG_2024_COELA.md)与工业伙伴 | 方法和真人协议较厚；任务集中Overcooked/家居，真实多人长期协作仍薄 |
| 语言、语音与非语言交互 | 自由表达、指代、打断、礼貌、身体距离如何变成可发现且可纠错的互动？ | [F.A.C.U.L.](papers/FACUL_AAAI2026.md)、[语音对话图](../../../library/themes/game-npc-social/papers/VOICE_CONTROLLED2025.md)、[Press A or Wave](../../../library/themes/game-npc-social/papers/PRESS_WAVE2024.md)、[礼貌机制](../../../library/themes/game-npc-social/papers/ETIQUETTE2024.md) | 有真实玩家和工程系统；多语言、无障碍、在线持续使用仍薄 |
| 人物知识、风格与原创角色 | 角色知道什么、怎样说、何时拒绝、如何适应作者创造的新人物？ | [Character-LLM](../../../library/themes/game-npc-social/papers/CHARACTER_LLM_2023.md)、[RoleLLM](../../../library/themes/game-npc-social/papers/ROLELLM_2024.md)、[Ditto](../../../library/themes/game-npc-social/papers/DITTO_2024.md)、[OpenCharacter](../../../library/themes/game-npc-social/papers/OPENCHARACTER_2025.md)、[CoSER](papers/COSER_2025.md)、[HER](../../../library/themes/game-npc-social/papers/HER_2026.md) | 训练与评价较厚；原创角色到实际行动的转移不足 |
| 情绪、动机与心理状态 | 事件怎样通过目标、解释和应对方式影响角色，而非仅改变情绪词？ | [EMA](../../../library/themes/game-npc-social/papers/EMA_2009.md)、[FAtiMA Modular](../../../library/themes/game-npc-social/papers/FATIMA_MODULAR_2014.md)、[PsychSim](../../../library/themes/game-npc-social/papers/PSYCHSIM_2005.md)、[Dynamic Persona Coherence](papers/DYNAMIC_PERSONA_COHERENCE_2026.md) | 跨传统与LLM有脉络；心理效度、情感表达与玩家理解仍需独立核验 |
| 记忆、关系与人物成长 | 如何记住谁经历了什么、信息来自哪里，并产生合理关系与行为变化？ | Generative Agents历史阅读；[Talk of the Town](../../../library/themes/game-npc-social/papers/TALK_OF_TOWN_2015.md)、[动态人格](papers/DYNAMIC_PERSONA_COHERENCE_2026.md)、[游戏同伴研究](../../../library/themes/game-npc-social/papers/COMPANIONS_DISSERTATION2019.md) | 概念与部分机制较厚；跨会话长期真人关系证据偏薄 |
| 叙事规划与体验管理 | 人物的局部选择怎样组成可理解的冲突、伏笔与故事，并容纳玩家分支？ | [CPOCL](../../../library/themes/game-npc-social/papers/CPOCL_2011.md)、[Glaive](../../../library/themes/game-npc-social/papers/GLAIVE_2014.md)、[Sabre](../../../library/themes/game-npc-social/papers/SABRE_2021.md)、[DODM](../../../library/themes/game-npc-social/papers/DODM_2006.md)、[StoryAssembler](../../../library/themes/game-npc-social/papers/STORYASSEMBLER2019.md)、[HAMLET](papers/HAMLET_2026.md) | 传统规划与LLM桥接较厚；大规模生产与开放分支验证仍薄 |
| 规则、世界模型与可执行性 | 谁定义和验证状态变化、前提与资源？语言生成何时需要确定性结算？ | [RPGBench](../../../library/themes/game-npc-social/papers/RPGBENCH_2025.md)、[AGWM](papers/AGWM_2026.md)、[Concordia](../../../library/themes/game-npc-social/papers/CONCORDIA_2023.md)、[NCP](papers/NCP_2026.md) | 已能区分文本世界/规则世界；广泛学习世界模型与引擎验证覆盖有限 |
| 多角色调度与社会推理 | 谁发言、谁行动、谁知道什么，冲突、误信与合作如何影响群体？ | [PsychSim](../../../library/themes/game-npc-social/papers/PSYCHSIM_2005.md)、[SOTOPIA](../../../library/themes/game-npc-social/papers/SOTOPIA_2024.md)/[π](../../../library/themes/game-npc-social/papers/SOTOPIA_PI_2024.md)、[MASCOT](papers/MASCOT_EMNLP2026.md)、[Agent Sociodrama](papers/AGENT_SOCIODRAMA_2026.md) | 有经典及新方法；不少是社会对话邻域，须保留游戏边界 |
| 群体规范、文化与社会仿真 | 游戏内社会如何支持生活秩序、冲突与故事；研究用模拟能否解释或预测真实人群？ | [Melting Pot](../../../library/themes/game-npc-social/papers/LEIBO_2021_MELTINGPOT.md)、[社会惯例](../../../library/themes/game-npc-social/papers/NORMS_2025.md)、[AgentSociety](../../../library/themes/game-npc-social/papers/AGENTSOCIETY_2025.md)、[CitySim](papers/CITYSIM_2025.md) | 有规模与规范研究；作品可玩性与真实社会外部验证是不同目标 |
| 经济、资源与制度 | 生产、消费、交易、价格和政策怎样同时支持玩家行为、平衡与可解释模拟？ | [MMOAgent](papers/MMOAGENT_KDD2025.md)、[GovSim](../../../library/themes/game-npc-social/papers/GOVSIM_2024.md)、[AI Economist](../../../library/themes/game-npc-social/papers/AI_ECONOMIST_2021.md)、[Vox Deorum](papers/VOX_DEORUM_2025.md) | 从单次交易扩至制度；玩家真实经济数据、机制校准与长期扰动仍薄 |
| 作者工具、可编辑性与调试 | 如何让作者说明意图、探索可能性、定位错误、修补角色且不破坏已有内容？ | [FAtiMA Toolkit](../../../library/themes/game-npc-social/papers/FATIMA_TOOLKIT2022.md)、[可解释作者工具](../../../library/themes/game-npc-social/papers/FATIMA_EXPLAINABLE2022.md)、[KNUDGE](papers/KNUDGE_2024.md)、[WhatELSE](../../../library/themes/game-npc-social/papers/WHATELSE2025.md)、[Orchid-Creator](../../../library/themes/game-npc-social/papers/ORCHID_CREATOR2026.md) | 玩家/作者研究明显增厚；团队生产、版本管理、QA覆盖仍薄 |
| 安全、知识权限与合法欺骗 | 玩家可以调查、劝说、骗人到什么程度？怎样阻止越权且保留玩法？ | SKT历史阅读；[AgentDojo](../../../library/themes/game-npc-social/papers/AGENTDOJO_2024.md)、[ASB](../../../library/themes/game-npc-social/papers/ASB_2025.md)、[Agentic Firewalls](../../../library/themes/game-npc-social/papers/AGENT_FIREWALLS_2026.md)为邻域 | 权限和评价较清晰；原生NPC多轮攻击与正常玩法配对证据少 |
| 玩家体验、选择与评价 | 分数更高是否意味着更有趣、更易理解、更有参与感、更值得重玩？ | [叙事选择](../../../library/themes/game-npc-social/papers/NARRATIVE_CHOICE2022.md)、[Façade体验](../../../library/themes/game-npc-social/papers/FACADE_PRESENCE2007.md)、[玩家涌现策略](../../../library/themes/game-npc-social/papers/PLAYER_EMERGENCE2024.md)、[DiaryPlay](../../../library/themes/game-npc-social/papers/DIARYPLAY2026.md) | 有多种真人/作者证据；长时、跨游戏、留存与文化外推仍薄 |
| 运行、部署与维护 | 如何控制端到端延迟、并发、成本、补丁回归和异常恢复？ | [F.A.C.U.L.](papers/FACUL_AAAI2026.md)、[MLMove](../../../library/themes/game-npc-social/papers/DURST_2024_MLMOVE.md)、EA/PUBG第一方系统记录 | 有实际系统，完整公开代码/生产追踪普遍不足 |

专题入口：[学习、控制与合作](LEARNING_CONTROL_AND_HUMAN_COOPERATION.md) · [角色训练与评价](ROLE_LEARNING_AND_EVALUATION.md) · [叙事与社会](SOCIAL_SIMULATION_AND_NARRATIVE.md) · [玩家与作者](PLAYER_EXPERIENCE_AND_AUTHORING.md) · [目标与控制](GOAL_CONTROL_REVIEW.md) · [人格变化](PERSONA_DRIFT.md) · [经济](GAME_ECONOMY.md) · [安全](NPC_SECURITY.md)。

## 3. 怎样读懂方法演进，而不只积累标题

**传统表示与学习式控制不是简单替代关系。** 行为树、GOAP、BDI、戏剧管理和社会规则使意图、动作前提与可编辑边界显式化；模仿学习和RL利用数据或交互获得难以手写的细节；语言模型扩展表达、知识和开放输入的覆盖。混合系统常把这些分工。关键比较是覆盖了哪些情境、保留了什么控制能力、需要多少示范／标注／脚本／算力，而非架构里有没有LLM。见[目标控制谱系](GOAL_CONTROL_REVIEW.md)和[原生系统](NATIVE_GAME_NPC_FRONTIER.md)。

**人物表达、情境互动、规则执行和使用体验是相互关联但不同的研究对象。** 角色QA、单次情境回应、多轮文本模拟、规则世界、引擎行动、真实玩家研究和持续产品使用各自回答不同问题。后者并非自动比前者更好的论文；评价应与主张匹配，跨对象外推时需要桥接证据。[CharacterBox](../../../library/themes/game-npc-social/papers/CHARACTERBOX_2024.md)、[CoSER](papers/COSER_2025.md)、[RPGBench](../../../library/themes/game-npc-social/papers/RPGBENCH_2025.md)恰好展示了三种不同任务组织。

**玩家适应与人物自主性需要共同设计。** 队友可能需要主动承担任务，也可能要让出关键行动；人物可以有自己的目标和反对意见，同时不能无谓破坏玩家策略。[FCP](../../../library/themes/game-npc-social/papers/STROUSE_2021_FCP.md)与[HSP](../../../library/themes/game-npc-social/papers/YU_2023_HSP.md)显示训练伙伴分布会改变真人协作；[同伴调查](../../../library/themes/game-npc-social/papers/COMPANIONS_DISSERTATION2019.md)同时报告对独立人格和不妨碍玩家的需求。不能把“越顺从越好”或“越自主越好”当统一目标。

**评价本身正在改变可见的进展。** 人格量表、LLM裁判、动作指标、作者研究和真人偏好有不同偏差。[SOTOPIA-π](../../../library/themes/game-npc-social/papers/SOTOPIA_PI_2024.md)的自动/人工差异、[CoSER](papers/COSER_2025.md)与[HER](../../../library/themes/game-npc-social/papers/HER_2026.md)的评委变更、[KNUDGE](papers/KNUDGE_2024.md)各质量维度的分歧，都要求按原协议理解效果，不能跨表拼排行榜。详见[测量规范](MEASUREMENT.md)。

## 4. 用广视野选择问题

方法研究需要连成四段证据：**游戏能力或作者困难 → 已有解决路径 → 在公平强参照下仍缺什么 → 解决后增加什么认识或可用能力**。描述、解释、设计理论和创作实践研究则应说明：**尚不清楚的玩家／作者现象 → 合适的研究对象与材料 → 可信的分析与竞争解释 → 怎样改变设计理解或实践**；它们不必先击败一个算法基线。不要求每篇工作发明全栈，也不因单个组件已有研究就否定组合贡献。

| 可能的整体贡献 | 应获得的证据 | 容易滑成的局部问题 |
|---|---|---|
| 行为方法 | 跨场景控制、风格／任务权衡、编辑与迁移 | 在一张图上加奖励或换提示后升分 |
| 合作方法 | 未见玩家／伙伴、分工、参与空间、适应过程 | 只追求agent代做全部任务的最高分 |
| 角色与关系方法 | 原创人物、事件引起的合理变化、可预测行为 | 单次问卷或相似度提高即称真实人格 |
| 叙事与作者系统 | 作者约束、分支空间、调试成本、作品和玩家 | 生成很多分支或堆多个agent即称创造力 |
| 社会／经济理解 | 个体规则和制度干预、外部校准、替代解释 | 模拟出现熟悉现象即称复现人类社会 |
| 评价贡献 | 清晰构念、独立效度、会改变已有判断 | 新命名一组小任务，再用同一LLM自评 |
| 玩家／开发者理解与设计证据 | 情境充分的访谈、观察、作品／使用过程和可信分析 | 将少量偏好包装为普遍因果效果，或因无算法胜率而否定设计认识 |

这里没有预先给某方向排优先级。选题的证据门槛与模型／接口公平性见[强基线](STRONG_BASELINES.md)；矿区A的现有工作只在[独立审查](../mine-a-persona-strategy/results/audits/INDEPENDENT_RESEARCH_VALUE_REVIEW_2026-10-18.md)中评判，不再充当外围地图的默认问题。

<a id="source-status"></a>
## 5. 阅读范围与仍然欠缺的覆盖

[阅读总账](READING_CATALOG.md)把“取得PDF”“完整正文”“选读附录”“作者改写章”“代码核查”和“本地实验”分开。新旧版本、改题名和同一研究的系统／基准不重复计数；摘要条目不混入正文数。旧卡未经重读不会随更新日期自动升级。

这不是系统穷尽的全领域综述。当前明显不足包括：经典导航／群体移动、面部和多模态表演、体育与赛车NPC、混合人群中的长期匹配、公平和无障碍设计、跨文化玩家、多人开发流程与长时上线证据；新近未取得全文的来源也在总账中明确列出。下一批阅读应由这些覆盖空白和引用链驱动，而非继续只追现有局部任务或凑篇数。
