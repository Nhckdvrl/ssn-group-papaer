# E37 — When during pretraining is the initialization-set component layout locked in?（2026-10-03）

- **状态：** REGISTERED（判据提交于计算之前）
- **类型：** PILOT（C05 的发育层；territory 的“发育顺序”层级）
- **对应：** C05（E35：布局由初始化决定，强度由数据决定）；Olsson 2022（induction 相变出现在早期）；Chen et al. ICML 2026（2511.16893，出现时间可预测）；Pre-carved Niches；E35 附加 step0 测量
- **解释假说（待检验）：** 早期梯度由初始化 + 各自然语料共享的低阶统计决定 → 同初始化在不同语料上的早期轨迹相近 → 角色分配的对称性破缺早期发生并被锁定。
- **阳性对照：** 每个 checkpoint 的 previous-token 图测量信度（两半文本）≥ 0.8；最终步复现 E35 的模式（这 3 个配方子集上 SI − SD > 0.1）
- **噪声地板：** 小样本（每步 SI 9 对、SD 9 对、DD 18 对），报告配对相似度的全部值与均值
- **问题（只回答这个）：** 在训练早期（step 2500 ≈ 3.6%、step 10000 ≈ 14%），同初始化不同数据的模型之间，induction / previous-token / 上下文取回头的布局是否已经与最终一样“由初始化决定”？

## 设置
- 模型：DataDecide 1B，配方 {dolma1_7, c4, dclm-baseline} × 初始化 {default, large-aux-2, large-aux-3} × step {2500, 10000}（18 个 checkpoint）；step 0（3 个初始化本身，E35 附加）与最终步（E35）复用。
- 读数：E35 的 M1 / M2 / M4 图（同一脚本 `e35_census.py --step`）。
- 量：每步的 SI / SD / DD 平均 Spearman；每个模型早期图与其自身最终图的 Spearman（锁定度）。

## 判据（M1、M2、M4 分别）
- **早期锁定：** step 2500 时 SI − SD > 0.1，且早期图与自身最终图的平均 Spearman ≥ 0.5。
- **逐渐形成：** step 2500 时 SI − SD ≤ 0.1，但 step 10000 时 > 0.1。
- **晚期形成：** 两个早期步都 ≤ 0.1（只在最终步出现）。
- 如实报告所有值；不追加步数。
