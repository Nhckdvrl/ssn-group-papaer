# E12：公开同家族三阶段Hu原任务测量（2026-10-03）

- **状态：** DONE
- **类型：** REPRO / D2 frozen stage measurement
- **对应：** C02、P02；human norm仪器已通过，先追踪原任务行为，不预设criterion。
- **问题（一句话）：** 同一公开Base→SFT→DPO谱系在Hu自然材料上的gold/human分布与option-order敏感性如何变化？
- **设置：** allenai/OLMoE-1B-7B-0125，Base SHA9b0c1aa87e34a20052389dce1f0cf01da783f654；SFT6f7a5b02aa069fdcb8d0cb6b837b9905a3d995d7；DPO0f2e2e1bd78f146685c346ac0f797ae146ffa8f9。官方model tree与ALTPRAG model_config均核对，DPO不是最终RLVR Instruct。n1365=169×5+104no-story×5；所有stage同一bare Hu原任务字串、add_special_tokens=False、无chat/no CoT，FP32、TF32关闭、batch8；不做任何训练。SFT仅发布PyTorch .bin，torch2.7 weights-only加载；其他safetensors，index核对后才跑。
- **读数：** 原numeric choice probability/argmax，human norm对齐、option-order差与gold endorsement；每phenomenon分别报告item-cluster CI，三stage不是三independent training seed。记录原prompt/data/token IDs SHA、model revision与所有选项单token断言。
- **阳性对照：** Hu原Flan1,365选择匹配；E11重建63,206条对应人类Correct码零错误。每stage固定首末项batch1/8概率差阈值1e-3，失败停止该stage分析；三tokenizer每条原prompt token-ID hash相同才称matched lexical input，否则先审混杂，不忽略版本差。
- **噪声地板 + MIE：** deterministic raw下一token；按item bootstrap2000draw seed0；无training replicate，不能给普适RLHF因果CI。无预设方向/能力MIE。
- **混杂审计：** 不将原prob MCQ冒称direct language knowledge；bare prompt对post-trained模型可能失配，后续matched elicitation control是解释前提；no-story不是unlicensed，不能计算FPR/d-prime。词表/原weight dtype（Base官方F32、DPO BF16）与precision纪录；只比较该checkpoint谱系，不能独立归因algorithm/data。
- **决策表（跑之前写）：** A gold/human均提高 → 描述task表现，不能推出discrimination；B gold提高但human/option-order不一致 → 优先边界与elicitation/人类歧义核对；C不单调 → 保留全部stage，审protocol后记录boundary，不救故事；Dnumerical/tokenizer不通过 → 技术失败/混杂，隔离结果。任何结果都不保住criterion hypothesis。
- **算力预算：** 下载约56GB外置；GPU5/6/7三stage独立、FP32每卡≤90GB、总≤1GPU·时；先下载再校验，不跨GPU训练/张量并行。

## 结果
跑前冻结。当前三stage准备；用户授权frozen独立多卡，仍PROPOSED，不改变ACTIVE。

完成范围校对：Base/SFT裸入口在E12，DPO同源裸入口补齐于E27；actual输入SHA一致，原旧chat不据此归因。结果E27-token-matched-stage-summary.json。
