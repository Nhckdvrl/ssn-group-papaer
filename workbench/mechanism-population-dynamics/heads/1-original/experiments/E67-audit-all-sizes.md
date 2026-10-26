# E67：1B 以下所有尺寸的初始化核查与 checkpoint 记录（2026-10-06）

- **状态：** DONE（2026-10-06）
- **类型：** CLAIM（评审意见“document the DataDecide checkpoints below 1B”；原稿写“we confirm every run's initialization from its released weights”，实际只有 1B 做了训练起点核查）
- **对应：** P12（1B 有 6 个 run 的初始化与标签不符）；C05；论文 Table 1 / Table sizes / App. A
- **问题（一句话）：** 4M–750M（以及 1B@7500 的 5 个 seed、1B 最终步的全部 75 个 run）中，论文用到的每个 run 是否真的从其 seed 标签对应的初始化开始训练？每个尺寸用的是哪个 checkpoint（步数、占训练比例）？
- **设置：**
  - 已有前提：`survey_all_sizes.json`（每个 repo / seed 的 step0 safetensors 哈希与步数列表；E45 只选了三个 seed 共享 step0 的配方）。
  - 新核查：对 E45 / E35 用到的每个 (尺寸, 配方, seed)，用 HTTP range 读取最早训练 checkpoint（step > 0 的最小步）与论文所用 checkpoint 的同一组张量（各 block 的 att_proj，至多 4 个 block，加 block 0 的 ff_proj），与每个 seed 的参照 step0（该尺寸、该 seed 最常见哈希的配方）求 Pearson 相关。
  - 脚本：`scripts/e67_audit_sizes.py`（CPU + 网络）。
- **读数：** (1) 每个 run：最早 checkpoint 与自己 seed 的 step0 相关 vs 与其他 seed 的 step0 相关的最大值；(2) 论文所用 checkpoint 与各 seed step0 的相关（同时作为 E68 的“初始化权重” baseline）；(3) 每个尺寸的 checkpoint 记录表：步数、占训练比例、seed、配方数。
- **阳性对照：** 1B 的 C4 / Dolma 1.7 / DCLM（已知 0.23 vs 0.000）；1B 的 6 个未核实 run 必须被判为不符（已知）。
- **噪声地板：** 不同 seed step0 之间相关 ≈ 0（独立初始化）；判“从自己 seed 开始”= 自己 seed 的相关 > 其他 seed 最大值的 5 倍且 > 0.02。
- **混杂审计：** 小尺寸最早 checkpoint 在训练的 10–22%（4M 为 1250 / 5725），相关会弱于 1B 的 3.6%——以其他 seed 为参照判定（已控制）；只读部分张量（写明）。
- **决策表（跑之前写）：** 全部符合 → 附录写“所有尺寸的训练起点核查一致”，并列 checkpoint 表；发现不符的 run → 与 P12 同样处理：从所有比较中排除并重算 E45 / E61 / E60 受影响尺寸，在论文中报告数量。
- **算力预算：** CPU + 网络，约 1000 次 range 读取　**实际：**

## 结果（2026-10-06；`results/e67/<size>.json`）
- 阳性对照 ✓：1B 最终步 75 个 run 中恰好标出 P12 的 6 个（最早 checkpoint 与任何 seed 的 step0 相关 0.000）；1B@7500 标出 fineweb-pro / small-aux-2（E45 已按 step0 哈希排除的那个）。
- **4M–750M 全部 636 个 run（13 个尺寸）都从其 seed 标签对应的初始化开始训练：** 最早 checkpoint（step 1250，1B 为 step 2500）与自己 seed step0 的相关 0.05–0.41（随尺寸增大），与其他 seed 的最大相关 ≤ 0.009；无读取错误。
- 论文所用 checkpoint 与自己 seed step0 的相关：0.014–0.074（小尺寸）、0.03–0.06（60M–750M）、0.03–0.05（1B 最终步），其他 seed ≤ 0.01 → “权重与初始值只剩 0.03–0.09 的相关”本身仍足以认出初始化（交给 E68 定量）。
- checkpoint 记录（论文所用步数 / 占训练比例）：4M–90M 为最终步；150M 37,500（98%）、300M 45,000（98%）、530M 51,250（89%）、750M 27,500（43%）、1B@7500 7,500（11%，5 个 seed）、1B 69,369（最终步，3 个 seed）。→ 论文 Table sizes 需要加这一列（评审意见 2）。
- 按决策表：全部符合 → 附录写“所有尺寸的训练起点核查一致，只有 1B 的 6 个 run 与 1B@7500 的 1 个 run 不符（均已排除）”，并列 checkpoint 表。
- 主张变化：无（P12 的范围确认只限于已知的 7 个 run）。
