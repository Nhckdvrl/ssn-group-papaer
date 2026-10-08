# E19：明确活动内角色证据能否覆盖旧关联？（2026-10-05）

- **状态：** DONE
- **类型：** PILOT
- **对应：** I01 / P10；E18迁移之后，区分弱句法cue未覆盖与强语义证据后的history dependence。
- **问题（一句话）：** 明确该次活动对象只有self/each-other（或只有原NP）之后，GP历史是否仍影响同一活动的角色续写？其作用是否扩散到另一活动？
- **设置：** 原独立episodic7源、2作者NP选项、GP/comma、2late-role证据、continued-same/continued-separate、3目标(ref/own-NP/other-NP)=336新输入；同pinned frozen Qwen3-8B FP32/SDPA、seed0/batch4、TF32=false，无chat/question/instruction。复用E14–16无late-evidence的对应168输入概率，非物理重复。报告all/eligible/acceptable/clear-episode-readout/clear-role-evidence、option0/1/both、每source。
- **材料：** S1不改；插入独立Luna构造的“In that [原activity noun], [actor] was/were [原activity] only X, not Y.”叙事句，再接原same/separate桥和原作者S2，目标仅三种替代。两方向语词基本相同、scope只限制原episode，不全局否定未来活动。它们是实验提供的信息，不宣称initial_only是作者gold。fields-v1含finished→continued的时间风险，在任何推理前改v2统一进行时，旧版保留。另两Luna分别192/144逐项审核grammar/排他性/证据句scope与S2 target scope/时间兼容，两种scope分别保存；运行前发现字段误读，保留v1并独立复查v2，clear-role层要求证据scope=original且目标scope符合桥；uncertain如dating双主体必须保留。原文/衍生句cache-only，结果hash/stat入git。
- **读数：** R=bits(own NP)−bits(author ref)，M=bits(other NP)−bits(own NP)。每role证据×桥报告GP/cue cells、D=GP−comma、相对无late-evidence的D变化、同/另一桥D交互，双向role-evidence对R/M的影响。两个NP先source内平均、paired bootstrap10000/seed20261005、95%CI。GP/cue中late句完全相同，固定词频/新近提及；不把separate的任意NP偏好标为accuracy，因为未指定新活动对象。
- **阳性对照：** reference-only与initial-NP-only应能反向改变同episode的ref/own偏好，分别在GP/cue报告。若连明确角色句都不能使读数响应，结果只说明instrument/语言条件有限，不归为不可修订记忆。三targets causal pre-context token一致、HF/manual loss对齐；旧config与权重锁定。
- **噪声地板 + MIE：** FP32词级漂移≈1e−5bits，n7或clear层更小，sampling CI完整报告。没有任意大小gate；大小、符号、scope及逐项共同更新解释。
- **混杂审计：** only/not句同时带重复谓词、reference及NP，主效应受recent lexical context影响；same/new与GP/cue配对共享这些文字，不能由role主效应推出内部机制。source NP选项plausibility差异保留。后文target与给定事实矛盾的变体刻意评分，不是语法自动排除；排他性/时间问题由独立审查事前标记。若明确correct-role句覆盖GP旧偏好，只说明当前强证据可覆盖，不能反推旧弱cue已成功修订；若残余仅separate，先检查新活动未约束而非说错。
- **决策表（跑之前写）：** 同episode的双向role控制有效且GP差显著缩小 → 旧测量主要是弱消歧/关联沿用，不能讲已修订后再激活；若scope两桥响应不同 → 追event-local覆盖/溢出，并需把另一事件真值明确指定才谈正确性；强cue控制有效但同episode仍稳定GP残差 → history在显式排他信息后仍影响续写，接独立原始资产/正反信息顺序控制，尚不称内部state；control弱/annotation不清楚/CI宽 → 查精确语言与读数，不扩大模型或prompt sweep。没有自动关闭/novelty gate。
- **算力预算：** 单空闲H20，336新输入，预计≤.03 GPU·h。**实际：** 20.057s / 0.00557143 GPU·h；336新输入。
- **命令：** workbench内source `scripts/env.sh`；`scripts/late_role_evidence.py build/adopt`；`$IIR_PYTHON scripts/event_identity_infer.py --experiment E19 --data $IIR_CACHE/E19-material-preparation-v1/audited-v2.jsonl --out $IIR_CACHE/runs/E19`；分析 `scripts/late_role_evidence.py analyze --cache $IIR_CACHE --new $IIR_CACHE/runs/E19 --out results/E19-summary.json`。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）

- 336/336acceptable；264clear-role/target scope。原7源same均clear，但hide/embrace/date三源的separate桥后S2可回指原活动，独立审为uncertain；严格scope对比只有4源。全部7结果与标注分项保留。
- 同活动7源：reference-only versus initial-only的R变化，GP +8.511 [5.146,12.319]bits，cue +10.598 [7.752,13.551]，阳性对照可用。reference-only后GP R+.229，cue+5.745；initial-only后GP−8.283，cue−4.853。绝对R不是准确率。
- 相同明确reference-only句后，GP−cue R仍−5.516 [−8.056,−3.290]bits、M+4.321 [2.555,6.683]；无late句时R−11.244 [−13.889,−8.804]。强角色信息显著改变偏好但没消除history。
- 明确范围4源：reference-only后的same−separate history交互−.018 [−.502,.690]，原−2.603 [−3.040,−2.237]；并非严格scope覆盖已证明，且separate活动对象没有正误gold。
- [统计](../results/E19-summary.json)、[config](../results/E19-config.json)、[分数](https://github.com/Nhckdvrl/ssn-group-papaer/blob/859e48c87cfbecaf017c0fd8e286ef18f59a61cd/workbench/incremental-interpretation-revision/results/E19-scores.csv)，执行git `5db67bcd8`。
- Metadata勘误：generic adopter将report source_items硬编码22，实际7；原cache audit report/hash与model config不改，corrected audit旁存，见[D0勘误](../results/D0-E19-audit-erratum.json)。模型按实际rows统计7，所有文本/teacher flags/推理保持不变。helper已修，不能把错误统计静默改掉。
- 按强cue有效且残余分支：追why。当前only-X/not-Y把被否定Y放最近，下一E20固定同activity、交换否定/肯定对象出现顺序，以分开nearest mention echo与仍沿用旧relation。不称成功恢复后再激活、不把scope不确定句判能力失败。I01仍PILOT、C01/C02仍L0。
