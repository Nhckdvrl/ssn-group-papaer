# 暂停时的完整研究总结（2026-10-06）

> 历史记录。2026-10-08后的完整方向/结果见[探索记录](EXPLORATION_RECORD.md)，整体判断见[探索总结](EXPLORATION_SUMMARY.md)；本页“下一步/在途/当前”描述当时状态，不是自动执行队列。

**结论：尚未找到已经充分验证、可以确认新颖性和论文价值的好 idea。** 有可复现的局部行为结构，也积累了重要反证；不能把它们升级为“成功修订后仍保留错误解释”或“一般角色绑定缺陷”。用户明确要求暂停：研究目标已暂停，无新推断、训练、数据构造或 API 请求；此轮仅整理已有工作、失败与文件并上传 main。Workbench 注册仍为 PROPOSED，不自行修改其他 ACTIVE 线。

## 1. 到底完成了什么

- 原定三个上游已下载、固定 revision/license/hash、统计规模；统一 loader/schema 已建立，原始数据留本地 cache。
- E00 完整执行 Qwen3-8B frozen inference、paired bootstrap、simple/GP question 与 GP/nonGP 分项、完整 prompt suite。**没有稳定复现 pooled GP-specific deficit**，不选一个获胜 prompt 宣布通过。用户后来取消停步 gate，因此推进 E01；这不等于追认 E00 成功。
- 共 **51 张实验卡：E00、E01、E03–E51**。E02 没有执行卡/运行，不能补造。实验卡保留事前问题、解释预测、配置、全部结果及勘误。
- E01 原始设计 90 lexical sets、626句变体、2672候选QA；已测最大的历史 snapshot 是279变体/1189QA，其中1158 eligible、4632任务。随后完整 Step Plan 输入审计结束于 **565/626变体、2405/2672 QA**，61变体未完成；**未运行新全量E01**，不能将历史snapshot说成完整系统测量。
- 后续围绕同一领域的角色证据、事件范围、谓词/指称形式、真实后续使用追原因；未做 SAE、probe、训练。主模型固定 Qwen3-8B，1.7B只用于E04/E05已知对照，不是多模型扩张。
- E51 六个独立H20 shard已完成 **4608回答**，.31912GPU·h；完整答案 Step Plan 审计失败较多，仅936回答完成，最终语义结论尚缺。
- 已有58份领域阅读/资产卡；新近读取的QA presupposition与multi-answer近邻补记到知识库，标明实际读取范围。没有据空检索或“更多模型”认证novelty。

## 2. 现在能说的事实，与不能说的解释

| 证据 | 可以说 | 不能说 |
|---|---|---|
| E03/E07：固定协议的顺序交互大、跨raw/native保留 | 同一问句的GP/nonGP差随query顺序反向；是稳定的任务条件测量事实C03 | 早提问必然改变内部parse；E08/E10并未支持简单独特GP阅读目标叙事 |
| E22/E24：history×具名/泛指表述的关系减中性读数有交互 | 存在局部、跨来源的条件概率结构C04 | 已成功修订、旧错误belief保留、或实际功能错误普遍发生 |
| E29–42：部分人工frame中旧角色证据反向影响新同类动作患者预测 | C05在已测表达/语境下有条件性预测结构 | GP是必要因素；不同事件的事实被普遍错绑定；logprob等于world belief |
| E43/E44：普通名字场景没有稳定绝对反向 | 原来较宽的一般角色反转解释受到明确反证，必须收窄 | 用负的neutral subtraction挽救普遍反转；只挑order/subset继续宣称稳健 |
| E46–48：inventory、event表达、词汇匹配明显调节 | 指称形式/额外提及/语篇结构是核心竞争因素 | 身份断言含义是唯一原因，或已发现新的内部binding机制 |
| E49/E50：单问/普通复述高分，formal复述/联合名字差 | 用途、格式与检索cue对回答有巨大影响 | 一个generic“知道但不会用”gap就是novelty；E49错误与C05预测偏移是同一机制 |
| E51：无two-names措辞后的literal-schema joint约82%，repeat指令约91% | 保守格式解析下仍有同patient劣势，是待审的线索 | 完整语义审计已通过；count题已证明角色数被当成实体数；已经找到好idea |

