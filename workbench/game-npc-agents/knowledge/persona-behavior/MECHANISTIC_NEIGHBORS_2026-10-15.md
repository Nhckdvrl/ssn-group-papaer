# 机制强近邻与当前增量定位

正文与关键附录已在本地PDF核读，不能沿用“前人全部单步”或“人格信号被助手先验压过是新发现”。本文件区分文献事实、我们的解释和仍待实验的竞争解释；新颖性定位不自动关闭I04。

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

## 当前科学推进口径

已有可靠正面观察：三模型一致personality立场都能影响真实物品选择；32B直接对话→动作同样有+11.7pp人物差，95%[4.2,20.0]。没有统一人格耗散证据。E51/E52/E53分别检查状态词、目标对象和任务关闭对决策的作用，是同一大问题的竞争解释，不是固定论文标题。

下一步是E54已有文本盲标和E55独立200原图：比较直接选择、自己的真实台词、原计划与一句普通事实grounding；分别保存表达、意图与事件。普通强提示若解释观察就采用该解释，仍追踪尚未被它解释的跨角色矛盾。

PDF资产在cache/papers，sha256：

| PDF | SHA256 |
|---|---|
| persona_circuit_icml2026 | 6aecee2f08b1211b7eab687b45c562957d196abff4fec92cc5ef6b2d24c68bed |
| pdd_iclr2026 | c753235245a6fc1f88f3115486bd82149d11d8dd1b3d912c14aba89d4ed19814 |
| trait_activation_acl2026 | 8c1f3e167ae95ae9243a587fbdaefdfc2fd864d2a65b52d60eabde3196ebda7c |
| roleplay_beliefs_2026 | 4d2346d1823e429c0dc49fb27366d60846708fef64efab05b32188dbe9979152 |
| dream_2026 | 16b36d5d2f4c94172a3686998006f62d6b37f4d4f5218a59994e8dc55d46e3d2 |
