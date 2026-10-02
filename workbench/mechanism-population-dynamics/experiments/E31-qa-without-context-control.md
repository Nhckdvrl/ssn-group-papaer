# E31 — Is the Flan QA-format effect about context, or about QA-mode answering in general?（2026-10-03）

- **状态：** REGISTERED（判据提交于计算之前）
- **类型：** PILOT（C04 的替代解释排查）
- **对应：** C04、E26（问答结尾单元 Flan Δ +1.3…+3.5，陈述结尾 ≈ 0）
- **替代解释：** Flan 改变的是“问答格式下的作答模式”（例如对记忆答案更 / 更不自信），而不是“问答格式下依据上下文”。若如此，无上下文的问答提示也应显示 Flan 差异。
- **阳性对照：** 所有模型在无上下文提示上 lp(答案) − lp(干扰) > 0（条目为已知条目，定义上应成立）
- **噪声地板：** 同 E26（4 配方 × 3 seed 合并 seed SD，df 8）
- **问题（只回答这个）：** 在没有上下文（或只有不含干扰答案的中性填充）时，问答格式相对陈述格式对“记忆答案 vs 干扰答案”偏好的影响，是否在 Flan 与 no-Flan 模型间不同？

## 设置
- 模型：E26 的 12 个（dolma1_7、no_flan、c4、dclm-baseline × 3 seed）。条目：E26 的共同已知条目（Flan 对 6 个模型）。
- 单元（stem、q、F 同 E26 构造）：n_decl = stem；n_qa = “Question: q Answer: stem”；f_decl = F′ + stem；f_qa = F′ + “Question: q Answer: stem”（F′ = 与 E26 cF 相同长度的中性填充，不含陈述 S）。
- 读数：记忆边际 lp(答案) − lp(干扰)。无上下文格式效应 NFE = (n_qa − n_decl) 与 (f_qa − f_decl) 的平均。

## 判据
- Flan 效应 Δ_NFE = mean_Flan(NFE) − mean_noFlan(NFE)，SE 同 E26。
- **上下文特异（支持 C04 解释）：** |Δ_NFE| < 2·SE，且 |Δ_NFE| < |E26 格式 Δ| / 3（= 0.74）。
- **一般作答模式（削弱 C04 解释）：** |Δ_NFE| > 2·SE。方向报告：若 Flan 使问答格式下记忆边际下降，说明 Flan 让模型在问答格式下对干扰答案本就更开放（需在 C04 中注明）。
