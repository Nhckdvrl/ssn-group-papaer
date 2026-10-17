# Persona、目标与原生行动：近邻定位

本页是跨论文定位，单篇身份、正文/附录/代码读取范围优先看论文卡；实验进度和自有主张只在整体报告、实验卡与CLAIMS维护。相关工作用于继承强基线和形成整体增量，不要求每个组件无人研究，也不因有近邻就自动缩窄或关闭问题。

## 已有认识与本项目要解释的关系

| 已有工作 | 已明确处理什么 | 对本研究的启发 |
|---|---|---|
| [The Personality Illusion](papers/THE_PERSONALITY_ILLUSION_2026.md)、[Rethinking Psychometric](papers/RETHINKING_PSYCHOMETRIC_2026.md) | 自述/行为效度、具体意图粒度、同/跨会话及priming | 表达、意图与执行分测；不把不一致本身当新发现。 |
| [Story Shapes the Agent](papers/STORY_SHAPES_AGENT_2026.md)、[Persona Vectors](papers/PERSONA_VECTORS_GAMES_2026.md) | 多阶段叙事先验/动作锚点、内部向量改变博弈策略 | 不能用“前人全部单步”或“首次steer策略”立论；要解释真实角色与世界条件。 |
| [PCSP](papers/PCSP_2026.md)、[PANDA](../../knowledge/papers/PERSONA_DYNAMICS_ACL2025.md) | 人物条件化行动、训练读出与独立行为、人格与任务探索 | 真实行为差是起点；本地奖励/分类器不自动成为独立人格金标。 |
| [Identity Overrides Incentives](papers/IDENTITY_OVERRIDES_INCENTIVES_2026.md)、[Persona-Guided TOD](papers/PERSONA_GUIDED_TASK_DIALOGUE_2026.md)、[Price of Agreement](papers/PRICE_OF_AGREEMENT_2026.md) | 人物×收益、明确优先、角色适配与任务grounding | 把人设/效用冲突或普通优先提示换名不够；原生任务依赖和玩家后续动作需进入解释。 |
| [DebtBench](papers/DEBTBENCH_ACL2026.md)、[MASCOT](../../knowledge/papers/MASCOT_EMNLP2026.md)、[SidConArena](papers/SIDCONARENA_2026.md)、[MMOAgent](../../knowledge/papers/MMOAGENT_KDD2025.md) | 谈判让步、社会贡献、真实多步经济与制度 | 协议、物品真正交付和本人后续目的不能互相替代。 |
| [NegaAlign](papers/NEGAALIGN_2026.md)、[AgentIF](papers/AGENTIF_NEURIPS2025.md)、[Agent GPA](papers/AGENT_GPA_2026.md) | 任务与约束共同满足、条件触发、计划质量与遵循 | 原生阶段交叉用于解释角色行为，不冒领一般否定困难或计划/执行分解。NegaAlign本已同时要求任务完成，不能误说只看违禁。 |
| [Principled Personas](papers/PRINCIPLED_PERSONAS_EMNLP2025.md)、[SimpleToM](papers/SIMPLETOM_ICLR2026.md)、[TriEx](papers/TRIEX_ACL2026.md)、[Trust/behavior](papers/TRUST_BELIEF_BEHAVIOR_2025.md) | 人格与任务效应、显式预测与应用、数值profile干预及rerun | 外部预测回答不是隐状态；相同信息和实际物理行动的干预才约束解释。 |
| [PSALM](papers/PSALM_NAACL2025.md)、[AGWM](../../knowledge/papers/AGWM_2026.md)、[SayCan](papers/SAYCAN_2022.md) | 前提反馈、动作模型、目标有用性与可执行性 | 继承可靠动作支持，仍需解释NPC选择何种目的及何时采用路径。 |
| [Dragon](../../knowledge/papers/HOW_TO_MOTIVATE_DRAGON_2021.md)、[KNUDGE](../../knowledge/papers/KNUDGE_2024.md)、[CDT](../../knowledge/papers/CDT_2026.md)、[NCP](../../knowledge/papers/NCP_2026.md) | 作者动机、专业RPG知识、情境人物逻辑、长期叙事约束 | 各有不同状态与评价对象；不能把authoring/narrator误称完整独立NPC引擎。 |

训练、投影/读出、组合控制的具体已有方法仍保留在逐篇卡：CIRL、BC-PMI、DAIL、PPG、PAMDP、SIPO、Poly-PPO等。它们已使用的对比学习、坐标对齐或辅助保护不是禁用工具；本项目要用整体证据说明角色取舍、执行条件与真实后果形成了什么新理解或改进。合作、持续目的与玩家改约的强邻近另见[合作定位](COOPERATION_AND_GOAL_POSITIONING.md)。

## 机制类原文的独有核读记录

以下五篇尚无独立单篇卡，保留完整原文范围和asset hash；这是文献事实，不是本项目已识别的内部机制。

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
