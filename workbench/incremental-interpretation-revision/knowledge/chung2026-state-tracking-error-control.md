# Rethinking State Tracking in Recurrent Models Through Error Control Dynamics

状态追踪的误差控制：Chung等，NeurIPS 2026，arXiv 2605.07755v1，主文§1–5；附录A局限。`[证据级别：主文精读，附录范围见下]`；接收presentation/公开评分未核对。
1. **论文形态：** 理论与受控实验。
2. **背景与压力：** [正文](https://arxiv.org/abs/2605.07755)。9类递归模型，C2/C6/S3，训练长度60、测试至1000；另以113个S3模型检验失败尺度。理论限定于保持符号状态的仿射返回映射；实验证明有有限长度成功的仿射例外。
3. **改变的前提：** 能表达状态转移不保证漂移受到控制。
4. **idea来源（RECONSTRUCTED）：** 近邻证明可表达，训练后的长程失败迫使作者增加误差控制这个对象。保持所有正确状态会约束状态分离方向的收缩。对GP可借“纠错时是否保住正确结构”的研究动作；不能把定理移植到非线性Transformer，也不能用均值几何阈值替代逐项行为证据。
5. **与近邻的距离：** 仿射SSM表达能力；state-dependent递归结构；group/state-tracking任务，论证增量是学得误差控制。重建的是论文论证中的研究动作，不冒充作者实际发现历史；定位不产生自动关线判决。
6. **方法 / 实验 / 数据 / 基线：** 第2/4项记录已核对设置与主表范围；可复用资产由原文链接取得，不把benchmark条数当独立统计单位。
7. **证据边界：** 实读范围：Main 1-5 and Appendix A limitations。PDF与失败/版本记录位于`/data1/xiangding/work/incremental-interpretation-revision/papers/reassessment-2026-10-07`；未核对的最终版本、review/score或附录不补猜测。第4项的局限必须随结论引用。
8. **可迁移研究动作：** 把第3项前提转成能被推翻的测量，并保留旧解释与阳性对照；先对齐对象和信息/算力，再决定是否迁移方法。
9. **对我们：** 第4项给出具体可借动作与不可外推边界；与I03/I04的共同定位见[整体画像](REVISION_RESEARCH_SYNTHESIS.md)。当前没有因此升级主张或得到合格idea。
