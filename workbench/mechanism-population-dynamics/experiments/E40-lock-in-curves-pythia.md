# E40 — Lock-in curves of role layout within single runs (Pythia, dense early checkpoints; CPU)（2026-10-03）

- **状态：** REGISTERED（判据提交于计算之前；E02 的逐头分数已在盘上，但从未做“早期图 vs 最终图”的分析）
- **类型：** PILOT（C05 / E37 的高时间分辨率补充；复用 E02）
- **对应：** E37（DataDecide 1B：step 2500 ≈ 3.6% 时布局已与最终相关 0.81–0.91，描述性）；C05；Olsson 2022（induction 相变）
- **阳性对照：** 每个 run 最终步附近相邻 checkpoint（130000 vs 143000）的图相关 ≥ 0.9（测量与晚期稳定性）
- **噪声地板：** 跨 seed 同一步的图相关（不同初始化，应低），作为“未锁定 / 偶然相似”的参照
- **问题（只回答这个）：** 在单个 run 内，previous-token 与 induction 角色在各头上的布局，从训练的哪一步起与最终布局一致（锁定）？

## 数据
- E02 的 `S_prev`、`S_ind`（每个 head 的分数）：Pythia-70M seed0–9（canonical + seed1..9）× 16 个 step（0、128、256、512、1000、2000、3000、4000、6000、8000、16000、32000、64000、100000、130000、143000）；31M、160M 有的 step 一并报告。

## 量
- 锁定曲线 c(t) = Spearman(图_t, 图_143000)（逐 run）；锁定步 t* = 最早的、此后所有 step 均满足 c ≥ 0.8 的 step。
- 参照：同一步不同 seed 之间的平均 Spearman。

## 判据（70M 为主）
- **早期锁定：** S_prev 与 S_ind 的锁定步中位数 ≤ 6000（≈ 4% 训练）。
- **晚期锁定：** 中位数 ≥ 32000。
- 其余如实报告；31M / 160M 只报告。
