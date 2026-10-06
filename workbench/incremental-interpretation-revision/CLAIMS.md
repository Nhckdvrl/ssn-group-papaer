# 主张账本 — Incremental Interpretation & Revision

**状态：2026-10-06 / PROPOSED baseline residency。**

当前有局限于固定模型/协议的本地测量事实C03–C05，已有具体候选I01，但尚无已确立的一般机制或新颖性判断。C00–C02仍是待验证对象，不能写成revision机制finding。

| ID | 待验证对象 | 等级 | 当前证据 | 升级条件 |
|---|---|---|---|---|
| C00 | 本地 harness 能在公开 GP 数据上复现一个已知的 GP-specific behavioral deficit | L0 | [E00](experiments/E00-baseline-reproduction.md) / [结果](results/E00-summary.json)：全 16-prefix 主效应 −2.81 pp [−11.50, 5.89]，顺序敏感，gate 未通过 | E00 阳性对照通过，并报告 item-paired CI |
| C01 | interpretation revision 可被“最终解释支持”和“初始错误解释残留”两个读数分开测量 | L0 | [E01](experiments/E01-component-revision-map.md) / [partial](results/E01-partial-summary.json)：独立Step5审核3句/13QA，104任务；NPZ对比只有一个lexical set，role与semantic不同响应待全量核对 | 受控构式中不同读数的响应具有稳定、可重复结构；不把语义兼容命题强标错误 |
| C02 | 不同 cue timing / cue strength 条件下存在可区分 competing accounts 的 revision structure | L0 | 仅 territory hypothesis | 预先写出不同解释的预测并由 E01/E02 区分 |
| C03 | 固定Qwen3-8B的GP/nonGP问答差值随query顺序反向，且反转不依赖assistant prefill或few-shot demos | L1（measurement；非novelty） | [E03](experiments/E03-e00-order-and-assertion-audit.md)、[E07](experiments/E07-native-readout-transfer.md) / [E07结果](results/E07-summary.json)：neutral/native/base交互+60.87 pp [44.93,76.81]；全部8个boundary×system×instruction交互正；67-set sensitivity同方向 | 下一步[E08](experiments/E08-reading-focus-versus-final-query.md)将final query固定，区分reading focus与回答启动/位置；目前不归因为内部parse或一般LLM能力 |
| C04 | 同一排他事实的具名/泛指表述对后续实体提及与活动患者偏好产生不同响应，且GP与逗号历史调节该响应 | L1（局部measurement，非能力/机制/novelty） | [E21](experiments/E21-named-versus-generic-exclusion.md)、[E22](experiments/E22-post-correction-entity-versus-role-use.md)/[E22统计](results/E22-summary.json)：严格4源named−generic的relation-minus-neutral变化GP−2.792 [−3.680,−1.904]bits、cue−.174 [−1.124,1.201]；全7同方向；[E24](experiments/E24-independent-correction-use-transfer.md)/[统计](results/E24-summary.json)独立12family主history交互−.795 [−1.210,−.394]、strict9−.766 [−1.168,−.363]。角色事实有效，实际错误未稳健成立 | 独立来源预测/实际角色使用、混杂审计后才讨论更一般解释；当前不能把概率偏好叫false belief或内部绑定 |
| C05 | 固定Qwen3-8B中，account/identity/report框架内，新other同谓词患者预测反向；普通名字场景未稳定迁移，非排他条件old absolute控制偏弱 | L1（限定协议measurement；2026-10-06收窄） | [E40](experiments/E40-plain-role-versus-exhaustive-focus.md)/[统计](results/E40-summary.json) 两order新J−9.921/−7.238；[E41](results/E41-summary.json) ready两order−6.236/−6.611；[E43](results/E43-summary.json) 最小事实所有new absolute D正，old J也负；[E44](experiments/E44-balanced-natural-scene-versus-entity-exposure.md)/[统计](results/E44-summary.json) old D+10.174/+9.054，newother D+2.623/−1.320(last CI跨0)，ready D+5.760/+4.124，native576明确正确 | E45名字仍反向但old absolute D近0/负；E46匹配分解frame；不得称一般角色反转或成功修订后残留，先定位自然语言必要变量及功能后果 |

