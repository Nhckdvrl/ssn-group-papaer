# E06：Oracle bottleneck ladder / regime identification（2026-10-02）

- **状态：** PLANNED
- **类型：** EXPLORE
- **对应：** I03
- **问题（一句话）：** goal distance、data support、candidate budget 改变时，end-to-end failure ceiling 是否会在 representation/metric、dynamics、proposal、horizon/target 四层之间出现可复现迁移？
- **设置：** 仅在 E01/E02 可信后。先 2 个任务 × 3 个 goal-distance bins × 2 search budgets；LeWM baseline + 至多一个已有 geometry intervention + 一个 dynamics intervention + 一个 proposal intervention（只在已有可靠 checkpoint 时加入），避免全 Cartesian product。
- **读数：** candidate-set oracle ceiling；encoded-real endpoint rank；predicted endpoint rank；true-dynamics scoring（可用环境）；nearby-ground-truth subgoal diagnostic；closed-loop success；goal distance；candidate margin；data support；compute。
- **阳性对照：** 人为把 candidate budget 极低应暴露 proposal ceiling；极近 goal/真实 dynamics 条件应降低 horizon/dynamics负担；这些 sanity check 不成立则 decomposition 不可信。
- **噪声地板 + MIE：** pair/episode bootstrap + train-seed variance；failure signature 只有在 oracle replacement 带来超过 repeated-eval floor 的 success/regret改善时才标为该层 bottleneck。MIE 在 E02 后冻结。
- **混杂审计：**
  - goal-distance bins 用 environment/native distance，不用模型自己的 metric 定义；
  - intervention compute/model-call 与 wall-clock 都报告；
  - native protocol 与 common protocol 分表；
  - one intervention 不同时改变多个层时需标 mixed；
  - true-dynamics only where reset/replay valid；
  - nearby subgoal 是 diagnostic，不当 deployable method；
  - 不按结果重新划 bin。
- **决策表（跑之前写）：** 少数 observable variables 能跨任务预测 signature/intervention ranking → E07；只有 per-task arbitrary pattern → I03 PARK；一个 bottleneck始终主导 → 收敛到该层并生成更窄 idea；oracle ladder不稳定 → 修 measurement。
- **算力预算：** 先复用 checkpoint 进行 evaluation；每格独立 job，但先 fractional grid，只有观察稳定后扩 seeds/tasks。　**实际：** 待运行

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
- 数字（含 CI / 种子方差）：未运行
- 结果文件：待生成
- 按决策表执行了什么：待运行
- 主张变化：无
- POST-HOC 分析：无