# Diverse Policies Recovering via PMI Weighted Imitation — ICLR2025

- 主源<https://arxiv.org/html/2410.15910> / official PDF<https://openreview.net/pdf/5049eb9f322c8b47b4114bdf870c0ace98d72e70.pdf>。
- 已读§4方法/Proposition1、§5 Atari与Basketball、Appendix A证明/B超参；作者code未找到可确认URL、未复现。
- **DOCUMENTED：** style关联只在部分state-action上明显；用MINE估p(z|s,a)/p(z)加权条件BC。I=0退化普通BC，H(Z|S,A)=0退化分style克隆。数据为Atari-Head人类游戏与职业篮球，style为程序化position/range/fire等；style fidelity与游戏reward分开测。
- **RECONSTRUCTED：** 整段轨迹同一style标签不意味着每一步等样携带style信息→按局部证据权重学习。我们不能称首次发现角色行为信息集中于部分机会/状态。
- **限制/距离：** 风格标签不是完整NPC角色价值，训练为IL非persona PPO；条件MI、机会与语义效度不能凭换NPC名称就成为新贡献。当前仅定位资料。
