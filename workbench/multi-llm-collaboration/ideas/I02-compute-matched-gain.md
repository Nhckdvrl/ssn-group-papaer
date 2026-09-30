# I02：训练型 LLM 团队的 performance–compute accounting（2026-10-01）

- **状态：** SEED
- **角色：** 全线公平比较基础设施；默认不是独立论文。
- **来源：** MARTI 等训练型 MAS 报告收益，而 equal-inference-cost / SAT 等工作已经把 strongest-member、compute-matched inference、router baseline 推成必须面对的对照。
- **研究动作：** 强基线翻案 + 评测协议。

## 关键修正

不再把“等 generated tokens 的一个点”叫作等算力。多模型团队的成本至少要同时看到：
1. LM calls / sample；
2. input / output tokens；
3. active-parameter-token 或可复现的近似 FLOPs；
4. training GPU·h；
5. inference GPU time；
6. wall latency（串行/并行策略写清）。

目标是画 **performance–compute Pareto curve**，而不是找到一个对我们有利的 matched point。

## 最近邻与边界

| 近邻 | 已有结论 | 我们的作用 |
|---|---|---|
| MARTI | 训练后团队在其预算定义下可优于单智能体 | 用统一 accounting 复核不同 training substrate |
| At Equal Inference Cost (2609.04217) | frozen-backbone prompt team 在等 LM-call 预算下没有清晰优势 | setting 不同，但已占“公平算力很重要”这个 claim |
| SAT (2609.22682) | 报告 strongest member、compute-matched inference、perfect router 等对照 | 把这些 baseline 作为最低公平性标准之一 |

## Pilot

在 E01 跑通后，至少保存：
- team performance；
- 未训练 team；
- 单模型 RL baseline；
- stronger single model（关键点即可）；
- self-consistency / repeated sampling；
- 上述 6 类 compute 指标。

不预先要求“team 必须赢”。若团队只有在某一种 accounting 下看起来更强，这本身首先是 measurement/pain，而不是 paper conclusion。

## Information gain

I02 的主要价值是防止整个 workbench 建立在不公平 baseline 上，并给 I01/I03/未来方法提供可审计的 value claim。
