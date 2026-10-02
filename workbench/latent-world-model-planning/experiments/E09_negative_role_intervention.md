# E09：Do heuristic negatives help because they are semantically correct?（2026-10-02）

- **状态：** PLANNED
- **类型：** PILOT
- **对应：** I06
- **前置：** E08 显示非微小、稳定的 semantic contamination，且 oracle/certification coverage足够。
- **问题（一句话）：** cross-trajectory negatives 的 planning增益来自正确的 reachability/distance semantics，还是来自 pair-count、repulsion、scale、dispersion等非语义 regularization？
- **设置：** 首轮 TwoRoom；优先 TD-JEPA（已有 official hinge-off baseline）+ RC-aux。每个 method做 paired variants，训练 budget/init/data匹配：
  1. **FULL**：原方法；
  2. **NO-XNEG**：去掉 cross negative term；
  3. **ORACLE-VALID**：仅对 certified semantic negatives施加原 negative loss；
  4. **ORACLE-CENSOR**：false/unknown cross pairs不作为 semantic negative；
  5. **COUNT-MATCHED VALID**：若 valid negatives少，重采/重权使 negative exposure与 FULL近似，分离标签正确性与负样本数量；
  6. **REPULSION-CONTROL（条件）**：不对具体 pair 声明 unreachable/far，只加入 matched-strength global dispersion/uniformity/scale regularizer；具体形式必须在 E08 后、第一条训练命令前写 amendment，不能事后挑最有效公式。
- **读数：**
  - semantic negative precision/calibration；
  - TD distance / reachability calibration to oracle；
  - latent/head scale、effective rank、pairwise dispersion；
  - negative-loss gradient norm，必要时区分 shared encoder/head；
  - same fixed candidate pool 的 random/mid/elite rank；
  - candidate regret、selected-action flip；
  - closed-loop success；
  - one-step/rollout prediction作 guard，不作主 outcome。
- **阳性对照：**
  - FULL vs NO-XNEG 先复现 TD-JEPA published direction；若组件作用方向都复制不了，先修 protocol；
  - ORACLE-VALID pairs 在可判 oracle 区域 semantic precision应接近1；
  - COUNT-MATCHED 的 total negative weight/exposure与 FULL可比较。
- **噪声地板 + MIE：**
  - 先1 train seed做 mechanism gate，随后才3+ train seeds；
  - candidate metrics bootstrap by start-goal；
  - success报告train-seed variance与paired episode CI；
  - 只有 calibration变化且decision null，不升级。
- **混杂审计：**
  - optimizer steps、positive exposure、rollout loss、SIGReg固定；
  - oracle只影响诊断 upper-bound pair selection，不能成为最终 deployable method；
  - count-match避免“过滤后只是loss变小”；
  - gradient/scale matching预注册；
  - TD-JEPA plan-time cost固定，不因variant临时换 temporal cost / L2；
  - RC-aux training-only与planner gate分开；
  - validation调参，test不调。
- **决策表：**
  - ORACLE-VALID > FULL 且 calibration+decision同步改善 → semantic false negatives在伤害；进入E10寻找无oracle过滤；
  - FULL > ORACLE-VALID，但 REPULSION-CONTROL恢复 → negative主要load-bearing作用是非语义geometry regularization；E10做 role separation；
  - COUNT-MATCHED VALID≈FULL且 calibration更好 → sample quantity是关键，语义过滤可行；
  - FULL/NO-XNEG差异复制不出 → I06暂停，先复现；
  - all variants decision≈noise → I06 PARK。
- **算力预算：** E00实测后填写；首轮TD-JEPA先 FULL/NO/ORACLE-VALID/COUNT-MATCHED，不一次铺满两方法×六variant。每run单GPU，可并行但数据先node-local。  
- **实际：** 待运行

## 结果
未运行。