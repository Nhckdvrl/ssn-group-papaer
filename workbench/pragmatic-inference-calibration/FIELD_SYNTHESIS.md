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

论文阅读覆盖见[题材库](../../library/themes/pragmatic-inference/README.md)，实验状态与数字见[工作台](README.md)。下载PDF不算全文阅读，正文/关键附录/代码各自注明。

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

E28/E31/E32补齐8B/14B及原alternative expectedness；E33真实IQAP human分布和E34原Circa同question自然回答完成。IQAP方向随强端点改善，Circa有条件解释也相当成功，这削弱“模型普遍不会调整强度”的大故事。负强度读数可以被选项顺序彻底改写；E36平衡的单句强度要求和E37原Flan native对照显示，强侧改善常伴弱侧恶化。因此局部prompt修补分支已经达到有界控制终点，不再给它加限定把instrument artifact保成paper。

我们现在还不知道的是：**在字面证据相同而交际上可用于推断的证据不同的自然情境，强模型会不会做对相应的推断变化？** 目前Circa同问题换回答同时换semantic content/难度；IQAP是人群graded判断，不能直接因果解释speaker certainty。需要真实上下文、原人类norm和候选意义固定的材料，先检查信息是否真的可识别，再决定实验。NAACL2022 SwDA-IA的真实对话/上下文效应、NAACL2025 projection/RSA的belief attribution是新驻留入口，阅读与源码检查进行中；不立即再下载20个benchmark跑表。最新corpus近邻扫描显示CIS、DRInQ、social world models、goal-directed alternatives仍拥有相关层claim，定位只界定增量，不自动判死。
