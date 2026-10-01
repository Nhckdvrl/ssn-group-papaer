# E07：Bottleneck interaction probe — geometry × dynamics × proposal（2026-10-02）

- **状态：** PLANNED
- **类型：** PILOT
- **对应：** I03
- **问题（一句话）：** E06 识别到的 regime switch 是否反映真实 load-bearing interaction，而不是单方法 ranking 或 protocol artifact？
- **设置：** 只在 E06 给出稳定 signature 后运行。选择 E06 中最能区分两个 regime 的 2 个 task/regime slices，做预注册 2×2：geometry×dynamics、dynamics×proposal 或 geometry×proposal 中**只选最有区分力的一组**；必要时第二组 confirmatory。方法选择来自 `EXPERIMENT_PROGRAM.md` 的 baseline gate。
- **读数：** paired success/regret；oracle-ladder signature；main effect / interaction effect；goal distance/support/margin；compute；训练/评测 seed。
- **阳性对照：** 在 E06 已知单个 intervention 有效的 slice 重现其 main effect；组合实验中的“关闭”配置必须回到同一 baseline。
- **噪声地板 + MIE：** ≥3 train seeds only after pilot supports effect；episode-level paired bootstrap + train-seed variance；interaction MIE = 足以改变“固定方法 vs regime-adaptive原则”结论的差异，数值在 E06 结果后预注册。
- **混杂审计：**
  - 组合方法训练步/数据/encoder initialization 匹配；
  - 不能把不同 repo 原生 protocol 的结果硬做 factorial；
  - compute/model-call budget 同时报；
  - hyperparameter 不在 test slice 调；
  - interaction analysis 预先定义，不事后挑最强 pair；
  - method implementation version固定；
  - failed runs不静默删。
- **决策表（跑之前写）：** interaction direction 与 E06 regime variable 一致且跨 ≥2 substrates → 生成 C## 并设计 adaptive/minimal intervention；只有 additive main effects → 不宣称 bottleneck relocation，保留 component evidence；interaction 每任务方向乱 → I03 PARK；baseline main effect复现失败 → VOID/回 E06。
- **算力预算：** E06 后填写；优先少量 2×2 confirmatory runs，不一次铺 3-way factorial；独立单 GPU并行。　**实际：** 待运行

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
- 数字（含 CI / 种子方差）：未运行
- 结果文件：待生成
- 按决策表执行了什么：待运行
- 主张变化：无
- POST-HOC 分析：无