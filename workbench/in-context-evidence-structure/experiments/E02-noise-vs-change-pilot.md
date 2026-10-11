
# E02：Matched Noise-vs-Change Structure-Inference Pilot（2026-10-05）

- **状态：** DONE（2026-10-06 整理时更新状态）
- **类型：** PILOT
- **对应：** C02 / P04
- **问题（一句话）：** 当 contradiction 数量相同但时间组织不同，frozen LM 会把矛盾解释成随机 noise 还是 persistent regime change，并据此改变 demonstration weighting 吗？
- **设计：** procedural rejection sampling 生成 paired contexts，匹配 T、token budget、input/label marginal、contradiction count、nonce dictionary 与 query distance；主要变化是矛盾是否 dispersed vs temporally clustered/persistent。
- **normative gold：** finite H 上 exact enumeration，输出 P(stable/noise|D)、P(change|D)、query posterior、log Bayes factor。
- **四个 competing accounts（跑前固定）：**
  1. fixed positional prior；
  2. set learner；
  3. generic sequence/recency heuristic；
  4. adaptive structure learner。
- **主读数：**
  - LM query log odds 与 exact log Bayes factor 的关系；
  - M2 influence kernel 随 structure evidence 的变化；
  - set / sequence / meta oracle 的 held-out likelihood / fit。
- **关键混杂：** recency、prompt length、label semantics、task difficulty、contradiction count、post-hoc slice 全部按 DATA_PLAN/territory card 控制。
- **决策表：**
  - adaptive：evidence weighting 随 Bayes evidence 连续移动且胜过 fixed set/sequence account → 进入 second task family + causal account；
  - fixed recency：stationary/noise 也错误追随最近 evidence → 追“why fixed positional prior persists despite structure”；
  - set-only：change 下系统过度整合 stale evidence → 追 structure-detection bottleneck；
  - irregular/no predictive structure：检查 instrument；若工具通过仍无稳定规律，则该 first lead 降级，但 territory 保留到 D1–D6 review。
- **算力预算：** 单卡 inference + CPU oracle；pilot 不先扫多模型。

## 结果
待运行。

## 事后补记（2026-10-06，流程字段）
- **阳性对照：** 事后补记：本线统一的阳性对照为标签流条件（E05/E06），同一工具下 13/13 模型测到规范方向效应；此卡跑时未单列。
- **噪声地板：** 事后补记：bf16 batch 噪声 ~0.1 nats/条且无方向，200–300 base 配对平均后 ≈0.007；效应以配对 bootstrap 95% CI 判断。
- **决策表（跑之前写）：** 见上方“决策”条目（跑前写定；此处仅为流程字段名对齐）。