**禁止提前升级：**
- 上游已报告的 garden-path effect 不是我们的 C-level novelty；
- “某模型答错很多”不是机制主张；
- probe/hidden-state separability 不能单独升级为“模型保留旧解释”。

## 作废 / 降级 / 未通过记录
- 2026-10-05 用户修订：取消agent用C00校准结果限制E01的停步gate；保留旧结果/证据等级，直接推进[E01](experiments/E01-component-revision-map.md)。C01/C02是measurement对象，不预注册novelty；最新论文ownership见[知识库](../../library/themes/incremental-language-processing/FIELD_MAP.md)。
- 2026-10-05：E00 不升 C00。句先有已知方向，但 prompt suite 整体不稳定；不得把选择句先视作通过。E03 注册追 why，原 E00 结果完整保留。

- 2026-10-05：[E04](experiments/E04-known-positive-control.md) 正方向 +19.84 pp [14.04, 25.82]，但 nonGP 30.71%、raw specificity DiD CI 跨零；[E05](experiments/E05-response-meaning-calibration.md) 8B 的 assertion response 下句先 +30.43 pp、题先 −23.91 pp。C00 不升级；原协议有效性问题未解决，不能把 positive direction 当严格 gate。C01/C02 未运行。

- 2026-10-05：[E06](experiments/E06-attachment-versus-event.md) GP subject-role控制仅0–5.80%，object-No高分不作为恢复证据；C00/C01/C02仍L0。nonGP joint读数是P06的测量痛点，不作隐藏parse或novelty主张。

- 2026-10-05：[E11](experiments/E11-extension-role-reference-audit.md) n1外审概率pilot：无歧义blocked extended的原短NP role PYes=.0404→fullNP=.9999，final semantic=1；不再将这项role extension下降解释为digging-in/commitment。四配置fullNP同向，head有题先失败；GP extended的新增问句未审完，结论范围明确限制。不是拒绝C01，也不是升级其能力/机制主张；旧E01分数和全部prompt保留。

- 2026-10-05：[E12](experiments/E12-input-probability-versus-answer-access.md) source processing存在提前Q效应，24clusters的GP−cue disamb交互+1.47 bits [.47,2.52]由cue facilitation主导；source word预测与最终QA不可混作同一读数。C03固定协议测量保留，C01/C02仍L0，不据此主张内部parse/承诺机制或novelty。


- 2026-10-05：[E13](experiments/E13-natural-followup-without-diagnostic-question.md) / [结果](results/E13-summary.json) question-free全自然S2 GP−comma −.031 [−.255,.211] / −.003 [−.173,.176]bits，不支持普遍后文代价；字面reference option交互+.905 [−.296,2.260]、其后邻词−.377 [−.637,−.111]，局部解读不确定。没有新能力/内部双parse/novelty主张；C01/C02保留L0。


- 2026-10-05：[E01 snapshot3](results/E01-external-snapshot3.md) / [完整统计](results/E01-external-snapshot3-summary.json)：NPZ initial-event extension DiD句先+51.63 [21.60,84.02]pp、题先−20.29 [−53.11,9.93]n9，统一commitment解释支持不足；NPS源7语法marginal主导eligible部分读数，acceptable同步报告；不将外部annotation agreement或原role题当内部parse能力。C01/C02仍L0。

- 2026-10-05：[E14](experiments/E14-event-identity-versus-extra-event.md)/[E15](experiments/E15-fixed-aspect-event-reference.md)：7episodic组原same−separate −2.61 [−3.78,−1.09]bits，固定continued仍−1.97 [−2.78,−.69]，aspect/预设贡献−.63 [−1.10,−.22]。只支持混合的条件续写响应；source-NP相对self/reciprocal偏好尚不能证明患者特异旧绑定，C01/C02维持L0。

