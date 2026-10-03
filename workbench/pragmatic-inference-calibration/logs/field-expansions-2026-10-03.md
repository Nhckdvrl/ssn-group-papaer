# 历史拓展记录：已退出当前执行计划

2026-10-03用户要求清理额外扩展。下文保留原判断的审计轨迹；其中“当前”“下一步”“正在运行”均指记录时，不能用于调度。当前研究判断见[FIELD_SYNTHESIS](../FIELD_SYNTHESIS.md)。不删除既有结果，不作为原对象已失败的证据。

# 扩大视野后的研究判断 — 2026-10-03

**当前推进 C01/C02、P02/P06：先确认 parent 仪器，再寻找语用边界的科学对象。** 没有 mature finding、没有预设 paper claim。初始 SDT 解释可以被推翻；不能把技术校对包装成贡献。

## 1. 问题比“推断得多不多”更大

好的理解至少需要回答四个问题：说话者本来可以说什么？为什么选择这句话？听者据此相信什么？新信息出现后，哪些理解应该撤回？这四步还受说话者知识、当前交际问题（QUD）、礼貌/真实/合作目标，以及双方是否真正确认共同背景影响。

因此，当前最有潜力的对象是**模型如何根据交际证据调整一个具体含义的可信程度与承诺程度**。全局 criterion 只是一个简化描述；如果不同现象/规范下变化方向相反，就应研究条件结构，不能加限定条件保住“更爱脑补”的故事。

我们要分开五种可观测量：备选表达的预期、对候选含义的判断、模型选择的回答、人群判断分布、互动中的修正行为。它们之间的差需要实验解释，不能先命名为“知道但不用”或“能力下降”。

## 2. 领域地图：哪些压力已经成立，哪些解释还没有

| 研究线 | 已成立的压力/ownership | 对当前方向的修正 |
|---|---|---|
| 细粒度理解与测量：Hu2023、Hu & Levy2023、Wu2024 | 总分不足；elicitation影响读数；free-form与MCQ不同 | 原MCQ字母/选项文本概率仍是metalinguistic。原始next-token不能自动被当成知识透明窗口 |
| 自然推断强弱：Degen2015、Hu et al. TACL2023 | scalar inference不是稳定二值规则；自然电话对话中变化很大，备选表达预期提供解释 | 优先利用自然graded变化；不能只造奇怪context证明bug。不能把“all”的词频变化等同概念备选可用性 |
| 语境许可：DRInQ、PaCE、SALT35 | 正确推断依赖语境、QUD和说话者知识；过强解释已被研究 | “context flip发现脑补”不是新颖性。需要分清事实概率与交际证据、保持candidate q不变 |
| 训练阶段：ALTPRAG、Wu2024、PragReST | post-training改变任务表现；已有语用训练方法和unsupported-inference分析 | 不能claim第一次看训练阶段、第一次counterfactual修复。干净stage谱系与同题同读数是归因前提 |
| 人类分布：Wavelength、PROBCOPA、Graded Expectations | 均值接近人可能伴随不同分布；base与post-trained的概率读数可能排序不同 | “模型分布更尖”已拥有。人群异质性不等于单模型认识不确定性，采样温度也不必模拟人群 |
| 目标与策略：Murthy et al. ICLR2026、RSA理论 | 沟通目标权重随prompt/reasoning/training变化；目标条件影响可说的备选集合 | generic“alignment改变bias”不足。需要新的自然条件结构或重新归因，而非再拟合一个参数 |
| 多模态/角色：non-verbal、presupposition、listener–speaker | 输入表达形式、判断/生成角色、reasoning与judgment可以分离 | 把全部失败压成同一个criterion可能丢掉真正重要的边界；这些分离本身也不是新claim |
| 互动与共同背景：common-ground survey、ACL2026 referential game | grounding是双方逐步建立的过程；重复用词与更多确认不自动代表共同理解 | 将静态“许可”推广到修正/撤回值得研究，但“LLM不会grounding”已拥有，要审记忆、视觉、顺序与prompt混杂 |

