# E02：Decision-Metric Alignment 复现与 oracle-ladder 校准（2026-10-02）

- **状态：** PLANNED
- **类型：** REPRO
- **对应：** I04；为 I02/I03 的 measurement calibration
- **问题（一句话）：** 在我们复现的 LeWM stack 上，能否按 Decision-Metric Alignment 的定义可靠测到 random / mid-CEM / elite candidate 的 latent↔real ordering，并把 representation/rollout/selection 三层拆开？
- **设置：** E01 通过后的固定 checkpoint；优先 TwoRoom + PushT/Cube。每个 start-goal 记录 random candidates、CEM 中间迭代、elite candidates；对可承担的小样本候选做 simulator restore/replay。按论文原定义实现 Plan-Real/CEM-stage Spearman，同时增加同一 candidate 的 encoded-real endpoint 与 predicted endpoint cost。
- **读数：** pair-level Spearman（random/mid/elite）；Spearman undefined 比例；candidate margin；(C_{real-latent})、(C_{pred-latent})、真实 task utility；ranking flips；fixed-pool selected regret；restore variance。
- **阳性对照：** (1) 对同一真实 task utility 单调变换，rank metric 不应改变；(2) 人为打乱 candidate-cost 配对后 Spearman 应接近随机基准；(3) 相同 candidate replay 的环境 utility 在重复波动范围内一致。
- **噪声地板 + MIE：** bootstrap 单位是 start-goal pair/episode，不把数千 candidates 当独立 n；先量化同一 pool 重复评估的 (ho) 与 regret 波动。MIE = 足以改变“继续 I02/I03 还是只保留 diagnostic”的差异，数值由 E01/E02 pilot CI 决定并在首次运行日志中冻结。
- **混杂审计：**
  - candidate pool 固定后再比 score；
  - random/mid/elite 的 candidate 数与来源记录；
  - task utility 方向统一（越高/越低）；
  - 不跨模型直接比较未归一化 latent MSE；
  - true endpoint 与 predicted endpoint 使用相同 encoder/preprocessing；
  - simulator privileged state 仅 diagnostic；
  - goal distance/horizon 分层保存，避免 Simpson effect。
- **决策表（跑之前写）：** 已知 stage-dependent alignment pattern 可稳定测量 → E03/E05/E06；只有 random 可测、elite 样本不足 → 增加 pair 数而非改 metric；已知 effect 完全测不到 → 核对原论文 protocol/goal definition/utility；只能靠 post-hoc 选样本才出现 → 不继续。
- **算力预算：** 主要复用 E01 checkpoint；单 GPU evaluation，可跨独立 eval seeds/episodes 分派；真实 candidate execution 先 subsample，按 CI 决定扩展。　**实际：** 待运行

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
- 数字（含 CI / 种子方差）：未运行
- 结果文件：待生成
- 按决策表执行了什么：待运行
- 主张变化：无
- POST-HOC 分析：无