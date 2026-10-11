# E07：Regime interaction confirmation（2026-10-02）

- **状态：** PLANNED
- **类型：** PILOT
- **对应：** I03
- **前置：** E06 必须先给出可复现的 predictive regime hypothesis；没有就不运行。
- **问题（一句话）：** E06 的 bottleneck relocation 是否是 load-bearing interaction，而不是单方法 leaderboard / protocol artifact？

## 设置

从 E06 预注册：
- 2 个能区分 regime 的 task/slice；
- 1 个最有信息增益的 2×2 interaction；
- 1 个 held-out task/slice 做确认（若成本允许）。

候选 interaction：
- metric/geometry × dynamics；
- dynamics × proposal；
- action-discrimination × proposal；
- metric × proposal；
- **不把 Q/protocol correction 当“方法开关”参与新颖性 factorial**；Q 必须先固定对齐。

方法只从 E06 已验证的 representative intervention选一个，不同时装一堆。

## 读数

- paired success / task cost / regret；
- E06 oracle signature；
- regime variable；
- main effects；
- interaction effect；
- intervention ranking；
- compute；
- train/eval seeds。

## 阳性对照

- 在 E06 已知 slice 复现单 intervention main effect；
- “off/off”回到同 baseline；
- protocol (H/K/score timing/action block)完全一致；
- oracle signature在重复 evaluation稳定。

## 噪声地板 + MIE

pilot先 1–2 train seeds；只有 interaction方向符合预注册 hypothesis才扩 ≥3 seeds。  
episode paired CI + train-seed variance分开。  
interaction MIE = 足以改变“一个固定方法 vs regime-aware rule”决策的量；在 E06 完成后、E07 首条训练命令前冻结。

## 混杂审计

- 组合方法数据、train steps、init匹配；
- 不把不同 repo 的 native protocol硬做 factorial；
- compute/model-call + wall-clock；
- hyperparameter validation-only；
- interaction pair跑前选择，不看 test；
- failed runs不删；
- held-out regime threshold不事后移动。

## 决策表

- interaction与 E06 regime variable一致，且 held-out slice/substrate也预测对 → 建 C##，尝试 practical adaptive/minimal intervention；
- 只有 additive gains → 不宣称 relocation law，保留 component evidence；
- interaction每任务方向不同 / threshold不泛化 → I03 PARK；
- baseline main effect复现失败 → VOID回 E06。

- **算力预算：** E06 后填；少量 2×2 independent single-GPU runs，不做 3-way full factorial。  
- **实际：** 待运行

## 结果
未运行。