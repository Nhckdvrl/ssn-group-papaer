# E02：comlrl-code-repro（2026-09-30）

- **状态：** PLANNED
- **类型：** REPRO（第二个基底：代码协作，支持从 0.5B 起步，另有 Minecraft 环境）
- **对应：** D1/D2 baseline residency；第二个 open-weight substrate；只有在任务确实需要协作时才用于 I01 泛化
- **问题（一句话）：** CoMLRL 的 MAGRPO 在代码协作（HumanEval / MBPP / CoopHumanEval）上能否以 Qwen2.5-0.5B→1.5B 复现 README 报告的趋势？
- **设置：** `pip install comlrl`，官方配置；2 智能体；Qwen2.5-0.5B 先跑通，再 1.5B；2 个种子
- **读数：** pass@1；训练曲线；协议中可定义的成员贡献；LM calls、tokens、近似 FLOPs、GPU time、wall latency。先确认 CoopHumanEval/任务构造是否真正产生 inter-agent dependency，避免把可独立完成的代码题误当 coordination substrate。
- **阳性对照：** 单智能体基线与 README 报告的起点一致
- **噪声地板 + MIE：** 同一 checkpoint 3 次采样评测的波动；若用于 cross-play，另在 pilot 前定义足以改变 substrate/partner-axis 决策的 MIE
- **混杂审计：** 训练集与评测集分开（CoopHumanEval 的构造方式先读清楚）；不筛种子
- **决策表（跑之前写）：** 结果 A（复现趋势且任务有真实 inter-agent dependency）→ 可作为 I01 的第二 substrate；结果 A2（复现趋势但任务可由单 agent 基本独立完成）→ 只保留为训练 baseline，不把 cross-play null 外推；结果 B（复现不了）→ 记痛点，查版本/配置，查不出则不作为主基底；不确定 → 加必要的 reproduction seed / task audit
- **算力预算：** 0.5B 与 1.5B 各一次单节点训练（以实测 GPU·时为准）　**实际：**

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
