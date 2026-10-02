# E29 — When during pretraining does the Flan-installed QA-format switch appear?（2026-10-03）

- **状态：** REGISTERED（判据提交于计算之前）
- **类型：** PILOT（发育时间；本工作区 territory 的“发育层”）
- **对应：** C04、E26；Kim et al. 2025（上下文偏好先升后降）；Zucchet et al. 2025（事实学习平台期）；Singh 2023（ICL 的出现与消退）；Mid-training 文献（Liu, Neubig, Xiong 2025：引入时机与混合比例的交互）
- **阳性对照：** clean 知识边际 K 在 step 2500 → 69369 之间上升（6 个模型都满足）；否则 checkpoint 加载 / 读数有误
- **噪声地板：** 每步 3+3 seed；SE = √((var_Flan + var_noFlan)/2) × √(2/3)（df 4）
- **问题（只回答这个）：** 在 DataDecide 1B 的训练过程中，Flan 带来的问答格式开关（FE_c1 的 Flan − noFlan 差）从哪一步开始出现、之后是否保持？

## 设置
- 模型：dolma1_7-1B、dolma1_7-no-flan-1B × 3 seed，step 2500 / 7500 / 17500 / 35000（最终步 69369 复用 E26）。
- 读数：E26 的 c1_decl、c1_qa 单元 + clean 边际；条目 = 该步 6 个模型共同已知的条目（各步分别取），类别等权平均（同 E26）。
- FE_c1 = margin(c1_qa) − margin(c1_decl)；Δ_FE(step) = mean_Flan − mean_noFlan；Δ_decl(step) 同理（陈述单元本身的 Flan 差）。

## 判据
- 每步：Δ_FE > 2·SE → “开关存在”。报告最早出现的步，以及之后各步（含最终）是否都存在（“出现后保持”）或出现后消失（“瞬态”）。
- 对照：Δ_decl 在各步应不显著（|Δ_decl| < 2·SE）；若早期显著 → 早期存在非格式的 Flan 效应，如实报告。
- 不追加步数；若所有中间步都不显著而最终显著 → 记为“晚期出现”。
