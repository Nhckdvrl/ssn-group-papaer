# D5定位：Pragmatic Inference Calibration

更新2026-10-03；当前无科学finding。来源：本地65,716篇语料nearest查询（2026-10-02）+ primary ACL/arXiv检索、PDF与公开代码。搜索未命中不证明不存在。

| 近邻 | 已拥有的claim / 证据 | 本轮资产核对 | 我们尚待测的增量与风险 |
|---|---|---|---|
| [Hu2023](https://aclanthology.org/2023.acl-long.230/) | 细粒度human/model错误结构、语境消融 | 169原项、五option order、104 no-story；Flan1,365选择完全匹配；374人、169项的原选项编码零错误 | 普通错误分类/human对齐已拥有；no-story不能充当unlicensed。风险高 |
| [Hu & Levy2023](https://aclanthology.org/2023.emnlp-main.306/) | direct probability与metalinguistic判断不同 | 本地MCQ letter/text仍是metalinguistic，不能冒称direct knowledge | 提示恢复/答案绑定不是新能力结论。风险高 |
| [Multi2024](https://aclanthology.org/2024.genbench-1.7/) | multilingual maxims+literal evaluation | 1,200单元；maxim240与literal60分开；原14B四语言×3seed完成，德语maxims比paper高9.16pp，解码细节未公开充分；无逐选项inference类别 | literal/pragmatic两侧不是我们的首创；需candidate-level许可与难度匹配，错误不自动FPR |
| [Wu2024](https://aclanthology.org/2024.emnlp-main.1258/) | free-form评测、PO与SFT差异 | LLM judge排序/长度等混杂；SFT不全优于base | 不能claim首次free-form或post-training；API-heavy protocol不作主仪器 |
| [Wavelength2025](https://aclanthology.org/2025.emnlp-main.1008/) | 强模型均值接近人、distribution更尖，listener/speaker | 100clues、50concept pairs、4,000human responses；FP32/关闭thinking修正后逐项概率 | human distribution与mean/width不一致已拥有；不是二值warrant benchmark。风险高 |
| [ALTPRAG2026](https://aclanthology.org/2026.eacl-long.9/) | 22模型Base/SFT/DPO、alternatives recovery改善 | code003a11d：main_base默认URIAL examples；shell/instruct有其他prompt；release原表1298行，而论文过滤650/swap1300，需要确认canonical版本 | 不能claim首次stage tracing。当前不能将其与PaCE平均差直接归同一latent criterion |
| [PaCE2026](https://aclanthology.org/2026.findings-acl.959/) | context flip、over-inference、strict prompt reversal、RLHF解释 | synthetic逻辑blocking；正文/表数不一；人类literal项获额外严格指令（Appendix F），默认model指令不匹配；没有可核对clean stage SHA | suppression与prompt reversal已拥有；matched warrant/readout/stage的重新归因才可能有增量。风险很高 |
| [DRInQ2026](https://aclanthology.org/2026.acl-long.1597/) | controlled context、licensed vs overly strong/malintent解释 | repo96a5ea：公开231行/148不同surface questions，不是论文400hard/819validated；首项author intended D但human consensus B | context licensing已拥有。自然human分歧资产值得驻留；不是自动精确撞车或kill，先核对版本 |
| [CIS2026](https://aclanthology.org/2026.acl-long.577/) | scalar inference graded表示、global vs graded steering | repob153760：后处理embedding加vector、cosine偏好；grade直接设alpha，未干预forward生成 | global tendency vs graded structure已有ownership；behavioral warrant/criterion与embedding几何不同，区别本身还不是贡献 |
| [SDT2026](https://arxiv.org/abs/2603.14893) | sensitivity/bias、instruction tuning偏移、temperature非纯criterion | 全文15页已读；confidence/type-2与forced choice的读数不同；30.1%漏匹配与fluency/分箱混杂 | SDT移用/泛SFT bias不是novelty。必须改变语用已有科学归因，不能换metric重报大模型好 |
| [PragReST2026](https://arxiv.org/abs/2606.18624) | counterfactual自生成+SFT/GRPO提升，含unsupported inference错误分析 | 正文/关键A/B/D附录已读；小human judge校准100项，precision0.780；error tag blind human核对；未跑原代码 | 不能claim首次counterfactual改善或首次标overextension。joint under/over boundary仍需同规范的证据 |

用户指定ALTPRAG/PaCE引用优先于默认venue限制；投递仍只ACL/EMNLP/NAACL主会。

## Ownership boundary

我们现在只登记territory：在同一沟通规范与明确候选含义下，辨别语境支持和推断倾向是否分离、这种分离是否改变现有训练阶段结论。没有发现、没有“首次SDT”、没有新loss/架构，也没有承诺criterion解释必须成立。

“是否存在任何言外之意”过于宽泛，日常literal陈述也能附带社交含义。下一版测量对象需明确候选命题q、语境C和交际问题；许可是q在C中获支持，而非全局是否nonliteral。human分布可表示歧义；未经human/parent验证的agent草案不当gold。matched context与选项保持不变的重要性是可识别性，而非为了切窄novelty。

## 最近扫描与compression risk

- corpus query：`pragmatic inference calibration context licensed overinterpretation sensitivity criterion post-training`，返回CIS、DRInQ、Wu、Wavelength、non-verbal及ICML2026 Criterion-Conditional ICL（VLM背景，未全文核对）。语料相似分与接受率都不是科学判决。
- primary检索：`pragmatic signal detection language models 2026` / `pragmatic over-inference 2026` / `pragmatic criterion LLM 2026`；未确认直接把licensed/unlicensed跨现象、clean stages同设定拆解的论文，不作为不存在证明。
- 最新发现[PragAlign](https://arxiv.org/abs/2609.02480)：生成服务dialogue的constraint反馈与human质量，摘要层；不是本轮主张的直接证据，不自动扩大baseline。
- 最大compression risk：复述PaCE“会脑补”、复述SDT“instruction改变bias”、复述Wavelength“均值好但distribution窄”、复述Hu/Levy“prompt影响测量”。当前技术校对全归D1/D2；只有新的稳定领域结构或对parent结论重新归因后再讨论paper形态。

## 扩展定位（2026-10-03）

| 近邻 | 已拥有 / 本轮资产 | 距离与compression risk |
|---|---|---|
| [Hu et al. TACL2023](https://aclanthology.org/2023.tacl-1.50/) | 自然within/cross-scale graded SI、string+concept两阶段alternative expectation；原BERT/GPT2 string已复现 | 不可claim首次备选预期解释/跨scale。未复现concept主回归；需要许可证据如何被使用的条件结构 |
| [EPITOME TACL2024](https://aclanthology.org/2024.tacl-1.45/) | mental-state识别vs语用使用、人类knowledge residual；SI与IR来源已核对 | generic知道不用已拥有；partial access也可排除特定q，不能强造二值negative。stage条件结构若改变已有归因才有信息 |
| [eliciture SCiL2025](https://aclanthology.org/2025.scil-1.39/) | 因果推断detect vs use、base/instruct比较 | 不可把knowledge–elicitation separation换名字；原资产未取得 |
| [SALT35 conditional alternatives](https://journals.linguisticsociety.org/proceedings/index.php/SALT/article/view/35.004) | QUD与epistemic access制约conditional perfection | 自然许可理论已拥有。原OSF401，不能冒称材料复现或全局无知识不推断 |
| [PROBCOPA TACL2026](https://aclanthology.org/2026.tacl-1.93/) | 人类graded判断与模型分布偏差 | 人群异质性不是模型解码方差；只报distribution sharpness风险高 |
| [Graded Expectations SCiL2026](https://aclanthology.org/2026.scil-main.46/) | base/instruct人类continuation预测，speaker策略 | 原Eq4频数加权需count-only null，未取code/data，不宣称结论错误；human预测≠normative助手本身已是邻域 |
| [Goal/value trade-offs ICLR2026](https://proceedings.iclr.cc/paper_files/paper/2026/hash/dc74a7c09fcf71705f433b52067edc05-Abstract-Conference.html) | prompt/reasoning/post-training改沟通目标权重，DPO/PPO真实训练 | genericalignment移动目标/criterion已拥有；认知模型拟合不是完全机制识别 |
| [Goal-directed alternatives ACL2026](https://aclanthology.org/2026.acl-long.1814/) | production choice的goal-conditioned备选集合与surprisal | “不是所有可说的都是合适备选”已有claim；新动作须用自然边界改变理解而非重拟合参数 |
| [Common ground survey2025](https://aclanthology.org/2025.luhme-1.2/)、[referential grounding ACL2026](https://aclanthology.org/2026.acl-long.410/) | 互动grounding/repair与human-modelpacts分离 | 语用证据来源的独特条件效应才可能超越长history/视觉/顺序混杂 |
| [ImplicatureX arXiv2026](https://arxiv.org/abs/2607.25094v2) | recognition/cancellation/joint、prior/negation/strengthening/irrelevant/length；canonical271与完整原prompt已核对 | S2已有直接近邻，ownership改写不kill。E21只作驻留；不能claim首次测撤回或首次更新false alarms。原Approx无human norm，不可自动作goldnegative |

最近新增corpus nearest“Communicative belief update implicature cancellation versus irrelevant followup calibrated context sensitive inference”返回DRInQ/CIS与DEL-ToM等（EMNLP2025推理扩展尚未全文读）；latest arXiv直接命中ImplicatureX。邻域已很拥挤，新颖性未成立。重点问条件证据是否改变post-training归因；若只剩一个prompt的归一化/格式偏差，留作仪器并回territory。

## 补充collision audit：2026-10-03

本地corpus nearest重新检索“speaker knowledge / conditional evidence use / post-training”；CIS/Wavelength/Wu2024仍直接邻近。额外定位如下；未输出自动判决。

| 近邻 | 已拥有的层级 | 我们不能声称 | 可能增量/待证据 | compression risk |
|---|---|---|---|---|
| Goodman/Stuhlmüller2013 | knowledge-dependent complete/partial cancellation，RSA+两human实验 | 首次发现知识门控、首次RSA | 同谱系如何改变candidate-specific evidence use；未成立 | 高 |
| CoNLL2021 connective tests | default倾向vs同题两侧辨别、implicit/explicit撤回 | 用pair/SDT拆倾向就新 | 现代自然跨现象结构与已有训练结论归因 | 高 |
| Accommodation ACL2026 main | at-issue/encoding/reliability，hit/FA、prompt与多轮pressure | 第一次false alarm/纠错边界，第一次QUD | 解读candidate posterior与行为规范的同材料分离；未成立 | 高 |
| Social Meaning arXiv2604.02512v2 | structure/magnitude separation、alternatives/motives prompts | 首次pragmatic calibration或epistemic prompt | 固定真实training lineage的条件证据结构；不是只换open model | 高 |
| ImplicatureX v2 | recognize/cancel/prior/irrelevant/strengthen/type/form | 首次撤回/取消、用连续差当新metric | matched stage与证据许可改变哪一环；Approx norm和readout gate先过 | 很高 |

E24源算术/顺序问题只修复仪器，不作为规避ownership的paper主题。强现代8B/14B端点与真实DPO结果尚未完成前，不声称领域特有稳定现象。

| 近邻 | 已拥有 | 距离 | compression risk |
|---|---|---|---|
| INLI / ACL2025 main | implicit/explicit entailment分类、human subset验证、跨domain训练保持 | 不同证据来源需要区别已拥有；4类不是逻辑唯一norm，hypothesis-only .595不等于artifact已排除 | 尚未识别同自然材料source/strength交互stage归因，不做40k新榜单 | 高：把criterion改名implicit-vs-explicit不是增量 |
| Sense and Sensitivity / CoNLL2026 | 真实reasoning提高prompt鲁棒却不成为human代理 | “更稳≠更human”、frame/polarity/order已拥有 | 知识问句E29只是control；要条件证据结构改变已有解释 | 高：generic elicitation story不够 |


## 自然解释强度与互动边界扫描

| 近邻 | 已拥有 | 当前距离/风险 |
|---|---|---|
| IQAP ACL2010 / 作者2011更新 | 自然scalar方向/强度、人类分布、语义关系与局部语用 | E33不claim首个人类分布校准；新阶段条件结构待证据 |
| CIRCA EMNLP2020 main | 多类间接回答、跨情景、PN误压No、问答only controls | E34初始配对只是probe；只换新model不能成为overcommitment paper |
| Scalar Calibration TACL2024 | 已直接Circa人类scalar/model calibration、ECE排序问题 | calibration+larger-model表已拥有，需改变具体科学解释 |
| Social world models ACL2026 main | 多family ToM–prag功能整合、localizer/消融/通用能力controls | 不能把观察提前机制化，更不能claim第一次共享mental-state网络 |
| Reference clarification arXiv2601.07820v2 | 不确定→澄清与实际信息使用脱节 | 互动停止/修复方向不是空白；当前静态实验不支持interaction claim |

Raffel作者blog[When will models be good enough](https://huggingface.co/blog/craffel/when-will-language-models-be-good-enough)全文已读（观点性文章，不作实验事实）：科学问题应与具体使用目标/成本联系，不把8卡占用或更大model排名当价值判断。Potts教学页语义关系分析明确指出same-direction答案可经后承也可经cooperative/expert上界补全，未来对象需区分两条证据链。


## 原真实语境与belief attribution近邻（2026-10-03）

| Parent | 已拥有claim | 当前允许的research action | compression risk |
|---|---|---|---|
| SwDA-IA / NAACL2022main | 真实问答需前后context、human gold会变化、Circa迁移有限 | 取original两批norm/证据turns后区分信息缺失与利用；官方repo仅README当前不可跑 | 很高：只重新说更多context有益不够 |
| Pan&Bergen / NAACL2025main | prior/predicate作用、人类projection graded、mixRSA比三API预测更好 | E38先源/human核对、frozen原numeric任务新stage端点，明确预测优劣不证表示必要性 | 很高：generic知道不用/graded prior与anotherRSA均已有 |
| LLM Beliefs Are in Their Heads / ACL2026main | truth Accuracy/Use/Coherence/Uniformity的residual/head probes与steering | 正文阅读进行中；model自身belief-like truth representation ≠ 归给speaker的belief | 高：不能claim第一次belief方向/steerability；当前无机制主张 |

最新corpus近邻检索仍出现CIS/DRInQ/nonverbal/social-world-models/goal-directed alternatives。只定位、不自动判死。39卡阅读范围逐卡标；最新human implicit-commitment论文正在取得正文，未读不计全文。

## 真假、承诺与partner适应的最新ownership（2026-10-03）

| 近邻 | 已拥有 | 允许的增量 / compression risk |
|---|---|---|
| Implicit dominance / Language and Cognition2026 | 同utterance真假交叉、implicit影响两层commitment、总体trust；三human实验 | E43迁移只是baseline；不能首次发现跨层影响，且原human也非两层独立。训练怎样改变目标间证据作用仍待跨素材/入口证据 |
| Human components / PNAS2025 | 人类三组语用组件，两大样本复现 | generic“pragmatics不是一个数”已拥有；Hu材料同来源，模型样本量不足factor机制解释 |
| BWIM / arXiv2603.19997 | partner特异cancel、confidence/action gap、澄清过多/过少 | 不能首次动态停止推断/首次询问；E45是task-floor基线，后续须新领域条件结构而非换local model |
| Listener adaptation / RAILS2025 | 经验驱动partner信心改变、选目标仍偏好 | literal S0仍可产生2/3 posterior，不把literal partner全标negative；两页摘要不是完整期刊证据 |
| Strategic Dialogue Assessment / D&D2026 | 非合作courtroom、commitment/credibility/goal收益、原court对话评估 | 摘要/引言已读，53页未全文；不能claim首次将战略欺骗/社会trust接入语用。正式数值与原labels未核对 |

corpus nearest “LLM pragmatic speaker commitment literal truth implicit meaning trust belief attribution”返回NAACL2025belief、ACL2025(RSA)²/INLI、EMNLP2024different pragmatic levels与Wave；最新primary搜索直接命中BWIM与2026implicit dominance，均纳入边界，不自动kill。另命中conditionals arXiv2605.21299（仅摘要）与LREC2026Emergence（仅摘要）：不算全文，不把已有alignment→intent representation说成我们的novelty。


## 选择机制、元认知与角色的ownership（2026-10-03，分阅读范围）

corpus nearest “language models speaker selection mechanism pragmatic inference world belief speaker intent commitment selective evidence”＋最新primary arXiv检索。词面commitment命中不等于相同scientific object，不输出kill。

| 近邻 | 改变的前提/已拥有 | 当前边界与如何发展 |
|---|---|---|
| [Mayn2025](../../library/themes/pragmatic-inference/speaker-reasoning-2025.md) | 关于partner reasoning的信念影响解释、人类异质性；正文/附录A–E全文、E47描述norm复现 | E49只是文本迁移；缺photo/history不称human effect精确复现，literal-S0 posterior非L0 |
| [Weak Evidence2022](../../library/themes/pragmatic-inference/weak-evidence-2022.md) | rhetorical selection解释已知反转并给speaker expectation条件预测；正文全文、SI未取得 | LLM weak-evidence已有2025大学slides直接展示，不首次发现；final filter727vs723未核对，不开无norm GPU |
| [NMI2026](../../library/themes/pragmatic-inference/confidence-behavior-2026.md) | confidence形成/行为阈值、两类独立预测与steering；公开v3正文主线/Methods读 | generic sensitivity/criterion、可干预confidence均已有；社会speaker attribution不同，但差异不足自动novelty |
| [Confidence-Commitment2026](../../library/themes/pragmatic-inference/confidence-commitment-2026.md) | verbal confidence更预测提交而非正确，probe/steering；核心论证与Methods深读，补充未全读 | 自己提交答案≠他人social责任。E48显示特定残差识别需要因果假设，不推翻实证或借bug转新领域 |
| [Roleplay2026](../../library/themes/pragmatic-inference/roleplay-belief-2026.md) | 行为/内部truth representation分离、干预深度；正文主线、附录/代码未核对 | 不能generic表达≠内部相信/knowledge≠use；主要机制不直接从自报告推断 |
| [SDA2026](../../library/themes/pragmatic-inference/strategic-dialogue-2026.md) | 目标相关承诺/credibility、非合作courtroom；§4/8–10已深入补读，非53页全文 | BEN/DET≠world truth；累积策略≠long-horizon planning；真实court data/labels未核对 |

额外词面近邻[When Does a Language Model Commit?](https://arxiv.org/abs/2605.06723)只读检索摘要，研究有限答案偏好稳定时点，非社会commitment；不计全文或宣布无碰撞。EMNLP2024 Belief Revision由corpus命中，尚未深读。2025弱证据LLM primary slides只读相关excerpt，不能反向证明我们的联合选择机制对象无人做过。

**compression risk仍高：** 单一reference游戏中的speaker/listener不一致、换现代checkpoint、一个新metric都不够。增量须能改变关于交际证据如何进入解释的已有结论，并跨独立材料保留；当前0成熟贡献。


最新nearest重新检索speaker intent/world truth/selective disclosure，返回EMNLP2024不同pragmatic levels、ACL2026goal-directed alternatives/social world models、Wavelength与Wu等。前者正文已补读：拥有training-vs-eval reasoning、partner depth/lexicon/data information的区别，非LLM自然数据。ICML2026cached-confidence正文/关键方法已深读：拥有自己答案信号的缓存、检索、多干预，未拥有别人表达选择对自然意图/world belief的联合条件预测。以上只是ownership定位；compression risk仍高，E49/E50暂无共同可用的role测量，不以近邻存在关线。