当前等级：C00–C02 L0，C03–C05 L1；I01 PILOT。没有L2/L3科学主旨，没有候选论文、没有稿件。人的科学品味决定未被agent替代。

## 3. 全部尝试：问题 → 实际结果 → 失败或边界

以下每行链接原实验卡；不以新总结覆盖旧结果。百分数差为pp；概率读数为bits；方括号为原paired 95%CI。不同定义的D/J/K不跨实验直接合并。

| 实验 | 做了什么、主要数字 | 保留下来的失败/解释边界 |
|---|---|---|
| [E00](experiments/E00-baseline-reproduction.md) | 原Amouyal16-prefix复现；pooled nonGP−GP lingering −2.81 [−11.50,5.89]pp，simple +10.69；句先+28.99、题先−24.64 | 不支持稳定pooled已知方向；完整prompt波动保留；极性混杂不能单独叫GP能力差 |
| [E01](experiments/E01-component-revision-map.md) | NP/Z、NP/S、MV/RR的cue/blocker/extension和final/initial双读数；多snapshot推进至279变体、4632任务 | 全量measurement未完成；NP引用、未assert≠false、prompt/mapping、词汇替换语义仍影响读数；最新完整审计565/626，不追认漏项 |
| [E03](experiments/E03-e00-order-and-assertion-audit.md) | 正交拆order/demo/interface/precision；FP32 order交互+66.67 [49.28,84.06]pp，所有8cell同方向 | BF16只造成0.61% accuracy flips，解释不了大反转；assertion也没解决；不是新revision机制 |
| [E04](experiments/E04-known-positive-control.md) | Qwen3-1.7B已知对照；pooled +19.84 [14.04,25.82]pp | nonGP lingering仅30.71%，specificity CI跨0；仅方向复现，未解决instrument问题 |
| [E05](experiments/E05-response-meaning-calibration.md) | standard/letter/asserted与两模型；8B asserted句先+30.43、题先−23.91pp | 换label与一句语义说明未解除顺序/floor；1.7B部分更差；所有mapping报告 |
| [E06](experiments/E06-attachment-versus-event.md) | 区分主句subject、direct-object、initial event；GP subject控制0–5.80%，nonGP joint约32–48% | object-No高分不是恢复；67-source clean敏感性没有解除异常 |
| [E07](experiments/E07-native-readout-transfer.md) | 移除prefill/fewshot并换native；order交互+60.87 [44.93,76.81]pp | 不依赖raw边界，但仍不能归因内部parse；C03只保留协议事实 |
| [E08](experiments/E08-reading-focus-versus-final-query.md) | 固定最终query在末尾，前/后相关及无关focus；before交互+1.45、after−7.25pp，均CI跨0 | 后置final focus对GP/nonGP都提升约22–23pp；不支持简单GP-specific早期阅读目标解释 |
| [E09](experiments/E09-published-comprehension-transfer.md) | 原SAP自然comprehension题1152任务；句先cue−GP +33.33/+19.44pp | 已知cue有效但选项mapping/顺序仍强；不能包装更多GP结构为贡献 |
| [E10](experiments/E10-question-versus-option-access.md) | 分离question/option位置；2304分析行；一个mapping交互+19.44，另一个+2.78 CI跨0 | 大差可由cue答案下降引起；不继续找最佳布局 |
| [E11](experiments/E11-extension-role-reference-audit.md) | 完整NP/head/原短NP和isolated主句；500分析行；comma extended fullNP−原role +31.49 [7.81,56.20]pp n3 | 无歧义extension下降部分是引用/constituent测量伪影；不能叫digging-in |
| [E12](experiments/E12-input-probability-versus-answer-access.md) | 输入disambiguator surprisal与最终QA分开；早Q交互+1.47 [.47,2.52]bits | cue facilitation主导且cue答案可下降；prediction/QA gap已有owner；不是统一能力下降 |
| [E13](experiments/E13-natural-followup-without-diagnostic-question.md) | Slattery原自然后文，无diagnostic Q；whole-S2 GP−comma约−.031/−.003bits，CI跨0 | 没有普遍后文代价；局部reference与邻词方向不同，不能只选窗口 |
| [E14](experiments/E14-event-identity-versus-extra-event.md) | same/separate activity桥；7明确episode交互−2.608 [−3.779,−1.090]bits | aspect/事件预设/长短NP竞争；后文并非全episode，不能把全部自然句强算同事件 |
| [E15](experiments/E15-fixed-aspect-event-reference.md) | 固定continued分解；事件指向−1.974、aspect−.634bits，两CI负 | 两成分都贡献；没有隔离内部event graph |
| [E16](experiments/E16-patient-specific-crossover.md) | 两患者NP交叉，排一般self/reciprocal抑制；桥交互+2.111 [1.167,3.137]bits | 患者特异但实体曝光/lexical association仍竞争，非能力准确率 |
| [E17](experiments/E17-relation-versus-entity-accessibility.md) | 原关系vs noticed中性提及；same neutral −.976 CI跨0，relation +7.823；额外交互+1.413 [.539,2.411] | 限制entity-only解释，仍不能排谓词检索/语义关联；中性并非严格零 |
| [E18](experiments/E18-predicate-paraphrase-transfer.md) | 独立动作释义；faithful9交互+1.439 [.895,1.908]bits | exact verb echo不足；related/faithful/边缘语法分项保留，不能叫完整semantic机制 |
| [E19](experiments/E19-late-exclusive-role-evidence.md) | 加晚到only-X/not-Y双向角色事实；GP移动+8.51、cue+10.60bits | fact有效不等于旧关联删除；separate后文3源可能仍回指旧活动，strict范围只有4源 |
| [E20](experiments/E20-exclusive-fact-versus-last-mention.md) | 同事实改变最后提及对象；7/7 history R负，均值−3.403 [−4.276,−2.444]bits | 顺序解释部分；绝对GP已支持允许对象，不能称完全不更新 |
| [E21](experiments/E21-named-versus-generic-exclusion.md) | 具名vs泛指排除；严格4源history读数差+3.06 [2.03,4.38]bits | POST-HOC主要cue−2.97bits、GP约+.09；不是named更好修复 |
| [E22](experiments/E22-post-correction-entity-versus-role-use.md) | named/generic×关系/neutral，GP−cue差−2.792 [−3.680,−1.904]bits | 局部测量C04；acceptable-only无GP，读数null；还没有实际错绑定证据 |
| [E23](experiments/E23-functional-role-continuation.md) | 224实际greedy续写＋一句恢复，完整外审 | 首审10→次审6明确contradiction，unknown多、48token cap多；首NP不是患者，功能失败不稳 |
| [E24](experiments/E24-independent-correction-use-transfer.md) | 12family独立来源；history交互−.795 [−1.210,−.394]bits，strict9−.766 | 跨source有概率结构，不能追认E23能力错误或event-specific精准修订 |
| [E25](experiments/E25-event-versus-actor-correction-scope.md) | 原事件/同actor新事件/另一actor新事件；后两交互−1.249/−2.070bits | 迁移不是只在旧event；新患者未指定，不能叫world scope错误 |
| [E26](experiments/E26-scoped-constraint-access-versus-portable-trace.md) | scope比较和final解释；八项joint base0，旧活动两互补题全No | 两问平均50%不是scope能力；先测算子与回答默认值 |
| [E27](experiments/E27-allowed-fact-relation-positive-control.md) | 匹配allowed命题；768新任务，allowed比较joint100%，excluded仍joint0 | 排纯No/default和全套truth验证，但支持/兼容/不确定任务解读仍竞争 |
| [E28](experiments/E28-three-way-event-constraint-state.md) | E/C/U三类、cyclic labels、unrelated控制；新sameActor U33.68%、other65.28%、unrelated100% | label/mapping波动强；未建立正确scoped状态与portable预测共存 |
| [E29](experiments/E29-source-ablation-dual-readout.md) | 移除原S1，保留角色事实；raw旧J+2.88、新same−1.59/other−3.06bits | GP不是必要；source-free不能叫GP修订残留；一般提及与contrast竞争 |
| [E30](experiments/E30-event-boundary-versus-participant-contrast.md) | separate→second边界；新same/other activity约−1.64/−2.11bits | exact separate非必要；native与预测不同，不能强合机制 |
| [E31](experiments/E31-predicate-match-versus-narrative-contrast.md) | 同/不同V，old/new actor及NLI；出现predicate-dependent结构，登记C05 L1 | 换V同时改meaning/selection；不能证明语义role存储或普遍反转 |
| [E32](experiments/E32-fact-order-versus-predicate-transfer.md) | 同token事实换序；sameV新activity−3.21/−4.48bits，different−same J+1.94/+2.36 | neutral也变；绝对不同V方向不跨order保留，不能只报J |
| [E33](experiments/E33-same-action-paraphrase-transfer.md) | 同一基本动作释义，两order；clear8新other J−2.165/−2.144bits，old+3.926 | exact新stem重复不足；非GP、未assert旧错误，仍只是动作/表述相关aftereffect |
| [E34](experiments/E34-retracted-report-versus-hypothetical-history.md) | 真撤回report vs hypothetical prior，相同final；来源H_J−.433 [−.710,−.129]bits | factual与hypo都有痕迹；冲突old-source native仅54.17%，不能叫成功revision后残留 |
| [E35](experiments/E35-current-world-priority-recovery.md) | 一句current-world priority；54.17→68.75%，paired+14.58 [12.50,16.67]pp | 三label mapping91.67/62.50/52.08；只部分恢复，不能挑一个map称能力完整 |
| [E36](experiments/E36-affirmative-role-versus-negated-alternative.md) | 肯定only、提及顺序；first oldJ+2.296、新other−1.790bits | 显式not非必要，但last other CI跨0；all-order普遍反向未成立 |
| [E37](experiments/E37-time-indexed-role-answer-without-letter-labels.md) | 自然短语current/initial/account；624明确正确，joint100% | 新who题432初审“文字有据0%”不是自然错误率；第三审语用不确定，首审指称参照不一致 |
| [E38](experiments/E38-independent-target-selection-versus-narrative-contrast.md) | 明确independent selection/fairness/selected-outcome；fairness效应局部，native1532clear＋4可恢复 | 文本预测不是概率信念；知道1/2不等于下一字符串概率1/2；不以generic gap认证novelty |
| [E39](experiments/E39-two-named-patients-without-reflexive-contrast.md) | 两个非反身named患者 | 反身非必要；仍在人工frame，不能叫ordinary language普遍作用 |
| [E40](experiments/E40-plain-role-versus-exhaustive-focus.md) | 去only/not；新other J−9.921/−7.238bits | old absolute D+.291/−.358近0，所谓old控制仅J/native成立；没有绝对old正/new负完整控制 |
| [E41](experiments/E41-event-completion-versus-participant-availability.md) | 结束/未知/明确ready；ready新J−6.236/−6.611，availability192/192正确 | 物理不能再参加不足以解释；原姓名/possessive指称问题保留，不把unknown前置No强判正确 |
| [E42](experiments/E42-native-continuation-versus-raw-text.md) | 原生条件续写评分；old activity正、新same负 | native也有很强neutral响应；teacher-forcing大数不是自由生成错误、world belief或新机制 |
| [E43](experiments/E43-minimal-event-facts-without-candidate-scaffold.md) | 最小普通名字事实；oldD+26.808、新same+20.878，native96/96正确 | **普通语言绝对反转被否定**；old J也负，neutral subtraction不能自动认证纯role |
| [E44](experiments/E44-balanced-natural-scene-versus-entity-exposure.md) | 普通场景配平提及、两order、ready；old+10.17/+9.05，新+2.62/−1.32(last CI跨0)，ready+5.76/+4.12 | **普遍跨自然场景故事不成立**；native576正确；保留反证、不筛order |
| [E45](experiments/E45-scaffold-preserving-proper-name-substitution.md) | 原frame只换proper names；新D−13.545/−12.625 | 不是description/possessive单独造成；old+.173 CI跨0/−2.004，old阳性控制偏弱 |
| [E46](experiments/E46-factorized-discourse-scaffold.md) | identity/report/event三因素；identity新D−6.556、interaction−3.335bits，native1534/1536正确 | report非必要；event作用含一般提及；identity meaning/词串曝光尚未分开 |
| [E47](experiments/E47-identity-assertion-versus-mention-list.md) | 断言/未核实引用/纯inventory；inventory−absent−3.849，quote−assert+1.076bits | 身份断言非主必要条件；new−old J inventory CI跨0；不是global关系排他机制 |
| [E48](experiments/E48-referent-preserving-form-crossover.md) | alias固定，fact/readout Name/Desc交叉；matching old增强+2.721/+3.455，新更负−1.521/−2.076bits | 表达匹配重要；跨形式并非全零，order也不齐；alias96正确、old758/768，不叫新entity机制 |
| [E49](experiments/E49-role-use-with-observed-second-event.md) | 真明说第二角色，单问vs formal recap；单问1530/1536，recap joint976true/506false/54unknown | audit首轮格式误判后完整重审；congruence CI跨0、不同V反而更差，不能合成C05同一机制 |
| [E50](experiments/E50-joint-role-use-versus-recap-format.md) | 三种联合用途；pair41.406% [36.719,46.484]，普通anchored98.047% [96.484,99.349]；pair同−异−54.688pp | 任务/输出格式很强；two names/entities可能诱发distinctness；generic retrieval/use gap非novelty |
| [E51](experiments/E51-role-occurrences-versus-referent-cardinality.md) | neutral pair/keyed/count×base/repeat；4608推断完；literal neutral joint81.51–82.42%，repeat91.28–91.54% | neutral仍同−异−26.56..−24.74pp，但最终语义审计缺；keyed多格式未解析、count定义/描述字串混杂和5cap；不作为已验证idea |

