# 领域地图：ICL 中的证据聚合（evidence aggregation in ICL）

**建立：** 2026-10-05（持续更新；每读一批论文就改这里，单篇深读卡在 `papers/`）

## 0. 一句话画像
ICL 研究在 2021–2026 形成了四条互相不太对话的线：
1. **“ICL 是 Bayesian 推断吗？”**（Xie 2022 → Falck 2024 martingale → Arora 2024 Bayesian scaling → Bigelow 2023/2025 belief dynamics → Gupta 2025 coin flips）——把 context 当证据，问 LLM 的 p(y|context) 像不像某个后验。几乎全部默认 **证据可交换（计数式累积）**：Bigelow 2025 的模型 log p(x|c) ∝ −#不一致标签，再乘 N^{-α} 的亚线性折扣。
2. **“顺序/位置效应是缺陷”**（Zhao 2021 calibrate、Lu 2022 order、Fang ICLR'25 InvICL、Li 2025 Order Matters、Jiao 2026 conflict）——把 recency/primacy 当 bias 去修。
3. **“非平稳/相关数据下的 ICL 理论”**（Bai 2023 in-context algorithm selection、Qin ICLR'26 GLA recency、Dudley ICML'26 change-point、Letey 2026 sequential correlation、Park ICLR'25 competition phases）——多在从头训练的小 transformer / 线性注意力上做，证明“能做到”。
4. **ICL 机制可解释性**（Olsson induction heads、Hendel/Todd task/function vectors、Cho ICLR'25 三步电路、Cho ICLR'26 information removal、Yang ICLR'26 TR/TL heads、Yang NeurIPS'25 geometry）——在真实 LLM 上找“编码→合并→检索复制”电路；recency 被解释成 **表示相似度的位置偏置**（Cho 2025 §3.2/§5.3）。

**它们之间的裂缝（我们驻留的地方）：** 线 1 默认可交换计数、线 2 把顺序依赖当 bug、线 3 说顺序依赖在非平稳时是对的、线 4 的电路天然是“逐条检索+投票”的**可加**结构。没有人问：**真实 LLM 的证据权重究竟是一个固定的位置核（可加），还是依赖证据的整体组织（非可加、像在推断生成过程）？** 这决定了“order sensitivity 是 bug 还是对非平稳先验的理性对冲”。

## 1. 已被占有的结论（不能当我们的 novelty）
| 结论 | 主人 |
|---|---|
| ICL 对顺序敏感；iid demos 应该置换不变 | Lu 2022；Fang ICLR'25；Li 2025 |
| 真实 LLM 违反 martingale/exchangeability | Falck ICML'24 |
| label 关系中途翻转后偏向近处信息（D→F / F→D / 交替，等数量） | **Kossen ICLR'24 §8**（最直接的父工作） |
| 单个 corrupted demo 能显著误导规则归纳；位置偏置；vulnerability/susceptible heads | Jiao 2026 |
| 非平稳回归下 recency/gating 有利 | Qin ICLR'26 |
| transformer 可以做 in-context change-point 检测（构造+训练） | Dudley ICML'26 |
| 相关序列改变有效 context 长度 | Letey 2026 |
| ICL 学习曲线 sigmoid、可用 Bayesian belief 模型拟合；steering=改先验 | Bigelow ICLR'24 / 2025 |
| LLM 在多轮对话中 belief stay/update/isolation 失败（逻辑证据、显式更正） | Xu 2026 BeliefTrack |
| transformer 可以 in-context 选择算法（理论） | Bai NeurIPS'23 |

## 2. 领域真正关心的问题（为什么我们的答案有人在乎）
- **ICL 到底在做什么推断**：Bayesian 视角的争论（Falck 说不是 Bayesian；Bigelow/Arora 说可以用 Bayesian 模型高精度预测）。若 LLM 对 *生成结构本身* 做推断，二者可调和：违反 exchangeability 不是“非 Bayesian”，而是“Bayesian 但先验允许非平稳”。
- **many-shot ICL / 长上下文**：亚线性证据累积（power law, Anil 2024; Bigelow 2025 的 N^{-α}）缺乏解释；非平稳先验天然产生旧证据折扣。
- **Agent / 长对话的 belief 更新**：何时应该改主意（BeliefTrack、reversal learning 的 LLM 研究）——我们的受控任务给出最小可测版本。
- **机制**：induction/retrieval 电路是逐条可加的；如果行为是非可加的，电路图里缺一个“结构/一致性”信号——直接给 Hakaze 系电路研究提出新对象。

## 3. 跨领域参照
- **认知科学：stochasticity vs volatility**（Behrens 2007；Nassar 2010；Piray & Daw 2021 Nat Commun）——理性学习者必须同时推断“环境多吵”和“环境多常变”，二者对学习率作用相反（噪声↑→学习率↓；波动↑→学习率↑）。这是我们 noise-vs-change 设计的直接理论来源：**同样的后缀反例，前缀噪声越多越不该认为是规则变化**——固定核/集合学习者预测相反方向。
- 统计：Bayesian online change-point detection（Adams & MacKay 2007）；hidden Markov 规则切换模型。

## 4. 我们的测量对象（持续修订）
- 证据权重是否 **可加**：用单条翻转估计位置核 w_t，预测多条翻转组合；残差即结构敏感性。
- 与 exact meta-oracle（联合推断 λ 波动率与 ε 噪声率）的对应：LLM 隐含的 hazard / noise 先验是多少？
- 方向相反预测的关键对照（noisy-prefix vs clean-prefix + 相同后缀）。
