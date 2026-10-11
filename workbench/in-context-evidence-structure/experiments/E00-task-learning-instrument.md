
# E00：Nonce Rule Task Learning Instrument Validation（2026-10-05）

- **状态：** DONE（2026-10-06 整理时更新状态）
- **类型：** REPRO / INSTRUMENT
- **对应：** C00
- **问题（一句话）：** frozen open LM 能否仅凭 demonstrations 学会 episode-randomized hidden rule，并在 held-out input 上稳定泛化，从而给后续 evidence-structure 实验提供有效仪器？
- **模型：** 先只用本地 Qwen3-8B（固定 revision）；不要先扫模型。
- **数据：** DATA_PLAN 中 3-bit nonce attribute、6-hypothesis hidden rule generator；300–1,000 episodes；0-shot 与 4/6/8-shot；每 episode 随机 nonce attribute / label dictionary。
- **读数：** exact target-label logprob（优先）+ forced-choice accuracy；按 episode paired。
- **阳性对照：** few-shot 明显优于 zero-shot chance；held-out query 排除 literal copy。
- **反混杂：** nonce label polarity / attribute names 轮换；输入组合 held out；prompt wording 冻结。
- **噪声地板 + MIE：** bootstrap over episode seeds；另报 dictionary remap 方差。只有当 single-regime performance 留出足够空间，使 E01 的结构差异可分辨，才进入 E01；不使用事后挑 seed/字典。
- **决策表：**
  - A：few-shot 稳定学习且 remap 后保持 → 进入 E01；
  - B：任务饱和 → 增加 hypothesis class（conjunction/parity）后重新 E00；
  - C：接近 chance → 简化 task / 增加 informative demos；仍不进入结构结论；
  - D：对 nonce dictionary 极敏感 → 先修 instrument。
- **算力预算：** 单卡推理，预计 <1 GPU·h 级；以实测为准。

## 结果
待运行。

## 事后补记（2026-10-06，流程字段）
- **决策表（跑之前写）：** 见上方“决策”条目（跑前写定；此处仅为流程字段名对齐）。
