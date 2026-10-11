# E23：角色事实是否约束实际续写，以及一句指令能否恢复（2026-10-05）

- **状态：** DONE
- **类型：** PILOT
- **对应：** I01/C04/P10；E21/E22的probability响应尚不能证明实际角色错误。
- **问题（一句话）：** 已有明确排他活动事实后，模型实际续写是否违背参与者约束，GP历史/纠正措辞如何改变错误，一句提醒能否恢复？
- **设置：** 既有E20 named/E21 generic，7 source×2NP×GP/comma×2role事实×base/one_instruction=224续写/112唯一叙事prefix。只截断既有独立审核S2在患者目标前，不造新句子；独立Luna两批64/48核对前缀与事件范围。base直接raw continuation，恢复仅前置一句Complete the final sentence while following the explicitly stated participant restrictions for that same activity，均无chat/fewshot。固定本地pinned Qwen3-8B，frozen FP32/SDPA/TF32false、seed0、greedy do_samplefalse、batch8、max_new_tokens48、EOS停止。所有source/NP/条件评分，无按likelihood选择输入/seed。
- **读数：** 预先独立裁定最先实现原活动的completion为consistent/contradiction/uncertain/no_activity；比较与同一活动only角色约束，不把新事件/比喻/body-part等模糊指称武断判错。所有224输出按盲化ID逐条外审，judge只看叙事prefix+completion，无分数/condition/mode/研究结论。主observed contradiction/全部输出（unknown不计确定错误，也不算正确）；同时报告4类分布、审计clear比例、possible违反上界=(contradiction+uncertain+no_activity)/总数、明确可判子集错误率作辅助。token-cap/EOS率报告，不把48token cap全部判失败。每source先平均再paired bootstrap10000/seed20261005。
- **切片：** 全7、eligible、prior-fact∩prefix-clear共同完整cohort（不根据生成选择）；NP0原作者较合理目标作事前functional主层，NP1和both同步；reference_only与initial_patient_only分开。主GP−cue violation差、named−generic差与base→一句恢复变化，每source/全部cell全报告，保留CI宽与零差结果。
- **阳性对照：** 既有E20/E21双向事实使target偏好明确移动；此处需检验generated活动对象是否随事实改变，允许结果不适用。input base BPE用完整原句在目标前截断，保持与前面likelihood因果前缀一致，不把dangling whitespace另编码。外审报告only作用范围/同活动性，范围不清事前分层。
- **噪声地板 + MIE：** greedy无采样方差，source7/严格4的配对CI及语义审计uncertainty主导；R8指令控制必报，修复不自动证明潜在能力。无效果大小硬gate。
- **混杂审计：** instructional raw prefix有额外任务/长度，不能据恢复说哪个内部机制；base首个活动续写直接功能读数，后续新事件不追罚。other场景、body-parts/association等自然生成难以精确判，unknown保留。greedy只是一次协议，若近乎无明确错误，不因看结果再采样找失败；转独立来源预测现有measurement，不能卖失败能力故事。原材料版权文本/rollouts仅cache，git只有hash/stat/code/card。
- **决策表（跑之前写）：** GP明确违反率稳定更高且一句无法恢复 → history影响实际关系使用支持增加，必须独立source预测；指令能恢复 → 默认续写策略/任务竞争增强，不卖一般revision无能；named只有实体mention增加且事实违反不增加 → 不支持correction害修复；事实控制无反应/unknown主导 → 限定续写仪器，报告问题，不扩大模型/prompt/sampling sweep。只有概率差且无实际违反 → 不包装成失效故事；进入独立材料的解释预测。
- **算力预算：** 单空闲H20，224 greedy×最多48新token≤.2 GPU·h；**实际：** 58.328s / .01620213 GPU·h。
- **命令：** source scripts/env.sh；functional_continuation.py build/adopt/run --data $IIR_CACHE/E23-material-preparation-v1/audited-v1.jsonl --out $IIR_CACHE/runs/E23；生成之后逐条独立annotation、按预注册schema分析。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）

224 greedy输出全部独立审核：首批130consistent/10contradiction/84uncertain；完整独立第二次审核130/6/88。224均达到48token cap，但首活动句很多已完整，不能cap=失败。两组标签均保留；第二次审核是**POST-HOC semantic calibration**，触发原因是NP后有限谓语/肯定后又明确否定，首NP不能直接判patient。无parent选择gold或悄改主读数。

原NP0/ref-only全7源首审named/generic base GP−cue确定违反差都是+28.57 [0,57.14]pp；次审named0、generic+14.29 [0,42.86]，不足以声称稳定能力损失。原事前共同clear4源NP0 base所有style/GP/cue两review都没有明确违反，但很多cue输出省略患者；这不证明零失败。第二审named base GP不确定4/7、cue6/7，generic GP4/7、cue6/7，可能违反上界/clear比例已同步报告。恢复控制未建立稳定减少错误，严格层的首审2条新增违反在次审变为再次GP/残缺句不确定；不将原raw instruction默认策略当一般能力判断。

[首次审核统计](../results/E23-first-review-summary.json)、[独立次审同读数](../results/E23-summary.json)、[审核差异](../results/E23-audit-comparison.json)、[配置](../results/E23-config.json)、[每source](https://github.com/Nhckdvrl/ssn-group-papaer/blob/859e48c87cfbecaf017c0fd8e286ef18f59a61cd/workbench/incremental-interpretation-revision/results/E23-per-source.csv)。按决策表限定functional仪器：自由续写会省略患者、复制残缺GP或自我否定，不能直接给probability finding加false-belief标签。接独立现成Ceháková2025 source预测E24，保持I01 PILOT，C04仍L1 local measurement，未升级实际错误/机制主张。
