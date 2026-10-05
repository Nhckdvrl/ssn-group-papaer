# E24：独立来源检验纠正后关系利用的history交互（2026-10-05）

- **状态：** PLANNED
- **类型：** PILOT
- **对应：** I01/C04/P10；结束Slattery7句措辞诊断，用独立source检验已观察结构的预测。
- **问题（一句话）：** 在Ceháková/Chromý2025原24 NPZ句中，具名否定相对泛指排除的activity-minus-neutral患者偏好，是否仍在GP历史后更受抑制？
- **设置：** 上游Zenodo16358492原NPZ24source/12同动词family，原GP/comma S1逐字保留，不改写S1/加sourceNP选项。24×2GP/cue×2role事实×2named/generic×(3activity targets+2neutral targets)=960输入。actor/ref/core NP/verb独立Luna抽字段v1/v2/v3；v1aux重复风险、fullNP与core混淆、singular themselves及item75 Q-the/source-their边界均在任何推理前修正，保留旧字段。only role facts为新增语义约束，原intransitive/Q不当源asserted fact。原actor continued that particular activity，随后In that same activity, actor was/were V-ing ref/own/other NP for a moment；neutral actor later noticed own/other NP for a moment。other NP取另一同动词published item的core，可能新引入，保留外审flag，不构造新词汇。两独立批480全文variant审计在模型之前完成；all输入评分。
- **读数：** M=bits(other NP)−bits(own NP)；具名−泛指M变化分别在activity/neutral、GP/cue与两个role facts报告。主reference-only的history role-specific change=[named−generic GP−cue]_activity−同值_neutral，预期E22严格4源−2.618 [−3.314,−1.770]方向在新source保留。另R=bits(own NP)−bits(ref)仅activity，双向role-effect报告。每原source先配对，两个同动词source在family内平均，再12family paired bootstrap10000/seed20261005/95%CI；不能把960变体或24同词来源当独立N。all/eligible/acceptable/facts-clear∩frame-role-clear，每层要求同family两source的所有条件完整共同交集，不按model score选cohort。
- **阳性对照：** 同活动事实reference-only对比initial-patient-only明显改变R，所有GP/cue/style报告，不以任何一cell好看叫工具通过。named reference-only coreNP均2词（possessive保留）与generic anyone else2词，肯定对象最后；initial-only self1/reciprocal2与generic2长度记录，不把它当pure mention。target span/pre-token身份与HF/manual loss校对。原384upstream QA共享schema，rawcorrect0/1由原PC Ibex as yes,no+hasCorrect脚本确认；published gold不是语义逻辑证书。
- **噪声地板 + MIE：** FP32约1e−5bits；12family/sample variation主要噪声。无固定effect gate；报告CI/逐family/role control，不用E22效应大小强迫复制幅度。
- **混杂审计：** 新activity readout是更明确的同活动progressive，而不是Slattery原S2，所以是事前预测transfer，不声称原样replication；参与者替代NP来自同verb另一source，只是foil且未在当前S1提及。任何跨frame句长/选择常识差别保留，在frame内先取matched named/generic后作interaction；R绝对长度不同非准确率。generic anyone else可能不覆盖puppy，严格审核排除并全体保留；collective couple/family数一致性逐条审。语义无gold，teacher flags不是人类真值。
- **决策表（跑之前写）：** primary负且双向role control有效、多个family一致 → C04跨source结构支持增强，继续找能区分语义角色排除与source replay的使用场景，不仅报告GP；无交互而两frame同named增强 → E22局部predicate/source interaction，限制一般叙事；方向反转 → 保留全部source，拆GP/cue/两个frame寻找原因，不追加同措辞sweep；control弱或teacher uncertain主导 → 限定readout，不以多模型找阳性。E23不足证明能力错误，任何E24概率正结果不追认它通过。
- **算力预算：** 单空闲H20，960新输入≤.06 GPU·h，frozen pinned本地Qwen3-8B/FP32/SDPA/batch4/seed0/TF32false，无chat/question/instruction；**实际：** 待运行。
- **命令：** source scripts/env.sh；correction_transfer.py build/adopt；event_identity_infer.py --experiment E24 --data $IIR_CACHE/E24-material-preparation-v1/audited-v1.jsonl --out $IIR_CACHE/runs/E24；correction_transfer.py analyze --run $IIR_CACHE/runs/E24 --out results/E24-summary.json。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）

待运行。C04 L1，I01 PILOT；没有PROMISING或已确立novel paper叙事。
