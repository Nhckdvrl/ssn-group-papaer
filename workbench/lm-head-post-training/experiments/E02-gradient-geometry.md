# E02：梯度投影与组级信号（2026-11-26；对话 E1）
- **状态：** PLANNED
- **类型：** PILOT / 标准测量与资产建设
- **对应：** I02
- **问题（一句话）：** 同轨迹的奖励加权与教师/on-policy 分布分别怎样影响单 token、题目级输出空间投影和梯度方向？
- **设置：** 首选 Qwen3-8B（固定 revision，选能产生足够可验证 rollout 的同一 checkpoint）；先 8 prompt × 4 rollout smoke，目标 128×8（讨论初始规模，按信号和算力调整）；保存固定 prompt、教师参考、采样 token、reward、advantage、mask、长度、截断；同轨迹 replay CE 与 advantage 加权，另教师 CE；不更新模型参数。实际数据/seed/revision/命令/采样设置及 GPU·时预检后写入。详见 [技术指南](../RESEARCH_PLAN.md) §3–4。
- **读数：** 正交投影能量 ρ、梯度增益 γ；逐 token 等权/能量加权与组级 ρ(sum g)、γ(sum g)、抵消、zero groups、有效秩和 cosine；真实参数梯度非同一对象。相同 token c≠0 下 ρ/γ 不变。零梯度 undefined，显式记录。分开 KL/clipping/entropy；以题为统计单位。
- **阳性对照：** 合成低秩 W 的列空间内/外向量、缩放不变量、显式投影 vs Gram/SVD 闭式、autograd vs CE 公式、正负 c 共线及正负抵消、实际模型少量 token 复算；rank threshold 敏感性。
- **噪声地板 + MIE：** 相同 logits 重复/高精度对照测数值误差；paired bootstrap 以 prompt 为单位；效应必须超出工具误差并影响后续训练选择。没有预定“瓶颈”ρ 阈值。若组级分母接近零，单列比例与绝对能量。
- **混杂审计：** 同轨迹、同分布、同 mask 控制 objective；教师轨迹差异只作分布观察；全对/全错、长度、熵、截断、tokenization、replay 概率与权重归一化透明报告；跨模型/跨词表因果未控制且不做首轮主张。运行前按 EXECUTION §4 逐项补齐。
- **决策表（跑之前写）：** 单 token 不变量失败→修实现；组级差异稳定→看抵消/真实参数梯度决定 E03；只有分布差异→限定归因；无信号→报告精度与不确定性、交人审；不确定→按组级 CI 增加同一条件的题目，不盲扫模型。
- **算力预算：** rollout 与 replay 单节点；smoke 记录吞吐、峰值显存、Gram/SVD 成本后确定 GPU·时上限。 **实际：** 未运行。

## 结果
未运行。保存原始 rollout、奖励校验和逐题统计到本地，提交小汇总；追加结果、CI、失败与主张变化。
