# CVPR 2027 评估 — SUPERSEDED

**原评估日期：2026-09-29　｜　状态更新：2026-10-02**

> **本文件不再代表当前执行计划。** 原版全文仍在 git history 中。2026-10-02 人审后，`video-world-model-temporal-interfaces` 从 ACTIVE-MAIN 降为 PAUSED。

## 为什么 supersede
旧评估把“分块因果生成的接缝是控制盲区”判断为可扩成 CVPR 主线，并计划继续：
- 扩到 ≥5 个系统；
- 扩大场景/seed；
- 调 overlap/context-anchor repair；
- 用真人短按和位姿漂移强化 downstream consequence。

进一步领域调查改变了这个判断：
1. **ActionSplice (2609.08230)** 已拥有 chunk-autoregressive model 的 in-flight action responsiveness / retargeting 宽故事。
2. **Causal Forcing (ICML 2026)** 已拥有 bidirectional teacher → AR student architectural gap。
3. **ForgeWM (2608.14022)** 已公开 Stage 0–3 并做 stage-wise inference ablation。
4. 当前 seam repair 本身不是新方法，而且有 control trade-off。
5. 即使把 seam 复现规模继续做大，scientific question 仍可能被 reviewer 压缩成一个特殊 temporal/serving bug。

## 现在如何使用旧结果
保留所有 E01–E31 数据、脚本和 harness，但只作为：
- action temporal fidelity probe；
- causalization stage-localization diagnostic；
- serving/chunk counterfactual；
- 新主线中 capability-specific effect 的一项证据。

**不要继续执行旧 P0/P1/P2 的扩系统路线，除非新主线的实验决策表明确需要。**

新主线：[`../real-time-causalization-capability-preservation/`](../real-time-causalization-capability-preservation/)