- 2026-10-05：[E16](experiments/E16-patient-specific-crossover.md) / [统计](results/E16-summary.json)：7episodic固定continued的患者特异桥交互A_M+2.11 [1.17,3.14]bits，7/7正；other-NP相对ref交互+.14 [−1.06,1.30]。排除“仅一般self/each-other抑制”不足以解释全部结果；仍未排除一般entity accessibility/lexical association，C01/C02不升级机制主张。

- 2026-10-05：[E17](experiments/E17-relation-versus-entity-accessibility.md)/[统计](results/E17-summary.json) 7源neutral GP患者提及差−.98 [−2.53,.69]而原谓词续写+7.82 [5.39,10.23]；额外scope interaction A_K+1.41 [.54,2.41]，neutral自身+.70 [.46,.93]。限制entity-salience-only解释，仍含lexical predicate retrieval/repair竞争，未建立新semantic mechanism，C01/C02保留L0。

- 2026-10-05：[E18](experiments/E18-predicate-paraphrase-transfer.md)/[统计](results/E18-summary.json) 独立faithful9源释义A+1.44 [.90,1.91]bits，strict episodic4（含1marginal）D_M_same+6.95 [4.89,9.68]。限制exact surface-verb echo但未证明prior correction完成或internal semantic state。I01已登记PILOT，C01/C02不升机制主张。

- 2026-10-05：[E19](experiments/E19-late-exclusive-role-evidence.md)/[统计](results/E19-summary.json) 7源明确角色双向控制使R移动GP+8.51 [5.15,12.32]、cue+10.60 [7.75,13.55]；reference-only后history差R−5.52 [−8.06,−3.29]bits。控制有效不等于旧关联删除，但negated-NP最近提及仍竞争；C01/C02不升机制主张。

- 2026-10-05：[E20](experiments/E20-exclusive-fact-versus-last-mention.md)/[统计](results/E20-summary.json) 同事实把允许对象最后说，7/7仍history R负，mean−3.40 [−4.28,−2.44]bits；GP绝对R+1.73 [.58,2.91]且role控制+9.56，不支持“完全不更新”。对象顺序解释部分，named remention仍未分；C01/C02不升语义机制主张。

- 2026-10-05：[E21](experiments/E21-named-versus-generic-exclusion.md)/[统计](results/E21-summary.json)严格4源named相对generic减小GP−cue差+3.06 [2.03,4.38]bits，但POST-HOC拆分主要cue−2.97 [−3.77,−1.60]、GP+.09 [−.93,1.12]。不支持“named更好修复”，也未证明错误再绑定；C01/C02不升机制结论。

- 2026-10-05：[E23](experiments/E23-functional-role-continuation.md)/[首审](results/E23-first-review-summary.json)/[次审](results/E23-summary.json)实际续写不支持稳定的role-violation结论：224标签10→6明确contradiction，严格4源NP0 base均无明确违反但多患者省略。首次GP差CI含0且语义标注不稳定；C04局限likelihood，不能升能力/false-belief/机制等级。原审计和全部输出不作废、不删改，POST-HOC完整次审透明保留。

- 2026-10-05：[E25](experiments/E25-event-versus-actor-correction-scope.md)/[统计](results/E25-summary.json)：C04信号迁移到同actor新event I−1.249 [−1.757,−.762]bits、另一actor新event−2.070 [−3.099,−1.200]；actor_transfer−.820 [−1.460,−.322]。不支持以此信号单独证明old event绑定未修订；portable association解释增加，但未证明scope错误。C04仍L1，下一E26 scope/final interpretation读数独立审计。

- 2026-10-05：[E26](experiments/E26-scoped-constraint-access-versus-portable-trace.md)/[统计](results/E26-summary.json)原句final主体读数GP94.79/91.67%、cue100/100%，但互补scope比较base原活动两问全部No（平均50）；八项joint base0。未建立scoped constraint access，不把50%叫scope failure；先E27匹配allowed-proposition控制区分No default/命题验证/比较算子。C04 L1/I01 PILOT。

- 2026-10-05：[E28](experiments/E28-three-way-event-constraint-state.md)/[统计](results/E28-summary.json)未证明局部约束与portable预测共存时scope判断正确：all12新活动U同actor33.68 [23.96,44.79]% /otherActor65.28 [59.72,70.49]%，unrelated U100%；signed-role迁移GP58.60/12.34pp、cue55.92/13.53，映射波动大。不能归因为GP-specific或与E25同一机制；C04 L1/I01 PILOT，下一源S1消融。

