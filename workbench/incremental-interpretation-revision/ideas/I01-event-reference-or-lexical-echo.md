# I01：旧关系再次影响续写，触发它的是活动回指还是原词重现？（2026-10-05）

- **状态：** PILOT（候选问题；不是已经找到的好paper idea）
- **来源：** P10；E14/E15把指向与aspect分开；E16患者特异交叉；E17中性entity control。先有异常与解释淘汰，再提出RQ，不从概念二分猜题。
- **研究动作：** 条件化异常 + 竞争解释分离 + 语义保持的语言干预。
- **如果为真，主张是：** 在相同最终合法句法下，旧患者关联对后续功能使用的影响取决于活动指向和后文谓词。更强的“已修订却被重新激活”还需证明最终解释确实恢复，当前不能写。
- **证据：** 原episodic7源：E15固定continued同/另一活动interaction −1.97 [−2.78,−.69]bits；E16患者特异 A_M+2.11 [1.17,3.14]、7/7正；E17关系使用−中性提及 K_same+8.80 [5.75,11.74]，额外scope A_K+1.41 [.54,2.41]，但neutral自身+.70 [.46,.93]。全22也保留A_K+1.27 [.49,2.06]。这支持一个条件化reuse问题，不能证明semantic event graph。
- **不同结果的信息增益：** 原谓词释义后患者效应保留 → 狭义原词echo不足，继续区分关系记忆与noisy-channel对源句的repair；释义后下降且变换语义/语法可信 → 原词重新访问旧关联更相关，不能讲完整semantic persistence；语义忠实性不够/切片不足 → 数据结论不确定，优先找已发表近义材料，不以分数挑同义词。

| 最近邻 | 已拥有的claim | 待验证的增量 / compression risk |
|---|---|---|
| Slattery et al. 2013；Sturt2007 | late semantic persistence、下游reflexive与旧解释、竞争句法/语义解释 | 同/另一活动×患者/中性提及×原谓词/释义，区分reuse的触发来源；“仍有旧解释”本身完全被拥有 |
| Cao & Schuler2025 CMCL | completion、error-control、reflexive binding、noisy-channel/局部错误忽略 | 需要event-reference效应在合法性/释义控制下的预测；只加binding readout会被压缩成重复 |
| Hanna & Mueller2025 NAACL；Li2024；Amouyal2025 | parse/QA不复用、initial/final问答、lingering、cue、paraphrase验证 | 不讲一般readout gap，问question-free正常后文中关系何时再次使用；paraphrase本身也已有owner |

- **最便宜的决定性 pilot：** [E18](../experiments/E18-predicate-paraphrase-transfer.md)，同source/NP/GP-cue/活动指向，独立构造与复核谓词释义；固定原始对照E16。阳性对照/噪声/决策表以事前实验卡为准，不刷更多prompt。
- **预期论文形态：** 解释条件化功能失败的受控研究；有可预测语言干预才有paper narrative。若只剩一般GP-deficit，继续在本territory测量，不自动关线。
- **排序打分（1–3，agent provisional）：** 证据2、增量清楚度1、形态匹配2、成本3、可完成性2、信息增益3。不能替人给Sasano签品味。
- **仍缺什么：** exact lemma-independent transfer、late explicit role证据/合法与malformed control、真正恢复后再用的证据、跨现成source独立验证。当前只有第一条有数据来源的候选问题，没有PROMISING或顶会like宣称。
- **最新定位：** 2026-10-05 venue-nearest：Amouyal2025、Yoshida2026，另有大量不相关entity/event检索项；最新primary arXiv检索未发现这个精确factorization，但搜索覆盖不完整，不能当新颖性证明；[知识库](../../../library/themes/incremental-language-processing/FIELD_MAP.md)。
