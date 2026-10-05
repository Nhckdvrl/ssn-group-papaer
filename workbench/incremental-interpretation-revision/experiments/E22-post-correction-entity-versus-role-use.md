# E22：纠正后的实体可及性与活动关系利用（2026-10-05）

- **状态：** PLANNED
- **类型：** PILOT
- **对应：** I01/P10；E21 named差主要cue下降，追why而非按差距叫修复。
- **问题（一句话）：** 同样的点名否定对比泛指排除，对own患者的增强是一般实体提及效应，还是原活动续写中特别强的关系利用？
- **设置：** E20 named/E21 generic的7源×2NP×GP/comma×2role facts×2NP targets=224新neutral输入。源S1/已独立审计role facts/same-continued桥逐字保留；S2变为原actor later noticed own/other author NP for a moment。2独立Luna审查128/96；224 eligible/112 acceptable（GP全marginal因原句garden-path，保留；acceptable-only GP/cue对比为空）、224neutral-role-clear。source NP指可提前提及的own，other是作者提供的替代实体，不保证在上下文已引入。prior-faithful flags源自E20/21，不重判已有only facts；shared完整严格4源。固定Qwen3-8B pinned/FP32/SDPA、seed0/batch4/TF32false，无问题或instruction。
- **读数：** M=bits(other NP)−bits(own NP)，D=M_GP−M_cue。对每role fact、GP/cue分别报告named−generic的M变化；主reference-only的关系续写变化减neutral变化。额外报告两frame的history style interaction，区分差值由GP或cue驱动。旧relation分数E20/21冻结复用。all/eligible/acceptable/neutral-role-clear/prior-faithful交集，NPoption0/1/both；先source内两NP平均，再source paired bootstrap10000/seed20261005/95%CI，不按结果挑source。
- **阳性对照：** E21双向role事实明显改变原关系偏好；新noticed审核不需要对象担任原活动患者。2NP targets pre-token相同，HF/manual NLL核对。build独立审计candidate224所有metadata与text逐字再现，原S1/证据/桥不改变。
- **噪声地板 + MIE：** FP32漂移约1e−5bits；主要不确定性来自7/严格4source，报告paired CI与每source，无硬效果gate。绝对跨frame总NLL不能直接作准确率；只比较固定替代对象的匹配对比。
- **混杂审计：** neutral更换谓词/句长/语义，不能隔离单个神经机制；named−generic在各frame内部保持上下文/目标，frame interaction用于区分纯实体提及解释。new-referent foil和selection单独保留。generic role含审核coverage不确定，严格层及全体同步，不看score修标签。grammaracceptable与GP条件耦合导致该层D缺失，明确报告不补造结果。
- **决策表（跑之前写）：** named−generic对neutral和relation近似相同 → 额外提及/实体可及性仍足以解释，不卖关系污染；relation变化强于neutral → 活动依赖的检索/关联解释增加但需实际角色违规；只GP/cue一边变化 → 明确是哪边，不能把较小D叫修复。CI宽/不同source反向 → 保留不确定和全source；下一functional续写+一句恢复检验，随后独立现成source预测，结束7句措辞局部诊断。
- **算力预算：** 单空闲H20 224新输入≤.03 GPU·h；**实际：** 待运行。
- **命令：** source scripts/env.sh；post_correction_entity.py build/adopt；event_identity_infer.py --experiment E22 --data $IIR_CACHE/E22-material-preparation-v1/audited-v1.jsonl --out $IIR_CACHE/runs/E22；post_correction_entity.py analyze --cache $IIR_CACHE --new $IIR_CACHE/runs/E22 --out results/E22-summary.json。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）

待运行。I01 PILOT；不从概率差宣布能力错误。
