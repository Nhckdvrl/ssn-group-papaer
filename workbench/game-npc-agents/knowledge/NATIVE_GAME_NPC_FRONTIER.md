# 原生游戏NPC：动作学习、语言接口、混合系统与运行

更新：2026-10-18。原生游戏系统的价值在于它要处理实际资产、感知、动作频率、玩家输入和运行限制。通关agent、仿真玩家、对手和角色伙伴可以共享方法，但其产品位置和评价目标不同。新正文记录见[总账](READING_CATALOG.md)，未重读项目保持原范围。

## 1. 先看接口，再看模型

| 系统类型 | 所获信息与动作 | 已有结果的适用范围 |
|---|---|---|
| 原始画面到按键 | 连续RGB、鼠标／键盘，基本不读引擎内部状态 | [VPT](../../../library/themes/game-npc-social/papers/BAKER_2022_VPT.md)、[SIMA](../../../library/themes/game-npc-social/papers/SIMA_2024.md)／[SIMA 2](../../../library/themes/game-npc-social/papers/SIMA2_2025.md)、[VideoGameBench](../../../library/themes/game-npc-social/papers/VIDEOGAMEBENCH_2026.md)关注感知与控制泛化 |
| 高层语言到技能 | 世界可见状态、实体语义、可调用技能和执行反馈 | [F.A.C.U.L.](papers/FACUL_AAAI2026.md)、PUBG Ally、[CoELA](../../../library/themes/game-npc-social/papers/ZHANG_2024_COELA.md)关注沟通、决策与协调 |
| 物理角色控制 | 身体状态、任务目标、动作示范或技能潜变量 | [DeepMimic](../../../library/themes/game-npc-social/papers/PENG_2018_DEEPMIMIC.md)／[AMP](../../../library/themes/game-npc-social/papers/PENG_2021_AMP.md)／[ASE](../../../library/themes/game-npc-social/papers/PENG_2022_ASE.md)关注运动、风格与技能组合 |
| 与规则／游戏AI结合的行为学习 | 结构状态、规则控制／成熟战术模块 | [MLMove](../../../library/themes/game-npc-social/papers/DURST_2024_MLMOVE.md)、EA案例、[Vox Deorum](papers/VOX_DEORUM_2025.md)关注风格、维护和可控增量 |
| 人格条件政策 | 角色向量、原生状态和固定动作空间 | PCSP、[MultiGAIL](../../../library/themes/game-npc-social/papers/MULTIGAIL_2023.md)关注共享策略与行为差异；运动风格不等于完整社会人格 |

CoELA不同条件分别使用RGB-D／位姿、实例ID掩码或符号对象状态；MLMove使用全部玩家结构状态。这些接口不能视为与玩家第一视角RGB等价。

强模型在第一类接口困难，不代表在第二类接口同样困难；第三类无需每帧调用LLM，也不是语言表达的替代。模型、控制层次、资产和运行约束一起决定研究对象。

## 2. 身体动作与行为风格是一条独立主线

DeepMimic把动作示范与任务奖励结合，使角色完成翻滚、移动、投掷等技能；AMP用动作分布先验减轻逐条轨迹跟踪；ASE把这些先验组织成可复用技能空间。关键认识是任务奖励与自然动作可以冲突，不能只报任务最高分。动作多样性、角色可控性、任务迁移和技能切换各有独立研究价值。[完整专题](LEARNING_CONTROL_AND_HUMAN_COOPERATION.md)

MultiGAIL研究多个示范风格及其组合，在一个赛车环境（连续动作）和一个导航环境（离散动作）、有限示范风格中验证；本文的persona主要是行为模式。MLMove从职业Counter-Strike日志学习战术移动，读取全部最多10名玩家的结构状态，并由作者实现的规则模块负责瞄准与射击，盲评观看轨迹与人类实际混合游玩是不同证据。它提供真实资产与运行链上的方法，仍不能把观众认为像人直接改写为最佳真人队友。[MultiGAIL](../../../library/themes/game-npc-social/papers/MULTIGAIL_2023.md)、[MLMove](../../../library/themes/game-npc-social/papers/DURST_2024_MLMOVE.md)

