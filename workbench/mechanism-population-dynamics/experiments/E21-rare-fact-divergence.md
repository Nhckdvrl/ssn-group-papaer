# E21 — Do same-recipe runs disagree mostly on rare facts?（2026-10-03，CPU-only）

- **状态：** REGISTERED（判据提交于计算之前；infini-gram 计数进行中，E13 数据已在盘上但未做此分析）
- **类型：** PILOT（复用 E13 数据 + 语料统计；不需要 GPU）
- **对应：** E13（410M × 10 run 的逐国家边际）、E18（run 差异是条件特异的）；Fehlauer et al. EMNLP 2025（低频 token 跨 seed 分歧更大）；Yu et al. 2023 / LMEnt 2025（高频事实更坚持记忆）
- **阳性对照：** 跨国家，run 平均记忆边际与 Pile 中“The capital of X is Y”计数正相关（Spearman ≥ 0.3）
- **噪声地板：** 国家级 bootstrap；实验单位：国家（n ≈ 172），seed 维度 n=10
- **问题（只回答这个）：** 410M 群体中，run 间仲裁分歧（同一国家上 10 个 run 的边际标准差）是否集中在 Pile 中罕见的事实上？

## 读数
- 边际 m_{c,r} = E13 `per_country[c].margin`（冲突提示下 lp(正确) − lp(干扰)，20 个干扰平均；越大越坚持记忆）。
- 频率 f_c = log(1 + Pile 中短语 “The capital of {country} is {capital}” 计数)；辅助：log(1 + 国家名计数)。
- 分歧 D_c = 10 个 run 上 m_{c,r} 的标准差；混杂：|mean_r m_{c,r}|（离决策边界的距离）与 mean 本身。

## 分析与判据
- 阳性对照：Spearman(f_c, mean_r m_{c,r}) ≥ 0.3。不通过 → 频率读数无效，主检验不可判定。
- 主检验：D_c 对 f_c 的偏 Spearman（控制 mean_r m_{c,r} 与 |mean_r m_{c,r}|，用秩回归残差）。
  - **集中于罕见事实：** 偏 ρ ≤ −0.3（且去掉 seed4 后 ≤ −0.2）。
  - **无关：** |偏 ρ| < 0.15。
  - 其余如实报告。
- 稳健性：用国家名频率代替短语频率重复一次（只报告）。