- 2026-10-05：[E29](experiments/E29-source-ablation-dual-readout.md)/[统计](results/E29-summary.json)移除完整S1仍有native scope迁移，同actor61.25 [52.07,70.07]pp、换actor10.97 [4.81,18.79]，GP不是必要条件。具名事实的患者预测J旧event+2.88 [1.81,3.83]bits，新同actor−1.59 [−2.45,−.71]、另一actor−3.06 [−4.12,−2.04]；POST-HOC实际activity方向也翻转，非只neutral主导。generic不同、边界词contrast竞争尚未排除，C04 L1/I01 PILOT；不能硬合为旧绑定残留。

- 2026-10-05：[E30](experiments/E30-event-boundary-versus-participant-contrast.md)/[统计](results/E30-summary.json)具名患者反向预测在second边界仍在：sameActor activity方向−1.641 [−2.635,−.805]、other−2.109 [−2.905,−1.278]bits，neutral近0；原event+2.646。只排除exact separate触发，不排所有contrast/关系抑制。native旧方向迁移仍正，既有一句scope控制不稳定修复，不能包装generic gap或强机制；C04 L1，下一cross-predicate区分。


- 2026-10-05：[E32](experiments/E32-fact-order-versus-predicate-transfer.md)/[统计](results/E32-summary.json)同token事实改序后，同V新event绝对反向保留（sameActor −3.213/other −4.483bits），但neutral也反向，sameActor J CI跨0、other J−3.307 [−4.769,−1.875]。不同V绝对变正不跨order保持；更稳的是different−same的matched-neutral J差+1.937 [1.043,2.841]/+2.359 [1.444,3.359]。因此C05保留L1历史测量，收窄“换V改变绝对方向”到具体事实表述；不升级成语义关系或普遍反向机制。


- 2026-10-06：[E33](experiments/E33-same-action-paraphrase-transfer.md)/[统计](results/E33-summary.json)独立basic clear8场景，旧event释义J+3.926 [3.005,4.912]bits；otherActor new两事实顺序−2.165 [−3.541,−.949]/−2.144 [−3.877,−.296]。sameActor J不确定但释义−不同动作差仍负，所有all/related、自然7、strict6完整保留。限制exact new-stem重复解释，词汇boost/focus/语义关联仍竞争。C05扩充L1条件性测量，不升级actual revision mechanism；source-free条件没有asserted错误初始事实，下一须直接测history，而非继续词汇局部优化。

- 2026-10-06：E34 [卡](experiments/E34-retracted-report-versus-hypothetical-history.md)/[统计](results/E34-summary.json)，预注册newother/ref-only factual−hypothetical H_J−.433 [−.710,−.129]bits；final old J+2.477、new−2.264，但冲突old-source native仅54.17 [51.39,57.64]%，不得称成功修订后的残留。C05保留L1/I01 PILOT；E35一句current-world优先级区分任务解读与final访问，E36准备affirmative角色实现区分focus。无需人决定执行这些已授权区分实验。

- 2026-10-06：E35 [卡](experiments/E35-current-world-priority-recovery.md)/[统计](results/E35-summary.json)，current-world指令factual冲突oldsource54.17→68.75%，paired+14.58 [12.50,16.67]pp，三map91.67/62.50/52.08%；final C100而E8.33→37.50。部分任务解读可恢复、mapping/否定竞争仍未解，不声称成功revision。C05 L1不变；E36肯定role/mention顺序独立审计raw1920/native672，三卡推理进行中。

- 2026-10-06：E36 [卡](experiments/E36-affirmative-role-versus-negated-alternative.md)/[统计](results/E36-summary.json)，肯定only、mention-first old J+2.296 [1.194,3.357]、newother同V−1.790 [−2.739,−.838]，predicate差+1.352 [.352,2.325]bits；mention-last otherActor−.246 CI跨0，all-order普遍反向不成立。显式not-X非必要、only/focus/recency未排除。C05 L1；E37无字母标签事实回答、E38明确新事件独立抽样继续高信息量区分。