## 3. 通用游戏行动训练已经有实质进展

VPT用少量带动作标注数据训练逆动力学模型，再标注大量网上视频，使学习过程获得人类动作监督。SIMA把语言指令与多款虚拟世界的键鼠控制结合；SIMA 2加入Gemini基础模型、人类轨迹、桥接推理／对话数据和强化学习训练。它们所解决的感知—行动学习不能仅解释为更长提示。[VPT](../../../library/themes/game-npc-social/papers/BAKER_2022_VPT.md)、[SIMA](../../../library/themes/game-npc-social/papers/SIMA_2024.md)、[SIMA 2](../../../library/themes/game-npc-social/papers/SIMA2_2025.md)

SIMA 2报告在十个训练域的原生视觉键鼠接口上，未用SIMA行动数据微调的Gemini Flash-Lite／Pro成功率仅3.2%／7.0%，尽管作者做过格式提示调整。该比较说明这个接口下的专门行动训练有重要作用，不是已证明所有强LLM高层NPC都会失败。未见游戏结果也低于训练环境；定性长片段仍含人类指导。报告发表于2025年，不能因本轮2026年阅读就改成年份。原文未给出可唯一确定的模型版本及完整基线提示，不能视为截至2026年旗舰API的充分比较。

BALROG、VideoGameBench分别给出文本／图像简化环境和真实旧商业游戏的连续任务。前者主表是2024模型的零样本下一动作、16观察历史；后者v3更新于2026年，但并未因此变成2026旗舰模型完整重测。各类任务的进度、成功、检查点和实时限制要按原协议理解。[BALROG](../../../library/themes/game-npc-social/papers/BALROG_2025.md)、[VideoGameBench](../../../library/themes/game-npc-social/papers/VIDEOGAMEBENCH_2026.md)

