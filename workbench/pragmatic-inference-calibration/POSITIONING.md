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
