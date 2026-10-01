# Video World Model Temporal Interfaces — legacy diagnostic workbench

## 状态
**PAUSED（2026-10-02，人决定；H 类 scientific-yield judgment）。**

这条线不是因为“现象不成立”暂停。相反，块首 / chunk-seam control deafness 已在多个系统和严格相位平衡回放中得到支持。暂停原因是：**把 seam-specific failure 本身当作 MAIN paper question，尺度与领域当前真正付费解决的问题不匹配。**

新主线：[`../real-time-causalization-capability-preservation/`](../real-time-causalization-capability-preservation/)  
新 territory 卡：[`../../search/our-taste/TERRITORY_REALTIME_CAUSALIZATION_2026-10-02.md`](../../search/our-taste/TERRITORY_REALTIME_CAUSALIZATION_2026-10-02.md)

## 保留下来的可靠资产
- **块首失聪**：必须从新 chunk 第一 latent 开始生效的短控制变化会显著弱化、丢失或推迟；E31 在控制按键时长后仍复现。
- **阶段定位**：minWM / WorldPlay 的阶段对照把问题指向 causalization 之后，而不是 VAE/tokenizer；distillation 可进一步放大，但不是唯一来源。
- **阴性对照**：双向 teacher / SFT 与逐帧 Oasis 没有同样的 seam pattern。
- **诊断工具**：phase-balanced action replay、grid shift、短脉冲/阶跃、paired-noise probing、teacher/student stage comparison。
- **系统 harness**：MG2、minWM、HY-WorldPlay，以及 overlap / context-anchor 干预。

这些资产现在只作为新主线中的 **action temporal fidelity / stage-localization diagnostic**。

## 为什么不再作为独立 MAIN story
1. **Field relevance 太窄。** 近期 Video World Model 的 load-bearing capabilities 是 controllability / responsiveness、long-horizon memory、persistent state、real-time interaction、physics / geometry 与 functional utility。“第一个 latent 上的短按会丢”本身太像实现层 corner case。
2. **最近邻压缩。** ActionSplice 已把 chunk-autoregressive sampling 中途 action update / responsiveness 写成 field-level problem；ForgeWM 已公开 Stage 0→1→2→3 并做 stage-wise inference ablation；Causal Forcing 已拥有 bidirectional teacher → AR student architectural gap。
3. **当前 repair 不够强。** overlap/context-anchor 在 minWM 改善有限、WorldPlay 出现过度转动；画质与代价没有形成干净方法结论。

## 旧计划处理
**停止执行**旧 `CVPR_ASSESSMENT.md` 的“扩到 ≥5 个系统 + 把 seam repair 调成论文”路线。

只有满足下面任一条件才继续 seam-specific 实验：
- 新主线需要它区分 architecture / few-step / self-rollout / serving 的贡献；
- 新 stage checkpoint 提供真正可归因的反事实；
- seam effect 被证明直接导致 persistent state、closed-loop objective 或真实 control fidelity 失败。

## 重新作为独立 workbench 的条件
需要新的 field-level consequence，而不是“更多系统复现”：真实 closed-loop / long-horizon consequence，或跨 lineage 的统一训练机制 + 自然的最小修复，并且明确越过 ActionSplice / ForgeWM / Causal Forcing 的 compression boundary。

## 资产位置
- `CLAIMS.md`：旧实验主张账本
- `CVPR_ASSESSMENT.md`：已 superseded 的历史评估
- `PAIN_LOG.md`、`experiments/`、`scripts/`、`analysis/`、`results/summary/`
- 大模型 / cache / 原始视频继续保存在本地，不进 git

## 决策记录
- 2026-09-29：seam-specific story 被选为 CVPR 2027 主线。
- **2026-10-02：人审后 PAUSED。** 现象可靠，但 scientific question 尺度偏小；新的最近邻改变了 ownership；继续堆 seam-specific scale 的信息增益低于转向 real-time causalization capability preservation。
