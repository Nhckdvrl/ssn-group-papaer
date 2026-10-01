# E06：Oracle bottleneck ladder / regime identification（2026-10-02）

- **状态：** PLANNED
- **类型：** EXPLORE
- **对应：** I03
- **问题（一句话）：** 在 protocol先对齐后，goal distance、candidate margin、planner-reachable fidelity、action discrimination 等变量是否能预测 end-to-end failure 的 binding layer（Q/R/D/A/P/H）？
- **前置：** E01/E02 measurement可信；没有 calibrated replay/rank，不运行。

## 初始 fractional design

首轮：
- 2 tasks：topology/navigation + contact-rich；
- 3 goal-distance bins；
- 2 candidate budgets；
- LeWM baseline；
- 先不加所有方法。

goal distance 用 environment/native可解释单位；若任务没有 exact distance，使用预注册 proxy/bin并写限制。

## Step 0 — protocol gate Q（必须先过）

同 frozen checkpoint / same starts:
- terminal@H；
- prefix@K（若 (K<H)）；
- running / trajectory cost；
- 明确 (H,K)、action block、primitive-step horizon、replanning interval。

若 P57-style time-index correction足以救 failure，则先标：
```text
Q = protocol/query-interface limited
```
并在对齐 protocol 后才继续归因 model layers。

## Oracle ladder

对 fixed candidate pool / same start-goal：

1. **Candidate-set oracle:** pool中真实最好 candidate → proposal ceiling。
2. **Encoded-real endpoint metric:** 去掉 learned rollout error → R/metric ceiling。
3. **Predicted endpoint:** 与 2 对比 → D/rollout contribution。
4. **Counterfactual action separation diagnostic:** elite actions是否产生可区分 predicted futures；有 AD-WM/PhyLatent-style可用指标时测 A。
5. **True-dynamics scoring:** simulator rollout替 model → D vs metric/search。
6. **Nearby true/recorded subgoal:** 只作 H/target-interface diagnostic。
7. **Planner-reachable fidelity:** 只有需要解释 P layer时调用 E05，不自动跑。

## Failure signature

- **Q** protocol / score-time / replanning interface
- **R** representation / planning metric
- **D** dynamics / rollout
- **A** counterfactual action discrimination
- **P** proposal / finite-budget search
- **H** horizon / target abstraction
- **M** mixed / unidentifiable

**标层规则：** oracle replacement带来的 paired success/regret改善必须超过 E02 repeat floor并有 bootstrap stability；多个 replacement一起才救则标 M，不强分。

## 读数

- success / task-native cost；
- fixed-pool oracle ceiling；
- encoded-real rank；
- predicted rank；
- candidate margin；
- action-discrimination margin；
- true-dynamics rank/selected regret；
- goal distance；
- (K/H)、action block；
- candidate budget；
- planner-reachable fidelity（conditional）；
- compute/model calls/wall-clock。

## 阳性对照

- 极低 candidate budget → 应降低 candidate-set oracle ceiling / 暴露 P；
- (Kll H)+terminal@H 的 known setting → instrumentation能暴露 Q；
- intentionally degraded predictor → D；
- known/constructed action-insensitive model or action-shuffle control → A；
- far goal + short horizon → H pressure应上升；
- 若这些都识别不出，oracle ladder无效。

## 噪声地板 + MIE

- episode/start-goal paired bootstrap；
- train-seed variance另报；
- signature只有 replacement effect > repeat floor 才赋标签；
- regime variable阈值不能用 test最优切点选择；先 exploratory连续曲线，confirmatory用held-out threshold/model。

## 混杂审计

- native protocol与 common protocol分表；
- H/K/action-block转换到 primitive env steps；
- goal bins跑前冻结；
- true-dynamics only where restore/replay validated；
- nearby subgoal不当 deployable method；
- different repo method不能直接放同 factorial，除非共同 protocol等价验证；
- privileged state只 diagnostic；
- compute/model calls + wall-clock都报；
- 不按结果重新定义 failure signature。

## 决策表

- 少数 variables跨任务预测 Q/R/D/A/P/H且 intervention ranking随之切换 → E07；
- Q 占大部分 → 先在 protocol-aligned setting重复其它 layers；若仍能提出超越 P57 的一般 law才考虑 paper；
- 一个非 Q layer始终主导 → 停大 map，收敛到该 layer的新 idea；
- 每任务各有一套阈值 → I03 PARK；
- signature不稳定 → 修 harness，不加模型。

- **算力预算：** 先复用 checkpoint做 fractional evaluation；每格独立 job；只有稳定后加 train seeds / methods。  
- **实际：** 待运行

## 结果
未运行。