# E33 — Is the Flan switch carried by a transplantable "QA-format state" in the residual stream?（2026-10-03）

- **状态：** REGISTERED（判据提交于计算之前；E28 判定开关不在前 10 取回头上）
- **类型：** PILOT（表征层面的机制检验）
- **对应：** C04、E26、E28；Todd et al. ICLR 2024（function vectors）；Hendel et al. 2023（task vectors）；E16（diff-of-means 旋钮在 Pythia 上失败——本实验的向量是两种提示格式之差，并设方法阳性对照）
- **方法阳性对照：** 在测试半上，把 v_l* 加到陈述提示末位后，该位置下一 token 分布与问答提示末位分布之间的 KL 平均下降 ≥ 30%（相对未加时）；6 个模型都需满足，否则移植无效、主检验不可判定
- **噪声地板：** 每配方 3 seed；SE = √((var_Flan + var_noFlan)/2) × √(2/3)
- **问题（只回答这个）：** 把问答格式在最后位置引起的残差变化（格式状态）移植到陈述提示上，是否在 Flan 模型中重现“问答格式下更信上下文”，而在 no-Flan 模型中不重现？

## 设置
- 模型：dolma1_7-1B、dolma1_7-no-flan-1B × 3 seed。条目：E28 的 300 条（6 模型共同已知、每类 50），按固定种子对半分为 A（估计 / 选层）与 B（测试）。
- 提示：E26 的 c1_decl、c1_qa（两者末尾 stem 相同 → 末位 token 相同）。
- 格式向量：v_l = mean_A[h_l(c1_qa, 末位) − h_l(c1_decl, 末位)]，h_l = 第 l 层输出残差，l ∈ {2, 4, 6, 8, 10, 12, 14}。
- 选层：在 A 上，把 v_l 加到 c1_decl 末位，取使采信边际上升最多的 l*（每个模型各自选；无 Flan 模型同样流程）。
- 测试（B）：Δ = margin(c1_decl + v_l*) − margin(c1_decl)；恢复率 Rec = Δ / (margin(c1_qa) − margin(c1_decl))（仅对 Flan 模型报告，因 no-Flan 的分母接近 0）。
- 只在提示末位加向量；采信边际同 E20（所有候选 token 对数概率之和）；稳健性：只用候选首 token 的边际（只报告）。

## 判据
- 方法阳性对照（见上）。
- **格式状态承载开关：** Flan 模型平均 Rec ≥ 0.5，且 Δ_Flan − Δ_noFlan > 2·SE。
- **只部分承载：** 0.2 ≤ Rec < 0.5 且 Δ 差 > 2·SE → 如实报告。
- **不承载：** Δ 差 < 2·SE → 格式开关不由单一末位格式状态表达；如实报告，不改为多位置移植。
