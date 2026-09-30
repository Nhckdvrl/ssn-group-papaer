# E01 — Pythia-70M induction baseline reproduction

- **状态：** PLANNED
- **对应：** D1/D2；验证 mechanism measurement instrument，不支持 population novelty
- **问题：** 我们能否在一个 canonical Pythia-70M training trajectory 上复现已知 induction behavior / mechanistic score / causal-ablation effect，并沿训练阶段得到可解释的 trajectory？
- **模型：** Pythia-70M canonical run；exact repository/revision/checkpoints 在 R0 artifact audit 后冻结
- **任务 / 样本：** 优先复用 parent measurement 的输入构造；另保留 held-out prompts
- **主要读数：** behavioral induction metric；head/component score；causal ablation effect；checkpoint trajectory
- **阳性对照：** 在 parent 文献明确存在 induction signal 的 late checkpoint 上，measurement 与 causal ablation 应检出预期方向的效应
- **噪声地板 + MIE：** 先用重复输入抽样 / held-out prompts 估计 measurement 与 ablation uncertainty；E01 的 MIE 是“足以确认 instrument 能复现 parent object”，不是新颖性阈值
- **关键混杂：** prompt construction；checkpoint revision；tokenization；head-score 定义；ablation implementation；artifact integrity
- **决策表（跑之前写）：** 结果 A（parent behavior + causal effect 可稳定复现）→ 冻结 harness，注册 E02 population sweep；结果 B（只复现相关性、因果 ablation 不复现）→ 优先修 instrument/parent matching，不进入 population claim；结果 C（artifact/checkpoint 异常）→ 记入 PAIN_LOG 并修 manifest；不确定 → 缩小到 parent exact setup，不扩大模型/任务
- **算力：** inference/activation/ablation only；70M；不得为了 E01 训练模型
- **输出：** accepted checkpoint manifest、可一键复跑脚本、raw per-prompt/per-head metrics、简短 baseline note
