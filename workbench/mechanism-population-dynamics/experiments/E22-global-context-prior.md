# E22 — Is there a corpus-level "context-trust prior" beyond item frequency?（2026-10-03，CPU-only）

- **状态：** REGISTERED（判据提交于计算之前；依赖 E20 的逐条目边际与 infini-gram 计数；登记时未查看任何 E20 逐条目结果）
- **类型：** PILOT（条目层面双重差分；不需要 GPU）
- **对应：** E20；Kim et al. 2025（2510.02370，合成数据：语料整体的不一致 / 重复设定全局偏好）；Yu 2023、LMEnt 2025、Fouilhé 2026（条目层面频率效应）
- **阳性对照：** 条目频率系数 γ 的方向：频率越高越不采信上下文（γ < 0，采信方向的边际）
- **噪声地板：** seed 间差异（每配方 3 seed）；条目级 bootstrap
- **问题（只回答这个）：** 同一批条目上，控制“该条目在训练语料中的频率”后，不同配方之间是否仍有超过 seed 噪声的系统性采信差异（即全局先验）？

## 设置
- 配方（有 infini-gram 索引或可由其插值）：dolma1_7（Dolma v1.7）、dclm-baseline（DCLM）、c4（C4）、dclm/dolma 25/50/75% 混合（频率按混合比例对两语料的归一化频率线性插值）；每配方 3 seed。
- 条目：World Capital（主），其余类别在计数可用时加入（只报告）。
- 读数：E20 `margin_all_items`（lp(干扰) − lp(答案)，采信方向），冲突形式分开。
- 频率：log(1 + 短语计数 / 语料 token 数 × 1e9)，语料 token 数取 infini-gram 文档给出的索引大小。

## 模型与判据
- 对每个冲突形式：margin_{i,r,s} = α_i + β_r + γ·logfreq_{i,r} + ε（OLS，条目固定效应 α_i、配方固定效应 β_r），seed 作为重复观测；β_r 的标准误用按 seed 的 cluster bootstrap（在每个配方内重采样 seed）。
- **阳性对照：** γ < 0 且 95% CI 不含 0。
- **全局先验存在：** dclm 与 dolma1_7 的 β 差的绝对值 > 2 × 其 bootstrap SE，且 25/50/75% 混合的 β 随 DCLM 比例单调（5 点 Spearman |ρ| ≥ 0.9）。
- **无全局先验：** β 差在 1 个 SE 内，或混合序列不单调。
- 其余如实报告；不追加协变量。