## 4. 必须显式保留的失败与勘误

1. **校准失败与停步错误。** E00–06没有解决整套测量的顺序/floor问题；后来用户明确取消自动gate。旧卡中的历史“未进入E01”只描述当时，不是当前授权，也不表示现在仍需要gate。
2. **事件/角色读数不等于真实错误。** E13 whole-S2近零；E23实际续写明确错误少且审计不稳；E37新who题初审错误解释作废；E43/E44普通场景反证是实质性结果，不能跳过。
3. **中性扣除并非自动净化。** E43 old J也负、E42 native neutral极强、E40/E45 old absolute控制偏弱；所有后续叙事保留这些限制。
4. **数据/语义审计也会错。** 原题tomato/tomatoes与floor/road；Jurayj部分配价/拼写；earlyQA未assert不能一律No；E49缺冠词与分段误判；E50固定class小错；原审核、重审、分歧均留cache，不能把模型审计称人类Gold。
5. **E51 Step批协议失败。** 192批（每批24回答）仅39批完整、936/4608回答。108批max_tokens、29批缺passage_sha256、12批schema断言、4批缺item_id。所有请求/响应保留，未自动重试；API确实走Step Plan，无HTTP账户/端点错误记录。失败是本次批大小/协议完成性的实际问题，不能冒充全审通过，也不能据成功批推总体效果。
6. **E01全量输入审计仍不全。** 626请求中565完成，59max_tokens＋2JSON解析失败；得到2405/2672QA注释。未采用成完整新的推断集；旧snapshots与新审计不混成一次复现。
7. **探索效率不足。** E19–48累积较多自构frame、词序/措辞/角色用途校对，逐步排除了多个错误解释，但自然材料的决定性功能验证仍晚、未完成。大量局部阳性并没有自动形成有价值主旨；整理必须呈现这个距离，而不以实验数量代替novelty。
8. **本次整理错误。** 我最初把“不上传大文件”误处理为压缩；用户明确纠正后，所有压缩包/读取改造已撤销，原分析逐字节恢复。没有压缩包上传，没有覆盖原统计或重写Git历史。

