# E24 — Is the recipe's copy-vs-recall prior carried by induction (copy) strength?（2026-10-03）

- **状态：** REGISTERED（判据提交于计算之前；GPU 部分在 E20 完成后用已缓存权重运行）
- **类型：** PILOT（数据 → 机制 → 倾向 的中介检验）
- **对应：** E20、E23；C01（induction 角色在 run 间可复现）；Olsson 2022；Chen, Luo, Pan 2026；Ortu et al. ACL 2024（复制 vs 回忆竞争）
- **阳性对照：** 每个模型在重复随机 token 序列上的第二遍 loss 显著低于第一遍（induction 存在）；随机 token 首遍 loss ≈ 均匀分布量级
- **噪声地板：** 序列 bootstrap；实验单位 = 模型（75），配方层面 n = 25
- **问题（只回答这个）：** DataDecide 1B 模型的 induction 复制强度，能否解释其在 Substitution 冲突上的采信边际——在配方之间，以及在同一配方的 seed 之间？

## 读数（每个模型）
- **I1 复制保真度（主）：** 200 条长度 2×128 的重复随机 token 序列（token 从 id 1000–40000 均匀抽取，固定种子），I1 = −（第二遍平均 loss）。
- I1b（辅）：首遍 − 第二遍 loss。补充（2026-10-03，仅 dolma1_7 default 冒烟后、群体运行前）：冒烟显示首遍 loss 12.6（高于均匀分布 10.8），首遍 loss 反映的是对随机 token 的先验校准而非复制，故主读数改为第二遍 loss，差值降为辅助。
- **I2 最大 induction 头分数：** 第二遍中各头对“上一次出现位置 + 1”的平均注意力，取最大头。
- 倾向：E20 Substitution 冲突 6 个类别的平均采信边际（A_sub）；知识：E20 clean 边际均值（K）。

## 判据
- **配方层面（25 个配方的 3 seed 均值）：** Spearman(I1, A_sub) ≥ 0.5 且对 K 的偏相关保持 ≥ 0.4 → induction 强度承载配方的复制先验。
- **中介（仅当 E23 主检验成立时计算）：** S1 → A_sub 的 Spearman 在控制 I1 后下降 ≥ 50% → 部分中介。
- **seed 层面（75 个配方内偏差）：** Spearman(ΔI1, ΔA_sub) ≥ 0.3 → seed 间差异也部分由 induction 强度承载；|ρ| < 0.15 → seed 差异与 induction 无关（与 E18 的“条件特异”一致）。
- |配方层面 ρ| < 0.2 → induction 强度不承载配方效应；如实报告。
