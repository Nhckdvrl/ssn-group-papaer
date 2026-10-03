# E49：第三个冲突数据集——NQ-Swap 上的 “Question:” 开关（2026-10-03）

- **状态：** PLANNED
- **类型：** CLAIM（C04 的数据集广度：2 → 3）
- **对应：** C04；A02 §2“C04 的数据集数量”一行；对标 Longpre et al. EMNLP 2021（NQ-Swap 原始实体替换设定）、Goyal ICLR 2025、Minder ICLR 2025（多冲突数据集）
- **问题（一句话）：** 在自然问题 + 维基百科段落的实体替换冲突（NQ-Swap）上，Flan / FLAN 是否同样只提高 “Question: … Answer:” 线索下的上下文采信，而不提高 “Q: … A:” 线索下的？
- **设置：**
  - 数据：`pminervini/NQ-Swap` dev（4746 条）；去 HTML 标签；以替换答案首次出现处为中心截取 120 词窗口；替换答案不在窗口内或原答案出现在窗口内的条目剔除（检查：保留 4727 条，剔除 19 条原答案泄漏）。
  - 单元：QA = 段落 + “ Question: q Answer:”；QA_short = 段落 + “ Q: q A:”；novel = 段落 + “ Query: q Response:”；closed = “Question: q Answer:”（无段落，用于判定是否已知）。
  - 读数：采信边际 = lp(替换答案) − lp(原答案)（E30 的 lp 函数，DataDecide 用 EOS、OLMo 2 用 BOS 作为起始 token）。**主读数：** 线索效应 = margin(QA) − margin(QA_short)；次读数：margin(QA) − margin(novel)、各单元水平。
  - 条目：6 个模型共同已知的条目（closed 上 lp(原) > lp(替换)）；若 < 100 条，退回全部条目（跑前固定的规则）。
  - 模型：(i) DataDecide 1B dolma1_7 vs dolma1_7-no-flan × 3 seed（最终步）；(ii) OLMo 2 1B：stage2 三个中期训练成分的最终步 vs stage1 最后三个 checkpoint（同 E30 Part A）。
  - 脚本：`scripts/e49_nqswap.py`。
- **阳性对照：** 上下文起作用：所有模型的 QA 水平 > 0（采信边际为正，即模型确实读了段落）；否则读数无效。
- **噪声地板 + MIE：** SE = √((var_with + var_without) / 2) × √(2/3)（每边 3 个）；Δ > 2·SE。
- **混杂审计：** NQ 问题为自然问句，无陈述句版本 → 用 “Q:/A:” 线索作对照（E32 已证明它不触发开关）；截窗规则固定；已知条目规则跑前固定；OLMo 2 的 stage1 与 stage2 还有其他数据差异（E30 已讨论），以“问答线索特异性”作为判据。
- **决策表（跑之前写）：**
  - 两个训练栈中 Question_vs_Q 的 Δ 都 > 2·SE → C04 扩展到第 3 个数据集（3 数据集 × 2 训练栈）。
  - 只有一个训练栈显著 → 如实写明。
  - 都不显著 → NQ-Swap 上不复现；检查 QA 水平差异，写进局限（可能与长段落 / 自然问句有关）。
- **算力预算：** 12 个模型 × 约 8 分钟 ≈ 2 GPU·时　**实际：**

## 结果（跑完后填写）
