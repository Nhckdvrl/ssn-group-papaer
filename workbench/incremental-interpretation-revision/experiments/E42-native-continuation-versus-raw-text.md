# E42：角色反向作用能否进入原生续写？（2026-10-06）

- **状态：** DONE
- **类型：** PILOT
- **对应：** C05 / I01 / P11；raw-text使用post-trained模型可能是协议伪影，不能只用正确QA给raw做能力背书。
- **问题（一句话）：** E40无only的旧正／新反向，是否也出现在模型原生chat条件续写、并经一句事件范围指令保持？
- **设置：** 原E40全部1920独立审计完整inputs/NP targets，不造新故事、不改NP，不选cell。把target-bearing末句之前的完整context放native user，system给“Continue the narrative with one sentence.”；目标句作为assistant continuation teacher-force，在目标NP段计算条件full-vocab NLL。assistant已知前缀仍是原target-bearing句，不把未生成前缀计为actual generation/accuracy。scope mode只追加一句“For each activity, keep its stated participant description scoped to that activity.” 两mode共3840，原raw E40固定参照。截断位置用authored_followup_start_word和原字符索引，native causal pretarget token pairs及specialtokens验证，固定nochathinking/FP32。
- **读数：** M=bits(B)−bits(A)，D=stated A−stated B，J=activity−neutral。主两个plain fact orders otherActor/sameV J，raw→native与scope−base paired，old阳性、两个actor×同/异V全部报。n12family两source平均bootstrap10000 seed20261005；all/eligible/共同grammar9及E31冻结11/9/9。full native old/同V/differentV表、prefix分段/目标完整性/hash全报告。
- **阳性对照：** native旧活动仍提高明确reported患者偏好；人工/模型loss首batch校验，两个target有相同原生causal pretarget tokens。原only/plain语义审计沿用，不加newwho错误gold。
- **噪声地板 + MIE：** FP32 seed0 batch4；raw与native是不同任务分布、system会改变风格，比较不证明hiddenstate。所有来源/分项固定，不选模式。
- **混杂审计：** assistant条件前缀为teacher-forced原文，不能叫自由生成违反事实；原生chat排除非chat输入作为效果必要条件，只在条件续写里讨论作用方向。R8只限定明示role描述范围，不替新event挑患者或要求P=1/2，任意强迫均衡指令不采用。完整故事原文已Luna独立审；两条system指令另作独立语义核对。
- **决策表（跑之前写）：** native old控制有效、两个order新other反向 → raw格式不是现象必要条件，保持event/action边界候选；native消失/变向且old有效 → 协议分布是核心边界，收窄C05而非换模型找方向；scope可恢复old/new方向 → 指令调节论据，不宣称隐藏belief错误；old控制失效或target前缀不同 → 优先why技术/材料，不扩大sweep。所有原实验保留，同I01继续。
- **算力预算：** base/scope GPU0/1独立，现有venv、同本地Qwen3-8B FP32，预计≤.15GPU·h；**实际：** 待填。
- **命令：** native_role_continuation.py prepare/run/analyze，原E40 audited-v2数据完全冻结。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）

[完整统计](../results/E42-summary.json)：native base old activity D两order+32.973 [27.923,38.078]/+21.043 [12.067,29.420]；newother同V activity D−69.382 [−75.343,−63.011]/−65.768 [−73.198,−57.783]bits。matched-neutral J−52.820 [−58.657,−46.868]/−48.213 [−54.294,−42.683]；scope mode仍−50.360/−41.637。方向进入原生条件续写，一句scope不能消除。native也有极强neutral作用（old D−33.210/−51.606），因此不只报J或把大数叫机制更强；target loss0–64bits、manual/HF首batch误差<1e−6，两alt native pretarget tokens全一致，分段/target原字节沿用，已追查没有数值/装配异常。幅度依任务分布、saturation/teacher-forced prefix，不直接对应world probability、hidden beliefs或自由生成错误。actual run7f4b2641，两mode合计3840，全部order/actor/predicate/grammar层保留。
