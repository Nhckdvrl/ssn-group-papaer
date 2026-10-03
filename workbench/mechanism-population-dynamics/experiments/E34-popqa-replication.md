# E34 — Does the Flan QA-format switch replicate on an independently constructed dataset (PopQA counterfactuals)?（2026-10-03）

- **状态：** DONE（2026-10-03；复现）
- **类型：** PILOT（数据集推广；C04 目前只在 ParaConflict 上）
- **对应：** C04、E26；PopQA（Mallen et al. ACL 2023：16 种关系、自然问句、实体流行度）；Xie et al. 2023；Du et al. ACL 2024
- **阳性对照：** 已知条目上 clean 记忆边际 > 0（定义上）；6 个 Flan 对模型在 decl 单元的采信率 > 50%（单句陈述足以让多数条目被采信，否则构造过弱）
- **噪声地板：** 4 配方（dolma1_7、no_flan、c4、dclm-baseline）× 3 seed 合并 seed SD；SE = SD × √(2/3)
- **问题（只回答这个）：** 在 PopQA 构造的反事实上，去掉 Flan 是否同样只降低问答格式下的上下文采信、不影响陈述格式？

## 构造
- 关系 → 陈述开头 stem（作者在登记时写定）：occupation “{s}'s occupation is”；place of birth “{s} was born in”；genre “The genre of {s} is”；father “The father of {s} is”；country “{s} is located in the country of”；producer “The producer of {s} is”；director “The director of {s} is”；capital of “{s} is the capital of”；screenwriter “The screenwriter of {s} is”；composer “The composer of {s} is”；color “The color of {s} is”；religion “The religion of {s} is”；sport “{s} plays the sport of”；author “The author of {s} is”；mother “The mother of {s} is”；capital “The capital of {s} is”。
- 干扰 = 同关系中按固定顺序下一个宾语不同、且不在本条 possible_answers 中的条目的宾语。S = stem + “ ” + 干扰 + “.”。
- 单元：decl = S + “ ” + stem；qa = S + “ Question: ” + 原问句 + “ Answer: ” + stem。clean = stem（判定已知：lp(答案) > lp(干扰)）。
- 抽样：每关系至多 150 条（固定种子），color（34 条）全取。
- 读数：采信边际 lp(干扰) − lp(答案)，各关系等权平均，在 Flan 对 6 个模型共同已知的条目上。

## 判据
- FE = qa − decl；Δ_FE = mean_Flan − mean_noFlan。
- **复现：** Δ_FE > 2·SE，且 |Δ_decl| < Δ_FE / 2。
- 不复现 → C04 限定为 ParaConflict 上的结果，如实报告。

---
## 结果（`results/e34/analysis.json`；2284 条构造，共同已知 1299 条；2026-10-03 07:15）
| 量 | Flan | no-Flan | Δ | SE |
|---|---|---|---|---|
| **FE（qa − decl）** | 3.51 | 1.60 | **+1.91** | 0.56 |
| decl | 8.43 | 8.70 | −0.27 | 0.27 |
| qa | 11.94 | 10.30 | +1.64 | 0.66 |
- 阳性对照 ✓（6 个模型 decl 采信率 95.6%–97.7% > 50%）。**判定：复现**（Δ_FE > 2·SE 且 |Δ_decl| < Δ_FE/2）。C04 不限于 ParaConflict 构造。
- 注：PopQA 上采信率接近天花板（decl 96–98%，qa 95–100%），连续边际是必要读数。
