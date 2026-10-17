# Holonomy / Multi-Way Alignment — 2026定位

- Holonomy主源<https://arxiv.org/abs/2601.21653> / <https://openreview.net/forum?id=czJqKToDGq>；作者文头与corpus标ICLR2026，official venue未独立核对。已读正文§2–3理论/估计器，非全文附录/代码审完。
- **DOCUMENTED：** global whitening、shared subspace、SO Procrustes、沿输入闭环组合holonomy；旋转不变性、线性null、有限样本/截断误差已有理论。不是所有policy质量的通用score。
- Multi-Way主源<https://arxiv.org/abs/2602.06205> / <https://github.com/acharaakshit/multiway-alignment>，当前仅摘要/方法入口/README，尚无完整代码审计。共享universe将多模型表示translation由M²降至M，pairwise Procrustes、GPA/GCP为作者方法；stitching/geometry preservation已有owner。
- **RECONSTRUCTED/对我们：** 特征坐标与功能配套关系可借已有理论分析，但E28真实co-step没utility信号。普通Procrustes及人工旋转null绝不能作为新NPC方法结论。
