# E22：纠正后的实体可及性与活动关系利用（2026-10-05）

- **状态：** DONE
- **类型：** PILOT
- **对应：** I01/P10；E21 named差主要cue下降，追why而非按差距叫修复。
- **问题（一句话）：** 同样的点名否定对比泛指排除，对own患者的增强是一般实体提及效应，还是原活动续写中特别强的关系利用？
- **设置：** E20 named/E21 generic的7源×2NP×GP/comma×2role facts×2NP targets=224新neutral输入。源S1/已独立审计role facts/same-continued桥逐字保留；S2变为原actor later noticed own/other author NP for a moment。2独立Luna审查128/96；224 eligible/112 acceptable（GP全marginal因原句garden-path，保留；acceptable-only GP/cue对比为空）、224neutral-role-clear。source NP指可提前提及的own，other是作者提供的替代实体，不保证在上下文已引入。prior-faithful flags源自E20/21，不重判已有only facts；shared完整严格4源。固定Qwen3-8B pinned/FP32/SDPA、seed0/batch4/TF32false，无问题或instruction。
- **读数：** M=bits(other NP)−bits(own NP)，D=M_GP−M_cue。对每role fact、GP/cue分别报告named−generic的M变化；主reference-only的关系续写变化减neutral变化。额外报告两frame的history style interaction，区分差值由GP或cue驱动。旧relation分数E20/21冻结复用。all/eligible/acceptable/neutral-role-clear/prior-faithful交集，NPoption0/1/both；先source内两NP平均，再source paired bootstrap10000/seed20261005/95%CI，不按结果挑source。
- **阳性对照：** E21双向role事实明显改变原关系偏好；新noticed审核不需要对象担任原活动患者。2NP targets pre-token相同，HF/manual NLL核对。build独立审计candidate224所有metadata与text逐字再现，原S1/证据/桥不改变。
- **噪声地板 + MIE：** FP32漂移约1e−5bits；主要不确定性来自7/严格4source，报告paired CI与每source，无硬效果gate。绝对跨frame总NLL不能直接作准确率；只比较固定替代对象的匹配对比。
- **混杂审计：** neutral更换谓词/句长/语义，不能隔离单个神经机制；named−generic在各frame内部保持上下文/目标，frame interaction用于区分纯实体提及解释。new-referent foil和selection单独保留。generic role含审核coverage不确定，严格层及全体同步，不看score修标签。grammaracceptable与GP条件耦合导致该层D缺失，明确报告不补造结果。
- **决策表（跑之前写）：** named−generic对neutral和relation近似相同 → 额外提及/实体可及性仍足以解释，不卖关系污染；relation变化强于neutral → 活动依赖的检索/关联解释增加但需实际角色违规；只GP/cue一边变化 → 明确是哪边，不能把较小D叫修复。CI宽/不同source反向 → 保留不确定和全source；下一functional续写+一句恢复检验，随后独立现成source预测，结束7句措辞局部诊断。
- **算力预算：** 单空闲H20 224新输入≤.03 GPU·h；**实际：** 14.985s / 0.00416260 GPU·h。
- **命令：** source scripts/env.sh；post_correction_entity.py build/adopt；event_identity_infer.py --experiment E22 --data $IIR_CACHE/E22-material-preparation-v1/audited-v1.jsonl --out $IIR_CACHE/runs/E22；post_correction_entity.py analyze --cache $IIR_CACHE --new $IIR_CACHE/runs/E22 --out results/E22-summary.json。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）

224全部评分，HF/manual差6.54e−8 nats。严格4源reference-only named−generic：neutral患者偏好GP+1.551 [.513,2.288] / cue+2.041 [.513,3.570]bits；原活动关系GP−1.241 [−3.156,.127] / cue+1.867 [−.186,3.355]。关系−neutral的变化GP−2.792 [−3.680,−1.904]，cue−.174 [−1.124,1.201]；history交互−2.618 [−3.314,−1.770]。全7同向（GP−2.718 [−3.429,−2.056]、cue+.507 [−.677,2.025]）。

解释：cue中named对原患者的增强大致跟neutral实体提及一起变化；GP中named提高neutral可及性，却相对抑制原活动患者关联。因此不能把E21的cue下降称角色错误污染，也不能用纯实体salience解释GP全部响应。它与语义排除有效、但mentioned entity仍显眼的混合解释相容；尚无内部机制或实际角色错误证明。

[统计](../results/E22-summary.json)、[每source](../results/E22-per-source.csv)、[配置](../results/E22-config.json)、[审计](../results/D0-E22-material-audit.json)。acceptable-only全部GP缺失，D为null而不是伪造通过；主eligible/外部faithful matched层保留GP。按决策表下一实际free continuation+一句恢复控制，随后独立材料预测，不继续7句措辞循环。C04登记为L1局部measurement，I01仍PILOT。