Voyager、JARVIS-1和Cradle的正文及实际选读附录范围已在[前轮阅读§3](FIELD_REVIEW_2026-10-18.md#3-游戏通关agent模型系统和执行器必须分开)登记。它们继续作为技能、记忆、反馈和运行接口的参照，不额外计为本轮新阅读，也不把通关成绩转写为人物和玩家价值。

## 4. 实际游戏中的混合架构

**F.A.C.U.L.（AAAI2026）。** 在Arena Breakout: Infinite中，快速意图解析处理简单语音，较小LLM处理复杂计划，实体检索结合游戏坐标与方向，行为树执行。100场游戏2550条命令、24名熟悉该功能的玩家评价提供了真实接口证据。87.2%是命令／实体识别正确，613ms是作者系统读数；不是全任务胜率，也没有当前强商业模型加同信息的对照。[规范卡](papers/FACUL_AAAI2026.md)

**Vox Deorum。** 在Civilization V／Vox Populi中让LLM选择宏观战略、科技和政策，成熟游戏AI承担战术执行。2327个完成局中未检出相对原AI的显著胜率差，同时策略分布改变；未显著不同不是等效性检验。论文所测版本尚未实现与真人的自然语言外交，延迟部分为推算；2026-10-18核到的当前作者README已宣称加入互动外交与承诺交换，本库未运行验证，不把后续功能归入原论文结果。[规范卡与当前项目入口](papers/VOX_DEORUM_2025.md)

**EA设计与部署案例。** 原有[Augmenting Game AI with Deep Reinforcement Learning](https://arxiv.org/html/2606.20210v1)正文阅读针对FC25守门员和Battlefield6士兵移动，讨论训练周期、可控性、模块化、可维护、debug、真实性和运行预算。作者报告的训练时间、感知和CPU开销来自专有引擎，不能继承为本库可复现性能。其价值是明确“可修、可维护、适合角色”与任务能力同等重要；CoG vision身份与方法普遍有效性分开。

**PUBG Ally。** 前轮定向深读覆盖55页报告的系统、质量／延迟、人评及关键附录；已有状态刷新、待办和承诺保留、反馈、事件重规划、BT快速行动及强模型离线质量参照。它提供成熟系统压力，但共享团队目标不等于各NPC独立利益；公开backbone不代表完整产品可复现。[单一应用记录](../mine-a-persona-strategy/knowledge/PLAYABLE_NPC_APPLICATION_AUDIT_2026-10-16.md)

## 5. 人格条件政策、世界模型和架构提议

**PCSP。** 原有完整正文、关键附录和源码核查保存于[PCSP卡](../mine-a-persona-strategy/knowledge/papers/PCSP_2026.md)。共享政策以自然语言persona条件化，在Mini-Inzoi、Melting Pot和UE5层次研究行为；内部检索与独立行为probe并非同一证据。在线LLM比较主要是1.7B，不代表当前强高层API；本库历史实验也不构成本轮运行。其[源码](https://github.com/yoosunghong/pcsp)是资产入口，实验仍暂停。

**LARP。** 开放世界记忆、技能、角色约束和冲突过滤是有用架构提议；完整正文没有实证任务集、基线或玩家研究。保留其设计思想，不登记为已验证可靠性。[规范卡](../../../library/themes/game-npc-social/papers/LARP_2023.md)

**AGWM。** 用人工DAG前提和结构变化监督学习世界预测；部分环境获益，但Crafter／Craftax的MSE未改善，OOD表缺同条件基线。它是局部预测方法邻域，不是角色规划或玩家体验的完整验证。[规范卡](papers/AGWM_2026.md)

## 6. 原有初筛来源：继续保留，但不升级阅读范围

| 来源 | 本库实际范围 | 应怎样使用 |
|---|---|---|
| [Human-Like Bots for Tactical Shooters](https://arxiv.org/abs/2501.00078) | 摘要及正式期刊身份；完整正文欠缺 | 廉价传感与行为模仿的原生方向入口 |
| [UBCL](https://arxiv.org/abs/2512.10835)、[Direct Behavior Specification](https://proceedings.mlr.press/v162/roy22a.html) | 前者摘要；后者§2–6及主要实验定向阅读 | 行为向量和显式约束，不自动覆盖社会人物 |
| [Events as Triggers](https://www.proroklab.org/publications/events-as-triggers-neurips2026/) | 作者接收页／摘要，非完整正文 | 事件触发角色变化邻域，不当已部署游戏系统 |
| [LLM-Guided RL for Adaptive NPC Behavior](https://arxiv.org/abs/2609.02931) | 正文部分；训练条件可能不等价 | 不用预印本单胜率建立强共识 |
| [ReactiveGWM](https://github.com/INV-WZQ/ReactiveGWM)、[WorldMind](https://github.com/TeaWhiteBro/WorldMind) | 项目README／发布说明 | 视频生成反应与引擎状态控制不同；代码可用性须再核 |
| [CRPO](https://proceedings.mlr.press/v306/tang26c.html)、[Persona-Pruner](https://proceedings.mlr.press/v306/kim26br.html) | 正式身份／摘要，后者另读repo入口 | 角色语言训练或剪枝，不冒称NPC动作学习证据 |
| [Proact-VL](https://arxiv.org/abs/2603.03447)、[Behavioral Foundation Models for Quality Diversity](https://arxiv.org/abs/2609.35615) | 前者指定方法／实验附录及官方入口；后者摘要／方法概览 | 主动解说和行为空间搜索是邻接，全文欠账仍在 |
| [AI for Games综述](https://arxiv.org/abs/2609.16679)、[ccb/agent-sandbox](https://github.com/ccb/agent-sandbox) | 综述NPC／运行／体验部分；项目README／目录 | 发现入口，不按目录标题或模板推定录用和可运行 |

本页仍欠经典导航、拥挤人群、体育／赛车、现代运动生成和动作表演的更完整谱系。下一批应从这些空白和作者需求追引文，而不是只增加语言型agent。
