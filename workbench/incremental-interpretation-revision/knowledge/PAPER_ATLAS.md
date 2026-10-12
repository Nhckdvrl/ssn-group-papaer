# 全库论文图谱（按科学问题组织，而不是按日期或下载数）

> **2026-10-12 结构性重编目**。覆盖迁移来的144篇/主题卡（含数个同论文重复版本）及本次3篇新增卡；去除3个重复内容后**144份规范主卡**。这里的数字是卡片数，**不是144篇实际独立精读论文**。历史86篇MAIN为历史自报，具体阅读范围仍须看原卡和[阅读账](READING_LEDGER.json)。本目录只对核心论文作选择性原文复核，不会把每篇都称重新独立验证。机器可检索的完整登记：[PAPER_CATALOG.json](PAPER_CATALOG.json)。

## 全领域问题如何相互扣住？

| 需要回答的真实问题 | 直接证据/理论层 | 典型伪因果解释 | 桥接研究 |
|---|---|---|---|
| 输入后到时究竟更新了什么？ | H0候选、晚cue作用、完整H1依赖 | 把append和retract混写 | [经典修订](#human)、[Agent信念](#belief) |
| 模型是否真正理解还是任务错配？ | 源蕴含、问答合同、自然复述、独立用途 | 把一个No分数当作修订 | [测量](#measurement)、[LLM加工](#lm_processing) |
| 什么因素决定新关系能被使用？ | 原生关系、外给关系、反事实、下游输出 | 粗状态patch称为语义修订 | [机制](#mechanism)、[人类新旧竞争](#human) |
| 训练信号该奖励什么？ | 生成池覆盖、同内容不同措辞、reward原目标、动作收益 | 把概率分解的符号看作旧解释机制 | [评分训练](#reward)、[belief](#belief) |

## <a id="human"></a>人类的修订、残留与竞争解析（17份规范卡）

**主问题：** 人类的旧解释为什么留存：没形成新结构、局部合法而全局破碎、语义痕迹未清理，还是问句诱发？

**在下个实验之前应比较的预测：** 相同最终正确/错误分数下，主句正关系、旧错诱发、结构priming、自由复述及另一句功能后果应出现可区分组合。

**先读的关键原文（并留意卡内实读范围）：** [christianson](christianson2001-thematic-roles-linger.md) · [vangompel](vangompel2006-garden-path-priming.md) · [patson](patson2009-paraphrase.md) · [slattery](slattery2013-competing-representations.md) · [huang ferreira](huang-ferreira2021-memory-versus-parse.md) · [cehakova](cehakova2023-diverse-reanalyses.md) · [mainakilaas](mainakilaas2026-digging-in.md) · [clark](clark2026-targeted-noisy-channel.md)。

**完整主题卡**（P0=本问题最重要切入，P1=主动近邻，P2=潜在桥接/外围；优先级是研究用途而非论文质量）：

- P0: [cehakova2023 diverse reanalyses](cehakova2023-diverse-reanalyses.md) · 阅读范围见卡内 · 本轮原文复核
- P0: [cehakova2025 disrupted final interpretations](cehakova2025-disrupted-final-interpretations.md) · 阅读范围见卡内
- P0: [christianson2001 thematic roles linger](christianson2001-thematic-roles-linger.md) · 阅读范围见卡内 · 本轮原文复核
- P0: [clark2026 targeted noisy channel](clark2026-targeted-noisy-channel.md) · 历史索引
- P0: [huang ferreira2021 memory versus parse](huang-ferreira2021-memory-versus-parse.md) · 阅读范围见卡内
- P0: [mainakilaas2026 digging in](mainakilaas2026-digging-in.md) · 阅读范围见卡内 · 本轮原文复核
- P0: [patson2009 paraphrase](patson2009-paraphrase.md) · 阅读范围见卡内
- P0: [slattery2013 competing representations](slattery2013-competing-representations.md) · 历史索引
- P0: [vangompel2006 garden path priming](vangompel2006-garden-path-priming.md) · 阅读范围见卡内
- P1: [clark2025 resource rational noisy channel](clark2025-resource-rational-noisy-channel.md) · 历史索引
- P1: [malyutina2016 blended interpretations](malyutina2016-blended-interpretations.md) · 阅读范围见卡内
- P1: [sturt2007 semantic persistence](sturt2007-semantic-persistence.md) · 阅读范围见卡内
- P2: [blott2020 semantic recovery](blott2020-semantic-recovery.md) · 阅读范围见卡内
- P2: [christianson2024 rereading and question order](christianson2024-rereading-and-question-order.md) · 阅读范围见卡内
- P2: [sinclair2022 structural persistence](sinclair2022-structural-persistence.md) · 阅读范围见卡内
- P2: [sinclair2026 human lm priming](sinclair2026-human-lm-priming.md) · 阅读范围见卡内
- P2: [vandyke2006 retrieval interference](vandyke2006-retrieval-interference.md) · 阅读范围见卡内

## <a id="lm_processing"></a>语言模型的增量加工与句法歧义（11份规范卡）

**主问题：** 在线 surprisal、生成的解释、任务回答、上下文轨迹为何不一致？哪些差异是自然材料、哪些是prompt与表示模型构造？

**在下个实验之前应比较的预测：** 最终依赖的成立与surprisal/role QA/轨迹分类给出不同预测；需控制构式与模型编码方式。

**先读的关键原文（并留意卡内实读范围）：** [amouyal](amouyal2025-garden-path-humans-llms.md) · [amouyal](amouyal-2026-processing-difficulties.md) · [li](li-2024-incremental-comprehension.md) · [cao](cao-2025-disambiguation.md) · [madureira](madureira2024-restart-incrementality.md) · [storer](storer2026-incremental-contextual-trajectories.md) · [lee](lee2026-good-enough-paraphrase.md)。

**完整主题卡**（P0=本问题最重要切入，P1=主动近邻，P2=潜在桥接/外围；优先级是研究用途而非论文质量）：

- P0: [amouyal 2026 processing difficulties](amouyal-2026-processing-difficulties.md) · 阅读范围见卡内 · 本轮原文复核
- P0: [amouyal2025 garden path humans llms](amouyal2025-garden-path-humans-llms.md) · 阅读范围见卡内
- P0: [cao 2025 disambiguation](cao-2025-disambiguation.md) · 阅读范围见卡内
- P0: [lee2026 good enough paraphrase](lee2026-good-enough-paraphrase.md) · 历史索引
- P0: [li 2024 incremental comprehension](li-2024-incremental-comprehension.md) · 阅读范围见卡内
- P0: [madureira2024 restart incrementality](madureira2024-restart-incrementality.md) · 阅读范围见卡内
- P0: [storer2026 incremental contextual trajectories](storer2026-incremental-contextual-trajectories.md) · 历史索引
- P1: [jumelet2024 structural priming](jumelet2024-structural-priming.md) · 阅读范围见卡内
- P2: [han2025 reading](han2025-reading.md) · 阅读范围见卡内
- P2: [mcgee2026 syntactic encapsulation](mcgee2026-syntactic-encapsulation.md) · 历史索引
- P2: [zhou2025 error driven priming](zhou2025-error-driven-priming.md) · 阅读范围见卡内

## <a id="measurement"></a>任务构念与测量有效性（10份规范卡）

**主问题：** 模型不知道事实、不能表达、不能按题型输出，还是 gold 本身不对应文本的逻辑承诺？

**在下个实验之前应比较的预测：** 同一关系有内容等价但需求不同的读数时，模型×任务难度交互可以改变所谓能力排序；不能据成功换prompt推出语义因果。

**先读的关键原文（并留意卡内实读范围）：** [hu](hu2023-metalinguistic-measurement.md) · [hu frank](hu-frank2024-task-demands.md) · [han](han2025-causal-comprehension.md) · [yoshida](yoshida2026-surprisal-existence.md)。

**完整主题卡**（P0=本问题最重要切入，P1=主动近邻，P2=潜在桥接/外围；优先级是研究用途而非论文质量）：

- P0: [han2025 causal comprehension](han2025-causal-comprehension.md) · 阅读范围见卡内
- P0: [hu frank2024 task demands](hu-frank2024-task-demands.md) · 历史索引
- P0: [hu2023 metalinguistic measurement](hu2023-metalinguistic-measurement.md) · 阅读范围见卡内
- P0: [yoshida2026 surprisal existence](yoshida2026-surprisal-existence.md) · 历史索引
- P2: [denning2026 thematic role knowledge](denning2026-thematic-role-knowledge.md) · 阅读范围见卡内
- P2: [gum natural reference assets](gum-natural-reference-assets.md) · 阅读范围见卡内
- P2: [mccoy2019 nli heuristics](mccoy2019-nli-heuristics.md) · 阅读范围见卡内
- P2: [spaulding2025 proto role context](spaulding2025-proto-role-context.md) · 历史索引
- P2: [upadhye2020 discourse reference prediction](upadhye2020-discourse-reference-prediction.md) · 阅读范围见卡内
- P2: [wang2026 implicit grammaticality](wang2026-implicit-grammaticality.md) · 历史索引

## <a id="mechanism"></a>可解码、因果绑定与跨用途（26份规范卡）

**主问题：** 有表征但不用、局部整体干预、位置/词汇/直接指针混用，如何与新旧语义依赖建立真正可证伪的因果连接？

**在下个实验之前应比较的预测：** 反事实应使两种机制对同一输出给出不同预测，并有无关/反向依赖对照，不能从whole-state patch直接读出唯一机制。

**先读的关键原文（并留意卡内实读范围）：** [hanna](hanna-2024-gp-mechanisms.md) · [mueller](mueller2025-right-causal-mediator-survey.md) · [feng](feng2024-binding-ids.md) · [gur arieh](gur-arieh2026-mixed-binding-retrieval.md) · [lepori](lepori2026-in-context-deployment.md) · [li](li2026-causal-quotient-belief-state.md)。

**完整主题卡**（P0=本问题最重要切入，P1=主动近邻，P2=潜在桥接/外围；优先级是研究用途而非论文质量）：

- P0: [feng2024 binding ids](feng2024-binding-ids.md) · 历史索引
- P0: [gur arieh2026 mixed binding retrieval](gur-arieh2026-mixed-binding-retrieval.md) · 历史索引
- P0: [hanna 2024 gp mechanisms](hanna-2024-gp-mechanisms.md) · 阅读范围见卡内
- P0: [lepori2026 in context deployment](lepori2026-in-context-deployment.md) · 历史索引
- P0: [li2026 causal quotient belief state](li2026-causal-quotient-belief-state.md) · 历史索引
- P0: [mueller2025 right causal mediator survey](mueller2025-right-causal-mediator-survey.md) · 历史索引
- P0: [wang2026 predictive sufficiency](wang2026-predictive-sufficiency.md) · 历史索引
- P1: [jung2026 trimodal binding](jung2026-trimodal-binding.md) · 历史索引
- P1: [li2026 hop generalization](li2026-hop-generalization.md) · 历史索引
- P2: [aljaafari2026 semantic role circuits](aljaafari2026-semantic-role-circuits.md) · 历史索引
- P2: [balcells2026 belief state geometry](balcells2026-belief-state-geometry.md) · 历史索引
- P2: [chen2026 perk parametric context](chen2026-perk-parametric-context.md) · 历史索引
- P2: [chung2026 state tracking error control](chung2026-state-tracking-error-control.md) · 历史索引
- P2: [elhelo2026 task specific knowledge](elhelo2026-task-specific-knowledge.md) · 历史索引
- P2: [gurnee2026 workspace selected sections](gurnee2026-workspace-selected-sections.md) · 历史索引
- P2: [lee2026 contrastive qk](lee2026-contrastive-qk.md) · 历史索引
- P2: [liu2026 lens semantic perspective](liu2026-lens-semantic-perspective.md) · 历史索引
- P2: [liu2026 rilke lifelong representation control](liu2026-rilke-lifelong-representation-control.md) · 历史索引
- P2: [lubana2026 priors in time](lubana2026-priors-in-time.md) · 历史索引
- P2: [prakash2026 lookback belief tracking](prakash2026-lookback-belief-tracking.md) · 阅读范围见卡内
- P2: [sbrolli2026 compositional binding](sbrolli2026-compositional-binding.md) · 历史索引
- P2: [uselis2026 binding functions](uselis2026-binding-functions.md) · 历史索引
- P2: [wang2023 belief representations](wang2023-belief-representations.md) · 历史索引
- P2: [zhang2026 attribution patching curvature](zhang2026-attribution-patching-curvature.md) · 历史索引
- P2: [zhang2026 theory of space](zhang2026-theory-of-space.md) · 历史索引
- P2: [zhao2026 faithful activation verbalization](zhao2026-faithful-activation-verbalization.md) · 历史索引

## <a id="belief"></a>前提、信念状态与Agent记忆更新（25份规范卡）

**主问题：** 新增条件何时应保持、撤回、增补关系；压缩时丢失的是哪些任务必需内容，状态文本如何影响后续动作？

**在下个实验之前应比较的预测：** 更新/保持/仅补充三种语义操作不应混为时间顺序；标明native belief、oracle content与行动结果。

**先读的关键原文（并留意卡内实读范围）：** [wilie](wilie2024-belief-revision.md) · [lidayan](lidayan2026-abbel.md) · [tang](tang2026-rebel.md) · [xu](xu2026-contextual-belief-management.md) · [wang](wang2026-predictive-sufficiency.md)。

**完整主题卡**（P0=本问题最重要切入，P1=主动近邻，P2=潜在桥接/外围；优先级是研究用途而非论文质量）：

- P0: [chen2026 revision versus elaboration](chen2026-revision-versus-elaboration.md) · 阅读范围见卡内
- P0: [lidayan2026 abbel](lidayan2026-abbel.md) · 历史索引
- P0: [tang2026 rebel](tang2026-rebel.md) · 历史索引
- P0: [wang2026 dark room reward](wang2026-dark-room-reward.md) · 历史索引
- P0: [wilie2024 belief revision](wilie2024-belief-revision.md) · 历史索引
- P0: [xu2026 contextual belief management](xu2026-contextual-belief-management.md) · 历史索引
- P1: [hase2024 rational belief revision](hase2024-rational-belief-revision.md) · 阅读范围见卡内
- P1: [huang2026 testable belief survey](huang2026-testable-belief-survey.md) · 历史索引
- P1: [xiong2026 hypothesis generation updating](xiong2026-hypothesis-generation-updating.md) · 历史索引
- P1: [zhou2026 jitmem read time curation](zhou2026-jitmem-read-time-curation.md) · 历史索引
- P2: [bozdag2026 learned persuasion](bozdag2026-learned-persuasion.md) · 历史索引
- P2: [chen2026 srl survey](chen2026-srl-survey.md) · 历史索引
- P2: [ding2026 state commitment](ding2026-state-commitment.md) · 历史索引
- P2: [li2026 attrimem](li2026-attrimem.md) · 历史索引
- P2: [li2026 memtrain](li2026-memtrain.md) · 历史索引
- P2: [liao2026 belief memory](liao2026-belief-memory.md) · 历史索引
- P2: [lu2026 structured episodic event memory](lu2026-structured-episodic-event-memory.md) · 历史索引
- P2: [qi2026 metarag](qi2026-metarag.md) · 历史索引
- P2: [smolin2026 beliefs behavior](smolin2026-beliefs-behavior.md) · 历史索引
- P2: [tan2026 ctrl rag](tan2026-ctrl-rag.md) · 历史索引
- P2: [tang2026 entity tracking state changes](tang2026-entity-tracking-state-changes.md) · 阅读范围见卡内
- P2: [tang2026 memory reward bench](tang2026-memory-reward-bench.md) · 历史索引
- P2: [yalon2026 belief guided agency](yalon2026-belief-guided-agency.md) · 历史索引
- P2: [yan2026 memory r2](yan2026-memory-r2.md) · 历史索引
- P2: [yangjia2025 spontaneous retraction](yangjia2025-spontaneous-retraction.md) · 历史索引

## <a id="reward"></a>候选生成、选择、评分与学习（26份规范卡）

**主问题：** 生成池缺少正确依赖、选择器漏选、重建奖赏偏好别的对象、还是长期动作没有读出正确内容？

**在下个实验之前应比较的预测：** 从固定语义候选×表述×是否需修订交叉开始；评分改变只有连接原生coverage与新用途才有机制含义。

**先读的关键原文（并留意卡内实读范围）：** [lidayan](lidayan2026-abbel.md) · [yin](yin2026-ledom-v4.md) · [yerram](yerram2024-time-reversal.md) · [kamoi](kamoi2024-self-correction-survey.md) · [min](min2022-channel-prompting.md) · [wang](wang2026-dark-room-reward.md)。

**完整主题卡**（P0=本问题最重要切入，P1=主动近邻，P2=潜在桥接/外围；优先级是研究用途而非论文质量）：

- P0: [kamoi2024 self correction survey](kamoi2024-self-correction-survey.md) · 历史索引
- P0: [min2022 channel prompting](min2022-channel-prompting.md) · 历史索引
- P0: [yerram2024 time reversal](yerram2024-time-reversal.md) · 历史索引
- P0: [yin2026 ledom v4](yin2026-ledom-v4.md) · 历史索引
- P2: [abhinandan2026 question first echoing](abhinandan2026-question-first-echoing.md) · 历史索引
- P2: [abu hara2026 r2po](abu-hara2026-r2po.md) · 历史索引
- P2: [deng2026 selection refinement](deng2026-selection-refinement.md) · 历史索引
- P2: [dukic2025 sift generative labeling](dukic2025-sift-generative-labeling.md) · 历史索引
- P2: [gupta2026 modality consistency ttt](gupta2026-modality-consistency-ttt.md) · 历史索引
- P2: [hatamizadeh2026 igrpo](hatamizadeh2026-igrpo.md) · 历史索引
- P2: [hu2026 context sensitive ssc grpo](hu2026-context-sensitive-ssc-grpo.md) · 历史索引
- P2: [hu2026 reasoning mechanisms survey](hu2026-reasoning-mechanisms-survey.md) · 历史索引
- P2: [huang2026 test time scaling theory](huang2026-test-time-scaling-theory.md) · 历史索引
- P2: [jang2026 described versus sampled distributions](jang2026-described-versus-sampled-distributions.md) · 阅读范围见卡内
- P2: [leviathan2025 prompt repetition](leviathan2025-prompt-repetition.md) · 阅读范围见卡内
- P2: [liu2025 selfelicit evidence](liu2025-selfelicit-evidence.md) · 历史索引
- P2: [luo2026 query visibility](luo2026-query-visibility.md) · 历史索引
- P2: [pres2026 self ctrl](pres2026-self-ctrl.md) · 历史索引
- P2: [queipo2026 mix compress refine](queipo2026-mix-compress-refine.md) · 历史索引
- P2: [rao2026 correct chain wrong answer](rao2026-correct-chain-wrong-answer.md) · 历史索引
- P2: [schiff2026 proseco](schiff2026-proseco.md) · 历史索引
- P2: [xie2026 position bias opd](xie2026-position-bias-opd.md) · 历史索引
- P2: [yang2026 intervention training](yang2026-intervention-training.md) · 历史索引
- P2: [zeng2026 sage](zeng2026-sage.md) · 历史索引
- P2: [zhai2026 core remasking](zhai2026-core-remasking.md) · 历史索引
- P2: [zhu2026 prefix steering](zhu2026-prefix-steering.md) · 历史索引

## <a id="adjacent"></a>领域边缘及方法借鉴（不自动成为主线）（29份规范卡）

**主问题：** 来自视觉、生成控制、报告改写、实体语义等研究，哪一项实验设计真正改变当前竞争解释，而不是看到相似词就迁移？

**在下个实验之前应比较的预测：** 只有具体干预对象与预测可映射到本线的语义关系时才从旁证进入核心。

**先读的关键原文（并留意卡内实读范围）：** [chen](chen2026-revision-versus-elaboration.md) · [chen](chen2026-report-revision-regression.md) · [hassan](hassan2026-echoing.md) · [kim](kim2023-questionable-assumptions.md)。

**完整主题卡**（P0=本问题最重要切入，P1=主动近邻，P2=潜在桥接/外围；优先级是研究用途而非论文质量）：

- P0: [chen2026 report revision regression](chen2026-report-revision-regression.md) · 历史索引
- P0: [hassan2026 echoing](hassan2026-echoing.md) · 阅读范围见卡内
- P0: [kim2023 questionable assumptions](kim2023-questionable-assumptions.md) · 阅读范围见卡内
- P2: [britton2024 discourse connectives](britton2024-discourse-connectives.md) · 阅读范围见卡内
- P2: [capuano2023 negation alternatives](capuano2023-negation-alternatives.md) · 阅读范围见卡内
- P2: [dhanda2026 deltalogic](dhanda2026-deltalogic.md) · 阅读范围见卡内
- P2: [dipta2025 de presuppose](dipta2025-de-presuppose.md) · 历史索引
- P2: [gong2026 timelitmus](gong2026-timelitmus.md) · 阅读范围见卡内
- P2: [hong2024 script causal inference](hong2024-script-causal-inference.md) · 阅读范围见卡内
- P2: [lacina2026 focus alternatives](lacina2026-focus-alternatives.md) · 阅读范围见卡内
- P2: [li2021 wikievents informative roles](li2021-wikievents-informative-roles.md) · 阅读范围见卡内
- P2: [li2025 epistemic modality](li2025-epistemic-modality.md) · 阅读范围见卡内
- P2: [liu2026 meta factivity](liu2026-meta-factivity.md) · 历史索引
- P2: [ma2026 cross view rereason](ma2026-cross-view-rereason.md) · 历史索引
- P2: [mann2025 ironic negation](mann2025-ironic-negation.md) · 阅读范围见卡内
- P2: [park2025 poco overcorrection](park2025-poco-overcorrection.md) · 历史索引
- P2: [pres2026 consistency position](pres2026-consistency-position.md) · 历史索引
- P2: [pucci2026 primed production](pucci2026-primed-production.md) · 阅读范围见卡内
- P2: [rai2026 frame event inference](rai2026-frame-event-inference.md) · 阅读范围见卡内
- P2: [rana2026 negative instruction pressure](rana2026-negative-instruction-pressure.md) · 阅读范围见卡内
- P2: [seo2025 neghalu](seo2025-neghalu.md) · 阅读范围见卡内
- P2: [shnaidman2026 false context recovery](shnaidman2026-false-context-recovery.md) · 阅读范围见卡内
- P2: [singh2026 agent brace](singh2026-agent-brace.md) · 历史索引
- P2: [wagner2026 word world probabilities](wagner2026-word-world-probabilities.md) · 阅读范围见卡内
- P2: [wang2025 false assumptions](wang2025-false-assumptions.md) · 阅读范围见卡内
- P2: [woergoetter2026 existential presupposition](woergoetter2026-existential-presupposition.md) · 阅读范围见卡内
- P2: [xu2025 sata bench](xu2025-sata-bench.md) · 阅读范围见卡内
- P2: [zhang2026 vision language synergy](zhang2026-vision-language-synergy.md) · 历史索引
- P2: [zhou2026 negation](zhou2026-negation.md) · 阅读范围见卡内

## 重复卡归一（保留历史链接，不保留第二套正文）

- `storer2026-contextual-trajectory.md` → [规范卡](storer2026-incremental-contextual-trajectories.md)：同一篇2610.00840，早期与较深版本去重。
- `gur-arieh2026-mixing-entity-retrieval.md` → [规范卡](gur-arieh2026-mixed-binding-retrieval.md)：同一篇2510.06182v2，旧只读§1–3.4与后续主文深读合并。
- `vangompel2006-structural-priming.md` → [规范卡](vangompel2006-garden-path-priming.md)：前一轮新建造成的重复卡，合并到原JML论文卡。

完整历史正文可以从[迁移时main提交](https://github.com/Nhckdvrl/ssn-group-papaer/tree/86c84ba09575c5e2baf5ec7a675784edd2a6859c/workbench/incremental-interpretation-revision/knowledge)定位；后一轮新卡的源在相应提交。历史索引链接继续可打开，但以规范卡为唯一实质内容。

## 研究边界

这个图谱是在**认知上组织论文关联**，不是自动宣称“阅读全部论文”或“最近邻已穷尽”。任何一个问题的主张应去[证据图](03_EVIDENCE_GRAPH.md)检查旧实验反证、再去[概念测量](02_CONSTRUCT_AND_MEASUREMENT.md)确认读数。新增论文先决定它改变了**哪个竞争解释的预测**，再选择主分类；同一篇可被多个主题引用但只有一个规范论文卡。维护协议见[LITERATURE_MAINTENANCE.md](LITERATURE_MAINTENANCE.md)。