## 5. 数据、环境与未执行的工作

| 资产 | 已完成 | 未完成/限制 |
|---|---|---|
| Amouyal / Jurayj / Turing | 初始3源revision/license/逐文件SHA；规模276QA/90component sets/两个48句TSV；统一schema | Turing是grammaticality刺激，未伪造comprehension Gold，未独立复现 |
| SAP | 官方原题与source audit；E09/E10/E12完成 | 原题少量target类型/mapping读数有限；不是新benchmark |
| Slattery / Čeháková | 公开原材料本地转录/解包及license/hash；自然后文与独立24source用于已有实验 | 原后文只有7明确episode；版权与派生文本不进git |
| GUM | 固定22fdf87f…；43 news/fiction文档，34683tokens；最终174候选全保留、14明确pre-alias条件 | 没有Qwen实验；原UD object不自动等于本研究患者，不能说174高质量Gold |
| WikiEvents | code revision253e0889…；六release文件/hash，246docs/3951events/5536arglinks；loader offset处理 | news版权不等于code MIT；无event-coref；14配对适配review中7明确不同事件、6不确定、1同一事件；个别标注角色不获原句支持，未推断 |
| 本地模型/环境 | Qwen3-8B revision b968826d…，14文件bytes逐个HF镜像核验；existing venv；FP32/SDPA/no-thinking/greedy/seed0；独立单卡 | 多卡用于独立shards；没有把8卡当高速训练集群；无SAE/probe/训练 |
| Step Plan | 固定step-5-preview，Messages /step_plan/v1/messages，总并发≤8、无代理、key仅私有配置 | 实际完成率如上，不用现金账户、不把max_tokens当审计完成；暂停后不发新请求 |

