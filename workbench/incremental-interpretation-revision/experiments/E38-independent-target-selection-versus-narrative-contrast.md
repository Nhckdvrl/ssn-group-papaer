# E38：未公布的新事件选择，还是普通叙事对比？（2026-10-06）

- **状态：** PLANNED
- **类型：** PILOT
- **对应：** C05 / I01 / P11；把role-transfer解释分为正常叙事alternatives与忽视明确独立性，不注册概率/QA gap为novelty。
- **问题（一句话）：** 新活动对象明确来自独立公平抽签、结果未公布时，旧角色事实的反向预测作用是否仍在，是否影响对未公布结果的回答？
- **设置：** 固定24source/12family、E31 otherActor sameV及E36 affirmative mention-first两个role实现。旧事实两方向/中性noticed控制原后文不变；在new began bridge之后加入Luna独立构造两候选选择说明，target NP取原sourceNP/donorNP。五policy：短candidate-only、长度匹配procedure-unknown（方法/概率/结果未报告）、independent-fair（独立于旧activity、各1/2、结果未报告）、selected-source/selected-other。每个candidate顺序source-first/other-first，仅列表交换；raw3840。native仅procedure-unknown/independent-fair/selected双分支，768contexts×base/一句selection scope recovery=1536 greedy outputs。fair问题直接问事前概率，其他三分支问被选中的target，不问actor是否已执行动作，避免E37活动默认读法。所有完整inputs先独立审计。raw GPU0，native current/fair GPU1/2，已有Qwen3-8B FP32。
- **读数：** raw M=bits(otherNP)−bits(sourceNP)，old-role D及J=activity−neutral，按form/policy/order全报；主对比affirmative-first、两order分别fair−procedure-unknown的J，亦报平均、contrast实现及candidate-onlyparent。已公布selected-source−selected-other对M/J是正向selection控制。native逐条独立审selection答案/事前1/2：correct/unknown vs擅选source/donor、explicit-none/unclear，R8 paired scope recovery；family两source平均bootstrap10000/seed20261005/95CI。all/eligible、grammar共同acceptable（跑前审计冻结）、E31 anchor-clear11/acceptable9/parent-faithful9。
- **阳性对照：** selected-source/selected-other对new target prediction及direct selection retrieval；fair概率1/2、procedure-unknown结果应未知，candidate-only没有声明已发生selection所以不问结果。旧event positive controls复用E29/E36冻结分数。原no-policy同V分数全部冻结，不能只挑实现/顺序。
- **噪声地板 + MIE：** n12不是3840独立n；固定FP32；unknown/fair action-stem提及及长度匹配0–2words差，隔离仅旧事实更远解释。效应CI而非达到某阈值停步。
- **混杂审计：** 此为明确构造的选择协议，healing/fighting等random target人工感独立标注，不冒充自然事件样本。抽中target不保证已实际行动，所以native只问selection、raw只测活动续写预期；selected并非现实执行accuracy。Token likelihood是字符串分布而不是world chance（Wagner/Abend ICML2026 position已owns该概念）；不能因M不等于0叫不知道1/2或因native1/2正确叫hidden world state正确。only仍focus；协议可改变注意/文本分布，fair-vs-unknown不能直接证明内部算法。scope instruction明确use新event信息，unknown时不借oldrole填结果，R8仍全报。无额外模型/训练/representation probe。
- **决策表（跑之前写）：** fairness抑制反向、selected正向控制有效 → 语义约束可重新调节角色aftereffect，ordinary discourse prediction竞争增强，不能卖普遍falsebelief residue。fair仍反向但native知道1/2、unknown答未知 → continuation role-effect独立于world概率表达，需解释事件/动作结构而非卖generic gap。unknown擅选且受oldrole方向影响、selected/fair控制有效 → 有具体selection grounding干扰，追why和R8；若回答不受oldrole、只默认某候选 → entity/order猜测，不能称role迁移。selected不能约束/审核不清 → 先追材料/目标归属，不盲扩sweep。所有结果保留，同I01推进，不停止/换线/论文写作。
- **算力预算：** raw单卡、native两卡独立，预计≤.20 GPU·h；**实际：** 待填。
- **命令：** `selection_transfer.py build/adopt`、`event_identity_infer.py --experiment E38`、`time_indexed_role.py run --experiment E38 --query current/fair`。完整选择fields-v1/v2/v3及raw留本地cache，hash持续记录。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）

跑前instruction核对：R8 exact sentence为`Report an unreported selection outcome as unspecified, while answering chance questions from the stated probabilities for the new selection.` chance与未公布outcome显式区分，避免scope恢复把fair概率题也误答unknown；尚未推理，未改数据/gold。
