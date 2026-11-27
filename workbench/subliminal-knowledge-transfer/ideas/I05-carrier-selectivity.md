# I05：载体选择性：载体的好坏取决于知识，存在排序反转（2026-11-27）

- **状态：** SEED（Stage 2；E05 含小规模自然语言载体）
- **来源（必填；优先高质量来源但不是白名单）：** 近邻局限或分歧：Li 2609.23260（Qwen-7B cat）数字 90.8% > 乱码 63.1% > 医学 34.3%；Casademunt（phantom transfer）数学 / 代码不迁移、Alpaca 最好；经典 KD 中 Nayak 要求“target-class balanced”，Frank & Davis 认为“KD is a sufficient sampling problem”
- **研究动作：** 设计空间分解（知识 × 载体）
- **如果为真，主张是：** 待 Stage 1 后写
- **不同结果各带来什么 information gain：** 结果 A（出现排序反转）→ 单载体研究的结论都需重读；结果 B（载体只有整体强弱）→ 记录为载体的通用效率；**不要求两边都能写成论文**
- **最近 3 个近邻与增量：**
  | 近邻 | 它的 claim | 我们的增量 |
  |---|---|---|
  | Li | broadband probe | 知识依赖的载体效应 |
  | Casademunt | 自然语言跨模型 | 受控比较 |
  | Frank & Davis | 充分采样 | LLM SL 情形 |
- **最便宜的决定性 pilot（能分出决策分支的最小算力）：** Stage 2 另写卡（阳性对照、噪声地板、决策表见对应实验卡）
- **预期论文形态：** B 构念+测量
- **排序打分（1–3）：** 待 Stage 0 结束后填写
- **PARKED / REFUTED 时：** —
