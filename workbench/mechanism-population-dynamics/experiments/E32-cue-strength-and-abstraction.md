# E32 — Is the Flan switch cue-driven, graded by cue strength, and abstract beyond the literal template?（2026-10-03）

- **状态：** REGISTERED（判据提交于计算之前）
- **类型：** PILOT（检验理论框架的三个预测；见 logs/2026-10-03.md 05:20）
- **对应：** C04、E26；Xie et al. ICLR 2022（ICL 作为对潜在文档概念的贝叶斯推断）；Pan et al. 2023（任务识别）；Sclar et al. ICLR 2024
- **阳性对照：** QA 单元的 Flan Δ 复现 E26 的 c1_qa 结果（> 2·SE）；否则本次运行无效
- **噪声地板：** 同 E26（dolma1_7、no_flan、c4、dclm-baseline 各 3 seed，合并 seed SD，df 8）
- **问题（只回答这个）：** Flan 带来的上下文采信提升是否 (P1) 随问答线索强度单调增加，(P2) 能被训练语料中罕见的问答标记触发，(P3) 在问句与当前实体不一致时仍被触发？

## 设置
- 上下文：E26 的单句陈述 S；结尾统一为 E26 的 stem。条目：E26 中 Flan 对 6 个模型共同已知的条目。
- 单元：decl = S + stem；A_only = S + “ Answer: ” + stem；Q_only = S + “ Question: q ” + stem；QA = S + “ Question: q Answer: ” + stem（= E26 c1_qa）；QA_short = S + “ Q: q A: ” + stem；novel = S + “ Query: q Response: ” + stem；incongruent = S + “ Question: q′ Answer: ” + stem（q′ = 同类别中按固定顺序的下一个条目的问句）。
- 标记频率（Dolma 1.7，infini-gram，登记前查得）：Question: 11,312,890；Answer: 9,644,632；Q: 38,387,178；A: 6,887,014；**Query: 146,036；Response: 745,776**。
- 读数：采信边际 lp(干扰) − lp(答案)；每单元的线索效应 = 单元 − decl；Flan Δ = mean_Flan − mean_noFlan。

## 判据
- **P1（线索强度）：** Δ(QA) > Δ(A_only) 且 Δ(QA) > Δ(Q_only)，两个差值均 > 1·SE_diff（SE_diff = √(SE²+SE²)）。
- **P2（抽象）：** Δ(novel) > 2·SE → 开关能被罕见标记触发（抽象文体表征）；Δ(novel) < 1·SE 且 Δ(QA_short) > 2·SE → 只对见过的模板起作用。报告 Δ(novel)/Δ(QA)。
- **P3（线索驱动）：** Δ(incongruent) > 2·SE → 线索驱动（问句内容与实体不一致仍触发）；< 1·SE → 语义驱动。
- 每条独立判定，如实报告；不追加单元。

## 构造检查（CPU，登记时）
- 2146 条：QA 单元与 E26 c1_qa 逐字相同（2146 / 2146）；incongruent 借用的问句不含本条目的答案或干扰（初版 33 条泄漏 → 改为按序向后找第一个不含二者、且主语不同的问句 → 0 条）。
