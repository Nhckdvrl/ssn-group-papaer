# E30 — Does instruction-data exposure install the QA-format switch in independently trained public models?（2026-10-03）

- **状态：** REGISTERED（判据提交于计算之前）
- **类型：** PILOT（C04 的独立家族检验：OLMo 2 中期训练前后的天然实验 + 公开基座模型横向描述）
- **对应：** C04、E26；OLMo 2（Team OLMo 2025：stage 1 预训练 ~4T token → stage 2 “Dolmino” 中期训练，混合物含 FLAN 等指令数据，3 个独立 ingredient 运行）；Fouilhé et al. 2026；Sclar et al. ICLR 2024
- **阳性对照：** 各模型次数效应（cK − c1）> 0（操纵有效）；clean 知识边际在 stage 2 后不下降（排除知识损失解释）
- **噪声地板：** Part A 中 3 个 ingredient 运行作为重复（stage 1 末只有 1 个点 → 用 stage 1 末附近 3 个 checkpoint 估计其局部波动）
- **问题（只回答这个）：** 在 OLMo 2 中，混入含指令数据的中期训练是否使“问答格式结尾相对陈述结尾使采信增加多少”（格式效应 FE_c1）显著变大？

## Part A（主检验）：OLMo-2-0425-1B
- checkpoint：stage1 末附近 3 个（stage1-step1880000 / 1890000 / 1907359 附近可用分支）；stage2 ingredient 1/2/3 的最终步；ingredient 1 的中间步（约 10%、25%、50% 处）。
- 读数：E26 的 c1_decl、c1_qa、cK_decl、cK_qa 单元 + clean 边际；条目 = 所有 checkpoint 共同已知的条目，类别等权（同 E26）。序列起始 token：tokenizer 的 bos（若无则 eos）。
- **判据：** ΔFE = mean_ingredient(FE_c1, stage2 末) − mean(FE_c1, stage1 末 3 点) > 2·SE，SE = √(var_stage2/3 + var_stage1/3)。且陈述单元 c1_decl 的变化 |Δ| < ΔFE/2（效应集中在问答格式）。
- 时间进程（只报告）：ingredient 1 中间步上的 FE_c1。

## Part B（只描述，不判定）：公开基座模型
- Pythia-1B / 1.4B（Pile，无指令数据）、OLMo-1B-0724-hf（Dolma 1.7，含 Flan）、OLMo-2-0425-1B（最终）、SmolLM2-1.7B、Qwen2.5-1.5B、Llama-3.2-1B、gemma-2-2b（各自文档化的预训练数据中指令 / 合成数据的有无与比例，查文档后记录；不在结果出来后补充）。
- 报告各模型 FE_c1 与其文档化指令数据暴露的对应；家族差异混杂架构 / 规模 / 数据，不作因果结论。

## 文档化的指令数据暴露（登记时、结果之前查得）
| 模型 | 预训练中的指令 / 问答式数据（文档） | 来源 |
|---|---|---|
| Pythia-1B / 1.4B | 无（Pile；无 Flan 类数据集） | Biderman et al. 2023；Gao et al. 2020 |
| OLMo-1B-0724-hf | Dolma 1.7，含 tulu_flan（约占 1–2%） | Dolma 1.7 / DataDecide named_data_mixes |
| OLMo-2-0425-1B stage1 末 | OLMo-mix-1124（DCLM 为主），无 FLAN 集合 | Team OLMo 2025 |
| OLMo-2-0425-1B stage2 末 | Dolmino 50B 混合物：**FLAN 16.6%**、数学 20.8%、DCLM 47.2%、pes2o 5.9%、Wiki 7.1%、StackExchange 2.5% | Team OLMo 2025（2501.00656）；dolmino-mix-1124 数据卡 |
| SmolLM2-1.7B | 网页 / 代码 / 数学，退火阶段上采样数学与代码；指令数据未记载 | Allal et al. 2025（2502.02737） |
| Qwen2.5-1.5B | 由 Qwen2 Instruct 系列生成的合成数据（数学 / 代码 / 知识），比例未公开 | Qwen Team 2024（2412.15115） |
| Llama-3.2-1B、gemma-2-2b | 未公开 | — |
预期（Part B，只描述）：Pythia 与 OLMo-2 stage1 末的 FE_c1 最小；OLMo-2 stage2 末最大或接近最大。