较新的自然数据采用来源/loader及适配所需检查，不再无差别全库逐条重审；构造/新增标注依用户要求用Step Plan。历史Luna/opencode审计保留原来源，不追改标签和模型署名。

## 6. 暂停留下的问题，不是继续运行的计划

- 当前最值得辨别的线索：联合角色问答是否诱发“不同角色默认不同实体”，以及它与普通输出列表惯例、alias解析、question presupposition的关系。E51只是局部线索，尚无完整语义审核和自然transport。
- 尚缺：上述区分的可靠全量读数、自然任务的真实后果、与已有presupposition/multi-answer/entity-binding工作的清晰增量，以及人对品味/尺度的判断。
- 若用户恢复，应先读这份总结、原卡与完整失败记录，避免再以同模板小改/更多模型寻显著性。这里不新建实验、不排日程，不因为暂停自动关闭territory或把I01升为候选。

## 7. 文件与复现入口

- [文件索引](FILE_INDEX.md)：状态、数据、claims、实验、完整统计与脚本的入口。
- [全部run库存](results/RUN_INVENTORY_2026-10-06.json)：逐run config/输出hash、实际任务与本地路径；不是把复用行当独立实验。
- [E51小统计](results/E51-literal-schema-compact.json)：literal解析上下界与pairedCI，明确非完整语义审计。
- [Step暂停快照](results/D0-StepPlan-pause-snapshot.json)：全部结束、完成/失败计数、Plan端点与manifest hash。
- [分析资产索引](results/ANALYSIS_ASSETS.json)：原文件路径/bytes/SHA，完整统计原样保留；本次不新增大分析、数据或模型文件，不使用压缩。

所有原始数据、构造版本、审核请求/响应、失败、rollouts、checkpoint继续在 `/data1/xiangding/work/incremental-interpretation-revision/`。GitHub保留代码、实验卡、阶段结论和小统计。既有历史大文件本次不新增/重传，不据此重写历史。
