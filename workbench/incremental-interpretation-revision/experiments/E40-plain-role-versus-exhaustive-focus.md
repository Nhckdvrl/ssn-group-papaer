# E40：普通角色事实还是排他焦点？（2026-10-06）

- **状态：** DONE
- **类型：** PILOT
- **对应：** C05 / I01 / P11；E39已排除self/reciprocal必要性，但only/focus和一般角色关系仍竞争。
- **问题（一句话）：** 不包含only/not/but的普通肯定患者事实，是否仍在旧event帮助、新同类event反向影响预测？
- **设置：** 保留E39两个明确不同具名对象、identity intro、原旧actor/活动、source/donor targets和全部原后文。Luna逐条写plain affirmative role A/B，unused entity只在report mention句出现，两世界A/B各一次且词袋相同；mention-first/last两顺序。无only/not/but/sole/exclusivity同义表达，也不添加否定旧关系、两人都行动、因果/次数/未来线索。用E39 affirmative两形式删除排他性后的语义版本，不声称真值等价（plain不排除未陈述患者）。原old192 + new768 ×2forms=1920raw。旧活动直接检索96contexts×base/scope=192greedy responses，问“文中明确描述”的患者，不把普通assertion标为exhaustive。全文先独立审、先核causal target pair/hash再推理。parent E39冻结同NP/suffix/intro对照，allforms/actors/predicates完整报告。
- **读数：** M=bits(B)−bits(A)，D=old stated A−stated B，J=Dactivity−Dneutral；主otherActor/sameV J两order及plain−only paired，另old/sameActor/differentV与different−same J全报。native明确reported-role retrieval与一句R8全报。12family先两source平均bootstrap10000/seed20261005/95CI；all/eligible/grammar共同交集及E31固定11/9/9。不能用CI作为停止/准入门槛。
- **阳性对照：** ordinary old角色D/J正，两个old A/B direct retrieval皆可用；E39相同intro/suffix原分数冻结，检查唯一删除为排他性语义及对应提问限定。不作新的accuracy失败主张。
- **噪声地板 + MIE：** 固定FP32 frozen seed0，无种子筛选，1920非独立n。构造与naturalness独立审核；plain不是exclusive的真值等价改写，比较是exhaustivity intervention。
- **混杂审计：** 排他语义可能改变discourse focus/informativeness而非internal mechanism；mention-first/last、matched neutral控制只能区分部分解释。unused entity介绍与动作患者区分，named referents distinct。任何旧who问题默认exhaustive风险以“explicitly described”问句独立构造避免。结果不能用probability/QA gap当novelty；不做SAE/probe/训练/多模型sweep。
- **决策表（跑之前写）：** plain保留otherActor反向和predicate结构 → only/focus不是必要条件，下一对availability/result-state与叙事关系反重复做区分；only反向plain转正/无作用且old控制正常 → 增量收窄到exhaustive role信息怎样在跨事件成为关系备选，优先测focus alternatives的可预测语境边界；plain/only同向但order敏感 → explicitentity/order与关系信息混合；old控制失效或材料gold不清 → 先查why，不扩大sweep。所有分项/不利结果保留，不自行关闭idea/改ACTIVE状态。
- **算力预算：** 现有venv，单卡GPU0 raw/单卡GPU1 native独立，batch4/8，预计≤.10GPU·h；**实际：** 待填。
- **命令：** plain_role_facts.py build/adopt；event_identity_infer.py E40；time_indexed_role.py E40 current；analyze_role_controls.py E40。字段和大raw只在cache。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）

跑前审计：两个独立Luna全文2016packets完成；原QA schema请求漏了共用grammar/scope/distinct字段，adapter在推理前fail-fast，原审计员重读96questions补齐字段为v2，raw判读/文字/答案不变。中间partial probability-v1仅cache保留未推理；adopt改为全任务验证后才写文件，实际用audited-v2。Step5附加field-level交叉审计进行，初4096tokens有10次max_tokens截断，未采用不完整JSON，扩到16384一次修复，不作为科学门槛或筛input依据。1920 causal-target pairs已核，尚未推理。

[完整统计](../results/E40-summary.json)：first/last old J+4.736 [3.362,6.075]/+6.313 [4.767,7.738]bits；newother同V J−9.921 [−11.649,−8.000]/−7.238 [−8.731,−5.667]；different−same J+5.070/+4.255，两个CI正。去only没有消除反向，first反而比E39 only更负−2.353 [−3.198,−1.474]；last变化CI跨0，完整因素全部报告，不选择first。native192内容正确、189clear/3简写nephew指称不确定；actual run f044bc71。Step5额外24fields审核23acceptable/1marginal、scope/distinct/question全部clear、96facts全nonexclusive，不改Luna grammar共同比较层。[Step](../results/D0-E40-Step5-cross-audit.json)是post-hoc交叉，不假称前置human gold。only/focus不必要，物理availability与叙事关系反重复接E41。
