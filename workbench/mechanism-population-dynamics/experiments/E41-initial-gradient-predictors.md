# E41 — Does the initial gradient (growth rate at step 0) predict which heads take which roles?（2026-10-03）

- **状态：** REGISTERED（判据提交于计算之前）
- **类型：** PILOT（C05 的机制：对称性破缺由什么决定）
- **对应：** C05、E39（单头初始权重统计量不能预测，|ρ| < 0.1）、E40（布局在 ≈ 2% 训练锁定，之前有共享阶段）；对称性破缺理论（Breaking Symmetry When Training Transformers 2402.05969；Symmetry Breaking in Transformers 2601.22257；Saxe et al. 2014：增长率由初始投影决定）
- **假说：** 决定哪个头胜出的不是初始“大小”，而是初始“增长率”——训练开始时损失梯度对该头参数的推动强度。
- **阳性对照：** 目标图同 E39（去噪平均图，拆半可靠性 0.68–0.94）；梯度测量的可靠性：两批不同文本上逐头梯度范数的 Spearman ≥ 0.8，否则主检验不可判定
- **噪声地板：** 错配零分布（一个初始化的梯度特征 vs 另一个初始化的目标图）
- **问题（只回答这个）：** step0 时语言建模损失对各头参数的梯度大小，能否预测该初始化下 induction / previous-token / 上下文取回角色的布局？

## 设置
- 模型：3 个初始化的 step0（DataDecide-c4-1B step0-seed-*，与所有配方相同）。
- 文本：E35 的 50 篇自然文本（Pile eval 固定子集，OLMo 分词，各 256 token），分为两批各 25 篇。
- 特征（逐头）：‖∂L/∂W_Q^h‖、‖∂L/∂W_K^h‖、‖∂L/∂W_V^h‖、‖∂L/∂W_O^h‖（单次前向 + 反向，fp32，每批一次）；以及 QK 合并 ‖∂L/∂W_Q^h‖·‖∂L/∂W_K^h‖。
- 目标：E39 的去噪平均图（M1 / M2 / M4）。

## 判据（同 E39）
- 对每个 (角色, 特征)：3 个初始化的 ρ_match 与 6 种错配的 ρ_mismatch。
- **初始梯度可预测角色：** 存在 (m, f) 使 ρ_match ≥ 0.3、ρ_match − ρ_mismatch ≥ 0.2、且 3 个初始化同号。
- **不可预测：** 所有 |ρ_match − ρ_mismatch| < 0.1。
- 其余如实报告。