总体地图依据[ACL2025语用综述](https://aclanthology.org/2025.acl-long.425/)及[共同背景综述](https://aclanthology.org/2025.luhme-1.2/)。前者覆盖57篇资源、仅11篇含非英语；它没有充分覆盖语言学实验，所以继续向认知科学与语义学回溯，不能把综述遗漏当gap。

## 3. 三条最有信息量的 tension

**任务答案变好，不一定说明更会利用交际证据。** ALTPRAG与PaCE提出这个压力，但两套任务、judge、提示与人类指令并不匹配。目前不能从它们的均值差推导统一latent criterion。E12将同一OLMoE Base/SFT/DPO放在Hu原材料上；E16检查bare/chat依赖。仍然没有可靠的licensed/unlicensed标签，暂不报SDT。

**模型可预测备选表达，但是否正确使用了“没有说出来”这条证据？** [Hu et al. TACL2023](https://aclanthology.org/2023.tacl-1.50/)用自然语境与跨scale人类数据解释推断强度；[SALT35](https://journals.linguisticsociety.org/proceedings/index.php/SALT/article/view/35.004)发现conditional perfection受QUD与speaker epistemic access约束。高expectedness不足以许可推断：说话者也必须知道/能够选择更强表达。E13先复现原BERT readout，再考虑这两类证据如何交互；不会把模板概率直接叫推断能力。

**人类式分布、正确解释与适当行动的目标可能不同。** Wavelength均值与distribution、PROBCOPA的graded judgments、Graded Expectations的continuation预测、ICLR2026的礼貌目标都在测不同对象。对“人会说什么”的预测和对“助手应该怎么回答”的规范要求也不同。它们不能通过一个human-alignment平均分相互替代。这个区分本身还不是论文，只有在同材料受控读数中改变已有科学归因才有价值。

## 4. 阅读暴露的测量风险，先登记而不放大成故事

- Hu原人类数据已重建：169项、63,206对应响应，Correct码零失配；3项人类modal与gold不同，全部保留。公开honesty Control没有相应人类分布；no-story不是negative。
- Multi四语言各原300题，gold A–E各60，literal中各12，已有位置平衡。E14用同题四个A–D轮转进一步测逐项稳定性；E固定以保留“以上皆非”的语义。它审查位置混杂，不提供FPR。
- ALTPRAG发布1298行与论文过滤650/交换1300需对齐；base入口默认URIAL。PaCE Appendix F给human literal额外严格指令。都限制“训练导致变化”的直接归因。
- [Graded Expectations](https://aclanthology.org/2026.scil-main.46/) Eq.4以人类completion频数 m(c) 加权model score。**我们的数学核对**：若候选集合与human目标均只含unambiguous L/T，且model给所有completion相同score，预测lie mass就等于human lie比例；若还含ambiguous，则null为包含其频数的lie比例。故相关性解释需要count-only/context-free null与候选覆盖核对。尚未取得原code/data，不据此宣布论文错误或泛化其stage结论。
- ICLR2026认知模型使用model自己的literal-semantics读数、拟合目标权重，held-out预测优于随机参数是有价值证据，但不等于参数完全可识别或真实神经机制。不能绕过其ownership再claim“第一次用目标解释alignment”。
- non-verbal测试明确告诉双方忠实参与沟通；推断silence不能无条件推广到所有无回应。presupposition以judge checklist衡量reasoning，不直接证明latent reasoning质量。互动referential game存在视觉/对象顺序/长history因素，不能把accuracy下降一概归grounding。

## 5. 三个研究动作种子，不承诺方向或novelty

| 种子 | 值得弄清楚的未知 | 便宜但有区分力的动作 | 现有ownership及什么才可能够主会 |
|---|---|---|---|
| S1：交际证据的条件门控 | 当备选表达很可用、但说话者无充分知识时，模型如何调整推断？post-training是否同时改变这两类证据的作用？ | 先E13原理论复现；取得SALT原材料/人类norm；保持utterance与candidate q，分别改变QUD、speaker knowledge，和自然graded数据交叉验证 | scalar variability、context licensing均已拥有。需要跨现象稳定的证据交互/训练阶段重新归因，单模型单prompt效应不足 |
| S2：推断的可撤回性 | 新证据到来时，模型是否同样能撤回自己推出来的含义与别人明确说过的含义？确认、拒绝和未确认如何影响更新？ | 从真实grounding/repair corpus找自然已发生的取消/修正；对同候选q比较证据来源，加入事实记忆、literal contradiction和history长度对照；优先找边界 | grounding/repair、belief revision已有大量近邻。必须显示语用证据来源的独特、可重复作用；不能只是长上下文/锚定bug。材料未驻留，不立即造dataset |
| S3：描述预测到规范作答的迁移 | 对别人意图的预测与助手采取的沟通规范，在哪些自然情境一致或分离？人类歧义被保留还是被答案要求压成一个判断？ | 对相同自然材料保留human分布；先E15/E16/E17检查角色与readout；再找真正需要判别两种规范的现有human材料 | listener–speaker、Graded Expectations、ICLR目标权重已拥有。必须揭示新的规范条件结构或改变parent归因；generic“预测≠行动”不算增量 |

优先度不是论文押注：S1有明确理论与轻量自然资产；S2面向真实沟通后果但材料/近邻审计仍不足；S3帮助审查归因但compression risk最高。没有把任何种子升级为PROMISING；D1/D2不为idea配额硬挂I##。

如果现有证据只剩格式/位置效应，就将它们留作仪器改进，回到这三个未知。若S1只在加三层限定后成立，同样退回territory，不继续局部修补。成熟结果最终应是一句跨材料可检验的事实，不能靠介绍pipeline制造重要性。

## 6. 手段要丰富，但围绕可排除的解释

| 解释 | 优先读数/对照 | 单独不能支持什么 |
|---|---|---|
| 语境没被表示/利用 | 同utterance、不同自然context；bidirectional/causal信息边界匹配；candidate概率 | 低MCQ分不证明没有语言知识 |
| 备选不可用或speaker不知道 | alternative expectation与speaker access分开操纵；human norm | 高alternative概率不许可排除其真值 |
| 输出/角色策略不同 | bare/chat、固定预算、位置轮换、概率/采样、完整invalid报告 | 一句恢复不证明整体能力正常 |
| human分布是异质人群 | participant与item层分开；重复人类norm；候选频数null | token entropy不等于人群意见分歧 |
| 共识未建立/无法撤回 | 自然repair轨迹、明确确认/拒绝、记忆与顺序阳性对照 | 更多确认或高lexical overlap不等于成功grounding |
| 训练阶段真正改变对象 | 同族真实checkpoint、相同输入与elicitation、跨family重复 | 一个Base/Instruct pair不能独立归因RLHF算法 |

Frozen inference优先；机制只在稳健边界后进入，训练只在真实bottleneck出现后考虑。闭源judge不作为主实验成立的条件。

## 7. Blog怎样改变我们的判断

[Kempner作者blog](https://kempnerinstitute.harvard.edu/research/deeper-learning/using-cognitive-models-to-reveal-value-trade-offs-in-language-models/)促使我们读到ICLR2026完整正文与关键实现附录：alignment的沟通目标权重已有明确研究，因此不能把criterion换名为utility就当创新。

[Wolfgang Schwarz的RSA讲解](https://www.umsu.de/blog/2023/791)把共同知识、可用表达、speaker goals和递归终点写成可执行模型。这帮助检查我们的推断许可究竟依赖哪个假设，而非把所有隐含意义当“更会脑补”。Blog用于提出假设，实证依据仍回原论文。

RSA-Control作者blog和probmods/problang网页本轮访问失败，**未读，不计入覆盖**。最新检索新增[ACL2026 goal-directed alternatives](https://aclanthology.org/2026.acl-long.1814/)，拥有备选集合定义改变生产成本解释的claim，正文§3–7与limits已读；cannot claim首次把goal/alternative集合分开。

## 8. 当前实验优先级

E12同源stage及E16elicitation排除训练归因混杂；E13复现解释型自然parent；E15补跨任务14B边界；E17核对human分布读数。E14用于审仪器，完成后不追着位置偏差做无休止prompt优化。全部结果先审bug并更新证据账本；不根据GPU空闲临时制造需要证明的claim。

论文阅读覆盖见[题材库](../../../library/themes/pragmatic-inference/README.md)，实验状态与数字见[工作台](../README.md)。下载PDF不算全文阅读，正文/关键附录/代码各自注明。

## 9. 本轮证据怎样修正问题

E13/E18已复现TACL2023的string predictor：原BERT8例及GPT2 294可对照值数值匹配；不同scalar材料关联差异本身是parent已有压力，尚无concept主回归复现。E17三模型各3200采样，采样均值对原likelihood MAE差三CI均含零，削弱单纯“受限概率归一化”解释；不是证明所有readout相同。E19原EPITOME评分可复现，但partial speaker access仍可排除某些候选，故**许可应针对具体q与具体证据，不能是全局knowledge=0/1 gate**；数词literal排除与交际implicit排除也必须区分。知识识别与使用的gap已由EPITOME和eliciture拥有，不把此gap换名字作贡献。

E20完整原下注elicitation在若干模型上不能产生有效完整下注；这是仪器不适用，不是能力negative，也不值得局部改prompt救故事。下一动作E21驻留新的直接近邻[ImplicatureX](https://arxiv.org/abs/2607.25094v2)：原四类natural/synthetic材料和prior/cancel/irrelevant/negation/strengthening对照。同baseline字节一致，source剔除双否定bug遵循canonical271；其较小Qwen3-4B natural recognition=.78与human相同已经在Table6，不能只追最大模型叙述。

S2的ownership因此需要明确：**首次观察LLM不善于撤回不是我们的对象**。仍值得弄清楚的是，模型的更新是否区别交际上有证据的新信息与无关续句，这种区别怎样依赖最初推断的来源/知识许可/交际目标；以及post-training到底改变哪一环。parent已有多控制，原Approx随机移植的续句是否真正中性需semantic/human核对，不能拿它无条件定义false alarm。E21是原协议复现和readout边界，不是宣布新metric或finding。若最终只剩同一系统的MCQ格式差异，不升scientific claim。

跨这些parent最值得继续问的未知仍不是“怎样写成论文”，而是**LLM会否对不同来源与强度的交际证据采取有区别的更新，而训练阶段如何改变这个区别**。这个问题尚未形成mature scientific object；要让固定自然材料、可靠norm和matched stage证据决定走向。

## 10. 新定位与训练阶段校对：没有统一“更爱脑补”结论

Goodman/Stuhlmüller2013全文再次说明partial knowledge可以只取消某个候选含义，非全局推断开关；utterance one与exactly-observed one不能混为字面证据。CoNLL2021已把同题两侧pair correctness和默认connective偏好分开，因此“发现accuracy混淆倾向”本身很老。新近邻[ACL2026 accommodation](https://aclanthology.org/2026.acl-long.736/)已有QUD/可靠性/encoding、纠正与false-positive对照及多轮pushback；[Social Meaning2026](https://arxiv.org/abs/2604.02512v2)直接拥有结构对但强度偏、alternative/knowledge-motive提示交互。这些是定位边界，不能桌面kill。

E22 Qwen matched bare里，Instruct比Base的scalar initial endorsement下降.110 CI[−.210,−.010]，cancel-minus-irrelevant更负.148 CI[−.277,−.028]；natural initial下降.283 CI[−.350,−.208]但连续条件差+.026 CI[−.007,.059]。**仍是待norm/入口/强模型检查的任务描述**，不是统一criterion或能力结论。OLMoE旧chat逐prompt SHA不一致：Base tokenizer BOS=None，SFT BOS50279；共享Jinja没共享实际token。旧chat阶段归因隔离，bare1365/784/3252字串token parity通过；E27固定完整SFT tokenizer并交叉BOS0/50279。

E26原下注Base bare746/760有效，common-chat0/760有效；Instruct bare713/common-chat741。这是读数的可用性边界，不能拿invalid作为语用错，不能挑入口救分数。目前最值得继续弄清楚的仍是**训练改变的到底是哪一类交际证据的使用，以及这些作用能否跨自然现象保留**。不把位置、浮点、模板修复写成paper主题。

ProbLang Chapter2知识模型与summary已读，教学解释不作为新的实验证据；其sample-belief与expected-utility两个模型需区分，未直接拟合或把一个拟合参数叫真实机制。

## 11. 回到最初的问题：不能只看一侧恢复

E29知识读数已经出现了原问题的一种测量风险：Q3的role澄清让full-access看起来恢复，但partial-access的知识规范更差，负问也不一致。这还不是语用推断false-alarm结果，因为knowledge问句与推断许可并非同一对象；它说明不能把“说者是否知道”的单侧高分当解释其它任务的可靠变量。E31使用原四变体在8B/14B验证边界，不继续堆恢复prompt。E27三stage匹配输入后也没有统一更爱推断：聊天初始support下降，裸入口方向不同且support极弱。现在仍未识别可以跨任务归因的criterion。

CoNLL2026 Sense and Sensitivity全文补读提醒：稳定性与human对应也必须分开，真实生成推理提高鲁棒性不自动提高human approximation；该claim已有ownership。DRInQ公开subset全量审核不提供固定candidate的足够语境pair，不能草率用它搭统一d-prime。当前优先是强自然parent边界与原规范的适用性，仍没有成熟paper claim。CEI/VakyArth最新preprint仅局部浏览，本轮未计入已读论文卡。


## 12. 自然材料与强端点带来的修正

构念校对：E33的“B probably meant Yes”衡量听者对意图解释的不确定性，不自动等于“B meant Probably Yes”所表达的说者不确定性。人群投票分布也不等于模型内在不确定性。Circa的条件/频率回答、IQAP意图分类、projection的speaker certainty必须分别保留；目前没有证据支持把三者统一称为一个“推断强度”变量。E33数值仍是预先声明的原意图候选读数，降级的是跨构念解释。

E28/E31/E32补齐8B/14B及原alternative expectedness；E33真实IQAP human分布和E34原Circa同question自然回答完成。IQAP方向随强端点改善，Circa有条件解释也相当成功，这削弱“模型普遍不会调整强度”的大故事。负强度读数可以被选项顺序彻底改写；E36平衡的单句强度要求和E37原Flan native对照显示，强侧改善常伴弱侧恶化。因此局部prompt修补分支已经达到有界控制终点，不再给它加限定把instrument artifact保成paper。

我们现在还不知道的是：**在字面证据相同而交际上可用于推断的证据不同的自然情境，强模型会不会做对相应的推断变化？** 目前Circa同问题换回答同时换semantic content/难度；IQAP是人群graded判断，不能直接因果解释speaker certainty。需要真实上下文、原人类norm和候选意义固定的材料，先检查信息是否真的可识别，再决定实验。NAACL2022 SwDA-IA的真实对话/上下文效应、NAACL2025 projection/RSA的belief attribution是新驻留入口，阅读与源码检查进行中；不立即再下载20个benchmark跑表。最新corpus近邻扫描显示CIS、DRInQ、social world models、goal-directed alternatives仍拥有相关层claim，定位只界定增量，不自动判死。

## 13. 把“什么时候停止脑补”拆成可检验对象

最新阅读把三件事明确分开：Degen/Tonhauser的世界先验与说者certainty；Koev对连续判断来源的理论替代（graded meaning或binary intent的不确定性）；Braun/Shetreet同话语真假交叉的literal/implicit commitment与trust。它们不能互换。E33的“probably meant Yes”仍是听者解释不确定性，不是说者表达“probably yes”。E38/E39原短numeric又受真实截断污染，E42全量有界校对已隔离，不围绕格式问题写paper。

[PNAS2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12718303/)的776人两样本研究已有语用多组件证据；机制名称是解释假说，相关不是神经机制因果。Hu2023来自同材料谱系，不是第二个独立natural substrate；少数相关checkpoint不能照搬human factor analysis。我们需要的是同材料的证据作用能否在分目标判断中保存，而非把所有任务压成latent criterion。

[BWIM2026](https://arxiv.org/abs/2603.19997v1)直接拥有partner-specific cancellation、confidence/action分离与澄清成本问题。最新public code与原confidence protocol有实现差异，E44已明确，E45先有界测试无歧义task floor，不以任务失败讲pragmatic ignorance。RAILS2025人类reference game更提示：literal speaker若随机选消息，收到一个消息仍可支持2/3目标posterior；literal speaker不等于literal listener，更不等于禁止推断。许可不是材料上的现成二值标签。

目前最值得弄清楚的未知是：**面对同一句话的不同证据，模型究竟在更新世界事实、说者意图、说者承诺还是听者行动；训练改变了哪个目标之间的联系？** E43只测retrospective attribution，不能推prospective action。强成功、有限入口、控制失败全部保留；暂未得到跨family/readout稳定领域结构。下一研究动作由这些边界决定，不把“任何跨层效应都是脑补”保成预设故事。


## 14. 深读怎样改变研究动作：不能只收集gap（2026-10-03）

这轮最有价值的是从parent解释链中得到约束，而非新增四个名词。几篇论文的idea来自已经有结果、但解释仍无法区分的压力：

| parent的演化动作 | 为什么不是再测一个分数 | 对我们的具体约束 |
|---|---|---|
| Mayn2025从listener自身reasoning到其对speaker reasoning能力的信念 | 简单control接近ceiling，但同一reference场景随partner变化；失败身份操纵也公开 | knowledge、speaker policy、listener解释分开；literal speaker仍可支持2/3目标后验，不能造unlicensed gold |
| Weak Evidence2022重新归因旧反效果 | 多个账户都解释反转，speaker expectation给出不同conditional prediction | 真实但弱证据能因被挑选而降低world belief；更深推断不等于更乐观或更负责 |
| NMI2026从能报confidence到confidence是否控制行为 | 先测信号，再让选项/阈值改变，并独立干预；不是confidence与accuracy另一张表 | pre/post decision读数分开，信号产生与action成本各需操纵；generic policy/sensitivity分离已有ownership |
| Confidence-Commitment2026重新解释同一个报告的意义 | 同trial分别预测正确性与后续commit/abstain，多读数/机制证据互相约束 | 残差关系仍需可识别性审计；E48禁止把noise改名policy就当机制 |
| Roleplay2026从成功说角色的话到是否深度内化 | 现在真假固定、时代endorsement改变，训练与预算控制；行为与probe联合 | 模型自己的事实表示、角色说法、归给他人的意图/社会责任是不同对象；generic knowing-versus-using不能claim |

**E45先给出的限制：** 五endpoint全未过无歧义build floor，64control正确仅5/19/21/29/8。Q3-14的64controls只有1格式invalid，但23其它错/11完整z反射错；不能拿confidence≈4的平均值推出partner推断缺陷。几何反射仅POST-HOC诊断，不新评分或能力修复。

**E41/E46给出的限制：** Q25-14 matched完整输入后，Hu不同现象与Impli初始/更新方向不同；Impli Base候选概率质量不足1%，只看归一化会制造解释。E46两端点完整数值各落在不同入口，Instr chat仍有基础理解/事实错，不能筛正确材料再称post-training改变推断结构。跨目标effect也在人类出现，不直接是hallucination。

**当前最值得继续弄清楚的未知（RECONSTRUCTED）：** 模型是否建立了能迁移到具体解释的speaker表达选择预测，还是不同交际问题只各自产生合理答案？这不是我们已发现的gap。E49用同24源场景，让speaker选择与listener解释相互约束，原control、身份、所有rotation都保留；先识别协议是否可用。照片/练习未迁移、speaker任务是派生，不能精确复现human identity effect，也不能将Bayes偏离自动叫内部机制错误。

**发展条件而非预设story：** 如果单个模型知道某项信息却没用，EPITOME已拥有；如果只是一种reference game的跨task不一致，尺度仍不足。值得升级的是选择过程的独立预测能跨自然材料约束推断方向/强度，并且训练改变其中可明确定位的一环。需要独立source、不同信息选择机制、成功理解与readout控制共同成立；未成立就保留成功/null并回到territory，不加限定保故事。

E48只是CPU parent账户校对：oracle真值代理完美时，阈值带噪估计的残差仍可对commit给出AUROC .833–.847，而对correctness≈.5。决策使用的估计噪声与同分布policy成分在这些观测下不可识别。它约束我们怎样解释数据，不贡献新的LLM能力结论，也不替代NMI独立steering证据。


2026-10-03 E49/E50完成：8640/6912原source读数完整，数值/source/token/EOS gates通过。E49无endpoint三身份全过无歧义控制；E50多数Qwen listener恢复，但speaker候选质量弱、身份effect随入口/terminal反转（Q3-8 bare full−.0180 vs content+.0048）。全部原item/missing bounds保留，不把generic role不一致或格式差叫新发现；C01/C02仍L0。当前未知需由独立自然source、成功理解与概率质量共同约束。E51跑前卡已写，核对dense OLMo2四stage和原IQAP/Circa输入；不追加E49/E50的局部prompt救分，资产预检尚在进行。


## 15. 一个有近邻但仍可探索的对象，需要哪些互相约束的预测

不能把“别人没用这个metric”当起点。当前证据更适合把交际链拆为：可见世界/知识→表达选择→收到的内容→意图解释→世界相信/社会责任/行动。RSA、Mayn、weak-evidence分别已拥有选择/解释的多个联系；EPITOME拥有knowledge-use分离；ICML/NMI confidence拥有自己答案的信号/检索/行动policy；普通链条本身不是novelty。

值得继续研究的不是链条图，而是**同一个模型对表达选择的独立预测，能否在新的真实语境中正确预测它应如何解释或撤回一个具体含义**。这给出三种可区分解释：选择预测错但条件使用一致；选择预测可用但解释未使用；两者都可用、只改变最终回答目标。当前E49/E50未同时满足读数控制，不能选择第二种讲Knowing vs Using。E51/E52先在两独立自然source确定较强训练谱系有哪些可用的条件行为，不生成二值许可标签，不用更大模型表本身当贡献。

EMNLP2024不同pragmatic-levels的结果提醒：lexicon未完全掌握时，最聪明listener仍受益于更明确speaker；learning时与eval时推断不能混。ICML2026cached-confidence正文与关键方法提醒：可解码、因果使用、最终verbalization分别需要证据，长prompt中冗余路由可让单一阻断无效。多手段应该排除不同解释，不是把同一个相关反复换图。

成熟增量的最低形态仍是领域特有的可迁移conditional prediction，能重解释已有训练/人类对齐结论；不是一个game、一个prompt的role gap，不是首次SDT/首次confidence。没有这一层证据时保留原数据、继续驻留，不缩小措辞硬保idea，也不以拥挤桌面关线。

E52的较强Q25仍不支持把post-training简单讲成更愿意推断：方向判断改善、definite解释phrase下降、human分布Brier变差并存，而原candidate mass/无QA lexical prior不可忽略。不是漂亮的“accuracy↑校准↓”finding，因为这些比较未隔离读数/规范。E53再把format compliance与semantic task floor拆开：无损表示恢复大量raw的可读性，语义/位置错误仍存在。两者约束怎样解释测量，不把instrument repair作为novel scientific object。weak-evidence原shared.js的J0/S1/J1/J2与原replication说明已进一步阅读，完整likelihood包括重复stick instances，正式benchmark需固定sampling、threshold与norm，不把表面“literal”当negative gold。

## 16. 从论文发展自己的问题：先找被混合的解释，不能只换设定

ACL2026 production-choice正文与附录A–D补读完成，原仓库公开访问404，不能称代码驻留或复现。它从“surprisal是成本”发展到“相对哪一套备选，才是哪一方的成本”；Weak Evidence从“弱证据反转”发展到“期待怎样的选择过程，才应该反转”；Mayn从“听者推理水平”发展到“他认为partner会怎样说”。共同动作是让已有解释产生不同的条件预测，而不是在同一平均效应旁补一个metric。

对我们的约束有三层：**语言上可预测**不自动等于**当前目标下可替代**，后者也不自动等于**当前说话者知道并能选择**。观察到对另一表达的高likelihood，只有在这些条件和具体候选意义明确后，才成为“没说它”的交际证据。Production-choice的history增加让goal-matching比例从4.7%升到15.2%，是parent的证据，不是我们的finding；它提示不能用context-free词频或开放续接概率替代goal-conditioned选择机制。

当前需要检验的对象因而仍是选择过程预测与具体解释之间的条件联系。为使一个实验有信息量，需要先写清：若只是词汇prior，哪些同goal/不同goal条件会同向；若使用了speaker选择证据，哪些候选命题应改变、哪些不应改变；若只改变回答规范，独立意图读数和事实/责任读数应怎样分离。不是现在宣称三种机制已被识别。E49/E50原控制未共同成功，E52受candidate质量/顺序限制，不能从这些数据选一条漂亮解释。E51仍是较强同谱系自然parent边界，后续的新实验必须先取得符合上述识别条件的原材料与norm，不能靠后标标签制造答案。


## 主问题不缩小：从“多少推断”到“凭什么推断”

研究对象仍是现实理解中合理的补全边界。信号受损可让修复更合理，speaker知识受限可削弱某个备选未被选中的证据，meaning prior改变“世界可能如此”的程度；这三者即使同样降低确定性，也不要求推断同向改变。值得知道的是训练有没有保留这些来源特有的条件关系，或只学到了通用补全/回答规范。若模型成功，也要检验这种结构能否预测新的表达与情景，不只找失败。

Gibson与Chen的研究动作是联合预测→exposure干预→混杂复核；EMNLP2025资源模型补充候选可达性与有限搜索的账户；Cai已发现原生LLM的人类式修复形状。我们可发展的实质问题是让这些解释对同一模型提出不同、可跨自然材料验证的预测，再问已有post-training“能力进步”如何重新归因。概念拼接、首次使用noise词汇、一个新metric都不是所求增量。近邻有答案的一部分，能给对照；不能以此把题缩成一个模型的一种句式。

当前I01只是SEED，未指定结果方向。E55全12800通过技术gate，但语义控制未共同成功、部分完整候选mass极低；不是paper claim。E56在原source固定320critical，发现release18改动与正文30不符，E57正在测公开版本的条件响应。它是驻留探针，不能靠该四类材料写领域结论；下一步优先独立knowledge/prior来源及合格数据构造，跨来源effect不直接相减。

数据载体规范见[DATA_PROTOCOL](../DATA_PROTOCOL.md)：自然性/控制性/人类norm分开，独立scene数量而非模型重复数决定证据宽度。可以构造或改造数据，但每项改动需标出改变的前提；无可靠许可gold时只报告响应，不造FPR。


E51收齐后的对象澄清：方向分数与人类四类分布可以分离，但这不能自动归因为speaker certainty丢失。IQAP definitely/probably判断的是听者如何解释B意图；自然语言输出的hedging又可以表达模型自己的不确定。EMNLP2024[Uncertainty in Words](../../../library/themes/pragmatic-inference/uncertainty-words-2024.md)已经拥有intrinsic一致性与语言decisiveness的faithfulness对象。我们的有意义未知仍是不同交际证据如何分别约束具体含义、合理修复与停止推断，而不是再做generic confidence-expression mismatch。数据字段要明确uncertainty referent与event-role/world-entailment；E58逐条候选解释与原标签的分歧先做源语义审计，不自动视作发现或改gold。


## E59/E60修正：先让条件关系可被识别
IQAP同source SFT→DPO四类分布距离跨三措辞都变差，copy映射成功、原W0复算零差，削弱单一词组解释；但无对话prior同步移动，不识别内在语用能力。措辞稳健只是排除一个账户，不能自动写成偏好训练损害calibration的paper。继续独立材料而不再添加alias。

ELM2025改变的是“表达形式索引人格”的前提：语境与实际知识信息约束表达选择理由，再约束人物印象。原模型研究用理论prompt改变trait评估，但这与模型是否响应实际证据不同。原human第二实验knowledge→trait变化较弱，lack-knowledge少了而speaker/hearer便利都增加；这提供多个可区分预测，不能把一条理论链预先当机制。

当前更有信息量的未知是：模型在同对话上对动机的归因，是否与其人物评价有一致的来源条件作用，而训练如何改变这两个环节？E61是原norm下的小型驻留，不证明joint belief、causal mediation或实际hidden motives。若只剩不同任务分数、不稳读数或六scene局部效应，就回到证据归因主问题；若稳定则跨信息量/relevance素材验证，不缩成这六个例子。

## 规模与训练差异什么时候有科学价值

用户提出的警惕成立于一种情况：所谓语用异常只是基础任务不可读、答案接口不适配或总体能力地板，随更强模型消失且没有可迁移条件结构。E61目前motive候选支持不稳，就不能把它与trait的分化讲成能力分离。但“随规模/训练变化”本身不是低价值证据；若同一模型对已读懂的证据，在不同推断目标上有可预测的作用，且竞争训练账户/跨现象迁移能被区分，这种依赖可以成为对象。匹配stage仍共变数据/算法/budget，不能单因果归DPO。

[Bayesian Teaching](../../../library/themes/pragmatic-inference/bayesian-teaching-2026.md)给出具体研究动作：先比较跨轮更新而非总分，改变监督teacher而非只换模型，加入随机错误/prior控制，再用信息量干预与跨自然域迁移检验。真实人群中原模型首轮准确很高，仍不代表适应；反过来human choice不完全服从自报偏好，规范正确不等于行为对齐。这和我们的答案prior/人类分布问题相关，但不能借此宣布已经识别了内部Bayes或criterion。

需要保持三个宽方向：具体含义推断的证据更新；表达选择引起的动机/社会评价；互动中的选择与信息利用。它们分别有parent，不是三个新workbench，也不是要全部再堆benchmark。选下一实验看哪个账户能被排除。E63用原知识理由条件约束第二方向；若可靠条件结构没有出现，就记录成功或未识别，不将题缩成某个prompt漏洞。

新数据定位也需谨慎：[W&C-Sent](../../../library/themes/pragmatic-inference/wc-sent-2026.md)是作者怎样描述目标人物，E61/E63是听者怎样从说者的交际选择评价说者；共同使用warmth/competence不使两种gold可互换。社会归因应用工作提供自然语料视野，但generated goal不是事实verifier。这些是数据选取约束，尚非贡献。


## 用户原对象纠偏（2026-10-03）
完整重读786行原提示词后的判断：主要执行漂移，初始方案的数据许可/SDT识别前提尚未兑现，不是原territory已被否定。之前“从多少推断到凭什么推断”等拓展只能为原推断边界提供竞争解释；社会评价反向没有licensed/unlicensed具体含义，不足替代主对象。之前建议撤SDT叙事过早：我们没有有效双侧测量，不能声称criterion解释已失败；仍只作为候选，不预押结果。

主测量应固定目标表达、候选含义和强度，在自然语境支持／不支持条件下看响应如何改变。现成数据不能满足时应有针对性构造与norm核查，而非继续堆邻接benchmark。解释广度来自比较账户，不来自不断更换dependent variable。当前0成熟贡献不构成territory失败证据；真正止损要以有效测量后的科学产出与数据可行性为依据。详细对照见logs/review-2026-10-03.md。
