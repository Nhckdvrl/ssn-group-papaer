# E41：对象占用／状态后果，还是跨事件关系反重复？（2026-10-06）

- **状态：** PLANNED
- **类型：** PILOT
- **对应：** C05 / I01 / P11；E39具名、E40无only仍反向后的下一具体解释区分。
- **问题（一句话）：** 明确旧活动结束、两个对象重新满足新活动条件后，旧患者的新事件反向预测是否消失？
- **设置：** E40全部原new-event rows（非穷尽肯定first/last、同/异actor×同/异predicate、two role worlds、activity/neutral、原source/donor target），不新增/筛source。新activity bridge后、target-bearing句前加入三种独立Luna构造长度匹配说明：status_unknown（旧活动结束时间和双方新活动条件未报告）、ended_only（旧活动在新活动前结束，但双方条件未报告）、ended_and_ready（结束且双方都重新满足新活动全部条件、此前参与不会妨碍再次参与）。所有三个protocol明确同一两名候选、无选择结果/概率、不给谁必须成为下一患者。三组词数尽量匹配±3、相同候选提及与新旧活动词次数；语义强干预与人工感独立审核，不能称自然故事原句。raw1536×3=4608，三policy GPU2/3/6独立并行，完整data先审。parent E40全体固定对照。
- **读数：** M=bits(B)−bits(A)，D=stated A−stated B，J=activity−neutral。主otherActor/sameV ready−ended、ended−unknown，两fact orders单报+平均；保留全部actors/predicates/order及different−same，禁止挑order/动词。n12先两source平均paired bootstrap10000 seed20261005 95CI，all/eligible/grammar共同parent交集及E31固定11/9/9。old control复用E40 frozen old positive，native只primary otherActor/sameV 288contexts×old reported-role +new availability问句×base/scope=1152responses，分别读事实可访问和明确ready/unknown，不给newwho错误gold。
- **阳性对照：** native能够读出ended_and_ready双方可参与、其他条件未报告readiness；旧明确reported角色仍能访问。E40 old J+4.736/+6.313两CI正。没有实际selected target，raw差不能叫accuracy/world chance。
- **噪声地板 + MIE：** 同FP32 frozen种子、单卡batch4/8，三policy并行是计算排程，不是增加独立N。长协议可能推开信息、注入普通salience/attention；unknown/ended/ready长度/两NP mentions和词义位置匹配，neutral相同。CIs为观察，不作gate。
- **混杂审计：** ended只解除时间overlap，不保证healing/dressing等结果状态被重置；ready明确恢复新活动所需条件但不许抹去旧活动曾发生。审计须逐场景核语义与自然度，ready不能只是愿意、也不只是泛泛free，不能暗示source或donor已被选中。若必要物理reset人工强，公开承认作为account诊断；自然资产CSK21已下载审计，用于下游语义压力但不冒充它已测role修订，也不把已有state-QA/prediction gap当novelty。R8一条，固定三policy，不扩模型/训练/probe。
- **决策表（跑之前写）：** ended消除反向 → 时间重叠/对象占用解释得到支持；ended仍负、ready消除 → 结果状态/可参与性解释强；明确ready仍负且native读对 → 占用/必要状态不足，继续检验关系反重复与内容修订而非称worldbelief错误；新V与同V都同样被协议重置 → 通用salience/attention调节，不能只称action-semantic解除；ready未被正确理解/语义含糊 → 先追材料与读数why、保留所有结果，不盲扩大sweep。I01继续，不自行改ACTIVE/进入论文阶段。
- **算力预算：** 三raw独立GPU2/3/6，native GPU7，已有venv/Qwen3-8B FP32，预计≤.25GPU·h；**实际：** 待填。
- **命令：** availability_roles.py build/adopt + event_identity_infer.py E41 + time_indexed_role.py E41 current/availability；raw perpolicy分片无跨GPU集群，全部cache留hash。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）

跑前R8固定单句：`Answer readiness questions from the new activity description, treating unreported conditions as unspecified; for earlier participant questions, use the explicitly reported earlier activity.` 三独立Luna全5184packet审计、候选/协议范围/hash覆盖；ready描述全部starting conditions，不只是willing。D0记录全部grammar/uncertain，尚未推理。4608causal contexts已核。

跑前记录勘误：上一提交提前写“4608已核”且D0输出因adapter失败为空；推理未开始。审计2把raw/question字段嵌套，adapter展平字段位置，原review字节/所有语义标签不变，重新adopt完成全量gold/hash/causal预检后才允许推理。本次上述预检真实完成，原失败没有被当作语义通过。
