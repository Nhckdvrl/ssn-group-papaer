# E01：drmas-math-repro（2026-09-30）

- **状态：** PLANNED
- **类型：** REPRO（基线复现；同时为 I01 的 pilot 提供两个独立种子的团队）
- **对应：** D1/D2 baseline residency；为 I01 提供两个独立训练 team，为 I02 建 compute accounting
- **问题（一句话）：** 在我们的单节点上，Dr. MAS 的数学双智能体（Solver + Verifier）训练能否复现官方趋势，种子间方差多大？
- **设置：** Dr. MAS 官方数学配置（verl 系，`requirements_sglang.txt`，flash-attn 2.7.4），2×Qwen2.5-1.5B-Instruct（显存或时间不够再降到更小模型；Qwen3-1.7B 作为备选）；**2 个种子**（A、B），其余配置完全相同；评测 MATH500 与 AMC（官方评测脚本）；记录每步梯度范数（Dr. MAS 的核心诊断）
- **读数：** 团队最终答案准确率；训练曲线；每个智能体的梯度范数；与官方报告趋势的差距（官方模型更大，只比较趋势与相对提升）；同时记录 LM calls、input/output tokens、近似 FLOPs（可复现算法）、GPU·s/GPU·h、wall latency
- **阳性对照：** 未训练团队与官方报告的起点是否一致（harness 正确性）
- **噪声地板 + MIE：** 同一 checkpoint 用 3 个采样种子重复评测；先估重复评测波动，再在 I01 pilot 前写清多大 cross-play 差异才值得进入第 3 training seed / 更强 coordination substrate；不把 2×noise 当硬科学阈值
- **混杂审计：** 输入指纹（每个 checkpoint 的评测输入字节一致）；两个种子的数据顺序只由种子决定；不筛种子
- **决策表（跑之前写）：** 结果 A（两个种子都复现到官方趋势，差距写得清）→ 做 I01 的 2×2 cross-play **smoke test**并继续 I02 accounting；结果 B（训练不稳 / 发散）→ 记为痛点，先按官方配置与 agent-wise normalization 复查，仍不稳定则优先 E02；不确定（只有一个种子复现）→ 加第 3 个 reproduction seed。**I01 在 math 上为 null 不等于 G-family 被否定。**
- **算力预算：** 每个种子一次单节点训练（官方参考：2×Qwen3-4B 在 4×H100 上约 38 小时；1.5B 预计明显更少，以实测 GPU·时为准）　**实际：**

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
