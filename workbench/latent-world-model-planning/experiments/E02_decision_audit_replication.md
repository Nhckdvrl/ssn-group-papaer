# E02：Known decision-alignment replication / measurement calibration（2026-10-02）

- **状态：** PLANNED
- **类型：** REPRO
- **对应：** I04；为 I01/I03 提供 measurement calibration
- **不是 novelty：** DA-LeWM 已有 Plan-Real / CEM-stage alignment；AD-WM 已有 elite-regret / counterfactual-action diagnostics；Objective Is the Bottleneck 已证明“信息存在但 planning objective 不会用”。

## 问题

在我们复现的 LeWM/TD-JEPA stack 上，能否可靠复现：
1. random → mid-CEM → elite candidate 的 latent↔real ordering；
2. encoded-real endpoint vs predicted endpoint 的差；
3. candidate margin / action discrimination / selected regret；
从而证明后续 oracle ladder 的 instrumentation 能测到已知问题？

## 设置

E01 通过后的固定 checkpoint；优先：
- TwoRoom；
- PushT 或 Cube 一个 contact-rich task。

每个 start-goal 保存：
- random candidate pool；
- CEM 中间 stage；
- final elite；
- selected candidate；
- stratified subset 的 simulator replay。

**planning protocol 固定写全：** horizon (H)、receding prefix (K)、action block、score time index、terminal/prefix/running cost。首轮先用 native setting；另做一个 P57-style protocol sanity，不把它混入“模型 alignment”。

## 读数

- Plan-Real Spearman / Kendall（按原文定义优先）；
- stage-wise rank correlation；
- undefined-correlation pair 比例；
- candidate margin；
- action-separation margin（有定义时）；
- (C_{mathrm{real endpoint}})；
- (C_{mathrm{pred endpoint}})；
- environment task utility；
- predicted→real ranking flips；
- fixed-pool selected regret；
- replay variance；
- protocol sensitivity: terminal@H vs prefix@K/running（sanity only）。

## 阳性对照

1. 对真实 task utility 做严格单调变换，rank metric不变；
2. 打乱 candidate-cost pairing，rank接近随机基准；
3. 相同 candidate replay 的 utility落在重复波动范围；
4. 在 (K<H) setting，人为比较 terminal@H vs prefix@K，instrumentation 必须能记录 score-index change，不要求每任务都复现 P57 的巨大数值。

## 噪声地板 + MIE

- bootstrap unit = start-goal / planning decision，不把 candidates当独立 n；
- 同一 pool repeated replay量化 rank/regret floor；
- Spearman undefined必须计数；
- MIE = 足以决定 “instrumentation已校准，可进入 E03/E06” 的差异，不把 E02 本身升级 science claim；
- 首次运行前根据 E01 repeat数据冻结阈值。

## 混杂审计

- candidate pool固定后再比较 score；
- random/mid/elite candidate来源和数量都保存；
- task utility方向统一；
- true/pred endpoint用同 encoder/preprocess；
- simulator state只进 diagnostic；
- goal distance / H / K / action block分层；
- 不跨模型直接比未标准化 latent MSE；
- protocol sanity 与 model comparison分表。

## 决策表

- 已知 stage-dependent alignment / ranking diagnostics可稳定测量 → 开 E03（I01）与 E06（I03）；
- random可测但 elite样本退化/全 tie → 增加 start-goal/candidate coverage，不换 metric追显著；
- known effect完全测不到 → 核对原论文 protocol、goal/task utility与 replay；
- 只有 post-hoc挑 episode才有 gap → measurement gate失败，不开始新 mechanism claim。

- **算力预算：** 复用 E01 checkpoint；evaluation为主；candidate replay 先 stratified subsample，按 CI扩。单 GPU独立 episode groups可并行。  
- **实际：** 待运行

## 结果
未运行。