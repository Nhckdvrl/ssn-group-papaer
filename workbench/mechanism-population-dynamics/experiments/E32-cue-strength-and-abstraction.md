# E32 — Is the Flan switch cue-driven, graded by cue strength, and abstract beyond the literal template?（2026-10-03）

- **状态：** DONE（2026-10-03；P1 ✗，P2 不触发（模板特异），P3 ✓ 线索驱动）
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

---
## 结果（`results/e32/analysis.json`；共同已知 1680 条；2026-10-03 07:00）
| 单元（线索效应 = 单元 − decl） | Flan − no-Flan Δ | SE |
|---|---|---|
| QA（Flan 模板 “Question: … Answer:”） | **+2.43** | 0.79 |
| Q_only（“Question: …”） | **+2.04** | 0.83 |
| A_only（“Answer:”） | +1.13 | 0.63 |
| QA_short（“Q: … A:”） | +0.39 | 0.89 |
| novel（“Query: … Response:”） | +0.52 | 0.83 |
| incongruent（问另一个实体） | **+3.06** | 1.42 |
- 阳性对照 ✓。**P1 ✗**（QA − Q_only = 0.39 < 1·SE_diff；“Question:” 单独即带来大部分效应）。**P2：novel 不触发**（0.52 < 2·SE；Δnovel/ΔQA = 0.21），且 “template only” 的严格判据也不满足（QA_short 0.39 未 > 2·SE）——**语义等价的 “Q:/A:” 同样不触发**。**P3 ✓（线索驱动）**：问句换成其他实体仍触发（3.06 > 2·SE）。
- **解读：** Flan 装入的不是抽象的“问答 / 阅读理解文体”表征，而是由其**字面模板（尤其 “Question:”）触发**、不检查语义一致性的行为。对理论框架的修正：模型对“文档类型”的识别依赖表面字面线索。
- 事后（不据此重测）：E27 中 S3 统计了所有问答标记，而起作用的只有 Flan 模板 → 可能是 E27 相关偏弱的原因。
