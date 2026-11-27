# I06：教师实现 × 学生结构的交叉决定可迁移性（2026-11-27）

- **状态：** SEED（Stage 2）
- **来源（必填；优先高质量来源但不是白名单）：** 近邻局限或分歧：Feng 附录 L 原文“each setting uses a single teacher, so we cannot tell whether the best student rank follows the number of directions the trait needs or the rank of the teacher's adapter”；Beyond Owls 计数实验同时把教师和学生改成 attention-only（+16.8 → +32.5），无法归因；Tang 显示教师偏好相同时，实现方式不同，迁移也不同
- **研究动作：** 交叉对照（教师 rank-1/16 × 学生 rank-1/16；Attn/MLP × Attn/MLP）
- **如果为真，主张是：** 待 Stage 1 后写
- **不同结果各带来什么 information gain：** 结果 A（对角线占优）→ 学生恢复的是共享子空间里的参数化投影；结果 B（列占优）→ 学生侧的归纳偏置主导；**不要求两边都能写成论文**
- **最近 3 个近邻与增量：**
  | 近邻 | 它的 claim | 我们的增量 |
  |---|---|---|
  | Feng 附录 H/L | 最优 rank 跟随复杂度 | 把教师实现与知识复杂度解开 |
  | Beyond Owls | attn-only 更强 | 2×2 交叉 |
  | Tang | 实现方式影响迁移 | 在 LLM 规则知识上做 |
- **最便宜的决定性 pilot（能分出决策分支的最小算力）：** Stage 2 另写卡（阳性对照、噪声地板、决策表见对应实验卡）
- **预期论文形态：** C 理论+受控
- **排序打分（1–3）：** 待 Stage 0 结束后填写
- **PARKED / REFUTED 时：** —
