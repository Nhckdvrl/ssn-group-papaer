# 实验入口

**2026-10-21：完成E01首次真实基线与E02普通恢复，共245次模型请求，独立故事仍为4。** 不复用、执行或重编号旧矿区A的实验。

| 实验 | 状态 | 实际交付 |
|---|---|---|
| [E01](E01-scope-aware-character-edit-baseline-gate.md) | DONE | Qwen3-8B、Llama-3.1-8B-Instruct、Step5各60请求；Step另1次预算恢复；[结果与分析](../results/e01/REPORT.md) |
| [E02](E02-same-information-controls.md) | DONE | Qwen 64调用，比较去原卡、一句提示、完整卡重写；[结果与分析](../results/e02/REPORT.md) |

[scope_edit_pilot](scope_edit_pilot/README.md)保留原V1/V1.1材料与双轨评分；新增runner、离线复算及全量台词入口。模型原始响应无损压缩，凭证和权重不入Git。C01/C02仅L0；台词审查不是独立真人评测，不把合成规则不匹配自动判为能力失败。
