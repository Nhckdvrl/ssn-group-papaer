# 人物、独立目的与真实合作：最近邻及整体定位

更新：2026-10-18。先按NPC玩法与完整系统判断，再借心理测量或内部表示解释残余。文献重要性不由它是否支持现有叙事决定；有近邻不自动否定集成贡献，但不能凭一个实现差别宣称空白。自有实验与研究判断见[独立审查](../results/audits/INDEPENDENT_RESEARCH_VALUE_REVIEW_2026-10-18.md)，本页只维护来源和定位。

## 应先读的直接谱系

| 研究谱系 | 已经解释或实现什么 | 对本研究真正形成的要求 |
|---|---|---|
| ABL、GOAP、CiF、Prom Week、Versu、Slice of Life | 目标/手段、执行反馈、中断与替代、私人意愿、社会拒绝和后果；也明确作者复杂度 | 不能将重规划/阶段切换本身写成贡献；可检验新语言提议、选择性修订、跨内容泛化或更低作者成本。[原文综合](../../knowledge/FIELD_REVIEW_2026-10-18.md#classical) |
| LIGHT/Dragon、Generative Agents | 作者动机、对话与行为；过度合作、口头有意但未赴约早有观察 | 在双方各有目标、独立规则后果和真实条件变化中提出更强解释，而非再次发现言行不一。[角色证据](../../knowledge/FIELD_REVIEW_2026-10-18.md#4-角色行为与社会模拟从文本像人到可核后果) |
| GenCoord、CT-Bench、ContractSim、TradeCraft | 私有信息/利益、条件承诺、真实交接/执行、原任务与履约分离、制度与自主选择 | 最近的整体近邻，须吸收强普通成功与提示/制度修复；不能逐篇列一个缺项就拼成原创性。[完整定位](COOPERATION_AND_GOAL_POSITIONING.md) |
| GAMMA、CollabBench、BayesBeliefAgent | 伙伴分布、人类补偿、强模型合作、belief到行动及选择性重规划 | 共享团队任务和NPC私有职责不同；普通重规划与强模型必须充分工作。[合作综合](../../knowledge/FIELD_REVIEW_2026-10-18.md#cooperation) |
| Microsoft CQC、Ubisoft NEO/Teammates、PUBG Ally | 角色边界、开放玩家、条件奖励、动作反馈与真实使用 | 已有正常记忆/工具/技能和商业模型参考；原型需求、离线指标和真人结果分开。[应用核查](PLAYABLE_NPC_APPLICATION_AUDIT_2026-10-16.md) |
| CHI虚假信息感知、开放对话研究、SKT | 角色动机和可理解后果、交互修复成本、安全与合法推进 | 不将更服从、零泄露、交付率或更长对话当玩家价值。[玩家证据](PLAYER_VALUE_EVIDENCE_2026-10-16.md) |

这些工作已经覆盖当前宽泛叙事的大块内容。可研究的剩余关系是：**当合作前提或实现办法变化时，原人物目的、职责和有效义务如何选择性持续，强普通系统在哪些条件下仍处理不好，并因此限制了什么有意义的玩家行动？** 这是待检验的问题，不是已确认的文献空白或新机制。

## 解释残余时再进入的心理与机制近邻

- 自述与行为效度：[The Personality Illusion](papers/THE_PERSONALITY_ILLUSION_2026.md)、[Rethinking Psychometric](papers/RETHINKING_PSYCHOMETRIC_2026.md)、[PCSP](papers/PCSP_2026.md)。真实动作是必要证据，但一个内部或外部persona分类器都不是完整角色金标。
- 叙事与人物策略：[Story Shapes the Agent](papers/STORY_SHAPES_AGENT_2026.md)、[Persona Vectors](papers/PERSONA_VECTORS_GAMES_2026.md)、[Identity Overrides Incentives](papers/IDENTITY_OVERRIDES_INCENTIVES_2026.md)、[Persona-Guided TOD](papers/PERSONA_GUIDED_TASK_DIALOGUE_2026.md)。情境适配、任务优先和策略steering均有前史。
- 约束、计划与实际执行：[NegaAlign](papers/NEGAALIGN_2026.md)、[AgentIF](papers/AGENTIF_NEURIPS2025.md)、[Agent GPA](papers/AGENT_GPA_2026.md)、[PSALM](papers/PSALM_NAACL2025.md)、[SayCan](papers/SAYCAN_2022.md)。保留任务完成、可执行性和普通反馈控制，不先把残差叫人格失效。
- 预测与行动的关系：[SimpleToM](papers/SIMPLETOM_ICLR2026.md)、[TriEx](papers/TRIEX_ACL2026.md)、[Trust/behavior](papers/TRUST_BELIEF_BEHAVIOR_2025.md)。问答/自述和行动时内部信念不是同一证据。
- 训练与表示方法CIRL、BC-PMI、DAIL、PPG、PAMDP、SIPO、Poly-PPO等继续保留在逐篇卡；方法可复用，但选择应由强基线下剩余问题驱动。

## 机制类原文的独有核读记录

以下是此前五篇原文的唯一核读记录，本轮未逐篇重新阅读。保留原文范围和asset hash，不把旧文中的“本轮”误读为2026-10-18；这些不是本项目已识别的内部机制。

## Tracing the Persona Circuit｜ICML 2026

[官方正文](https://proceedings.mlr.press/v306/qin26h.html)。**文献事实：** §3–4以Latent Persona Vector扩展因果patch；600 trait contrast pairs，三对特质各100 discovery/100 validation。主要Llama3.2-3B，另Qwen2.5/13B验证；Character-LLM的1714单轮、450多轮和RoleBench文本评价。附录G对helpful assistant/assistant/helpful person/pirate匹配方向消融，支持人格信号与助手方向竞争；15-turn检查已做。Table1–2局部头增强改善文本人格分数并保留一般任务。PMLR只链接PDF/OpenReview；检索出的`suehuynh/icml-persona-circuit-reproduction`是第三方复现，不能当作者代码。

**我们的解释：** 泛称“知道角色但助手先验覆盖”或“少数头增强人格”已有明确owner。**竞争解释：** 本项目的动作变化可能来自这种竞争，也可能来自仍然完整的人格对具体目标/状态/条件承诺的不同解释；要以原生实体裁决和相同信息干预区分，而不是用阶段方向角度代替。

## Persona Dynamic Decoding｜ICLR 2026

[正文](https://arxiv.org/abs/2603.01438)。**文献事实：** CAPS理论→PIE语境属性重要性→PIA多目标解码；Qwen2.5-7B/Llama3-8B，CharacterEval1785多轮/77角色、BeyondDialogue3552对话、PersonalityBench180k问题。Table1为文本对比胜率；Table2的PB仍由CharacterEval文本判据打分，不是游戏引擎action。附录D有人评和规模/权重消融。

**我们的解释：** “人格影响因语境而变”和动态属性加权不是本项目新主张。**竞争解释：** 原生资源选择差可能是恰当情境适配，而非人格失效；必须保留短/中/长动机及合法行动机会，比较具体意图与实际状态。

## Trait Activation in Silicon｜ACL 2026 main

[正文](https://aclanthology.org/2026.acl-long.1792/)。**文献事实：** 十个正/负特质LoRA加DIAMONDS情境强度调制，Llama3-8B骨干；SPB-5k实际5420生成场景，情境测试85场景×25探针=2125交互，另32角色BFI。§4使用文本Trait-Situation Fit，DeepSeek-V3.2 judge；200场景人工数据校对、20场景judge校对。附录有训练/生成/评分协议。材料按论文要求验证后学术访问，不能声称已拿到其权重或源码。

**我们的解释：** 强情境压缩人物差异、助手惯性及情境LoRA已有owner。**竞争解释：** E53人物差被任务状态放大/压平可能是情境强度的实例，或是具体目标被错误地视为已完成；需要直接测状态解释和真实动作，不能只给旧理论换NPC名称。

## When Role-playing, Do Models Believe What They Say?｜2026预印本v3

[最新正文](https://arxiv.org/abs/2606.11502)。**文献事实：** 15历史人物/时代原型；prompt、ICL、SFT、OCT与EM，Llama3.3-70B/Qwen3-8B。真值probe来自800真/800假statement，包含chat-template及训练后probe重新校准；另有质疑辩护和推理推广，不能把probe角度独自叫信念。代码链接[作者仓库](https://github.com/BenSturgeon/persona-belief-probes-submission)，本轮尚未代码复现。

**我们的解释：** “角色说什么不等于内部相信什么”也已有实证owner。**竞争解释：** NPC自己台词可能是策略借口而非私有目标；E52的物品词干预改变行动，不证明原台词是错误信念或人格消失。我们的对象是可动态校验的游戏状态/目标与后续事件，不能以era-belief换皮。

## DREAM｜KDD 2026

[正文](https://arxiv.org/abs/2608.05170)。**文献事实：** Event–Belief–Consequence启发的事件图、时间约束检索和动态profile；CoSER文本/LLM评价、LifeChoice多选、TCM600场景（60人工核对），Table4消融timestamp/memory/dynamic profile。正文明确在线互动对话写回EMG仍为后续扩展。

**我们的解释：** 泛称因果事件记忆和长期角色一致性已有owner；本项目不先造新图记忆。**竞争解释：** E50差异可能被既有时间/目标记忆方法解释，或需要对实际engine event和社交意图区别建模；先用普通grounding对照和独立原生场景检查。


PDF资产在cache/papers，sha256：

| PDF | SHA256 |
|---|---|
| persona_circuit_icml2026 | 6aecee2f08b1211b7eab687b45c562957d196abff4fec92cc5ef6b2d24c68bed |
| pdd_iclr2026 | c753235245a6fc1f88f3115486bd82149d11d8dd1b3d912c14aba89d4ed19814 |
| trait_activation_acl2026 | 8c1f3e167ae95ae9243a587fbdaefdfc2fd864d2a65b52d60eabde3196ebda7c |
| roleplay_beliefs_2026 | 4d2346d1823e429c0dc49fb27366d60846708fef64efab05b32188dbe9979152 |
| dream_2026 | 16b36d5d2f4c94172a3686998006f62d6b37f4d4f5218a59994e8dc55d46e3d2 |



## AgentSense：语言交互的目标与私有信息

[AgentSense，NAACL2025 Main](https://aclanthology.org/2025.naacl-long.257/)本轮核读§3.3–4.2、Table2及模拟/评价附录入口（并非重现其结果）。1225场景由245脚本模板扩展，原生是多轮语言交互，允许语言表达动作/表情；双方有目标和私有信息。完成由self/other及三外部judge判，信息推断用选择题，PSI测换profile后的goal分数波动。已有profile、伙伴与多目标/隐私的交互认识，不能声称首次研究动态伙伴和人物目标。其文本动作不提供LIGHT的持有/消费flag。PDF SHA256 `efe9700cae93fbacf63ba374506e26efc9f1c3355f69844462534cdb35f16b3e`；本地未复现AutoGen/11模型评测。
