# E07：Qwen3跨语言原生/格式与Hu读数（2026-10-02）

- **状态：** DONE
- **类型：** REPRO / instrument validation
- **对应：** C01、P03、P04。
- **问题（一句话）：** E02/E06原生与format读数差异是否在另一个现代checkpoint复现，Hu原生概率与生成之间哪些差异仅属elicitation？
- **解释：** A原生输出绑定造成loss；B选择本身对format敏感；C现代3B读数只对该checkpoint。此处模型版本/参数/训练均不同，不能归为SFT、scale或RLHF因果。
- **设置：** Qwen3-4B revision1cfa9a7208912126459214e8b04321603b3df60c，native Multi四语言各300×seeds0/1/2，T=.5/top_p1/top_k0、max1024、batch32；显式enable_thinking=False现代reference。随后同题format-only要求，max1024与native相同，控制E06不同预算混杂，是否运行先审native无异常故障。Hu原169×5和104×5no-story raw continuation，保持parent numeric logprob，无chat包装。
- **读数：** 全部解析率/截断率，maxim240/literal60分开accuracy与item-cluster CI；Hu七phenomena/no-story概率和choice_order稳定性。Qwen3是现代补充，不是Multi2024原模型。
- **阳性对照：** 原Flan Hu公开1,365选择匹配；Multi oracle1200与parser adversarial通过；Qwen3模板关闭thinking且完整序列严格prefix核对。
- **噪声地板 + MIE：** 三次固定采样全保留，按item聚合，不挑seed；先报告原生/format paired读数，再考虑类别边界；无能力MIE。
- **混杂审计：** tokenizer/chat模板/version冻结、输出原文/scorer SHA；无可靠许可标签，不计算SDT；no-story不是literal counterfactual，错误不是自动false alarm。
- **决策表（跑之前写）：** A解析损失被指令消除 → readout confound；B选择变化 → 同题概率与option likelihood核对；C两个checkpoint结构不一致 → 明确boundary，不能扩大claim。任意漂亮effect先审技术差异。
- **算力预算：** GPU0–3四语言独立、GPU5 Hu；≤1 GPU·时，全8卡授权；实际待记录。

## 结果
子agent模型请求网络重连，无实际运行；root接管执行。本卡在运行前落盘。

### 中断记录
上一轮进程结束后，韩语第三seed仅288/300、无完成metadata；原888条保留为partial，不能挑掉第三seed。按相同参数重跑完整seed2，另存recovery，首288条与旧输出核对；组合时显式引用原seed0/1与完整recovery，不用伪造wall_seconds。
