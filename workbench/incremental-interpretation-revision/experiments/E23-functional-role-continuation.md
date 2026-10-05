# E23：角色事实是否约束实际续写，以及一句指令能否恢复（2026-10-05）

- **状态：** PLANNED
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
- **算力预算：** 单空闲H20，224 greedy×最多48新token≤.2 GPU·h；**实际：** 待运行。
- **命令：** source scripts/env.sh；functional_continuation.py build/adopt/run --data $IIR_CACHE/E23-material-preparation-v1/audited-v1.jsonl --out $IIR_CACHE/runs/E23；生成之后逐条独立annotation、按预注册schema分析。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）

待运行。未注册新的能力/机制主张；I01 PILOT。
