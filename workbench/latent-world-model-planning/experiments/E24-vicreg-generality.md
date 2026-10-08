# E24：机制是否只属于 SIGReg？——VICReg 正则下的规模 × D_eff × L2 规划（2026-10-07 22:15）

- **状态：** RUNNING（本卡在任何 VICReg 结果之前写定）
- **类型：** CONFIRMATORY（I16 机制的推广检验）
- **对应：** I16；E23 B / 塌缩分析（26 个 TwoRoom 检查点上 L2 成功率对 log D_eff 的 R² 0.83–0.89）
- **问题：** 换成另一类常用的反坍缩正则（VICReg：方差铰链 + 协方差去相关，PLDM 类 latent 世界模型使用），“规模推高 D_eff → latent L2 规划短视”是否仍然成立？还是只属于 SIGReg 的高斯化目标？
- **设置：** TwoRoom，XXS / S / M，种子 0 / 1，60k 步，其余同 E21；正则 = 方差铰链 + 0.04 × 协方差非对角平方和 / D，权重 1.0（替代 SIGReg 项），`train.py --reg vicreg --sigreg_w 1.0`。
- **读数：** D_eff 与 P(K≥0.5)·D_eff（kernel_bound.py）；度量视野；n=200 闭环 CEM+L2 与慢特征 / auto（offset 25 / 50 / 75）。
- **预测：** (i) VICReg 下 D_eff 随尺寸上升；(ii) L2 远目标成功率随尺寸下降；(iii) VICReg 检查点落在 SIGReg 的“成功率–log D_eff”回归线附近（残差在 ±10pp 内）；(iv) 慢特征 / auto 仍 ≥ 90%（off50）。
- **决策表：** (i)(ii) 成立 → 机制写成“各向同性类反坍缩正则”的一般性质；(i) 不成立（VICReg 下 D_eff 不随尺寸上升）且 (ii) 不成立 → 机制限定为 SIGReg / 高斯化正则，论文明确写出；(iii) 偏离大 → D_eff 不是充分统计量，另找变量。训练坍缩（D_eff 很低、近目标崩）→ 调一次权重（0.3 或 3.0）后仍坍缩则报告为不适用。
- **噪声地板：** n=200 二项 SE ≈ 3.5pp；种子间 ±5pp（E21）。
- **算力：** 6 次训练（fvcrc13 / fvcrc10 空闲卡），评测走既有队列。