- 2026-10-06：E37 [卡](experiments/E37-time-indexed-role-answer-without-letter-labels.md)/[统计](results/E37-summary.json)，624current/initial/account直接短语全correct、joint100% [100,100]。432new问句初审文字支持0%，第三审自然correctness全uncertain，不能称真实role error；首次new entity分类参照框不一致，已标无效解读、原数保留。C05 L1，E38用明确选择结果/概率取代活动默认who读法继续why。

- 2026-10-06：E43/E44反驳“普通语言中稳定反向角色迁移”的扩大解释，C05从E29–33的候选叙事收窄到已测描述/报告框架；等级仍L1，全部正负结果保留。E43 old J也负、new absolute D正，neutral subtraction不能认证纯role测量。E44普通场景ready old-role/availability576明确正确，new角色预测正；不借subset/order筛选挽救普遍叙事。E45追NP realization vs frame。

- 2026-10-06校对：E40 old activity D+.291/−.358近0，此前“old控制有效”仅J/native成立。E45名字替换仍newother D−13.545/−12.625，但old+.173 CI跨0/−2.004，不能称name条件old正/new负；191/192native正确。frame影响可能包括一般反重复/提及，E46分开activity/neutral及new−old。

- 2026-10-06：E46 8cell身份说明主newSame activity−6.556 [−7.935,−5.254]bits，identity×event−3.335 [−4.091,−2.500]；unused report非必要。new−old J的identity−4.357 [−6.206,−2.434]但event−.270 CI跨0，不能把general mention的全部效应叫关系机制。原人工frame中的必要表达成分更清楚，C05仍L1。E47区分assertion地位、quoted词串与纯名称曝光；尚无内部机制或一般能力结论。

- 2026-10-06：E47纯name inventory−absent newSame D−3.849 [−5.053,−2.670]bits；unverified−asserted仅+1.076 [.264,1.815]。因此不得把E46身份主作用归为身份断言含义，mere actor/entity exposure与语篇结构仍主竞争解释。inventory对new−old J CI跨0，predicate差+1.940 [1.232,2.660]独立报告。native old患者1536correct、status383/384，不将readout gap单独作为novelty。C05仍L1，已进一步收窄。

- 2026-10-06：E48 [卡](experiments/E48-referent-preserving-form-crossover.md)/[统计](results/E48-summary.json) alias固定后表达匹配old D增强+2.721/+3.455、newSame更负−1.521/−2.076bits，paired CI均不跨0；跨形式较弱但I1 Desc→Name仍−.968 [−1.682,−.253]，不能宣称完全词汇局限。mapping96correct，old758/768；I0 Desc→Desc平均old+5.863/new−2.913但first CI跨0，不包装各order稳定。C05仍L1/I01PILOT，下一E49明确第二角色事实后的实际复述，不以一般binding/priming或gap认证好idea。

- 2026-10-06：E49 [卡](experiments/E49-role-use-with-observed-second-event.md)/[统计](results/E49-summary.json)第二patient直接问1530/1536正确，formal joint976/1536true、54unknown；basejoint bounds61.98–64.97%，pairedfamily95CI宽。congruenceCI跨0，differentV在incongruent/base反而约−20pp，不能把C05预测偏移和这些角色错误认同为同一机制。首轮审计格式误判作废解读、完整重审/cross及951firstcorrected对照保留。C05L1/I01PILOT不升级；E50区分普通复述/联合Names/actor retrieval cue。

- 2026-10-06：E50 [卡](experiments/E50-joint-role-use-versus-recap-format.md)/[统计](results/E50-summary.json)：列表joint41.41% [36.72,46.48]、同patient−不同patient−54.69pp [−60.68,−47.92]，而actor锚定普通复述98.05%。反驳将formal复述错误直接扩为一般角色使用失败；two names问法的不同实体预设是POST-HOC竞争解释，E51事前无该预设/分栏/计数/允许重复对照。未把该差认证novelty，C05L1/I01PILOT。
