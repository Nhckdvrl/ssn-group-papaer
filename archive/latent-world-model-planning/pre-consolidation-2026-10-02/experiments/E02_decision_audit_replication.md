# E02：Decision-Metric Alignment replication / downstream decision calibration（2026-10-02）

- **状态：** PLANNED
- **类型：** REPRO
- **对应：** I04；为 I06 / I03 提供 shared downstream measurement
- **问题（一句话）：** 在复现的 LeWM-family stack 上，能否稳定测到 random / mid-CEM / elite candidate 的 latent↔real ordering，并把 metric、rollout、selection、planning protocol 四层拆开？
- **设置：** E01 通过后的固定 checkpoint；优先 TwoRoom + PushT/Cube。每个 start-goal记录 random candidates、CEM中间迭代、elite candidates；对预注册 subsample做 simulator restore/replay。按 Decision-Metric Alignment 原定义实现 Plan-Real / CEM-stage Spearman，同时增加 encoded-real endpoint 与 predicted endpoint score。
- **读数：**
  - pair-level Spearman rho（random/mid/elite）；
  - undefined rho比例；
  - candidate margin；
  - real task utility；
  - encoded-real endpoint score；
  - predicted endpoint score；
  - ranking flips；
  - fixed-pool selected regret；
  - restore variance；
  - planning horizon H、execution/replanning prefix K、scoring time index / cost aggregation。
- **阳性对照：**
  1. 对真实 utility做严格单调变换，rank metric不应变；
  2. 打乱 candidate-cost pairing 后 rho 应接近随机基准；
  3. same candidate replay 的 environment utility在重复波动内一致；
  4. H>K 时至少跑一个 terminal-at-H vs prefix-at-K / running-cost protocol sanity，防止 P57 time-index mismatch被误当model failure。
- **噪声地板 + MIE：** bootstrap unit是 start-goal / planning decision，不把数千 candidates当独立 n。相同 pool 重复评估得到 rho / regret floor。MIE在第一次 pilot 后、任何新 mechanism experiment前冻结。
- **混杂审计：**
  - candidate pool固定后再比score；
  - random/mid/elite来源与数量记录；
  - utility方向统一；
  - 不跨模型直接比未归一化 latent MSE；
  - encoded-real / predicted endpoint 使用相同 encoder/preprocess；
  - privileged state仅diagnostic；
  - goal distance分层；
  - H/K/action block/frameskip/replanning/scoring-index写进manifest；
  - native paper protocol 与 common audit protocol分表。
- **决策表（跑之前写）：**
  - known stage-dependent alignment能稳定测 → I06 downstream measurement / E06可用；
  - random可测但elite样本不足 → 加 start-goal pairs，不换metric；
  - known effect完全测不到 → 核原论文 protocol / goal definition / utility；
  - time-index control本身造成巨大差异 → 先固定protocol再解释model；
  - 只有post-hoc选样本才出现 → 不继续。
- **算力预算：** 复用 E01 checkpoint；主要单GPU evaluation，可拆 eval manifests；真实 candidate execution先subsample再按CI扩。  
- **实际：** 待运行

## 结果
未运行。