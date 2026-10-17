# 目标控制研究谱系：切口为什么重要，哪些认识已属于前人

核查日：2026-10-13。本文是定向阅读的综合，不是“全部NPC文献已精读”。原文动机记为 DOCUMENTED；推断作者如何想到实验只记为 RECONSTRUCTED。阅读范围逐条列出，没有本地重现论文数字。

## 1. LIGHT / How to Motivate Your Dragon：先有角色自己的动机

来源：[NAACL 2021正式论文](https://aclanthology.org/2021.naacl-main.64/)、[完整HTML](https://arxiv.org/html/2010.00685v3)、[PDF](https://aclanthology.org/2021.naacl-main.64.pdf)。本轮读正文任务/数据/方法/结果及关键设置附录，查看PDF p.2示例；并核查LIGHT当前引擎入口，未完整恢复旧训练代码。

DOCUMENTED：原LIGHT人物可以对话和行动，但没有系统的自身目标；作者加入短/中/长期动机、时间线、可执行行动与人类示范。RECONSTRUCTED：不是靠更长persona制造人格，而是把“人物想达到的结果”加入可执行环境，让说话和行动共同承担任务。

7486个quest、2111条示范是不同资产；示范平均12.92个事件，其中2.18个行动、10.74个对话。原伙伴为固定模型且无自身独立目标；部分语言奖励依赖学习到的DM或参考话语。不能把这些数据自动称为自然长期关系、强动态玩家或纯引擎评分。

**给我们的认识：** 沿用原生角色动机与世界，而不是从竞赛接口生长NPC概念。原作者的事件型action goal和高层自然动机不同；重新映射目标必须明确是新任务定义，不能指控旧评分不忠实。

## 2. Direct Behavior Specification：成功率不能代表作者控制

来源：[ICML 2022](https://proceedings.mlr.press/v162/roy22a.html)、[全文](https://arxiv.org/html/2112.12228v6)、[Ubisoft研究说明](https://www.ubisoft.com/en-us/studio/laforge/news/6phoEAQOzIdkiMv8T2kLNS/direct-behavior-specification-via-constrained-reinforcement-learning)。两次定向阅读覆盖§2–6、实验设置与主实验图，核过作者/机构，未完整代码复现；查看PDF的真实环境/约束示例。

DOCUMENTED：多项行为要求难以靠reward权重反复调；以可解释的事件频率约束表示要求，并处理优化稳定性与主任务不进展。RECONSTRUCTED：先展示reward设计随约束数量恶化，再把设计者希望直接控制的量变成训练约束，不靠堆复杂网络解决含糊目标。

**研究尺度启发：** 约束满足不能通过“不行动”免费取得，目标成功和行为边界要同时测。已有工作不意味着我们能把一张目标/计划表当新方法；贡献须有新的可检验认识或明确瓶颈。

## 3. Goal Drift：持续与切换已被直接研究

来源：[全文](https://arxiv.org/html/2505.02709v1)、[PDF](https://arxiv.org/pdf/2505.02709)。本轮读方法、结果、关键历史控制和局限，查看Figure1。AIES2025/预印本谱系，不误标ICML主会。

DOCUMENTED：股票环境中设置竞争压力与暂时工具性目标，后者完成后要回到原目标；比较强提示、上下文与行为历史。作者已发现切换比单纯持续更难，并以历史改造支持模式延续解释。部分工具性阶段由程序构造，不能直接等价真实角色行动造成的状态演化。

RECONSTRUCTED：不只记录“忘了目标”，而是把忘记、行为模式延续、压力和时间分离；这正是我们需要学习的实验动作。

**直接重合风险：** “目标切换难”“历史行动影响后续”“提醒目标有帮助”均不能作为我们的新发现。NPC切口必须进一步由真实角色和世界的目标/手段/完成条件解释结果，仅换游戏皮肤不够。

## 4. Everitt等：能力不足与不运用能力必须分开

来源：[Evaluating the Goal-Directedness of Large Language Models](https://arxiv.org/html/2504.11844v1)。本轮读§1–4和能力/上下文局限；会场未据正式录用页完成核实，按2025预印本使用，不能因模板关键词ICML认定录用。

DOCUMENTED：用子任务估计模型能做到的事，再判断复合任务是否充分运用该能力；含信息收集、规划执行、受干扰动作和倒塔后重试。它已经讨论坚持性测试可能混淆自动循环与有目的行为。

**迁移：** 同一NPC变化后快照的从零执行是必要能力对照；不能把局部观测下的失败直接叫目标丢失。我们不直接复制其归一化GD指标，因为独立子任务能力可迁移是额外假设，原文也承认限制。

## 5. Arghal等：无用子目标、内部状态与计划的强近邻

来源：[2026全文](https://arxiv.org/html/2602.08964v1)、[OpenReview入口](https://openreview.net/forum?id=E3xtLUfA5E)。本轮读§3–5、关键实验/假设；OpenReview遇浏览器验证，接收身份暂不升级。

DOCUMENTED：在可控gridworld区分难度、等难变换、钥匙作为工具性子目标与无用目标样式线索，并解码内部地图/计划。无门时仍绕去拿钥匙的偏好已经有直接研究；动作与探针解码地图的一致性也不是空白。

**迁移与限制：** 先测可观察状态、能力、语义诱因，而非见到错误就归因于“意图被覆盖”。可解码不等于被因果使用；本工作台不预定SAE或探针方法，更不能仅重复无用钥匙图。

## 6. Hypothetical Minds 与 Bayesian Partner Modelling

来源：[Hypothetical Minds ICLR2025](https://proceedings.iclr.cc/paper_files/paper/2025/hash/12f483f624b378f9f3058d8ecd3c7ff5-Abstract-Conference.html)、[原文](https://arxiv.org/pdf/2407.07086)、[Bayesian Partner Modelling](https://arxiv.org/abs/2608.18490)。Hypothetical Minds沿用前轮已记录的正文/成本阅读，未重新运行。10月13日Bayesian论文仅摘要可读；10月17日已成功补核正文／附录指定部分，读取范围和对本项目的影响见下方领域补核，不再将当前范围写成只有摘要。

前者通过提出/评价/修正伙伴策略假设在线适应；后者摘要直接提出“正确推断但执行旧技能”，以伙伴矛盾驱动选择性重规划。

**主张边界：** belief–action gap、事件触发replanning都已有明确owner。相关方法比较需要说明每步/事件触发的计划更新频率，不能只以不更新计划作为弱参照。不能把其云端默认配置当本地成本。

## 7. 经典游戏规划与真正的游戏制作需求

来源：[Orkin GDC 2006](https://gdcvault.com/play/1013459/Three-States-and-a-Plan)、[GOAP十年开发者回顾](https://www.gdcvault.com/play/1022019/Goal-Oriented-Action-Planning-Ten)、[Ubisoft Teammates](https://news.ubisoft.com/en-us/article/3mWlITIuWuu0MoVuR6o8ps/ubisoft-reveals-teammates-an-ai-experiment-to-change-the-game)、[KRAFTON技术访谈](https://developer.nvidia.com/blog/how-krafton-built-pubg-ally-a-co-playable-character-powered-by-nvidia-ace/)。读取会议讲述简介和厂商技术全文，不冒称看完受限演讲视频。

GOAP早已让人物选择达成目标的行动路线。Ubisoft强调作者边界与玩家对角色行动的影响；KRAFTON区分高层语言选择和快速行为树反应。它们共同支持“稳定目的、适应局势”的制作需求，却不证明某个LM必然有缺陷。

**对照要求：** 符号规划器是必须认真考虑的强参照，不可故意只比聊天模型；高层结果和动作步骤应分开控制。商业实时小模型说明本地部署有现实动机，不提供可以免费继承的专有数据或产品效果。

## 8. 与近期角色/叙事研究的关系

KNUDGE、CDT、NCP、Dynamic Persona与最新NARRA-Gym仍需保留在认识中，不能因不用它们的pipeline而忽略。CDT有情境/多轮评价，NCP有多审核器、人类与自然输入对照，不能冒领缺失控制。NARRA-Gym评估互动叙事体验而不只是文本质量；但它的自动叙事世界不是本项目低成本状态真值。

相关前沿补查合并在下节。选择本切口的理由不是“没有近邻”，而是角色目标控制的重要性、可从本地交互中区分解释的机会，以及可能改变控制/评价认识的尺度。

## 9. 伙伴分布、协作要求与叙事评价的参照

**GAMMA（NeurIPS2024）。** [正式论文](https://proceedings.neurips.cc/paper_files/paper/2024/hash/6e9f99809b6df59e8fe5c9ffe269bf40-Abstract-Conference.html)关注训练伙伴分布无法覆盖真实玩家风格。这里的generative agent是生成伙伴政策，不是LLM。原阅读核了问题/方法及主要对照，未本地重训；伙伴数量不是目标，是否改善目标配对分布才是设计对象。模拟伙伴结果不能充当人类体验结论。

**Hypothetical Minds的成本与对照补充。** 原阅读另核正文§4.5、Appendix B.1及官方README，而非全部提示/后台分支。论文已有仅提示、模块化、假设评价与精炼对照，也有Llama-3-70B配置。1000-step RWS示例GPT-4约10美元/局，Llama3配置4卡，均为作者成本。不能把无训练当无成本；本地替换后需说明与原配方的差异。

**alem（NeurIPS2026 Evaluations & Datasets Track，作者公告）。** [原文](https://arxiv.org/html/2606.08340v1)§1–3、任务接口/依赖和评价设计已读，未全核45页。它保留布局、操控交接与同步要求，以原生文本动作检验协作；单体困难、依赖和套路不能混成一个协作分数。一个难度参数也可能改变多项机制。此处借鉴相同世界中可核依赖的研究设计，没有重训其MARL。

**NARRA-Gym（NeurIPS2026，具体track未单独确认）。** [原文](https://arxiv.org/html/2605.08503v1)框架、实验/评价、误差与局限已读，未复现。它用9模型×8persona及3judge研究互动叙事，自动与人类评价排序可能不同；持续角色、记忆、响应和体验应分开。其样本数不是其他NPC研究的充分样本门槛。

上述两项身份最初核自[alem作者公告](https://www.kaleabtessera.com/news/)、[NARRA作者页](https://jackwwj619.github.io/)及[机构公告](https://www.som.lmu.de/ai/en/update/news-overview/news/5-papers-accepted-at-neurips-2026-7c6c1c03.html)。标题目录仅作发现入口；只见标题或未取得原文的项目不补写机制。Goal-Directedness的后续正式身份/阅读范围以[单篇卡](papers/GOAL_DIRECTEDNESS_ICML_2026.md)为准。

[Collab-Overcooked（EMNLP2025）](https://aclanthology.org/2025.emnlp-main.249/)作为必要协作/过程评价的来源仍保留；原记录为初筛及指定部分阅读，不升为全文/代码复现。它与GAMMA的伙伴分布、Hypothetical Minds的策略推断是互补问题，不是一条互相继承的方法链。

<a id="field-review-2026-10-17"></a>
## 2026-10-17领域尺度补核（只读）

用户要求维持暂停、从领域尺度判断整体认识与下一实验。本次只读原文、既有本地全文／论文卡和检索定位；未启动任何引擎、模型或推理API。整体判断与建议仅维护在[I04](../ideas/I04-commitment-conflict-stage-arbitration.md)，不复制第二份报告或启动E86。

- **Bayesian Partner Modelling补读。** [HTML v1](https://arxiv.org/html/2608.18490v1)本次可读；核§4–5／Tables1–4、App8.4–9.4及10.1–10.2提示。沿用而非新建[已有论文卡§4](../../../library/themes/game-npc-social/INTERACTION_PAPER_CARDS_2026-10-03.md#4-bayesian-partner-modelling-enables-adaptive-replanning-for-llm-coordination--arxiv-2026-08)，补了精确原文范围。相同posterior只入prompt与触发技能中断的对照已做；一般重规划也能取得相近奖励但调用更多，RL基线若干场景更强，不能宣称一种中断方法普遍更优。App10.1明确共同团队得分且伙伴不能沟通，与可谈判、负有职责／承诺的NPC不同。行为识别、动作切换及事件控制已是强基线，本项目不能仅把“看出变化却仍做旧计划”当新发现。未取得／运行该文自身实现；列出的ProAgent等仓库不是其完整runner。
- **目标—手段并非概念空白。** 复核[Everitt等方法与讨论](https://arxiv.org/html/2504.11844v1)的能力条件化定义，及[Arghal等§4.3／Table1](https://arxiv.org/html/2602.08964v1)的工具性钥匙、无用钥匙与两路径控制。坚持、无用子目标与可解码计划均有前史；不能将“替代出现仍追旧物”一例独立包装。值得检验的是作者目的／职责、有效承诺与开放玩家贡献在真实闭环中怎样共同决定应保持和应改变的部分。
- **社会修订与工具修订分开。** 补核[Talk is Cheap §5.7／Appendix F](https://arxiv.org/html/2605.01750v1)：透明信息改善部分指标却未可靠提升最优率，早期提案锚定已有分析。核[ContractSim §3／Appendix B.2](https://arxiv.org/html/2608.10475v1)：允许合同条件，履约期无重谈；主履约实验fresh agent不带协商历史。核[CT-Bench AppB](https://arxiv.org/html/2607.22750v1)：重谈列为后续，不否认其已做真实自主拒付。TradeCraft仍按已全文核读的作者版本理解其未来承诺／自主制作，不因当前交易原子结算就排除其重合。我们的增量按整体可检验关系判断，不用各自实现限制虚构无人研究的空白。
- **定位检索。** 两个venue-corpus nearest查询：`goal directed role conditioned agents adapting cooperation to changing causal task dependencies and partner actions`、`language agents private goals negotiated commitments dynamic grounding alternative plans execution`；命中CaPo／COMBO、Plan-and-Act、Agent GPA等，均仅作标题定位，不新增已精读声明。网页检索同名TradeCraft还返回另一代码仓库，作者／论文对应关系本次未审，不能据同名混同原论文资产。

**本次判断。** 现有数据最强的整体认识是：角色影响真实行为，其后果随目的、请求、共同前提和用途的关系变化；单一任务分不能识别人设控制。这可作为实证研究的骨架。下一轮应检验NPC是否能按实际因果作用选择性调整合作，同时保留原作者职责与已接受义务；先面对及时重规划、普通明确说明和可靠技能，仍不预选方法、神经机制或阴性故事。它没有被标为已解决、尚未产生新证据等级；当前暂停继续有效。
